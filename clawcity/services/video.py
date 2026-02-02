"""Video generation service using FFmpeg"""
import subprocess
import os
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
        """Combine all audio files in a scene directory"""
        audio_files = sorted(audio_dir.glob("*.mp3"))
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
        
        output_path = audio_dir / "combined.mp3"
        combined.export(str(output_path), format="mp3")
        return output_path
    
    def create_scene_video(
        self,
        scene: Scene,
        context: PipelineContext,
        audio_dir: Optional[Path] = None,
        engine: str = "openai"
    ) -> PipelineResult:
        """Create video for a single scene"""
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
        
        if video_path.exists():
            return PipelineResult(
                success=True,
                stage="video",
                message=f"Skipped (exists): {video_path.name}",
                output_path=video_path
            )
        
        # Get audio
        if audio_dir is None:
            audio_dir = context.get_audio_dir(scene.id, engine)
        
        audio_path = self.combine_scene_audio(audio_dir)
        duration = scene.duration_seconds
        
        # Build FFmpeg command
        if audio_path and audio_path.exists():
            audio_duration = self._get_audio_duration(audio_path)
            duration = max(duration, audio_duration)
            
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(image_path),
                "-i", str(audio_path),
                "-c:v", self.config.video.codec,
                "-c:a", self.config.video.audio_codec,
                "-shortest",
                "-b:a", "192k", # Erzwinge 192k Audio-Bitrate
                "-t", str(duration),
                "-pix_fmt", self.config.video.pix_fmt,
                "-vf", f"scale={self.config.video.resolution[0]}:{self.config.video.resolution[1]}:force_original_aspect_ratio=decrease,pad={self.config.video.resolution[0]}:{self.config.video.resolution[1]}:(ow-iw)/2:(oh-ih)/2",
                str(video_path)
            ]
        else:
            # No audio - use default duration
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(image_path),
                "-c:v", self.config.video.codec,
                "-t", str(duration),
                "-pix_fmt", self.config.video.pix_fmt,
                "-vf", f"scale={self.config.video.resolution[0]}:{self.config.video.resolution[1]}:force_original_aspect_ratio=decrease,pad={self.config.video.resolution[0]}:{self.config.video.resolution[1]}:(ow-iw)/2:(oh-ih)/2",
                "-an",
                str(video_path)
            ]
        
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
        """Combine all scene videos into full episode with filter_complex for audio"""
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
        
        video_paths: List[Path] = []
        if intro_path and intro_path.exists():
            video_paths.append(intro_path.absolute())
        
        video_paths.extend([v.absolute() for v in videos])
        
        if len(video_paths) == 0:
            return PipelineResult(
                success=False,
                stage="full_episode",
                message="No videos found to concatenate",
                output_path=output_path
            )
        
        # Nur 1 Video? Direkt kopieren
        if len(video_paths) == 1:
            import shutil
            shutil.copy2(video_paths[0], output_path)
            size_mb = output_path.stat().st_size / (1024 * 1024)
            return PipelineResult(
                success=True,
                stage="full_episode",
                message=f"Full episode (single): {output_path.name} ({size_mb:.1f} MB)",
                output_path=output_path,
                metadata={"scenes": len(videos), "size_mb": size_mb}
            )

        # Methode: Filter Complex (robusteste Audio/Video-Zusammenführung)
        # Baut separate Video- und Audio-Streams und konkateniert diese explizit
        
        n = len(video_paths)
        
        # Build input arguments
        input_args = []
        for v in video_paths:
            input_args.extend(["-i", str(v)])
        
        # Build filter_complex
        # Concatenate video streams: [0:v][1:v][2:v]...concat=n=N:v=1:a=0[outv]
        # Concatenate audio streams: [0:a][1:a][2:a]...concat=n=N:v=0:a=1[outa]
        video_concat = "".join([f"[{i}:v]" for i in range(n)])
        audio_concat = "".join([f"[{i}:a]" for i in range(n)])
        
        filter_complex = (
            f"{video_concat}concat=n={n}:v=1:a=0[outv];"
            f"{audio_concat}concat=n={n}:v=0:a=1[outa]"
        )
        
        cmd = [
            "ffmpeg", "-y"
        ] + input_args + [
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", self.config.video.codec,
            "-c:a", self.config.video.audio_codec,
            "-b:a", "192k",
            "-pix_fmt", self.config.video.pix_fmt,
            str(output_path)
        ]
        
        # Run command
        result = subprocess.run(cmd, capture_output=True)

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
