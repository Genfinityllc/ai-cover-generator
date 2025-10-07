"""
Lightweight AI Cover Generator Fallback
Works without heavy ML dependencies for immediate testing
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Optional
import uvicorn

app = FastAPI(title="AI Cover Generator - Lightweight")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Ultra-simple health check"""
    return {"status": "healthy", "version": "1.0.0-lightweight"}

@app.post("/api/generate/cover")
async def generate_cover(
    title: str,
    subtitle: Optional[str] = None,
    style: str = "Dark",
    width: int = 1800,
    height: int = 900
):
    """Generate cover image using your style preferences"""
    try:
        # Create background based on your style references
        image = create_style_background(style, width, height)
        
        # Add text with layout awareness
        image = add_text_overlay(image, title, subtitle)
        
        # Convert to base64 for response
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        return {
            "success": True,
            "image_url": f"data:image/png;base64,{img_str}",
            "style": style,
            "message": "Cover generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

def create_style_background(style: str, width: int, height: int) -> Image.Image:
    """Create background matching your aesthetic preferences"""
    
    style_configs = {
        "Dark": {
            "gradient": [(10, 15, 35), (30, 20, 60), (15, 40, 80)],
            "accent_color": (0, 200, 255),  # Cyan
            "secondary_color": (200, 50, 200)  # Magenta
        },
        "Colorful": {
            "gradient": [(60, 20, 100), (120, 40, 160), (80, 60, 180)],
            "accent_color": (255, 100, 200),  # Pink
            "secondary_color": (100, 150, 255)  # Blue
        },
        "Light": {
            "gradient": [(240, 245, 250), (220, 230, 245), (200, 220, 240)],
            "accent_color": (100, 150, 200),  # Light blue
            "secondary_color": (150, 100, 200)  # Light purple
        }
    }
    
    config = style_configs.get(style, style_configs["Dark"])
    
    # Create gradient background
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    
    # Multi-point gradient
    for i in range(height):
        ratio = i / height
        if ratio < 0.3:
            # Top gradient
            t = ratio / 0.3
            r = int(config["gradient"][0][0] * (1-t) + config["gradient"][1][0] * t)
            g = int(config["gradient"][0][1] * (1-t) + config["gradient"][1][1] * t)
            b = int(config["gradient"][0][2] * (1-t) + config["gradient"][1][2] * t)
        else:
            # Bottom gradient
            t = (ratio - 0.3) / 0.7
            r = int(config["gradient"][1][0] * (1-t) + config["gradient"][2][0] * t)
            g = int(config["gradient"][1][1] * (1-t) + config["gradient"][2][1] * t)
            b = int(config["gradient"][1][2] * (1-t) + config["gradient"][2][2] * t)
            
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # Add subtle geometric elements (respecting layout zones)
    add_geometric_elements(draw, width, height, config, style)
    
    return image

def add_geometric_elements(draw, width, height, config, style):
    """Add style-appropriate geometric elements"""
    
    if style == "Dark":
        # Tech grid lines and cubes (bottom half only)
        for i in range(3):
            y = height * 0.6 + i * 40
            if y < height * 0.75:  # Avoid watermark zone
                draw.line([(0, y), (width, y)], fill=config["accent_color"], width=1)
        
        # Corner accents
        for i in range(5):
            x = i * 20
            draw.line([(x, height-20), (x, height)], fill=config["secondary_color"], width=2)
    
    elif style == "Colorful":
        # Cosmic orbs (middle area only)
        import random
        for _ in range(8):
            x = random.randint(width//4, 3*width//4)
            y = random.randint(int(height*0.5), int(height*0.7))
            radius = random.randint(20, 60)
            # Semi-transparent circles
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                        outline=config["accent_color"], width=2)
    
    elif style == "Light":
        # Clean minimal lines
        for i in range(3):
            y = height * 0.8 + i * 10
            draw.line([(width*0.1, y), (width*0.9, y)], 
                     fill=config["accent_color"], width=1)

def add_text_overlay(image: Image.Image, title: str, subtitle: Optional[str]) -> Image.Image:
    """Add text respecting layout zones"""
    
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # Load fonts with fallbacks
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size=int(height * 0.08))
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size=int(height * 0.04))
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Title placement (top 30% area)
    title_x = int(width * 0.1)
    title_y = int(height * 0.15)
    
    # Add shadow for readability
    shadow_offset = 4
    draw.text((title_x + shadow_offset, title_y + shadow_offset), title, 
             font=title_font, fill=(0, 0, 0, 100))
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255))
    
    # Subtitle if provided
    if subtitle:
        subtitle_x = int(width * 0.15)
        subtitle_y = int(height * 0.35)
        
        draw.text((subtitle_x + shadow_offset//2, subtitle_y + shadow_offset//2), subtitle,
                 font=subtitle_font, fill=(0, 0, 0, 80))
        draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(200, 220, 255))
    
    # Add Genfinity watermark area (center bottom)
    watermark_text = "GENFINITY"
    watermark_font = subtitle_font
    watermark_x = int(width * 0.4)
    watermark_y = int(height * 0.85)
    
    draw.text((watermark_x + 2, watermark_y + 2), watermark_text,
             font=watermark_font, fill=(0, 0, 0, 60))
    draw.text((watermark_x, watermark_y), watermark_text, 
             font=watermark_font, fill=(150, 150, 150))
    
    return image

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)