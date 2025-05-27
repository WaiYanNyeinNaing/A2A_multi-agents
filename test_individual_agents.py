#!/usr/bin/env python3
"""
Test individual agents to debug their JSON responses
"""
import sys
import asyncio
import httpx
import json

async def test_individual_agent(port, agent_name, task):
    """Test an individual agent directly"""
    
    print(f"\n🔍 Testing {agent_name} on port {port}")
    print(f"Task: {task}")
    print("-" * 50)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "id": f"test-{agent_name}-001",
            "message": {
                "parts": [{"type": "text", "text": task}]
            }
        },
        "id": "req-001"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"http://localhost:{port}/a2a", json=payload)
            response.raise_for_status()
            result = response.json()
            
            print("✅ Response received!")
            
            # Check artifacts
            artifacts = result.get("result", {}).get("artifacts", [])
            if artifacts and len(artifacts) > 0:
                first_artifact = artifacts[0]
                if "parts" in first_artifact and first_artifact["parts"]:
                    first_part = first_artifact["parts"][0]
                    if first_part.get("type") == "text":
                        content = first_part.get("text", "")
                        print(f"Content preview: {content[:300]}...")
                        
                        # Try to parse as JSON
                        if content.strip().startswith("{"):
                            try:
                                parsed_data = json.loads(content)
                                print(f"✅ JSON parsed successfully!")
                                print(f"Keys: {list(parsed_data.keys())}")
                                
                                # Show relevant fields
                                if agent_name == "research":
                                    print(f"Summary: {parsed_data.get('summary', 'N/A')[:100]}...")
                                    print(f"Total results: {parsed_data.get('total_results', 'N/A')}")
                                elif agent_name == "writing":
                                    print(f"Title: {parsed_data.get('title', 'N/A')}")
                                    print(f"Word count: {parsed_data.get('word_count', 'N/A')}")
                                    print(f"Content preview: {parsed_data.get('content', 'N/A')[:200]}...")
                                elif agent_name == "image":
                                    print(f"File path: {parsed_data.get('file_path', 'N/A')}")
                                    print(f"File name: {parsed_data.get('file_name', 'N/A')}")
                                    print(f"Generation successful: {parsed_data.get('generation_successful', 'N/A')}")
                                    
                            except json.JSONDecodeError as e:
                                print(f"❌ JSON parse error: {e}")
                        else:
                            print("⚠️ Content is not JSON format")
                    else:
                        print(f"❌ First part is not text: {first_part.get('type')}")
                else:
                    print("❌ No parts in artifact")
                    print(f"Artifact keys: {list(first_artifact.keys())}")
            else:
                print("❌ No artifacts in response")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Test all individual agents"""
    print("🧪 Testing Individual A2A Agents")
    print("=" * 50)
    
    # Test each agent
    await test_individual_agent(8003, "research", "MCP protocol for AI agents")
    await test_individual_agent(8002, "writing", "write an article about MCP protocol")
    await test_individual_agent(8001, "image", "generate an image about MCP protocol")

if __name__ == "__main__":
    asyncio.run(main())