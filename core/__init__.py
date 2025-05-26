# core/__init__.py
"""
A2A Multi-Agent System - Core Components
"""

from .a2a_client import A2AClient
from .a2a_server import A2AServer, serve_agent_a2a

__all__ = ['A2AClient', 'A2AServer', 'serve_agent_a2a']