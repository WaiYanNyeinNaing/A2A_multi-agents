# servers/assistant_server.py
"""
Assistant Agent Server
Starts the Assistant/Orchestrator agent on port 8000
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import AssistantAgent
from core import serve_agent_a2a

if __name__ == "__main__":
    agent = AssistantAgent()
    agent_info = agent.get_agent_info()
    print(f"🚀 Starting Assistant Agent on port 8000")
    serve_agent_a2a(agent, agent_info, port=8000)