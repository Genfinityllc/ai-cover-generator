#!/usr/bin/env python3
"""
Training Data Validation Script
Checks if your logo datasets are ready for LoRA training
"""

import os
import argparse
from pathlib import Path
from PIL import Image
import hashlib
from collections import defaultdict
import sys

def validate_training_data(data_dir: str):
    """Validate training data structure and quality"""
    
    print("🔍 Validating Training Data")
    print("=" * 50)
    
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"❌ Training data directory not found: {data_dir}")
        return False
    
    # Get all logo directories
    logo_dirs = [d for d in data_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    if not logo_dirs:
        print("❌ No logo directories found!")
        return False
    
    print(f"📁 Found {len(logo_dirs)} logo directories")
    
    total_images = 0
    issues = []
    duplicates = defaultdict(list)
    
    for logo_dir in logo_dirs:
        logo_name = logo_dir.name
        print(f"\n🏷️  Checking: {logo_name}")
        
        # Get image files
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']:
            image_files.extend(logo_dir.glob(ext))
        
        image_count = len(image_files)
        total_images += image_count
        
        print(f"   📸 Images: {image_count}")
        
        # Check image count
        if image_count < 10:
            issues.append(f"⚠️  {logo_name}: Only {image_count} images (recommend 20-30)")
        elif image_count < 20:
            issues.append(f"💡 {logo_name}: {image_count} images (could use more for better results)")
        else:
            print(f"   ✅ Good image count: {image_count}")
        
        # Check individual images
        valid_images = 0
        for img_file in image_files:
            try:
                with Image.open(img_file) as img:
                    width, height = img.size
                    
                    # Check resolution
                    if width < 256 or height < 256:
                        issues.append(f"⚠️  {img_file.name}: Low resolution ({width}x{height})")
                    
                    # Check for duplicates by file hash
                    with open(img_file, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        duplicates[file_hash].append(str(img_file))
                    
                    valid_images += 1
                    
            except Exception as e:
                issues.append(f"❌ {img_file.name}: Invalid image - {str(e)}")
        
        print(f"   ✅ Valid images: {valid_images}/{image_count}")
        
        # Sample some image info
        if image_files:
            sample_img = image_files[0]
            try:
                with Image.open(sample_img) as img:
                    print(f"   📐 Sample size: {img.size}")
                    print(f"   🎨 Sample mode: {img.mode}")
            except:
                pass
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    print(f"Total logos: {len(logo_dirs)}")
    print(f"Total images: {total_images}")
    print(f"Average per logo: {total_images/len(logo_dirs):.1f}")
    
    # Check for duplicates
    duplicate_sets = [files for files in duplicates.values() if len(files) > 1]
    if duplicate_sets:
        print(f"\n🔄 Found {len(duplicate_sets)} sets of duplicate images:")
        for i, dupe_set in enumerate(duplicate_sets[:5]):  # Show first 5
            print(f"   Set {i+1}: {[Path(f).name for f in dupe_set]}")
    
    # Report issues
    if issues:
        print(f"\n⚠️  ISSUES FOUND ({len(issues)}):")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"   {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more issues")
    else:
        print("\n✅ No major issues found!")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if total_images < len(logo_dirs) * 20:
        print("   • Add more training images (aim for 20-30 per logo)")
    print("   • Ensure variety in backgrounds and lighting")
    print("   • Include both logo+text and symbol-only versions")
    print("   • Test with different sizes and orientations")
    
    return len(issues) == 0

def main():
    parser = argparse.ArgumentParser(description="Validate LoRA training data")
    parser.add_argument("--data-dir", default="./training_data", help="Training data directory")
    
    args = parser.parse_args()
    
    success = validate_training_data(args.data_dir)
    
    if success:
        print("\n🎉 Training data validation passed!")
        print("🚀 Ready to start LoRA training!")
        return 0
    else:
        print("\n❌ Please fix the issues above before training")
        return 1

if __name__ == "__main__":
    exit(main())