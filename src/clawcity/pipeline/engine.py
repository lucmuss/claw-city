# -*- coding: utf-8 -*-
"""Pipeline engine for orchestrating episode generation."""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from clawcity.core.config import get_config
from clawcity.core.exceptions import PipelineError, ScriptError
from clawcity.core.models import Episode, PipelineContext, PipelineResult
from clawcity.services.audio import AudioService
from clawcity.services.images import get_image_service
from clawcity.services.video import get_video_service


class PipelineStage(Enum):
    SETUP = "setup"
    IMAGES = "images"
    AUDIO = "audio"
    VIDEO = "video"
    FULL = "full"


@dataclass
class StageConfig:
    enabled: bool = True
    skip_existing: bool = True
    retries: int = 3


class PipelineEngine:
    """Main pipeline engine that orchestrates all stages."""

    def __init__(self) -> None:
        self.config = get_config()
        self.stages: dict[PipelineStage, StageConfig] = {
            PipelineStage.SETUP: StageConfig(),
            PipelineStage.IMAGES: StageConfig(),
            PipelineStage.AUDIO: StageConfig(),
            PipelineStage.VIDEO: StageConfig(),
            PipelineStage.FULL: StageConfig(),
        }
        self._progress_callbacks: list[Callable[[str, int, int], None]] = []
        self._results: list[PipelineResult] = []

    def on_progress(self, callback: Callable[[str, int, int], None]) -> None:
        """Register progress callback."""
        self._progress_callbacks.append(callback)

    def _notify_progress(self, stage: str, current: int, total: int) -> None:
        """Notify all progress callbacks."""
        for callback in self._progress_callbacks:
            with contextlib.suppress(Exception):
                callback(stage, current, total)

    def load_episode(
        self, episode_num: int, script_path: Path | None = None
    ) -> Episode:
        """Load an episode from a YAML script."""
        scripts_dir = self.config.scripts_dir
        if script_path is None:
            candidates = [
                scripts_dir / f"ep{episode_num:02d}_v3.yaml",
                scripts_dir / f"ep{episode_num:02d}.yaml",
                scripts_dir / f"episode_{episode_num:02d}.yaml",
            ]
            for candidate in candidates:
                if candidate.exists():
                    script_path = candidate
                    break

        if script_path is None or not script_path.exists():
            raise ScriptError(f"Script for episode {episode_num} not found")

        with open(script_path, encoding="utf-8") as handle:
            data = yaml.safe_load(handle)

        return Episode.from_dict(data)

    def create_context(self, episode: Episode, clean: bool = False) -> PipelineContext:
        """Create pipeline context for an episode."""
        output_root = self.config.output_dir
        output_dir = output_root / f"ep{episode.number:02d}"

        if clean and output_dir.exists():
            import shutil

            print(f"Cleaning existing files in {output_dir}")
            shutil.rmtree(output_dir)
            print("Cleaned")

        output_dir.mkdir(parents=True, exist_ok=True)

        return PipelineContext(
            episode=episode,
            output_dir=output_dir,
            config=self.config.__dict__ if hasattr(self.config, "__dict__") else {},
        )

    def run_stage(
        self, stage: PipelineStage, context: PipelineContext, **kwargs: Any
    ) -> PipelineResult:
        """Run a single pipeline stage."""
        stage_config = self.stages.get(stage, StageConfig())

        if not stage_config.enabled:
            return PipelineResult(
                success=True,
                stage=stage.value,
                message=f"Skipped {stage.value} (disabled)",
            )

        print("")
        print("=" * 50)
        print(f"Stage: {stage.value.upper()}")
        print("=" * 50)

        try:
            if stage == PipelineStage.IMAGES:
                return self._run_images(context)
            if stage == PipelineStage.AUDIO:
                engine = kwargs.get("audio_engine", "openai")
                return self._run_audio(context, engine)
            if stage == PipelineStage.VIDEO:
                engine = kwargs.get("audio_engine", "openai")
                return self._run_video(context, engine)
            if stage == PipelineStage.FULL:
                return self._run_full(context)
            return PipelineResult(
                success=True, stage=stage.value, message="Setup complete"
            )
        except Exception as exc:
            raise PipelineError(f"Stage {stage.value} failed: {exc}") from exc

    def _run_images(self, context: PipelineContext) -> PipelineResult:
        """Run image generation stage."""
        service = get_image_service()
        return service.generate_episode(context)

    def _run_audio(
        self, context: PipelineContext, engine: str = "openai"
    ) -> PipelineResult:
        """Run audio generation stage."""
        service = AudioService(provider=engine)
        return asyncio.run(service.generate_episode(context, engine))

    def _run_video(
        self, context: PipelineContext, engine: str = "openai"
    ) -> PipelineResult:
        """Run video generation stage."""
        service = get_video_service()
        return service.generate_episode(context, engine)

    def _run_full(self, context: PipelineContext) -> PipelineResult:
        """Run full episode combination stage."""
        service = get_video_service()
        intro = self.config.assets_dir / "intro.mp4"
        return service.create_full_episode(context, intro if intro.exists() else None)

    def run(
        self,
        episode_num: int,
        script_path: Path | None = None,
        stages: list[PipelineStage] | None = None,
        audio_engine: str = "openai",
        skip_existing: bool = True,
        clean: bool = False,
    ) -> list[PipelineResult]:
        """Run the pipeline for a single episode."""
        _ = skip_existing
        if stages is None:
            stages = [
                PipelineStage.SETUP,
                PipelineStage.IMAGES,
                PipelineStage.AUDIO,
                PipelineStage.VIDEO,
                PipelineStage.FULL,
            ]

        print("")
        print("#" * 60)
        print(f"# CLAW CITY PIPELINE - Episode {episode_num:02d}")
        print("#" * 60)

        episode = self.load_episode(episode_num, script_path)
        print(f"Episode: {episode.title}")
        print(f"Scenes: {episode.scene_count}")
        print(f"Duration: ~{episode.total_duration_seconds // 60} min")

        context = self.create_context(episode, clean=clean)
        print(f"Output: {context.output_dir}")

        results: list[PipelineResult] = []
        total_stages = len(stages)

        for i, stage in enumerate(stages, 1):
            self._notify_progress(stage.value, i, total_stages)

            try:
                result = self.run_stage(
                    stage, context, audio_engine=audio_engine, clean=clean
                )
                results.append(result)

                if not result.success and stage not in {PipelineStage.FULL}:
                    print(f"Stage {stage.value} failed, stopping pipeline")
                    break

            except Exception as exc:
                print(f"Stage {stage.value} error: {exc}")
                results.append(
                    PipelineResult(success=False, stage=stage.value, message=str(exc))
                )
                break

        self._print_summary(results, context)
        self._results = results
        return results

    def _print_summary(
        self, results: list[PipelineResult], context: PipelineContext
    ) -> None:
        """Print pipeline summary."""
        print("")
        print("#" * 60)
        print(f"# PIPELINE COMPLETE - Episode {context.episode.number:02d}")
        print("#" * 60)

        success_count = sum(1 for result in results if result.success)
        total_count = len(results)

        print(f"Results: {success_count}/{total_count} stages successful")

        for result in results:
            status = "OK" if result.success else "FAIL"
            print(f"  {status} {result.stage}: {result.message}")

        images_dir = context.output_dir / "images"
        audio_dir = context.output_dir / "audio_edge"
        if not audio_dir.exists():
            audio_dir = context.output_dir / "audio_openai"
        video_dir = context.output_dir / "video"

        print("Output files:")
        if images_dir.exists():
            count = len(list(images_dir.glob("*.png")))
            print(f"  Images: {count}")
        if audio_dir.exists():
            count = len(list(audio_dir.rglob("*.mp3")))
            print(f"  Audio clips: {count}")
        if video_dir.exists():
            count = len(list(video_dir.glob("scene_*.mp4")))
            print(f"  Scene videos: {count}")

        full_ep = context.get_full_episode_path()
        if full_ep.exists():
            size_mb = full_ep.stat().st_size / (1024 * 1024)
            print(f"  Full episode: {full_ep.name} ({size_mb:.1f} MB)")


def get_pipeline() -> PipelineEngine:
    """Get a new pipeline instance."""
    return PipelineEngine()
