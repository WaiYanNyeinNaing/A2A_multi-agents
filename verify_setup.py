#!/usr/bin/env python3
"""
Quick verification script to test A2A system setup
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    """Test that all required packages can be imported."""
    print("🔍 Checking imports...")
    
    try:
        import google.generativeai
        print("  ✅ google-generativeai")
    except ImportError as e:
        print(f"  ❌ google-generativeai: {e}")
        return False
    
    try:
        import fastapi
        print("  ✅ fastapi")
    except ImportError as e:
        print(f"  ❌ fastapi: {e}")
        return False
    
    try:
        import uvicorn
        print("  ✅ uvicorn")
    except ImportError as e:
        print(f"  ❌ uvicorn: {e}")
        return False
    
    try:
        import httpx
        print("  ✅ httpx")
    except ImportError as e:
        print(f"  ❌ httpx: {e}")
        return False
    
    return True

def check_agents():
    """Test that agent modules can be imported."""
    print("\n🤖 Checking agent modules...")
    
    try:
        from agents import BaseAgent, AssistantAgent, ImageAgent, WritingAgent, ResearchAgent, ReportAgent
        print("  ✅ All agent classes imported successfully")
        print(f"    • BaseAgent, AssistantAgent, ImageAgent, WritingAgent")
        print(f"    • ResearchAgent, ReportAgent")
        return True
    except ImportError as e:
        print(f"  ❌ Agent import failed: {e}")
        return False

def check_core():
    """Test that core modules work."""
    print("\n🏗️ Checking core modules...")
    
    try:
        from core import A2AClient, A2AServer
        print("  ✅ Core A2A modules imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Core import failed: {e}")
        return False

def check_env():
    """Check environment configuration."""
    print("\n⚙️ Checking environment setup...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("  ❌ .env file not found")
        return False
    
    print("  ✅ .env file exists")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("  ⚠️  GEMINI_API_KEY not set or using placeholder")
        print("     Edit .env file and add your actual API key")
        return False
    
    print("  ✅ GEMINI_API_KEY is configured")
    return True

def main():
    """Run all verification checks."""
    print("🚀 A2A Multi-Agent System Setup Verification")
    print("=" * 50)
    
    checks = [
        check_imports,
        check_agents, 
        check_core,
        check_env
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("🎉 All checks passed! Your A2A system is ready.")
        print("\nNext steps:")
        print("1. Start the agents: uv run python servers/assistant_server.py")
        print("2. Start interactive interface: uv run python tools/interactive_interface.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()