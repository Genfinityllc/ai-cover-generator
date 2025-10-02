#!/usr/bin/env python3
"""
LoRA Training Setup for Mac Studio
Uses a simplified but effective training approach
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'torch',
        'diffusers',
        'transformers', 
        'accelerate',
        'peft',
        'datasets',
        'pillow'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"   ❌ {package}")
    
    return missing

def install_training_dependencies():
    """Install additional dependencies for LoRA training"""
    print("📦 Installing LoRA training dependencies...")
    
    # Additional packages for training
    training_packages = [
        'datasets',
        'accelerate',
        'xformers',  # For memory efficiency
        'bitsandbytes',  # For 8-bit training (if available on Mac)
    ]
    
    for package in training_packages:
        try:
            print(f"   Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  {package} failed to install: {e}")

def setup_kohya_trainer():
    """Setup Kohya LoRA trainer (recommended for production)"""
    print("🛠️  Setting up Kohya LoRA trainer...")
    
    kohya_dir = Path("./external/kohya-ss")
    
    if not kohya_dir.exists():
        print("📥 Cloning Kohya LoRA trainer...")
        try:
            subprocess.run([
                'git', 'clone', 
                'https://github.com/kohya-ss/sd-scripts.git',
                str(kohya_dir)
            ], check=True)
            print("   ✅ Kohya trainer cloned")
        except subprocess.CalledProcessError:
            print("   ❌ Failed to clone Kohya trainer")
            return False
    else:
        print("   ✅ Kohya trainer already exists")
    
    # Install Kohya requirements
    requirements_file = kohya_dir / "requirements.txt"
    if requirements_file.exists():
        print("📦 Installing Kohya requirements...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '-r', str(requirements_file)
            ], check=True, capture_output=True)
            print("   ✅ Kohya requirements installed")
        except subprocess.CalledProcessError:
            print("   ⚠️  Some Kohya requirements may have failed")
    
    return True

def create_training_config():
    """Create training configuration files"""
    print("📝 Creating training configuration...")
    
    config_dir = Path("./training_configs")
    config_dir.mkdir(exist_ok=True)
    
    # Sample training config
    config_content = """# LoRA Training Configuration
# Optimized for Mac Studio Metal

# Model settings
model_name: "stabilityai/stable-diffusion-xl-base-1.0"
vae_name: null
output_dir: "./models/lora"

# LoRA settings
network_module: "networks.lora"
network_dim: 64
network_alpha: 64
network_train_unet_only: true
network_weights: null

# Training settings
resolution: 1024
batch_size: 1
max_train_epochs: 1000
learning_rate: 1e-4
lr_scheduler: "cosine_with_restarts"
optimizer_type: "AdamW8bit"

# Data settings
train_data_dir: "./training_data"
reg_data_dir: null
enable_bucket: true
min_bucket_reso: 512
max_bucket_reso: 1024

# Memory optimization (Mac Studio)
mixed_precision: "fp16"
gradient_checkpointing: true
xformers: true
lowram: true

# Output settings
save_every_n_epochs: 100
save_model_as: "safetensors"
"""
    
    with open(config_dir / "default_config.yaml", "w") as f:
        f.write(config_content)
    
    print(f"   ✅ Config saved to: {config_dir / 'default_config.yaml'}")
    
    return config_dir

def main():
    """Main setup function"""
    print("🚀 LoRA Training Setup for Mac Studio")
    print("=" * 50)
    
    # Check current dependencies
    missing = check_dependencies()
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("📦 Installing missing packages...")
        for package in missing:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
                print(f"   ✅ {package} installed")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to install {package}")
    
    # Install training-specific dependencies
    install_training_dependencies()
    
    # Setup Kohya trainer (optional but recommended)
    kohya_success = setup_kohya_trainer()
    
    # Create training configs
    config_dir = create_training_config()
    
    print("\n✅ LoRA Training Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Collect training images (20-30 per logo)")
    print("2. Place images in training_data/{logo_name}/ folders")
    print("3. Run: python scripts/validate_training_data.py")
    print("4. Start training: python scripts/train_lora_simple.py")
    
    if kohya_success:
        print("\n🎯 Advanced Training (Kohya):")
        print("   For production-quality LoRAs, use Kohya trainer in ./external/kohya-ss/")
    
    print(f"\n📁 Training config: {config_dir}")
    
    return 0

if __name__ == "__main__":
    exit(main())