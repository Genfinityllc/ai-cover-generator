#!/usr/bin/env python3
"""Debug LoRA names and loading"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ai_service import AIService

async def main():
    """Debug LoRA names"""
    print("🔍 Debugging LoRA names and loading...")
    
    ai_service = AIService()
    await ai_service.initialize()
    
    print("\n📋 Available LoRA models:")
    for name, info in ai_service.lora_models.items():
        print(f"  - {name}: {info.get('type', 'unknown')} ({info['path']})")
    
    print(f"\n🎯 Looking for client 'xdc_network':")
    lora_name = await ai_service._get_lora_for_client("xdc_network")
    print(f"  Mapped to: {lora_name}")
    
    if lora_name:
        print(f"  Exists in models? {'YES' if lora_name in ai_service.lora_models else 'NO'}")
        if lora_name in ai_service.lora_models:
            print(f"  Model info: {ai_service.lora_models[lora_name]}")

if __name__ == "__main__":
    asyncio.run(main())