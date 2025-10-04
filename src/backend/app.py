"""
Project Sentinel Backend Server
Flask + Socket.IO server for real-time retail analytics
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sentinel-secret-key'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
data_processor = DataProcessor()
anomaly_detector = AnomalyDetector()
event_generator = EventGenerator()
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
    
    def on_data_received(event_data):
        """Callback for when new streaming data is received"""
        # Store in database
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
        
        # Process for anomalies
        detected_events = anomaly_detector.process_event(event_data)
        
        # Generate and emit events
        for event in detected_events:
            event_generator.add_event(event)
            socketio.emit('new_event', event)
        
        # Emit raw data update
        socketio.emit('data_update', {
            'dataset': event_data.get('dataset'),
            'timestamp': event_data.get('timestamp'),
            'data': event_data.get('event', {})
        })
    
    # Initialize streaming client
    streaming_client = StreamingClient(
        host='127.0.0.1',
        port=8765,
        callback=on_data_received
    )
    
    # Start streaming
    try:
        streaming_client.start()
    except Exception as e:
        print(f"Error in streaming: {e}")

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
    print("Starting Project Sentinel Backend Server...")
    print("Dashboard will be available at: http://localhost:3000")
    print("API available at: http://localhost:5000")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)