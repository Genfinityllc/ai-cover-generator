#!/usr/bin/env python3
"""
Correct Overlay Implementation - Full-size centered Genfinity watermark
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os

def generate_correct_overlay_covers():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"🖥️  Using device: {device}")
    
    # Load watermark at full size
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
    
    # Test prompts
    test_prompts = [
        "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic",
        
        "futuristic dark interface design, glowing circuit patterns, digital data streams, cyberpunk atmosphere with purple and blue neon accents, 3D geometric elements, tech industry professional background"
    ]
    
    os.makedirs("/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs", exist_ok=True)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🎨 Generating correct overlay cover {i}/2...")
        print(f"📝 Prompt: {prompt[:60]}...")
        
        try:
            # Generate base image
            image = pipeline(
                prompt=prompt,
                negative_prompt="text, letters, words, watermarks, signatures, logos, low quality, blurry, amateur, ugly",
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
            
            # Resize watermark to exact same size (1800x900) to match background
            full_size_watermark = watermark.resize((1800, 900), Image.Resampling.LANCZOS)
            
            # Center the watermark overlay (since it's same size, just composite)
            final_image = Image.alpha_composite(base_rgba, full_size_watermark)
            
            # Convert to RGB and save
            final_rgb = final_image.convert("RGB")
            
            filename = f"/Users/valorkopeny/crypto-news-curator-backend/ai-cover-generator/style_outputs/correct_overlay_test_{i}.png"
            final_rgb.save(filename)
            
            print(f"✅ Saved correct overlay: {filename}")
            print(f"📐 Final resolution: {final_rgb.size}")
            print(f"🏷️  Watermark: Full-size (1800x900) centered overlay")
            
        except Exception as e:
            print(f"❌ Cover {i} failed: {str(e)}")
    
    print("\n🎉 Correct overlay covers complete!")
    print("📁 Files saved to style_outputs/ directory")
    print("🏷️  Watermark now properly overlaid at full-size and centered")

if __name__ == "__main__":
    generate_correct_overlay_covers()