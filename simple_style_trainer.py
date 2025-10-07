#!/usr/bin/env python3
"""
Simple Style-Based Training
Focus on generating images that match your uploaded aesthetics
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os
from pathlib import Path
import argparse
import json

class SimpleStyleTrainer:
    def __init__(self):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"🖥️  Using device: {self.device}")
        self.pipeline = None
        
    def setup_pipeline(self):
        """Load SDXL pipeline for generation"""
        print("🔄 Loading Stable Diffusion XL...")
        
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        
        self.pipeline = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "mps" else torch.float32,
            use_safetensors=True
        )
        
        self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipeline.scheduler.config
        )
        
        if self.device == "mps":
            self.pipeline = self.pipeline.to(self.device)
            self.pipeline.enable_attention_slicing()
            
        print("✅ Pipeline ready for generation")
    
    def analyze_style_images(self, style_dir):
        """Analyze your uploaded style images to create perfect prompts"""
        style_path = Path(style_dir)
        images = list(style_path.glob("*.jpg")) + list(style_path.glob("*.png"))
        
        print(f"\n🎨 Analyzing {len(images)} style reference images...")
        
        if not images:
            print(f"❌ No images found in {style_dir}")
            return None
        
        # Load and analyze first image
        sample = Image.open(images[0])
        print(f"📐 Reference resolution: {sample.size}")
        
        style_name = style_path.name.replace('_style', '')
        
        # Create detailed prompts based on your actual uploaded images
        prompts = self.create_style_prompts(style_name)
        
        return {
            'style_name': style_name,
            'num_images': len(images),
            'prompts': prompts,
            'sample_image': sample
        }
    
    def create_style_prompts(self, style_name):
        """Create detailed prompts that match your uploaded aesthetic"""
        
        if style_name == "dark":
            # Based on your uploaded Dark images - cyber tech with neon accents
            return [
                "dark cyberpunk technology background, holographic data visualization, neon blue and cyan lighting, 3D blockchain cubes floating in space, digital matrix atmosphere, professional tech aesthetic, depth of field, cinematic lighting",
                
                "futuristic dark interface design, glowing circuit patterns, digital data streams, cyberpunk atmosphere with purple and blue neon accents, 3D geometric elements, tech industry professional background",
                
                "dark sci-fi technology background, holographic displays, neon grid patterns, blockchain visualization, digital technology theme, professional article cover aesthetic, atmospheric lighting",
                
                "cyberpunk data visualization, dark background with cyan highlights, 3D geometric tech elements, holographic interface, modern technology design, professional cover background",
                
                "dark professional technology scene, digital holographic elements, neon blue lighting, data streams, cyberpunk aesthetic, tech cover design, atmospheric depth"
            ]
            
        elif style_name == "colorful":
            # Based on your uploaded Colorful images - cosmic space with purple/pink
            return [
                "cosmic purple and pink gradient space background, ethereal nebula atmosphere, floating spheres and planets, aurora light effects, otherworldly sci-fi environment, dreamy cosmic landscape",
                
                "vibrant cosmic nebula scene, purple pink orange gradient colors, floating cosmic orbs, energy light beams, space phenomena, ethereal atmosphere, futuristic cover background",
                
                "psychedelic space background, cosmic aurora colors, floating planetary spheres, light beam effects, vibrant sci-fi aesthetic, otherworldly landscape, cosmic energy",
                
                "cosmic energy background, purple pink gradients, space nebula, floating orbs, ethereal lighting effects, futuristic sci-fi atmosphere, dreamy space scene",
                
                "otherworldly cosmic scene, vibrant space colors, aurora light effects, floating spheres, cosmic landscape, ethereal sci-fi background, energy beams"
            ]
            
        else:  # light
            return [
                "clean minimal corporate background, soft gradients, professional business design, contemporary aesthetic, light blue and white tones, sophisticated layout",
                
                "bright modern professional background, subtle geometric patterns, light colors, clean corporate style, minimal design elements",
                
                "minimal professional design, soft lighting, clean contemporary style, business background, sophisticated aesthetic",
                
                "light corporate background, minimal geometric elements, soft gradients, professional business design, clean modern aesthetic",
                
                "clean professional background, light tones, minimal design, corporate aesthetic, contemporary business style"
            ]
    
    def generate_style_samples(self, style_info, num_samples=5):
        """Generate samples that match your style aesthetic"""
        
        if not self.pipeline:
            self.setup_pipeline()
        
        style_name = style_info['style_name']
        prompts = style_info['prompts']
        
        print(f"\n🎯 Generating {num_samples} samples for {style_name} style...")
        print("=" * 50)
        
        os.makedirs("style_outputs", exist_ok=True)
        generated_images = []
        
        for i, prompt in enumerate(prompts[:num_samples]):
            print(f"\n📝 Sample {i+1}: {prompt[:60]}...")
            
            try:
                # Generate with optimal settings for your style
                image = self.pipeline(
                    prompt=prompt,
                    negative_prompt="text, letters, words, watermarks, signatures, low quality, blurry, amateur, ugly",
                    width=1792,  # Divisible by 8 (closest to 1800)
                    height=896,  # Divisible by 8 (closest to 900)
                    num_inference_steps=35,  # Higher quality
                    guidance_scale=8.0,      # Strong prompt adherence
                    num_images_per_prompt=1
                ).images[0]
                
                # Save with descriptive name
                filename = f"style_outputs/{style_name}_sample_{i+1}.png"
                image.save(filename)
                
                print(f"✅ Generated: {filename}")
                generated_images.append(filename)
                
            except Exception as e:
                print(f"❌ Sample {i+1} failed: {str(e)}")
                continue
        
        print(f"\n🎉 Generated {len(generated_images)} style samples!")
        return generated_images
    
    def create_article_covers(self, style_info, article_titles):
        """Create actual article covers using your style"""
        
        if not self.pipeline:
            self.setup_pipeline()
        
        style_name = style_info['style_name']
        base_prompt = style_info['prompts'][0]  # Use best prompt
        
        print(f"\n📰 Creating article covers in {style_name} style...")
        print("=" * 50)
        
        os.makedirs("article_covers", exist_ok=True)
        covers = []
        
        for i, title in enumerate(article_titles):
            print(f"\n📝 Cover {i+1}: {title}")
            
            # Modify prompt for article cover context
            article_prompt = f"{base_prompt}, professional article cover background, no text or titles, cover design aesthetic"
            
            try:
                image = self.pipeline(
                    prompt=article_prompt,
                    negative_prompt="text, letters, words, titles, watermarks, signatures, logos, low quality",
                    width=1792,
                    height=896,
                    num_inference_steps=40,
                    guidance_scale=8.5,
                    num_images_per_prompt=1
                ).images[0]
                
                # Save cover
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:30]
                filename = f"article_covers/{style_name}_{safe_title.replace(' ', '_')}.png"
                image.save(filename)
                
                print(f"✅ Cover saved: {filename}")
                covers.append({
                    'title': title,
                    'file': filename,
                    'style': style_name
                })
                
            except Exception as e:
                print(f"❌ Cover for '{title}' failed: {str(e)}")
                continue
        
        return covers
    
    def interactive_refinement(self, style_name):
        """Interactive refinement of your style generation"""
        
        style_dir = f"training_data/{style_name}_style"
        style_info = self.analyze_style_images(style_dir)
        
        if not style_info:
            return
        
        print(f"\n🔧 Interactive Style Refinement: {style_name}")
        print("Commands:")
        print("  'generate' - Create style samples")
        print("  'covers' - Create article covers") 
        print("  'prompts' - Show current prompts")
        print("  'quit' - Exit")
        
        while True:
            command = input(f"\n[{style_name}] Enter command: ").strip().lower()
            
            if command == 'generate':
                num = input("How many samples? (default 3): ").strip()
                num_samples = int(num) if num.isdigit() else 3
                self.generate_style_samples(style_info, num_samples)
                
            elif command == 'covers':
                print("Enter article titles (one per line, empty line to finish):")
                titles = []
                while True:
                    title = input("Title: ").strip()
                    if not title:
                        break
                    titles.append(title)
                
                if titles:
                    self.create_article_covers(style_info, titles)
                else:
                    # Default titles
                    default_titles = [
                        "Bitcoin Reaches New All-Time High", 
                        "DeFi Innovation Report 2025",
                        "Blockchain Technology Adoption"
                    ]
                    self.create_article_covers(style_info, default_titles)
                    
            elif command == 'prompts':
                print(f"\nCurrent prompts for {style_name}:")
                for i, prompt in enumerate(style_info['prompts'], 1):
                    print(f"  {i}. {prompt}")
                    
            elif command == 'quit':
                break
                
            else:
                print("❓ Unknown command. Try: generate, covers, prompts, quit")

def main():
    parser = argparse.ArgumentParser(description="Simple Style Training")
    parser.add_argument("--style", choices=["dark", "colorful", "light"], required=True)
    parser.add_argument("--mode", choices=["analyze", "generate", "interactive"], default="interactive")
    
    args = parser.parse_args()
    
    trainer = SimpleStyleTrainer()
    
    if args.mode == "interactive":
        trainer.interactive_refinement(args.style)
    elif args.mode == "analyze":
        style_dir = f"training_data/{args.style}_style"
        style_info = trainer.analyze_style_images(style_dir)
        if style_info:
            print(f"\n✅ Analysis complete for {args.style} style")
    elif args.mode == "generate":
        style_dir = f"training_data/{args.style}_style"
        style_info = trainer.analyze_style_images(style_dir)
        if style_info:
            trainer.generate_style_samples(style_info)

if __name__ == "__main__":
    main()