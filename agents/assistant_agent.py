# agents/assistant_agent.py
"""
Assistant Agent using Google Gemini and A2A Protocol
- Inherits from BaseAgent for common functionality
- Main orchestrator that coordinates with specialized agents
"""

import os
import httpx
from typing import Dict, Any
from .base_agent import BaseAgent

class AssistantAgent(BaseAgent):
    """
    Main Assistant Agent that orchestrates tasks using A2A protocol
    """
    
    def __init__(self):
        super().__init__(agent_type="orchestrator")
        
        # A2A Agent URLs
        self.image_agent_url = os.getenv('IMAGE_AGENT_URL', 'http://localhost:8001')
        self.writer_agent_url = os.getenv('WRITER_AGENT_URL', 'http://localhost:8002')
        self.research_agent_url = os.getenv('RESEARCH_AGENT_URL', 'http://localhost:8003')
        self.report_agent_url = os.getenv('REPORT_AGENT_URL', 'http://localhost:8004')
    
    def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        Main function to process user requests and coordinate with other agents.
        
        Args:
            user_input: User's request/prompt
            
        Returns:
            Dict containing the coordinated response from multiple agents
        """
        try:
            # Analyze the request first
            analysis = self._analyze_request_sync(user_input)
            
            # Execute coordination
            agent_results = self._coordinate_agents_sync(analysis, user_input)
            
            # Generate final response
            final_response = self._generate_final_response_sync(user_input, analysis, agent_results)
            
            return self.create_success_response(
                request_id=self.generate_unique_id(),
                user_input=user_input,
                analysis=analysis,
                agent_results=agent_results,
                final_response=final_response
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "coordination_error")

    def _analyze_request_sync(self, user_input: str) -> Dict[str, Any]:
        """Analyze user request to determine which agents to involve using Gemini LLM."""
        prompt = f'''
You are an intelligent request analyzer for a multi-agent system. Analyze the user request and determine which specialized agents should handle it.

Available agents:
- image: Generate images, create visuals, illustrations, photos, artwork
- writing: Create articles, stories, content, text-based responses  
- research: Web search, fact-checking, gather information, investigate topics
- report: Create comprehensive reports, analyze data, structured documents

Examples:

User: "Create a picture of a sunset over mountains"
Analysis: {{"required_agents": ["image"], "primary_task": "image generation", "coordination_strategy": "sequential"}}

User: "Draw me a cute cartoon cat"  
Analysis: {{"required_agents": ["image"], "primary_task": "image generation", "coordination_strategy": "sequential"}}

User: "Write an article about renewable energy"
Analysis: {{"required_agents": ["writing"], "primary_task": "content creation", "coordination_strategy": "sequential"}}

User: "Research the latest developments in AI technology"
Analysis: {{"required_agents": ["research"], "primary_task": "information gathering", "coordination_strategy": "sequential"}}

User: "Find information about climate change and create a comprehensive report"
Analysis: {{"required_agents": ["research", "report"], "primary_task": "research and reporting", "coordination_strategy": "sequential"}}

User: "Research renewable energy trends and create an article with solar panel images"
Analysis: {{"required_agents": ["research", "writing", "image"], "primary_task": "multi-modal content creation", "coordination_strategy": "sequential"}}

User: "Make an illustration showing the water cycle"
Analysis: {{"required_agents": ["image"], "primary_task": "educational illustration", "coordination_strategy": "sequential"}}

User: "Generate a logo for my company"
Analysis: {{"required_agents": ["image"], "primary_task": "logo design", "coordination_strategy": "sequential"}}

Now analyze this request:
User: "{user_input}"
Analysis: '''
        
        try:
            response = self.call_gemini_api(prompt)
            
            # Try to parse JSON response from Gemini
            import json
            try:
                # Look for JSON in the response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    parsed = json.loads(json_str)
                    
                    # Validate the parsed response has required fields
                    if "required_agents" in parsed and "primary_task" in parsed:
                        return parsed
            except Exception as e:
                print(f"JSON parsing error: {e}")
            
            # Fallback: simple keyword-based analysis
            user_lower = user_input.lower()
            
            if any(word in user_lower for word in ["image", "picture", "photo", "draw", "sketch", "illustration", "visual", "artwork", "logo", "graphic"]):
                return {"required_agents": ["image"], "primary_task": "image generation", "coordination_strategy": "sequential"}
            elif any(word in user_lower for word in ["research", "find", "search", "investigate", "study"]):
                return {"required_agents": ["research"], "primary_task": "research", "coordination_strategy": "sequential"}
            elif any(word in user_lower for word in ["report", "analysis", "comprehensive"]):
                return {"required_agents": ["research", "report"], "primary_task": "report creation", "coordination_strategy": "sequential"}
            else:
                return {"required_agents": ["writing"], "primary_task": "text generation", "coordination_strategy": "sequential"}
            
        except Exception as e:
            print(f"Analysis error: {e}")
            # Ultimate fallback
            return {"required_agents": ["writing"], "primary_task": "general assistance", "coordination_strategy": "sequential"}

    def _coordinate_agents_sync(self, analysis: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Coordinate with required agents based on analysis."""
        results = {}
        required_agents = analysis.get("required_agents", [])
        
        for agent in required_agents:
            if agent == "image":
                results[agent] = self._call_agent_a2a(self.image_agent_url, user_input)
            elif agent == "writing":
                results[agent] = self._call_agent_a2a(self.writer_agent_url, user_input)
            elif agent == "research":
                results[agent] = self._call_agent_a2a(self.research_agent_url, user_input)
            elif agent == "report":
                results[agent] = self._call_agent_a2a(self.report_agent_url, user_input)
        
        return results

    def _call_agent_a2a(self, agent_url: str, user_input: str) -> Dict[str, Any]:
        """Make A2A protocol call to another agent."""
        try:
            task_id = self.generate_unique_id()
            payload = {
                "jsonrpc": "2.0",
                "method": "tasks/send",
                "params": {
                    "id": task_id,
                    "message": {
                        "parts": [{"type": "text", "text": user_input}]
                    }
                },
                "id": self.generate_unique_id()
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{agent_url}/a2a", json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Extract the actual result from A2A response
                if result.get("result") and result["result"].get("artifacts"):
                    return {"success": True, "artifacts": result["result"]["artifacts"]}
                else:
                    return {"success": False, "error": "No artifacts returned"}
                
        except Exception as e:
            return {"error": f"Agent communication failed: {str(e)}"}

    def _generate_final_response_sync(self, user_input: str, analysis: Dict[str, Any], agent_results: Dict[str, Any]) -> str:
        """Generate final response combining all agent results."""
        prompt = f'''
        Generate a final response to the user based on these results:
        
        User Request: "{user_input}"
        Analysis: {analysis}
        Agent Results: {agent_results}
        
        Provide a helpful, comprehensive response that incorporates the results from all agents.
        '''
        
        try:
            return self.call_gemini_api(prompt)
        except:
            return "I've processed your request using multiple specialized agents. Please check the individual agent results for details."

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": "Assistant Orchestrator",
            "type": "orchestrator",
            "model": self.model_name,
            "capabilities": ["coordination", "analysis", "multi_agent_orchestration"],
            "connected_agents": ["image", "writing", "research", "report"],
            "status": "ready" if self.gemini_client else "not_ready"
        }