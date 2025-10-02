from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid

from ..services.storage_service import StorageService
from ..core.logging import setup_logging

router = APIRouter()
logger = setup_logging()

class ImageMetadata(BaseModel):
    id: str
    filename: str
    url: str
    size: str
    title: Optional[str] = None
    subtitle: Optional[str] = None
    client_id: Optional[str] = None
    created_at: str

class UploadResponse(BaseModel):
    filename: str
    url: str
    message: str

@router.get("/images", response_model=List[ImageMetadata])
async def list_images(limit: int = 50, offset: int = 0, client_id: Optional[str] = None):
    """
    List generated cover images with metadata
    """
    try:
        storage_service = StorageService()
        images = await storage_service.list_images(
            limit=limit,
            offset=offset,
            client_id=client_id
        )
        
        return images
        
    except Exception as e:
        logger.error(f"Error listing images: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list images")

@router.post("/upload-watermark", response_model=UploadResponse)
async def upload_watermark(file: UploadFile = File(...)):
    """
    Upload watermark file (PNG/SVG)
    """
    if not file.content_type in ["image/png", "image/svg+xml"]:
        raise HTTPException(
            status_code=400, 
            detail="Only PNG and SVG files are allowed for watermarks"
        )
    
    try:
        storage_service = StorageService()
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"watermark_{uuid.uuid4()}.{file_extension}"
        
        # Upload to watermarks bucket
        url = await storage_service.upload_watermark(
            file_data=await file.read(),
            filename=unique_filename,
            content_type=file.content_type
        )
        
        return UploadResponse(
            filename=unique_filename,
            url=url,
            message="Watermark uploaded successfully"
        )
        
    except Exception as e:
        logger.error(f"Error uploading watermark: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload watermark")

@router.delete("/image/{image_id}")
async def delete_image(image_id: str):
    """
    Delete a generated image
    """
    try:
        storage_service = StorageService()
        success = await storage_service.delete_image(image_id)
        
        if success:
            return {"message": "Image deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
            
    except Exception as e:
        logger.error(f"Error deleting image {image_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete image")

@router.get("/logos")
async def list_available_logos():
    """
    List available LoRA models for logo generation
    """
    try:
        storage_service = StorageService()
        logos = await storage_service.list_available_logos()
        
        return {
            "logos": logos,
            "count": len(logos)
        }
        
    except Exception as e:
        logger.error(f"Error listing logos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list available logos")

@router.post("/backup")
async def backup_images():
    """
    Backup all generated images (admin endpoint)
    """
    try:
        storage_service = StorageService()
        backup_url = await storage_service.create_backup()
        
        return {
            "backup_url": backup_url,
            "message": "Backup created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create backup")

@router.get("/stats")
async def get_storage_stats():
    """
    Get storage usage statistics
    """
    try:
        storage_service = StorageService()
        stats = await storage_service.get_storage_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get storage statistics")