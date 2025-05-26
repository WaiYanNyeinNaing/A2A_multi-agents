# servers/research_server.py
"""
Research Agent Server
Starts the Research agent on port 8003
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import ResearchAgent
from core import serve_agent_a2a

if __name__ == "__main__":
    agent = ResearchAgent()
    agent_info = agent.get_agent_info()
    print(f"🔍 Starting Research Agent on port 8003")
    serve_agent_a2a(agent, agent_info, port=8003)