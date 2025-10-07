#!/usr/bin/env python3
"""
Fixed Style Generator - Addresses MPS black image issue
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os

def generate_working_samples():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"🖥️  Using device: {device}")
    
    # Load pipeline with MPS fixes
    print("🔄 Loading Stable Diffusion XL with MPS optimizations...")
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    
    pipeline = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float32,  # Use float32 instead of float16 for MPS
        use_safetensors=True,
        variant=None  # Don't use fp16 variant
    )
    
    # Use different scheduler
    pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
        pipeline.scheduler.config,
        use_karras_sigmas=True
    )
    
    if device == "mps":
        pipeline = pipeline.to(device)
        # Disable attention slicing which can cause issues
        # pipeline.enable_attention_slicing()
        
        # Enable memory efficient attention
        pipeline.enable_model_cpu_offload()
    
    print("✅ Pipeline ready with MPS fixes")
    
    # Simpler, more reliable prompts
    test_prompts = [
        "cyberpunk neon lights, dark background, blue and purple glow, technology theme",
        "holographic display, futuristic interface, dark space, glowing elements",
        "digital matrix, green code streams, black background, sci-fi atmosphere"
    ]
    
    os.makedirs("fixed_outputs", exist_ok=True)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
        
        try:
            # Generate with conservative settings
            image = pipeline(
                prompt=prompt,
                negative_prompt="text, letters, words, low quality",
                width=512,   # Start smaller to test
                height=512,
                num_inference_steps=20,  # Fewer steps
                guidance_scale=7.5,      # Standard guidance
                num_images_per_prompt=1,
                generator=torch.Generator(device=device).manual_seed(42)  # Fixed seed
            ).images[0]
            
            filename = f"fixed_outputs/test_{i}.png"
            image.save(filename)
            print(f"✅ Generated: {filename}")
            
            # Check if image is actually generated
            img_array = torch.tensor(list(image.getdata()))
            if img_array.std() < 0.01:  # Almost all same values = likely black
                print(f"⚠️  Warning: Image {i} appears to be blank/black")
            else:
                print(f"✅ Image {i} has content (std: {img_array.std():.3f})")
            
        except Exception as e:
            print(f"❌ Test {i} failed: {str(e)}")
    
    print("\n🧪 MPS compatibility test complete!")

if __name__ == "__main__":
    generate_working_samples()