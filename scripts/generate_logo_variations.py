#!/usr/bin/env python3
"""
Logo Variation Generator
Takes 1 high-quality logo and creates 20+ training variations
Automatically handles backgrounds, sizes, effects, and formats
"""

import os
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random
import numpy as np

class LogoVariationGenerator:
    def __init__(self, output_size=(512, 512)):
        self.output_size = output_size
        self.variation_count = 0
        
        # Background colors for variations
        self.background_colors = [
            (255, 255, 255),    # White
            (0, 0, 0),          # Black
            (50, 50, 50),       # Dark gray
            (200, 200, 200),    # Light gray
            (240, 240, 240),    # Off-white
            (30, 30, 30),       # Near black
            (100, 100, 100),    # Medium gray
            (250, 250, 250),    # Very light gray
        ]
        
        # Gradient backgrounds
        self.gradient_colors = [
            [(0, 0, 0), (100, 100, 100)],      # Black to gray
            [(255, 255, 255), (200, 200, 200)], # White to light gray
            [(50, 50, 50), (150, 150, 150)],   # Dark to medium gray
            [(240, 240, 240), (255, 255, 255)], # Light gradient
        ]
        
        # Crypto-themed backgrounds
        self.crypto_colors = [
            (247, 147, 26),     # Bitcoin orange
            (98, 126, 234),     # Ethereum blue
            (242, 169, 0),      # Binance gold
            (0, 82, 255),       # Coinbase blue
            (26, 117, 255),     # Crypto blue
            (255, 102, 0),      # Orange
        ]
    
    def load_logo(self, logo_path: str) -> Image.Image:
        """Load and prepare logo image"""
        print(f"📁 Loading logo: {logo_path}")
        
        logo = Image.open(logo_path)
        
        # Convert to RGBA to handle transparency
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        print(f"   Original size: {logo.size}")
        print(f"   Mode: {logo.mode}")
        
        return logo
    
    def resize_logo_for_background(self, logo: Image.Image, bg_size: tuple, scale_factor: float) -> Image.Image:
        """Resize logo to fit background with specified scale"""
        
        # Calculate new size maintaining aspect ratio
        logo_width, logo_height = logo.size
        bg_width, bg_height = bg_size
        
        # Scale the logo
        max_width = int(bg_width * scale_factor)
        max_height = int(bg_height * scale_factor)
        
        # Maintain aspect ratio
        width_ratio = max_width / logo_width
        height_ratio = max_height / logo_height
        scale_ratio = min(width_ratio, height_ratio)
        
        new_width = int(logo_width * scale_ratio)
        new_height = int(logo_height * scale_ratio)
        
        return logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def create_solid_background(self, color: tuple) -> Image.Image:
        """Create solid color background"""
        return Image.new('RGB', self.output_size, color)
    
    def create_gradient_background(self, color1: tuple, color2: tuple, direction='vertical') -> Image.Image:
        """Create gradient background"""
        width, height = self.output_size
        background = Image.new('RGB', self.output_size, color1)
        draw = ImageDraw.Draw(background)
        
        if direction == 'vertical':
            for y in range(height):
                ratio = y / height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
        else:  # horizontal
            for x in range(width):
                ratio = x / width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(x, 0), (x, height)], fill=(r, g, b))
        
        return background
    
    def create_noise_background(self, base_color: tuple, noise_level=20) -> Image.Image:
        """Create background with subtle noise"""
        width, height = self.output_size
        background = Image.new('RGB', self.output_size, base_color)
        
        # Add noise
        noise = np.random.randint(-noise_level, noise_level, (height, width, 3))
        bg_array = np.array(background)
        noisy_array = np.clip(bg_array + noise, 0, 255).astype(np.uint8)
        
        return Image.fromarray(noisy_array)
    
    def apply_logo_effects(self, logo: Image.Image, effect_type: str) -> Image.Image:
        """Apply effects to logo"""
        if effect_type == 'blur':
            return logo.filter(ImageFilter.GaussianBlur(radius=1))
        elif effect_type == 'sharpen':
            return logo.filter(ImageFilter.SHARPEN)
        elif effect_type == 'brightness_up':
            enhancer = ImageEnhance.Brightness(logo)
            return enhancer.enhance(1.2)
        elif effect_type == 'brightness_down':
            enhancer = ImageEnhance.Brightness(logo)
            return enhancer.enhance(0.8)
        elif effect_type == 'contrast_up':
            enhancer = ImageEnhance.Contrast(logo)
            return enhancer.enhance(1.3)
        elif effect_type == 'contrast_down':
            enhancer = ImageEnhance.Contrast(logo)
            return enhancer.enhance(0.7)
        else:
            return logo
    
    def position_logo_on_background(self, background: Image.Image, logo: Image.Image, position='center') -> Image.Image:
        """Position logo on background"""
        bg_width, bg_height = background.size
        logo_width, logo_height = logo.size
        
        if position == 'center':
            x = (bg_width - logo_width) // 2
            y = (bg_height - logo_height) // 2
        elif position == 'top_left':
            x = bg_width // 8
            y = bg_height // 8
        elif position == 'top_right':
            x = bg_width - logo_width - (bg_width // 8)
            y = bg_height // 8
        elif position == 'bottom_left':
            x = bg_width // 8
            y = bg_height - logo_height - (bg_height // 8)
        elif position == 'bottom_right':
            x = bg_width - logo_width - (bg_width // 8)
            y = bg_height - logo_height - (bg_height // 8)
        else:  # random
            x = random.randint(20, bg_width - logo_width - 20)
            y = random.randint(20, bg_height - logo_height - 20)
        
        # Paste logo with transparency
        background.paste(logo, (x, y), logo)
        return background
    
    def generate_variations(self, logo_path: str, output_dir: str, count: int = 25) -> list:
        """Generate multiple logo variations"""
        
        print(f"🎨 Generating {count} logo variations...")
        
        # Load original logo
        original_logo = self.load_logo(logo_path)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        variations = []
        
        # Generate variations
        for i in range(count):
            variation_name = f"variation_{i+1:02d}.png"
            variation_path = output_path / variation_name
            
            # Choose variation parameters
            scale_factor = random.uniform(0.3, 0.8)  # Logo size relative to background
            
            # Resize logo
            sized_logo = self.resize_logo_for_background(original_logo, self.output_size, scale_factor)
            
            # Choose background type
            bg_type = random.choice(['solid', 'gradient', 'noise', 'crypto'])
            
            if bg_type == 'solid':
                bg_color = random.choice(self.background_colors)
                background = self.create_solid_background(bg_color)
            elif bg_type == 'gradient':
                colors = random.choice(self.gradient_colors)
                direction = random.choice(['vertical', 'horizontal'])
                background = self.create_gradient_background(colors[0], colors[1], direction)
            elif bg_type == 'noise':
                base_color = random.choice(self.background_colors)
                background = self.create_noise_background(base_color)
            else:  # crypto
                crypto_color = random.choice(self.crypto_colors)
                background = self.create_solid_background(crypto_color)
            
            # Apply random effect to logo
            if random.random() < 0.3:  # 30% chance of effect
                effect = random.choice(['blur', 'sharpen', 'brightness_up', 'brightness_down', 'contrast_up', 'contrast_down'])
                sized_logo = self.apply_logo_effects(sized_logo, effect)
            
            # Position logo
            if i < 5:
                # First few variations use center position
                position = 'center'
            else:
                position = random.choice(['center', 'center', 'center', 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'random'])
            
            # Create final variation
            final_image = self.position_logo_on_background(background, sized_logo, position)
            
            # Save variation
            final_image.save(variation_path)
            variations.append(str(variation_path))
            
            if (i + 1) % 5 == 0:
                print(f"   ✅ Generated {i + 1}/{count} variations")
        
        print(f"✅ All variations saved to: {output_path}")
        return variations

def main():
    parser = argparse.ArgumentParser(description="Generate logo training variations")
    parser.add_argument("--input", "-i", required=True, help="Input logo file path")
    parser.add_argument("--output-dir", "-o", required=True, help="Output directory")
    parser.add_argument("--count", "-c", type=int, default=25, help="Number of variations to generate")
    parser.add_argument("--size", "-s", default="512x512", help="Output size (e.g., 512x512)")
    
    args = parser.parse_args()
    
    # Parse size
    if 'x' in args.size:
        width, height = map(int, args.size.split('x'))
        output_size = (width, height)
    else:
        output_size = (512, 512)
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        return 1
    
    try:
        # Create generator
        generator = LogoVariationGenerator(output_size=output_size)
        
        # Generate variations
        variations = generator.generate_variations(
            logo_path=args.input,
            output_dir=args.output_dir,
            count=args.count
        )
        
        print(f"\n🎉 Success! Generated {len(variations)} logo variations")
        print(f"📁 Output directory: {args.output_dir}")
        
        # Show next steps
        print(f"\n📋 Next Steps:")
        print(f"1. Review generated variations in: {args.output_dir}")
        print(f"2. Add more manual variations if needed")
        print(f"3. Validate: python scripts/validate_training_data.py")
        print(f"4. Train LoRA: python scripts/train_lora_simple.py --logo-name {Path(args.output_dir).name}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating variations: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())