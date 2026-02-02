"""Custom exceptions for Claw City pipeline"""


class ClawCityError(Exception):
    """Base exception for all Claw City errors"""
    pass


class ConfigurationError(ClawCityError):
    """Raised when there's a configuration problem"""
    pass


class ScriptError(ClawCityError):
    """Raised when there's a problem with the script/YAML"""
    pass


class AudioGenerationError(ClawCityError):
    """Raised when audio generation fails"""
    pass


class ImageGenerationError(ClawCityError):
    """Raised when image generation fails"""
    pass


class VideoGenerationError(ClawCityError):
    """Raised when video generation fails"""
    pass


class PipelineError(ClawCityError):
    """Raised when pipeline execution fails"""
    pass


class RateLimitError(ClawCityError):
    """Raised when API rate limit is hit"""
    pass


class APIError(ClawCityError):
    """Raised when an API call fails"""
    pass
