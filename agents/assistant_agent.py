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
        """Analyze user request to determine which agents to involve."""
        prompt = f'''
        Analyze this user request to determine which agents should be involved:
        
        Request: "{user_input}"
        
        Available agents:
        - image: Generate images, create visuals, edit images
        - writing: Content creation, text editing, creative writing
        - research: Web search, fact-checking, information gathering  
        - report: Comprehensive reports, data analysis, structured documents
        
        Respond with JSON only:
        {{
            "required_agents": ["agent1", "agent2"],
            "primary_task": "brief description",
            "coordination_strategy": "sequential|parallel|hybrid"
        }}
        '''
        
        try:
            response = self.call_gemini_api(prompt)
            # Parse JSON response - simplified for now
            if "image" in user_input.lower() or "visual" in user_input.lower():
                return {"required_agents": ["image"], "primary_task": "image generation", "coordination_strategy": "sequential"}
            elif "research" in user_input.lower() or "find" in user_input.lower():
                return {"required_agents": ["research"], "primary_task": "research", "coordination_strategy": "sequential"}
            elif "report" in user_input.lower():
                return {"required_agents": ["research", "report"], "primary_task": "report creation", "coordination_strategy": "sequential"}
            else:
                return {"required_agents": ["writing"], "primary_task": "text generation", "coordination_strategy": "sequential"}
        except:
            # Fallback analysis
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