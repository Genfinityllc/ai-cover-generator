#!/usr/bin/env python3
"""
Simple Cover Generator - Lightweight version for testing
Generates text-based covers without ML dependencies
"""

import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import openai
import json

class SimpleCoverGenerator:
    def __init__(self):
        self.output_dir = Path("style_outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Client color schemes
        self.client_colors = {
            "hedera": {
                "bg": (138, 43, 226),  # Purple
                "text": (255, 255, 255),
                "accent": (75, 0, 130)
            },
            "algorand": {
                "bg": (0, 120, 140),  # Teal
                "text": (255, 255, 255),
                "accent": (0, 85, 100)
            },
            "constellation": {
                "bg": (72, 61, 139),  # Dark slate blue
                "text": (255, 255, 255),
                "accent": (106, 90, 205)
            },
            "bitcoin": {
                "bg": (255, 165, 0),  # Orange
                "text": (0, 0, 0),
                "accent": (255, 140, 0)
            },
            "generic": {
                "bg": (52, 73, 94),  # Dark blue-gray
                "text": (255, 255, 255),
                "accent": (41, 128, 185)
            }
        }
    
    def generate_ai_enhanced_prompt(self, article_content, client):
        """Generate AI-enhanced prompt using OpenAI"""
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠️ No OpenAI API key found, using default prompt")
            return f"Professional {client} cryptocurrency news cover, modern design"
        
        try:
            openai.api_key = os.getenv('OPENAI_API_KEY')
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Create a brief visual description for a crypto news cover."},
                    {"role": "user", "content": f"Create a visual description for a {client} crypto news cover about: {article_content[:500]}"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            prompt = response.choices[0].message.content.strip()
            print(f"🤖 AI-enhanced description: {prompt}")
            return prompt
            
        except Exception as e:
            print(f"⚠️ OpenAI API failed: {e}")
            return f"Professional {client} cryptocurrency news cover, modern design"
    
    def create_gradient_background(self, width, height, color1, color2):
        """Create a gradient background"""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        for i in range(height):
            # Linear gradient from top to bottom
            ratio = i / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        return img
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def generate_cover(self, title, subtitle=None, client="generic", article_file=None):
        """Generate a simple cover image"""
        
        print(f"🎨 Generating simple cover for {client}: {title}")
        
        # Read article content if provided
        article_content = ""
        if article_file and os.path.exists(article_file):
            with open(article_file, 'r', encoding='utf-8') as f:
                article_content = f.read()
            print(f"📖 Read article content ({len(article_content)} chars)")
        
        # Get AI enhancement if possible
        ai_description = self.generate_ai_enhanced_prompt(article_content, client)
        
        # Image dimensions
        width, height = 1800, 900
        
        # Get client colors
        colors = self.client_colors.get(client, self.client_colors["generic"])
        
        # Create gradient background
        bg_color1 = colors["bg"]
        bg_color2 = colors["accent"]
        img = self.create_gradient_background(width, height, bg_color1, bg_color2)
        
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 72)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            meta_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            meta_font = ImageFont.load_default()
        
        # Draw title (wrapped)
        title_lines = self.wrap_text(title, title_font, width - 200)
        title_y = height // 3
        
        for i, line in enumerate(title_lines):
            bbox = title_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = title_y + i * 80
            
            # Draw shadow
            draw.text((x+3, y+3), line, font=title_font, fill=(0, 0, 0, 128))
            # Draw text
            draw.text((x, y), line, font=title_font, fill=colors["text"])
        
        # Draw subtitle if provided
        if subtitle:
            subtitle_y = title_y + len(title_lines) * 80 + 40
            bbox = subtitle_font.getbbox(subtitle)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            # Draw shadow
            draw.text((x+2, subtitle_y+2), subtitle, font=subtitle_font, fill=(0, 0, 0, 128))
            # Draw text
            draw.text((x, subtitle_y), subtitle, font=subtitle_font, fill=colors["text"])
        
        # Draw client branding
        client_text = f"{client.upper()} NEWS"
        bbox = meta_font.getbbox(client_text)
        text_width = bbox[2] - bbox[0]
        x = width - text_width - 50
        y = height - 80
        
        draw.text((x, y), client_text, font=meta_font, fill=colors["text"])
        
        # Draw AI enhancement indicator
        if ai_description:
            ai_text = "🤖 AI Enhanced"
            draw.text((50, height - 80), ai_text, font=meta_font, fill=colors["text"])
        
        # Save the image
        output_file = self.output_dir / f"boxed_cover_{client}.png"
        img.save(output_file, "PNG", quality=95)
        
        print(f"✅ Cover saved: {output_file}")
        return str(output_file)

def main():
    parser = argparse.ArgumentParser(description="Simple Cover Generator")
    parser.add_argument("--title", required=True, help="Article title")
    parser.add_argument("--subtitle", help="Article subtitle")
    parser.add_argument("--client", default="generic", help="Client ID")
    parser.add_argument("--article", help="Article file path")
    
    args = parser.parse_args()
    
    generator = SimpleCoverGenerator()
    output_path = generator.generate_cover(
        title=args.title,
        subtitle=args.subtitle,
        client=args.client,
        article_file=args.article
    )
    
    print(f"🎯 Generated: {output_path}")

if __name__ == "__main__":
    main()