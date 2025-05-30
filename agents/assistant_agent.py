# agents/assistant_agent.py
"""
Assistant Agent using Google Gemini and A2A Protocol
- Inherits from BaseAgent for common functionality
- Main orchestrator that coordinates with specialized agents
"""

import os
import httpx
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

class AssistantAgent(BaseAgent):
    """
    Main Assistant Agent that orchestrates tasks using A2A protocol
    """
    
    def __init__(self):
        super().__init__("orchestrator")
        
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # A2A Agent URLs (use 127.0.0.1 for Windows compatibility)
        self.image_agent_url = os.getenv('IMAGE_AGENT_URL', 'http://127.0.0.1:8001')
        self.writer_agent_url = os.getenv('WRITER_AGENT_URL', 'http://127.0.0.1:8002')
        self.research_agent_url = os.getenv('RESEARCH_AGENT_URL', 'http://127.0.0.1:8003')
        self.report_agent_url = os.getenv('REPORT_AGENT_URL', 'http://127.0.0.1:8004')
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
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

For multi-intent requests, identify ALL tasks and plan sequential execution:

Examples:

User: "Create a picture of a sunset over mountains"
Analysis: {{"required_agents": ["image"], "tasks": ["image generation"], "primary_task": "image generation", "coordination_strategy": "sequential"}}

User: "Research A2A protocol and generate an image for it"
Analysis: {{"required_agents": ["research", "image"], "tasks": ["research A2A protocol", "generate image based on research"], "primary_task": "research-enhanced image generation", "coordination_strategy": "sequential"}}

User: "Find information about climate change and create a comprehensive report"
Analysis: {{"required_agents": ["research", "report"], "tasks": ["research climate change", "create report from research"], "primary_task": "research and reporting", "coordination_strategy": "sequential"}}

User: "Research renewable energy trends, write an article, and create solar panel images"
Analysis: {{"required_agents": ["research", "writing", "image"], "tasks": ["research renewable energy", "write article from research", "generate solar panel images"], "primary_task": "comprehensive content creation", "coordination_strategy": "sequential"}}

User: "Write an article about AI and make an illustration for it"
Analysis: {{"required_agents": ["writing", "image"], "tasks": ["write AI article", "create illustration for article"], "primary_task": "article with visual", "coordination_strategy": "sequential"}}

User: "Research machine learning and create a report with diagrams"
Analysis: {{"required_agents": ["research", "report", "image"], "tasks": ["research machine learning", "create comprehensive report", "generate diagrams for report"], "primary_task": "documented research with visuals", "coordination_strategy": "sequential"}}

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
        """Coordinate with required agents based on analysis - sequential execution with context passing."""
        results = {}
        required_agents = analysis.get("required_agents", [])
        tasks = analysis.get("tasks", [])
        
        # Keep track of accumulated context for subsequent agents
        accumulated_context = {"original_request": user_input}
        
        self.logger.info(f"🎯 Starting sequential coordination for {len(required_agents)} agents")
        self.logger.info(f"📋 Planned tasks: {tasks}")
        
        # Log agent URLs for debugging
        self.logger.info("🔗 Agent URLs:")
        self.logger.info(f"   Image: {self.image_agent_url}")
        self.logger.info(f"   Writer: {self.writer_agent_url}") 
        self.logger.info(f"   Research: {self.research_agent_url}")
        self.logger.info(f"   Report: {self.report_agent_url}")
        
        for i, agent in enumerate(required_agents):
            self.logger.info(f"🔄 Step {i+1}/{len(required_agents)}: Executing {agent} agent")
            
            # Log current step without delays
            self.logger.info(f"🔄 Processing {agent} agent...")
            
            # Create context-aware prompt for each agent
            agent_prompt = self._create_context_aware_prompt(agent, user_input, accumulated_context, i, tasks)
            
            # Execute agent task directly
            try:
                if agent == "image":
                    results[agent] = self._call_agent_a2a(self.image_agent_url, agent_prompt)
                elif agent == "writing":
                    results[agent] = self._call_agent_a2a(self.writer_agent_url, agent_prompt)
                elif agent == "research":
                    results[agent] = self._call_agent_a2a(self.research_agent_url, agent_prompt)
                elif agent == "report":
                    results[agent] = self._call_agent_a2a(self.report_agent_url, agent_prompt)
            except Exception as e:
                self.logger.error(f"❌ Failed to call {agent} agent: {e}")
                results[agent] = {"success": False, "error": str(e)}
            
            # Add this agent's results to accumulated context for next agents
            if results[agent].get("success"):
                accumulated_context[f"{agent}_result"] = results[agent]
                self.logger.info(f"✅ {agent} agent completed successfully")
            else:
                self.logger.error(f"❌ {agent} agent failed: {results[agent].get('error')}")
        
        self.logger.info(f"🎉 All {len(required_agents)} agents completed")
        return results

    def _create_context_aware_prompt(self, agent: str, original_request: str, context: Dict[str, Any], step: int, tasks: List[str]) -> str:
        """Create context-aware prompt for each agent based on previous results."""
        
        # Get the specific task for this agent
        task_description = tasks[step] if step < len(tasks) else f"{agent} task"
        
        if agent == "research":
            # Research is usually first, so use original request
            return original_request
            
        elif agent == "image" and "research_result" in context:
            # Image generation after research - extract key topics only
            research_data = context["research_result"]
            
            # Extract just the summary/key topics instead of full research data
            summary = "No summary available"
            try:
                if isinstance(research_data, dict) and "artifacts" in research_data:
                    first_artifact = research_data["artifacts"][0]
                    if "parts" in first_artifact and first_artifact["parts"]:
                        content = first_artifact["parts"][0].get("text", "")
                        if content.strip().startswith("{"):
                            import json
                            parsed = json.loads(content)
                            summary = parsed.get("summary", "")[:200]  # Limit to 200 chars
                            
            except Exception:
                summary = f"Research about: {original_request}"
            
            return f'''Create an image related to: {original_request}

Key research findings: {summary}

Generate a professional visual that represents these concepts.'''
            
        elif agent == "writing" and "research_result" in context:
            # Writing after research - use research summary instead of raw data
            research_data = context["research_result"]
            try:
                import json
                if isinstance(research_data, dict) and "artifacts" in research_data:
                    first_artifact = research_data["artifacts"][0]
                    if "parts" in first_artifact and first_artifact["parts"]:
                        content = first_artifact["parts"][0].get("text", "")
                        if content.strip().startswith("{"):
                            parsed_research = json.loads(content)
                            summary = parsed_research.get("summary", "")
                            topic = parsed_research.get("topic", original_request)
                            return f'''Write a comprehensive article about: {topic}

Research Summary: {summary}

Create well-structured content with proper sections and engaging writing.'''
            except:
                pass
            
            return f"Write a comprehensive article about: {original_request}"
            
        elif agent == "report":
            # Report generation - use any available context
            if "research_result" in context:
                research_data = context["research_result"]
                return f'''Create a comprehensive report for: {original_request}

Use this research data as the foundation:
Research Results: {research_data}'''
            else:
                return f"Create a comprehensive report about: {original_request}"
                
        elif agent == "image":
            # Generate focused image prompt based on available context
            if "research_result" in context:
                # Extract key topics from research for image generation
                research_data = context["research_result"]
                # Parse research JSON to extract topic
                try:
                    import json
                    if isinstance(research_data, dict) and "artifacts" in research_data:
                        first_artifact = research_data["artifacts"][0]
                        if "parts" in first_artifact and first_artifact["parts"]:
                            content = first_artifact["parts"][0].get("text", "")
                            if content.strip().startswith("{"):
                                parsed_research = json.loads(content)
                                topic = parsed_research.get("topic", original_request)
                                return f"Create a professional visual illustration for: {topic}"
                except:
                    pass
            
            # Fallback: generate focused prompt from original request
            return f"Create a professional visual illustration for: {original_request}"
            
        else:
            # Default: use original request
            return original_request

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
            
            # Simple HTTP request for Windows compatibility
            import requests
            
            target_url = f"{agent_url}/a2a"
            self.logger.info(f"🔌 Sending request to {target_url}...")
            self.logger.info(f"📤 Payload: {payload}")
            
            # Basic POST request with minimal configuration  
            try:
                response = requests.post(target_url, json=payload, timeout=30)
                self.logger.info(f"📥 Response status: {response.status_code}")
                
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    self.logger.error(f"❌ HTTP Error: {error_msg}")
                    return {"success": False, "error": error_msg}
                    
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection failed to {target_url}: {str(e)}"
                self.logger.error(f"❌ Connection Error: {error_msg}")
                return {"success": False, "error": error_msg}
            except Exception as e:
                error_msg = f"Request failed to {target_url}: {str(e)}"
                self.logger.error(f"❌ Request Error: {error_msg}")
                return {"success": False, "error": error_msg}
                
            result = response.json()
            
            # Extract the actual result from A2A response
            if result.get("result") and result["result"].get("artifacts"):
                artifacts = result["result"]["artifacts"]
                
                # Extract data from first artifact (the main response)
                if artifacts and len(artifacts) > 0:
                    first_artifact = artifacts[0]
                    
                    # Check if artifact has parts array
                    if "parts" in first_artifact and first_artifact["parts"]:
                        first_part = first_artifact["parts"][0]
                        if first_part.get("type") == "text":
                            content = first_part.get("text", "")
                            try:
                                # Try to parse as JSON (for structured responses)
                                import json
                                if content.strip().startswith("{"):
                                    parsed_data = json.loads(content)
                                    return {"success": True, "artifacts": artifacts, **parsed_data}
                            except:
                                pass
                    
                    # Legacy format support
                    elif first_artifact.get("type") == "text":
                        content = first_artifact.get("content", "")
                        try:
                            import json
                            if content.strip().startswith("{"):
                                parsed_data = json.loads(content)
                                return {"success": True, "artifacts": artifacts, **parsed_data}
                        except:
                            pass
                        
                        # Return with artifacts
                        return {"success": True, "artifacts": artifacts}
                    else:
                        return {"success": False, "error": "Empty artifacts"}
                else:
                    return {"success": False, "error": "No artifacts returned"}
                
        except Exception as e:
            error_msg = f"Unexpected error with {agent_url}: {str(e)}"
            self.logger.error(f"❌ Unexpected Error: {error_msg}")
            return {"success": False, "error": error_msg}

    def _generate_final_response_sync(self, user_input: str, analysis: Dict[str, Any], agent_results: Dict[str, Any]) -> str:
        """Generate comprehensive final response combining ALL agent results."""
        
        # Count successful and failed tasks
        successful_tasks = []
        failed_tasks = []
        
        for agent, result in agent_results.items():
            if result.get("success"):
                successful_tasks.append(agent)
            else:
                failed_tasks.append(agent)
        
        # Build comprehensive response showing ALL results
        response_parts = []
        response_parts.append(f"🎯 **Multi-Agent Task Completed**")
        response_parts.append(f"**Your request:** {user_input}")
        response_parts.append(f"**Tasks executed:** {len(agent_results)} agents ({len(successful_tasks)} successful, {len(failed_tasks)} failed)")
        response_parts.append("")
        
        # Show results from each agent
        for i, (agent, result) in enumerate(agent_results.items(), 1):
            agent_name = agent.replace("_", " ").title()
            response_parts.append(f"## {i}. {agent_name} Agent Results")
            
            if result.get("success"):
                if agent == "research":
                    # Research results
                    total_results = result.get("total_results", 0)
                    summary = result.get("summary", "Research completed")
                    response_parts.append(f"✅ **Research completed successfully**")
                    response_parts.append(f"- **Sources found:** {total_results}")
                    response_parts.append(f"- **Summary:** {summary[:200]}..." if len(summary) > 200 else f"- **Summary:** {summary}")
                    
                elif agent == "image":
                    # Image generation results
                    file_path = result.get("file_path", "unknown")
                    file_name = result.get("file_name", "unknown")
                    file_size = result.get("file_size_kb", 0)
                    response_parts.append(f"✅ **Image generated successfully**")
                    response_parts.append(f"- **File:** {file_name}")
                    response_parts.append(f"- **Location:** {file_path}")
                    response_parts.append(f"- **Size:** {file_size} KB")
                    
                elif agent == "writing":
                    # Writing results
                    word_count = result.get("word_count", 0)
                    title = result.get("title", "Content created")
                    response_parts.append(f"✅ **Content created successfully**")
                    response_parts.append(f"- **Title:** {title}")
                    response_parts.append(f"- **Word count:** {word_count}")
                    
                elif agent == "report":
                    # Report results
                    sections = result.get("sections", 0)
                    word_count = result.get("word_count", 0)
                    response_parts.append(f"✅ **Report generated successfully**")
                    response_parts.append(f"- **Sections:** {sections}")
                    response_parts.append(f"- **Word count:** {word_count}")
                    
            else:
                # Failed task
                error = result.get("error", "Unknown error")
                response_parts.append(f"❌ **{agent_name} failed:** {error}")
            
            response_parts.append("")
        
        # Add overall summary
        if len(successful_tasks) == len(agent_results):
            response_parts.append("🎉 **All tasks completed successfully!** All requested deliverables have been generated and are ready for use.")
        elif len(successful_tasks) > 0:
            response_parts.append(f"⚠️ **Partial completion:** {len(successful_tasks)}/{len(agent_results)} tasks succeeded. Successful deliverables are available.")
        else:
            response_parts.append("❌ **All tasks failed.** Please check the error messages above and try again.")
        
        return "\n".join(response_parts)

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": "Assistant Orchestrator",
            "type": "orchestrator",
            "model": self.model_name,
            "capabilities": ["coordination", "analysis", "multi_agent_orchestration"],
            "connected_agents": ["image", "writing", "research", "report"],
            "status": "ready"
        }