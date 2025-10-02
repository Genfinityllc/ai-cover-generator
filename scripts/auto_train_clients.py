#!/usr/bin/env python3
"""
Auto-Train All Client LoRAs (Non-Interactive)
Starts training immediately for all user client logos
"""

import sys
import subprocess
import time
from pathlib import Path
import json
from datetime import datetime

def log_progress(message, log_file="training_progress.log"):
    """Log progress with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # Also write to log file
    with open(log_file, "a") as f:
        f.write(log_entry + "\n")

def main():
    """Auto-train all client LoRAs"""
    
    log_progress("🎨 Starting Auto-Training for All Client LoRAs")
    log_progress("=" * 60)
    
    # Define YOUR actual client logos (from your uploaded files)
    your_clients = [
        # XDC Network (your main client)
        {"name": "xdc_network", "priority": 1, "epochs": 50},  # Reduced epochs for faster training
        {"name": "xdc_logo", "priority": 2, "epochs": 50},
        
        # Hedera ecosystem
        {"name": "hedera", "priority": 3, "epochs": 50},
        {"name": "hedera_foundation", "priority": 4, "epochs": 50}, 
        {"name": "hbar", "priority": 5, "epochs": 50},
        
        # HashPack
        {"name": "hashpack", "priority": 6, "epochs": 50},
        {"name": "hashpack_color", "priority": 7, "epochs": 50},
        
        # Constellation
        {"name": "constellation", "priority": 8, "epochs": 50},
        {"name": "constellation_alt", "priority": 9, "epochs": 50},
        
        # Algorand
        {"name": "algorand", "priority": 10, "epochs": 50},
        
        # THA
        {"name": "tha", "priority": 11, "epochs": 50},
        {"name": "tha_color", "priority": 12, "epochs": 50},
        
        # Genfinity
        {"name": "genfinity", "priority": 13, "epochs": 50},
        {"name": "genfinity_black", "priority": 14, "epochs": 50},
    ]
    
    log_progress(f"📋 Training {len(your_clients)} client LoRAs")
    for client in your_clients:
        log_progress(f"   {client['priority']:2d}. {client['name']} ({client['epochs']} epochs)")
    
    log_progress(f"⏱️  Estimated training time: {len(your_clients) * 10} minutes")
    log_progress(f"   (≈10 minutes per LoRA with 50 epochs)")
    
    # Create models directory
    models_dir = Path("models/lora")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Train each client LoRA
    successful = []
    failed = []
    total_start_time = time.time()
    
    for i, client in enumerate(your_clients, 1):
        client_name = client['name']
        epochs = client['epochs']
        
        log_progress(f"\n[{i}/{len(your_clients)}] Training: {client_name}")
        log_progress(f"🔄 Starting LoRA training ({epochs} epochs)...")
        
        start_time = time.time()
        
        try:
            # Check if LoRA already exists
            lora_file = models_dir / f"{client_name}_lora.safetensors"
            if lora_file.exists():
                log_progress(f"   ⚠️  LoRA already exists, skipping: {lora_file}")
                successful.append({
                    "name": client_name,
                    "duration": 0,
                    "file": str(lora_file),
                    "status": "already_exists"
                })
                continue
            
            # Run training command
            cmd = [
                sys.executable,
                "scripts/train_lora_simple.py",
                "--logo-name", client_name,
                "--epochs", str(epochs),
                "--learning-rate", "1e-4",
                "--rank", "64"
            ]
            
            log_progress(f"   🚀 Command: {' '.join(cmd)}")
            
            # Run training with timeout (30 minutes per LoRA)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                log_progress(f"   ✅ Success! ({duration/60:.1f} minutes)")
                successful.append({
                    "name": client_name,
                    "duration": duration,
                    "file": str(lora_file),
                    "status": "trained"
                })
            else:
                error_msg = result.stderr[-200:] if result.stderr else "Unknown error"
                log_progress(f"   ❌ Failed: {error_msg}")
                failed.append({
                    "name": client_name,
                    "error": error_msg,
                    "duration": duration
                })
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            log_progress(f"   ⏰ Timeout after {duration/60:.1f} minutes")
            failed.append({
                "name": client_name,
                "error": "Training timeout (>30 minutes)",
                "duration": duration
            })
        except Exception as e:
            duration = time.time() - start_time
            log_progress(f"   ❌ Exception: {str(e)}")
            failed.append({
                "name": client_name,
                "error": str(e),
                "duration": duration
            })
    
    # Final summary
    total_duration = time.time() - total_start_time
    
    log_progress(f"\n📊 FINAL TRAINING SUMMARY")
    log_progress("=" * 60)
    log_progress(f"⏱️  Total time: {total_duration/3600:.1f} hours")
    
    log_progress(f"\n✅ Successful: {len(successful)}")
    for client in successful:
        status = client.get('status', 'trained')
        if status == 'already_exists':
            log_progress(f"   • {client['name']}: Already existed")
        else:
            log_progress(f"   • {client['name']}: {client['duration']/60:.1f} minutes")
    
    if failed:
        log_progress(f"\n❌ Failed: {len(failed)}")
        for client in failed:
            log_progress(f"   • {client['name']}: {client['error'][:100]}")
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_duration_hours": total_duration / 3600,
        "successful": successful,
        "failed": failed,
        "summary": {
            "total_clients": len(your_clients),
            "successful_count": len(successful),
            "failed_count": len(failed),
            "success_rate": len(successful) / len(your_clients) * 100
        }
    }
    
    with open("training_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    log_progress(f"\n💾 Detailed results saved to: training_results.json")
    
    # Show next steps
    if successful:
        log_progress(f"\n🚀 Next Steps:")
        log_progress(f"1. Test API integration: ./start.sh")
        log_progress(f"2. Validate LoRAs: python scripts/test_all_loras.py")
        log_progress(f"3. Deploy to production: ./deploy.sh")
        
        log_progress(f"\n🔗 Your LoRAs are ready for API integration!")
        log_progress(f"   Example API calls:")
        for client in successful[:3]:  # Show first 3
            client_name = client['name']
            if 'xdc' in client_name:
                api_id = 'xdc'
            elif 'hedera' in client_name or 'hbar' in client_name:
                api_id = 'hedera'
            elif 'algorand' in client_name:
                api_id = 'algorand'
            else:
                api_id = client_name.split('_')[0]
            
            log_progress(f'   curl -X POST /api/generate/cover -d \'{{"client_id": "{api_id}", "title": "Breaking News"}}\'')
    
    log_progress(f"\n🎉 Auto-training complete!")
    
    return 0 if len(failed) == 0 else 1

if __name__ == "__main__":
    exit(main())