# agents/writing_agent.py
"""
Writing Agent using Google Gemini
- Specialized for content creation and article writing
- Uses Google Gemini 2.0 Flash for high-quality content generation
"""

import os
from typing import Dict, Any, Optional
from .base_agent import BaseAgent

class WritingAgent(BaseAgent):
    """
    Writing Agent specialized for content creation and article writing
    """
    
    def __init__(self):
        super().__init__("writing_specialist")
        
    def write_article(self, topic: str, style: str = "informative", word_count: int = 800) -> Dict[str, Any]:
        """
        Write an article on the given topic.
        
        Args:
            topic: The topic or subject to write about
            style: Writing style (informative, persuasive, narrative, etc.)
            word_count: Target word count for the article
            
        Returns:
            Dict containing the article content and metadata
        """
        try:
            # Generate article using Gemini
            prompt = f"""
            Write a comprehensive {style} article about: {topic}
            
            Requirements:
            - Target length: approximately {word_count} words
            - Include a compelling title
            - Structure with clear introduction, body, and conclusion
            - Use engaging and {style} tone
            - Include specific details and examples where relevant
            - Make it informative and well-researched
            
            Please format the response as follows:
            Title: [Your compelling title here]
            
            [Article content here with proper paragraphs]
            """
            
            content = self.call_gemini_api(prompt)
            
            # Extract title and content
            lines = content.strip().split('\n')
            title = "Untitled Article"
            article_content = content
            
            # Try to extract title if formatted properly
            if lines and lines[0].startswith("Title:"):
                title = lines[0].replace("Title:", "").strip()
                # Join remaining lines as content
                article_content = '\n'.join(lines[1:]).strip()
            
            # Count words (approximate)
            word_count_actual = len(article_content.split())
            
            self.logger.info(f"✅ Article created: '{title}' ({word_count_actual} words)")
            
            return self.create_success_response(
                article_id=self.generate_unique_id(),
                title=title,
                content=article_content,
                word_count=word_count_actual,
                style=style,
                topic=topic
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "writing_error")
    
    def write_blog_post(self, topic: str, audience: str = "general") -> Dict[str, Any]:
        """
        Write a blog post optimized for web reading.
        
        Args:
            topic: The topic to write about
            audience: Target audience (general, technical, business, etc.)
            
        Returns:
            Dict containing the blog post content and metadata
        """
        try:
            prompt = f"""
            Write an engaging blog post about: {topic}
            
            Target audience: {audience}
            
            Requirements:
            - Catchy, SEO-friendly title
            - Hook readers with an engaging introduction
            - Use subheadings to break up content
            - Include practical insights or actionable advice
            - Conversational tone appropriate for {audience} audience
            - Length: 600-1000 words
            - End with a compelling conclusion
            
            Format:
            Title: [SEO-friendly title]
            
            [Blog post content with subheadings]
            """
            
            content = self.call_gemini_api(prompt)
            
            # Extract title and content
            lines = content.strip().split('\n')
            title = "Blog Post"
            blog_content = content
            
            if lines and lines[0].startswith("Title:"):
                title = lines[0].replace("Title:", "").strip()
                blog_content = '\n'.join(lines[1:]).strip()
            
            word_count = len(blog_content.split())
            
            self.logger.info(f"✅ Blog post created: '{title}' ({word_count} words)")
            
            return self.create_success_response(
                blog_id=self.generate_unique_id(),
                title=title,
                content=blog_content,
                word_count=word_count,
                audience=audience,
                topic=topic,
                content_type="blog_post"
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "blog_writing_error")
    
    def summarize_content(self, content: str, length: str = "medium") -> Dict[str, Any]:
        """
        Create a summary of the given content.
        
        Args:
            content: The content to summarize
            length: Summary length (short, medium, long)
            
        Returns:
            Dict containing the summary and metadata
        """
        try:
            # Determine target length
            if length == "short":
                target = "2-3 sentences"
            elif length == "long":
                target = "3-4 paragraphs"
            else:  # medium
                target = "1-2 paragraphs"
            
            prompt = f"""
            Create a {length} summary of the following content in {target}:
            
            {content}
            
            Focus on the main points and key insights. Be concise but comprehensive.
            """
            
            summary = self.call_gemini_api(prompt)
            word_count = len(summary.split())
            
            self.logger.info(f"✅ Summary created: {length} length ({word_count} words)")
            
            return self.create_success_response(
                summary_id=self.generate_unique_id(),
                summary=summary,
                original_length=len(content.split()),
                summary_length=word_count,
                compression_ratio=round(word_count / len(content.split()), 2),
                length_type=length
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "summarization_error")
    
    def get_agent_info(self):
        """Return agent information for A2A protocol."""
        return {
            "name": "Writing Specialist",
            "type": "content_writing", 
            "model": self.model_name,
            "capabilities": ["write_article", "write_blog_post", "summarize_content"],
            "status": "ready"
        }