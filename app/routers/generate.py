from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import asyncio

from ..models.requests import GenerateCoverRequest, ManualGenerateRequest
from ..services.ai_service import AIService
from ..services.storage_service import StorageService
from ..core.logging import setup_logging

router = APIRouter()
logger = setup_logging()

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    image_url: Optional[str] = None
    preview_url: Optional[str] = None
    message: str

# In-memory job tracking (use Redis in production)
generation_jobs: Dict[str, Dict[str, Any]] = {}

@router.post("/cover", response_model=GenerationResponse)
async def generate_cover(request: GenerateCoverRequest, background_tasks: BackgroundTasks):
    """
    Automated cover generation endpoint for integration with existing app
    """
    job_id = str(uuid.uuid4())
    
    # Initialize job tracking
    generation_jobs[job_id] = {
        "status": "queued",
        "request": request.dict(),
        "created_at": asyncio.get_event_loop().time()
    }
    
    # Queue background generation task
    background_tasks.add_task(process_cover_generation, job_id, request)
    
    return GenerationResponse(
        job_id=job_id,
        status="queued",
        message="Cover generation started. Check status with job_id."
    )

@router.post("/manual", response_model=GenerationResponse)
async def manual_generate(request: ManualGenerateRequest, background_tasks: BackgroundTasks):
    """
    Manual generation endpoint for web app workflow
    """
    job_id = str(uuid.uuid4())
    
    # Initialize job tracking
    generation_jobs[job_id] = {
        "status": "queued",
        "request": request.dict(),
        "created_at": asyncio.get_event_loop().time()
    }
    
    # Queue background generation task
    background_tasks.add_task(process_manual_generation, job_id, request)
    
    return GenerationResponse(
        job_id=job_id,
        status="queued",
        message="Manual generation started. Check status with job_id."
    )

@router.get("/status/{job_id}", response_model=GenerationResponse)
async def get_generation_status(job_id: str):
    """
    Get status of a generation job
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = generation_jobs[job_id]
    
    return GenerationResponse(
        job_id=job_id,
        status=job["status"],
        image_url=job.get("image_url"),
        preview_url=job.get("preview_url"),
        message=job.get("message", "")
    )

@router.get("/preview/{job_id}")
async def get_preview(job_id: str):
    """
    Get preview of generated image
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = generation_jobs[job_id]
    
    if job["status"] != "completed" or not job.get("preview_url"):
        raise HTTPException(status_code=404, detail="Preview not ready")
    
    # Return preview image (implement actual file serving)
    return {"preview_url": job["preview_url"]}

async def process_cover_generation(job_id: str, request: GenerateCoverRequest):
    """
    Background task for automated cover generation
    """
    try:
        # Update status
        generation_jobs[job_id]["status"] = "processing"
        
        # Initialize services
        ai_service = AIService()
        storage_service = StorageService()
        
        # Generate image
        logger.info(f"Starting generation for job {job_id}")
        
        # Step 1: Generate background with SDXL + LoRA
        background_image = await ai_service.generate_background(
            client_id=request.client_id,
            prompt_enhancement=request.title
        )
        
        # Step 2: Add text overlay
        final_image = await ai_service.add_text_overlay(
            image=background_image,
            title=request.title,
            subtitle=request.subtitle,
            size=(request.width, request.height)
        )
        
        # Step 3: Upload to Supabase
        image_url = await storage_service.upload_image(
            image=final_image,
            filename=f"cover_{job_id}.png",
            metadata={
                "title": request.title,
                "subtitle": request.subtitle,
                "client_id": request.client_id,
                "size": request.size
            }
        )
        
        # Update job status
        generation_jobs[job_id].update({
            "status": "completed",
            "image_url": image_url,
            "message": "Cover generated successfully"
        })
        
        logger.info(f"Completed generation for job {job_id}")
        
    except Exception as e:
        logger.error(f"Error in generation job {job_id}: {str(e)}")
        generation_jobs[job_id].update({
            "status": "failed",
            "message": f"Generation failed: {str(e)}"
        })

async def process_manual_generation(job_id: str, request: ManualGenerateRequest):
    """
    Background task for manual generation workflow
    """
    try:
        # Update status
        generation_jobs[job_id]["status"] = "processing"
        
        # Initialize services
        ai_service = AIService()
        storage_service = StorageService()
        
        # Generate image with manual parameters
        logger.info(f"Starting manual generation for job {job_id}")
        
        # Step 1: Generate background
        background_image = await ai_service.generate_background(
            lora_models=request.selected_logos,
            custom_prompt=request.custom_prompt,
            style_params=request.style_parameters
        )
        
        # Step 2: Add text overlay
        image_with_text = await ai_service.add_text_overlay(
            image=background_image,
            title=request.title,
            subtitle=request.subtitle,
            size=(request.width, request.height),
            text_style=request.text_style
        )
        
        # Step 3: Add watermark if provided
        final_image = image_with_text
        if request.watermark_data:
            final_image = await ai_service.add_watermark(
                image=image_with_text,
                watermark_data=request.watermark_data,
                position=request.watermark_position
            )
        
        # Step 4: Save preview (temporary)
        preview_url = await storage_service.save_preview(
            image=final_image,
            job_id=job_id
        )
        
        # Update job status with preview
        generation_jobs[job_id].update({
            "status": "preview_ready",
            "preview_url": preview_url,
            "message": "Preview ready for approval"
        })
        
        logger.info(f"Preview ready for job {job_id}")
        
    except Exception as e:
        logger.error(f"Error in manual generation job {job_id}: {str(e)}")
        generation_jobs[job_id].update({
            "status": "failed",
            "message": f"Generation failed: {str(e)}"
        })

@router.post("/approve/{job_id}")
async def approve_generation(job_id: str):
    """
    Approve manual generation and save to final storage
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = generation_jobs[job_id]
    
    if job["status"] != "preview_ready":
        raise HTTPException(status_code=400, detail="No preview ready for approval")
    
    try:
        storage_service = StorageService()
        
        # Move from preview to final storage
        final_url = await storage_service.finalize_image(job_id)
        
        # Update job status
        generation_jobs[job_id].update({
            "status": "completed",
            "image_url": final_url,
            "message": "Image approved and saved"
        })
        
        return GenerationResponse(
            job_id=job_id,
            status="completed",
            image_url=final_url,
            message="Image approved and saved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve image: {str(e)}")

@router.delete("/job/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a generation job
    """
    if job_id not in generation_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = generation_jobs[job_id]
    
    if job["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed job")
    
    # Mark as cancelled
    generation_jobs[job_id]["status"] = "cancelled"
    
    return {"message": "Job cancelled successfully"}