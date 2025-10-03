from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ImageSize(str, Enum):
    STANDARD = "1800x900"
    HD = "1920x1080"

class WatermarkPosition(str, Enum):
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    CENTER = "center"

class GenerateCoverRequest(BaseModel):
    """Request model for automated cover generation"""
    title: str = Field(..., description="Article title")
    subtitle: Optional[str] = Field(None, description="Article subtitle")
    client_id: Optional[str] = Field(None, description="Client ID for LoRA selection")
    size: ImageSize = Field(ImageSize.STANDARD, description="Image size")
    
    # Computed properties for compatibility
    @property
    def width(self) -> int:
        return 1920 if self.size == ImageSize.HD else 1800
    
    @property
    def height(self) -> int:
        return 1080 if self.size == ImageSize.HD else 900

class ManualGenerateRequest(BaseModel):
    """Request model for manual generation workflow"""
    title: str = Field(..., description="Image title")
    subtitle: Optional[str] = Field(None, description="Image subtitle")
    selected_logos: List[str] = Field(default=[], description="Selected LoRA models")
    custom_prompt: Optional[str] = Field(None, description="Custom generation prompt")
    watermark_data: Optional[bytes] = Field(None, description="Watermark image data")
    watermark_position: WatermarkPosition = Field(WatermarkPosition.BOTTOM_RIGHT, description="Watermark position")
    size: ImageSize = Field(ImageSize.STANDARD, description="Image size")
    
    # Style parameters
    style_parameters: Optional[Dict[str, Any]] = Field(default={}, description="Generation parameters")
    text_style: Optional[Dict[str, Any]] = Field(default={}, description="Text overlay style")
    
    # Computed properties
    @property
    def width(self) -> int:
        return 1920 if self.size == ImageSize.HD else 1800
    
    @property
    def height(self) -> int:
        return 1080 if self.size == ImageSize.HD else 900

class GenerateImageResponse(BaseModel):
    """Response model for image generation"""
    success: bool
    image_url: str
    image_id: str
    generation_time: float
    parameters: Dict[str, Any]
    error: Optional[str] = None

class BatchGenerateRequest(BaseModel):
    """Request model for batch generation"""
    requests: List[GenerateCoverRequest] = Field(..., max_items=10)
    
class BatchGenerateResponse(BaseModel):
    """Response model for batch generation"""
    success: bool
    results: List[GenerateImageResponse]
    total_time: float
    failed_count: int

class ImageMetadata(BaseModel):
    """Metadata for generated images"""
    image_id: str
    title: str
    style: str
    brand_logo: Optional[str]
    generation_params: Dict[str, Any]
    created_at: str
    file_size: int
    dimensions: Dict[str, int]