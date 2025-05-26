#!/usr/bin/env python3
"""
Start All A2A Agent Servers
Convenient script to start all 5 agent servers in separate processes
"""

import subprocess
import sys
import time
import signal
import os

def start_server(script_path, port, name):
    """Start a server in a subprocess"""
    print(f"🚀 Starting {name} on port {port}...")
    cmd = [sys.executable, script_path]
    return subprocess.Popen(cmd, cwd=os.getcwd())

def main():
    """Start all agent servers"""
    print("🎯 A2A Multi-Agent System - Starting All Servers")
    print("=" * 60)
    
    servers = [
        ("servers/assistant_server.py", 8000, "Assistant Agent"),
        ("servers/image_server.py", 8001, "Image Agent"),
        ("servers/writing_server.py", 8002, "Writing Agent"),
        ("servers/research_server.py", 8003, "Research Agent"),
        ("servers/report_server.py", 8004, "Report Agent"),
    ]
    
    processes = []
    
    try:
        # Start all servers
        for script, port, name in servers:
            if os.path.exists(script):
                proc = start_server(script, port, name)
                processes.append((proc, name))
                time.sleep(2)  # Wait between starts
            else:
                print(f"❌ {script} not found")
        
        print(f"\n✅ Started {len(processes)} agent servers")
        print("🔗 Agent URLs:")
        for _, port, name in servers:
            print(f"   • {name}: http://localhost:{port}")
        
        print(f"\n🎮 Run the interactive interface:")
        print(f"   uv run python tools/interactive_interface.py")
        print(f"\n⏹️  Press Ctrl+C to stop all servers")
        
        # Wait for keyboard interrupt
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping all servers...")
        
        # Terminate all processes
        for proc, name in processes:
            try:
                proc.terminate()
                print(f"   Stopped {name}")
            except:
                pass
        
        # Wait for processes to terminate
        for proc, name in processes:
            try:
                proc.wait(timeout=5)
            except:
                proc.kill()  # Force kill if not terminated
        
        print("✅ All servers stopped")

if __name__ == "__main__":
    main()