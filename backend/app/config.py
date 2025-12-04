"""
CONFIG.PY - Simple configuration without pydantic-settings

We use:
- python-dotenv to load .env values (if present)
- os.getenv to read environment variables
"""

import os
from functools import lru_cache

from dotenv import load_dotenv

# Load variables from .env file in backend folder (if it exists)
# e.g. DATABASE_URL=sqlite:///./dropout_prediction.db
load_dotenv()


class Settings:
    """
    Simple settings object.
    Values are read from environment variables if present,
    otherwise fall back to defaults.
    """

    def __init__(self) -> None:
        # Database URL
        # Example: sqlite:///./dropout_prediction.db
        #          postgresql://user:password@host/dbname
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            "sqlite:///./dropout_prediction.db",
        )

        # Secret key for JWT
        self.SECRET_KEY: str = os.getenv(
            "SECRET_KEY",
            "change-this-secret-key-in-production",
        )

        # JWT algorithm
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

        # Token expiry in minutes (default: 24 hours)
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
        )

        # Debug flag (not used heavily, but available)
        self.DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Using lru_cache so Settings() is created only once.
    """
    return Settings()


# This is what the rest of the app imports
settings = get_settings()