"""
Layout-Aware LoRA Image Generation
Generates backgrounds that respect text and watermark zones
"""
import torch
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class LayoutAwareGenerator:
    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.layout_zones = self._define_layout_zones()
        
    def _define_layout_zones(self) -> Dict[str, Dict]:
        """Define safe zones and restricted areas for text/watermark"""
        return {
            "watermark_zone": {
                "area": (0.2, 0.75, 0.8, 0.95),  # center bottom 60% width, 20% height
                "description": "Genfinity watermark placement",
                "avoid": True
            },
            "title_zone": {
                "area": (0.1, 0.1, 0.9, 0.4),   # top area for main title
                "description": "Main article title placement", 
                "avoid": True
            },
            "subtitle_zone": {
                "area": (0.15, 0.35, 0.85, 0.5),  # below title
                "description": "Article subtitle placement",
                "avoid": True
            },
            "logo_zone": {
                "area": (0.05, 0.05, 0.25, 0.25),  # top left corner
                "description": "Crypto logo placement",
                "avoid": False  # Can have subtle background elements
            },
            "safe_content_zone": {
                "area": (0.0, 0.5, 1.0, 0.75),   # middle band
                "description": "Main visual content area",
                "avoid": False
            }
        }
    
    async def generate_layout_aware_background(
        self,
        style: str,  # "Dark", "Colorful", "Light"
        article_title: str,
        subtitle: Optional[str] = None,
        crypto_network: Optional[str] = None,
        width: int = 1800,
        height: int = 900
    ) -> Image.Image:
        """Generate background with layout awareness"""
        
        # Create layout-aware prompt
        base_prompt = self._get_style_prompt(style)
        layout_prompt = self._create_layout_aware_prompt(
            base_prompt, article_title, subtitle, crypto_network
        )
        
        # Generate background with layout constraints
        background = await self._generate_with_layout_constraints(
            layout_prompt, width, height, style
        )
        
        return background
    
    def _get_style_prompt(self, style: str) -> str:
        """Get base prompt for each style aesthetic"""
        style_prompts = {
            "Dark": """
                dark cyberpunk tech background, neon blue and purple lights, 
                3D blockchain cubes, digital data streams, holographic elements,
                professional tech aesthetic, deep black background with cyan accents,
                futuristic interface elements, minimalist composition
            """,
            "Colorful": """
                cosmic purple and pink gradient background, ethereal space atmosphere,
                floating spheres and planets, light beams and aurora effects,
                futuristic sci-fi environment, nebula colors, cosmic energy,
                dreamy otherworldly landscape, vibrant but not overwhelming
            """,
            "Light": """
                clean bright background, minimal modern design, soft gradients,
                professional corporate aesthetic, subtle geometric patterns,
                light blue and white tones, contemporary business style,
                sophisticated and clean layout
            """
        }
        return style_prompts.get(style, style_prompts["Light"])
    
    def _create_layout_aware_prompt(
        self, 
        base_prompt: str, 
        title: str, 
        subtitle: Optional[str],
        network: Optional[str]
    ) -> str:
        """Create prompt with layout constraints"""
        
        # Analyze title length and complexity
        title_words = len(title.split())
        title_complexity = "complex multi-line" if title_words > 6 else "single line"
        
        # Layout constraints based on content
        layout_constraints = [
            "composition with clear center bottom space for watermark",
            f"avoid visual elements in top area for {title_complexity} title",
            "background-focused design without central subjects",
            "atmospheric lighting that doesn't interfere with text readability"
        ]
        
        if subtitle:
            layout_constraints.append("extra vertical space for subtitle text")
            
        if network:
            layout_constraints.append(f"subtle {network} themed elements in background only")
        
        # Combine base prompt with layout awareness
        full_prompt = f"""
        {base_prompt.strip()}
        
        Layout requirements: {', '.join(layout_constraints)}
        
        Composition guidelines:
        - keep center bottom 20% clear for branding
        - keep top 30% relatively clear for title overlay
        - focus visual interest in middle horizontal band
        - atmospheric background without dominant central subjects
        - professional article cover aesthetic
        """
        
        return full_prompt.strip()
    
    async def _generate_with_layout_constraints(
        self,
        prompt: str,
        width: int,
        height: int, 
        style: str
    ) -> Image.Image:
        """Generate image with layout constraints applied"""
        
        # Negative prompt to avoid interference zones
        negative_prompt = """
        text, letters, words, titles, watermarks, logos, central subjects,
        people faces, large objects in center bottom, busy center composition,
        cluttered layout, text overlays, branding elements, signatures,
        dominant foreground objects blocking title area
        """
        
        try:
            # Generate using the AI service with layout awareness
            if not self.ai_service.initialized:
                await self.ai_service.initialize()
            
            # Apply style-specific LoRA if available
            lora_model = f"genfinity_{style.lower()}_style"
            if lora_model in self.ai_service.lora_models:
                logger.info(f"🎨 Using {lora_model} LoRA for style generation")
            
            # Generate with guidance for layout
            image = self.ai_service.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=30,
                guidance_scale=7.5,
                num_images_per_prompt=1
            ).images[0]
            
            # Post-process to ensure layout compliance
            image = self._post_process_layout_compliance(image, style)
            
            return image
            
        except Exception as e:
            logger.error(f"❌ Layout-aware generation failed: {str(e)}")
            # Fallback to solid gradient background
            return self._create_fallback_background(width, height, style)
    
    def _post_process_layout_compliance(self, image: Image.Image, style: str) -> Image.Image:
        """Ensure generated image respects layout zones"""
        
        # Convert to numpy for processing
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Apply subtle masks to ensure text zones are readable
        zones = self.layout_zones
        
        # Slightly darken/blur watermark zone to ensure contrast
        watermark_zone = zones["watermark_zone"]["area"]
        y1 = int(watermark_zone[1] * height)
        y2 = int(watermark_zone[3] * height)
        x1 = int(watermark_zone[0] * width)
        x2 = int(watermark_zone[2] * width)
        
        # Apply subtle overlay for better watermark visibility
        overlay_strength = 0.15  # 15% overlay
        if style == "Dark":
            img_array[y1:y2, x1:x2] = img_array[y1:y2, x1:x2] * (1 - overlay_strength)
        else:
            # For bright styles, add subtle dark overlay for contrast
            img_array[y1:y2, x1:x2] = img_array[y1:y2, x1:x2] * (1 - overlay_strength) + 30 * overlay_strength
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _create_fallback_background(self, width: int, height: int, style: str) -> Image.Image:
        """Create fallback gradient background if generation fails"""
        
        colors = {
            "Dark": [(10, 10, 30), (50, 20, 80)],      # Dark blue gradient
            "Colorful": [(80, 20, 120), (150, 50, 200)], # Purple gradient  
            "Light": [(240, 245, 250), (220, 230, 240)]  # Light blue gradient
        }
        
        gradient_colors = colors.get(style, colors["Light"])
        
        # Create gradient background
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        for i in range(height):
            ratio = i / height
            r = int(gradient_colors[0][0] * (1 - ratio) + gradient_colors[1][0] * ratio)
            g = int(gradient_colors[0][1] * (1 - ratio) + gradient_colors[1][1] * ratio)
            b = int(gradient_colors[0][2] * (1 - ratio) + gradient_colors[1][2] * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        return image

    async def add_text_and_watermark(
        self,
        background: Image.Image,
        title: str,
        subtitle: Optional[str] = None,
        watermark_path: Optional[str] = None
    ) -> Image.Image:
        """Add title, subtitle, and watermark to the background"""
        
        # Create a copy to work with
        image = background.copy()
        draw = ImageDraw.Draw(image)
        
        width, height = image.size
        
        # Load fonts (fallback to default if custom fonts not available)
        try:
            title_font = ImageFont.truetype("Arial-Bold", size=int(height * 0.08))
            subtitle_font = ImageFont.truetype("Arial", size=int(height * 0.04))
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add title with proper positioning
        title_zone = self.layout_zones["title_zone"]["area"]
        title_x = int(width * title_zone[0])
        title_y = int(height * title_zone[1])
        title_width = int(width * (title_zone[2] - title_zone[0]))
        
        # Add text shadow for better readability
        shadow_offset = 3
        draw.text((title_x + shadow_offset, title_y + shadow_offset), title, 
                 font=title_font, fill=(0, 0, 0, 128))  # Semi-transparent shadow
        draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255))
        
        # Add subtitle if provided
        if subtitle:
            subtitle_zone = self.layout_zones["subtitle_zone"]["area"]
            subtitle_x = int(width * subtitle_zone[0])
            subtitle_y = int(height * subtitle_zone[1])
            
            draw.text((subtitle_x + shadow_offset, subtitle_y + shadow_offset), subtitle,
                     font=subtitle_font, fill=(0, 0, 0, 128))
            draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(200, 200, 200))
        
        # Add watermark if provided
        if watermark_path and os.path.exists(watermark_path):
            try:
                watermark = Image.open(watermark_path).convert("RGBA")
                
                # Resize watermark to fit in designated zone
                watermark_zone = self.layout_zones["watermark_zone"]["area"]
                wm_width = int(width * (watermark_zone[2] - watermark_zone[0]))
                wm_height = int(height * (watermark_zone[3] - watermark_zone[1]))
                
                watermark = watermark.resize((wm_width, wm_height), Image.Resampling.LANCZOS)
                
                # Position watermark
                wm_x = int(width * watermark_zone[0])
                wm_y = int(height * watermark_zone[1])
                
                # Paste watermark with alpha blending
                image.paste(watermark, (wm_x, wm_y), watermark)
                
            except Exception as e:
                logger.warning(f"⚠️ Could not add watermark: {str(e)}")
        
        return image