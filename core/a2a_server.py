# a2a_server.py
"""
A2A Protocol Server for Agent Communication
- Wraps agents to be A2A-compliant
- Handles JSON-RPC requests/responses
- Provides Agent Card discovery
"""

import os
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class TaskStatus(BaseModel):
    state: str
    message: Optional[Dict[str, Any]] = None
    timestamp: str

class Task(BaseModel):
    id: str
    status: TaskStatus
    artifacts: Optional[list] = None

class A2AServer:
    """A2A Protocol Server"""
    
    def __init__(self, agent, agent_info: Dict[str, Any], port: int = 8000):
        self.agent = agent
        self.agent_info = agent_info
        self.port = port
        self.tasks = {}  # In-memory task storage
        self.app = FastAPI(title=f"A2A Server - {agent_info['name']}")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes for A2A protocol."""
        
        @self.app.get("/.well-known/agent.json")
        async def get_agent_card():
            """Return Agent Card for discovery."""
            return self.generate_agent_card()
        
        @self.app.post("/a2a")
        async def handle_a2a_request(request: JSONRPCRequest):
            """Handle A2A JSON-RPC requests."""
            try:
                if request.method == "tasks/send":
                    result = await self.handle_task_send(request.params)
                elif request.method == "tasks/get":
                    result = await self.handle_task_get(request.params)
                elif request.method == "tasks/cancel":
                    result = await self.handle_task_cancel(request.params)
                else:
                    raise HTTPException(status_code=400, detail="Method not found")
                
                return JSONRPCResponse(id=request.id, result=result)
                
            except Exception as e:
                logger.error(f"❌ A2A request failed: {e}")
                return JSONRPCResponse(
                    id=request.id,
                    error={"code": -32603, "message": "Internal error", "data": str(e)}
                )
    
    def generate_agent_card(self) -> Dict[str, Any]:
        """Generate Agent Card for A2A discovery."""
        base_url = f"http://localhost:{self.port}"
        
        # Map agent capabilities to skills
        skills = []
        for capability in self.agent_info.get("capabilities", []):
            if capability == "generate_image":
                skills.append({
                    "id": "generate_image",
                    "name": "Image Generation",
                    "description": "Generate images from text descriptions",
                    "tags": ["image", "generation", "ai"],
                    "examples": ["Generate a sunset landscape", "Create a robot illustration"]
                })
            elif capability == "write_article":
                skills.append({
                    "id": "write_article", 
                    "name": "Article Writing",
                    "description": "Write articles and content on any topic",
                    "tags": ["writing", "content", "articles"],
                    "examples": ["Write about climate change", "Create a tech article"]
                })
            elif capability == "request_analysis":
                skills.append({
                    "id": "process_request",
                    "name": "Request Processing",
                    "description": "Analyze and coordinate complex user requests",
                    "tags": ["coordination", "analysis", "orchestration"],
                    "examples": ["Create article and image", "Coordinate multiple tasks"]
                })
        
        return {
            "name": self.agent_info["name"],
            "description": f"A2A-enabled {self.agent_info['type']} agent",
            "url": f"{base_url}/a2a",
            "version": "1.0.0",
            "capabilities": {
                "streaming": False,
                "pushNotifications": False
            },
            "defaultInputModes": ["text/plain", "application/json"],
            "defaultOutputModes": ["text/plain", "application/json", "image/png"],
            "skills": skills
        }
    
    async def handle_task_send(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tasks/send method."""
        task_id = params.get("id")
        message = params.get("message", {})
        
        # Extract user message
        user_input = ""
        for part in message.get("parts", []):
            if part.get("type") == "text":
                user_input += part.get("text", "")
        
        logger.info(f"📨 Processing task {task_id}: {user_input}")
        
        # Create task
        task = Task(
            id=task_id,
            status=TaskStatus(
                state="working",
                timestamp=datetime.now().isoformat()
            )
        )
        self.tasks[task_id] = task
        
        try:
            # Route based on agent type and capabilities
            agent_type = self.agent_info.get("type")
            
            if agent_type == "image_generation":
                # Image generation agent - call the function directly
                if hasattr(self.agent, 'adk_agent') and self.agent.adk_agent.tools:
                    # Get the actual function from the FunctionTool
                    tool_function = self.agent.adk_agent.tools[0].func  # Use .func instead of .function
                    result = tool_function(user_input, style="professional")
                else:
                    result = self.agent.generate_image(user_input)
                    
            elif agent_type == "content_writing":
                # Writing agent - call the function directly
                if hasattr(self.agent, 'adk_agent') and self.agent.adk_agent.tools:
                    # Get the actual function from the FunctionTool
                    tool_function = self.agent.adk_agent.tools[0].func  # Use .func instead of .function
                    result = tool_function(user_input, style="informative")
                else:
                    result = self.agent.write_article(user_input)
                    
            elif agent_type == "orchestrator":
                # Assistant agent - handle processing
                result = self.agent.process_user_request(user_input)
                    
            elif agent_type == "research":
                # Research agent - call research_topic method
                result = self.agent.research_topic(user_input)
                
            elif agent_type == "report":
                # Report agent - call write_research_report method
                result = self.agent.write_research_report(user_input)
                    
            else:
                result = {"success": False, "error": f"Unknown agent type: {agent_type}"}
            
            # Update task with result
            if result.get("success"):
                task.status.state = "completed"
                task.artifacts = [self.create_artifact(result)]
                task.status.message = {
                    "role": "agent", 
                    "parts": [{"type": "text", "text": "Task completed successfully"}]
                }
            else:
                task.status.state = "failed"
                error_msg = result.get("error", "Unknown error occurred")
                task.status.message = {
                    "role": "agent", 
                    "parts": [{"type": "text", "text": f"Task failed: {error_msg}"}]
                }
            
            task.status.timestamp = datetime.now().isoformat()
            self.tasks[task_id] = task
            
            return task.dict()
            
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            task.status.state = "failed"
            task.status.message = {
                "role": "agent", 
                "parts": [{"type": "text", "text": f"Execution error: {str(e)}"}]
            }
            task.status.timestamp = datetime.now().isoformat()
            self.tasks[task_id] = task
            return task.dict()
    
    async def handle_task_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tasks/get method."""
        task_id = params.get("id")
        
        if task_id not in self.tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return self.tasks[task_id].dict()
    
    async def handle_task_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tasks/cancel method."""
        task_id = params.get("id")
        
        if task_id not in self.tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = self.tasks[task_id]
        if task.status.state in ["completed", "failed", "canceled"]:
            return task.dict()
        
        task.status.state = "canceled"
        task.status.timestamp = datetime.now().isoformat()
        self.tasks[task_id] = task
        
        return task.dict()
    
    def create_artifact(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create artifact from agent result."""
        parts = []
        import json
        
        # Debug logging
        logger.info(f"🔍 Creating artifact for result with keys: {list(result.keys())}")
        
        # Handle different result types with proper JSON serialization (order matters!)
        if "summary" in result and "total_results" in result:  # Research agent
            logger.info("📊 Processing research agent result")
            parts.append({"type": "text", "text": json.dumps(result, indent=2)})
        elif "file_path" in result and "generation_successful" in result:  # New file-based image agent
            logger.info("🎨 Processing image agent result")
            parts.append({"type": "text", "text": json.dumps(result, indent=2)})
        elif "content" in result and "word_count" in result:  # Writing agent - serialize to JSON for assistant
            logger.info("✍️ Processing writing agent result")
            parts.append({"type": "text", "text": json.dumps(result, indent=2)})
        elif "content" in result:  # Legacy content format
            logger.info("📝 Processing legacy content format")
            parts.append({"type": "text", "text": result["content"]})
        elif "image_data" in result:  # Legacy base64 image data
            logger.info("🖼️ Processing legacy image data")
            parts.append({
                "type": "file",
                "file": {
                    "name": f"generated_image_{result.get('image_id', 'unknown')}.png",
                    "mimeType": "image/png",
                    "bytes": result["image_data"]
                }
            })
        elif "summary" in result and "total_results" in result:  # Research agent
            # Research agent results - serialize to JSON for assistant to parse
            import json
            parts.append({"type": "text", "text": json.dumps(result, indent=2)})
        elif "final_response" in result:  # Assistant agent
            parts.append({"type": "text", "text": result["final_response"]})
            
            # Also check if assistant coordinated and got image data
            if "agent_results" in result:
                agent_results = result["agent_results"]
                if "image_result" in agent_results:
                    image_result = agent_results["image_result"]
                    if image_result.get("success") and "image_data" in image_result:
                        parts.append({
                            "type": "file",
                            "file": {
                                "name": image_result.get("image_name", "coordinated_image.png"),
                                "mimeType": image_result.get("mime_type", "image/png"),
                                "bytes": image_result["image_data"]
                            }
                        })
        elif "analysis" in result and "agent_results" in result:  # Assistant agent detailed result
            # Create a comprehensive response for assistant
            response_text = result.get("final_response", "Task completed")
            parts.append({"type": "text", "text": response_text})
            
            # Check for image data in agent results
            agent_results = result.get("agent_results", {})
            
            # Handle image agent results
            if "image" in agent_results:
                image_result = agent_results["image"]
                if image_result.get("success") and image_result.get("artifacts"):
                    # Extract image artifacts from the image agent response
                    for artifact in image_result["artifacts"]:
                        for part in artifact.get("parts", []):
                            if part.get("type") == "file":
                                parts.append(part)
            
            # Legacy support for old format
            elif "image_result" in agent_results:
                image_result = agent_results["image_result"]
                if image_result.get("success") and "image_data" in image_result:
                    parts.append({
                        "type": "file",
                        "file": {
                            "name": image_result.get("image_name", "generated_image.png"),
                            "mimeType": image_result.get("mime_type", "image/png"),
                            "bytes": image_result["image_data"]
                        }
                    })
            
            # Also include the structured data
            parts.append({
                "type": "data", 
                "data": {
                    "analysis": result.get("analysis"),
                    "agent_results": result.get("agent_results"),
                    "request_id": result.get("request_id")
                }
            })
        else:
            # Generic response - convert entire result to data part
            parts.append({"type": "data", "data": result})
        
        return {
            "name": f"Result_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "parts": parts,
            "index": 0
        }
    
    def run(self):
        """Run the A2A server."""
        logger.info(f"🚀 Starting A2A server for {self.agent_info['name']} on port {self.port}")
        logger.info(f"📋 Agent Card: http://localhost:{self.port}/.well-known/agent.json")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

# Convenience function to start agent as A2A server
def serve_agent_a2a(agent, agent_info: Dict[str, Any], port: int = 8000):
    """Start an agent as an A2A server."""
    server = A2AServer(agent, agent_info, port)
    server.run()

