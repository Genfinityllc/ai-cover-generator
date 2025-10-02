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
    """Health check endpoint with system information"""
    
    # Check Metal/MPS availability on macOS
    metal_available = torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False
    
    # Memory information
    memory_info = {}
    if metal_available and hasattr(torch, 'mps'):
        try:
            memory_info = {
                "metal_available": True,
                "device": "mps"
            }
        except:
            memory_info = {"metal_available": False, "device": "cpu"}
    else:
        memory_info = {"metal_available": False, "device": "cpu"}
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        platform=platform.platform(),
        metal_available=metal_available,
        torch_version=torch.__version__,
        memory_info=memory_info
    )

@router.get("/models")
async def models_status():
    """Check if AI models are loaded and ready"""
    from ..services.ai_service import AIService
    
    ai_service = AIService()
    status = await ai_service.get_status()
    
    return {
        "sdxl_loaded": status.get("sdxl_loaded", False),
        "lora_models_count": status.get("lora_models_count", 0),
        "device": status.get("device", "unknown"),
        "memory_usage": status.get("memory_usage", {})
    }