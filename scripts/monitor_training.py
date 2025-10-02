#!/usr/bin/env python3
"""
Monitor LoRA Training Progress
Shows real-time progress of batch training
"""

import time
import os
from pathlib import Path
import json

def check_training_progress():
    """Check current training progress"""
    
    # Check for progress log
    log_file = Path("training_progress.log")
    if log_file.exists():
        print("📋 Latest Training Log:")
        print("-" * 50)
        with open(log_file, "r") as f:
            lines = f.readlines()
            # Show last 10 lines
            for line in lines[-10:]:
                print(line.strip())
    
    # Check models directory
    models_dir = Path("models/lora")
    if models_dir.exists():
        lora_files = list(models_dir.glob("*_lora.safetensors"))
        print(f"\n📁 LoRA Files Created: {len(lora_files)}")
        for lora_file in lora_files:
            size_mb = lora_file.stat().st_size / (1024 * 1024)
            print(f"   ✅ {lora_file.name} ({size_mb:.1f} MB)")
    
    # Check results file
    results_file = Path("training_results.json")
    if results_file.exists():
        print(f"\n📊 Training Results Available:")
        with open(results_file, "r") as f:
            results = json.load(f)
            summary = results.get("summary", {})
            print(f"   Total: {summary.get('total_clients', 0)}")
            print(f"   Successful: {summary.get('successful_count', 0)}")
            print(f"   Failed: {summary.get('failed_count', 0)}")
            print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")

def main():
    """Monitor training progress"""
    print("🔍 LoRA Training Progress Monitor")
    print("=" * 50)
    
    check_training_progress()
    
    print(f"\n💡 Tips:")
    print(f"   • Training runs in background")
    print(f"   • Each LoRA takes ~10-15 minutes (50 epochs)")
    print(f"   • Total estimated time: ~2-3 hours")
    print(f"   • Check progress: python scripts/monitor_training.py")
    print(f"   • Full log: tail -f training_progress.log")

if __name__ == "__main__":
    main()