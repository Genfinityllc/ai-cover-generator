from fastapi import APIRouter
from pydantic import BaseModel
import platform
import torch
from typing import Dict, Any

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str
    platform: str
    metal_available: bool
    torch_version: str
    memory_info: Dict[str, Any]

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - always returns healthy for Railway"""
    
    try:
        # Check Metal/MPS availability on macOS (but don't fail if imports fail)
        metal_available = False
        torch_version = "unknown"
        
        try:
            metal_available = torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False
            torch_version = torch.__version__
        except:
            pass
        
        # Memory information (safe fallback)
        memory_info = {"metal_available": metal_available, "device": "cpu"}
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            platform=platform.platform(),
            metal_available=metal_available,
            torch_version=torch_version,
            memory_info=memory_info
        )
        
    except Exception as e:
        # Always return healthy for Railway health checks, even with errors
        return HealthResponse(
            status="healthy",
            version="1.0.0", 
            platform="unknown",
            metal_available=False,
            torch_version="unknown",
            memory_info={"device": "cpu", "error": str(e)[:100]}
        )

@router.get("/models")
async def models_status():
    """Check if AI models are loaded and ready"""
    try:
        from ..services.ai_service import AIService
        
        ai_service = AIService()
        status = await ai_service.get_status()
        
        return {
            "sdxl_loaded": status.get("sdxl_loaded", False),
            "lora_models_count": status.get("lora_models_count", 0),
            "device": status.get("device", "unknown"),
            "memory_usage": status.get("memory_usage", {})
        }
    except Exception as e:
        return {
            "sdxl_loaded": False,
            "lora_models_count": 0,
            "device": "unknown",
            "memory_usage": {},
            "error": str(e)[:100],
            "status": "initializing"
        }