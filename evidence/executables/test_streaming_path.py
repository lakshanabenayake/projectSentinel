#!/usr/bin/env python3
"""
Quick test to verify streaming server path is correct
"""

import sys
from pathlib import Path

def test_streaming_server_path():
    """Test if streaming server can be found in new location"""
    
    print("=== Streaming Server Path Test ===")
    
    # Mimic run_demo.py path setup
    base_path = Path(__file__).parent.parent.parent
    src_path = base_path / "src"
    data_path = src_path / "data"
    stream_server_path = data_path / "streaming-server"
    
    print(f"Base path: {base_path}")
    print(f"Src path: {src_path}")
    print(f"Data path: {data_path}")
    print(f"Stream server path: {stream_server_path}")
    print()
    
    # Test possible streaming server locations
    possible_paths = [
        stream_server_path / "stream_server.py",
        src_path / "data" / "streaming-server" / "stream_server.py",
        base_path / "zebra" / "data" / "streaming-server" / "stream_server.py",  # fallback
    ]
    
    print("Checking streaming server locations:")
    found = False
    
    for i, path in enumerate(possible_paths, 1):
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"{i}. {status} {path}")
        if exists and not found:
            print(f"   → Found streaming server at: {path}")
            found = True
    
    print()
    if found:
        print("🎉 Streaming server found successfully!")
        return True
    else:
        print("❌ Streaming server not found in any location")
        return False

if __name__ == "__main__":
    success = test_streaming_server_path()
    sys.exit(0 if success else 1)