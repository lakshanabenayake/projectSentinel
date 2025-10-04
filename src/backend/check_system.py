#!/usr/bin/env python3
"""
Project Sentinel - Quick Start Script
Tests connections and provides diagnostic information
"""

import os
import sys
import subprocess
import socket
import time

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_port(host, port, name):
    """Check if a port is open"""
    try:
        sock = socket.create_connection((host, port), timeout=2)
        sock.close()
        print(f"✅ {name} is running on {host}:{port}")
        return True
    except (ConnectionRefusedError, socket.timeout):
        print(f"❌ {name} is NOT running on {host}:{port}")
        return False
    except Exception as e:
        print(f"⚠️  Error checking {name}: {e}")
        return False

def check_file_exists(path):
    """Check if file exists"""
    if os.path.exists(path):
        print(f"✅ Found: {path}")
        return True
    else:
        print(f"❌ Missing: {path}")
        return False

def main():
    print_header("Project Sentinel - System Status Check")
    
    # Get base directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = current_dir
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    
    print(f"📁 Backend Directory: {backend_dir}")
    print(f"📁 Project Root: {project_root}")
    
    # Check Python files
    print_header("1. Checking Backend Files")
    required_files = [
        'app.py',
        'streaming_client.py',
        'data_processor.py',
        'anomaly_detector.py',
        'event_generator.py',
        'sentinel_detector.py'
    ]
    
    all_files_present = True
    for file in required_files:
        file_path = os.path.join(backend_dir, file)
        if not check_file_exists(file_path):
            all_files_present = False
    
    if not all_files_present:
        print("\n⚠️  Some required files are missing!")
        return
    
    # Check data files
    print_header("2. Checking Data Files")
    data_dir = os.path.join(project_root, '..', '..', '..', 'data', 'input')
    data_files = [
        'products_list.csv',
        'customer_data.csv',
        'pos_transactions.jsonl',
        'rfid_readings.jsonl',
        'queue_monitoring.jsonl',
        'product_recognition.jsonl',
        'inventory_snapshots.jsonl'
    ]
    
    print(f"📂 Data directory: {data_dir}")
    for file in data_files:
        file_path = os.path.join(data_dir, file)
        check_file_exists(file_path)
    
    # Check streaming server
    print_header("3. Checking Streaming Server")
    stream_running = check_port('127.0.0.1', 8765, 'Streaming Server')
    
    if not stream_running:
        print("\n🔧 To start the streaming server:")
        print("   cd d:/ProjectSentinel/zebra/data/streaming-server")
        print("   python stream_server.py --port 8765 --speed 10 --loop")
    
    # Check backend server
    print_header("4. Checking Backend Server")
    backend_running = check_port('127.0.0.1', 5000, 'Backend API Server')
    
    if not backend_running:
        print("\n🔧 To start the backend server:")
        print("   cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/backend")
        print("   python app.py")
    
    # Check frontend
    print_header("5. Checking Frontend Server")
    frontend_running = check_port('127.0.0.1', 5173, 'Frontend Dev Server')
    
    if not frontend_running:
        print("\n🔧 To start the frontend:")
        print("   cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/frontend")
        print("   npm run dev")
    
    # Output directory
    print_header("6. Checking Output Directory")
    output_dir = os.path.join(project_root, 'evidence', 'output', 'final')
    if os.path.exists(output_dir):
        print(f"✅ Output directory exists: {output_dir}")
        
        # Check for events file
        events_file = os.path.join(output_dir, 'events.jsonl')
        if os.path.exists(events_file):
            size = os.path.getsize(events_file)
            print(f"✅ Events file exists: {events_file} ({size} bytes)")
        else:
            print(f"📝 Events file will be created at: {events_file}")
    else:
        print(f"⚠️  Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # Summary
    print_header("System Status Summary")
    
    status = {
        'Backend Files': all_files_present,
        'Streaming Server': stream_running,
        'Backend API': backend_running,
        'Frontend': frontend_running
    }
    
    print("\nComponent Status:")
    for component, is_ready in status.items():
        status_icon = "✅" if is_ready else "❌"
        print(f"  {status_icon} {component}")
    
    all_ready = all(status.values())
    
    if all_ready:
        print("\n🎉 All systems are GO! System is ready.")
        print("\n🌐 Access Points:")
        print("   Dashboard:  http://localhost:5173")
        print("   Backend API: http://localhost:5000/api/events")
        print("   Health Check: http://localhost:5000/api/health")
    else:
        print("\n⚠️  Some components are not running.")
        print("Please start the missing components using the commands above.")
        
        if not stream_running:
            print("\n🚨 CRITICAL: Streaming server must be running first!")
    
    # Test connection if streaming server is running
    if stream_running:
        print_header("7. Testing Stream Connection")
        print("Attempting to read from stream...")
        
        try:
            sock = socket.create_connection(('127.0.0.1', 8765), timeout=5)
            with sock.makefile('r', encoding='utf-8') as stream:
                line = stream.readline().strip()
                if line:
                    import json
                    data = json.loads(line)
                    if data.get('service'):
                        print(f"✅ Stream is active!")
                        print(f"   Datasets: {len(data.get('datasets', []))} available")
                        print(f"   Events: {data.get('events', 0)} total")
                    else:
                        print(f"✅ Receiving events from stream")
            sock.close()
        except Exception as e:
            print(f"⚠️  Stream test failed: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
