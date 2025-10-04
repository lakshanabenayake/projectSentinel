"""
Project Sentinel - Streaming Client Module
Handles connection to data stream server with reconnection logic
"""

import socket
import json
import time
import threading
from typing import Iterator, Callable, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingClient:
    """Robust streaming client with reconnection capabilities"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, 
                 reconnect_delay: int = 5, max_retries: int = 10):
        self.host = host
        self.port = port
        self.reconnect_delay = reconnect_delay
        self.max_retries = max_retries
        self.is_running = False
        self.connection = None
        self.stream = None
        self.retry_count = 0
        
    def connect(self) -> bool:
        """Establish connection to stream server"""
        try:
            logger.info(f"Connecting to stream server at {self.host}:{self.port}")
            self.connection = socket.create_connection((self.host, self.port), timeout=10)
            self.stream = self.connection.makefile("r", encoding="utf-8")
            self.retry_count = 0
            logger.info("Successfully connected to stream server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Clean disconnect from server"""
        self.is_running = False
        if self.stream:
            try:
                self.stream.close()
            except:
                pass
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        logger.info("Disconnected from stream server")
    
    def read_events(self) -> Iterator[dict]:
        """Generator that yields JSON events with reconnection logic"""
        self.is_running = True
        
        while self.is_running:
            try:
                if not self.connection or not self.stream:
                    if not self.connect():
                        if self.retry_count >= self.max_retries:
                            logger.error(f"Max retries ({self.max_retries}) reached. Giving up.")
                            break
                        self.retry_count += 1
                        logger.warning(f"Retry {self.retry_count}/{self.max_retries} in {self.reconnect_delay} seconds...")
                        time.sleep(self.reconnect_delay)
                        continue
                
                # Read events from stream
                for line in self.stream:
                    if not self.is_running:
                        break
                        
                    if not line.strip():
                        continue
                        
                    try:
                        event = json.loads(line)
                        yield event
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON: {e}")
                        continue
                        
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                logger.warning(f"Connection lost: {e}")
                self.disconnect()
                if self.is_running:
                    time.sleep(self.reconnect_delay)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                self.disconnect()
                if self.is_running:
                    time.sleep(self.reconnect_delay)
    
    def start_streaming(self, event_handler: Callable[[dict], None]):
        """Start streaming in background thread"""
        def stream_worker():
            try:
                for event in self.read_events():
                    if not self.is_running:
                        break
                    event_handler(event)
            except Exception as e:
                logger.error(f"Stream worker error: {e}")
        
        self.streaming_thread = threading.Thread(target=stream_worker, daemon=True)
        self.streaming_thread.start()
        logger.info("Started streaming in background thread")
    
    def stop_streaming(self):
        """Stop streaming and cleanup"""
        self.is_running = False
        self.disconnect()
        if hasattr(self, 'streaming_thread'):
            self.streaming_thread.join(timeout=5)
        logger.info("Stopped streaming")
    
    def get_connection_status(self) -> dict:
        """Get current connection status"""
        return {
            "connected": bool(self.connection and self.stream),
            "running": self.is_running,
            "host": self.host,
            "port": self.port,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }