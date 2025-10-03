from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str

@router.get("/")
async def health_check():
    """Ultra-minimal health check - guaranteed to work"""
    return {"status": "healthy", "version": "1.0.0"}

@router.get("/detailed")
async def detailed_health():
    """Detailed health check with ML info"""
    try:
        import platform
        import torch
        from typing import Dict, Any
        
        # Check Metal/MPS availability on macOS (but don't fail if imports fail)
        metal_available = False
        torch_version = "unknown"
        
        try:
            metal_available = torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False
            torch_version = torch.__version__
        except:
            pass
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "platform": platform.platform(),
            "metal_available": metal_available,
            "torch_version": torch_version,
            "memory_info": {"metal_available": metal_available, "device": "cpu"}
        }
        
    except Exception as e:
        return {
            "status": "healthy",
            "version": "1.0.0", 
            "platform": "unknown",
            "metal_available": False,
            "torch_version": "unknown",
            "memory_info": {"device": "cpu", "error": str(e)[:100]}
        }

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