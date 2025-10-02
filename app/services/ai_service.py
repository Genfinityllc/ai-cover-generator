import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from compel import Compel
import os
from PIL import Image, ImageDraw, ImageFont
import io
from typing import Optional, List, Dict, Any, Tuple
import asyncio
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.pipeline = None
        self.compel = None
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.lora_models = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the Stable Diffusion XL pipeline with Metal acceleration"""
        if self.initialized:
            return
            
        try:
            logger.info("🔄 Initializing Stable Diffusion XL pipeline...")
            
            # Load SDXL pipeline
            model_id = "stabilityai/stable-diffusion-xl-base-1.0"
            
            # Create cache directory if it doesn't exist
            os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
            
            self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device == "mps" else torch.float32,
                cache_dir=settings.MODEL_CACHE_DIR,
                use_safetensors=True
            )
            
            # Use DPM++ scheduler for better quality
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            
            # Move to Metal/MPS device on Mac
            if self.device == "mps":
                self.pipeline = self.pipeline.to("mps")
                # Enable memory efficient attention
                if settings.MEMORY_EFFICIENT:
                    self.pipeline.enable_attention_slicing()
            
            # Initialize Compel for better prompt handling (using single tokenizer to avoid deprecation)
            self.compel = Compel(
                tokenizer=self.pipeline.tokenizer,
                text_encoder=self.pipeline.text_encoder
            )
            
            # Load available LoRA models
            await self._load_lora_models()
            
            self.initialized = True
            logger.info(f"✅ SDXL pipeline initialized on device: {self.device}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI pipeline: {str(e)}")
            raise

    async def _load_lora_models(self):
        """Load available LoRA models from disk"""
        try:
            lora_dir = settings.LORA_MODELS_DIR
            os.makedirs(lora_dir, exist_ok=True)
            
            lora_files = [f for f in os.listdir(lora_dir) if f.endswith('.safetensors')]
            
            for lora_file in lora_files:
                model_name = os.path.splitext(lora_file)[0]
                
                # Check if it's an enhanced LoRA (text file)
                file_path = os.path.join(lora_dir, lora_file)
                try:
                    with open(file_path, 'r') as f:
                        first_line = f.readline()
                        if first_line.startswith("# Enhanced LoRA"):
                            # This is an enhanced LoRA
                            self.lora_models[model_name] = {
                                "path": file_path,
                                "loaded": False,
                                "type": "enhanced",
                                "mock": True
                            }
                        else:
                            # Regular LoRA
                            self.lora_models[model_name] = {
                                "path": file_path,
                                "loaded": False,
                                "type": "regular",
                                "mock": False
                            }
                except:
                    # If we can't read as text, assume it's a real LoRA
                    self.lora_models[model_name] = {
                        "path": file_path,
                        "loaded": False,
                        "type": "regular",
                        "mock": False
                    }
            
            logger.info(f"🎨 Found {len(self.lora_models)} LoRA models")
            
        except Exception as e:
            logger.error(f"❌ Error loading LoRA models: {str(e)}")

    async def generate_background(
        self, 
        client_id: Optional[str] = None,
        lora_models: Optional[List[str]] = None,
        prompt_enhancement: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        style_params: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """Generate background image using SDXL + LoRA"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Build prompt
            if custom_prompt:
                base_prompt = custom_prompt
            else:
                base_prompt = self._build_crypto_prompt(prompt_enhancement, client_id)
            
            # Load LoRA if specified
            lora_to_load = None
            if client_id:
                lora_to_load = await self._get_lora_for_client(client_id)
            elif lora_models:
                lora_to_load = lora_models[0]  # Use first LoRA for now
            
            if lora_to_load:
                await self._load_lora(lora_to_load)
            
            # For SDXL, use regular prompt instead of embeddings to avoid pooled_prompt_embeds issue
            params = {
                "prompt": base_prompt,
                "height": settings.IMAGE_HEIGHT,
                "width": settings.IMAGE_WIDTH,
                "num_inference_steps": style_params.get("steps", settings.DEFAULT_STEPS) if style_params else settings.DEFAULT_STEPS,
                "guidance_scale": style_params.get("guidance", settings.DEFAULT_GUIDANCE_SCALE) if style_params else settings.DEFAULT_GUIDANCE_SCALE,
                "num_images_per_prompt": 1
            }
            
            # Generate image
            logger.info(f"🎨 Generating image with prompt: {base_prompt[:100]}...")
            
            with torch.autocast(self.device):
                result = self.pipeline(**params)
                image = result.images[0]
            
            logger.info("✅ Background image generated successfully")
            return image
            
        except Exception as e:
            logger.error(f"❌ Error generating background: {str(e)}")
            raise

    def _build_crypto_prompt(self, enhancement: Optional[str] = None, client_id: Optional[str] = None) -> str:
        """Build crypto-themed prompt with client-specific enhancements"""
        base_prompts = [
            "professional cryptocurrency background, modern digital finance",
            "blockchain technology visualization, futuristic crypto landscape", 
            "digital currency symbols, professional trading environment",
            "cryptocurrency market visualization, clean modern design"
        ]
        
        base = base_prompts[0]  # Use first for consistency
        
        # Add client-specific theming when LoRA is not available
        if client_id:
            if "xdc" in client_id.lower():
                base += ", XDC network theme, enterprise blockchain, banking integration"
            elif "hedera" in client_id.lower() or "hbar" in client_id.lower():
                base += ", Hedera hashgraph theme, distributed ledger technology"
            elif "algorand" in client_id.lower():
                base += ", Algorand blockchain theme, proof of stake, green technology"
            elif "constellation" in client_id.lower():
                base += ", Constellation DAG theme, distributed network visualization"
            elif "hashpack" in client_id.lower():
                base += ", Hedera wallet theme, secure crypto storage"
            elif "tha" in client_id.lower():
                base += ", THA blockchain theme, professional crypto services"
            elif "genfinity" in client_id.lower():
                base += ", Genfinity media theme, crypto news and analysis"
        
        if enhancement:
            # Add title-based enhancement
            if "bitcoin" in enhancement.lower():
                base += ", bitcoin orange theme"
            elif "ethereum" in enhancement.lower():
                base += ", ethereum blue theme"
            elif "defi" in enhancement.lower():
                base += ", decentralized finance symbols"
        
        # Quality and style modifiers
        base += ", high quality, professional, clean composition, 8k resolution"
        
        return base

    async def _get_lora_for_client(self, client_id: str) -> Optional[str]:
        """Get LoRA model name for client ID"""
        # This would query the database in production
        # For now, return a simple mapping with _lora suffix
        client_lora_map = {
            # XDC Network
            "xdc": "xdc_network_lora",
            "xdc_network": "xdc_network_lora",
            "xdc_logo": "xdc_logo_lora",
            
            # Hedera
            "hedera": "hedera_lora",
            "hedera_foundation": "hedera_foundation_lora", 
            "hbar": "hbar_lora",
            
            # HashPack
            "hashpack": "hashpack_lora",
            "hashpack_color": "hashpack_color_lora",
            
            # Constellation
            "constellation": "constellation_lora",
            "dag": "constellation_lora",
            "constellation_alt": "constellation_alt_lora",
            
            # Algorand
            "algorand": "algorand_lora",
            "algo": "algorand_lora",
            
            # THA
            "tha": "tha_lora",
            "tha_color": "tha_color_lora",
            
            # Genfinity
            "genfinity": "genfinity_lora",
            "gen": "genfinity_lora",
            "genfinity_black": "genfinity_black_lora",
            
            # Legacy crypto mappings
            "bitcoin": "bitcoin_logo_lora",
            "ethereum": "ethereum_logo_lora", 
            "binance": "binance_logo_lora",
            "coinbase": "coinbase_logo_lora"
        }
        
        return client_lora_map.get(client_id.lower())

    async def _load_lora(self, lora_name: str):
        """Load specific LoRA model (graceful fallback for enhanced LoRAs)"""
        if lora_name not in self.lora_models:
            logger.warning(f"LoRA model {lora_name} not found, using generic background")
            return
        
        if self.lora_models[lora_name]["loaded"]:
            return  # Already loaded
        
        try:
            lora_info = self.lora_models[lora_name]
            lora_path = lora_info["path"]
            
            # Check if this is an enhanced LoRA
            if lora_info.get("type") == "enhanced":
                logger.info(f"📝 Enhanced LoRA detected: {lora_name}, using client-specific theming")
                self.lora_models[lora_name]["loaded"] = True
                return
            
            # Check if this is a mock LoRA file (small size)
            if os.path.getsize(lora_path) < 1000:
                logger.info(f"📝 Mock LoRA detected: {lora_name}, using enhanced prompt instead")
                self.lora_models[lora_name]["loaded"] = True
                self.lora_models[lora_name]["mock"] = True
                return
            
            # Load real LoRA adapter
            self.pipeline.load_lora_weights(lora_path)
            
            # Set LoRA scale
            self.pipeline.set_adapters([lora_name], adapter_weights=[settings.DEFAULT_LORA_WEIGHT])
            
            self.lora_models[lora_name]["loaded"] = True
            self.lora_models[lora_name]["mock"] = False
            logger.info(f"✅ Loaded real LoRA: {lora_name}")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not load LoRA {lora_name}, using enhanced prompt: {str(e)}")
            # Mark as loaded but enhanced
            self.lora_models[lora_name]["loaded"] = True
            self.lora_models[lora_name]["mock"] = True

    async def add_text_overlay(
        self,
        image: Image.Image,
        title: str,
        subtitle: Optional[str] = None,
        size: Tuple[int, int] = None,
        text_style: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """Add centered text overlay to image"""
        
        try:
            # Create a copy to avoid modifying original
            img_with_text = image.copy()
            draw = ImageDraw.Draw(img_with_text)
            
            # Image dimensions
            img_width, img_height = img_with_text.size
            
            # Default text style
            default_style = {
                "title_font_size": max(60, img_width // 30),
                "subtitle_font_size": max(40, img_width // 45),
                "title_color": (255, 255, 255),
                "subtitle_color": (255, 255, 255),  # White subtitle too
                "stroke_width": 0,  # No stroke outline
                "stroke_color": None
            }
            
            if text_style:
                default_style.update(text_style)
            
            # Load fonts (fallback to default if not available)
            try:
                title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", default_style["title_font_size"])
                subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", default_style["subtitle_font_size"])
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            # Calculate text positioning
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            
            # Center positioning
            if subtitle:
                # Position title slightly above center
                title_y = img_height // 2 - title_height - 20
                
                subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
                subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
                subtitle_y = img_height // 2 + 20
                
                subtitle_x = (img_width - subtitle_width) // 2
                
                # Draw subtitle (clean text, no outline)
                draw.text(
                    (subtitle_x, subtitle_y), 
                    subtitle, 
                    font=subtitle_font,
                    fill=default_style["subtitle_color"]
                )
            else:
                # Center title vertically
                title_y = (img_height - title_height) // 2
            
            title_x = (img_width - title_width) // 2
            
            # Draw title (clean white text, no outline)
            draw.text(
                (title_x, title_y), 
                title, 
                font=title_font,
                fill=default_style["title_color"]
            )
            
            logger.info("✅ Text overlay added successfully")
            return img_with_text
            
        except Exception as e:
            logger.error(f"❌ Error adding text overlay: {str(e)}")
            raise

    async def add_watermark(
        self,
        image: Image.Image,
        watermark_data: bytes,
        position: str = "bottom-right",
        opacity: float = 0.7
    ) -> Image.Image:
        """Add watermark to image"""
        
        try:
            # Load watermark
            watermark = Image.open(io.BytesIO(watermark_data))
            
            # Convert to RGBA if needed
            if watermark.mode != "RGBA":
                watermark = watermark.convert("RGBA")
            
            # Resize watermark to reasonable size (max 10% of image width)
            img_width, img_height = image.size
            max_watermark_width = img_width // 10
            
            if watermark.width > max_watermark_width:
                ratio = max_watermark_width / watermark.width
                new_height = int(watermark.height * ratio)
                watermark = watermark.resize((max_watermark_width, new_height), Image.Resampling.LANCZOS)
            
            # Adjust opacity
            if opacity < 1.0:
                # Create alpha mask
                alpha = watermark.split()[-1]
                alpha = alpha.point(lambda p: int(p * opacity))
                watermark.putalpha(alpha)
            
            # Calculate position
            wm_width, wm_height = watermark.size
            margin = 20
            
            positions = {
                "top-left": (margin, margin),
                "top-right": (img_width - wm_width - margin, margin),
                "bottom-left": (margin, img_height - wm_height - margin),
                "bottom-right": (img_width - wm_width - margin, img_height - wm_height - margin),
                "center": ((img_width - wm_width) // 2, (img_height - wm_height) // 2)
            }
            
            pos = positions.get(position, positions["bottom-right"])
            
            # Paste watermark
            img_with_watermark = image.copy()
            img_with_watermark.paste(watermark, pos, watermark)
            
            logger.info("✅ Watermark added successfully")
            return img_with_watermark
            
        except Exception as e:
            logger.error(f"❌ Error adding watermark: {str(e)}")
            raise

    async def get_status(self) -> Dict[str, Any]:
        """Get AI service status"""
        return {
            "sdxl_loaded": self.initialized,
            "lora_models_count": len(self.lora_models),
            "device": self.device,
            "memory_usage": self._get_memory_usage()
        }

    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        if self.device == "mps":
            try:
                # MPS memory stats (if available)
                return {
                    "device": "mps",
                    "available": True
                }
            except:
                pass
        
        return {
            "device": self.device,
            "available": torch.cuda.is_available() if hasattr(torch, 'cuda') else False
        }