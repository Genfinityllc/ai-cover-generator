# 🎨 **Logo Collection & Training Guide**

This guide shows you how to collect 1 high-quality logo and automatically generate 25+ training variations.

---

## 🚀 **Quick Start (5 Minutes)**

### **Step 1: Get 1 High-Quality Logo**
Download the official logo for the crypto/brand you want to train:

- **Bitcoin**: https://bitcoin.org/img/logos/logotype-white.png
- **Ethereum**: https://ethereum.org/static/assets/ethereum-logo.png  
- **Binance**: Search "Binance official logo PNG"
- **Your Client**: Get from their website or press kit

### **Step 2: Generate 25 Training Variations**
```bash
# Example: Generate Bitcoin training variations
python3 scripts/generate_logo_variations.py \
  --input /path/to/bitcoin-logo.png \
  --output-dir training_data/bitcoin \
  --count 25
```

### **Step 3: Validate & Train**
```bash
# Check if training data is ready
python3 scripts/validate_training_data.py

# Train the LoRA
python3 scripts/train_lora_simple.py --logo-name bitcoin --epochs 100
```

---

## 📋 **Detailed Collection Process**

### **🔍 Finding Official Logos**

| Brand | Official Source | Best Format |
|-------|----------------|-------------|
| **Bitcoin** | bitcoin.org/en/press-kit | SVG/PNG |
| **Ethereum** | ethereum.org/en/assets | SVG/PNG |
| **Binance** | binance.com → About → Brand Assets | PNG |
| **Coinbase** | coinbase.com → Press | SVG |
| **Cardano** | cardano.org/brand-assets | SVG |
| **Solana** | solana.com/branding | SVG/PNG |

### **📥 Download Tips**

1. **Look for "Press Kit" or "Brand Assets"** on official websites
2. **Download the highest resolution** available
3. **Prefer PNG or SVG** formats
4. **Get transparent background** versions when possible
5. **Download both symbol-only and logo+text** versions

---

## 🤖 **Using the Logo Variation Generator**

### **Basic Usage**
```bash
python3 scripts/generate_logo_variations.py \
  --input your_logo.png \
  --output-dir training_data/your_brand \
  --count 25
```

### **Advanced Options**
```bash
# Generate 30 variations at 1024x1024 resolution
python3 scripts/generate_logo_variations.py \
  --input ethereum-logo.png \
  --output-dir training_data/ethereum \
  --count 30 \
  --size 1024x1024
```

### **What the Generator Creates**

The script automatically generates variations with:

✅ **Different Backgrounds**:
- Solid colors (white, black, gray)
- Gradients (subtle)
- Crypto-themed colors (orange, blue)
- Textured/noise backgrounds

✅ **Different Logo Sizes**:
- 30%-80% of background size
- Maintains aspect ratio
- Various positioning

✅ **Different Positions**:
- Centered (most common)
- Corner positions
- Random placements

✅ **Different Effects**:
- Brightness adjustments
- Contrast variations  
- Subtle blur/sharpen
- Color enhancements

---

## 📁 **File Organization**

### **Recommended Structure**
```
training_data/
├── bitcoin/           # 25+ Bitcoin logo variations
├── ethereum/          # 25+ Ethereum logo variations
├── binance/           # 25+ Binance logo variations
├── coinbase/          # 25+ Coinbase logo variations
├── your_client_1/     # 25+ Your client's logo variations
└── your_client_2/     # 25+ Another client's logo variations
```

### **Naming Convention**
The generator automatically creates files like:
```
bitcoin/
├── variation_01.png
├── variation_02.png
├── variation_03.png
...
└── variation_25.png
```

---

## 🎯 **Complete Workflow Example**

### **Example: Setting up Bitcoin Training**

**1. Download Bitcoin Logo**
```bash
# Download official Bitcoin logo
curl -o bitcoin-logo.png "https://bitcoin.org/img/logos/logotype-white.png"
```

**2. Generate Variations**
```bash
# Create 25 training variations
python3 scripts/generate_logo_variations.py \
  --input bitcoin-logo.png \
  --output-dir training_data/bitcoin \
  --count 25
```

**3. Validate Dataset**
```bash
# Check training data quality
python3 scripts/validate_training_data.py
```

**Expected Output:**
```
✅ Bitcoin: 25 images
✅ Good image count: 25
✅ All images valid
🚀 Ready to start LoRA training!
```

**4. Train LoRA**
```bash
# Train Bitcoin LoRA (takes 15-30 minutes)
python3 scripts/train_lora_simple.py \
  --logo-name bitcoin \
  --epochs 100 \
  --learning-rate 1e-4
```

**5. Test Results**
```bash
# Test the trained LoRA
python3 scripts/test_lora.py \
  --lora-path models/lora/bitcoin_lora.safetensors \
  --prompt "professional bitcoin logo on clean background"
```

---

## 📊 **Quality Guidelines**

### **Input Logo Requirements**
- **Resolution**: 256x256 minimum (512x512+ preferred)
- **Format**: PNG with transparency, or high-quality JPG
- **Quality**: Clean, official logos (not screenshots)
- **Background**: Transparent preferred, solid color acceptable

### **Generated Variation Quality**
- **Count**: 25+ variations per logo
- **Diversity**: Different backgrounds, sizes, positions
- **Resolution**: 512x512 (configurable)
- **Format**: PNG with transparency support

### **Training Readiness Checklist**
- [ ] 25+ images per logo directory
- [ ] All images are 512x512 or larger
- [ ] Good variety in backgrounds
- [ ] Logo clearly visible in all variations
- [ ] No corrupted or duplicate images

---

## 🔧 **Troubleshooting**

### **"Logo too small" Error**
```bash
# Increase input logo resolution
# Use --size parameter for larger outputs
python3 scripts/generate_logo_variations.py \
  --input logo.png \
  --output-dir training_data/brand \
  --size 1024x1024
```

### **Poor Logo Visibility**
- Use higher contrast backgrounds
- Increase logo size in variations
- Ensure input logo has good quality

### **Not Enough Variations**
```bash
# Generate more variations
python3 scripts/generate_logo_variations.py \
  --input logo.png \
  --output-dir training_data/brand \
  --count 35  # More variations
```

### **Manual Additions**
After generating variations, you can manually add:
- Different logo orientations
- Logos with company text
- Logos on real backgrounds
- Hand-curated high-quality versions

---

## 🎨 **Multiple Logos Workflow**

### **Batch Processing Script**
```bash
#!/bin/bash
# Script to process multiple logos

LOGOS=(
    "bitcoin:bitcoin-logo.png"
    "ethereum:ethereum-logo.png"
    "binance:binance-logo.png"
    "coinbase:coinbase-logo.png"
)

for logo_info in "${LOGOS[@]}"; do
    IFS=':' read -r brand_name logo_file <<< "$logo_info"
    
    echo "Processing $brand_name..."
    python3 scripts/generate_logo_variations.py \
        --input logos/$logo_file \
        --output-dir training_data/$brand_name \
        --count 25
done

echo "All logos processed!"
```

---

## 🚀 **Production Tips**

### **For Best Results**
1. **Start with official logos** from company press kits
2. **Generate 25-30 variations** per logo
3. **Add 5-10 manual variations** for uniqueness
4. **Train with 100+ epochs** for production quality
5. **Test thoroughly** before deploying

### **Scaling to Many Clients**
1. **Create a logos/ directory** for original source files
2. **Use batch scripts** for processing multiple logos
3. **Standardize naming** for easy management
4. **Version control** your training data

### **Integration with API**
Once trained, your LoRAs work automatically:
```python
# Your app calls this, LoRA loads automatically
POST /api/generate/cover
{
  "title": "Bitcoin News",
  "client_id": "bitcoin"  # ← Loads bitcoin_lora.safetensors
}
```

---

## 🎯 **Next Steps**

1. **Collect 3-5 official logos** for your main clients
2. **Generate variations** using the script
3. **Train your first LoRA** with Bitcoin/Ethereum
4. **Test quality** and adjust parameters
5. **Scale up** to all your clients

**Ready to start collecting logos! 🎨✨**