# agents/writing_agent.py
"""
Writing Agent using Google Gemini API
- Inherits from BaseAgent for common functionality  
- Specialized for content writing and editing
"""

from typing import Dict, Any
from .base_agent import BaseAgent

class WritingAgent(BaseAgent):
    """Writing Agent using Gemini for content generation"""
    
    def __init__(self):
        super().__init__(agent_type="writing_specialist")
    
    def write_article(self, topic: str, style: str = "informative", length: str = "short") -> Dict[str, Any]:
        """Write article on given topic."""
        try:
            word_targets = {"short": "300-400", "medium": "500-700", "long": "800-1000"}
            target_words = word_targets.get(length, "300-400")
            
            prompt = f"""
            Write a {style} article about: {topic}
            
            Requirements:
            - Length: {target_words} words
            - Style: {style}
            - Include clear introduction, body, and conclusion
            - Use engaging headlines and structure
            - Be informative and well-researched
            
            Topic: {topic}
            """
            
            article_text = self.call_gemini_api(prompt)
            word_count = len(article_text.split())
            
            return self.create_success_response(
                article_id=self.generate_unique_id(),
                topic=topic,
                style=style,
                length=length,
                content=article_text,
                word_count=word_count
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "article_writing_error")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "name": "Writing Specialist",
            "type": "content_writing", 
            "model": self.model_name,
            "capabilities": ["write_article"],
            "styles": ["informative", "creative", "professional", "casual"],
            "lengths": ["short", "medium", "long"],
            "status": "ready" if self.gemini_client else "not_ready"
        }