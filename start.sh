#!/bin/bash

# AI Cover Image Generator - Startup Script
echo "🚀 Starting AI Cover Image Generator"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📋 Copying .env.example to .env..."
    cp .env.example .env
    echo "✏️  Please edit .env with your Supabase credentials before proceeding."
    echo "📖 See README.md for configuration details."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p models/cache
mkdir -p models/lora
mkdir -p temp_images
mkdir -p storage

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" < "3.10" ]]; then
    echo "⚠️  Warning: Python 3.10+ recommended for best compatibility"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check Metal/MPS availability (on macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🖥️  Checking Metal acceleration..."
    python3 -c "
import torch
print(f'🔧 PyTorch version: {torch.__version__}')
if hasattr(torch.backends, 'mps'):
    print(f'⚡ Metal acceleration: {torch.backends.mps.is_available()}')
else:
    print('❌ Metal acceleration: Not available (PyTorch too old)')
"
fi

# Test configuration
echo "🧪 Testing configuration..."
python3 -c "
try:
    from app.core.config import settings
    print('✅ Configuration loaded successfully')
    print(f'📁 Model cache: {settings.MODEL_CACHE_DIR}')
    print(f'🎨 LoRA models: {settings.LORA_MODELS_DIR}')
    print(f'🖼️  Image size: {settings.IMAGE_WIDTH}x{settings.IMAGE_HEIGHT}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"

# Start the server
echo ""
echo "🚀 Starting FastAPI server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "📖 API documentation: http://localhost:8000/docs"
echo "🏥 Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start uvicorn server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload