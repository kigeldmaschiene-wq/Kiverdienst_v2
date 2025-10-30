"""
Routes package initialization
"""
from .setup import bp as setup_bp
from .brands import bp as brands_bp
from .videos import bp as videos_bp
from .characters import bp as characters_bp
from .system import bp as system_bp
from .content import bp as content_bp

__all__ = ['setup_bp', 'brands_bp', 'videos_bp', 'characters_bp', 'system_bp', 'content_bp']
