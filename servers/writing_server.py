# servers/writing_server.py
"""
Writing Agent Server
Starts the Writing agent on port 8002
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import WritingAgent
from core import serve_agent_a2a

if __name__ == "__main__":
    agent = WritingAgent()
    agent_info = agent.get_agent_info()
    print(f"✍️ Starting Writing Agent on port 8002")
    serve_agent_a2a(agent, agent_info, port=8002)