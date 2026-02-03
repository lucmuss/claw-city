"""Pipeline engine for orchestrating episode generation"""

import asyncio
import yaml
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from clawcity.core.config import get_config
from clawcity.core.models import Episode, PipelineContext, PipelineResult, ProcessingStatus
from clawcity.core.exceptions import PipelineError, ScriptError
from clawcity.services.audio import get_audio_service
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
    """Main pipeline engine that orchestrates all stages"""

    def __init__(self):
        self.config = get_config()
        self.stages: Dict[PipelineStage, StageConfig] = {
            PipelineStage.SETUP: StageConfig(),
            PipelineStage.IMAGES: StageConfig(),
            PipelineStage.AUDIO: StageConfig(),
            PipelineStage.VIDEO: StageConfig(),
            PipelineStage.FULL: StageConfig(),
        }
        self._progress_callbacks: List[Callable[[str, int, int], None]] = []
        self._results: List[PipelineResult] = []

    def on_progress(self, callback: Callable[[str, int, int], None]):
        """Register progress callback"""
        self._progress_callbacks.append(callback)

    def _notify_progress(self, stage: str, current: int, total: int):
        """Notify all progress callbacks"""
        for cb in self._progress_callbacks:
            try:
                cb(stage, current, total)
            except Exception:
                pass

    def load_episode(self, episode_num: int, script_path: Optional[Path] = None) -> Episode:
        """Load episode from YAML script"""
        if script_path is None:
            # Try different naming conventions
            candidates = [
                Path("scripts/ep{:02d}_v3.yaml".format(episode_num)),
                Path("scripts/ep{:02d}.yaml".format(episode_num)),
                Path("scripts/episode_{:02d}.yaml".format(episode_num)),
            ]
            for candidate in candidates:
                if candidate.exists():
                    script_path = candidate
                    break

        if script_path is None or not script_path.exists():
            raise ScriptError(
                "Script for episode {} not found".format(episode_num)
            )

        with open(script_path) as f:
            data = yaml.safe_load(f)

        return Episode.from_dict(data)

    def create_context(self, episode: Episode, clean: bool = False) -> PipelineContext:
        """Create pipeline context for episode"""
        output_dir = Path("output/ep{:02d}".format(episode.number))

        # Clean existing files if requested
        if clean and output_dir.exists():
            import shutil

            print("\n🧹 Cleaning existing files in {}".format(output_dir))
            shutil.rmtree(output_dir)
            print("   ✓ Cleaned")

        output_dir.mkdir(parents=True, exist_ok=True)

        return PipelineContext(
            episode=episode,
            output_dir=output_dir,
            config=self.config.__dict__ if hasattr(self.config, "__dict__") else {},
        )

    def run_stage(self, stage: PipelineStage, context: PipelineContext, **kwargs) -> PipelineResult:
        """Run a single pipeline stage"""
        stage_config = self.stages.get(stage, StageConfig())

        if not stage_config.enabled:
            return PipelineResult(
                success=True, stage=stage.value, message="Skipped {} (disabled)".format(stage.value)
            )

        print("\n" + '='*50)
        print("🎬 Stage: {}".format(stage.value.upper()))
        print("=" * 50)

        try:
            if stage == PipelineStage.IMAGES:
                return self._run_images(context)
            elif stage == PipelineStage.AUDIO:
                engine = kwargs.get("audio_engine", "openai")
                return self._run_audio(context, engine)
            elif stage == PipelineStage.VIDEO:
                engine = kwargs.get("audio_engine", "openai")
                return self._run_video(context, engine)
            elif stage == PipelineStage.FULL:
                return self._run_full(context)
            else:
                return PipelineResult(success=True, stage=stage.value, message="Setup complete")
        except Exception as e:
            raise PipelineError("Stage {} failed: {}".format(stage.value, e))

    def _run_images(self, context: PipelineContext) -> PipelineResult:
        """Run image generation stage"""
        service = get_image_service()
        return service.generate_episode(context)

    def _run_audio(self, context: PipelineContext, engine: str = "openai") -> PipelineResult:
        """Run audio generation stage"""
        from clawcity.services.audio import AudioService

        service = AudioService(provider=engine)
        return asyncio.run(service.generate_episode(context, engine))

    def _run_video(self, context: PipelineContext, engine: str = "openai") -> PipelineResult:
        """Run video generation stage"""
        service = get_video_service()
        return service.generate_episode(context, engine)

    def _run_full(self, context: PipelineContext) -> PipelineResult:
        """Run full episode combination stage"""
        service = get_video_service()
        intro = Path("assets/intro.mp4")
        return service.create_full_episode(context, intro if intro.exists() else None)

    def run(
        self,
        episode_num: int,
        script_path: Optional[Path] = None,
        stages: Optional[List[PipelineStage]] = None,
        audio_engine: str = "openai",
        skip_existing: bool = True,
        clean: bool = False,
    ) -> List[PipelineResult]:
        """
        Run complete pipeline for an episode

        Args:
            episode_num: Episode number
            script_path: Optional path to script file
            stages: List of stages to run (default: all)
            audio_engine: TTS engine to use (openai/edge)
            skip_existing: Skip existing files
            clean: Delete existing files before generation
        """
        # Default: run all stages
        if stages is None:
            stages = [
                PipelineStage.SETUP,
                PipelineStage.IMAGES,
                PipelineStage.AUDIO,
                PipelineStage.VIDEO,
                PipelineStage.FULL,
            ]

        # Load episode
        print("\n" + '#'*60)
        print("# 🎬 CLAW CITY PIPELINE - Episode {:02d}".format(episode_num))
        print('#'*60)

        episode = self.load_episode(episode_num, script_path)
        print("\n📖 Episode: {}".format(episode.title))
        print("   Scenes: {}".format(episode.scene_count))
        print("   Duration: ~{} min".format(episode.total_duration_seconds // 60))

        context = self.create_context(episode, clean=clean)
        print("   Output: {}".format(context.output_dir))

        # Run stages
        results = []
        total_stages = len(stages)

        for i, stage in enumerate(stages, 1):
            self._notify_progress(stage.value, i, total_stages)

            try:
                result = self.run_stage(stage, context, audio_engine=audio_engine, clean=clean)
                results.append(result)

                if not result.success and stage not in [PipelineStage.FULL]:
                    print("\n❌ Stage {} failed, stopping pipeline".format(stage.value))
                    break

            except Exception as e:
                print("\n❌ Stage {} error: {}".format(stage.value, e))
                results.append(PipelineResult(success=False, stage=stage.value, message=str(e)))
                break

        # Summary
        self._print_summary(results, context)
        self._results = results
        return results

    def _print_summary(self, results: List[PipelineResult], context: PipelineContext):
        """Print pipeline summary"""
        print("\n" + '#'*60)
        print("# ✅ PIPELINE COMPLETE - Episode {:02d}".format(context.episode.number))
        print('#'*60)

        success_count = sum(1 for r in results if r.success)
        total_count = len(results)

        print("\n📊 Results: {}/{} stages successful".format(success_count, total_count))

        for r in results:
            status = "✓" if r.success else "✗"
            print("   {} {}: {}".format(status, r.stage, r.message))

        # File counts
        # We try to detect which audio engine was used based on directory existence
        images_dir = context.output_dir / "images"
        audio_dir = context.output_dir / "audio_edge"
        if not audio_dir.exists():
            audio_dir = context.output_dir / "audio_openai"

        video_dir = context.output_dir / "video"

        print("\n📁 Output Files:")
        if images_dir.exists():
            count = len(list(images_dir.glob("*.png")))
            print("   🖼️  Images: {}".format(count))
        if audio_dir.exists():
            count = len(list(audio_dir.rglob("*.mp3")))
            print("   🎵 Audio clips: {}".format(count))
        if video_dir.exists():
            count = len(list(video_dir.glob("scene_*.mp4")))
            print("   🎬 Scene videos: {}".format(count))

        full_ep = context.get_full_episode_path()
        if full_ep.exists():
            size_mb = full_ep.stat().st_size / (1024 * 1024)
            print("   ⭐ Full Episode: {} ({:.1f} MB)".format(full_ep.name, size_mb))


# Singleton
_engine: Optional[PipelineEngine] = None


def get_pipeline() -> PipelineEngine:
    """Get or create pipeline engine"""
    global _engine
    if _engine is None:
        _engine = PipelineEngine()
    return _engine
