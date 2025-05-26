# servers/image_server.py
"""
Image Generation Agent Server
Starts the Image Generation agent on port 8001
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import ImageAgent
from core import serve_agent_a2a

if __name__ == "__main__":
    agent = ImageAgent()
    agent_info = agent.get_agent_info()
    print(f"🎨 Starting Image Generation Agent on port 8001")
    serve_agent_a2a(agent, agent_info, port=8001)