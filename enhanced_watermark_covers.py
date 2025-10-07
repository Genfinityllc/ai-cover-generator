#!/usr/bin/env python3
"""
Enhanced Watermark Version - More Visible Genfinity Branding
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageEnhance, ImageDraw
import os

def generate_enhanced_watermark_covers():
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
    
    # Enhanced test prompts with better watermark positioning
    test_prompts = [
        "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic, darker bottom right corner",
        
        "futuristic dark interface design, glowing circuit patterns, digital data streams, cyberpunk atmosphere with purple and blue neon accents, 3D geometric elements, tech industry professional background, solid dark area bottom right"
    ]
    
    os.makedirs("/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", exist_ok=True)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🎨 Generating enhanced watermarked cover {i}/2...")
        print(f"📝 Prompt: {prompt[:60]}...")
        
        try:
            # Generate base image
            image = pipeline(
                prompt=prompt,
                negative_prompt="text, letters, words, watermarks, signatures, logos, low quality, blurry, amateur, ugly, bright areas in bottom right corner, light areas in bottom right",
                width=1792,
                height=896,
                num_inference_steps=25,
                guidance_scale=7.5,
                num_images_per_prompt=1,
                generator=torch.Generator(device=device).manual_seed(42 + i)
            ).images[0]
            
            # Resize to exactly 1800x900
            resized_image = image.resize((1800, 900), Image.Resampling.LANCZOS)
            base_rgba = resized_image.convert("RGBA")
            
            # Enhanced watermark positioning and visibility
            watermark_width = int(1800 * 0.1)  # 180px width
            watermark_ratio = watermark.size[1] / watermark.size[0]
            watermark_height = int(watermark_width * watermark_ratio)
            
            resized_watermark = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
            
            # Position with more padding for visibility
            padding = 40
            x_pos = 1800 - watermark_width - padding
            y_pos = 900 - watermark_height - padding
            
            # Create subtle dark background for watermark visibility
            overlay = Image.new("RGBA", (1800, 900), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Draw subtle dark rectangle behind watermark area
            bg_padding = 15
            bg_x1 = x_pos - bg_padding
            bg_y1 = y_pos - bg_padding
            bg_x2 = x_pos + watermark_width + bg_padding
            bg_y2 = y_pos + watermark_height + bg_padding
            
            overlay_draw.rounded_rectangle(
                [bg_x1, bg_y1, bg_x2, bg_y2],
                radius=8,
                fill=(0, 0, 0, 80)  # Semi-transparent dark background
            )
            
            # Composite everything
            final_image = Image.new("RGBA", (1800, 900), (0, 0, 0, 0))
            final_image.paste(base_rgba, (0, 0))
            final_image = Image.alpha_composite(final_image, overlay)
            final_image.paste(resized_watermark, (x_pos, y_pos), resized_watermark)
            
            # Convert to RGB and save
            final_rgb = final_image.convert("RGB")
            
            filename = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/enhanced_watermark_test_{i}.png"
            final_rgb.save(filename)
            
            print(f"✅ Saved enhanced cover: {filename}")
            print(f"📐 Final resolution: {final_rgb.size}")
            print(f"🏷️  Watermark: {watermark_width}x{watermark_height} at ({x_pos}, {y_pos})")
            print(f"🎨 Background: ({bg_x1}, {bg_y1}) to ({bg_x2}, {bg_y2})")
            
        except Exception as e:
            print(f"❌ Cover {i} failed: {str(e)}")
    
    print("\n🎉 Enhanced watermarked covers complete!")
    print("📁 Files saved to style_outputs/ directory")
    print("🏷️  Watermarks now have subtle dark backgrounds for better visibility")

if __name__ == "__main__":
    generate_enhanced_watermark_covers()