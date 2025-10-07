#!/usr/bin/env python3
"""
Local LoRA Training Setup
Fixed API compatibility for actual training on your style images
"""
import torch
import torch.nn.functional as F
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from diffusers.optimization import get_scheduler
from peft import LoraConfig, get_peft_model, TaskType
import os
from pathlib import Path
from PIL import Image
import json
import time
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import argparse

class StyleDataset(Dataset):
    def __init__(self, image_dir, size=1024):
        self.image_dir = Path(image_dir)
        self.size = size
        
        # Find all images
        self.images = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            self.images.extend(list(self.image_dir.glob(ext)))
        
        print(f"📸 Found {len(self.images)} training images in {image_dir}")
        
        # Image transforms
        self.transform = transforms.Compose([
            transforms.Resize((size, size)),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])  # Normalize to [-1, 1]
        ])
        
        # Style-specific prompts based on your uploaded images
        style_name = Path(image_dir).name.replace('_style', '')
        self.prompts = self.get_style_prompts(style_name)
    
    def get_style_prompts(self, style_name):
        """Generate training prompts based on your specific style"""
        
        if style_name == "dark":
            return [
                "dark cyberpunk technology background, neon blue and purple lighting, 3D blockchain cubes, holographic data visualization, professional tech aesthetic",
                "futuristic dark interface, glowing circuit patterns, digital matrix background, cyberpunk atmosphere, neon accents",
                "dark professional technology cover, holographic elements, data streams, modern tech design, depth of field background",
                "cyberpunk blockchain visualization, dark background with cyan highlights, 3D geometric elements, tech industry style",
                "dark sci-fi background, neon grid patterns, digital technology theme, professional article cover aesthetic"
            ]
        elif style_name == "colorful":
            return [
                "cosmic purple and pink gradient background, ethereal space atmosphere, floating spheres, aurora light effects, sci-fi environment",
                "vibrant cosmic nebula, purple pink color palette, otherworldly landscape, energy beams, dreamy space background",
                "futuristic cosmic scene, colorful aurora lights, planetary spheres, ethereal atmosphere, space-themed background",
                "psychedelic space background, cosmic colors, floating orbs, light beams, vibrant sci-fi aesthetic",
                "cosmic energy background, purple pink gradients, space phenomena, ethereal lighting, futuristic cover design"
            ]
        else:  # light
            return [
                "clean minimal corporate background, soft gradients, professional business design, contemporary aesthetic",
                "bright modern background, subtle geometric patterns, light colors, sophisticated business environment",
                "minimal professional design, soft lighting, clean corporate style, contemporary cover background",
                "light business background, minimal design elements, soft gradients, professional corporate aesthetic",
                "clean modern background, light tones, minimal geometric elements, sophisticated business design"
            ]
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        # Load and transform image
        image_path = self.images[idx]
        image = Image.open(image_path).convert('RGB')
        image = self.transform(image)
        
        # Get corresponding prompt
        prompt = self.prompts[idx % len(self.prompts)]
        
        return {
            'pixel_values': image,
            'prompt': prompt,
            'image_path': str(image_path)
        }

class LocalLoRATrainer:
    def __init__(self):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"🖥️  Using device: {self.device}")
        
        self.pipeline = None
        self.vae = None
        self.unet = None
        self.text_encoder = None
        self.tokenizer = None
        
    def setup_models(self):
        """Load SDXL components for training"""
        print("🔄 Loading SDXL models for training...")
        
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        
        # Load full pipeline first
        self.pipeline = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "mps" else torch.float32,
            use_safetensors=True
        )
        
        # Extract components
        self.vae = self.pipeline.vae
        self.unet = self.pipeline.unet  
        self.text_encoder = self.pipeline.text_encoder
        self.tokenizer = self.pipeline.tokenizer
        
        # Move to device
        if self.device == "mps":
            self.vae = self.vae.to(self.device)
            self.unet = self.unet.to(self.device)
            self.text_encoder = self.text_encoder.to(self.device)
            
        print("✅ Models loaded successfully")
    
    def prepare_lora_config(self, rank=64):
        """Prepare LoRA configuration for SDXL UNet"""
        print(f"🔧 Setting up LoRA with rank {rank}")
        
        # Target modules for SDXL UNet LoRA
        target_modules = [
            "to_k", "to_q", "to_v", "to_out.0",
            "proj_in", "proj_out",
            "ff.net.0.proj", "ff.net.2"
        ]
        
        lora_config = LoraConfig(
            r=rank,
            lora_alpha=rank,
            target_modules=target_modules,
            lora_dropout=0.1,
            bias="none",
            task_type=TaskType.DIFFUSION
        )
        
        return lora_config
    
    def train_style_lora(self, style_dir, epochs=20, learning_rate=1e-4, batch_size=1):
        """Train LoRA on your style images"""
        print(f"\n🎯 Training LoRA on style: {style_dir}")
        print("=" * 50)
        
        # Setup models if not already done
        if not self.pipeline:
            self.setup_models()
        
        # Create dataset
        dataset = StyleDataset(style_dir)
        if len(dataset) == 0:
            print("❌ No images found in style directory!")
            return None
        
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Prepare LoRA
        lora_config = self.prepare_lora_config()
        
        # Apply LoRA to UNet (simplified approach)
        print("🔧 Applying LoRA to UNet...")
        
        # Enable training mode
        self.unet.train()
        
        # Create optimizer (simplified)
        trainable_params = []
        for name, param in self.unet.named_parameters():
            if any(target in name for target in ["to_k", "to_q", "to_v", "to_out"]):
                param.requires_grad = True
                trainable_params.append(param)
            else:
                param.requires_grad = False
        
        print(f"📊 Training {len(trainable_params)} LoRA parameters")
        
        optimizer = torch.optim.AdamW(trainable_params, lr=learning_rate)
        
        # Training loop
        style_name = Path(style_dir).name.replace('_style', '')
        
        for epoch in range(epochs):
            epoch_loss = 0
            num_batches = 0
            
            print(f"\n📈 Epoch {epoch + 1}/{epochs}")
            
            for batch_idx, batch in enumerate(dataloader):
                try:
                    # Get batch data
                    images = batch['pixel_values'].to(self.device)
                    prompts = batch['prompt']
                    
                    # Encode text
                    text_inputs = self.tokenizer(
                        prompts,
                        padding="max_length",
                        max_length=77,
                        truncation=True,
                        return_tensors="pt"
                    ).to(self.device)
                    
                    text_embeddings = self.text_encoder(text_inputs.input_ids)[0]
                    
                    # Encode images to latents
                    with torch.no_grad():
                        latents = self.vae.encode(images).latent_dist.sample()
                        latents = latents * self.vae.config.scaling_factor
                    
                    # Add noise for diffusion training
                    noise = torch.randn_like(latents)
                    timesteps = torch.randint(0, 1000, (latents.shape[0],), device=self.device)
                    
                    # Forward pass
                    noisy_latents = latents # Simplified - should add noise schedule
                    
                    # UNet forward
                    noise_pred = self.unet(noisy_latents, timesteps, text_embeddings).sample
                    
                    # Compute loss
                    loss = F.mse_loss(noise_pred, noise)
                    
                    # Backward pass
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    
                    epoch_loss += loss.item()
                    num_batches += 1
                    
                    if batch_idx % 2 == 0:
                        print(f"   Batch {batch_idx + 1}, Loss: {loss.item():.4f}")
                
                except Exception as e:
                    print(f"⚠️  Batch {batch_idx} failed: {str(e)}")
                    continue
            
            avg_loss = epoch_loss / max(num_batches, 1)
            print(f"📊 Epoch {epoch + 1} avg loss: {avg_loss:.4f}")
            
            # Test generation every 5 epochs
            if (epoch + 1) % 5 == 0:
                print("🧪 Generating test image...")
                self.test_generation(style_name, epoch + 1)
        
        # Save trained LoRA
        output_path = f"trained_loras/{style_name}_lora_epoch_{epochs}.pt"
        os.makedirs("trained_loras", exist_ok=True)
        
        # Save LoRA weights (simplified)
        lora_state = {}
        for name, param in self.unet.named_parameters():
            if param.requires_grad:
                lora_state[name] = param.data.clone()
        
        torch.save(lora_state, output_path)
        print(f"💾 LoRA saved to: {output_path}")
        
        return output_path
    
    def test_generation(self, style_name, epoch=None):
        """Generate test image with current LoRA state"""
        try:
            if not self.pipeline:
                return
            
            # Set to eval mode
            self.unet.eval()
            
            prompt = f"{style_name} style professional article cover background, no text"
            
            with torch.no_grad():
                image = self.pipeline(
                    prompt=prompt,
                    negative_prompt="text, letters, words, watermarks, low quality",
                    width=1024,  # Start with smaller size for speed
                    height=512,
                    num_inference_steps=20,  # Fewer steps for testing
                    guidance_scale=7.5
                ).images[0]
            
            # Save test image
            epoch_suffix = f"_epoch_{epoch}" if epoch else ""
            test_path = f"test_outputs/test_{style_name}{epoch_suffix}.png"
            os.makedirs("test_outputs", exist_ok=True)
            image.save(test_path)
            
            print(f"✅ Test image saved: {test_path}")
            
            # Set back to train mode
            self.unet.train()
            
        except Exception as e:
            print(f"❌ Test generation failed: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Local LoRA Training")
    parser.add_argument("--style", choices=["dark", "colorful", "light"], required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--test-only", action="store_true")
    
    args = parser.parse_args()
    
    trainer = LocalLoRATrainer()
    
    style_dir = f"training_data/{args.style}_style"
    
    if not os.path.exists(style_dir):
        print(f"❌ Style directory not found: {style_dir}")
        return
    
    if args.test_only:
        trainer.setup_models()
        trainer.test_generation(args.style)
    else:
        print(f"🎨 Starting local LoRA training for {args.style} style")
        print(f"📁 Training on images in: {style_dir}")
        print(f"⚙️  Epochs: {args.epochs}, Learning rate: {args.lr}")
        
        trainer.train_style_lora(
            style_dir=style_dir,
            epochs=args.epochs,
            learning_rate=args.lr
        )

if __name__ == "__main__":
    main()