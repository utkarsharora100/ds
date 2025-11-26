#!/usr/bin/env python3
"""
Combined startup script for frontend + backend
Runs both FastAPI backend and HTTP server for frontend
"""
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print("\n Shutting down services...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    print(" Starting Movie Booking System (Combined Frontend + Backend)")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Start backend (FastAPI)
    print("\n Starting Backend API (port 9000)...")
    backend_process = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "Application_server.Application_server:app",
            "--host", "0.0.0.0",
            "--port", "9000"
        ],
        cwd=project_root
    )
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start frontend (HTTP server)
    print(" Starting Frontend Web Server (port 3000)...")
    frontend_dir = project_root / "web"
    frontend_process = subprocess.Popen(
        [
            sys.executable, "-m", "http.server",
            "3000",
            "--bind", "0.0.0.0"
        ],
        cwd=frontend_dir
    )
    
    print("\nServices started!")
    print("   Backend API:  http://localhost:9000")
    print("   Frontend UI:  http://localhost:3000")
    print("\nPress Ctrl+C to stop all services\n")
    
    try:
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("Services stopped")

if __name__ == "__main__":
    main()

