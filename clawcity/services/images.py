"""Image generation service using Replicate/Flux"""
import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import replicate
    HAS_REPLICATE = True
except ImportError:
    HAS_REPLICATE = False

from clawcity.core.config import get_config
from clawcity.core.exceptions import ImageGenerationError, ConfigurationError, RateLimitError
from clawcity.core.models import Scene, PipelineContext, PipelineResult


class ImageService:
    """Service for generating scene images"""
    
    def __init__(self):
        self.config = get_config()
        
        if not HAS_REPLICATE:
            raise ConfigurationError("replicate package not installed. Install with: pip install replicate")
        
        if not self.config.replicate_api_token:
            raise ConfigurationError("REPLICATE_API_TOKEN not set")
        
        os.environ["REPLICATE_API_TOKEN"] = self.config.replicate_api_token
    
    def build_prompt(self, scene_prompt: str) -> str:
        """Build full prompt with style suffix"""
        return f"{scene_prompt}. {self.config.images.style_suffix}"
    
    def generate(
        self,
        prompt: str,
        output_path: Path,
        max_retries: Optional[int] = None
    ) -> PipelineResult:
        """Generate a single image with retry logic"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.exists():
            return PipelineResult(
                success=True,
                stage="image",
                message=f"Skipped (exists): {output_path.name}",
                output_path=output_path
            )
        
        max_retries = max_retries or self.config.images.max_retries
        full_prompt = self.build_prompt(prompt)
        
        for attempt in range(max_retries):
            try:
                print(f"  ⏳ Generating {output_path.name} (attempt {attempt + 1})")
                
                output = replicate.run(
                    self.config.images.model,
                    input={
                        "prompt": full_prompt,
                        "num_outputs": 1,
                        "aspect_ratio": self.config.images.aspect_ratio,
                        "output_format": self.config.images.output_format,
                        "output_quality": self.config.images.output_quality
                    }
                )
                
                image_url = output[0]
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                size_kb = len(response.content) / 1024
                return PipelineResult(
                    success=True,
                    stage="image",
                    message=f"Generated: {output_path.name} ({size_kb:.0f} KB)",
                    output_path=output_path,
                    metadata={"size_kb": size_kb, "attempts": attempt + 1}
                )
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "throttled" in error_str.lower():
                    wait_time = self.config.images.rate_limit_delay + (attempt * 3)
                    print(f"  ⏳ Rate limit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    if attempt == max_retries - 1:
                        raise ImageGenerationError(f"Failed after {max_retries} attempts: {e}")
                    print(f"  ⚠️  Error: {e}, retrying...")
                    time.sleep(2)
        
        return PipelineResult(
            success=False,
            stage="image",
            message=f"Failed to generate {output_path.name}",
            output_path=output_path
        )
    
    def generate_scene(
        self,
        scene: Scene,
        context: PipelineContext
    ) -> PipelineResult:
        """Generate image for a scene"""
        output_path = context.get_image_path(scene.id)
        
        result = self.generate(scene.image_prompt, output_path)
        
        # NOTE: Rate limiting is handled internally by 'generate' on 429 errors.
        # Adding a global sleep here is ineffective in a ThreadPoolExecutor, 
        # relying on internal retries is more effective.
        
        return result
    
    def generate_episode(
        self,
        context: PipelineContext,
    ) -> PipelineResult:
        """Generate images for all scenes in episode (parallel)"""
        
        max_workers = self.config.images.max_workers
        
        total_scenes = len(context.episode.scenes)
        completed = 0
        failed = []
        
        print(f"\n🎨 Generating images for {total_scenes} scenes (Parallel, workers={max_workers})...")
        print(f"   Model: {self.config.images.model}")
        print("-" * 40)

        def _worker(scene):
            try:
                return self.generate_scene(scene, context)
            except Exception as e:
                return PipelineResult(success=False, stage="image", message=str(e), metadata={"scene_id": scene.id})

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_scene = {executor.submit(_worker, scene): scene for scene in context.episode.scenes}
            
            for future in as_completed(future_to_scene):
                scene = future_to_scene[future]
                try:
                    result = future.result()
                    if result.success:
                        completed += 1
                        print(f"  ✓ Scene {scene.id} finished")
                    else:
                        failed.append(scene.id)
                        print(f"  ✗ Scene {scene.id} failed: {result.message}")
                except Exception as e:
                    failed.append(scene.id)
                    print(f"  ✗ Scene {scene.id} error: {e}")

        return PipelineResult(
            success=len(failed) == 0,
            stage="images_episode",
            message=f"Images: {completed}/{total_scenes} generated",
            output_path=context.output_dir / "images",
            metadata={"completed": completed, "failed": failed, "total": total_scenes}
        )


# Singleton instance
_image_service = None


def get_image_service() -> ImageService:
    """Get or create image service singleton"""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
