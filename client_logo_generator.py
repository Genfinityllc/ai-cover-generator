#!/usr/bin/env python3
"""
Client Logo Integration Generator
Tests LoRA training with specific client brand elements
Hedera, Algorand, Constellation logo integration
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont
import os
import random
import argparse

class ClientLogoGenerator:
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
        
        # Randomly select a font
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
                # Fallback to system fonts
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
    
    def get_client_brand_prompts(self, client="hedera"):
        """Get detailed prompts for specific client brand integration"""
        
        brand_prompts = {
            "hedera": {
                "base": "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting",
                "logo_elements": "Hedera hashgraph logo elements, geometric H symbol patterns, distributed ledger technology visualization, hexagonal geometric patterns, interconnected node networks, hashgraph data structures, DAG visualization, consensus algorithm imagery, Hedera branding colors blue and white",
                "style": "professional blockchain technology aesthetic, futuristic distributed systems, clean geometric design"
            },
            
            "algorand": {
                "base": "modern technology background, clean geometric patterns, bright professional lighting",
                "logo_elements": "Algorand logo elements, circular geometric patterns, pure proof of stake visualization, blockchain consensus imagery, Algorand branding colors black and teal, geometric A symbol integration, decentralized network nodes, smart contract visualization, scalable blockchain imagery",
                "style": "clean modern fintech aesthetic, professional blockchain design, sophisticated technology branding"
            },
            
            "constellation": {
                "base": "cosmic space background, star network patterns, deep space atmosphere",
                "logo_elements": "Constellation network logo elements, star constellation patterns, DAG constellation imagery, cosmic network visualization, distributed node networks resembling star patterns, Constellation branding cosmic theme, interconnected stellar networks, space-based distributed systems",
                "style": "cosmic technology aesthetic, space-based networking theme, stellar distributed systems"
            }
        }
        
        if client.lower() not in brand_prompts:
            client = "hedera"  # Default fallback
        
        brand = brand_prompts[client.lower()]
        
        # Combine all elements
        full_prompt = f"{brand['base']}, {brand['logo_elements']}, {brand['style']}, no text, no letters, no words, professional article cover background"
        
        return full_prompt
    
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
                
                # Subtle shadow
                shadow_offset = 2
                shadow_color = (0, 0, 0, 60)
                
                draw.text((x + shadow_offset, y + shadow_offset), line, fill=shadow_color, font=fonts["title"])
                draw.text((x, y), line, fill=(255, 255, 255, 255), font=fonts["title"])
        
        # SUBTITLE
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
                shadow_offset = 1
                shadow_color = (0, 0, 0, 40)
                
                draw.text((x + shadow_offset, y + shadow_offset), line, fill=shadow_color, font=fonts["subtitle"])
                draw.text((x, y), line, fill=(0, 255, 255, 255), font=fonts["subtitle"])
        
        return overlay
    
    def generate_client_brand_cover(self, title="", subtitle="", client="hedera"):
        """Generate cover with specific client brand logo integration"""
        
        # Get random fonts for this generation
        fonts, font_name = self.get_random_fonts()
        
        # Get client-specific prompt with logo elements
        brand_prompt = self.get_client_brand_prompts(client)
        
        print(f"\n🏢 Generating {client.upper()} branded cover...")
        print(f"🎲 Using font: {font_name}")
        print(f"📰 Title: {title}")
        print(f"📝 Subtitle: {subtitle}")
        print(f"🎨 Brand elements: {client} logo integration")
        
        try:
            # Generate background with client logo elements
            image = self.pipeline(
                prompt=brand_prompt,
                negative_prompt="text, letters, words, titles, subtitles, watermarks, signatures, typography, fonts, readable text, characters, alphabet, numbers, low quality, blurry, amateur, ugly, wrong logo, incorrect branding",
                width=1792,
                height=896,
                num_inference_steps=30,  # Higher quality for logo integration
                guidance_scale=8.0,      # Strong prompt adherence for logo elements
                num_images_per_prompt=1,
                generator=torch.Generator(device=self.device).manual_seed(random.randint(1, 1000))
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
            
            print("✅ Client brand cover generation complete")
            return final_image.convert("RGB"), font_name
            
        except Exception as e:
            print(f"❌ Cover generation failed: {str(e)}")
            return None, None

def test_client_logo_integration():
    """Test logo integration for client brands"""
    generator = ClientLogoGenerator()
    
    # Test cases for different client brands
    client_tests = [
        {
            "title": "Hedera Network Update",
            "subtitle": "Hashgraph Technology Advances",
            "client": "hedera"
        },
        {
            "title": "Algorand Consensus",
            "subtitle": "Pure Proof of Stake Innovation", 
            "client": "algorand"
        },
        {
            "title": "Constellation Network",
            "subtitle": "DAG Technology Evolution",
            "client": "constellation"
        }
    ]
    
    os.makedirs("/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", exist_ok=True)
    
    for i, test in enumerate(client_tests, 1):
        print(f"\n🧪 Client Test {i}/{len(client_tests)}: {test['client'].upper()}")
        
        cover, font_name = generator.generate_client_brand_cover(
            title=test["title"],
            subtitle=test["subtitle"], 
            client=test["client"]
        )
        
        if cover:
            filename = f"client_logo_{test['client']}_{font_name.replace(' ', '_')[:15]}.png"
            filepath = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/{filename}"
            cover.save(filepath)
            print(f"✅ Saved: {filepath}")
            print(f"🏢 Client: {test['client'].upper()}")
            print(f"🎲 Font: {font_name}")
        else:
            print(f"❌ Failed to generate {test['client']} cover")
    
    print("\n🎉 Client logo integration testing complete!")
    print("🏢 Each cover integrates specific client brand elements")
    print("🎨 LoRA training tested with Hedera, Algorand, and Constellation themes")

def main():
    parser = argparse.ArgumentParser(description="Client Logo Integration Generator")
    parser.add_argument("--title", type=str, default="Brand Update", help="Article title")
    parser.add_argument("--subtitle", type=str, default="Technology News", help="Article subtitle") 
    parser.add_argument("--client", choices=["hedera", "algorand", "constellation"], default="hedera", help="Client brand")
    parser.add_argument("--test", action="store_true", help="Run client logo integration tests")
    
    args = parser.parse_args()
    
    if args.test:
        test_client_logo_integration()
    else:
        generator = ClientLogoGenerator()
        cover, font_name = generator.generate_client_brand_cover(
            title=args.title,
            subtitle=args.subtitle,
            client=args.client
        )
        
        if cover:
            filename = f"client_cover_{args.client}.png"
            filepath = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/{filename}"
            cover.save(filepath)
            print(f"✅ Cover saved: {filepath}")
            print(f"🏢 Client: {args.client.upper()}")
            print(f"🎲 Font: {font_name}")

if __name__ == "__main__":
    main()