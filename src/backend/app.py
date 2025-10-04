"""
Project Sentinel Backend Server
Flask + Socket.IO server for real-time retail analytics
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import os
import sqlite3
import threading
import time
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from data_processor import DataProcessor
from anomaly_detector import AnomalyDetector
from event_generator import EventGenerator
from streaming_client import StreamingClient
from sentinel_detector import SentinelDetector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sentinel-secret-key'
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure SocketIO with threading mode for better compatibility
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

# Global instances
data_processor = DataProcessor()
anomaly_detector = AnomalyDetector()
event_generator = EventGenerator()
sentinel_detector = SentinelDetector()  # New enhanced detector
streaming_client = None

# Database initialization
def init_database():
    """Initialize SQLite database for storing processed data"""
    conn = sqlite3.connect('sentinel.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_id TEXT NOT NULL,
            event_name TEXT NOT NULL,
            station_id TEXT,
            customer_id TEXT,
            product_sku TEXT,
            data JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stream_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            station_id TEXT,
            status TEXT,
            data JSON,
            processed BOOLEAN DEFAULT FALSE
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/events')
def get_events():
    """Get recent events"""
    limit = request.args.get('limit', 50, type=int)
    
    conn = sqlite3.connect('sentinel.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, event_id, event_name, station_id, customer_id, product_sku, data
        FROM events 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    events = []
    for row in cursor.fetchall():
        events.append({
            'timestamp': row[0],
            'event_id': row[1],
            'event_name': row[2],
            'station_id': row[3],
            'customer_id': row[4],
            'product_sku': row[5],
            'data': json.loads(row[6]) if row[6] else {}
        })
    
    conn.close()
    return jsonify(events)

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = sqlite3.connect('sentinel.db')
    cursor = conn.cursor()
    
    # Get event counts by type
    cursor.execute('''
        SELECT event_name, COUNT(*) as count
        FROM events 
        WHERE datetime(created_at) > datetime('now', '-1 hour')
        GROUP BY event_name
    ''')
    event_counts = dict(cursor.fetchall())
    
    # Get station status
    cursor.execute('''
        SELECT station_id, COUNT(*) as activity
        FROM stream_data 
        WHERE datetime(timestamp) > datetime('now', '-10 minutes')
        GROUP BY station_id
    ''')
    station_activity = dict(cursor.fetchall())
    
    conn.close()
    
    return jsonify({
        'event_counts': event_counts,
        'station_activity': station_activity,
        'total_events': sum(event_counts.values()),
        'active_stations': len(station_activity)
    })

@app.route('/api/monitoring/consumption')
def get_consumption_stats():
    """Monitor event consumption and processing rates"""
    conn = sqlite3.connect('sentinel.db')
    cursor = conn.cursor()
    
    # Get total counts
    cursor.execute('SELECT COUNT(*) FROM stream_data')
    total_stream_data = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM events')
    total_events = cursor.fetchone()[0]
    
    # Get recent activity (last 5 minutes)
    cursor.execute('''
        SELECT COUNT(*) FROM stream_data 
        WHERE datetime(timestamp) > datetime('now', '-5 minutes')
    ''')
    recent_stream_data = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM events 
        WHERE datetime(created_at) > datetime('now', '-5 minutes')
    ''')
    recent_events = cursor.fetchone()[0]
    
    # Get processing rate by dataset
    cursor.execute('''
        SELECT dataset, COUNT(*) as count
        FROM stream_data 
        WHERE datetime(timestamp) > datetime('now', '-1 hour')
        GROUP BY dataset
    ''')
    dataset_counts = dict(cursor.fetchall())
    
    # Check latest timestamp
    cursor.execute('SELECT MAX(timestamp) FROM stream_data')
    latest_data = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_consumed': total_stream_data,
        'total_events_generated': total_events,
        'recent_5min_data': recent_stream_data,
        'recent_5min_events': recent_events,
        'consumption_rate_per_minute': recent_stream_data / 5 if recent_stream_data > 0 else 0,
        'dataset_distribution': dataset_counts,
        'latest_data_timestamp': latest_data,
        'status': 'consuming' if recent_stream_data > 0 else 'idle'
    })

@app.route('/api/monitoring/stream-health')
def get_stream_health():
    """Check streaming connection health"""
    global streaming_client
    
    conn = sqlite3.connect('sentinel.db')
    cursor = conn.cursor()
    
    # Check for recent data
    cursor.execute('''
        SELECT COUNT(*) FROM stream_data 
        WHERE datetime(timestamp) > datetime('now', '-1 minute')
    ''')
    last_minute_count = cursor.fetchone()[0]
    
    # Check connection gaps
    cursor.execute('''
        SELECT timestamp FROM stream_data 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''')
    result = cursor.fetchone()
    last_data_time = result[0] if result else None
    
    conn.close()
    
    streaming_status = 'connected' if streaming_client and hasattr(streaming_client, 'connected') else 'unknown'
    
    return jsonify({
        'streaming_client_status': streaming_status,
        'data_flow_healthy': last_minute_count > 0,
        'last_data_received': last_data_time,
        'data_points_last_minute': last_minute_count,
        'server_port': 8765
    })

@app.route('/api/monitoring/detection-stats')
def get_detection_stats():
    """Get enhanced detection engine statistics"""
    global sentinel_detector
    
    stats = sentinel_detector.get_statistics()
    
    # Also check if output file exists
    output_exists = os.path.exists(stats.get('output_file', ''))
    file_size = 0
    if output_exists:
        file_size = os.path.getsize(stats['output_file'])
    
    return jsonify({
        **stats,
        'output_file_exists': output_exists,
        'output_file_size_bytes': file_size,
        'detection_engine': 'SentinelDetector v2.0'
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('status', {'status': 'connected', 'message': 'Connected to Sentinel backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

def process_streaming_data():
    """Background thread to process streaming data and emit updates"""
    global streaming_client
    
    event_counter = {'count': 0}  # Use dict for mutable reference
    
    def on_data_received(event_data):
        """Callback for when new streaming data is received"""
        event_counter['count'] += 1
        
        # Log every 10 events to show consumption is happening
        if event_counter['count'] % 10 == 0:
            print(f"📥 Consumed {event_counter['count']} events from stream...")
        
        # Store in database
        try:
            conn = sqlite3.connect('sentinel.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stream_data (dataset, timestamp, station_id, status, data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                event_data.get('dataset'),
                event_data.get('timestamp'),
                event_data.get('event', {}).get('station_id'),
                event_data.get('event', {}).get('status'),
                json.dumps(event_data.get('event', {}))
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Database error: {e}")
        
        # Process for anomalies using enhanced detector
        try:
            detected_event = sentinel_detector.detect(event_data)
            
            # If event was detected, emit it to frontend
            if detected_event:
                print(f"🚨 DETECTED: {detected_event.get('event_data', {}).get('event_name')} at {detected_event.get('timestamp')}")
                socketio.emit('new_event', detected_event)
        except Exception as e:
            print(f"❌ Sentinel detector error: {e}")
            
        # Also process with original detector for compatibility
        try:
            legacy_events = anomaly_detector.process_event(event_data)
            for event in legacy_events:
                event_generator.add_event(event)
                socketio.emit('legacy_event', event)
                print(f"🔔 Legacy event: {event.get('event_data', {}).get('event_name', 'unknown')}")
        except Exception as e:
            print(f"⚠️  Legacy detector error: {e}")
        
        # Emit raw data update to frontend
        try:
            socketio.emit('data_update', {
                'dataset': event_data.get('dataset'),
                'timestamp': event_data.get('timestamp'),
                'data': event_data.get('event', {})
            })
        except Exception as e:
            print(f"⚠️  WebSocket emit error: {e}")
    
    # Initialize streaming client
    print("🔌 Initializing streaming client...")
    streaming_client = StreamingClient(
        host='127.0.0.1',
        port=8765,
        callback=on_data_received
    )
    
    # Start streaming
    try:
        print("🌊 Starting stream consumption...")
        streaming_client.start()
        print("✅ Streaming client running!")
    except Exception as e:
        print(f"❌ Error starting streaming client: {e}")
        import traceback
        traceback.print_exc()

@app.route('/api/start_processing')
def start_processing():
    """Start data processing"""
    thread = threading.Thread(target=process_streaming_data)
    thread.daemon = True
    thread.start()
    return jsonify({"status": "started", "message": "Data processing started"})

@app.route('/api/export_events')
def export_events():
    """Export events to JSONL format"""
    output_file = request.args.get('output', 'events.jsonl')
    return event_generator.export_to_file(output_file)

if __name__ == '__main__':
    init_database()
    print("=" * 60)
    print("🚀 Starting Project Sentinel Backend Server...")
    print("=" * 60)
    print("📊 Dashboard will be available at: http://localhost:3000")
    print("🔌 API available at: http://localhost:5000")
    print("🌊 Connecting to streaming server at: 127.0.0.1:8765")
    print("=" * 60)
    
    # Auto-start streaming client in background thread
    print("⚡ Auto-starting streaming client...")
    streaming_thread = threading.Thread(target=process_streaming_data, daemon=True)
    streaming_thread.start()
    time.sleep(2)  # Give it time to connect
    print("✅ Streaming client started")
    print("=" * 60)
    
    socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)