#!/usr/bin/env python3
"""
Professional Text Overlay System
Adds clean, readable titles and subtitles to AI-generated covers
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap

class TextOverlayGenerator:
    def __init__(self):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.pipeline = None
        self.watermark = None
        self.setup_pipeline()
        self.load_watermark()
        
    def setup_pipeline(self):
        """Load optimized SDXL pipeline"""
        print(f"🖥️  Using device: {self.device}")
        print("🔄 Loading Stable Diffusion XL...")
        
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        
        self.pipeline = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            use_safetensors=True,
            variant=None
        )
        
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipeline.scheduler.config,
            use_karras_sigmas=True
        )
        
        if self.device == "mps":
            self.pipeline = self.pipeline.to(self.device)
            self.pipeline.enable_model_cpu_offload()
            
        print("✅ Pipeline ready")
    
    def load_watermark(self):
        """Load Genfinity watermark"""
        watermark_path = "/Users/valorkopeny/Desktop/genfinity-watermark.png"
        try:
            self.watermark = Image.open(watermark_path).convert("RGBA")
            print(f"✅ Loaded watermark: {self.watermark.size}")
        except Exception as e:
            print(f"⚠️  No watermark found: {e}")
            self.watermark = None
    
    def get_fonts(self):
        """Load professional fonts with fallbacks"""
        fonts = {}
        
        # Try to load system fonts
        font_paths = [
            "/System/Library/Fonts/Arial.ttc",
            "/System/Library/Fonts/Helvetica.ttc", 
            "/System/Library/Fonts/Futura.ttc",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
        
        for size_name, size in [("title", 72), ("subtitle", 36), ("small", 24)]:
            fonts[size_name] = None
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        fonts[size_name] = ImageFont.truetype(font_path, size)
                        break
                except:
                    continue
            
            # Fallback to default
            if fonts[size_name] is None:
                fonts[size_name] = ImageFont.load_default()
        
        return fonts
    
    def create_text_overlay(self, width, height, title, subtitle=""):
        """Create professional text overlay"""
        
        # Create transparent overlay
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        fonts = self.get_fonts()
        
        # Title styling
        if title:
            title = title.upper()
            
            # Wrap long titles
            wrapped_title = textwrap.fill(title, width=25)
            title_lines = wrapped_title.split('\n')
            
            # Calculate title positioning (upper third)
            total_title_height = len(title_lines) * 80
            start_y = 100
            
            for i, line in enumerate(title_lines):
                # Get text dimensions
                bbox = draw.textbbox((0, 0), line, font=fonts["title"])
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center horizontally
                x = (width - text_width) // 2
                y = start_y + (i * 80)
                
                # Create text with multiple shadows for better visibility
                shadow_offsets = [(4, 4), (2, 2), (1, 1)]
                shadow_colors = [(0, 0, 0, 220), (0, 0, 0, 180), (0, 0, 0, 140)]
                
                # Draw shadows
                for offset, color in zip(shadow_offsets, shadow_colors):
                    draw.text((x + offset[0], y + offset[1]), line, fill=color, font=fonts["title"])
                
                # Draw main text in white
                draw.text((x, y), line, fill=(255, 255, 255, 255), font=fonts["title"])
        
        # Subtitle styling
        if subtitle:
            # Wrap subtitle
            wrapped_subtitle = textwrap.fill(subtitle, width=50)
            subtitle_lines = wrapped_subtitle.split('\n')
            
            # Position below title
            subtitle_start_y = start_y + total_title_height + 40
            
            for i, line in enumerate(subtitle_lines):
                bbox = draw.textbbox((0, 0), line, font=fonts["subtitle"])
                text_width = bbox[2] - bbox[0]
                
                x = (width - text_width) // 2
                y = subtitle_start_y + (i * 45)
                
                # Subtitle shadows
                draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 180), font=fonts["subtitle"])
                draw.text((x + 1, y + 1), line, fill=(0, 0, 0, 120), font=fonts["subtitle"])
                
                # Subtitle text in light gray
                draw.text((x, y), line, fill=(220, 220, 220, 255), font=fonts["subtitle"])
        
        return overlay
    
    def generate_cover_with_text(self, title="", subtitle="", style="dark", company="", custom_prompt=""):
        """Generate cover with proper text overlay"""
        
        # Style-based prompts (avoid text in generation)
        style_prompts = {
            "dark": "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic, clean composition, no text, no letters",
            "colorful": "cosmic purple and pink gradient space background, ethereal nebula atmosphere, floating spheres and planets, aurora light effects, otherworldly sci-fi environment, dreamy cosmic landscape, clean composition, no text, no letters", 
            "light": "clean minimal corporate background, soft gradients, professional business design, contemporary aesthetic, light blue and white tones, sophisticated layout, clean composition, no text, no letters"
        }
        
        base_prompt = custom_prompt or style_prompts.get(style, style_prompts["dark"])
        
        # Add company elements
        if company.lower() == "hedera":
            base_prompt += ", Hedera hashgraph elements, distributed ledger visualization, geometric H patterns"
        elif company.lower() == "bitcoin":
            base_prompt += ", Bitcoin blockchain elements, cryptocurrency visualization"
        
        print(f"\n🎨 Generating {style} style background...")
        print(f"📰 Title: {title}")
        print(f"📝 Subtitle: {subtitle}")
        
        try:
            # Generate clean background (no text)
            background = self.pipeline(
                prompt=base_prompt,
                negative_prompt="text, letters, words, titles, subtitles, existing logos, watermarks, signatures, typography, fonts, readable text, character, alphabet, numbers, low quality, blurry",
                width=1792,
                height=896,
                num_inference_steps=25,
                guidance_scale=7.5,
                num_images_per_prompt=1,
                generator=torch.Generator(device=self.device).manual_seed(42)
            ).images[0]
            
            # Resize to exact specification
            background = background.resize((1800, 900), Image.Resampling.LANCZOS)
            background_rgba = background.convert("RGBA")
            
            # Create text overlay
            text_overlay = self.create_text_overlay(1800, 900, title, subtitle)
            
            # Composite background + text
            if text_overlay:
                final_image = Image.alpha_composite(background_rgba, text_overlay)
            else:
                final_image = background_rgba
            
            # Apply watermark
            if self.watermark:
                watermark_resized = self.watermark.resize((1800, 900), Image.Resampling.LANCZOS)
                final_image = Image.alpha_composite(final_image, watermark_resized)
            
            return final_image.convert("RGB")
            
        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            return None

def test_text_overlay():
    """Test the text overlay system"""
    generator = TextOverlayGenerator()
    
    # Test cases
    test_cases = [
        {
            "title": "Hedera wins the Race",
            "subtitle": "Hashgraph Technology Leads Innovation",
            "style": "dark",
            "company": "hedera",
            "filename": "hedera_with_title.png"
        },
        {
            "title": "Bitcoin Reaches New Heights", 
            "subtitle": "Cryptocurrency Market Surges",
            "style": "dark",
            "company": "bitcoin",
            "filename": "bitcoin_with_title.png"
        },
        {
            "title": "DeFi Revolution Continues",
            "subtitle": "Decentralized Finance Transforms Banking",
            "style": "colorful",
            "company": "",
            "filename": "defi_with_title.png"
        }
    ]
    
    os.makedirs("/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", exist_ok=True)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/{len(test_cases)}: {test['title']}")
        
        cover = generator.generate_cover_with_text(
            title=test["title"],
            subtitle=test["subtitle"], 
            style=test["style"],
            company=test["company"]
        )
        
        if cover:
            filepath = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/{test['filename']}"
            cover.save(filepath)
            print(f"✅ Saved: {filepath}")
        else:
            print(f"❌ Failed to generate {test['filename']}")
    
    print("\n🎉 Text overlay testing complete!")

if __name__ == "__main__":
    test_text_overlay()