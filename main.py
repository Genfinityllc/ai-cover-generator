#!/usr/bin/env python3
"""
LoRA AI Cover Generation Service - FIXED VERSION
FastAPI service for generating crypto news covers with client-specific branding
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LoRA AI Cover Generator",
    description="Generate cryptocurrency news covers with client-specific LoRA models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output directory exists
output_dir = Path("style_outputs")
output_dir.mkdir(exist_ok=True)

# Mount static files AFTER creating directory
app.mount("/images", StaticFiles(directory=str(output_dir)), name="images")

# Request models
class GenerateRequest(BaseModel):
    title: str
    subtitle: Optional[str] = None
    client_id: Optional[str] = "generic"
    article_content: Optional[str] = None
    style: Optional[str] = "professional"
    size: Optional[str] = "1792x896"

class GenerateResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    generation_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LoRA AI Cover Generator",
        "version": "1.0.0"
    }

@app.get("/status")
async def service_status():
    """Get service status and capabilities"""
    # Check if the main generator script exists
    generator_path = Path("boxed_subtitle_generator.py")
    
    return {
        "available": generator_path.exists(),
        "service": "LoRA AI Cover Generator",
        "python_version": sys.version,
        "generator_script": str(generator_path.absolute()),
        "output_directory": str(Path("style_outputs").absolute()),
        "supported_clients": [
            "hedera", "algorand", "constellation", 
            "bitcoin", "ethereum", "generic"
        ]
    }

@app.post("/generate", response_model=GenerateResponse)
async def generate_cover(request: GenerateRequest):
    """Generate a cover image using the LoRA AI system"""
    
    try:
        logger.info(f"🎨 Generating cover for: {request.title}")
        
        # Create temporary article file if content provided
        temp_article = None
        if request.article_content:
            temp_article = tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.txt', 
                delete=False
            )
            article_content = f"{request.title}\n\n{request.article_content}"
            temp_article.write(article_content)
            temp_article.close()
        
        # Use simple generator first, can switch to full ML later
        cmd_args = [
            sys.executable,  # Use current Python interpreter
            "simple_generator.py",
            "--title", request.title,
            "--client", request.client_id or "generic"
        ]
        
        # Add subtitle if provided
        if request.subtitle:
            cmd_args.extend(["--subtitle", request.subtitle])
        
        # Add article file if provided
        if temp_article:
            cmd_args.extend(["--article", temp_article.name])
        
        # Set environment variables
        env = os.environ.copy()
        if "OPENAI_API_KEY" in env:
            logger.info("✅ OpenAI API key found")
        else:
            logger.warning("⚠️ OpenAI API key not found")
        
        logger.info(f"🚀 Executing: {' '.join(cmd_args)}")
        
        # Execute the generation script
        import time
        start_time = time.time()
        
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env
        )
        
        generation_time = time.time() - start_time
        
        # Clean up temp file
        if temp_article:
            try:
                os.unlink(temp_article.name)
            except:
                pass
        
        if result.returncode != 0:
            logger.error(f"❌ Generation failed: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Generation script failed",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
            )
        
        # Check for output file
        client_id = request.client_id or "generic"
        output_file = f"boxed_cover_{client_id}.png"
        output_path = output_dir / output_file
        
        if not output_path.exists():
            logger.error(f"❌ Output file not found: {output_path}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Output file not created",
                    "expected_path": str(output_path),
                    "stdout": result.stdout
                }
            )
        
        # Return success response
        image_url = f"/images/{output_file}"
        
        logger.info(f"✅ Cover generated successfully: {image_url}")
        
        return GenerateResponse(
            success=True,
            image_url=image_url,
            image_path=str(output_path),
            generation_time=generation_time,
            metadata={
                "client_id": client_id,
                "title": request.title,
                "subtitle": request.subtitle,
                "style": request.style,
                "size": request.size,
                "stdout": result.stdout.split('\n')[-10:] if result.stdout else []  # Last 10 lines
            }
        )
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Generation timed out")
        raise HTTPException(
            status_code=408,
            detail="Generation timed out after 5 minutes"
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected error during generation",
                "message": str(e)
            }
        )

@app.get("/images/{filename}")
async def get_image(filename: str):
    """Serve generated images"""
    file_path = output_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "LoRA AI Cover Generator",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "generate": "/generate",
            "images": "/images/{filename}",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting AI Cover Generator on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)