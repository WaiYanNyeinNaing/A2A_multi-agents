# core/a2a_client.py
"""
A2A Protocol Client for Agent Communication
- Discovers other agents via Agent Cards
- Sends JSON-RPC requests to A2A agents
- Handles task lifecycle and responses
"""

import httpx
import uuid
import asyncio
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2AClient:
    """A2A Protocol Client for communicating with other agents"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.agent_cards = {}  # Cache for discovered agent cards
    
    async def discover_agent(self, base_url: str) -> Dict[str, Any]:
        """Discover agent by fetching its Agent Card."""
        agent_card_url = f"{base_url}/.well-known/agent.json"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(agent_card_url)
                response.raise_for_status()
                
                agent_card = response.json()
                self.agent_cards[base_url] = agent_card
                
                logger.info(f"🔍 Discovered agent: {agent_card.get('name')} at {base_url}")
                return agent_card
                
        except Exception as e:
            logger.error(f"❌ Failed to discover agent at {base_url}: {e}")
            raise
    
    async def send_message(self, agent_url: str, message: str, task_id: str = None) -> Dict[str, Any]:
        """Send message to an A2A agent."""
        if not task_id:
            task_id = str(uuid.uuid4())
        
        # Prepare JSON-RPC request
        request_payload = {
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }
            },
            "id": str(uuid.uuid4())
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get agent card if not cached
                if agent_url not in self.agent_cards:
                    await self.discover_agent(agent_url)
                
                agent_card = self.agent_cards[agent_url]
                a2a_endpoint = agent_card["url"]
                
                logger.info(f"📤 Sending message to {agent_card['name']}: {message[:50]}...")
                
                response = await client.post(
                    a2a_endpoint,
                    json=request_payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                
                if "error" in result and result["error"] is not None:
                    logger.error(f"❌ Agent returned error: {result['error']}")
                    return {"success": False, "error": result["error"], "task_id": task_id}
                
                task_data = result.get("result", {})
                logger.info(f"✅ Message sent successfully, task state: {task_data.get('status', {}).get('state')}")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "task_data": task_data,
                    "agent_name": agent_card["name"]
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to send message to {agent_url}: {e}")
            return {"success": False, "error": str(e), "task_id": task_id}
    
    async def get_task_status(self, agent_url: str, task_id: str) -> Dict[str, Any]:
        """Get status of a task from an A2A agent."""
        request_payload = {
            "jsonrpc": "2.0",
            "method": "tasks/get",
            "params": {
                "id": task_id
            },
            "id": str(uuid.uuid4())
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if agent_url not in self.agent_cards:
                    await self.discover_agent(agent_url)
                
                agent_card = self.agent_cards[agent_url]
                a2a_endpoint = agent_card["url"]
                
                response = await client.post(
                    a2a_endpoint,
                    json=request_payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                
                if "error" in result and result["error"] is not None:
                    return {"success": False, "error": result["error"]}
                
                return {"success": True, "task_data": result.get("result", {})}
                
        except Exception as e:
            logger.error(f"❌ Failed to get task status: {e}")
            return {"success": False, "error": str(e)}
    
    async def wait_for_completion(self, agent_url: str, task_id: str, max_wait: int = 60) -> Dict[str, Any]:
        """Wait for task completion with polling."""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status_result = await self.get_task_status(agent_url, task_id)
            
            if not status_result["success"]:
                return status_result
            
            task_data = status_result["task_data"]
            state = task_data.get("status", {}).get("state")
            
            if state in ["completed", "failed", "canceled"]:
                logger.info(f"✅ Task {task_id} finished with state: {state}")
                return {"success": True, "task_data": task_data, "final_state": state}
            
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > max_wait:
                logger.warning(f"⏰ Task {task_id} timeout after {max_wait}s")
                return {"success": False, "error": "Task timeout", "task_data": task_data}
            
            # Wait before next poll
            await asyncio.sleep(2)
    
    async def send_and_wait(self, agent_url: str, message: str, max_wait: int = 60) -> Dict[str, Any]:
        """Send message and wait for completion."""
        # Send message
        send_result = await self.send_message(agent_url, message)
        
        if not send_result["success"]:
            return send_result
        
        task_id = send_result["task_id"]
        
        # Check if already completed
        task_data = send_result["task_data"]
        state = task_data.get("status", {}).get("state")
        
        if state in ["completed", "failed", "canceled"]:
            return {
                "success": True,
                "task_data": task_data,
                "final_state": state,
                "agent_name": send_result["agent_name"]
            }
        
        # Wait for completion
        wait_result = await self.wait_for_completion(agent_url, task_id, max_wait)
        
        if wait_result["success"]:
            wait_result["agent_name"] = send_result["agent_name"]
        
        return wait_result
    
    def extract_result(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract useful result from task data."""
        artifacts = task_data.get("artifacts", [])
        
        if not artifacts:
            return {"type": "no_artifacts", "data": None}
        
        artifact = artifacts[0]  # Get first artifact
        parts = artifact.get("parts", [])
        
        if not parts:
            return {"type": "no_parts", "data": None}
        
        part = parts[0]  # Get first part
        part_type = part.get("type")
        
        if part_type == "text":
            return {"type": "text", "data": part.get("text")}
        elif part_type == "file":
            file_info = part.get("file", {})
            return {
                "type": "file",
                "data": {
                    "name": file_info.get("name"),
                    "mimeType": file_info.get("mimeType"),
                    "bytes": file_info.get("bytes"),
                    "uri": file_info.get("uri")
                }
            }
        elif part_type == "data":
            return {"type": "data", "data": part.get("data")}
        
        return {"type": "unknown", "data": part}
    
    async def discover_multiple_agents(self, agent_urls: list) -> Dict[str, Dict[str, Any]]:
        """Discover multiple agents concurrently."""
        tasks = [self.discover_agent(url) for url in agent_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        discovered = {}
        for i, result in enumerate(results):
            url = agent_urls[i]
            if isinstance(result, Exception):
                logger.error(f"❌ Failed to discover {url}: {result}")
            else:
                discovered[url] = result
        
        return discovered