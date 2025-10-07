#!/usr/bin/env python3
"""
Generate Dark Style Article Covers with Genfinity Watermark
Resolution: 1800x900 pixels
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image, ImageEnhance
import os

def generate_watermarked_covers():
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
    
    # Load pipeline with working MPS configuration
    print("🔄 Loading Stable Diffusion XL...")
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    
    pipeline = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float32,  # Working config for MPS
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
    
    # Test prompts for Dark style covers
    test_prompts = [
        "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic, avoid center and bottom right areas",
        
        "futuristic dark interface design, glowing circuit patterns, digital data streams, cyberpunk atmosphere with purple and blue neon accents, 3D geometric elements, tech industry professional background, clear space bottom right"
    ]
    
    os.makedirs("/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", exist_ok=True)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🎨 Generating watermarked cover {i}/2...")
        print(f"📝 Prompt: {prompt[:60]}...")
        
        try:
            # Generate at exact resolution: 1800x900
            image = pipeline(
                prompt=prompt,
                negative_prompt="text, letters, words, watermarks, signatures, logos, low quality, blurry, amateur, ugly, objects in bottom right corner",
                width=1800,   # Exact requirement
                height=900,   # Exact requirement  
                num_inference_steps=25,
                guidance_scale=7.5,
                num_images_per_prompt=1,
                generator=torch.Generator(device=device).manual_seed(42 + i)
            ).images[0]
            
            print(f"✅ Generated base image: {image.size}")
            
            # Apply watermark overlay
            # Convert base image to RGBA for compositing
            base_rgba = image.convert("RGBA")
            
            # Resize watermark to appropriate size (about 10% of width)
            watermark_width = int(1800 * 0.1)  # 180px width
            watermark_ratio = watermark.size[1] / watermark.size[0]
            watermark_height = int(watermark_width * watermark_ratio)
            
            resized_watermark = watermark.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
            
            # Position watermark in bottom right with padding
            padding = 30
            x_pos = 1800 - watermark_width - padding
            y_pos = 900 - watermark_height - padding
            
            # Create final composite
            final_image = Image.new("RGBA", (1800, 900), (0, 0, 0, 0))
            final_image.paste(base_rgba, (0, 0))
            final_image.paste(resized_watermark, (x_pos, y_pos), resized_watermark)
            
            # Convert back to RGB and save
            final_rgb = final_image.convert("RGB")
            
            filename = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/watermarked_dark_cover_{i}.png"
            final_rgb.save(filename)
            
            print(f"✅ Saved watermarked cover: {filename}")
            print(f"📐 Final resolution: {final_rgb.size}")
            print(f"🏷️  Watermark position: ({x_pos}, {y_pos})")
            
        except Exception as e:
            print(f"❌ Cover {i} failed: {str(e)}")
            # Try fallback without watermark
            try:
                print(f"🔄 Fallback: generating without watermark...")
                fallback_filename = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/fallback_dark_cover_{i}.png"
                image.save(fallback_filename)
                print(f"✅ Fallback saved: {fallback_filename}")
            except Exception as e2:
                print(f"❌ Fallback also failed: {str(e2)}")
    
    print("\n🎉 Watermarked test covers complete!")
    print("📁 Check style_outputs/ directory for results")

if __name__ == "__main__":
    generate_watermarked_covers()