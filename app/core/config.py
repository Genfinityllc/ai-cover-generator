try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_STORAGE_BUCKET: str = "cover-images"
    
    # Model Configuration
    HUGGINGFACE_TOKEN: Optional[str] = None
    MODEL_CACHE_DIR: str = "./models/cache"
    
    # Image Generation Settings
    IMAGE_WIDTH: int = 1800
    IMAGE_HEIGHT: int = 900
    DEFAULT_STEPS: int = 30
    DEFAULT_GUIDANCE_SCALE: float = 7.5
    
    # LoRA Configuration
    LORA_MODELS_DIR: str = "./models/lora"
    DEFAULT_LORA_WEIGHT: float = 0.8
    
    # Performance Settings (Mac Studio Metal)
    USE_METAL: bool = True
    BATCH_SIZE: int = 1
    MEMORY_EFFICIENT: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()