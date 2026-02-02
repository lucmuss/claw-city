"""Data models for Claw City pipeline"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any
from enum import Enum


class ProcessingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Character:
    id: str
    name: str
    voice: str = "alloy"
    archetype: str = ""
    folder: Optional[Path] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        return cls(
            id=data["id"],
            name=data["name"],
            voice=data.get("voice", "alloy"),
            archetype=data.get("archetype", ""),
            folder=Path(data["folder"]) if "folder" in data else None
        )


@dataclass
class DialogueLine:
    character: str
    text: str
    emotion: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueLine":
        return cls(
            character=data["character"],
            text=data["text"],
            emotion=data.get("emotion")
        )


@dataclass
class Scene:
    id: int
    title: str
    location: str
    time: str
    duration: str
    image_prompt: str
    dialogue: List[DialogueLine] = field(default_factory=list)
    status: ProcessingStatus = ProcessingStatus.PENDING
    visual_summary: Optional[str] = None # For context window
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        return cls(
            id=data["id"],
            title=data.get("title", f"Scene {data['id']}"),
            location=data.get("location", ""),
            time=data.get("time", ""),
            duration=data.get("duration", "10 sec"),
            image_prompt=data["image_prompt"],
            dialogue=[DialogueLine.from_dict(d) for d in data.get("dialogue", [])],
            visual_summary=data["image_prompt"] # Default to image_prompt as visual summary
        )
    
    @property
    def full_text(self) -> str:
        return " ".join([d.text for d in self.dialogue])
    
    @property
    def duration_seconds(self) -> int:
        """Parse duration string like '25 sec' to seconds"""
        try:
            return int(self.duration.split()[0])
        except (ValueError, IndexError):
            return 10


@dataclass
class Episode:
    number: int
    title: str
    subtitle: Optional[str] = None
    duration: Optional[str] = None
    tone: Optional[str] = None
    themes: List[str] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        ep_data = data.get("episode", {})
        return cls(
            number=ep_data["number"],
            title=ep_data["title"],
            subtitle=ep_data.get("subtitle"),
            duration=ep_data.get("duration"),
            tone=ep_data.get("tone"),
            themes=ep_data.get("themes", []),
            scenes=[Scene.from_dict(s) for s in data.get("scenes", [])]
        )
    
    @property
    def scene_count(self) -> int:
        return len(self.scenes)
    
    @property
    def total_duration_seconds(self) -> int:
        return sum(s.duration_seconds for s in self.scenes)


@dataclass
class PipelineContext:
    episode: Episode
    output_dir: Path
    config: Dict[str, Any] = field(default_factory=dict)
    characters: Dict[str, Character] = field(default_factory=dict)
    
    def get_scene_dir(self, scene_id: int) -> Path:
        return self.output_dir / f"scene_{scene_id:02d}"
    
    def get_image_path(self, scene_id: int) -> Path:
        return self.output_dir / "images" / f"scene_{scene_id:02d}.png"
    
    def get_audio_dir(self, scene_id: int, engine: str = "openai") -> Path:
        return self.output_dir / f"audio_{engine}" / f"scene_{scene_id:02d}"
    
    def get_video_path(self, scene_id: int) -> Path:
        return self.output_dir / "video" / f"scene_{scene_id:02d}.mp4"
    
    def get_full_episode_path(self) -> Path:
        return self.output_dir / f"EP{self.episode.number:02d}_FULL.mp4"


@dataclass
class PipelineResult:
    success: bool
    stage: str
    message: str
    output_path: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
