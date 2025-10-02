#!/usr/bin/env python3
"""
Batch Logo Processing Script
Processes multiple client logos at once for LoRA training
"""

import os
import argparse
from pathlib import Path
import subprocess
import sys

class BatchLogoProcessor:
    def __init__(self, variations_per_logo=25):
        self.variations_per_logo = variations_per_logo
        self.processed_logos = []
        self.failed_logos = []
        
        # Define logo mapping - maps file names to client names
        self.logo_mappings = {
            # XDC Network
            "XDC NETWORK WITH COIN LOGO WHITE.png": "xdc_network",
            "XDC LOGO White.png": "xdc_logo",
            
            # Algorand
            "Algorand Logo White.png": "algorand",
            
            # Constellation
            "Constellation Logo white.png": "constellation",
            "Logo Constellation white.png": "constellation_alt",
            
            # Hedera
            "H Hedera Logo White.png": "hedera",
            "Hedera Logo white.png": "hedera_foundation", 
            "Hedera Foundation logo white.png": "hedera_foundation_alt",
            "hbar.png": "hbar",
            
            # HashPack
            "HashPack logo White.png": "hashpack",
            "HashPack logo Color.png": "hashpack_color",
            
            # THA
            "THA Logo White.png": "tha",
            "THA Logo color.png": "tha_color",
            
            # Genfinity
            "Genfinity high res logo.png": "genfinity",
            "Genfinity Logo - white copy.svg": "genfinity_white",
            "black gen logo.jpg": "genfinity_black",
        }
    
    def get_client_name_from_file(self, filename: str) -> str:
        """Get client name from filename"""
        if filename in self.logo_mappings:
            return self.logo_mappings[filename]
        
        # Fallback: create name from filename
        base_name = Path(filename).stem
        client_name = base_name.lower()
        client_name = client_name.replace(" logo", "")
        client_name = client_name.replace(" white", "")
        client_name = client_name.replace(" color", "")
        client_name = client_name.replace(" ", "_")
        client_name = client_name.replace("-", "_")
        
        return client_name
    
    def process_single_logo(self, logo_path: str, client_name: str) -> bool:
        """Process a single logo file"""
        try:
            print(f"\n🎨 Processing: {Path(logo_path).name}")
            print(f"   Client: {client_name}")
            
            # Create output directory
            output_dir = f"training_data/{client_name}"
            
            # Check if already processed
            output_path = Path(output_dir)
            if output_path.exists():
                existing_images = len(list(output_path.glob("*.png")))
                if existing_images >= 20:
                    print(f"   ⚠️  Already has {existing_images} images, skipping...")
                    return True
            
            # Run logo variation generator
            cmd = [
                sys.executable, 
                "scripts/generate_logo_variations.py",
                "--input", logo_path,
                "--output-dir", output_dir,
                "--count", str(self.variations_per_logo)
            ]
            
            print(f"   🔄 Generating {self.variations_per_logo} variations...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Success! Generated variations in {output_dir}")
                self.processed_logos.append({
                    "client_name": client_name,
                    "logo_file": Path(logo_path).name,
                    "output_dir": output_dir,
                    "variations": self.variations_per_logo
                })
                return True
            else:
                print(f"   ❌ Failed: {result.stderr}")
                self.failed_logos.append({
                    "client_name": client_name,
                    "logo_file": Path(logo_path).name,
                    "error": result.stderr
                })
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            self.failed_logos.append({
                "client_name": client_name,
                "logo_file": Path(logo_path).name,
                "error": str(e)
            })
            return False
    
    def process_directory(self, logo_dir: str, file_patterns: list = None) -> dict:
        """Process all logos in a directory"""
        
        logo_path = Path(logo_dir)
        if not logo_path.exists():
            print(f"❌ Directory not found: {logo_dir}")
            return {"processed": [], "failed": []}
        
        print(f"🔍 Scanning directory: {logo_dir}")
        
        # Default patterns for logo files
        if file_patterns is None:
            file_patterns = ["*.png", "*.jpg", "*.jpeg", "*.svg"]
        
        # Find logo files
        logo_files = []
        for pattern in file_patterns:
            logo_files.extend(logo_path.glob(pattern))
        
        # Filter out non-logo files
        filtered_files = []
        for logo_file in logo_files:
            filename = logo_file.name.lower()
            # Skip obvious non-logo files
            if any(skip in filename for skip in ['banner', 'poster', 'ad', 'psd']):
                continue
            filtered_files.append(logo_file)
        
        print(f"📁 Found {len(filtered_files)} logo files to process")
        
        # Process each logo
        for i, logo_file in enumerate(filtered_files, 1):
            print(f"\n[{i}/{len(filtered_files)}] Processing: {logo_file.name}")
            
            client_name = self.get_client_name_from_file(logo_file.name)
            success = self.process_single_logo(str(logo_file), client_name)
            
            if success:
                print(f"   ✅ Completed: {client_name}")
            else:
                print(f"   ❌ Failed: {client_name}")
        
        return {
            "processed": self.processed_logos,
            "failed": self.failed_logos
        }
    
    def generate_client_mappings(self) -> dict:
        """Generate client ID mappings for API integration"""
        mappings = {}
        
        for logo_info in self.processed_logos:
            client_name = logo_info["client_name"]
            
            # Create various mapping variations
            mappings[client_name] = client_name
            
            # Add common variations
            if "xdc" in client_name:
                mappings["xdc"] = client_name
            elif "algorand" in client_name:
                mappings["algorand"] = client_name
                mappings["algo"] = client_name
            elif "constellation" in client_name:
                mappings["constellation"] = client_name
                mappings["dag"] = client_name
            elif "hedera" in client_name:
                mappings["hedera"] = client_name
                mappings["hbar"] = client_name
            elif "hashpack" in client_name:
                mappings["hashpack"] = client_name
            elif "tha" in client_name:
                mappings["tha"] = client_name
            elif "genfinity" in client_name:
                mappings["genfinity"] = client_name
                mappings["gen"] = client_name
        
        return mappings
    
    def print_summary(self):
        """Print processing summary"""
        print(f"\n📊 BATCH PROCESSING SUMMARY")
        print("=" * 50)
        
        print(f"✅ Successfully processed: {len(self.processed_logos)}")
        for logo in self.processed_logos:
            print(f"   • {logo['client_name']}: {logo['variations']} variations")
        
        if self.failed_logos:
            print(f"\n❌ Failed to process: {len(self.failed_logos)}")
            for logo in self.failed_logos:
                print(f"   • {logo['client_name']}: {logo['error'][:100]}...")
        
        # Generate client mappings
        mappings = self.generate_client_mappings()
        if mappings:
            print(f"\n🔗 Generated Client Mappings:")
            for client_id, lora_name in mappings.items():
                print(f"   \"{client_id}\": \"{lora_name}\",")
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Update ai_service.py with new client mappings")
        print(f"2. Validate training data: python scripts/validate_training_data.py")
        print(f"3. Train LoRAs for each client")
        print(f"4. Test API integration")

def main():
    parser = argparse.ArgumentParser(description="Batch process client logos")
    parser.add_argument("--logo-dir", required=True, help="Directory containing logo files")
    parser.add_argument("--variations", type=int, default=25, help="Variations per logo")
    parser.add_argument("--patterns", nargs="+", default=["*.png", "*.jpg", "*.jpeg"], 
                       help="File patterns to match")
    
    args = parser.parse_args()
    
    print("🎨 Batch Logo Processing for LoRA Training")
    print("=" * 50)
    
    # Initialize processor
    processor = BatchLogoProcessor(variations_per_logo=args.variations)
    
    # Process all logos
    results = processor.process_directory(args.logo_dir, args.patterns)
    
    # Print summary
    processor.print_summary()
    
    return 0

if __name__ == "__main__":
    exit(main())