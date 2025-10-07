#!/usr/bin/env python3
"""
Production Cover Generator - Complete System
Combines all improvements: watermark overlay, title integration, style training
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont
import os
import argparse
import json
from pathlib import Path

class ProductionCoverGenerator:
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
    
    def get_style_prompts(self, style="dark"):
        """Get enhanced prompts for different styles"""
        prompts = {
            "dark": [
                "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic, depth of field, cinematic lighting",
                "futuristic dark interface design, glowing circuit patterns, digital data streams, cyberpunk atmosphere with purple and blue neon accents, 3D geometric elements, tech industry professional background",
                "dark sci-fi technology background, holographic displays, neon grid patterns, blockchain visualization, digital technology theme, professional article cover aesthetic, atmospheric lighting"
            ],
            "colorful": [
                "cosmic purple and pink gradient space background, ethereal nebula atmosphere, floating spheres and planets, aurora light effects, otherworldly sci-fi environment, dreamy cosmic landscape",
                "vibrant cosmic nebula scene, purple pink orange gradient colors, floating cosmic orbs, energy light beams, space phenomena, ethereal atmosphere, futuristic cover background",
                "psychedelic space background, cosmic aurora colors, floating planetary spheres, light beam effects, vibrant sci-fi aesthetic, otherworldly landscape, cosmic energy"
            ],
            "light": [
                "clean minimal corporate background, soft gradients, professional business design, contemporary aesthetic, light blue and white tones, sophisticated layout",
                "bright modern professional background, subtle geometric patterns, light colors, clean corporate style, minimal design elements",
                "light corporate background, minimal geometric elements, soft gradients, professional business design, clean modern aesthetic"
            ]
        }
        return prompts.get(style, prompts["dark"])
    
    def generate_article_cover(self, title="", subtitle="", style="dark", company_logo="", custom_prompt=""):
        """Generate complete article cover with title and watermark"""
        
        # Use custom prompt or style-based prompt
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            prompts = self.get_style_prompts(style)
            base_prompt = prompts[0]  # Use primary prompt for style
        
        # Add company-specific elements if provided
        if company_logo.lower() == "hedera":
            base_prompt += ", Hedera hashgraph elements, distributed ledger visualization, geometric H patterns"
        elif company_logo.lower() == "bitcoin":
            base_prompt += ", Bitcoin blockchain elements, cryptocurrency visualization, digital gold themes"
        
        print(f"\n🎨 Generating {style} style cover...")
        print(f"📰 Title: {title}")
        print(f"📝 Base prompt: {base_prompt[:80]}...")
        
        try:
            # Generate base image
            image = self.pipeline(
                prompt=base_prompt,
                negative_prompt="text, letters, words, existing logos, watermarks, signatures, low quality, blurry, amateur, ugly",
                width=1792,
                height=896,
                num_inference_steps=25,
                guidance_scale=7.5,
                num_images_per_prompt=1,
                generator=torch.Generator(device=self.device).manual_seed(42)
            ).images[0]
            
            # Resize to exact specification (1800x900)
            resized_image = image.resize((1800, 900), Image.Resampling.LANCZOS)
            base_rgba = resized_image.convert("RGBA")
            
            # Add title overlay if provided
            if title:
                title_overlay = Image.new("RGBA", (1800, 900), (0, 0, 0, 0))
                draw = ImageDraw.Draw(title_overlay)
                
                # Load fonts
                try:
                    title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", 64)
                    subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", 32)
                except:
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
                
                # Calculate title positioning
                title_bbox = draw.textbbox((0, 0), title.upper(), font=title_font)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (1800 - title_width) // 2
                title_y = 120
                
                # Add title with shadow
                draw.text((title_x + 3, title_y + 3), title.upper(), fill=(0, 0, 0, 200), font=title_font)
                draw.text((title_x, title_y), title.upper(), fill=(255, 255, 255, 255), font=title_font)
                
                # Add subtitle if provided
                if subtitle:
                    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
                    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                    subtitle_x = (1800 - subtitle_width) // 2
                    subtitle_y = title_y + 80
                    
                    draw.text((subtitle_x + 2, subtitle_y + 2), subtitle, fill=(0, 0, 0, 150), font=subtitle_font)
                    draw.text((subtitle_x, subtitle_y), subtitle, fill=(200, 200, 200, 255), font=subtitle_font)
                
                # Composite title
                base_rgba = Image.alpha_composite(base_rgba, title_overlay)
            
            # Apply watermark overlay (full-size centered)
            if self.watermark:
                full_size_watermark = self.watermark.resize((1800, 900), Image.Resampling.LANCZOS)
                final_image = Image.alpha_composite(base_rgba, full_size_watermark)
            else:
                final_image = base_rgba
            
            # Convert to RGB and return
            final_rgb = final_image.convert("RGB")
            
            print("✅ Cover generation complete")
            return final_rgb
            
        except Exception as e:
            print(f"❌ Cover generation failed: {str(e)}")
            return None
    
    def batch_generate(self, articles, style="dark", output_dir="generated_covers"):
        """Generate multiple covers for a list of articles"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📰 Batch generating {len(articles)} covers...")
        
        for i, article in enumerate(articles, 1):
            title = article.get("title", f"Article {i}")
            subtitle = article.get("subtitle", "")
            company = article.get("company", "")
            
            print(f"\n📰 {i}/{len(articles)}: {title}")
            
            cover = self.generate_article_cover(
                title=title,
                subtitle=subtitle,
                style=style,
                company_logo=company
            )
            
            if cover:
                # Safe filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:40]
                filename = f"{output_dir}/{style}_{safe_title.replace(' ', '_')}.png"
                cover.save(filename)
                print(f"✅ Saved: {filename}")
            
        print(f"\n🎉 Batch generation complete! Check {output_dir}/ directory")

def main():
    parser = argparse.ArgumentParser(description="Production Cover Generator")
    parser.add_argument("--title", type=str, default="", help="Article title")
    parser.add_argument("--subtitle", type=str, default="", help="Article subtitle")
    parser.add_argument("--style", choices=["dark", "colorful", "light"], default="dark", help="Cover style")
    parser.add_argument("--company", type=str, default="", help="Company logo to integrate (hedera, bitcoin, etc)")
    parser.add_argument("--custom-prompt", type=str, default="", help="Custom generation prompt")
    parser.add_argument("--batch", type=str, help="JSON file with batch articles")
    parser.add_argument("--output", type=str, default="style_outputs", help="Output directory")
    
    args = parser.parse_args()
    
    generator = ProductionCoverGenerator()
    
    if args.batch:
        # Batch mode
        with open(args.batch, 'r') as f:
            articles = json.load(f)
        generator.batch_generate(articles, args.style, args.output)
    else:
        # Single cover mode
        cover = generator.generate_article_cover(
            title=args.title,
            subtitle=args.subtitle,
            style=args.style,
            company_logo=args.company,
            custom_prompt=args.custom_prompt
        )
        
        if cover:
            filename = f"{args.output}/production_cover.png"
            os.makedirs(args.output, exist_ok=True)
            cover.save(filename)
            print(f"✅ Cover saved: {filename}")

if __name__ == "__main__":
    main()