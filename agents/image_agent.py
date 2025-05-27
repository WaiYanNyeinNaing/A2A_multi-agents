# agents/image_agent.py
"""
Image Generation Agent using Google Gemini API
- Inherits from BaseAgent for common functionality
- Specialized for image generation using Imagen
"""

import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import logging
from .base_agent import BaseAgent

class ImageAgent(BaseAgent):
    """
    Image Generation Agent using Gemini Imagen
    """
    
    def __init__(self):
        super().__init__("image_generation_specialist")
        self.image_model = os.getenv('IMAGEN_MODEL_NAME', 'imagen-3.0-generate-002')
        
        # Setup image storage directory
        self.images_dir = Path("generated_images")
        self.images_dir.mkdir(exist_ok=True)
        
        # Initialize Gemini client for image generation
        try:
            # Load environment variables from .env file
            from dotenv import load_dotenv
            load_dotenv()
            
            import google.genai as genai
            
            # Try different authentication methods
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if api_key:
                self.gemini_client = genai.Client(api_key=api_key)
                self.logger.info("✅ Gemini client initialized with API key")
            else:
                # Try default authentication (ADC)
                self.gemini_client = genai.Client()
                self.logger.info("✅ Gemini client initialized with default auth")
        except Exception as e:
            self.logger.error(f"❌ Could not initialize Gemini client: {e}")
            self.gemini_client = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def generate_image(self, prompt: str, aspect_ratio: str = "16:9", style: str = "professional") -> Dict[str, Any]:
        """
        Generate an image using Gemini Imagen.
        
        Args:
            prompt: Detailed description of the image to generate
            aspect_ratio: Image aspect ratio (16:9, 1:1, 9:16)
            style: Visual style preference (professional, artistic, photographic, etc.)
            
        Returns:
            Dict containing image data, metadata, and generation details
        """
        try:
            # Check if Gemini client is available
            if not self.gemini_client:
                return self.create_error_response(
                    "Image generation unavailable: Missing GEMINI_API_KEY or GOOGLE_API_KEY environment variable. Please set your Google AI API key.",
                    "api_key_missing"
                )
            
            from google.genai import types
            
            # Create enhanced prompt
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            # Generate image using Imagen - explicitly request only 1 image
            response = self.gemini_client.models.generate_images(
                model=self.image_model,
                prompt=enhanced_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,  # Explicitly only 1 image
                    aspect_ratio=aspect_ratio
                )
            )
            
            if response.generated_images and len(response.generated_images) > 0:
                # Always use only the first image, ignore any additional ones
                image_bytes = response.generated_images[0].image.image_bytes
                
                self.logger.info(f"📊 Received {len(response.generated_images)} image(s) from API, using first one only")
                if len(response.generated_images) > 1:
                    self.logger.warning(f"⚠️ API returned {len(response.generated_images)} images, but only processing 1 as requested")
                
                # Save image to local file
                save_result = self._save_image_to_file(image_bytes, prompt, style)
                
                if save_result["success"]:
                    self.logger.info(f"✅ Image generated and saved: {save_result['file_path']}")
                    self.logger.info(f"📝 Original prompt: {prompt}")
                    self.logger.info(f"🎨 Style: {style}, Aspect ratio: {aspect_ratio}")
                    self.logger.info(f"📊 File size: {save_result['file_size_kb']} KB")
                    
                    return self.create_success_response(
                        image_id=save_result['image_id'],
                        file_path=str(save_result['file_path']),
                        file_name=save_result['file_name'],
                        file_size_kb=save_result['file_size_kb'],
                        image_format="png",
                        generation_successful=True,
                        prompt={
                            "original": prompt,
                            "enhanced": enhanced_prompt,
                            "style": style
                        },
                        parameters={
                            "aspect_ratio": aspect_ratio,
                            "model": self.image_model
                        },
                        log_message=f"Image saved successfully to {save_result['file_path']}"
                    )
                else:
                    raise ValueError(f"Failed to save image: {save_result['error']}")
            else:
                raise ValueError("No images generated by Imagen")
                
        except Exception as e:
            self.logger.error(f"❌ Image generation failed: {e}")
            return self.create_error_response(str(e), "image_generation_error")
    
    def _create_mock_image(self, prompt: str, style: str) -> Dict[str, Any]:
        """Create a mock image response for testing when API is not configured."""
        # Create a simple mock image (1x1 pixel PNG)
        mock_image_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # IHDR data
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x78, 0x9C, 0x62, 0x00, 0x00, 0x00, 0x02,  # Compressed data
            0x00, 0x01, 0xE2, 0x21, 0xBC, 0x33, 0x00, 0x00,  # IDAT end
            0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42,  # IEND chunk
            0x60, 0x82
        ])
        
        # Save mock image to file
        save_result = self._save_image_to_file(mock_image_data, prompt, style)
        
        if save_result["success"]:
            self.logger.info(f"🔧 Created mock image for testing: {save_result['file_name']}")
            return self.create_success_response(
                image_id=self.generate_unique_id(),
                file_path=save_result["file_path"],
                file_name=save_result["file_name"],
                file_size_kb=save_result["file_size_kb"],
                generation_successful=True,
                prompt=prompt,
                style=style,
                log_message=f"Mock image created for testing (API not configured). File: {save_result['file_name']}"
            )
        else:
            return self.create_error_response("Failed to save mock image", "mock_save_error")
    
    def _save_image_to_file(self, image_bytes: bytes, prompt: str, style: str) -> Dict[str, Any]:
        """Save image bytes to a local file with descriptive naming."""
        try:
            # Generate unique image ID and timestamp
            image_id = self.generate_unique_id()[:8]  # Shorter ID for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create descriptive filename from prompt (sanitized)
            prompt_snippet = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            prompt_snippet = "_".join(prompt_snippet.split())  # Replace spaces with underscores
            
            # Build filename with guaranteed uniqueness
            filename = f"{timestamp}_{prompt_snippet}_{style}_{image_id}.png"
            file_path = self.images_dir / filename
            
            # Ensure file doesn't already exist (though it shouldn't with unique ID)
            counter = 1
            original_file_path = file_path
            while file_path.exists():
                self.logger.warning(f"⚠️ File {filename} already exists, adding counter")
                name_parts = filename.rsplit('.', 1)
                filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                file_path = self.images_dir / filename
                counter += 1
            
            # Save single image file
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            # Calculate file size
            file_size_kb = round(len(image_bytes) / 1024, 2)
            
            self.logger.info(f"💾 Saved single image: {filename} ({file_size_kb} KB)")
            
            return {
                "success": True,
                "image_id": image_id,
                "file_path": file_path,
                "file_name": filename,
                "file_size_kb": file_size_kb
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def enhance_prompt(self, basic_prompt: str, enhancement_type: str = "detailed") -> Dict[str, Any]:
        """
        Enhance a basic prompt for better image generation.
        
        Args:
            basic_prompt: Basic image description
            enhancement_type: Type of enhancement (detailed, artistic, photographic)
            
        Returns:
            Dict containing enhanced prompt
        """
        enhanced_prompt = self._enhance_prompt(basic_prompt, enhancement_type)
        return {
            "original_prompt": basic_prompt,
            "enhanced_prompt": enhanced_prompt,
            "enhancement_type": enhancement_type
        }
    
    def _enhance_prompt(self, basic_prompt: str, style: str = "professional") -> str:
        """Enhance a basic prompt for better image generation."""
        style_enhancements = {
            "professional": "professional, high-quality, clean composition, corporate style, well-lit",
            "artistic": "artistic, creative, expressive, unique perspective, dynamic composition",
            "photographic": "photographic, realistic, detailed, sharp focus, natural lighting",
            "minimalist": "minimalist, clean, simple, uncluttered, modern design",
            "vintage": "vintage, retro, classic style, warm tones, nostalgic feel"
        }
        
        enhancement = style_enhancements.get(style, style_enhancements["professional"])
        return f"{enhancement}, {basic_prompt}, high resolution, detailed, visually appealing"
    
    def _get_prompt_suggestions(self, prompt: str) -> list:
        """Get suggestions for improving the prompt."""
        return [
            "Consider adding lighting details (natural light, studio lighting, golden hour)",
            "Specify the mood or atmosphere (calm, energetic, mysterious, cheerful)",
            "Include composition details (close-up, wide shot, bird's eye view)"
        ][:3]
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": "Image Generation Specialist",
            "type": "image_generation",
            "model": self.image_model,
            "capabilities": ["generate_image", "enhance_prompt"],
            "status": "ready"
        }