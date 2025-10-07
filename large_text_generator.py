#!/usr/bin/env python3
"""
Large-Scale Text Generator
Creates massive, professional titles matching your reference examples
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

class LargeTextGenerator:
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
    
    def get_massive_fonts(self):
        """Load very large fonts for prominent text"""
        fonts = {}
        
        # System font paths
        font_paths = [
            "/System/Library/Fonts/Arial.ttc",
            "/System/Library/Fonts/Helvetica.ttc", 
            "/System/Library/Fonts/Futura.ttc",
            "/Library/Fonts/Arial.ttf"
        ]
        
        # Much larger font sizes based on your reference images
        font_sizes = {
            "title": 150,      # Massive title (was 72)
            "subtitle": 80,    # Large subtitle (was 36) 
            "small": 50        # Small text (was 24)
        }
        
        for size_name, size in font_sizes.items():
            fonts[size_name] = None
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        fonts[size_name] = ImageFont.truetype(font_path, size)
                        break
                except:
                    continue
            
            # Fallback
            if fonts[size_name] is None:
                fonts[size_name] = ImageFont.load_default()
        
        return fonts
    
    def create_massive_text_overlay(self, width, height, title, subtitle=""):
        """Create prominent text overlay like your reference examples"""
        
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        fonts = self.get_massive_fonts()
        
        # MASSIVE TITLE (like "Algorand" in your reference)
        if title:
            title = title.upper()
            
            # Check if title fits on one line
            bbox = draw.textbbox((0, 0), title, font=fonts["title"])
            title_width = bbox[2] - bbox[0]
            
            # If too wide, split intelligently
            if title_width > width * 0.9:  # 90% of width max
                # Split at natural break points
                words = title.split()
                if len(words) > 1:
                    # Try different split points
                    best_split = len(words) // 2
                    line1 = " ".join(words[:best_split])
                    line2 = " ".join(words[best_split:])
                    title_lines = [line1, line2]
                else:
                    # Single long word - force wrap
                    mid = len(title) // 2
                    title_lines = [title[:mid], title[mid:]]
            else:
                title_lines = [title]
            
            # Calculate vertical centering
            line_height = 180  # Spacing between lines
            total_title_height = len(title_lines) * line_height
            
            # Center vertically, but bias towards upper-center
            start_y = (height - total_title_height) // 2 - 50
            
            for i, line in enumerate(title_lines):
                # Get precise text dimensions
                bbox = draw.textbbox((0, 0), line, font=fonts["title"])
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center horizontally
                x = (width - text_width) // 2
                y = start_y + (i * line_height)
                
                # BOLD shadow effects for visibility
                shadow_layers = [
                    (6, 6, (0, 0, 0, 255)),    # Deep shadow
                    (4, 4, (0, 0, 0, 200)),    # Medium shadow
                    (2, 2, (0, 0, 0, 150)),    # Light shadow
                ]
                
                # Draw shadows
                for dx, dy, color in shadow_layers:
                    draw.text((x + dx, y + dy), line, fill=color, font=fonts["title"])
                
                # Main text - bright white
                draw.text((x, y), line, fill=(255, 255, 255, 255), font=fonts["title"])
        
        # LARGE SUBTITLE (like "Building Intelligent Infrastructure")
        if subtitle:
            # Position below title
            subtitle_y = start_y + total_title_height + 60
            
            # Check if subtitle fits
            bbox = draw.textbbox((0, 0), subtitle, font=fonts["subtitle"])
            subtitle_width = bbox[2] - bbox[0]
            
            if subtitle_width > width * 0.9:
                # Wrap subtitle if needed
                words = subtitle.split()
                mid = len(words) // 2
                line1 = " ".join(words[:mid])
                line2 = " ".join(words[mid:])
                subtitle_lines = [line1, line2]
            else:
                subtitle_lines = [subtitle]
            
            for i, line in enumerate(subtitle_lines):
                bbox = draw.textbbox((0, 0), line, font=fonts["subtitle"])
                text_width = bbox[2] - bbox[0]
                
                x = (width - text_width) // 2
                y = subtitle_y + (i * 90)
                
                # Subtitle shadows
                draw.text((x + 3, y + 3), line, fill=(0, 0, 0, 220), font=fonts["subtitle"])
                draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 180), font=fonts["subtitle"])
                
                # Subtitle in cyan/blue (like your reference)
                draw.text((x, y), line, fill=(0, 255, 255, 255), font=fonts["subtitle"])
        
        return overlay
    
    def generate_cover_with_massive_text(self, title="", subtitle="", style="dark", company=""):
        """Generate cover with massive, prominent text"""
        
        # Clean background prompts (no text generation)
        style_prompts = {
            "dark": "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic, clean composition, no text, no letters, no words",
            "colorful": "cosmic purple and pink gradient space background, ethereal nebula atmosphere, floating spheres and planets, aurora light effects, otherworldly sci-fi environment, dreamy cosmic landscape, clean composition, no text, no letters, no words", 
            "light": "clean minimal corporate background, soft gradients, professional business design, contemporary aesthetic, light blue and white tones, sophisticated layout, clean composition, no text, no letters, no words"
        }
        
        base_prompt = style_prompts.get(style, style_prompts["dark"])
        
        # Add company elements
        if company.lower() == "hedera":
            base_prompt += ", Hedera hashgraph elements, distributed ledger visualization, geometric H patterns"
        elif company.lower() == "bitcoin":
            base_prompt += ", Bitcoin blockchain elements, cryptocurrency visualization"
        
        print(f"\n🎨 Generating {style} style with MASSIVE text...")
        print(f"📰 Title: {title}")
        print(f"📝 Subtitle: {subtitle}")
        
        try:
            # Generate clean background
            background = self.pipeline(
                prompt=base_prompt,
                negative_prompt="text, letters, words, titles, subtitles, typography, fonts, readable text, characters, alphabet, numbers, logos, watermarks, signatures, low quality, blurry",
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
            
            # Create MASSIVE text overlay
            text_overlay = self.create_massive_text_overlay(1800, 900, title, subtitle)
            
            # Composite background + massive text
            final_image = Image.alpha_composite(background_rgba, text_overlay)
            
            # Apply watermark last
            if self.watermark:
                watermark_resized = self.watermark.resize((1800, 900), Image.Resampling.LANCZOS)
                final_image = Image.alpha_composite(final_image, watermark_resized)
            
            return final_image.convert("RGB")
            
        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            return None

def test_massive_text():
    """Test massive text system"""
    generator = LargeTextGenerator()
    
    # Test cases matching your reference style
    test_cases = [
        {
            "title": "Hedera Wins Race",
            "subtitle": "Hashgraph Technology Revolution",
            "style": "dark",
            "company": "hedera",
            "filename": "massive_hedera.png"
        },
        {
            "title": "Bitcoin Update", 
            "subtitle": "Cryptocurrency Market Analysis",
            "style": "dark",
            "company": "bitcoin",
            "filename": "massive_bitcoin.png"
        },
        {
            "title": "DeFi Revolution",
            "subtitle": "Building Decentralized Finance",
            "style": "colorful",
            "company": "",
            "filename": "massive_defi.png"
        }
    ]
    
    os.makedirs("/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", exist_ok=True)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/{len(test_cases)}: {test['title']}")
        
        cover = generator.generate_cover_with_massive_text(
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
    
    print("\n🎉 Massive text testing complete!")
    print("📏 Text now matches reference scale - much larger and more prominent!")

if __name__ == "__main__":
    test_massive_text()