"""
Streaming Client for Project Sentinel
Connects to the streaming server and processes real-time data
"""

import socket
import json
import threading
import time
from typing import Callable, Dict, Any, Optional

class StreamingClient:
    """Client to connect to Project Sentinel streaming server"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 8765, callback: Optional[Callable] = None):
        self.host = host
        self.port = port
        self.callback = callback
        self.running = False
        self.socket = None
        self.thread = None
    
    def start(self):
        """Start the streaming client"""
        self.running = True
        self.thread = threading.Thread(target=self._connect_and_stream)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the streaming client"""
        self.running = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join()
    
    def _connect_and_stream(self):
        """Connect to server and start streaming data"""
        print(f"🔌 Attempting to connect to {self.host}:{self.port}...")
        
        try:
            self.socket = socket.create_connection((self.host, self.port), timeout=10)
            print(f"✅ Connected to streaming server at {self.host}:{self.port}")
            
            event_count = 0
            
            with self.socket.makefile('r', encoding='utf-8') as stream:
                for line in stream:
                    if not self.running:
                        print("🛑 Stopping streaming client...")
                        break
                        
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        event_data = json.loads(line)
                        
                        # Handle the initial banner
                        if event_data.get('service') == 'project-sentinel-event-stream':
                            print(f"📋 Stream Banner: {event_data.get('datasets', [])} datasets available")
                            print(f"📋 Total events: {event_data.get('events', 0)}, Speed: {event_data.get('speed_factor', 1)}x")
                            continue
                        
                        event_count += 1
                        
                        # Log first few events for debugging
                        if event_count <= 5:
                            print(f"📦 Event #{event_count}: {event_data.get('dataset')} @ {event_data.get('timestamp')}")
                        
                        # Process the event if callback is provided
                        if self.callback and callable(self.callback):
                            self.callback(event_data)
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Error parsing JSON: {e}")
                        print(f"   Line: {line[:100]}...")
                        continue
                    except Exception as e:
                        print(f"❌ Error processing event: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
        
        except ConnectionRefusedError:
            print(f"❌ Could not connect to streaming server at {self.host}:{self.port}")
            print(f"   Make sure the streaming server is running:")
            print(f"   python stream_server.py --port {self.port} --speed 10 --loop")
        except socket.timeout:
            print(f"⏱️  Connection timeout to {self.host}:{self.port}")
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.socket:
                self.socket.close()
                print(f"🔌 Disconnected from streaming server")

def test_streaming_client():
    """Test function for streaming client"""
    def on_data_received(event_data):
        print(f"Received: {event_data.get('dataset')} - {event_data.get('timestamp')}")
    
    client = StreamingClient(callback=on_data_received)
    
    try:
        client.start()
        print("Streaming client started. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while client.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping streaming client...")
        client.stop()

if __name__ == '__main__':
    test_streaming_client()