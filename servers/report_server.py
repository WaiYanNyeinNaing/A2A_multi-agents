# servers/report_server.py
"""
Report Agent Server
Starts the Report Writing agent on port 8004
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import ReportAgent
from core import serve_agent_a2a

if __name__ == "__main__":
    agent = ReportAgent()
    agent_info = agent.get_agent_info()
    print(f"📊 Starting Report Writing Agent on port 8004")
    serve_agent_a2a(agent, agent_info, port=8004)