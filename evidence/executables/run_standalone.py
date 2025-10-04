#!/usr/bin/env python3
"""
Project Sentinel - Standalone Demo (No External Dependencies)
A simplified version that works with only Python standard library
"""

import json
import socket
import threading
import time
import os
import sys
import http.server
import socketserver
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for our API"""
    
    def __init__(self, *args, sentinel_demo=None, **kwargs):
        self.sentinel_demo = sentinel_demo
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/health':
            self.send_json_response({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})
        elif self.path == '/api/metrics':
            self.send_json_response(self.sentinel_demo.get_metrics() if self.sentinel_demo else {})
        elif self.path == '/api/events':
            events = self.sentinel_demo.get_recent_events() if self.sentinel_demo else []
            self.send_json_response(events)
        elif self.path == '/' or self.path == '/dashboard':
            self.send_dashboard_html()
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        response = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode())
    
    def send_dashboard_html(self):
        """Send simple HTML dashboard"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Project Sentinel - Store Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #1976d2; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .metric-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 24px; font-weight: bold; color: #1976d2; }
        .metric-label { font-size: 14px; color: #666; margin-top: 5px; }
        .events { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .event-item { padding: 10px; margin: 5px 0; border-left: 4px solid #2196f3; background: #f8f9fa; }
        .event-critical { border-left-color: #f44336; background: #ffebee; }
        .event-warning { border-left-color: #ff9800; background: #fff3e0; }
        .status { display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 12px; }
        .status-connected { background: #4caf50; color: white; }
        .refresh-btn { background: #1976d2; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Project Sentinel - Store Monitor Dashboard</h1>
            <span class="status status-connected" id="status">● LIVE</span>
            <button class="refresh-btn" onclick="refreshData()">Refresh Data</button>
        </div>
        
        <div class="metrics" id="metrics">
            <div class="metric-card">
                <div class="metric-value" id="total-events">-</div>
                <div class="metric-label">Total Events</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="active-stations">-</div>
                <div class="metric-label">Active Stations</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="active-customers">-</div>
                <div class="metric-label">Active Customers</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="alerts-count">-</div>
                <div class="metric-label">Active Alerts</div>
            </div>
        </div>
        
        <div class="events">
            <h3>Recent Events</h3>
            <div id="events-list">Loading events...</div>
        </div>
    </div>
    
    <script>
        async function refreshData() {
            try {
                // Fetch metrics
                const metricsResponse = await fetch('/api/metrics');
                const metrics = await metricsResponse.json();
                
                document.getElementById('total-events').textContent = metrics.total_events || 0;
                document.getElementById('active-stations').textContent = (metrics.active_stations || []).length;
                document.getElementById('active-customers').textContent = (metrics.active_customers || []).length;
                document.getElementById('alerts-count').textContent = (metrics.alerts || []).length;
                
                // Fetch events
                const eventsResponse = await fetch('/api/events');
                const events = await eventsResponse.json();
                
                const eventsList = document.getElementById('events-list');
                if (events.length === 0) {
                    eventsList.innerHTML = '<p>No events detected yet. System is monitoring...</p>';
                } else {
                    eventsList.innerHTML = events.slice(0, 10).map(event => `
                        <div class="event-item ${event.priority === 'critical' ? 'event-critical' : event.priority === 'warning' ? 'event-warning' : ''}">
                            <strong>${event.event_data.event_name}</strong><br>
                            <small>${new Date(event.timestamp).toLocaleString()} | ${event.event_id}</small>
                            ${event.event_data.station_id ? `<br><small>Station: ${event.event_data.station_id}</small>` : ''}
                        </div>
                    `).join('');
                }
                
                document.getElementById('status').textContent = '● LIVE';
            } catch (error) {
                document.getElementById('status').textContent = '● OFFLINE';
                console.error('Failed to refresh data:', error);
            }
        }
        
        // Auto-refresh every 5 seconds
        setInterval(refreshData, 5000);
        
        // Initial load
        refreshData();
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode())

class StandaloneSentinelDemo:
    """Standalone demo using only Python standard library"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.events = []
        self.metrics = {
            "total_events": 0,
            "active_stations": [],
            "active_customers": [],
            "alerts": []
        }
        self.event_counter = 0
        
        # Event detection state (from serve1.py)
        self.seen_rfids = {}
        self.scanned_items = {}
        self.expected_weights = {}
        self.inventory_snapshot = {}
        
    def log(self, message):
        """Print timestamped log message"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def create_event(self, event_name, data, priority="info"):
        """Create and store event"""
        self.event_counter += 1
        event_id = f"E{self.event_counter:03d}"
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_id": event_id,
            "event_data": {"event_name": event_name, **data},
            "priority": priority
        }
        
        self.events.insert(0, event)  # Add to beginning
        if len(self.events) > 100:  # Keep only last 100
            self.events = self.events[:100]
        
        self.metrics["total_events"] = self.event_counter
        
        if "station_id" in data and data["station_id"] not in self.metrics["active_stations"]:
            self.metrics["active_stations"].append(data["station_id"])
        
        if "customer_id" in data and data["customer_id"] not in self.metrics["active_customers"]:
            self.metrics["active_customers"].append(data["customer_id"])
        
        if priority in ["warning", "critical"]:
            self.metrics["alerts"].append(event)
            if len(self.metrics["alerts"]) > 50:
                self.metrics["alerts"] = self.metrics["alerts"][:50]
        
        self.log(f"Event: {event_name} ({priority})")
        
        # Write to output file
        self.write_event_to_file(event)
        
        return event
    
    def write_event_to_file(self, event):
        """Write event to events.jsonl file"""
        output_dir = self.base_path / "evidence" / "output" / "final"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "events.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    
    def read_events_from_stream(self, host="127.0.0.1", port=8765):
        """Try to read events from stream server"""
        try:
            self.log(f"Connecting to stream server at {host}:{port}")
            with socket.create_connection((host, port), timeout=5) as conn:
                with conn.makefile("r", encoding="utf-8") as stream:
                    for line in stream:
                        if not line.strip():
                            continue
                        try:
                            event = json.loads(line)
                            self.process_stream_event(event)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.log(f"Stream connection failed: {e}")
            self.log("Generating sample events instead...")
            self.generate_sample_events()
    
    def process_stream_event(self, event):
        """Process event from stream (using serve1.py logic)"""
        dataset = event.get("dataset", "")
        ev = event.get("event", {})
        status = ev.get("status")
        station = ev.get("station_id", "SCC1")
        cust = ev.get("customer_id", "C001")
        
        # Scanner avoidance detection
        if dataset.lower() == "rfid_data" and status == "Active":
            sku = ev["data"].get("sku")
            if sku:
                self.seen_rfids.setdefault(cust, set()).add(sku)
        
        # POS transactions
        elif dataset.lower() == "pos_transactions":
            sku = ev["data"].get("sku")
            if sku:
                self.scanned_items.setdefault(cust, set()).add(sku)
                
                # Success detection
                if sku in self.seen_rfids.get(cust, set()):
                    self.create_event("Success Operation", {
                        "station_id": station,
                        "customer_id": cust,
                        "product_sku": sku
                    }, "info")
                    self.seen_rfids[cust].discard(sku)
        
        # Queue monitoring
        elif dataset.lower() == "queue_monitor" and status == "Active":
            customer_count = ev["data"].get("customer_count", 0)
            if customer_count >= 6:
                self.create_event("Long Queue Length", {
                    "station_id": station,
                    "num_of_customers": customer_count
                }, "warning")
        
        # Check for scanner avoidance
        for cust_id, rfids in list(self.seen_rfids.items()):
            scanned = self.scanned_items.get(cust_id, set())
            missing = rfids - scanned
            if missing:
                for sku in missing:
                    self.create_event("Scanner Avoidance", {
                        "station_id": station,
                        "customer_id": cust_id,
                        "product_sku": sku
                    }, "warning")
                self.seen_rfids[cust_id].clear()
    
    def generate_sample_events(self):
        """Generate sample events for demonstration"""
        self.log("Generating sample events...")
        
        sample_events = [
            ("Success Operation", {"station_id": "SCC1", "customer_id": "C001", "product_sku": "PRD_F_03"}, "info"),
            ("Scanner Avoidance", {"station_id": "SCC1", "customer_id": "C002", "product_sku": "PRD_S_04"}, "warning"),
            ("Barcode Switching", {"station_id": "SCC2", "customer_id": "C003", "actual_sku": "PRD_F_08", "scanned_sku": "PRD_F_07"}, "warning"),
            ("Long Queue Length", {"station_id": "SCC1", "num_of_customers": 7}, "warning"),
            ("Weight Discrepancies", {"station_id": "SCC2", "customer_id": "C004", "expected_weight": 425, "actual_weight": 680}, "warning"),
            ("Unexpected Systems Crash", {"station_id": "SCC3", "duration_seconds": 180}, "critical"),
            ("Success Operation", {"station_id": "SCC2", "customer_id": "C005", "product_sku": "PRD_F_12"}, "info"),
            ("Inventory Discrepancy", {"SKU": "PRD_F_03", "Expected_Inventory": 150, "Actual_Inventory": 120}, "warning"),
        ]
        
        for i, (event_name, data, priority) in enumerate(sample_events):
            time.sleep(2)  # Simulate real-time generation
            self.create_event(event_name, data, priority)
    
    def get_metrics(self):
        """Get current metrics"""
        return self.metrics
    
    def get_recent_events(self):
        """Get recent events"""
        return self.events[:20]  # Return last 20 events
    
    def start_event_processor(self):
        """Start event processing in background thread"""
        def event_worker():
            self.read_events_from_stream()
        
        thread = threading.Thread(target=event_worker, daemon=True)
        thread.start()
        self.log("Event processor started")
    
    def start_server(self, port=5000):
        """Start HTTP server"""
        def make_handler(*args, **kwargs):
            return SimpleHTTPRequestHandler(*args, sentinel_demo=self, **kwargs)
        
        try:
            with socketserver.TCPServer(("", port), make_handler) as httpd:
                self.log(f"Server started on port {port}")
                self.log(f"Dashboard: http://localhost:{port}")
                self.log(f"API Health: http://localhost:{port}/api/health")
                self.log(f"API Metrics: http://localhost:{port}/api/metrics")
                self.log("Press Ctrl+C to stop")
                
                # Start event processing
                self.start_event_processor()
                
                httpd.serve_forever()
        except KeyboardInterrupt:
            self.log("Server stopped")
        except Exception as e:
            self.log(f"Server error: {e}")

def main():
    """Main entry point"""
    print("=== Project Sentinel Standalone Demo ===")
    print("Using Python standard library only (no external dependencies)")
    
    demo = StandaloneSentinelDemo()
    demo.start_server(5000)

if __name__ == "__main__":
    main()