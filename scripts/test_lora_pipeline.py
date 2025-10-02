#!/usr/bin/env python3
"""
Simple test of the LoRA training pipeline
Tests basic functionality without strict validation
"""

import sys
import torch
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_pytorch_metal():
    """Test PyTorch and Metal availability"""
    print("🔍 Testing PyTorch and Metal...")
    
    print(f"   PyTorch version: {torch.__version__}")
    
    if hasattr(torch.backends, 'mps'):
        metal_available = torch.backends.mps.is_available()
        print(f"   Metal (MPS) available: {metal_available}")
        
        if metal_available:
            # Test basic Metal operations
            try:
                device = torch.device("mps")
                x = torch.randn(100, 100).to(device)
                y = torch.mm(x, x.t())
                print(f"   ✅ Metal computation test passed")
                return "mps"
            except Exception as e:
                print(f"   ⚠️  Metal test failed: {e}")
                return "cpu"
        else:
            print("   Using CPU")
            return "cpu"
    else:
        print("   Metal not supported (PyTorch too old)")
        return "cpu"

def test_diffusers_import():
    """Test diffusers library import"""
    print("🔍 Testing Diffusers library...")
    
    try:
        from diffusers import StableDiffusionXLPipeline
        print("   ✅ Diffusers imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Diffusers import failed: {e}")
        return False

def test_training_data():
    """Test training data availability"""
    print("🔍 Testing training data...")
    
    data_dir = Path("training_data")
    if not data_dir.exists():
        print("   ❌ Training data directory not found")
        return False
    
    # Check for any logo directories with images
    logo_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    
    total_images = 0
    for logo_dir in logo_dirs:
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(logo_dir.glob(ext))
        
        if image_files:
            print(f"   📁 {logo_dir.name}: {len(image_files)} images")
            total_images += len(image_files)
    
    if total_images > 0:
        print(f"   ✅ Found {total_images} training images total")
        return True
    else:
        print("   ❌ No training images found")
        return False

def test_simple_generation():
    """Test simple image generation without LoRA"""
    print("🔍 Testing basic image generation...")
    
    try:
        from diffusers import StableDiffusionXLPipeline
        
        device = test_pytorch_metal()
        
        print("   🔄 Loading SDXL pipeline (this may take a while)...")
        
        # Load a smaller model for testing
        pipeline = StableDiffusionXLPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16 if device == "mps" else torch.float32,
            use_safetensors=True
        )
        
        if device == "mps":
            pipeline = pipeline.to("mps")
        
        print("   ✅ Pipeline loaded successfully")
        
        # Generate a simple test image
        print("   🎨 Generating test image...")
        
        prompt = "a simple cryptocurrency logo, professional design"
        
        with torch.autocast(device):
            image = pipeline(
                prompt,
                height=512,
                width=512,
                num_inference_steps=10,  # Quick test
                guidance_scale=7.5
            ).images[0]
        
        # Save test image
        output_dir = Path("temp_images")
        output_dir.mkdir(exist_ok=True)
        
        test_image_path = output_dir / "pipeline_test.png"
        image.save(test_image_path)
        
        print(f"   ✅ Test image generated: {test_image_path}")
        return True
        
    except Exception as e:
        print(f"   ❌ Generation test failed: {e}")
        return False

def main():
    """Run all pipeline tests"""
    print("🧪 LoRA Training Pipeline Test")
    print("=" * 50)
    
    tests = [
        ("PyTorch/Metal", test_pytorch_metal),
        ("Diffusers Library", test_diffusers_import),
        ("Training Data", test_training_data),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Optional generation test (takes longer)
    print(f"\n📋 Test Results:")
    print("-" * 30)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Overall assessment
    print(f"\n🎯 Assessment:")
    if all(results.values()):
        print("✅ All basic tests passed! LoRA training pipeline ready.")
        print("\n🚀 Next steps:")
        print("1. Add more training images (20-30 per logo)")
        print("2. Run: python scripts/train_lora_simple.py --logo-name bitcoin --epochs 50")
        print("3. Test with generated LoRA")
        
        # Ask about generation test
        response = input("\n🎨 Run image generation test? (takes 2-3 minutes) [y/N]: ")
        if response.lower() in ['y', 'yes']:
            print("\nImage Generation Test:")
            test_simple_generation()
            
    else:
        print("❌ Some tests failed. Please fix issues before proceeding.")
        print("\n🔧 Common fixes:")
        print("• Ensure PyTorch is installed: pip install torch")
        print("• Install diffusers: pip install diffusers")
        print("• Create sample data: python scripts/collect_sample_images.py")

if __name__ == "__main__":
    main()