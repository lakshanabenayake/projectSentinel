#!/usr/bin/env python3
"""
Debug script to check path resolution in run_demo.py
"""

import sys
import os
from pathlib import Path

def debug_paths():
    """Debug path resolution"""
    
    print("=== Path Debug Information ===")
    print(f"Current script: {__file__}")
    print(f"Script directory: {Path(__file__).parent}")
    print(f"Parent directory: {Path(__file__).parent.parent}")
    print(f"Project root (parent.parent.parent): {Path(__file__).parent.parent.parent}")
    print()
    
    # Mimic run_demo.py path setup
    base_path = Path(__file__).parent.parent.parent
    src_path = base_path / "src"
    backend_path = src_path / "backend"
    frontend_path = src_path / "frontend"
    zebra_path = base_path / "zebra"
    stream_server_path = zebra_path / "data" / "streaming-server"
    
    print("=== Resolved Paths ===")
    print(f"Base path: {base_path}")
    print(f"Exists: {base_path.exists()}")
    print()
    print(f"Src path: {src_path}")
    print(f"Exists: {src_path.exists()}")
    print()
    print(f"Backend path: {backend_path}")
    print(f"Exists: {backend_path.exists()}")
    print()
    print(f"Frontend path: {frontend_path}")
    print(f"Exists: {frontend_path.exists()}")
    print()
    print(f"Zebra path: {zebra_path}")
    print(f"Exists: {zebra_path.exists()}")
    print()
    print(f"Stream server path: {stream_server_path}")
    print(f"Exists: {stream_server_path.exists()}")
    print()
    
    # Check specific files
    print("=== Specific Files ===")
    
    backend_app = backend_path / "app.py"
    print(f"Backend app.py: {backend_app}")
    print(f"Exists: {backend_app.exists()}")
    
    frontend_package = frontend_path / "package.json"
    print(f"Frontend package.json: {frontend_package}")
    print(f"Exists: {frontend_package.exists()}")
    
    stream_server = stream_server_path / "stream_server.py"
    print(f"Stream server: {stream_server}")
    print(f"Exists: {stream_server.exists()}")
    
    # List contents of key directories
    print("\n=== Directory Contents ===")
    
    if base_path.exists():
        print(f"\nBase path contents:")
        for item in base_path.iterdir():
            print(f"  {item.name}")
    
    if backend_path.exists():
        print(f"\nBackend path contents:")
        for item in backend_path.iterdir():
            print(f"  {item.name}")
    
    if zebra_path.exists():
        print(f"\nZebra path contents:")
        for item in zebra_path.iterdir():
            print(f"  {item.name}")

if __name__ == "__main__":
    debug_paths()