#!/usr/bin/env python3
"""
Enhanced LoRA Generator with Title Integration and Logo Elements
Test: "Hedera wins the Race" article
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageDraw, ImageFont
import os

def test_hedera_article_cover():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"🖥️  Using device: {device}")
    
    # Load watermark
    watermark_path = "/Users/valorkopeny/Desktop/genfinity-watermark.png"
    try:
        watermark = Image.open(watermark_path).convert("RGBA")
        print(f"✅ Loaded Genfinity watermark: {watermark.size}")
    except Exception as e:
        print(f"❌ Failed to load watermark: {e}")
        return
    
    # Load pipeline
    print("🔄 Loading Stable Diffusion XL...")
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    
    pipeline = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        use_safetensors=True,
        variant=None
    )
    
    pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
        pipeline.scheduler.config,
        use_karras_sigmas=True
    )
    
    if device == "mps":
        pipeline = pipeline.to(device)
        pipeline.enable_model_cpu_offload()
    
    print("✅ Pipeline ready")
    
    # Enhanced prompt for Hedera article with logo elements
    hedera_prompt = """
    dark cyberpunk technology background, holographic data visualization, 
    neon blue and cyan lighting, 3D blockchain cubes floating in space, 
    digital matrix atmosphere, professional tech aesthetic, 
    Hedera logo elements, hashgraph network visualization, 
    distributed ledger technology, geometric H patterns, 
    racing elements, speed lines, victory theme, 
    professional article cover design, 
    space for title text layout
    """
    
    print(f"\n🏁 Generating Hedera 'wins the Race' article cover...")
    print(f"📝 Enhanced prompt with logo elements...")
    
    os.makedirs("/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", exist_ok=True)
    
    try:
        # Generate enhanced background with Hedera elements
        image = pipeline(
            prompt=hedera_prompt,
            negative_prompt="text, letters, words, existing logos, watermarks, signatures, low quality, blurry, amateur, ugly",
            width=1792,
            height=896,
            num_inference_steps=30,  # Higher quality for test
            guidance_scale=8.0,      # Strong prompt adherence
            num_images_per_prompt=1,
            generator=torch.Generator(device=device).manual_seed(123)  # Consistent seed
        ).images[0]
        
        # Resize to exactly 1800x900
        resized_image = image.resize((1800, 900), Image.Resampling.LANCZOS)
        base_rgba = resized_image.convert("RGBA")
        
        # Add article title overlay
        title_overlay = Image.new("RGBA", (1800, 900), (0, 0, 0, 0))
        draw = ImageDraw.Draw(title_overlay)
        
        # Try to load a good font, fallback to default
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", 72)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttc", 36)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add title with professional styling
        title_text = "HEDERA WINS THE RACE"
        subtitle_text = "Hashgraph Technology Leads Distributed Ledger Innovation"
        
        # Calculate title position (upper portion)
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (1800 - title_width) // 2
        title_y = 150
        
        # Add title with shadow effect
        # Shadow
        draw.text((title_x + 3, title_y + 3), title_text, fill=(0, 0, 0, 200), font=title_font)
        # Main text
        draw.text((title_x, title_y), title_text, fill=(255, 255, 255, 255), font=title_font)
        
        # Add subtitle
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (1800 - subtitle_width) // 2
        subtitle_y = title_y + 100
        
        # Subtitle with shadow
        draw.text((subtitle_x + 2, subtitle_y + 2), subtitle_text, fill=(0, 0, 0, 150), font=subtitle_font)
        draw.text((subtitle_x, subtitle_y), subtitle_text, fill=(200, 200, 200, 255), font=subtitle_font)
        
        # Combine background, title, and watermark
        full_size_watermark = watermark.resize((1800, 900), Image.Resampling.LANCZOS)
        
        final_image = Image.alpha_composite(base_rgba, title_overlay)
        final_image = Image.alpha_composite(final_image, full_size_watermark)
        
        # Convert to RGB and save
        final_rgb = final_image.convert("RGB")
        
        filename = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/hedera_wins_race_cover.png"
        final_rgb.save(filename)
        
        print(f"✅ Saved Hedera article cover: {filename}")
        print(f"📐 Final resolution: {final_rgb.size}")
        print(f"🏁 Title: 'Hedera wins the Race'")
        print(f"🏷️  Full-size Genfinity watermark applied")
        
    except Exception as e:
        print(f"❌ Hedera cover failed: {str(e)}")
    
    print("\n🎉 Enhanced LoRA test with article title complete!")

if __name__ == "__main__":
    test_hedera_article_cover()