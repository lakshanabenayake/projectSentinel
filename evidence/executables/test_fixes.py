#!/usr/bin/env python3
"""
Quick test to verify the fixes work
"""

import sys
import subprocess
import os
from pathlib import Path

def test_python_command():
    """Test if Python commands work with spaces in path"""
    print(f"Testing Python executable: {sys.executable}")
    
    # Test with list format (should work)
    try:
        pip_cmd = [sys.executable, "-m", "pip", "--version"]
        result = subprocess.run(pip_cmd, capture_output=True, text=True, check=True)
        print(f"✓ List format works: pip {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"✗ List format failed: {e}")
        return False

def test_npm_command():
    """Test npm command variations"""
    print("Testing npm commands...")
    
    # Test basic npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✓ npm (shell=True) works: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"npm (shell=True) failed: {e}")
    
    # Test npm.cmd
    try:
        result = subprocess.run(["npm.cmd", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ npm.cmd works: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"npm.cmd failed: {e}")
    
    print("✗ npm not working")
    return False

def test_paths():
    """Test path resolution"""
    print("Testing project paths...")
    
    base_path = Path(__file__).parent.parent.parent
    print(f"Project root: {base_path}")
    
    paths_to_check = [
        "src/backend/app.py",
        "src/backend/requirements.txt", 
        "src/frontend/package.json",
        "zebra/data/streaming-server/stream_server.py"
    ]
    
    all_good = True
    for path_str in paths_to_check:
        path = base_path / path_str
        if path.exists():
            print(f"✓ {path_str}")
        else:
            print(f"✗ {path_str} missing")
            all_good = False
    
    return all_good

def main():
    print("=== Testing Fixes ===\n")
    
    python_ok = test_python_command()
    npm_ok = test_npm_command()
    paths_ok = test_paths()
    
    print(f"\n=== Results ===")
    print(f"Python commands: {'✓' if python_ok else '✗'}")
    print(f"npm commands: {'✓' if npm_ok else '✗'}")
    print(f"Project paths: {'✓' if paths_ok else '✗'}")
    
    if python_ok and paths_ok:
        print("\n🎉 Core functionality should work!")
        if not npm_ok:
            print("⚠ npm issues - frontend will be disabled")
    else:
        print("\n❌ Still have issues to fix")

if __name__ == "__main__":
    main()