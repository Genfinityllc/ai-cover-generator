#!/usr/bin/env python3
"""
Generate remaining dark style samples
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os

def generate_remaining_samples():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"🖥️  Using device: {device}")
    
    # Load pipeline
    print("🔄 Loading Stable Diffusion XL...")
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    
    pipeline = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "mps" else torch.float32,
        use_safetensors=True
    )
    
    pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
        pipeline.scheduler.config
    )
    
    if device == "mps":
        pipeline = pipeline.to(device)
        pipeline.enable_attention_slicing()
    
    print("✅ Pipeline ready")
    
    # Dark style prompts (continuing from sample 3)
    remaining_prompts = [
        "dark sci-fi technology background, holographic displays, neon grid patterns, blockchain visualization, digital technology theme, professional article cover aesthetic, atmospheric lighting",
        "cyberpunk data visualization, dark background with cyan highlights, 3D geometric tech elements, holographic interface, modern technology design, professional cover background",
        "dark professional technology scene, digital holographic elements, neon blue lighting, data streams, cyberpunk aesthetic, tech cover design, atmospheric depth"
    ]
    
    os.makedirs("style_outputs", exist_ok=True)
    
    for i, prompt in enumerate(remaining_prompts, 3):  # Start from sample 3
        print(f"\n📝 Sample {i+1}: {prompt[:60]}...")
        
        try:
            image = pipeline(
                prompt=prompt,
                negative_prompt="text, letters, words, watermarks, signatures, low quality, blurry, amateur, ugly",
                width=1792,  # Divisible by 8
                height=896,  # Divisible by 8
                num_inference_steps=35,
                guidance_scale=8.0,
                num_images_per_prompt=1
            ).images[0]
            
            filename = f"style_outputs/dark_sample_{i+1}.png"
            image.save(filename)
            print(f"✅ Generated: {filename}")
            
        except Exception as e:
            print(f"❌ Sample {i+1} failed: {str(e)}")
    
    print("\n🎉 Dark style samples complete!")

if __name__ == "__main__":
    generate_remaining_samples()