from supabase import create_client, Client
import os
from PIL import Image
import io
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.supabase: Client = None
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET
        self.initialized = False

    async def initialize(self):
        """Initialize Supabase client"""
        if self.initialized:
            return
        
        try:
            self.supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            
            # Ensure bucket exists
            await self._ensure_bucket_exists()
            
            self.initialized = True
            logger.info("✅ Supabase storage service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize storage service: {str(e)}")
            raise

    async def _ensure_bucket_exists(self):
        """Ensure the storage bucket exists"""
        try:
            # List buckets to check if ours exists
            buckets = self.supabase.storage.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            
            if self.bucket_name not in bucket_names:
                # Create bucket
                self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={"public": True}
                )
                logger.info(f"📦 Created storage bucket: {self.bucket_name}")
            
        except Exception as e:
            logger.error(f"❌ Error ensuring bucket exists: {str(e)}")

    async def upload_image(
        self,
        image: Image.Image,
        filename: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Upload generated image to Supabase storage"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Convert PIL Image to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Upload to Supabase storage
            result = self.supabase.storage.from_(self.bucket_name).upload(
                file=img_buffer.getvalue(),
                path=f"covers/{filename}",
                file_options={"content-type": "image/png"}
            )
            
            if result.status_code != 200:
                raise Exception(f"Upload failed with status {result.status_code}")
            
            # Get public URL
            url_result = self.supabase.storage.from_(self.bucket_name).get_public_url(f"covers/{filename}")
            image_url = url_result
            
            # Save metadata to database
            await self._save_image_metadata(filename, image_url, metadata)
            
            logger.info(f"✅ Image uploaded successfully: {filename}")
            return image_url
            
        except Exception as e:
            logger.error(f"❌ Error uploading image: {str(e)}")
            raise

    async def upload_watermark(
        self,
        file_data: bytes,
        filename: str,
        content_type: str
    ) -> str:
        """Upload watermark file to storage"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Upload to watermarks folder
            result = self.supabase.storage.from_(self.bucket_name).upload(
                file=file_data,
                path=f"watermarks/{filename}",
                file_options={"content-type": content_type}
            )
            
            if result.status_code != 200:
                raise Exception(f"Watermark upload failed with status {result.status_code}")
            
            # Get public URL
            url_result = self.supabase.storage.from_(self.bucket_name).get_public_url(f"watermarks/{filename}")
            
            logger.info(f"✅ Watermark uploaded successfully: {filename}")
            return url_result
            
        except Exception as e:
            logger.error(f"❌ Error uploading watermark: {str(e)}")
            raise

    async def save_preview(self, image: Image.Image, job_id: str) -> str:
        """Save preview image for approval workflow"""
        
        try:
            filename = f"preview_{job_id}.png"
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Upload to previews folder
            result = self.supabase.storage.from_(self.bucket_name).upload(
                file=img_buffer.getvalue(),
                path=f"previews/{filename}",
                file_options={"content-type": "image/png"}
            )
            
            if result.status_code != 200:
                raise Exception(f"Preview upload failed with status {result.status_code}")
            
            # Get public URL
            url_result = self.supabase.storage.from_(self.bucket_name).get_public_url(f"previews/{filename}")
            
            logger.info(f"✅ Preview saved: {filename}")
            return url_result
            
        except Exception as e:
            logger.error(f"❌ Error saving preview: {str(e)}")
            raise

    async def finalize_image(self, job_id: str) -> str:
        """Move preview to final storage"""
        
        try:
            preview_filename = f"preview_{job_id}.png"
            final_filename = f"final_{job_id}_{int(datetime.now().timestamp())}.png"
            
            # Download preview
            preview_data = self.supabase.storage.from_(self.bucket_name).download(f"previews/{preview_filename}")
            
            # Upload as final image
            result = self.supabase.storage.from_(self.bucket_name).upload(
                file=preview_data,
                path=f"covers/{final_filename}",
                file_options={"content-type": "image/png"}
            )
            
            if result.status_code != 200:
                raise Exception(f"Final upload failed with status {result.status_code}")
            
            # Get public URL
            url_result = self.supabase.storage.from_(self.bucket_name).get_public_url(f"covers/{final_filename}")
            
            # Clean up preview
            self.supabase.storage.from_(self.bucket_name).remove([f"previews/{preview_filename}"])
            
            logger.info(f"✅ Image finalized: {final_filename}")
            return url_result
            
        except Exception as e:
            logger.error(f"❌ Error finalizing image: {str(e)}")
            raise

    async def _save_image_metadata(self, filename: str, url: str, metadata: Dict[str, Any]):
        """Save image metadata to database"""
        
        try:
            # Prepare data for database
            db_data = {
                "id": str(uuid.uuid4()),
                "filename": filename,
                "image_url": url,
                "title": metadata.get("title"),
                "subtitle": metadata.get("subtitle"),
                "client_id": metadata.get("client_id"),
                "image_size": metadata.get("size", "1800x900"),
                "generation_params": json.dumps(metadata.get("generation_params", {})),
                "created_at": datetime.now().isoformat()
            }
            
            # Insert into database (create table if needed)
            result = self.supabase.table("generated_images").insert(db_data).execute()
            
            if not result.data:
                raise Exception("Failed to save metadata to database")
            
            logger.info(f"✅ Metadata saved for {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error saving metadata: {str(e)}")
            # Don't raise here - image upload succeeded

    async def list_images(
        self,
        limit: int = 50,
        offset: int = 0,
        client_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List generated images with metadata"""
        
        try:
            query = self.supabase.table("generated_images").select("*")
            
            if client_id:
                query = query.eq("client_id", client_id)
            
            result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"❌ Error listing images: {str(e)}")
            return []

    async def delete_image(self, image_id: str) -> bool:
        """Delete image and its metadata"""
        
        try:
            # Get image metadata
            result = self.supabase.table("generated_images").select("filename").eq("id", image_id).execute()
            
            if not result.data:
                return False
            
            filename = result.data[0]["filename"]
            
            # Delete from storage
            self.supabase.storage.from_(self.bucket_name).remove([f"covers/{filename}"])
            
            # Delete metadata
            self.supabase.table("generated_images").delete().eq("id", image_id).execute()
            
            logger.info(f"✅ Image deleted: {image_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting image: {str(e)}")
            return False

    async def list_available_logos(self) -> List[Dict[str, Any]]:
        """List available LoRA models/logos"""
        
        try:
            # This would query the client_logos table in production
            # For now, return static list based on available LoRA files
            lora_dir = settings.LORA_MODELS_DIR
            
            if not os.path.exists(lora_dir):
                return []
            
            lora_files = [f for f in os.listdir(lora_dir) if f.endswith('.safetensors')]
            
            logos = []
            for lora_file in lora_files:
                model_name = os.path.splitext(lora_file)[0]
                logos.append({
                    "id": model_name,
                    "name": model_name.replace("_", " ").title(),
                    "model_path": os.path.join(lora_dir, lora_file),
                    "available": True
                })
            
            return logos
            
        except Exception as e:
            logger.error(f"❌ Error listing logos: {str(e)}")
            return []

    async def create_backup(self) -> str:
        """Create backup of all images"""
        
        try:
            # This is a simplified backup - in production, implement proper backup strategy
            backup_filename = f"backup_{int(datetime.now().timestamp())}.json"
            
            # Get all image metadata
            images = await self.list_images(limit=1000)
            
            # Create backup metadata
            backup_data = {
                "created_at": datetime.now().isoformat(),
                "images_count": len(images),
                "images": images
            }
            
            # Upload backup metadata
            backup_buffer = io.BytesIO(json.dumps(backup_data, indent=2).encode())
            
            result = self.supabase.storage.from_(self.bucket_name).upload(
                file=backup_buffer.getvalue(),
                path=f"backups/{backup_filename}",
                file_options={"content-type": "application/json"}
            )
            
            if result.status_code != 200:
                raise Exception(f"Backup upload failed with status {result.status_code}")
            
            # Get public URL
            url_result = self.supabase.storage.from_(self.bucket_name).get_public_url(f"backups/{backup_filename}")
            
            logger.info(f"✅ Backup created: {backup_filename}")
            return url_result
            
        except Exception as e:
            logger.error(f"❌ Error creating backup: {str(e)}")
            raise

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        
        try:
            # Get image count and metadata
            images_result = self.supabase.table("generated_images").select("id", count="exact").execute()
            images_count = images_result.count or 0
            
            # Get storage usage (simplified - would need proper implementation)
            stats = {
                "total_images": images_count,
                "storage_bucket": self.bucket_name,
                "initialized": self.initialized,
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting storage stats: {str(e)}")
            return {
                "error": str(e),
                "initialized": self.initialized
            }