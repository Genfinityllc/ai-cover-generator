#!/usr/bin/env python3
"""
Train LoRAs for User's Specific Client Logos Only
Excludes sample/test data, trains only real client logos
"""

import sys
import subprocess
import time
from pathlib import Path

def main():
    """Train LoRAs for user's actual client logos"""
    
    print("🎨 Training LoRAs for Your Client Logos")
    print("=" * 50)
    
    # Define YOUR actual client logos (from your uploaded files)
    your_clients = [
        # XDC Network (your main client)
        {"name": "xdc_network", "priority": 1, "epochs": 100},
        {"name": "xdc_logo", "priority": 2, "epochs": 100},
        
        # Hedera ecosystem
        {"name": "hedera", "priority": 3, "epochs": 100},
        {"name": "hedera_foundation", "priority": 4, "epochs": 100}, 
        {"name": "hbar", "priority": 5, "epochs": 100},
        
        # HashPack
        {"name": "hashpack", "priority": 6, "epochs": 100},
        {"name": "hashpack_color", "priority": 7, "epochs": 100},
        
        # Constellation
        {"name": "constellation", "priority": 8, "epochs": 100},
        {"name": "constellation_alt", "priority": 9, "epochs": 100},
        
        # Algorand
        {"name": "algorand", "priority": 10, "epochs": 100},
        
        # THA
        {"name": "tha", "priority": 11, "epochs": 100},
        {"name": "tha_color", "priority": 12, "epochs": 100},
        
        # Genfinity
        {"name": "genfinity", "priority": 13, "epochs": 100},
        {"name": "genfinity_black", "priority": 14, "epochs": 100},
    ]
    
    print(f"📋 Your Client Logos to Train: {len(your_clients)}")
    for client in your_clients:
        print(f"   {client['priority']:2d}. {client['name']}")
    
    print(f"\n⏱️  Estimated training time: {len(your_clients) * 20} minutes")
    print(f"   (≈20 minutes per LoRA on Mac Studio)")
    
    # Confirm before starting
    response = input(f"\n🚀 Start training all {len(your_clients)} client LoRAs? [y/N]: ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Training cancelled")
        return 1
    
    # Train each client LoRA
    successful = []
    failed = []
    
    for i, client in enumerate(your_clients, 1):
        client_name = client['name']
        epochs = client['epochs']
        
        print(f"\n[{i}/{len(your_clients)}] Training: {client_name}")
        print(f"🔄 Starting LoRA training ({epochs} epochs)...")
        
        start_time = time.time()
        
        try:
            # Run training command
            cmd = [
                sys.executable,
                "scripts/train_lora_simple.py",
                "--logo-name", client_name,
                "--epochs", str(epochs),
                "--learning-rate", "1e-4",
                "--rank", "64"
            ]
            
            # Run training (this will take 15-30 minutes per client)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"   ✅ Success! ({duration/60:.1f} minutes)")
                successful.append({
                    "name": client_name,
                    "duration": duration,
                    "file": f"models/lora/{client_name}_lora.safetensors"
                })
            else:
                print(f"   ❌ Failed: {result.stderr}")
                failed.append({
                    "name": client_name,
                    "error": result.stderr
                })
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout (>1 hour)")
            failed.append({
                "name": client_name,
                "error": "Training timeout"
            })
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            failed.append({
                "name": client_name,
                "error": str(e)
            })
    
    # Summary
    print(f"\n📊 TRAINING SUMMARY")
    print("=" * 50)
    
    print(f"✅ Successful: {len(successful)}")
    for client in successful:
        print(f"   • {client['name']}: {client['duration']/60:.1f} minutes")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for client in failed:
            print(f"   • {client['name']}: {client['error'][:100]}...")
    
    # Show API integration
    if successful:
        print(f"\n🔗 Your LoRAs are ready for API integration:")
        print(f"   Example API calls:")
        for client in successful[:3]:  # Show first 3
            client_id = client['name'].replace('_', '').replace('network', '').replace('foundation', '')[:10]
            print(f'   curl -X POST /api/generate/cover -d \'{{"client_id": "{client_id}", "title": "News"}}\'')
    
    print(f"\n🎉 Training complete!")
    return 0

if __name__ == "__main__":
    exit(main())