from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from .routers import generate, health, storage
from .core.config import settings
from .core.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="AI Cover Image Generator",
    description="Generate cover images for crypto news articles using Stable Diffusion XL + LoRA",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(generate.router, prefix="/api/generate", tags=["generation"])
app.include_router(storage.router, prefix="/api/storage", tags=["storage"])

# Serve static files (generated images for preview)
if os.path.exists("./temp_images"):
    app.mount("/temp", StaticFiles(directory="./temp_images"), name="temp")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup - Non-blocking for Railway health checks"""
    logger.info("🚀 Starting AI Cover Image Generator API")
    
    try:
        # Initialize storage service first (lightweight)
        from .services.storage_service import StorageService
        storage_service = StorageService()
        await storage_service.initialize()
        
        logger.info("✅ Storage service initialized")
        
        # Initialize AI model in background (heavy operation)
        # Don't block startup for Railway health checks
        import asyncio
        asyncio.create_task(initialize_ai_models())
        
        logger.info("✅ API started - AI models initializing in background")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
        # Don't fail startup - let health check handle it

async def initialize_ai_models():
    """Initialize AI models in background"""
    try:
        logger.info("🧠 Initializing AI models...")
        
        from .services.ai_service import AIService
        ai_service = AIService()
        await ai_service.initialize()
        
        logger.info("✅ AI models initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ AI model initialization failed: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down AI Cover Image Generator API")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )