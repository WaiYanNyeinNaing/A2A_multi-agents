# agents/base_agent.py
"""
Base Agent Class for A2A Multi-Agent System
- Common functionality and patterns shared across all agents
- Standardized initialization and setup
- Abstract methods for specialized implementations
"""

import os
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Google Generative AI imports
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all A2A agents
    """
    
    def __init__(self, agent_type: str, default_model: str = 'gemini-2.0-flash-exp'):
        self.agent_type = agent_type
        self.gemini_client = None
        self.model_name = os.getenv('GEMINI_MODEL_NAME', default_model)
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.initialize_gemini_client()
    
    def initialize_gemini_client(self):
        """Initialize Gemini client with common setup."""
        try:
            # Setup proxy if needed
            proxy_url = os.getenv('HTTP_PROXY')
            if proxy_url:
                os.environ["http_proxy"] = proxy_url
                os.environ["https_proxy"] = proxy_url
            
            self.gemini_client = genai.Client(api_key=self.api_key)
            logger.info(f"✅ Gemini client initialized for {self.agent_type}")
            
        except ImportError:
            logger.error("❌ google-genai package not installed")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            raise
    
    @abstractmethod
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        pass
    
    def generate_unique_id(self) -> str:
        """Generate unique ID for tasks/artifacts."""
        return str(uuid.uuid4())
    
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def create_success_response(self, **kwargs) -> Dict[str, Any]:
        """Create standardized success response."""
        return {
            "success": True,
            "timestamp": self.get_timestamp(),
            "agent": self.agent_type,
            **kwargs
        }
    
    def create_error_response(self, error: str, error_type: str = "execution_error") -> Dict[str, Any]:
        """Create standardized error response."""
        logger.error(f"❌ {self.agent_type} error: {error}")
        return {
            "success": False,
            "error": error,
            "error_type": error_type,
            "timestamp": self.get_timestamp(),
            "agent": self.agent_type
        }
    
    def call_gemini_api(self, prompt: str, **kwargs) -> str:
        """Common method to call Gemini API."""
        try:
            response = self.gemini_client.models.generate_content(
                model=self.model_name,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )]
            )
            
            return response.candidates[0].content.parts[0].text
            
        except Exception as e:
            logger.error(f"❌ Gemini API call failed: {e}")
            raise