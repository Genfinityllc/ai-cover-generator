#!/usr/bin/env python3
"""
Final Production Generator - Massive Text System
Based on user reference examples with prominent, large-scale titles
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont
import os
import argparse
import json
from pathlib import Path

class FinalProductionGenerator:
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
            torch_dtype=torch.float32,  # Working config for MPS
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
        """Load large fonts matching reference scale"""
        fonts = {}
        
        font_paths = [
            "/System/Library/Fonts/Arial.ttc",
            "/System/Library/Fonts/Helvetica.ttc", 
            "/System/Library/Fonts/Futura.ttc",
            "/Library/Fonts/Arial.ttf"
        ]
        
        # Large font sizes based on user reference examples
        font_sizes = {
            "title": 150,      # Massive title like "Algorand"
            "subtitle": 80,    # Large subtitle 
            "small": 50        # Smaller elements
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
            
            if fonts[size_name] is None:
                fonts[size_name] = ImageFont.load_default()
        
        return fonts
    
    def get_style_prompts(self, style="dark"):
        """Get enhanced prompts for different styles"""
        prompts = {
            "dark": "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic, depth of field, cinematic lighting, no text, no letters, no words",
            "colorful": "cosmic purple and pink gradient space background, ethereal nebula atmosphere, floating spheres and planets, aurora light effects, otherworldly sci-fi environment, dreamy cosmic landscape, no text, no letters, no words",
            "light": "clean minimal corporate background, soft gradients, professional business design, contemporary aesthetic, light blue and white tones, sophisticated layout, no text, no letters, no words"
        }
        return prompts.get(style, prompts["dark"])
    
    def create_massive_text_overlay(self, width, height, title, subtitle=""):
        """Create massive text overlay like user reference examples"""
        
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        fonts = self.get_massive_fonts()
        
        # MASSIVE TITLE
        if title:
            title = title.upper()
            
            # Check if title fits on one line
            bbox = draw.textbbox((0, 0), title, font=fonts["title"])
            title_width = bbox[2] - bbox[0]
            
            # Smart line breaking
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
                
                # Multiple shadow layers for visibility
                shadow_layers = [
                    (6, 6, (0, 0, 0, 255)),
                    (4, 4, (0, 0, 0, 200)),
                    (2, 2, (0, 0, 0, 150)),
                ]
                
                for dx, dy, color in shadow_layers:
                    draw.text((x + dx, y + dy), line, fill=color, font=fonts["title"])
                
                # Main text - bright white
                draw.text((x, y), line, fill=(255, 255, 255, 255), font=fonts["title"])
        
        # LARGE SUBTITLE
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
                
                # Subtitle shadows
                draw.text((x + 3, y + 3), line, fill=(0, 0, 0, 220), font=fonts["subtitle"])
                draw.text((x + 2, y + 2), line, fill=(0, 0, 0, 180), font=fonts["subtitle"])
                
                # Subtitle in cyan
                draw.text((x, y), line, fill=(0, 255, 255, 255), font=fonts["subtitle"])
        
        return overlay
    
    def generate_final_cover(self, title="", subtitle="", style="dark", company="", custom_prompt=""):
        """Generate final production cover with massive text"""
        
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
                generator=torch.Generator(device=self.device).manual_seed(42)
            ).images[0]
            
            # Resize to exact specification
            resized_image = image.resize((1800, 900), Image.Resampling.LANCZOS)
            base_rgba = resized_image.convert("RGBA")
            
            # Add massive text overlay
            if title:
                text_overlay = self.create_massive_text_overlay(1800, 900, title, subtitle)
                base_rgba = Image.alpha_composite(base_rgba, text_overlay)
            
            # Apply watermark
            if self.watermark:
                full_size_watermark = self.watermark.resize((1800, 900), Image.Resampling.LANCZOS)
                final_image = Image.alpha_composite(base_rgba, full_size_watermark)
            else:
                final_image = base_rgba
            
            print("✅ Cover generation complete")
            return final_image.convert("RGB")
            
        except Exception as e:
            print(f"❌ Cover generation failed: {str(e)}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Final Production Cover Generator")
    parser.add_argument("--title", type=str, default="", help="Article title")
    parser.add_argument("--subtitle", type=str, default="", help="Article subtitle") 
    parser.add_argument("--style", choices=["dark", "colorful", "light"], default="dark", help="Cover style")
    parser.add_argument("--company", type=str, default="", help="Company logo to integrate")
    parser.add_argument("--custom-prompt", type=str, default="", help="Custom generation prompt")
    parser.add_argument("--output", type=str, default="/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", help="Output directory")
    parser.add_argument("--filename", type=str, default="final_cover.png", help="Output filename")
    
    args = parser.parse_args()
    
    generator = FinalProductionGenerator()
    
    cover = generator.generate_final_cover(
        title=args.title,
        subtitle=args.subtitle,
        style=args.style,
        company=args.company,
        custom_prompt=args.custom_prompt
    )
    
    if cover:
        os.makedirs(args.output, exist_ok=True)
        filepath = f"{args.output}/{args.filename}"
        cover.save(filepath)
        print(f"✅ Final cover saved: {filepath}")
        print(f"📐 Resolution: 1800x900")
        print(f"🏷️  Genfinity watermark: Applied")
        print(f"📰 Massive text: {args.title}")
    else:
        print("❌ Failed to generate cover")

if __name__ == "__main__":
    main()