#!/usr/bin/env python3
"""
Quick test to verify streaming server connection
"""

import socket
import json

def test_connection():
    """Test connection to streaming server"""
    host = '127.0.0.1'
    port = 8765
    
    print(f"Testing connection to {host}:{port}...")
    
    try:
        # Try to connect
        sock = socket.create_connection((host, port), timeout=5)
        print(f"✅ Connected successfully!")
        
        # Read first few lines
        with sock.makefile('r', encoding='utf-8') as stream:
            for i, line in enumerate(stream):
                if i >= 5:  # Read only first 5 events
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    
                    if data.get('service'):
                        print(f"\n📋 Banner:")
                        print(f"   Service: {data.get('service')}")
                        print(f"   Datasets: {data.get('datasets')}")
                        print(f"   Total Events: {data.get('events')}")
                        print(f"   Speed: {data.get('speed_factor')}x")
                        print(f"   Looping: {data.get('loop')}")
                    else:
                        print(f"\n📦 Event {i}:")
                        print(f"   Dataset: {data.get('dataset')}")
                        print(f"   Sequence: {data.get('sequence')}")
                        print(f"   Timestamp: {data.get('timestamp')}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Error: {e}")
        
        sock.close()
        print(f"\n✅ Stream is working correctly!")
        return True
        
    except ConnectionRefusedError:
        print(f"❌ Connection refused!")
        print(f"\n🔧 Make sure streaming server is running:")
        print(f"   cd d:/ProjectSentinel/zebra/data/streaming-server")
        print(f"   python stream_server.py --port 8765 --speed 10 --loop")
        return False
        
    except socket.timeout:
        print(f"⏱️  Connection timeout!")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Stream Connection Test")
    print("=" * 60)
    test_connection()
