"""
dependencies.py
----------------
FastAPI dependency injection helpers.
If you later add authentication (JWT tokens, OAuth), add them here.
"""

from app.config import settings


def get_settings():
    """Dependency that returns the application settings."""
    return settings
