#!/usr/bin/env python3
"""
Project Sentinel Flask Backend
Integrates event detection with real-time dashboard streaming
"""

import json
import socket
import threading
import time
from datetime import datetime
from typing import Dict, Any, Iterator
import os
import sys

try:
    from flask import Flask, request, jsonify
    from flask_socketio import SocketIO, emit
    from flask_cors import CORS
    flask_available = True
except ImportError as e:
    print(f"Flask dependencies not available: {e}")
    print("Please install: pip install flask flask-socketio flask-cors")
    flask_available = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'project-sentinel-secret-key'
CORS(app, origins=["http://localhost:3000"])

# Use threading async_mode to avoid eventlet issues on Python 3.12
socketio = SocketIO(app, 
                   cors_allowed_origins=["http://localhost:3000"], 
                   async_mode='threading',
                   logger=False, 
                   engineio_logger=False)

# Global state for event detection (from serve1.py)
EVENT_COUNTER = 0
seen_rfids = {}            # customer_id -> set of SKUs detected by RFID
scanned_items = {}         # customer_id -> set of SKUs scanned at POS
expected_weights = {}      # customer_id -> total expected weight
inventory_snapshot = {}    # SKU -> expected inventory

# Dashboard metrics
dashboard_metrics = {
    "total_events": 0,
    "active_stations": set(),
    "active_customers": set(),
    "alerts": [],
    "queue_stats": {},
    "inventory_alerts": 0
}

# Connected clients
connected_clients = []

# @algorithm Event Stream Reader | Consumes real-time data from stream server
def read_events(host: str, port: int) -> Iterator[dict]:
    """Generator that yields JSON events from stream server"""
    try:
        with socket.create_connection((host, port)) as conn:
            with conn.makefile("r", encoding="utf-8") as stream:
                for line in stream:
                    if not line.strip():
                        continue
                    yield json.loads(line)
    except Exception as e:
        print(f"Error connecting to stream server: {e}")
        return

# @algorithm Event Generator | Creates standardized events for dashboard
def create_event(event_name: str, data: Dict[str, Any], priority: str = "info"):
    """Create standardized event format"""
    global EVENT_COUNTER
    EVENT_COUNTER += 1
    event_id = f"E{EVENT_COUNTER:03d}"
    
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_id": event_id,
        "event_data": {"event_name": event_name, **data},
        "priority": priority
    }
    
    # Update dashboard metrics
    dashboard_metrics["total_events"] += 1
    if "station_id" in data:
        dashboard_metrics["active_stations"].add(data["station_id"])
    if "customer_id" in data:
        dashboard_metrics["active_customers"].add(data["customer_id"])
    
    # Add to alerts if high priority
    if priority in ["warning", "critical"]:
        dashboard_metrics["alerts"].append({
            "id": event_id,
            "message": event_name,
            "priority": priority,
            "timestamp": event["timestamp"],
            "data": data
        })
        # Keep only last 50 alerts
        if len(dashboard_metrics["alerts"]) > 50:
            dashboard_metrics["alerts"] = dashboard_metrics["alerts"][-50:]
    
    return event

# @algorithm Scanner Avoidance Detection | Identifies items detected by RFID but not scanned
def detect_scanner_avoidance(customer_id: str, station_id: str):
    """Detect items detected by RFID but not scanned at POS"""
    if customer_id in seen_rfids:
        scanned = scanned_items.get(customer_id, set())
        missing = seen_rfids[customer_id] - scanned
        if missing:
            for sku in missing:
                event = create_event("Scanner Avoidance", {
                    "station_id": station_id,
                    "customer_id": customer_id,
                    "product_sku": sku
                }, priority="warning")
                broadcast_event(event)
            seen_rfids[customer_id].clear()

# @algorithm Barcode Switching Detection | Validates scanned vs recognized products
def detect_barcode_switching(customer_id: str, station_id: str, predicted_sku: str):
    """Detect when scanned barcode doesn't match product recognition"""
    if customer_id in scanned_items and scanned_items[customer_id]:
        last_scanned = list(scanned_items[customer_id])[-1]
        if predicted_sku and last_scanned and predicted_sku != last_scanned:
            event = create_event("Barcode Switching", {
                "station_id": station_id,
                "customer_id": customer_id,
                "actual_sku": predicted_sku,
                "scanned_sku": last_scanned
            }, priority="warning")
            broadcast_event(event)

# @algorithm Weight Validation | Detects weight discrepancies in transactions
def detect_weight_discrepancy(customer_id: str, station_id: str, actual_weight: float, expected_weight: float, sku: str):
    """Detect significant weight discrepancies"""
    if actual_weight and expected_weight and abs(actual_weight - expected_weight) > 50:
        event = create_event("Weight Discrepancies", {
            "station_id": station_id,
            "customer_id": customer_id,
            "product_sku": sku,
            "expected_weight": expected_weight,
            "actual_weight": actual_weight
        }, priority="warning")
        broadcast_event(event)

# @algorithm Queue Analysis | Monitors customer flow and wait times
def detect_queue_issues(station_id: str, customer_count: int, dwell_time: int, customer_id: str = None):
    """Detect long queues and wait times"""
    dashboard_metrics["queue_stats"][station_id] = {
        "customer_count": customer_count,
        "average_dwell_time": dwell_time
    }
    
    if customer_count >= 6:
        event = create_event("Long Queue Length", {
            "station_id": station_id,
            "num_of_customers": customer_count
        }, priority="warning")
        broadcast_event(event)
    
    if dwell_time >= 300:
        event = create_event("Long Wait Time", {
            "station_id": station_id,
            "customer_id": customer_id or "UNKNOWN",
            "wait_time_seconds": dwell_time
        }, priority="warning")
        broadcast_event(event)

# @algorithm Data Correlation | Main event processing and correlation logic
def process_event(event: dict):
    """Main event processing logic (adapted from serve1.py)"""
    dataset = event.get("dataset", "")
    ev = event.get("event", {})
    status = ev.get("status")
    station = ev.get("station_id", "UNKNOWN")
    cust = ev.get("customer_id", "UNKNOWN")

    # 1. RFID data processing
    if dataset.lower() == "rfid_data" and status == "Active":
        sku = ev["data"].get("sku")
        if sku:
            seen_rfids.setdefault(cust, set()).add(sku)

    # 2. POS transactions
    elif dataset.lower() == "pos_transactions":
        sku = ev["data"].get("sku")
        if sku:
            scanned_items.setdefault(cust, set()).add(sku)
        
        weight = ev["data"].get("weight_g", 0)
        expected_weights[cust] = expected_weights.get(cust, 0) + weight

        # System crash detection
        if status == "System Crash":
            event_obj = create_event("Unexpected Systems Crash", {
                "station_id": station,
                "duration_seconds": 180
            }, priority="critical")
            broadcast_event(event_obj)

        # Success operation detection
        if sku and sku in seen_rfids.get(cust, set()):
            event_obj = create_event("Success Operation", {
                "station_id": station,
                "customer_id": cust,
                "product_sku": sku
            }, priority="info")
            broadcast_event(event_obj)
            seen_rfids[cust].discard(sku)

        # Weight discrepancy check
        actual_weight = ev["data"].get("weight_g")
        expected_weight = ev["data"].get("price")  # Using price as weight proxy
        if sku and actual_weight and expected_weight:
            detect_weight_discrepancy(cust, station, actual_weight, expected_weight, sku)

    # 3. Product recognition
    elif dataset.lower() == "product_recognition" and status == "Active":
        predicted_sku = ev["data"].get("predicted_product")
        if predicted_sku:
            detect_barcode_switching(cust, station, predicted_sku)

    # 4. Queue monitoring
    elif dataset.lower() == "queue_monitor" and status == "Active":
        customer_count = ev["data"].get("customer_count", 0)
        dwell = ev["data"].get("average_dwell_time", 0)
        detect_queue_issues(station, customer_count, dwell, cust)

    # 5. Inventory snapshots
    elif dataset.lower() == "inventory_snapshots" and status == "Active":
        for sku, qty in ev.get("data", {}).items():
            if sku in inventory_snapshot and qty != inventory_snapshot[sku]:
                event_obj = create_event("Inventory Discrepancy", {
                    "SKU": sku,
                    "Expected_Inventory": inventory_snapshot[sku],
                    "Actual_Inventory": qty
                }, priority="warning")
                broadcast_event(event_obj)
                dashboard_metrics["inventory_alerts"] += 1
            inventory_snapshot[sku] = qty

    # 6. Staffing and checkout actions
    elif dataset.lower() == "staffing" and status == "Active":
        event_obj = create_event("Staffing Needs", {
            "station_id": station,
            "Staff_type": ev.get("data", {}).get("Staff_type", "UNKNOWN")
        }, priority="info")
        broadcast_event(event_obj)

    elif dataset.lower() == "checkout_action" and status == "Active":
        event_obj = create_event("Checkout Station Action", {
            "station_id": station,
            "Action": ev.get("data", {}).get("Action", "Open")
        }, priority="info")
        broadcast_event(event_obj)

    # Periodic scanner avoidance check
    detect_scanner_avoidance(cust, station)

def broadcast_event(event: dict):
    """Broadcast event to all connected dashboard clients"""
    socketio.emit('new_event', event, namespace='/')
    
def broadcast_metrics():
    """Broadcast current dashboard metrics"""
    metrics = {
        **dashboard_metrics,
        "active_stations": list(dashboard_metrics["active_stations"]),
        "active_customers": list(dashboard_metrics["active_customers"])
    }
    socketio.emit('metrics_update', metrics, namespace='/')

def stream_processor():
    """Background thread to process data stream"""
    print("Starting stream processor...")
    while True:
        try:
            for event in read_events("127.0.0.1", 8765):
                process_event(event)
                # Broadcast metrics every 10 events
                if EVENT_COUNTER % 10 == 0:
                    broadcast_metrics()
        except Exception as e:
            print(f"Stream processor error: {e}")
            time.sleep(5)  # Wait before reconnecting

# Flask Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get current dashboard metrics"""
    metrics = {
        **dashboard_metrics,
        "active_stations": list(dashboard_metrics["active_stations"]),
        "active_customers": list(dashboard_metrics["active_customers"])
    }
    return jsonify(metrics)

@app.route('/api/events', methods=['GET'])
def get_recent_events():
    """Get recent events"""
    return jsonify(dashboard_metrics["alerts"][-20:])  # Last 20 alerts

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    connected_clients.append(request.sid)
    # Send current metrics to new client
    broadcast_metrics()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')
    if request.sid in connected_clients:
        connected_clients.remove(request.sid)

@socketio.on('request_metrics')
def handle_metrics_request():
    """Handle metrics request from client"""
    broadcast_metrics()

if __name__ == '__main__':
    if not flask_available:
        print("Cannot start server - Flask dependencies missing")
        sys.exit(1)
    
    # Start stream processor in background thread
    stream_thread = threading.Thread(target=stream_processor, daemon=True)
    stream_thread.start()
    
    print("Starting Flask-SocketIO server on port 5000...")
    print("Health check: http://localhost:5000/api/health")
    print("Metrics: http://localhost:5000/api/metrics")
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"Server startup failed: {e}")
        sys.exit(1)