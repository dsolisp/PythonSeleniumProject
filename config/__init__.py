"""Configuration package initialization."""

# Import the simple working settings for now
try:
    from .simple_settings import settings

    __all__ = ["settings"]
except ImportError:
    # Fallback if simple_settings doesn't exist
    settings = None
    __all__ = []
