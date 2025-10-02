#!/usr/bin/env python3
"""
Sample Image Collection Helper
Creates sample training images from existing logos/sources
"""

import os
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

def create_sample_bitcoin_images():
    """Create sample Bitcoin training images"""
    print("🪙 Creating sample Bitcoin images...")
    
    bitcoin_dir = Path("training_data/bitcoin")
    bitcoin_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample Bitcoin logo URLs (public domain/CC)
    sample_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/256px-Bitcoin.svg.png",
        # Add more URLs as needed
    ]
    
    # Create variations programmatically
    colors = [
        (255, 255, 255),  # White
        (0, 0, 0),        # Black  
        (247, 147, 26),   # Bitcoin Orange
        (100, 100, 100),  # Gray
    ]
    
    # Create simple Bitcoin-style images
    for i, bg_color in enumerate(colors):
        create_logo_variation(
            bitcoin_dir / f"bitcoin_sample_{i+1}.png",
            "₿", bg_color, (247, 147, 26) if bg_color != (247, 147, 26) else (255, 255, 255)
        )
    
    # Create text versions
    text_variations = ["BITCOIN", "BTC", "₿"]
    for i, text in enumerate(text_variations):
        create_text_logo(
            bitcoin_dir / f"bitcoin_text_{i+1}.png",
            text, (247, 147, 26), (255, 255, 255)
        )
    
    print(f"   ✅ Created sample images in {bitcoin_dir}")

def create_sample_ethereum_images():
    """Create sample Ethereum training images"""
    print("💎 Creating sample Ethereum images...")
    
    ethereum_dir = Path("training_data/ethereum")
    ethereum_dir.mkdir(parents=True, exist_ok=True)
    
    colors = [
        (255, 255, 255),  # White
        (0, 0, 0),        # Black
        (98, 126, 234),   # Ethereum Blue
        (100, 100, 100),  # Gray
    ]
    
    # Create diamond-like shapes for Ethereum
    for i, bg_color in enumerate(colors):
        create_ethereum_variation(
            ethereum_dir / f"ethereum_sample_{i+1}.png",
            bg_color, (98, 126, 234) if bg_color != (98, 126, 234) else (255, 255, 255)
        )
    
    # Create text versions
    text_variations = ["ETHEREUM", "ETH", "Ξ"]
    for i, text in enumerate(text_variations):
        create_text_logo(
            ethereum_dir / f"ethereum_text_{i+1}.png",
            text, (98, 126, 234), (255, 255, 255)
        )
    
    print(f"   ✅ Created sample images in {ethereum_dir}")

def create_logo_variation(filepath: Path, symbol: str, bg_color: tuple, text_color: tuple):
    """Create a logo variation with symbol"""
    size = 512
    image = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(image)
    
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 200)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    bbox = draw.textbbox((0, 0), symbol, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), symbol, fill=text_color, font=font)
    
    image.save(filepath)

def create_ethereum_variation(filepath: Path, bg_color: tuple, logo_color: tuple):
    """Create Ethereum diamond shape"""
    size = 512
    image = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Create diamond shape (simplified Ethereum logo)
    center_x, center_y = size // 2, size // 2
    diamond_size = 150
    
    # Upper diamond
    points = [
        (center_x, center_y - diamond_size),           # Top
        (center_x - diamond_size//2, center_y - 30),   # Left
        (center_x, center_y),                          # Center
        (center_x + diamond_size//2, center_y - 30),   # Right
    ]
    draw.polygon(points, fill=logo_color)
    
    # Lower diamond
    points = [
        (center_x, center_y),                          # Center
        (center_x - diamond_size//2, center_y + 30),   # Left
        (center_x, center_y + diamond_size),           # Bottom
        (center_x + diamond_size//2, center_y + 30),   # Right
    ]
    draw.polygon(points, fill=tuple(max(0, c-50) for c in logo_color))
    
    image.save(filepath)

def create_text_logo(filepath: Path, text: str, text_color: tuple, bg_color: tuple):
    """Create text-based logo"""
    size = 512
    image = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=text_color, font=font)
    
    image.save(filepath)

def create_sample_generic_crypto():
    """Create generic crypto symbols"""
    print("🪙 Creating generic crypto samples...")
    
    crypto_dir = Path("training_data/crypto_general")
    crypto_dir.mkdir(parents=True, exist_ok=True)
    
    symbols = ["₿", "Ξ", "◊", "●", "▲"]
    colors = [(255, 255, 255), (0, 0, 0), (50, 150, 250), (250, 150, 50)]
    
    for i, symbol in enumerate(symbols):
        for j, bg_color in enumerate(colors):
            text_color = (0, 0, 0) if bg_color == (255, 255, 255) else (255, 255, 255)
            create_logo_variation(
                crypto_dir / f"crypto_symbol_{i}_{j}.png",
                symbol, bg_color, text_color
            )
    
    print(f"   ✅ Created sample images in {crypto_dir}")

def main():
    """Create sample training datasets"""
    print("🎨 Creating Sample Training Datasets")
    print("=" * 50)
    print("This will create basic sample images to test LoRA training.")
    print("For production, replace with high-quality official logos.")
    print()
    
    # Create sample datasets
    create_sample_bitcoin_images()
    create_sample_ethereum_images()
    create_sample_generic_crypto()
    
    print("\n✅ Sample datasets created!")
    print("\n📋 Next steps:")
    print("1. Replace sample images with real high-quality logos")
    print("2. Add 15-25 more images per logo directory")
    print("3. Validate: python scripts/validate_training_data.py")
    print("4. Train: python scripts/train_lora_simple.py --logo-name bitcoin")
    
    print("\n💡 Tips for better training data:")
    print("• Use official logo files from company press kits")
    print("• Include transparent backgrounds")
    print("• Vary image sizes and positions")
    print("• Add different lighting and backgrounds")
    
    return 0

if __name__ == "__main__":
    exit(main())