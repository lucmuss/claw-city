# -*- coding: utf-8 -*-
"""Custom exceptions for the Claw City pipeline."""


class ClawCityError(Exception):
    """Base exception for all Claw City errors."""


class ConfigurationError(ClawCityError):
    """Raised when there is a configuration problem."""


class ScriptError(ClawCityError):
    """Raised when there is a script or YAML problem."""


class AudioGenerationError(ClawCityError):
    """Raised when audio generation fails."""


class ImageGenerationError(ClawCityError):
    """Raised when image generation fails."""


class VideoGenerationError(ClawCityError):
    """Raised when video generation fails."""


class PipelineError(ClawCityError):
    """Raised when pipeline execution fails."""


class RateLimitError(ClawCityError):
    """Raised when API rate limit is hit."""


class APIError(ClawCityError):
    """Raised when an API call fails."""
