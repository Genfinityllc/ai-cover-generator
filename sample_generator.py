#!/usr/bin/env python3
"""
Sample LoRA Style Generator
Creates sample cover images based on your style preferences
"""
from PIL import Image, ImageDraw, ImageFont
import random
import os

def create_sample_cover(style: str, title: str, subtitle: str = None, save_path: str = None):
    """Generate a sample cover image based on your style preferences"""
    
    width, height = 1800, 900
    
    # Style configurations based on your references
    style_configs = {
        "Dark": {
            "gradient": [(10, 15, 35), (25, 35, 65), (15, 45, 85)],
            "accent": (0, 200, 255),     # Cyan
            "secondary": (200, 50, 200),  # Magenta
            "elements": "tech_grid"
        },
        "Colorful": {
            "gradient": [(60, 20, 100), (120, 40, 160), (80, 60, 180)],
            "accent": (255, 100, 200),   # Pink
            "secondary": (100, 150, 255), # Blue
            "elements": "cosmic_orbs"
        },
        "Light": {
            "gradient": [(240, 245, 250), (220, 230, 245), (200, 220, 240)],
            "accent": (100, 150, 200),   # Light blue
            "secondary": (150, 100, 200), # Light purple
            "elements": "minimal_lines"
        }
    }
    
    config = style_configs.get(style, style_configs["Dark"])
    
    print(f"🎨 Generating {style} style cover: '{title}'")
    
    # Create base image
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Create gradient background
    for i in range(height):
        ratio = i / height
        if ratio < 0.4:
            # Top gradient
            t = ratio / 0.4
            r = int(config["gradient"][0][0] * (1-t) + config["gradient"][1][0] * t)
            g = int(config["gradient"][0][1] * (1-t) + config["gradient"][1][1] * t)
            b = int(config["gradient"][0][2] * (1-t) + config["gradient"][1][2] * t)
        else:
            # Bottom gradient
            t = (ratio - 0.4) / 0.6
            r = int(config["gradient"][1][0] * (1-t) + config["gradient"][2][0] * t)
            g = int(config["gradient"][1][1] * (1-t) + config["gradient"][2][1] * t)
            b = int(config["gradient"][1][2] * (1-t) + config["gradient"][2][2] * t)
        
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # Add style-specific elements
    add_style_elements(draw, width, height, config, style)
    
    # Add text overlays
    add_text_overlay(draw, width, height, title, subtitle, style)
    
    # Add watermark zone
    add_watermark_zone(draw, width, height, config)
    
    # Save the image
    if not save_path:
        save_path = f"sample_{style.lower()}_{title.replace(' ', '_')[:20]}.png"
    
    image.save(save_path)
    print(f"✅ Sample saved to: {save_path}")
    
    return image, save_path

def add_style_elements(draw, width, height, config, style):
    """Add style-appropriate visual elements"""
    
    if style == "Dark":
        # Tech grid lines (avoiding text zones)
        grid_y_start = int(height * 0.5)  # Start below title area
        grid_y_end = int(height * 0.75)   # End before watermark
        
        # Horizontal tech lines
        for i in range(4):
            y = grid_y_start + i * 40
            if y < grid_y_end:
                alpha = 100 - i * 20  # Fade out
                draw.line([(50, y), (width-50, y)], fill=config["accent"] + (alpha,), width=2)
        
        # Corner tech elements
        for i in range(8):
            x = i * 25
            y = height - 30 + i * 2
            if x < width * 0.3:  # Left side only
                draw.line([(x, y), (x, height)], fill=config["secondary"], width=1)
        
        # Data cubes (middle area)
        for _ in range(6):
            x = random.randint(int(width*0.6), int(width*0.9))
            y = random.randint(int(height*0.5), int(height*0.7))
            size = random.randint(15, 30)
            draw.rectangle([x, y, x+size, y+size], outline=config["accent"], width=2)
    
    elif style == "Colorful":
        # Cosmic orbs (middle area only)
        for _ in range(12):
            x = random.randint(int(width*0.2), int(width*0.8))
            y = random.randint(int(height*0.45), int(height*0.75))
            radius = random.randint(20, 80)
            # Layered circles for depth
            for r in range(radius, radius//3, -10):
                alpha = int(150 * (r / radius))
                color = config["accent"] if r % 20 < 10 else config["secondary"]
                draw.ellipse([x-r, y-r, x+r, y+r], outline=color, width=2)
        
        # Light beams
        for _ in range(4):
            x1 = random.randint(0, width//2)
            y1 = random.randint(int(height*0.5), int(height*0.8))
            x2 = x1 + random.randint(200, 400)
            y2 = y1 + random.randint(-100, 100)
            draw.line([(x1, y1), (x2, y2)], fill=config["secondary"], width=3)
    
    elif style == "Light":
        # Clean minimal elements
        line_y = int(height * 0.82)
        draw.line([(width*0.1, line_y), (width*0.9, line_y)], fill=config["accent"], width=3)
        
        # Subtle geometric accents
        for i in range(5):
            x = width * 0.85 + i * 15
            y = height * 0.6 + i * 8
            draw.line([(x, y), (x, y + 20)], fill=config["secondary"], width=2)

def add_text_overlay(draw, width, height, title, subtitle, style):
    """Add title and subtitle with proper layout"""
    
    # Try to load system fonts, fallback to default
    try:
        if style == "Dark":
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial Black.ttf", size=int(height * 0.08))
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size=int(height * 0.04))
        else:
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size=int(height * 0.08))
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size=int(height * 0.04))
    except:
        # Fallback fonts
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Title placement (respecting layout zones)
    title_x = int(width * 0.1)
    title_y = int(height * 0.12)
    
    # Add shadow for readability
    shadow_offset = 6
    shadow_color = (0, 0, 0) if style != "Dark" else (0, 0, 0)
    text_color = (255, 255, 255) if style == "Dark" else (255, 255, 255)
    
    # Title shadow
    draw.text((title_x + shadow_offset, title_y + shadow_offset), title, 
             font=title_font, fill=shadow_color)
    # Title text
    draw.text((title_x, title_y), title, font=title_font, fill=text_color)
    
    # Subtitle if provided
    if subtitle:
        subtitle_x = int(width * 0.12)
        subtitle_y = int(height * 0.28)
        subtitle_color = (200, 220, 255) if style == "Dark" else (180, 180, 220)
        
        # Subtitle shadow
        draw.text((subtitle_x + shadow_offset//2, subtitle_y + shadow_offset//2), subtitle,
                 font=subtitle_font, fill=shadow_color)
        # Subtitle text
        draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=subtitle_color)

def add_watermark_zone(draw, width, height, config):
    """Add Genfinity watermark in designated zone"""
    
    # Watermark zone (center bottom)
    watermark_text = "GENFINITY"
    
    try:
        watermark_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size=int(height * 0.04))
    except:
        watermark_font = ImageFont.load_default()
    
    # Calculate centered position
    bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
    text_width = bbox[2] - bbox[0]
    
    watermark_x = (width - text_width) // 2
    watermark_y = int(height * 0.85)
    
    # Add subtle background for watermark
    bg_padding = 20
    draw.rectangle([
        watermark_x - bg_padding, 
        watermark_y - bg_padding//2,
        watermark_x + text_width + bg_padding,
        watermark_y + int(height * 0.05)
    ], fill=(0, 0, 0, 50))
    
    # Watermark text
    draw.text((watermark_x + 2, watermark_y + 2), watermark_text,
             font=watermark_font, fill=(0, 0, 0))  # Shadow
    draw.text((watermark_x, watermark_y), watermark_text,
             font=watermark_font, fill=(150, 150, 150))  # Main text

def main():
    """Generate sample covers for all three styles"""
    
    # Sample article titles
    samples = [
        {
            "title": "Bitcoin Reaches New All-Time High",
            "subtitle": "Breaking: BTC surpasses $150K amid institutional adoption",
            "style": "Dark"
        },
        {
            "title": "Scaling On-Chain AI Infrastructure", 
            "subtitle": "Revolutionary blockchain solutions for artificial intelligence",
            "style": "Colorful"
        },
        {
            "title": "DeFi Innovation Report 2025",
            "subtitle": "Comprehensive analysis of decentralized finance trends",
            "style": "Light"
        }
    ]
    
    print("🎨 Generating LoRA style samples based on your preferences...")
    print("=" * 60)
    
    generated_files = []
    
    for sample in samples:
        image, path = create_sample_cover(
            style=sample["style"],
            title=sample["title"],
            subtitle=sample["subtitle"]
        )
        generated_files.append(path)
        print()
    
    print("=" * 60)
    print("🎉 Sample generation complete!")
    print(f"📁 Generated {len(generated_files)} sample covers:")
    for file in generated_files:
        print(f"   • {file}")
    
    print("\n💡 These samples show:")
    print("   • Your Dark/Colorful/Light style aesthetics")
    print("   • Layout-aware design (clear zones for text/watermark)")
    print("   • Professional article cover format")
    print("   • Genfinity branding integration")
    
    return generated_files

if __name__ == "__main__":
    main()