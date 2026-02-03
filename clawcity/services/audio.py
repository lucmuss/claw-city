"""Audio generation service with multiple TTS providers"""
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

from clawcity.core.config import get_config
from clawcity.core.exceptions import AudioGenerationError, ConfigurationError
from clawcity.core.models import Scene, PipelineContext, PipelineResult


# Voice mapping for characters (OpenAI)
VOICE_MAP: Dict[str, str] = {
    "narrator": "nova",
    "max": "echo",
    "gina": "shimmer",
    "werner": "onyx",
    "eric": "fable",
    "herbert": "alloy",
    "oma_gerda": "nova",
    "tim_tim": "echo",
    "lisa": "shimmer",
    "lena": "shimmer",
    "beate": "nova",
    "günther": "onyx",
    "berthold": "onyx",
    "fiona": "shimmer",
    "heinrich": "alloy",
    "sabrina": "shimmer",
    "app": "alloy",
    "paul": "alloy",
}

# Voice mapping for characters (Edge TTS)
EDGE_VOICE_MAP: Dict[str, str] = {
    "narrator": "de-DE-ConradNeural",
    "max": "de-DE-KillianNeural",
    "gina": "de-DE-KatjaNeural",
    "werner": "de-DE-FlorianMultilingualNeural",
    "eric": "de-DE-KillianNeural",
    "herbert": "de-DE-ConradNeural",
    "oma_gerda": "de-DE-SeraphinaMultilingualNeural",
    "tim_tim": "de-DE-AmalaNeural",
    "lisa": "de-DE-KatjaNeural",
    "lena": "de-DE-KatjaNeural",
    "beate": "de-DE-SeraphinaMultilingualNeural",
    "günther": "de-DE-FlorianMultilingualNeural",
    "berthold": "de-DE-FlorianMultilingualNeural",
    "fiona": "de-DE-KatjaNeural",
    "heinrich": "de-DE-ConradNeural",
    "sabrina": "de-DE-AmalaNeural",
    "app": "de-DE-SeraphinaMultilingualNeural",
    "paul": "de-DE-FlorianMultilingualNeural",
    "default": "de-DE-ConradNeural"
}


class AudioService:
    """Service for generating audio from text"""
    
    def __init__(self, provider: Optional[str] = None):
        self.config = get_config()
        self.provider = provider or self.config.tts.provider
        self._openai_client: Optional[OpenAI] = None
        
        if self.provider == "openai" and not HAS_OPENAI:
            raise ConfigurationError("OpenAI package not installed. Install with: pip install openai")
        if self.provider == "edge" and not HAS_EDGE_TTS:
            raise ConfigurationError("edge-tts package not installed. Install with: pip install edge-tts")
    
    @property
    def openai_client(self):
        """Lazy initialization of OpenAI client"""
        if self._openai_client is None:
            if not self.config.openai_api_key:
                raise ConfigurationError("OPENAI_API_KEY not set")
            self._openai_client = OpenAI(api_key=self.config.openai_api_key)
        return self._openai_client
    
    def get_voice(self, character: str) -> str:
        """Get voice for character"""
        char_id = character.lower()
        if self.provider == "openai":
            return VOICE_MAP.get(char_id, "alloy")
        else:
            # Edge TTS - try character-specific voice, then fallback
            return EDGE_VOICE_MAP.get(char_id, EDGE_VOICE_MAP["default"])
    
    async def generate_line(
        self,
        text: str,
        character: str,
        output_path: Path,
        emotion: Optional[str] = None
    ) -> PipelineResult:
        """Generate audio for a single dialogue line"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.exists():
            return PipelineResult(
                success=True,
                stage="audio",
                message=f"Skipped (exists): {output_path.name}",
                output_path=output_path
            )
        
        try:
            if self.provider == "openai":
                await self._generate_openai(text, character, output_path)
            else:
                await self._generate_edge(text, character, output_path)
            
            return PipelineResult(
                success=True,
                stage="audio",
                message=f"Generated: {output_path.name}",
                output_path=output_path
            )
        except Exception as e:
            raise AudioGenerationError(f"Failed to generate audio for {character}: {e}")
    
    async def _generate_openai(self, text: str, character: str, output_path: Path):
        """Generate using OpenAI TTS"""
        voice = self.get_voice(character)
        
        response = self.openai_client.audio.speech.create(
            model=self.config.tts.openai_model,
            voice=voice,
            input=text,
            response_format="mp3"
        )
        
        response.stream_to_file(str(output_path))
    
    async def _generate_edge(self, text: str, character: str, output_path: Path):
        """Generate using Edge TTS"""
        voice = self.get_voice(character)
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
    
    async def generate_scene(
        self,
        scene: Scene,
        context: PipelineContext,
        engine: str = "openai"
    ) -> PipelineResult:
        """Generate audio for all lines in a scene and combine them"""
        audio_dir = context.get_audio_dir(scene.id, engine)
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        generated = 0
        failed = 0
        
        # Temporarily switch provider for this scene if engine matches
        old_provider = self.provider
        self.provider = engine
        
        try:
            for i, line in enumerate(scene.dialogue):
                output_path = audio_dir / f"{i:03d}_{line.character}.mp3"
                
                result = await self.generate_line(
                    text=line.text,
                    character=line.character,
                    output_path=output_path,
                    emotion=line.emotion
                )
                
                if result.success:
                    generated += 1
                else:
                    failed += 1
        finally:
            self.provider = old_provider
        
        # Combine scene audio immediately after generation
        if failed == 0 and generated > 0:
            from clawcity.services.video import get_video_service
            video_service = get_video_service()
            video_service.combine_scene_audio(audio_dir)
        
        return PipelineResult(
            success=failed == 0,
            stage="audio_scene",
            message=f"Scene {scene.id}: {generated} generated, {failed} failed",
            output_path=audio_dir,
            metadata={"generated": generated, "failed": failed, "total": len(scene.dialogue)}
        )
    
    async def generate_episode(
        self,
        context: PipelineContext,
        engine: str = "openai"
    ) -> PipelineResult:
        """Generate audio for entire episode"""
        total_scenes = len(context.episode.scenes)
        completed = 0
        failed = 0
        
        print(f"\n🎤 Generating audio for {total_scenes} scenes...")
        print(f"   Engine: {engine}")
        print(f"   Estimated cost: ~${total_scenes * 0.015:.2f}")
        print("-" * 40)
        
        for scene in context.episode.scenes:
            try:
                result = await self.generate_scene(scene, context, engine)
                if result.success:
                    completed += 1
                    print(f"  ✓ Scene {scene.id}")
                else:
                    failed += 1
                    print(f"  ✗ Scene {scene.id} (partial)")
            except Exception as e:
                failed += 1
                print(f"  ✗ Scene {scene.id}: {e}")
        
        return PipelineResult(
            success=failed == 0,
            stage="audio_episode",
            message=f"Audio: {completed}/{total_scenes} scenes complete",
            metadata={"completed": completed, "failed": failed, "total": total_scenes}
        )


# Singleton instance
_audio_service = None


def get_audio_service() -> AudioService:
    """Get or create audio service singleton"""
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService()
    return _audio_service
