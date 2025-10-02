"""
Mock AI Service for Railway deployment
Generates test images without heavy ML dependencies
"""
import os
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from typing import Optional, List, Dict, Any, Tuple
import asyncio
import logging

logger = logging.getLogger(__name__)

class MockAIService:
    def __init__(self):
        self.initialized = False
        self.lora_models = {}
        
    async def initialize(self):
        """Mock initialization"""
        if self.initialized:
            return
            
        logger.info("🧪 Initializing Mock AI Service for Railway deployment...")
        
        # Mock LoRA models
        self.lora_models = {
            "xdc_network_lora": {"loaded": True, "mock": True},
            "hedera_lora": {"loaded": True, "mock": True},
            "hashpack_lora": {"loaded": True, "mock": True},
            "constellation_lora": {"loaded": True, "mock": True},
            "algorand_lora": {"loaded": True, "mock": True},
            "tha_lora": {"loaded": True, "mock": True},
            "genfinity_lora": {"loaded": True, "mock": True},
        }
        
        self.initialized = True
        logger.info("✅ Mock AI Service initialized")

    async def generate_background(
        self, 
        client_id: Optional[str] = None,
        lora_models: Optional[List[str]] = None,
        prompt_enhancement: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        style_params: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """Generate mock background image"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create a gradient background based on client
            width, height = 1792, 896
            
            # Client-specific colors
            client_colors = {
                "xdc": ((0, 30, 60), (0, 100, 200)),  # XDC blue
                "hedera": ((80, 0, 80), (160, 0, 160)),  # Hedera purple
                "hashpack": ((0, 80, 160), (0, 120, 240)),  # HashPack blue
                "constellation": ((20, 20, 80), (60, 60, 160)),  # Constellation dark blue
                "algorand": ((0, 0, 0), (100, 100, 100)),  # Algorand dark
                "tha": ((40, 80, 120), (80, 160, 240)),  # THA light blue
                "genfinity": ((20, 20, 20), (80, 80, 80)),  # Genfinity dark
            }
            
            # Default crypto colors
            default_colors = ((10, 20, 40), (30, 60, 120))
            
            # Get colors for client
            colors = default_colors
            for key, client_color in client_colors.items():
                if client_id and key in client_id.lower():
                    colors = client_color
                    break
            
            # Create gradient background
            image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(image)
            
            for y in range(height):
                # Linear gradient from top to bottom
                ratio = y / height
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                
                draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))
            
            # Add some geometric elements for crypto feel
            self._add_crypto_elements(draw, width, height, colors[1])
            
            logger.info(f"✅ Mock background generated for client: {client_id}")
            return image
            
        except Exception as e:
            logger.error(f"❌ Error generating mock background: {str(e)}")
            raise

    def _add_crypto_elements(self, draw, width, height, accent_color):
        """Add simple geometric elements to simulate crypto styling"""
        # Add some subtle geometric shapes
        for i in range(3):
            x = width - 200 + i * 50
            y = height - 150 + i * 30
            size = 40 - i * 10
            
            # Semi-transparent rectangles
            color = (accent_color[0], accent_color[1], accent_color[2], 100)
            draw.rectangle([x, y, x + size, y + size], outline=accent_color, width=2)

    async def add_text_overlay(
        self,
        image: Image.Image,
        title: str,
        subtitle: Optional[str] = None,
        size: Tuple[int, int] = None,
        text_style: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """Add text overlay to image"""
        
        try:
            img_with_text = image.copy()
            draw = ImageDraw.Draw(img_with_text)
            
            img_width, img_height = img_with_text.size
            
            # Default text style
            default_style = {
                "title_font_size": max(60, img_width // 30),
                "subtitle_font_size": max(40, img_width // 45),
                "title_color": (255, 255, 255),
                "subtitle_color": (255, 255, 255),
            }
            
            if text_style:
                default_style.update(text_style)
            
            # Use default font (no system font dependencies)
            try:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            except:
                title_font = None
                subtitle_font = None
            
            # Calculate text positioning
            if title_font:
                title_bbox = draw.textbbox((0, 0), title, font=title_font)
                title_width = title_bbox[2] - title_bbox[0]
                title_height = title_bbox[3] - title_bbox[1]
            else:
                # Estimate text size
                title_width = len(title) * 20
                title_height = 30
            
            # Center positioning
            if subtitle:
                title_y = img_height // 2 - title_height - 20
                
                if subtitle_font:
                    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
                    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                else:
                    subtitle_width = len(subtitle) * 15
                
                subtitle_y = img_height // 2 + 20
                subtitle_x = (img_width - subtitle_width) // 2
                
                # Draw subtitle
                draw.text(
                    (subtitle_x, subtitle_y), 
                    subtitle, 
                    font=subtitle_font,
                    fill=default_style["subtitle_color"]
                )
            else:
                title_y = (img_height - title_height) // 2
            
            title_x = (img_width - title_width) // 2
            
            # Draw title
            draw.text(
                (title_x, title_y), 
                title, 
                font=title_font,
                fill=default_style["title_color"]
            )
            
            logger.info("✅ Text overlay added to mock image")
            return img_with_text
            
        except Exception as e:
            logger.error(f"❌ Error adding text overlay: {str(e)}")
            raise

    async def add_watermark(
        self,
        image: Image.Image,
        watermark_data: bytes,
        position: str = "bottom-right",
        opacity: float = 0.7
    ) -> Image.Image:
        """Add watermark to image (simplified)"""
        # For mock, just return the image unchanged
        logger.info("✅ Mock watermark applied")
        return image

    async def get_status(self) -> Dict[str, Any]:
        """Get mock service status"""
        return {
            "sdxl_loaded": self.initialized,
            "lora_models_count": len(self.lora_models),
            "device": "mock",
            "memory_usage": {"device": "mock", "available": True},
            "mock_mode": True
        }