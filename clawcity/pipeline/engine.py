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
                Path(f"scripts/ep{episode_num:02d}_v3.yaml"),
                Path(f"scripts/ep{episode_num:02d}.yaml"),
                Path(f"scripts/episode_{episode_num:02d}.yaml"),
            ]
            for candidate in candidates:
                if candidate.exists():
                    script_path = candidate
                    break
        
        if script_path is None or not script_path.exists():
            raise ScriptError(f"Script for episode {episode_num} not found")
        
        with open(script_path) as f:
            data = yaml.safe_load(f)
        
        return Episode.from_dict(data)
    
    def create_context(self, episode: Episode, clean: bool = False) -> PipelineContext:
        """Create pipeline context for episode"""
        output_dir = Path(f"output/ep{episode.number:02d}")
        
        # Clean existing files if requested
        if clean and output_dir.exists():
            import shutil
            print(f"\n🧹 Cleaning existing files in {output_dir}")
            shutil.rmtree(output_dir)
            print(f"   ✓ Cleaned")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return PipelineContext(
            episode=episode,
            output_dir=output_dir,
            config=self.config.__dict__ if hasattr(self.config, '__dict__') else {}
        )
    
    def run_stage(
        self,
        stage: PipelineStage,
        context: PipelineContext,
        **kwargs
    ) -> PipelineResult:
        """Run a single pipeline stage"""
        stage_config = self.stages.get(stage, StageConfig())
        
        if not stage_config.enabled:
            return PipelineResult(
                success=True,
                stage=stage.value,
                message=f"Skipped {stage.value} (disabled)"
            )
        
        print(f"\n{'='*50}")
        print(f"🎬 Stage: {stage.value.upper()}")
        print('='*50)
        
        try:
            if stage == PipelineStage.IMAGES:
                return self._run_images(context)
            elif stage == PipelineStage.AUDIO:
                engine = kwargs.get('audio_engine', 'openai')
                return self._run_audio(context, engine)
            elif stage == PipelineStage.VIDEO:
                engine = kwargs.get('audio_engine', 'openai')
                return self._run_video(context, engine)
            elif stage == PipelineStage.FULL:
                return self._run_full(context)
            else:
                return PipelineResult(
                    success=True,
                    stage=stage.value,
                    message="Setup complete"
                )
        except Exception as e:
            raise PipelineError(f"Stage {stage.value} failed: {e}")
    
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
        return service.create_full_episode(
            context,
            intro if intro.exists() else None
        )
    
    def run(
        self,
        episode_num: int,
        script_path: Optional[Path] = None,
        stages: Optional[List[PipelineStage]] = None,
        audio_engine: str = "openai",
        skip_existing: bool = True,
        clean: bool = False
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
        print(f"\n{'#'*60}")
        print(f"# 🎬 CLAW CITY PIPELINE - Episode {episode_num:02d}")
        print(f"{'#'*60}")
        
        episode = self.load_episode(episode_num, script_path)
        print(f"\n📖 Episode: {episode.title}")
        print(f"   Scenes: {episode.scene_count}")
        print(f"   Duration: ~{episode.total_duration_seconds // 60} min")
        
        context = self.create_context(episode, clean=clean)
        print(f"   Output: {context.output_dir}")
        
        # Run stages
        results = []
        total_stages = len(stages)
        
        for i, stage in enumerate(stages, 1):
            self._notify_progress(stage.value, i, total_stages)
            
            try:
                result = self.run_stage(
                    stage,
                    context,
                    audio_engine=audio_engine,
                    clean=clean
                )
                results.append(result)
                
                if not result.success and stage not in [PipelineStage.FULL]:
                    print(f"\n❌ Stage {stage.value} failed, stopping pipeline")
                    break
                    
            except Exception as e:
                print(f"\n❌ Stage {stage.value} error: {e}")
                results.append(PipelineResult(
                    success=False,
                    stage=stage.value,
                    message=str(e)
                ))
                break
        
        # Summary
        self._print_summary(results, context)
        self._results = results
        return results
    
    def _print_summary(self, results: List[PipelineResult], context: PipelineContext):
        """Print pipeline summary"""
        print(f"\n{'#'*60}")
        print(f"# ✅ PIPELINE COMPLETE - Episode {context.episode.number:02d}")
        print(f"{'#'*60}")
        
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        print(f"\n📊 Results: {success_count}/{total_count} stages successful")
        
        for r in results:
            status = "✓" if r.success else "✗"
            print(f"   {status} {r.stage}: {r.message}")
        
        # File counts
        images_dir = context.output_dir / "images"
        audio_dir = context.output_dir / f"audio_openai"
        video_dir = context.output_dir / "video"
        
        print(f"\n📁 Output Files:")
        if images_dir.exists():
            count = len(list(images_dir.glob("*.png")))
            print(f"   🖼️  Images: {count}")
        if audio_dir.exists():
            count = len(list(audio_dir.rglob("*.mp3")))
            print(f"   🎵 Audio clips: {count}")
        if video_dir.exists():
            count = len(list(video_dir.glob("scene_*.mp4")))
            print(f"   🎬 Scene videos: {count}")
        
        full_ep = context.get_full_episode_path()
        if full_ep.exists():
            size_mb = full_ep.stat().st_size / (1024 * 1024)
            print(f"   ⭐ Full Episode: {full_ep.name} ({size_mb:.1f} MB)")


# Singleton
_engine: Optional[PipelineEngine] = None


def get_pipeline() -> PipelineEngine:
    """Get or create pipeline engine"""
    global _engine
    if _engine is None:
        _engine = PipelineEngine()
    return _engine
