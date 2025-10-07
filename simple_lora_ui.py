#!/usr/bin/env python3
"""
Simple LoRA Training Interface
Command-line menu system for easy model training and testing
"""
import os
import json
from production_cover_generator import ProductionCoverGenerator

class SimpleLoRAInterface:
    def __init__(self):
        self.generator = None
        
    def setup_generator(self):
        """Initialize generator on first use"""
        if self.generator is None:
            print("🔄 Initializing AI system...")
            self.generator = ProductionCoverGenerator()
            print("✅ Ready!")
    
    def main_menu(self):
        """Main interface menu"""
        while True:
            print("\n" + "="*50)
            print("🎨 LoRA Training & Testing Studio")
            print("="*50)
            print("1. 🖼️  Generate Single Cover")
            print("2. 📚 Batch Generate Covers")
            print("3. 🧪 Test Different Styles")
            print("4. 📊 Train Custom Style")
            print("5. 📁 Manage Training Data")
            print("6. ⚙️  System Status")
            print("7. 🚪 Exit")
            
            choice = input("\n📝 Enter choice (1-7): ").strip()
            
            if choice == "1":
                self.generate_single_cover()
            elif choice == "2":
                self.batch_generate_menu()
            elif choice == "3":
                self.test_styles_menu()
            elif choice == "4":
                self.train_custom_style()
            elif choice == "5":
                self.manage_training_data()
            elif choice == "6":
                self.system_status()
            elif choice == "7":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def generate_single_cover(self):
        """Generate a single article cover"""
        self.setup_generator()
        
        print("\n🖼️  Generate Single Cover")
        print("-" * 30)
        
        title = input("📰 Article title: ").strip()
        subtitle = input("📝 Subtitle (optional): ").strip()
        
        print("\n🎨 Available styles:")
        print("1. Dark (cyberpunk/tech)")
        print("2. Colorful (cosmic/space)")
        print("3. Light (corporate/clean)")
        
        style_choice = input("Style choice (1-3): ").strip()
        style_map = {"1": "dark", "2": "colorful", "3": "light"}
        style = style_map.get(style_choice, "dark")
        
        print("\n🏢 Company integration:")
        print("1. None")
        print("2. Hedera")
        print("3. Bitcoin")
        print("4. Custom")
        
        company_choice = input("Company choice (1-4): ").strip()
        company_map = {"1": "", "2": "hedera", "3": "bitcoin", "4": "custom"}
        company = company_map.get(company_choice, "")
        
        if company == "custom":
            company = input("Enter company name: ").strip()
        
        print(f"\n🎯 Generating cover...")
        print(f"   Title: {title}")
        print(f"   Style: {style}")
        print(f"   Company: {company or 'None'}")
        
        cover = self.generator.generate_article_cover(
            title=title,
            subtitle=subtitle,
            style=style,
            company_logo=company
        )
        
        if cover:
            filename = f"style_outputs/single_cover_{style}.png"
            os.makedirs("style_outputs", exist_ok=True)
            cover.save(filename)
            print(f"✅ Cover saved: {filename}")
        
        input("\n📱 Press Enter to continue...")
    
    def batch_generate_menu(self):
        """Batch generation options"""
        print("\n📚 Batch Generate Covers")
        print("-" * 30)
        print("1. Use test articles (included)")
        print("2. Load custom JSON file")
        print("3. Create quick batch")
        
        choice = input("Choice (1-3): ").strip()
        
        if choice == "1":
            self.run_test_batch()
        elif choice == "2":
            self.load_custom_batch()
        elif choice == "3":
            self.create_quick_batch()
    
    def run_test_batch(self):
        """Run batch with test articles"""
        self.setup_generator()
        
        if os.path.exists("test_articles.json"):
            with open("test_articles.json", 'r') as f:
                articles = json.load(f)
            
            print(f"\n🧪 Running test batch with {len(articles)} articles...")
            
            style = input("Style (dark/colorful/light) [dark]: ").strip() or "dark"
            
            self.generator.batch_generate(articles, style, "batch_output")
        else:
            print("❌ test_articles.json not found")
        
        input("\n📱 Press Enter to continue...")
    
    def test_styles_menu(self):
        """Test different styles with same content"""
        self.setup_generator()
        
        print("\n🧪 Test Different Styles")
        print("-" * 30)
        
        title = input("Test title [Crypto Innovation]: ").strip() or "Crypto Innovation"
        
        styles = ["dark", "colorful", "light"]
        
        print(f"\n🎨 Generating {title} in all styles...")
        
        for style in styles:
            print(f"   🔄 Generating {style} style...")
            cover = self.generator.generate_article_cover(
                title=title,
                style=style
            )
            
            if cover:
                filename = f"style_outputs/test_{style}_style.png"
                os.makedirs("style_outputs", exist_ok=True)
                cover.save(filename)
                print(f"   ✅ {style} saved")
        
        print("🎉 Style comparison complete! Check style_outputs/")
        input("\n📱 Press Enter to continue...")
    
    def train_custom_style(self):
        """Custom style training interface"""
        print("\n📊 Train Custom Style")
        print("-" * 30)
        print("This feature will be implemented with your training images.")
        print("For now, you can:")
        print("1. Add images to training_data/[style_name]_style/")
        print("2. Use the production generator with custom prompts")
        print("3. Test different prompt combinations")
        
        custom_prompt = input("\n🎨 Test custom prompt (optional): ").strip()
        
        if custom_prompt:
            self.setup_generator()
            title = input("Test title: ").strip() or "Custom Style Test"
            
            cover = self.generator.generate_article_cover(
                title=title,
                custom_prompt=custom_prompt
            )
            
            if cover:
                filename = "style_outputs/custom_test.png"
                cover.save(filename)
                print(f"✅ Custom test saved: {filename}")
        
        input("\n📱 Press Enter to continue...")
    
    def manage_training_data(self):
        """Training data management"""
        print("\n📁 Manage Training Data")
        print("-" * 30)
        
        training_dir = "training_data"
        
        if os.path.exists(training_dir):
            styles = [d for d in os.listdir(training_dir) if os.path.isdir(os.path.join(training_dir, d))]
            print(f"Found {len(styles)} style directories:")
            for style in styles:
                style_path = os.path.join(training_dir, style)
                images = [f for f in os.listdir(style_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                print(f"   📁 {style}: {len(images)} images")
        else:
            print("No training_data directory found.")
            print("Create training_data/[style_name]_style/ directories")
            print("Add your reference images to train custom styles")
        
        input("\n📱 Press Enter to continue...")
    
    def system_status(self):
        """Show system status"""
        print("\n⚙️  System Status")
        print("-" * 30)
        
        # Check dependencies
        try:
            import torch
            device = "mps" if torch.backends.mps.is_available() else "cpu"
            print(f"🖥️  Device: {device}")
        except:
            print("❌ PyTorch not available")
        
        try:
            from diffusers import StableDiffusionXLPipeline
            print("✅ Diffusers available")
        except:
            print("❌ Diffusers not available")
        
        # Check watermark
        watermark_path = "/Users/valorkopeny/Desktop/genfinity-watermark.png"
        if os.path.exists(watermark_path):
            print("✅ Genfinity watermark found")
        else:
            print("⚠️  Watermark not found")
        
        # Check output directories
        if os.path.exists("style_outputs"):
            files = os.listdir("style_outputs")
            print(f"📁 style_outputs: {len(files)} files")
        else:
            print("📁 style_outputs: Not created yet")
        
        input("\n📱 Press Enter to continue...")
    
    def create_quick_batch(self):
        """Create a quick batch interactively"""
        print("\n⚡ Create Quick Batch")
        print("-" * 30)
        
        articles = []
        
        while True:
            title = input(f"\nArticle {len(articles) + 1} title (or 'done'): ").strip()
            if title.lower() == 'done':
                break
            
            subtitle = input("Subtitle (optional): ").strip()
            company = input("Company (optional): ").strip()
            
            articles.append({
                "title": title,
                "subtitle": subtitle,
                "company": company
            })
        
        if articles:
            self.setup_generator()
            style = input("Style (dark/colorful/light) [dark]: ").strip() or "dark"
            
            print(f"\n🚀 Generating {len(articles)} covers...")
            self.generator.batch_generate(articles, style, "quick_batch_output")
        
        input("\n📱 Press Enter to continue...")

def main():
    interface = SimpleLoRAInterface()
    
    print("🎨 Welcome to LoRA Training & Testing Studio!")
    print("This tool helps you generate AI covers and train custom styles.")
    
    try:
        interface.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()