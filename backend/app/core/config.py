"""Application configuration management.

This module defines the :class:`Settings` object used across the
application.  The configuration is based on Pydantic settings so it can be
customised via environment variables when the service is deployed.  When no
variables are provided sensible defaults that work for development are
used.
"""

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, BaseSettings, Field


class Settings(BaseSettings):
    """Central application configuration."""

    PROJECT_NAME: str = Field(
        "Contract Management System",
        description="Human friendly application name.",
    )
    API_V1_STR: str = Field("/api", description="Prefix for API routes.")
    SECRET_KEY: str = Field(
        "change-me", description="Secret key used to sign JWT tokens."
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30, description="Default expiration time for access tokens in minutes."
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        7, description="Default expiration time for refresh tokens in days."
    )

    SQLALCHEMY_DATABASE_URI: str = Field(
        "sqlite+aiosqlite:///./contracts.db",
        description="Database connection string.",
    )

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default_factory=list,
        description="List of origins allowed by CORS.",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""

    return Settings()


settings = get_settings()
