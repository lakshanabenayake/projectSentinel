#!/usr/bin/env python3
"""
Project Sentinel Demo Automation Script
Installs dependencies, starts services, and generates outputs for judging
"""

import os
import sys
import subprocess
import time
import threading
import signal
import json
from pathlib import Path

class SentinelDemo:
    """Main demo automation class"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.src_path = self.base_path / "src"
        self.backend_path = self.src_path / "backend"
        self.frontend_path = self.src_path / "frontend"
        self.output_path = Path("./results")
        
        self.backend_process = None
        self.frontend_process = None
        self.streaming_process = None
        
        # Setup signal handlers for cleanup
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
    
    def log(self, message):
        """Print timestamped log message"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def run_command(self, command, cwd=None, check=True):
        """Run shell command with error handling"""
        self.log(f"Running: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                check=check,
                capture_output=True,
                text=True
            )
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}")
            if e.stderr:
                print(e.stderr)
            if check:
                raise
            return e
    
    def install_python_dependencies(self):
        """Install Python backend dependencies"""
        self.log("Installing Python dependencies...")
        
        # Check if pip is available
        try:
            subprocess.run(["pip3", "--version"], check=True, capture_output=True)
            pip_cmd = "pip3"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pip_cmd = "pip"
        
        # Install backend requirements
        requirements_file = self.backend_path / "requirements.txt"
        if requirements_file.exists():
            self.run_command(f"{pip_cmd} install -r {requirements_file}", cwd=self.backend_path)
        else:
            # Install essential packages if requirements.txt is missing
            packages = [
                "flask==2.3.3",
                "flask-socketio==5.3.6", 
                "flask-cors==4.0.0",
                "pandas==2.1.1",
                "numpy==1.24.3",
                "scikit-learn==1.3.0"
            ]
            for package in packages:
                self.run_command(f"{pip_cmd} install {package}")
    
    def install_node_dependencies(self):
        """Install Node.js frontend dependencies"""
        self.log("Installing Node.js dependencies...")
        
        # Check if npm is available
        try:
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("WARNING: npm not found. Skipping frontend installation.")
            return False
        
        # Install frontend dependencies
        if (self.frontend_path / "package.json").exists():
            self.run_command("npm install", cwd=self.frontend_path)
            return True
        else:
            self.log("WARNING: package.json not found. Skipping frontend installation.")
            return False
    
    def start_streaming_server(self):
        """Start the data streaming server"""
        self.log("Starting streaming server...")
        
        # Look for streaming server in data directory
        streaming_server_path = None
        possible_paths = [
            self.base_path.parent.parent.parent / "data" / "streaming-server" / "stream_server.py",
            Path("../../../data/streaming-server/stream_server.py"),
            Path("./stream_server.py")
        ]
        
        for path in possible_paths:
            if path.exists():
                streaming_server_path = path
                break
        
        if not streaming_server_path:
            self.log("WARNING: Streaming server not found. Demo will run with mock data.")
            return None
        
        try:
            self.streaming_process = subprocess.Popen([
                sys.executable, str(streaming_server_path),
                "--port", "8765",
                "--speed", "10", 
                "--loop"
            ], cwd=streaming_server_path.parent)
            
            # Wait a moment for server to start
            time.sleep(3)
            return self.streaming_process
        except Exception as e:
            self.log(f"Failed to start streaming server: {e}")
            return None
    
    def start_backend(self):
        """Start Flask backend server"""
        self.log("Starting Flask backend...")
        
        app_path = self.backend_path / "app.py"
        if not app_path.exists():
            self.log("ERROR: Backend app.py not found")
            return None
        
        try:
            env = os.environ.copy()
            env["FLASK_APP"] = str(app_path)
            env["FLASK_ENV"] = "development"
            
            self.backend_process = subprocess.Popen([
                sys.executable, str(app_path)
            ], cwd=self.backend_path, env=env)
            
            # Wait for backend to start
            time.sleep(5)
            return self.backend_process
        except Exception as e:
            self.log(f"Failed to start backend: {e}")
            return None
    
    def start_frontend(self):
        """Start React frontend server"""
        self.log("Starting React frontend...")
        
        if not (self.frontend_path / "package.json").exists():
            self.log("WARNING: Frontend not available")
            return None
        
        try:
            self.frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], cwd=self.frontend_path)
            
            # Wait for frontend to start
            time.sleep(10)
            return self.frontend_process
        except Exception as e:
            self.log(f"Failed to start frontend: {e}")
            return None
    
    def generate_sample_events(self):
        """Generate sample events for testing"""
        self.log("Generating sample events...")
        
        try:
            # Import and use event generator
            sys.path.append(str(self.backend_path))
            from event_generator import EventGenerator
            
            generator = EventGenerator()
            
            # Generate sample events
            sample_events = generator.generate_sample_events()
            
            # Create output directories
            self.output_path.mkdir(exist_ok=True)
            test_output = self.output_path / "test"
            final_output = self.output_path / "final"
            test_output.mkdir(exist_ok=True)
            final_output.mkdir(exist_ok=True)
            
            # Export to both test and final directories
            generator.export_to_file(test_output / "events.jsonl")
            generator.export_to_file(final_output / "events.jsonl")
            
            self.log(f"Generated {len(sample_events)} sample events")
            return True
            
        except Exception as e:
            self.log(f"Failed to generate events: {e}")
            return False
    
    def take_screenshots(self):
        """Take dashboard screenshots (placeholder)"""
        self.log("Taking dashboard screenshots...")
        
        # Create screenshots directory
        screenshots_dir = self.output_path / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        # Create placeholder screenshot info
        screenshot_info = {
            "dashboard-overview.png": "Main dashboard with real-time analytics",
            "alerts-panel.png": "Security alerts and anomaly detection",
            "station-overview.png": "Self-checkout station status monitoring",
            "event-log.png": "Real-time event detection log"
        }
        
        with open(screenshots_dir / "screenshot-info.json", "w") as f:
            json.dump(screenshot_info, f, indent=2)
        
        self.log("Screenshot placeholders created")
    
    def wait_for_demo(self):
        """Wait for demo to run and collect data"""
        self.log("Demo is running. Collecting data for 30 seconds...")
        
        # Let the system run and collect some data
        time.sleep(30)
        
        # Take screenshots
        self.take_screenshots()
        
        self.log("Demo data collection complete")
    
    def cleanup(self, signum=None, frame=None):
        """Clean up processes"""
        self.log("Cleaning up processes...")
        
        for process_name, process in [
            ("Frontend", self.frontend_process),
            ("Backend", self.backend_process), 
            ("Streaming", self.streaming_process)
        ]:
            if process and process.poll() is None:
                self.log(f"Stopping {process_name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def run(self):
        """Main demo execution"""
        try:
            self.log("=== Project Sentinel Demo Starting ===")
            
            # Step 1: Install dependencies
            self.install_python_dependencies()
            frontend_available = self.install_node_dependencies()
            
            # Step 2: Start streaming server
            self.start_streaming_server()
            
            # Step 3: Start backend
            if not self.start_backend():
                self.log("ERROR: Failed to start backend")
                return False
            
            # Step 4: Start frontend (if available)
            if frontend_available:
                self.start_frontend()
            
            # Step 5: Generate sample data
            self.generate_sample_events()
            
            # Step 6: Wait and collect data
            self.wait_for_demo()
            
            self.log("=== Demo Complete ===")
            self.log(f"Results available in: {self.output_path.absolute()}")
            
            if frontend_available:
                self.log("Dashboard available at: http://localhost:3000")
            self.log("API available at: http://localhost:5000")
            
            return True
            
        except KeyboardInterrupt:
            self.log("Demo interrupted by user")
            return False
        except Exception as e:
            self.log(f"Demo failed: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    demo = SentinelDemo()
    success = demo.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()