#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import signal
import socket
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

def find_available_port(start=8082, end=8090):
    """Find an available port in the given range."""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except:
                continue
    return start

def kill_existing_processes():
    """Kill any existing backend or frontend processes."""
    subprocess.run(['pkill', '-f', 'uvicorn open_webui.main:app'], stderr=subprocess.DEVNULL)
    subprocess.run(['pkill', '-f', 'vite dev'], stderr=subprocess.DEVNULL)
    time.sleep(1)

def main():
    # Kill existing processes
    kill_existing_processes()
    
    # Find available port
    backend_port = find_available_port()
    
    print("=" * 40)
    print("Starting Open WebUI Development")
    print(f"Backend:  http://localhost:{backend_port}")
    print(f"Frontend: http://localhost:5173")
    print("=" * 40)
    
    # Set environment variables
    env = os.environ.copy()
    env['BACKEND_PORT'] = str(backend_port)
    
    # Write .env file
    with open(PROJECT_ROOT / '.env', 'w') as f:
        f.write(f"BACKEND_PORT={backend_port}\n")
        f.write(f"VITE_API_BASE_URL=http://localhost:{backend_port}\n")
    
    # Start backend
    print(f"Starting backend on port {backend_port}...")
    backend_process = subprocess.Popen(
        ['./dev.sh'],
        cwd=PROJECT_ROOT / 'backend',
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait for backend to be ready
    print("Waiting for backend to start...")
    for i in range(30):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect(('localhost', backend_port))
                print("✓ Backend is ready!")
                break
        except:
            time.sleep(1)
    else:
        print("Warning: Backend may not be fully started")
    
    # Start frontend
    print("Starting frontend...")
    frontend_process = subprocess.Popen(
        ['npm', 'run', 'dev:frontend'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Print output from both processes
    def handle_output(process, prefix):
        while True:
            line = process.stdout.readline()
            if not line:
                break
            print(f"[{prefix}] {line}", end='')
    
    # Handle Ctrl+C
    def signal_handler(sig, frame):
        print("\nShutting down...")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Monitor processes
    try:
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("Backend process terminated")
                frontend_process.terminate()
                break
            if frontend_process.poll() is not None:
                print("Frontend process terminated")
                backend_process.terminate()
                break
            
            # Read output from backend
            line = backend_process.stdout.readline()
            if line:
                print(f"[Backend] {line}", end='')
            
            # Read output from frontend
            line = frontend_process.stdout.readline()
            if line:
                print(f"[Frontend] {line}", end='')
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()