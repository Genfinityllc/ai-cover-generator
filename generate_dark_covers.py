#!/usr/bin/env python3
"""
Generate Dark Style Article Covers - Working MPS Configuration
Based on your uploaded Dark aesthetic references
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os

def generate_dark_article_covers():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"🖥️  Using device: {device}")
    
    # Load pipeline with working MPS configuration
    print("🔄 Loading Stable Diffusion XL for Dark style covers...")
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
    
    print("✅ Pipeline ready for Dark style generation")
    
    # Dark style prompts based on your uploaded references
    dark_prompts = [
        "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic, depth of field, cinematic lighting",
        
        "futuristic dark interface design, glowing circuit patterns, digital data streams, cyberpunk atmosphere with purple and blue neon accents, 3D geometric elements, tech industry professional background",
        
        "dark sci-fi technology background, holographic displays, neon grid patterns, blockchain visualization, digital technology theme, professional article cover aesthetic, atmospheric lighting",
        
        "cyberpunk data visualization, dark background with cyan highlights, 3D geometric tech elements, holographic interface, modern technology design, professional cover background",
        
        "dark professional technology scene, digital holographic elements, neon blue lighting, data streams, cyberpunk aesthetic, tech cover design, atmospheric depth"
    ]
    
    os.makedirs("dark_article_covers", exist_ok=True)
    
    for i, prompt in enumerate(dark_prompts, 1):
        print(f"\n🎨 Generating Dark cover {i}/5...")
        print(f"📝 Prompt: {prompt[:60]}...")
        
        try:
            # Generate at article cover resolution
            image = pipeline(
                prompt=prompt,
                negative_prompt="text, letters, words, watermarks, signatures, logos, low quality, blurry, amateur, ugly",
                width=1792,   # Divisible by 8 for SDXL
                height=896,   # Half of width for cover ratio
                num_inference_steps=25,  # Good quality but reasonable time
                guidance_scale=7.5,      # Standard guidance
                num_images_per_prompt=1,
                generator=torch.Generator(device=device).manual_seed(42 + i)  # Varied seeds
            ).images[0]
            
            filename = f"dark_article_covers/dark_cover_{i}.png"
            image.save(filename)
            print(f"✅ Generated: {filename}")
            
        except Exception as e:
            print(f"❌ Cover {i} failed: {str(e)}")
            # Try smaller resolution as fallback
            try:
                print(f"🔄 Retrying cover {i} at 1024x512...")
                image = pipeline(
                    prompt=prompt,
                    negative_prompt="text, letters, words, watermarks, signatures, low quality",
                    width=1024,
                    height=512,
                    num_inference_steps=20,
                    guidance_scale=7.5,
                    generator=torch.Generator(device=device).manual_seed(42 + i)
                ).images[0]
                
                filename = f"dark_article_covers/dark_cover_{i}_1024.png"
                image.save(filename)
                print(f"✅ Fallback generated: {filename}")
                
            except Exception as e2:
                print(f"❌ Fallback also failed: {str(e2)}")
    
    print("\n🎉 Dark style article covers complete!")
    print("📁 Check dark_article_covers/ directory for results")

if __name__ == "__main__":
    generate_dark_article_covers()