"""Video generation service using FFmpeg"""
import subprocess
import os
import tempfile
from pathlib import Path
from typing import Optional, List

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

from clawcity.core.config import get_config
from clawcity.core.exceptions import VideoGenerationError, ConfigurationError
from clawcity.core.models import Scene, PipelineContext, PipelineResult


class VideoService:
    """Service for creating videos from images and audio"""
    
    def __init__(self):
        self.config = get_config()
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Verify FFmpeg is installed"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise ConfigurationError("FFmpeg not found. Please install FFmpeg.")
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds"""
        if not HAS_PYDUB:
            # Fallback: assume default duration
            return self.config.video.default_duration
        
        try:
            audio = AudioSegment.from_mp3(str(audio_path))
            return len(audio) / 1000.0
        except Exception:
            return self.config.video.default_duration
    
    def combine_scene_audio(self, audio_dir: Path) -> Optional[Path]:
        """Combine all audio files in a scene directory and return the combined path"""
        # PRIORITY: If combined.mp3 already exists, use it
        combined_path = audio_dir / "combined.mp3"
        if combined_path.exists():
            return combined_path

        audio_files = sorted([f for f in audio_dir.glob("*.mp3") if f.name != "combined.mp3"])
        if not audio_files:
            return None
        
        if len(audio_files) == 1:
            return audio_files[0]
        
        # Combine multiple audio files
        if not HAS_PYDUB:
            # Fallback: use first file only
            return audio_files[0]
        
        combined = AudioSegment.empty()
        for f in audio_files:
            combined += AudioSegment.from_mp3(str(f))
        
        combined.export(str(combined_path), format="mp3")
        return combined_path
    
    def create_scene_video(
        self,
        scene: Scene,
        context: PipelineContext,
        audio_dir: Optional[Path] = None,
        engine: str = "openai"
    ) -> PipelineResult:
        """Create video for a single scene with strictly standardized parameters"""
        image_path = context.get_image_path(scene.id)
        video_path = context.get_video_path(scene.id)
        video_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not image_path.exists():
            return PipelineResult(
                success=False,
                stage="video",
                message=f"Image not found: {image_path}",
                output_path=video_path
            )
        
        # Get audio
        if audio_dir is None:
            audio_dir = context.get_audio_dir(scene.id, engine)
        
        audio_path = self.combine_scene_audio(audio_dir)
        duration = scene.duration_seconds
        
        # Unified parameters for best compatibility
        # h.264, yuv420p, 25fps, AAC Stereo 44100Hz
        common_args = [
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "25",
            "-profile:v", "high",
            "-level:v", "4.1",
            "-c:a", "aac",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "192k"
        ]
        
        if audio_path and audio_path.exists():
            audio_duration = self._get_audio_duration(audio_path)
            duration = max(duration, audio_duration)
            
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(image_path),
                "-i", str(audio_path),
                "-t", str(duration),
                "-vf", f"scale={self.config.video.resolution[0]}:{self.config.video.resolution[1]}:force_original_aspect_ratio=decrease,pad={self.config.video.resolution[0]}:{self.config.video.resolution[1]}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                "-shortest"
            ] + common_args + [str(video_path)]
        else:
            # Generate silent stereo audio
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(image_path),
                "-f", "lavfi",
                "-i", "anullsrc=r=44100:cl=stereo",
                "-t", str(duration),
                "-vf", f"scale={self.config.video.resolution[0]}:{self.config.video.resolution[1]}:force_original_aspect_ratio=decrease,pad={self.config.video.resolution[0]}:{self.config.video.resolution[1]}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                "-shortest"
            ] + common_args + [str(video_path)]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode == 0:
            size_mb = video_path.stat().st_size / (1024 * 1024)
            return PipelineResult(
                success=True,
                stage="video",
                message=f"Created: {video_path.name} ({size_mb:.1f} MB)",
                output_path=video_path,
                metadata={"duration": duration, "size_mb": size_mb}
            )
        else:
            error = result.stderr.decode()[:200]
            raise VideoGenerationError(f"FFmpeg failed: {error}")
    
    def create_full_episode(
        self,
        context: PipelineContext,
        intro_path: Optional[Path] = None
    ) -> PipelineResult:
        """Combine all scene videos using the concat demuxer (most robust)"""
        video_dir = context.output_dir / "video"
        output_path = context.get_full_episode_path()
        
        if not video_dir.exists():
            return PipelineResult(
                success=False,
                stage="full_episode",
                message=f"Video directory not found: {video_dir}",
                output_path=output_path
            )
        
        videos = sorted(video_dir.glob("scene_*.mp4"))
        
        # Step 1: Normalize Intro if exists
        temp_intro = None
        video_paths: List[Path] = []
        
        if intro_path and intro_path.exists():
            temp_intro = Path(tempfile.gettempdir()) / "normalized_intro.mp4"
            # Re-encode intro to match scenes exactly
            cmd = [
                "ffmpeg", "-y",
                "-i", str(intro_path),
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "25",
                "-profile:v", "high", "-level:v", "4.1",
                "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
                "-shortest",
                str(temp_intro)
            ]
            subprocess.run(cmd, capture_output=True)
            video_paths.append(temp_intro)
        
        video_paths.extend([v.absolute() for v in videos])
        
        if len(video_paths) == 0:
            return PipelineResult(
                success=False,
                stage="full_episode",
                message="No videos found to concatenate",
                output_path=output_path
            )

        # Step 2: Create concat list file
        list_file = Path(tempfile.gettempdir()) / f"concat_list_{context.episode.number}.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for v in video_paths:
                f.write(f"file '{v}'\n")
        
        # Step 3: Concat without re-encoding
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True)

        # Cleanup
        if list_file.exists():
            list_file.unlink()
        if temp_intro and temp_intro.exists():
            temp_intro.unlink()

        if result.returncode == 0:
            size_mb = output_path.stat().st_size / (1024 * 1024)
            return PipelineResult(
                success=True,
                stage="full_episode",
                message=f"Full episode: {output_path.name} ({size_mb:.1f} MB)",
                output_path=output_path,
                metadata={"scenes": len(videos), "size_mb": size_mb}
            )
        else:
            error = result.stderr.decode()
            print(f"FFmpeg error: {error}")
            raise VideoGenerationError(f"Failed to combine videos: {error[:200]}")
    
    def generate_episode(
        self,
        context: PipelineContext,
        engine: str = "openai"
    ) -> PipelineResult:
        """Generate videos for all scenes"""
        total_scenes = len(context.episode.scenes)
        completed = 0
        
        print(f"\n🎬 Creating videos for {total_scenes} scenes...")
        print("-" * 40)
        
        for scene in context.episode.scenes:
            try:
                result = self.create_scene_video(scene, context, engine=engine)
                if result.success:
                    completed += 1
                    print(f"  ✓ Scene {scene.id}")
                else:
                    print(f"  ✗ Scene {scene.id}: {result.message}")
            except Exception as e:
                print(f"  ✗ Scene {scene.id}: {e}")
        
        # Create full episode
        full_result = None
        if completed > 0:
            print("\n🎬 Combining into full episode...")
            intro = Path("assets/intro.mp4")
            full_result = self.create_full_episode(context, intro if intro.exists() else None)
            if full_result.success:
                print(f"  ✓ {full_result.message}")
        
        return PipelineResult(
            success=completed > 0,
            stage="video_episode",
            message=f"Videos: {completed}/{total_scenes} scenes + full episode",
            output_path=context.output_dir / "video",
            metadata={
                "completed": completed,
                "total": total_scenes,
                "full_episode": full_result.output_path if full_result else None
            }
        )


# Singleton instance
_video_service = None


def get_video_service() -> VideoService:
    """Get or create video service singleton"""
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service
