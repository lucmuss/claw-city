# -*- coding: utf-8 -*-
"""Configuration management for the Claw City pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class TTSConfig:
    provider: str = "openai"
    openai_model: str = "tts-1"
    openai_voice: str = "alloy"
    edge_voice: str = "de-DE-ConradNeural"

    @classmethod
    def from_env(cls) -> TTSConfig:
        return cls(
            provider=os.getenv("TTS_PROVIDER", "openai"),
            openai_model=os.getenv("OPENAI_TTS_MODEL", "tts-1"),
            openai_voice=os.getenv("OPENAI_TTS_VOICE", "alloy"),
            edge_voice=os.getenv("EDGE_TTS_VOICE", "de-DE-ConradNeural"),
        )


@dataclass
class ImageConfig:
    provider: str = "replicate"
    model: str = "black-forest-labs/flux-schnell"
    aspect_ratio: str = "16:9"
    output_format: str = "png"
    output_quality: int = 90
    rate_limit_delay: int = 12
    max_retries: int = 3
    max_workers: int = 3
    style_suffix: str = (
        "Simpsons cartoon art style, clean vector lines, warm colors, "
        "friendly characters, simple backgrounds, professional animation quality, "
        "2D cartoon, flat colors, expressive faces"
    )

    @classmethod
    def from_env(cls) -> ImageConfig:
        return cls(
            provider=os.getenv("IMAGE_PROVIDER", "replicate"),
            model=os.getenv("REPLICATE_MODEL", "black-forest-labs/flux-schnell"),
            aspect_ratio=os.getenv("IMAGE_ASPECT_RATIO", "16:9"),
            output_format=os.getenv("IMAGE_OUTPUT_FORMAT", "png"),
            output_quality=int(os.getenv("IMAGE_OUTPUT_QUALITY", "90")),
            rate_limit_delay=int(os.getenv("RATE_LIMIT_DELAY", "12")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            max_workers=int(os.getenv("MAX_WORKERS", "3")),
        )


@dataclass
class VideoConfig:
    resolution: tuple[int, int] = (1920, 1080)
    codec: str = "libx264"
    audio_codec: str = "aac"
    pix_fmt: str = "yuv420p"
    default_duration: int = 8

    @classmethod
    def from_env(cls) -> VideoConfig:
        width = int(os.getenv("VIDEO_WIDTH", "1920"))
        height = int(os.getenv("VIDEO_HEIGHT", "1080"))
        return cls(
            resolution=(width, height),
            default_duration=int(os.getenv("SCENE_DURATION", "8")),
        )


@dataclass
class AppConfig:
    project_name: str = "Claw City"
    version: str = "0.1.0"
    debug: bool = False

    tts: TTSConfig = field(default_factory=TTSConfig.from_env)
    images: ImageConfig = field(default_factory=ImageConfig.from_env)
    video: VideoConfig = field(default_factory=VideoConfig.from_env)

    openai_api_key: str | None = None
    replicate_api_token: str | None = None

    base_dir: Path = field(default_factory=lambda: Path.cwd())
    scripts_dir: Path = field(default_factory=lambda: Path("scripts"))
    output_dir: Path = field(default_factory=lambda: Path("output"))
    assets_dir: Path = field(default_factory=lambda: Path("assets"))
    configs_dir: Path = field(default_factory=lambda: Path("configs"))
    data_dir: Path = field(default_factory=lambda: Path("data"))

    def __post_init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
        self.debug = _env_bool("DEBUG", default=False)

    @classmethod
    def load(cls, config_path: Path | None = None) -> AppConfig:
        """Load configuration from file and environment."""
        load_dotenv()
        config = cls()

        if config_path is None:
            config_path = config.configs_dir / "pipeline_settings.yaml"

        if config_path.exists():
            with open(config_path, encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
                if data:
                    config._merge_yaml(data)

        return config

    def _merge_yaml(self, data: dict[str, Any]) -> None:
        """Merge YAML configuration data into the current config."""
        if "project" in data:
            self.project_name = data["project"].get("name", self.project_name)

        if "image_generation" in data:
            img = data["image_generation"]
            self.images.provider = img.get("provider", self.images.provider)
            self.images.style_suffix = img.get(
                "prompt_suffix", self.images.style_suffix
            )

        if "output" in data:
            out = data["output"]
            if "base_dir" in out:
                self.output_dir = Path(out["base_dir"])

        if "api" in data and "replicate" in data["api"]:
            rep = data["api"]["replicate"]
            self.images.rate_limit_delay = rep.get(
                "rate_limit_delay", self.images.rate_limit_delay
            )
            self.images.max_workers = rep.get("max_workers", self.images.max_workers)


_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = AppConfig.load()
    return _config


def reload_config() -> None:
    """Reload configuration from disk and environment."""
    global _config
    _config = AppConfig.load()
