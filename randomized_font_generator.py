#!/usr/bin/env python3
"""
Randomized Font Generator with Custom Fonts and Subtle Shadows
Uses your custom font collection with elegant styling
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont
import os
import random
import argparse

class RandomizedFontGenerator:
    def __init__(self):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.pipeline = None
        self.watermark = None
        self.custom_fonts = [
            '/Users/valorkopeny/Library/Fonts/StyreneA-Black-Trial-BF63f6cbd9da245.otf',
            '/Users/valorkopeny/Library/Fonts/StretchPro.otf',
            '/Users/valorkopeny/Library/Fonts/fonnts.com-Aeonik-Bold.ttf'
        ]
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
    
    def get_random_fonts(self):
        """Load random selection from your custom fonts"""
        fonts = {}
        
        # Font sizes
        font_sizes = {
            "title": 150,
            "subtitle": 80,
            "small": 50
        }
        
        # Randomly select a font for this generation
        selected_font_path = random.choice(self.custom_fonts)
        font_name = os.path.basename(selected_font_path).split('.')[0]
        
        print(f"🎲 Selected font: {font_name}")
        
        # Load the selected font in different sizes
        for size_name, size in font_sizes.items():
            try:
                if os.path.exists(selected_font_path):
                    fonts[size_name] = ImageFont.truetype(selected_font_path, size)
                    print(f"✅ Loaded {size_name}: {size}px")
                else:
                    raise FileNotFoundError(f"Font not found: {selected_font_path}")
            except Exception as e:
                print(f"⚠️  Failed to load {selected_font_path}: {e}")
                # Fallback to system fonts
                fallback_fonts = [
                    "/System/Library/Fonts/Arial.ttc",
                    "/System/Library/Fonts/Helvetica.ttc"
                ]
                for fallback in fallback_fonts:
                    try:
                        if os.path.exists(fallback):
                            fonts[size_name] = ImageFont.truetype(fallback, size)
                            print(f"📝 Fallback to system font: {size}px")
                            break
                    except:
                        continue
                
                # Final fallback
                if size_name not in fonts:
                    fonts[size_name] = ImageFont.load_default()
                    print(f"⚠️  Using default font for {size_name}")
        
        return fonts, font_name
    
    def get_style_prompts(self, style="dark"):
        """Get enhanced prompts for different styles"""
        prompts = {
            "dark": "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic, depth of field, cinematic lighting, no text, no letters, no words",
            "colorful": "cosmic purple and pink gradient space background, ethereal nebula atmosphere, floating spheres and planets, aurora light effects, otherworldly sci-fi environment, dreamy cosmic landscape, no text, no letters, no words",
            "light": "clean minimal corporate background, soft gradients, professional business design, contemporary aesthetic, light blue and white tones, sophisticated layout, no text, no letters, no words"
        }
        return prompts.get(style, prompts["dark"])
    
    def create_elegant_text_overlay(self, width, height, title, subtitle="", fonts=None, font_name=""):
        """Create elegant text overlay with subtle shadows"""
        
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        if not fonts:
            fonts, font_name = self.get_random_fonts()
        
        # TITLE with elegant styling
        if title:
            title = title.upper()
            
            # Smart line breaking
            bbox = draw.textbbox((0, 0), title, font=fonts["title"])
            title_width = bbox[2] - bbox[0]
            
            if title_width > width * 0.9:
                words = title.split()
                if len(words) > 1:
                    best_split = len(words) // 2
                    line1 = " ".join(words[:best_split])
                    line2 = " ".join(words[best_split:])
                    title_lines = [line1, line2]
                else:
                    mid = len(title) // 2
                    title_lines = [title[:mid], title[mid:]]
            else:
                title_lines = [title]
            
            # Calculate positioning
            line_height = 180
            total_title_height = len(title_lines) * line_height
            start_y = (height - total_title_height) // 2 - 50
            
            for i, line in enumerate(title_lines):
                bbox = draw.textbbox((0, 0), line, font=fonts["title"])
                text_width = bbox[2] - bbox[0]
                
                x = (width - text_width) // 2
                y = start_y + (i * line_height)
                
                # SUBTLE shadow - much lighter and smaller offset
                # Single subtle shadow instead of multiple heavy shadows
                shadow_offset = 2  # Much smaller offset
                shadow_color = (0, 0, 0, 60)  # Much more transparent (was 255)
                
                draw.text((x + shadow_offset, y + shadow_offset), line, fill=shadow_color, font=fonts["title"])
                
                # Main text - crisp white
                draw.text((x, y), line, fill=(255, 255, 255, 255), font=fonts["title"])
                
                print(f"📝 Title line {i+1}: '{line}' at ({x}, {y})")
        
        # SUBTITLE with matching elegant styling
        if subtitle:
            subtitle_y = start_y + total_title_height + 60
            
            bbox = draw.textbbox((0, 0), subtitle, font=fonts["subtitle"])
            subtitle_width = bbox[2] - bbox[0]
            
            if subtitle_width > width * 0.9:
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
                
                # Subtle subtitle shadow
                shadow_offset = 1  # Even smaller for subtitle
                shadow_color = (0, 0, 0, 40)  # Very light shadow
                
                draw.text((x + shadow_offset, y + shadow_offset), line, fill=shadow_color, font=fonts["subtitle"])
                
                # Subtitle in elegant cyan
                draw.text((x, y), line, fill=(0, 255, 255, 255), font=fonts["subtitle"])
                
                print(f"📝 Subtitle line {i+1}: '{line}' at ({x}, {y})")
        
        return overlay
    
    def generate_cover_with_random_fonts(self, title="", subtitle="", style="dark", company="", custom_prompt=""):
        """Generate cover with randomized fonts and elegant styling"""
        
        # Get random fonts for this generation
        fonts, font_name = self.get_random_fonts()
        
        # Use custom or style-based prompt
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self.get_style_prompts(style)
        
        # Add company elements
        if company.lower() == "hedera":
            base_prompt += ", Hedera hashgraph elements, distributed ledger visualization, geometric H patterns"
        elif company.lower() == "bitcoin":
            base_prompt += ", Bitcoin blockchain elements, cryptocurrency visualization"
        
        print(f"\n🎨 Generating {style} style cover...")
        print(f"🎲 Using font: {font_name}")
        print(f"📰 Title: {title}")
        print(f"📝 Subtitle: {subtitle}")
        
        try:
            # Generate clean background
            image = self.pipeline(
                prompt=base_prompt,
                negative_prompt="text, letters, words, titles, subtitles, existing logos, watermarks, signatures, typography, fonts, readable text, characters, alphabet, numbers, low quality, blurry, amateur, ugly",
                width=1792,
                height=896,
                num_inference_steps=25,
                guidance_scale=7.5,
                num_images_per_prompt=1,
                generator=torch.Generator(device=self.device).manual_seed(random.randint(1, 1000))  # Random seed for variety
            ).images[0]
            
            # Resize to exact specification
            resized_image = image.resize((1800, 900), Image.Resampling.LANCZOS)
            base_rgba = resized_image.convert("RGBA")
            
            # Add elegant text overlay
            if title:
                text_overlay = self.create_elegant_text_overlay(1800, 900, title, subtitle, fonts, font_name)
                base_rgba = Image.alpha_composite(base_rgba, text_overlay)
            
            # Apply watermark
            if self.watermark:
                full_size_watermark = self.watermark.resize((1800, 900), Image.Resampling.LANCZOS)
                final_image = Image.alpha_composite(base_rgba, full_size_watermark)
            else:
                final_image = base_rgba
            
            print("✅ Cover generation complete")
            return final_image.convert("RGB"), font_name
            
        except Exception as e:
            print(f"❌ Cover generation failed: {str(e)}")
            return None, None

def test_randomized_fonts():
    """Test randomized font system with multiple generations"""
    generator = RandomizedFontGenerator()
    
    # Test cases to show font variety
    test_cases = [
        {
            "title": "Hedera Wins Race",
            "subtitle": "Hashgraph Technology Revolution",
            "style": "dark",
            "company": "hedera"
        },
        {
            "title": "Bitcoin Revolution", 
            "subtitle": "Cryptocurrency Market Update",
            "style": "dark",
            "company": "bitcoin"
        },
        {
            "title": "DeFi Innovation",
            "subtitle": "Building Future Finance",
            "style": "colorful",
            "company": ""
        }
    ]
    
    os.makedirs("/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", exist_ok=True)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/{len(test_cases)}: {test['title']}")
        
        cover, font_name = generator.generate_cover_with_random_fonts(
            title=test["title"],
            subtitle=test["subtitle"], 
            style=test["style"],
            company=test["company"]
        )
        
        if cover:
            # Include font name in filename
            safe_font = font_name.replace(' ', '_').replace('-', '_')[:20]
            filename = f"random_font_{safe_font}_{i}.png"
            filepath = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/{filename}"
            cover.save(filepath)
            print(f"✅ Saved: {filepath}")
            print(f"🎲 Font used: {font_name}")
        else:
            print(f"❌ Failed to generate test {i}")
    
    print("\n🎉 Randomized font testing complete!")
    print("🎨 Each cover uses a different random font from your collection")
    print("✨ Subtle shadows replace heavy drop shadows")

def main():
    parser = argparse.ArgumentParser(description="Randomized Font Cover Generator")
    parser.add_argument("--title", type=str, default="Test Title", help="Article title")
    parser.add_argument("--subtitle", type=str, default="Test Subtitle", help="Article subtitle") 
    parser.add_argument("--style", choices=["dark", "colorful", "light"], default="dark", help="Cover style")
    parser.add_argument("--company", type=str, default="", help="Company logo to integrate")
    parser.add_argument("--test", action="store_true", help="Run font randomization tests")
    
    args = parser.parse_args()
    
    if args.test:
        test_randomized_fonts()
    else:
        generator = RandomizedFontGenerator()
        cover, font_name = generator.generate_cover_with_random_fonts(
            title=args.title,
            subtitle=args.subtitle,
            style=args.style,
            company=args.company
        )
        
        if cover:
            filename = f"custom_font_cover.png"
            filepath = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/{filename}"
            cover.save(filepath)
            print(f"✅ Cover saved: {filepath}")
            print(f"🎲 Font used: {font_name}")

if __name__ == "__main__":
    main()