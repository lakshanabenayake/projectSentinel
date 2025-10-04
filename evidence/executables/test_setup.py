#!/usr/bin/env python3
"""
Project Sentinel - Setup Test
Quick test to verify dependencies and configuration
"""

import sys
import subprocess
from pathlib import Path

def test_python_setup():
    """Test Python and basic dependencies"""
    print("Testing Python setup...")
    
    # Test Python version
    print(f"Python version: {sys.version}")
    
    # Test basic imports
    try:
        import json, socket, threading, time, os
        print("✓ Standard library imports OK")
    except ImportError as e:
        print(f"✗ Standard library import failed: {e}")
        return False
    
    # Test Flask imports
    try:
        import flask
        print(f"✓ Flask {flask.__version__} available")
    except ImportError:
        print("✗ Flask not available")
        return False
    
    try:
        import flask_socketio
        print(f"✓ Flask-SocketIO available")
    except ImportError:
        print("✗ Flask-SocketIO not available")
        return False
        
    try:
        import flask_cors
        print("✓ Flask-CORS available")
    except ImportError:
        print("✗ Flask-CORS not available")
        return False
    
    return True

def test_node_setup():
    """Test Node.js setup"""
    print("\nTesting Node.js setup...")
    
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✓ Node.js {result.stdout.strip()} available")
        node_available = True
    except FileNotFoundError:
        print("✗ Node.js not available")
        node_available = False
    
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=True)
        print(f"✓ npm {result.stdout.strip()} available")
        npm_available = True
    except (FileNotFoundError, subprocess.CalledProcessError):
        try:
            # Try with .cmd extension on Windows
            result = subprocess.run(["npm.cmd", "--version"], capture_output=True, text=True)
            print(f"✓ npm {result.stdout.strip()} available")
            npm_available = True
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("✗ npm not available")
            npm_available = False
    
    return node_available and npm_available

def test_project_structure():
    """Test project structure"""
    print("\nTesting project structure...")
    
    # Go up two levels from evidence/executables/ to project root
    base_path = Path(__file__).parent.parent.parent
    
    required_paths = [
        "src/backend/app.py",
        "src/backend/requirements.txt", 
        "src/frontend/package.json",
        "zebra/data/streaming-server/stream_server.py"
    ]
    
    all_good = True
    for path_str in required_paths:
        path = base_path / path_str
        if path.exists():
            print(f"✓ {path_str} exists")
        else:
            print(f"✗ {path_str} missing")
            all_good = False
    
    return all_good

def main():
    print("=== Project Sentinel Setup Test ===\n")
    
    python_ok = test_python_setup()
    node_ok = test_node_setup()  
    structure_ok = test_project_structure()
    
    print("\n=== Test Summary ===")
    
    if python_ok:
        print("✓ Python backend dependencies OK")
    else:
        print("✗ Python backend has issues")
        print("  Run: pip install flask flask-socketio flask-cors requests")
    
    if node_ok:
        print("✓ Node.js frontend dependencies OK")
    else:
        print("⚠ Node.js not available - frontend will be disabled")
        print("  Install Node.js from: https://nodejs.org/")
    
    if structure_ok:
        print("✓ Project structure OK")
    else:
        print("✗ Project structure has issues")
    
    if python_ok and structure_ok:
        print("\n🎉 Ready to run demo!")
        print("Run: python run_demo.py")
    else:
        print("\n❌ Setup incomplete - please fix issues above")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)