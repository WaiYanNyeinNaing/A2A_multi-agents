#!/usr/bin/env python3
"""
Quick test script for the A2A multi-agent coordination system
"""
import sys
import asyncio
import httpx
import json

async def test_assistant_coordination():
    """Test the assistant agent coordination with research + writing + image"""
    
    print("🚀 Testing A2A Multi-Agent Coordination")
    print("=" * 50)
    
    # Payload for A2A protocol
    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "id": "test-coordination-001",
            "message": {
                "parts": [{"type": "text", "text": "research MCP protocol for AI agents and write a brief article about it and generate a visual"}]
            }
        },
        "id": "req-001"
    }
    
    try:
        # Configure HTTP client for Windows compatibility
        timeout_config = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)
        
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            print("📤 Sending coordination request to assistant agent...")
            response = await client.post("http://127.0.0.1:8000/a2a", json=payload)
            response.raise_for_status()
            result = response.json()
            
            print("✅ Response received!")
            print("Full result structure:")
            print(json.dumps(result, indent=2)[:2000])  # First 2000 chars
            
            # Extract and display the response
            artifacts = result.get("result", {}).get("artifacts", [])
            if artifacts and len(artifacts) > 0:
                first_artifact = artifacts[0]
                print(f"\n📋 First artifact type: {first_artifact.get('type')}")
                if first_artifact.get("type") == "text":
                    content = first_artifact.get("content", "")
                    print("\n📋 Assistant Response:")
                    print("-" * 40)
                    print(content[:1000])  # First 1000 chars
                    print("-" * 40)
                else:
                    print(f"Unexpected artifact type: {first_artifact.get('type')}")
                    print(f"Artifact keys: {list(first_artifact.keys())}")
            else:
                print("❌ No artifacts in response")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing A2A coordination system...")
    success = asyncio.run(test_assistant_coordination())
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")