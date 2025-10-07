#!/usr/bin/env python3
"""
Refined Logo Generator with Actual Brand Integration
Based on comprehensive analysis of reference examples
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont
import os
import random
import argparse

class RefinedLogoGenerator:
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
        
        font_sizes = {
            "title": 150,
            "subtitle": 80,
            "small": 50
        }
        
        selected_font_path = random.choice(self.custom_fonts)
        font_name = os.path.basename(selected_font_path).split('.')[0]
        
        print(f"🎲 Selected font: {font_name}")
        
        for size_name, size in font_sizes.items():
            try:
                if os.path.exists(selected_font_path):
                    fonts[size_name] = ImageFont.truetype(selected_font_path, size)
                else:
                    raise FileNotFoundError(f"Font not found: {selected_font_path}")
            except Exception as e:
                print(f"⚠️  Failed to load {selected_font_path}: {e}")
                fallback_fonts = [
                    "/System/Library/Fonts/Arial.ttc",
                    "/System/Library/Fonts/Helvetica.ttc"
                ]
                for fallback in fallback_fonts:
                    try:
                        if os.path.exists(fallback):
                            fonts[size_name] = ImageFont.truetype(fallback, size)
                            break
                    except:
                        continue
                
                if size_name not in fonts:
                    fonts[size_name] = ImageFont.load_default()
        
        return fonts, font_name
    
    def smart_line_breaking(self, title, draw, font):
        """Smart line breaking - longer first line, shorter second line"""
        words = title.split()
        
        if len(words) <= 2:
            return [title]  # Single line for short titles
        
        # Find the best split point for longer first line
        best_split = None
        best_ratio = 0
        
        for i in range(1, len(words)):
            line1 = " ".join(words[:i])
            line2 = " ".join(words[i:])
            
            # Calculate lengths
            bbox1 = draw.textbbox((0, 0), line1, font=font)
            bbox2 = draw.textbbox((0, 0), line2, font=font)
            width1 = bbox1[2] - bbox1[0]
            width2 = bbox2[2] - bbox2[0]
            
            # We want first line longer, so ratio should be > 1
            if width2 > 0:
                ratio = width1 / width2
                if ratio > best_ratio and ratio >= 1.2:  # First line at least 20% longer
                    best_ratio = ratio
                    best_split = i
        
        # If no good split found, use middle split
        if best_split is None:
            best_split = len(words) // 2 + 1  # Bias towards longer first line
        
        line1 = " ".join(words[:best_split])
        line2 = " ".join(words[best_split:])
        
        return [line1, line2]
    
    def get_refined_brand_prompts(self, client="hedera"):
        """Get high-quality prompts based on reference analysis"""
        
        brand_prompts = {
            "hedera": {
                "base": "professional cyberpunk technology background, high-tech digital environment, premium quality, photorealistic",
                "logos": "multiple Hedera H logo symbols scattered as background elements, white circular Hedera logos on dark background, Hedera branding elements integrated naturally, geometric H symbols floating in space",
                "tech": "hashgraph network visualization, distributed ledger technology, interconnected nodes, hexagonal patterns, professional blockchain aesthetic",
                "quality": "8k resolution, professional photography quality, cinematic lighting, depth of field"
            },
            
            "algorand": {
                "base": "modern professional technology background, clean corporate environment, premium fintech aesthetic, photorealistic",
                "logos": "multiple Algorand circular logo symbols as background elements, Algorand A symbols integrated into design, clean geometric Algorand branding, professional logo placement",
                "tech": "blockchain consensus visualization, pure proof of stake imagery, clean network nodes, modern geometric patterns, sophisticated technology design",
                "quality": "8k resolution, professional photography quality, corporate lighting, premium finish"
            },
            
            "constellation": {
                "base": "cosmic space technology background, stellar network environment, premium space aesthetic, photorealistic",
                "logos": "multiple Constellation star logo symbols floating in space, purple Constellation logos as background elements, geometric star patterns, professional space branding",
                "tech": "DAG network visualization, star constellation patterns, cosmic technology nodes, stellar distributed systems, space-based networking",
                "quality": "8k resolution, professional space photography, cosmic lighting, premium quality"
            }
        }
        
        if client.lower() not in brand_prompts:
            client = "hedera"
        
        brand = brand_prompts[client.lower()]
        
        # Combine for maximum quality and logo integration
        full_prompt = f"{brand['base']}, {brand['logos']}, {brand['tech']}, {brand['quality']}, professional article cover background, no text, no words, no letters"
        
        return full_prompt
    
    def create_refined_text_overlay(self, width, height, title, subtitle="", fonts=None, font_name=""):
        """Create refined text overlay with tight spacing and smart breaks"""
        
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        if not fonts:
            fonts, font_name = self.get_random_fonts()
        
        # TITLE with tight spacing and smart line breaking
        if title:
            title = title.upper()
            
            # Smart line breaking for longer first line
            title_lines = self.smart_line_breaking(title, draw, fonts["title"])
            
            # MUCH TIGHTER line spacing (was 180, now 140)
            line_height = 140  # Reduced from 180
            total_title_height = len(title_lines) * line_height
            start_y = (height - total_title_height) // 2 - 50
            
            for i, line in enumerate(title_lines):
                bbox = draw.textbbox((0, 0), line, font=fonts["title"])
                text_width = bbox[2] - bbox[0]
                
                x = (width - text_width) // 2
                y = start_y + (i * line_height)
                
                # Very subtle shadow
                shadow_offset = 2
                shadow_color = (0, 0, 0, 50)  # Even more subtle
                
                draw.text((x + shadow_offset, y + shadow_offset), line, fill=shadow_color, font=fonts["title"])
                draw.text((x, y), line, fill=(255, 255, 255, 255), font=fonts["title"])
                
                print(f"📝 Title line {i+1}: '{line}' at ({x}, {y})")
        
        # SUBTITLE with matching tight spacing
        if subtitle:
            # Position closer to title (was +60, now +40)
            subtitle_y = start_y + total_title_height + 40  # Tighter spacing
            
            bbox = draw.textbbox((0, 0), subtitle, font=fonts["subtitle"])
            subtitle_width = bbox[2] - bbox[0]
            
            if subtitle_width > width * 0.9:
                words = subtitle.split()
                # Apply same smart breaking to subtitle
                subtitle_lines = self.smart_line_breaking(subtitle, draw, fonts["subtitle"])
            else:
                subtitle_lines = [subtitle]
            
            for i, line in enumerate(subtitle_lines):
                bbox = draw.textbbox((0, 0), line, font=fonts["subtitle"])
                text_width = bbox[2] - bbox[0]
                
                x = (width - text_width) // 2
                y = subtitle_y + (i * 70)  # Tighter subtitle spacing
                
                # Subtle subtitle shadow
                shadow_offset = 1
                shadow_color = (0, 0, 0, 30)
                
                draw.text((x + shadow_offset, y + shadow_offset), line, fill=shadow_color, font=fonts["subtitle"])
                draw.text((x, y), line, fill=(0, 255, 255, 255), font=fonts["subtitle"])
                
                print(f"📝 Subtitle line {i+1}: '{line}' at ({x}, {y})")
        
        return overlay
    
    def generate_refined_cover(self, title="", subtitle="", client="hedera"):
        """Generate refined cover with actual logo integration and tight spacing"""
        
        fonts, font_name = self.get_random_fonts()
        
        # Get refined prompt with actual logo integration
        brand_prompt = self.get_refined_brand_prompts(client)
        
        print(f"\n🏢 Generating REFINED {client.upper()} cover...")
        print(f"🎲 Using font: {font_name}")
        print(f"📰 Title: {title}")
        print(f"📝 Subtitle: {subtitle}")
        print(f"🎨 Logos: Actual {client} logo elements in background")
        print(f"✨ Quality: High-resolution professional finish")
        
        try:
            # Generate with higher quality settings for refined look
            image = self.pipeline(
                prompt=brand_prompt,
                negative_prompt="text, letters, words, titles, subtitles, watermarks, signatures, typography, fonts, readable text, characters, alphabet, numbers, low quality, blurry, amateur, ugly, poor lighting, pixelated, distorted logos",
                width=1792,
                height=896,
                num_inference_steps=35,  # Higher quality
                guidance_scale=9.0,      # Stronger prompt adherence
                num_images_per_prompt=1,
                generator=torch.Generator(device=self.device).manual_seed(random.randint(100, 999))
            ).images[0]
            
            # Resize to exact specification
            resized_image = image.resize((1800, 900), Image.Resampling.LANCZOS)
            base_rgba = resized_image.convert("RGBA")
            
            # Add refined text overlay with tight spacing
            if title:
                text_overlay = self.create_refined_text_overlay(1800, 900, title, subtitle, fonts, font_name)
                base_rgba = Image.alpha_composite(base_rgba, text_overlay)
            
            # Apply watermark
            if self.watermark:
                full_size_watermark = self.watermark.resize((1800, 900), Image.Resampling.LANCZOS)
                final_image = Image.alpha_composite(base_rgba, full_size_watermark)
            else:
                final_image = base_rgba
            
            print("✅ Refined cover generation complete")
            return final_image.convert("RGB"), font_name
            
        except Exception as e:
            print(f"❌ Cover generation failed: {str(e)}")
            return None, None

def test_refined_system():
    """Test the refined system with better logos and spacing"""
    generator = RefinedLogoGenerator()
    
    # Test cases based on your reference examples
    refined_tests = [
        {
            "title": "Hedera Network Update",
            "subtitle": "AI RWAS Stablecoins Innovation",
            "client": "hedera"
        },
        {
            "title": "Algorand Goes Natively Multichain",
            "subtitle": "Cross Chain Technology Breakthrough", 
            "client": "algorand"
        },
        {
            "title": "Constellation Network DEX is Live",
            "subtitle": "Decentralized Exchange Launch",
            "client": "constellation"
        }
    ]
    
    os.makedirs("/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", exist_ok=True)
    
    for i, test in enumerate(refined_tests, 1):
        print(f"\n🧪 Refined Test {i}/{len(refined_tests)}: {test['client'].upper()}")
        
        cover, font_name = generator.generate_refined_cover(
            title=test["title"],
            subtitle=test["subtitle"], 
            client=test["client"]
        )
        
        if cover:
            filename = f"refined_{test['client']}_{font_name.replace(' ', '_')[:15]}.png"
            filepath = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/{filename}"
            cover.save(filepath)
            print(f"✅ Saved: {filepath}")
            print(f"🏢 Client: {test['client'].upper()}")
            print(f"🎲 Font: {font_name}")
            print(f"✨ Features: Tight spacing + Logo integration + High quality")
        else:
            print(f"❌ Failed to generate refined {test['client']} cover")
    
    print("\n🎉 Refined system testing complete!")
    print("✨ Enhanced with: Actual logo integration, tight line spacing, smart line breaks, premium quality")

def main():
    parser = argparse.ArgumentParser(description="Refined Logo Integration Generator")
    parser.add_argument("--title", type=str, default="Brand Technology Update", help="Article title")
    parser.add_argument("--subtitle", type=str, default="Innovation Breakthrough", help="Article subtitle") 
    parser.add_argument("--client", choices=["hedera", "algorand", "constellation"], default="hedera", help="Client brand")
    parser.add_argument("--test", action="store_true", help="Run refined system tests")
    
    args = parser.parse_args()
    
    if args.test:
        test_refined_system()
    else:
        generator = RefinedLogoGenerator()
        cover, font_name = generator.generate_refined_cover(
            title=args.title,
            subtitle=args.subtitle,
            client=args.client
        )
        
        if cover:
            filename = f"refined_cover_{args.client}.png"
            filepath = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/{filename}"
            cover.save(filepath)
            print(f"✅ Cover saved: {filepath}")
            print(f"🏢 Client: {args.client.upper()}")
            print(f"🎲 Font: {font_name}")

if __name__ == "__main__":
    main()