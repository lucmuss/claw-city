# -*- coding: utf-8 -*-
"""Image generation service using Replicate/Flux."""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

try:
    import replicate

    HAS_REPLICATE = True
except ImportError:
    HAS_REPLICATE = False

from clawcity.core.config import get_config
from clawcity.core.exceptions import ConfigurationError, ImageGenerationError
from clawcity.core.models import PipelineContext, PipelineResult, Scene
from clawcity.pipeline.prompt_builder import build_image_prompt


class ImageService:
    """Service for generating scene images."""

    def __init__(self) -> None:
        self.config = get_config()

        if not HAS_REPLICATE:
            raise ConfigurationError(
                "replicate package not installed. Install with: uv add replicate"
            )

        if not self.config.replicate_api_token:
            raise ConfigurationError("REPLICATE_API_TOKEN not set")

        os.environ["REPLICATE_API_TOKEN"] = self.config.replicate_api_token

    def generate(
        self, prompt: str, output_path: Path, max_retries: int | None = None
    ) -> PipelineResult:
        """Generate a single image with retry logic."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            return PipelineResult(
                success=True,
                stage="image",
                message=f"Skipped (exists): {output_path.name}",
                output_path=output_path,
            )

        max_retries = max_retries or self.config.images.max_retries
        full_prompt = prompt

        for attempt in range(max_retries):
            try:
                print(f"Generating {output_path.name} (attempt {attempt + 1})")

                output = replicate.run(
                    self.config.images.model,
                    input={
                        "prompt": full_prompt,
                        "num_outputs": 1,
                        "aspect_ratio": self.config.images.aspect_ratio,
                        "output_format": self.config.images.output_format,
                        "output_quality": self.config.images.output_quality,
                    },
                )

                image_url = output[0]
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()

                with open(output_path, "wb") as handle:
                    handle.write(response.content)

                size_kb = len(response.content) / 1024
                return PipelineResult(
                    success=True,
                    stage="image",
                    message=f"Generated: {output_path.name} ({size_kb:.0f} KB)",
                    output_path=output_path,
                    metadata={"size_kb": size_kb, "attempts": attempt + 1},
                )

            except Exception as exc:
                error_str = str(exc)
                if "429" in error_str or "throttled" in error_str.lower():
                    wait_time = self.config.images.rate_limit_delay + (attempt * 3)
                    print(f"Rate limit hit, waiting {wait_time}s")
                    time.sleep(wait_time)
                else:
                    if attempt == max_retries - 1:
                        raise ImageGenerationError(
                            f"Failed after {max_retries} attempts: {exc}"
                        ) from exc
                    print(f"Error: {exc}. Retrying")
                    time.sleep(2)

        return PipelineResult(
            success=False,
            stage="image",
            message=f"Failed to generate {output_path.name}",
            output_path=output_path,
        )

    def generate_scene(
        self,
        scene: Scene,
        context: PipelineContext,
        previous_scenes: list[Scene] | None = None,
    ) -> PipelineResult:
        """Generate an image for a scene."""
        output_path = context.get_image_path(scene.id)
        full_image_prompt = build_image_prompt(scene, previous_scenes)
        return self.generate(full_image_prompt, output_path)

    def generate_episode(self, context: PipelineContext) -> PipelineResult:
        """Generate images for all scenes in an episode in parallel."""
        max_workers = self.config.images.max_workers

        total_scenes = len(context.episode.scenes)
        completed = 0
        failed: list[int] = []

        print(f"Images: generating {total_scenes} scenes (workers={max_workers})")
        print(f"Model: {self.config.images.model}")
        print("-" * 40)

        def _worker(index: int, scene: Scene) -> PipelineResult:
            previous_scenes: list[Scene] = []
            if index > 0:
                start_idx = max(0, index - 2)
                previous_scenes = context.episode.scenes[start_idx:index]

            try:
                return self.generate_scene(scene, context, previous_scenes)
            except Exception as exc:
                return PipelineResult(
                    success=False,
                    stage="image",
                    message=str(exc),
                    metadata={"scene_id": scene.id},
                )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_scene = {
                executor.submit(_worker, i, scene): scene
                for i, scene in enumerate(context.episode.scenes)
            }

            for future in as_completed(future_to_scene):
                scene = future_to_scene[future]
                try:
                    result = future.result()
                    if result.success:
                        completed += 1
                        print(f"Scene {scene.id}: ok")
                    else:
                        failed.append(scene.id)
                        print(f"Scene {scene.id}: failed - {result.message}")
                except Exception as exc:
                    failed.append(scene.id)
                    print(f"Scene {scene.id}: error - {exc}")

        return PipelineResult(
            success=len(failed) == 0,
            stage="images_episode",
            message=f"Images: {completed}/{total_scenes} generated",
            output_path=context.output_dir / "images",
            metadata={"completed": completed, "failed": failed, "total": total_scenes},
        )


_image_service: ImageService | None = None


def get_image_service() -> ImageService:
    """Get or create the image service singleton."""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
