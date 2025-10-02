#!/usr/bin/env python3
"""
Test script for AI cover image generation
Tests the complete pipeline locally
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ai_service import AIService
from app.models.requests import GenerateCoverRequest, ImageSize

async def test_basic_generation():
    """Test basic image generation without LoRA"""
    print("🧪 Testing basic image generation...")
    
    ai_service = AIService()
    await ai_service.initialize()
    
    # Test prompt
    test_prompt = "Bitcoin reaches new all-time high"
    
    # Generate background
    image = await ai_service.generate_background(
        prompt_enhancement=test_prompt
    )
    
    # Add text overlay
    final_image = await ai_service.add_text_overlay(
        image=image,
        title="Bitcoin Reaches $100K",
        subtitle="Historic milestone for cryptocurrency"
    )
    
    # Save test image
    output_path = Path("./temp_images")
    output_path.mkdir(exist_ok=True)
    
    final_image.save(output_path / "test_generation.png")
    print(f"✅ Test image saved to: {output_path / 'test_generation.png'}")

async def test_api_request():
    """Test with API request format"""
    print("🧪 Testing API request format...")
    
    # Create test request
    request = GenerateCoverRequest(
        title="Ethereum ETF Approved",
        subtitle="SEC gives green light to spot ETF",
        client_id="ethereum",
        size=ImageSize.STANDARD
    )
    
    ai_service = AIService()
    await ai_service.initialize()
    
    # Generate with client_id (will attempt to load LoRA)
    image = await ai_service.generate_background(
        client_id=request.client_id,
        prompt_enhancement=request.title
    )
    
    # Add text overlay
    final_image = await ai_service.add_text_overlay(
        image=image,
        title=request.title,
        subtitle=request.subtitle,
        size=(request.width, request.height)
    )
    
    # Save test image
    output_path = Path("./temp_images")
    output_path.mkdir(exist_ok=True)
    
    final_image.save(output_path / "test_api_request.png")
    print(f"✅ API test image saved to: {output_path / 'test_api_request.png'}")

async def test_different_sizes():
    """Test different image sizes"""
    print("🧪 Testing different image sizes...")
    
    ai_service = AIService()
    await ai_service.initialize()
    
    sizes = [
        (ImageSize.STANDARD, "1800x900"),
        (ImageSize.HD, "1920x1080")
    ]
    
    for size_enum, size_str in sizes:
        request = GenerateCoverRequest(
            title=f"Test Image {size_str}",
            subtitle="Size compatibility test",
            size=size_enum
        )
        
        # Generate image
        image = await ai_service.generate_background(
            prompt_enhancement=request.title
        )
        
        # Add text overlay
        final_image = await ai_service.add_text_overlay(
            image=image,
            title=request.title,
            subtitle=request.subtitle,
            size=(request.width, request.height)
        )
        
        # Save test image
        output_path = Path("./temp_images")
        output_path.mkdir(exist_ok=True)
        
        filename = f"test_size_{size_str.replace('x', '_')}.png"
        final_image.save(output_path / filename)
        print(f"✅ {size_str} test image saved to: {output_path / filename}")

async def test_system_info():
    """Test system capabilities"""
    print("🔍 Testing system information...")
    
    ai_service = AIService()
    
    # Check device
    print(f"🖥️  Device: {ai_service.device}")
    print(f"🧠 MPS Available: {ai_service.device == 'mps'}")
    
    # Initialize and check status
    await ai_service.initialize()
    status = await ai_service.get_status()
    
    print("📊 System Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")

def main():
    """Run all tests"""
    print("🚀 Starting AI Cover Generator Tests")
    print("=" * 50)
    
    async def run_tests():
        try:
            await test_system_info()
            print()
            
            await test_basic_generation()
            print()
            
            await test_api_request()
            print()
            
            await test_different_sizes()
            print()
            
            print("🎉 All tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run tests
    asyncio.run(run_tests())

if __name__ == "__main__":
    main()