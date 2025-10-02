# 🖼️ AI Cover Image Generator

A FastAPI-based service for generating cover images for crypto news articles using Stable Diffusion XL with LoRA fine-tuning support.

## 🚀 Features

- **Automated API workflow** - Generate covers directly from article metadata
- **Manual web workflow** - Interactive creation with preview and approval
- **LoRA fine-tuning** - Brand-specific logo integration  
- **Metal acceleration** - Optimized for Mac Studio M1/M2
- **Supabase storage** - Cloud storage and metadata management
- **Railway deployment** - Production-ready hosting

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   FastAPI API    │───▶│   Supabase      │
│   (News CMS)    │    │   (Generation)   │    │   (Storage)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Stable Diffusion │
                       │ XL + LoRA        │
                       │ (Mac Studio)     │
                       └──────────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.11+
- Mac Studio with Metal support (for local development)
- Supabase account
- Railway account (for deployment)

### Local Development

1. **Clone and setup**:
   ```bash
   cd ai-cover-generator
   pip install -r requirements.txt
   ```

2. **Environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Initialize directories**:
   ```bash
   mkdir -p models/{cache,lora} temp_images storage
   ```

4. **Run development server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🎯 API Endpoints

### Generation

- `POST /api/generate/cover` - Automated cover generation
- `POST /api/generate/manual` - Manual generation with preview
- `GET /api/generate/status/{job_id}` - Check generation status
- `POST /api/generate/approve/{job_id}` - Approve manual generation

### Storage

- `GET /api/storage/images` - List generated images
- `POST /api/storage/upload-watermark` - Upload watermark files
- `GET /api/storage/logos` - List available LoRA models

### Health

- `GET /health` - Service health check
- `GET /health/models` - AI models status

## 🔧 Usage Examples

### Automated Generation

```python
import httpx

response = httpx.post("http://localhost:8000/api/generate/cover", json={
    "title": "Bitcoin Reaches New All-Time High",
    "subtitle": "Historic milestone at $100,000",
    "client_id": "bitcoin_magazine",
    "size": "1800x900"
})

job_id = response.json()["job_id"]
```

### Manual Generation

```python
response = httpx.post("http://localhost:8000/api/generate/manual", json={
    "title": "Ethereum 2.0 Launch",
    "subtitle": "The merge is complete",
    "selected_logos": ["ethereum_logo"],
    "custom_prompt": "futuristic ethereum blockchain visualization",
    "size": "1920x1080"
})
```

## 🎨 LoRA Training

### Prepare Training Data

1. **Organize logos**:
   ```
   training_data/
   ├── bitcoin/
   │   ├── image1.png
   │   ├── image2.png
   │   └── ...
   ├── ethereum/
   │   ├── image1.png
   │   └── ...
   └── binance/
       └── ...
   ```

2. **Train LoRA models**:
   ```bash
   python scripts/train_lora.py --logo-dir ./training_data --output-dir ./models/lora
   ```

3. **Train specific logo**:
   ```bash
   python scripts/train_lora.py --logo-dir ./training_data --logo-name bitcoin
   ```

### Training Parameters

- **Rank**: 64 (adjustable for quality vs size)
- **Learning Rate**: 1e-4
- **Epochs**: 1000 (adjust based on data size)
- **Target Modules**: UNet attention layers

## 🚀 Deployment

### Railway Deployment

1. **Connect Repository**:
   - Link GitHub repository to Railway
   - Select `ai-cover-generator` subdirectory

2. **Environment Variables**:
   ```bash
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_key
   SUPABASE_STORAGE_BUCKET=cover-images
   # Add other required variables
   ```

3. **Deploy**:
   - Railway will automatically build using Dockerfile
   - Health check endpoint: `/health`

### Docker Deployment

```bash
# Build image
docker build -t ai-cover-generator .

# Run container
docker run -p 8000:8000 --env-file .env ai-cover-generator
```

## 🧪 Testing

### Test Generation Pipeline

```bash
python scripts/test_generation.py
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Generate test cover
curl -X POST http://localhost:8000/api/generate/cover \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Article", "subtitle": "Test subtitle"}'
```

## 📊 Performance

### Mac Studio M1/M2

- **Generation Time**: 15-30 seconds per image
- **Memory Usage**: ~8GB VRAM for SDXL
- **Batch Size**: 1 (optimal for Metal)
- **Image Quality**: High (1800×900, 1920×1080)

### Optimization Tips

1. **Enable Memory Efficiency**:
   ```python
   pipeline.enable_attention_slicing()
   pipeline.enable_model_cpu_offload()
   ```

2. **Use Float16**:
   ```python
   torch_dtype=torch.float16  # For Metal
   ```

3. **Cache Models**:
   - Set `MODEL_CACHE_DIR` to persistent storage
   - Preload models during startup

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `SUPABASE_URL` | Supabase project URL | Required |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key | Required |
| `MODEL_CACHE_DIR` | Model cache directory | `./models/cache` |
| `LORA_MODELS_DIR` | LoRA models directory | `./models/lora` |
| `USE_METAL` | Enable Metal acceleration | `true` |

### Image Generation Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `IMAGE_WIDTH` | Default image width | `1800` |
| `IMAGE_HEIGHT` | Default image height | `900` |
| `DEFAULT_STEPS` | Inference steps | `30` |
| `DEFAULT_GUIDANCE_SCALE` | CFG scale | `7.5` |
| `DEFAULT_LORA_WEIGHT` | LoRA weight | `0.8` |

## 🛠️ Troubleshooting

### Common Issues

1. **Metal/MPS not available**:
   ```bash
   # Check Metal support
   python -c "import torch; print(torch.backends.mps.is_available())"
   ```

2. **Model loading errors**:
   - Ensure sufficient disk space (20GB+ for SDXL)
   - Check Hugging Face token if using gated models

3. **Memory issues**:
   - Enable memory efficient attention
   - Reduce batch size to 1
   - Use CPU offloading

4. **Supabase connection**:
   - Verify credentials in `.env`
   - Check bucket permissions
   - Ensure service role key has storage access

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
uvicorn app.main:app --reload --log-level debug
```

## 📈 Monitoring

### Health Checks

- **API**: `GET /health`
- **Models**: `GET /health/models`
- **Storage**: `GET /api/storage/stats`

### Metrics

- Generation success rate
- Average generation time
- Storage usage
- Model loading status

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
- Create GitHub issue
- Check troubleshooting guide
- Review API documentation at `/docs`