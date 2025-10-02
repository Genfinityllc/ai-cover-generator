# 🎨 **LoRA Training Guide - Step by Step**

This guide will walk you through training LoRA models for crypto logos on your Mac Studio.

## 🚀 **Quick Start (5 Minutes)**

### **Step 1: Setup Training Environment**
```bash
cd ai-cover-generator
python3 scripts/setup_lora_training.py
```

### **Step 2: Create Sample Training Data**
```bash
python3 scripts/collect_sample_images.py
```

### **Step 3: Validate Your Data**
```bash
python3 scripts/validate_training_data.py
```

### **Step 4: Train Your First LoRA**
```bash
python3 scripts/train_lora_simple.py --logo-name bitcoin --epochs 50
```

---

## 📚 **Detailed Training Process**

### **Phase 1: Prepare Training Data** 📁

#### **1.1 Collect Logo Images**
For each crypto logo you want to train, collect **20-30 high-quality images**:

```
training_data/
├── bitcoin/           # 20-30 Bitcoin logo variations
├── ethereum/          # 20-30 Ethereum logo variations
├── binance/           # 20-30 Binance logo variations
└── your_client/       # 20-30 Your client's logo variations
```

#### **1.2 Image Requirements**
- **Format**: PNG or JPG
- **Resolution**: 512x512 minimum (1024x1024 preferred)
- **Variety**: Different backgrounds, sizes, lighting
- **Quality**: Clean, professional logos

#### **1.3 Where to Find Images**
1. **Official Sources**:
   - Company press kits
   - Brand guideline PDFs
   - Official websites
   - Marketing materials

2. **Create Variations**:
   ```bash
   # Use this helper to create background variations
   python3 scripts/create_logo_variations.py --input logo.png --output-dir training_data/bitcoin/
   ```

#### **1.4 Validate Your Dataset**
```bash
python3 scripts/validate_training_data.py --data-dir training_data
```

**Expected output:**
```
✅ No major issues found!
Total logos: 4
Total images: 95
Average per logo: 23.8
🚀 Ready to start LoRA training!
```

---

### **Phase 2: Configure Training** ⚙️

#### **2.1 Training Parameters**

| Parameter | Recommended | Description |
|-----------|-------------|-------------|
| **Epochs** | 50-200 | More epochs = better quality |
| **Learning Rate** | 1e-4 | Default works well |
| **Rank** | 64 | Higher = more detailed but larger file |
| **Batch Size** | 1 | Optimal for Mac Studio |

#### **2.2 Mac Studio Optimization**
The training is optimized for Mac Studio Metal acceleration:
- **Memory Efficient**: Uses gradient checkpointing
- **Metal Backend**: Leverages Apple Silicon GPU  
- **Mixed Precision**: FP16 for faster training

---

### **Phase 3: Training Process** 🎯

#### **3.1 Train Individual LoRAs**
```bash
# Train Bitcoin LoRA
python3 scripts/train_lora_simple.py \
  --logo-name bitcoin \
  --epochs 100 \
  --learning-rate 1e-4 \
  --rank 64

# Train Ethereum LoRA  
python3 scripts/train_lora_simple.py \
  --logo-name ethereum \
  --epochs 100
```

#### **3.2 Training Output**
```
🎨 Starting LoRA training for: bitcoin
🔄 Loading SDXL model: stabilityai/stable-diffusion-xl-base-1.0
✅ Model loaded on device: mps
🔧 Setting up LoRA layers with rank 64
📸 Found 23 training images for bitcoin
🔄 Training for 100 epochs...
   Epoch 0/100: Loss = 0.1234
   Epoch 20/100: Loss = 0.0987
   ...
✅ LoRA training complete for bitcoin
📁 Saved to: ./models/lora/bitcoin_lora.safetensors
```

#### **3.3 Training Time Estimates**
- **Mac Studio M1 Max**: ~15-30 minutes per 100 epochs
- **Mac Studio M2 Ultra**: ~10-20 minutes per 100 epochs
- **Memory Usage**: ~12-16GB during training

---

### **Phase 4: Testing Your LoRAs** 🧪

#### **4.1 Test Individual LoRA**
```bash
python3 scripts/test_lora.py \
  --lora-path ./models/lora/bitcoin_lora.safetensors \
  --prompt "professional bitcoin logo on white background"
```

#### **4.2 Test in Main API**
```bash
# Start the API
./start.sh

# Test with client_id
curl -X POST "http://localhost:8000/api/generate/cover" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bitcoin Breaks $100K",
    "subtitle": "Historic milestone reached",
    "client_id": "bitcoin",
    "size": "1800x900"
  }'
```

---

### **Phase 5: Production Deployment** 🚀

#### **5.1 Upload LoRAs to Production**
```bash
# Copy LoRAs to deployment
scp ./models/lora/*.safetensors your-server:/app/models/lora/

# Or include in Docker build
COPY models/lora/ /app/models/lora/
```

#### **5.2 Client Mapping**
Update the client-to-LoRA mapping in your API:

```python
# In ai_service.py
async def _get_lora_for_client(self, client_id: str) -> Optional[str]:
    client_lora_map = {
        "bitcoin": "bitcoin_lora",
        "ethereum": "ethereum_lora", 
        "binance": "binance_lora",
        "coinbase": "coinbase_lora",
        "your_client": "your_client_lora"
    }
    return client_lora_map.get(client_id.lower())
```

---

## 🔧 **Advanced Training Tips**

### **Improve Training Quality**

1. **More Data**: 50+ images per logo gives better results
2. **Data Augmentation**: Rotate, scale, color-adjust existing images
3. **Regularization**: Add general crypto images to prevent overfitting
4. **Higher Resolution**: Train on 1024x1024 for better detail

### **Troubleshooting Common Issues**

#### **"Out of Memory" Error**
```bash
# Reduce batch size or use CPU offloading
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
```

#### **Poor Logo Recognition**
- Collect more varied training images
- Increase training epochs (200-500)
- Check image quality and backgrounds

#### **Training Too Slow**
- Ensure Metal acceleration is enabled
- Close other GPU-intensive apps
- Use smaller batch size

### **Using Kohya Trainer (Advanced)**

For production-quality LoRAs, use the full Kohya trainer:

```bash
# Setup (one time)
git clone https://github.com/kohya-ss/sd-scripts.git external/kohya-ss
cd external/kohya-ss
pip install -r requirements.txt

# Prepare config
python3 ../../scripts/create_kohya_config.py --logo-name bitcoin

# Train with Kohya
python train_network.py --config_file ../../training_configs/bitcoin_config.toml
```

---

## 📊 **Training Results**

### **Expected Quality Levels**

| Epochs | Quality | Use Case |
|--------|---------|----------|
| 50 | Basic | Testing/prototyping |
| 100 | Good | Production ready |
| 200+ | Excellent | High-quality production |

### **File Sizes**
- **Rank 32**: ~25MB per LoRA
- **Rank 64**: ~50MB per LoRA  
- **Rank 128**: ~100MB per LoRA

---

## 🎯 **Next Steps**

1. **Start with samples**: Use the provided sample images to test the pipeline
2. **Collect real logos**: Replace samples with official brand assets
3. **Train systematically**: Train one logo at a time, test each
4. **Integrate with API**: Update client mappings and deploy
5. **Monitor results**: Check generation quality and adjust as needed

---

## 🆘 **Getting Help**

- **Validation fails**: Check image formats and count
- **Training errors**: Review Python/PyTorch installation
- **Poor results**: Increase training data or epochs
- **Memory issues**: Reduce batch size or use CPU offloading

**Happy training! 🎨✨**