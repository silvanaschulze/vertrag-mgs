"""Application configuration management.

This module defines the :class:`Settings` object used across the
application.  The configuration is based on Pydantic settings so it can be
customised via environment variables when the service is deployed.  When no
variables are provided sensible defaults that work for development are
used.
"""

from functools import lru_cache
from typing import List, Annotated, cast

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # strings e ints com defaults simples (Pylance entende):
    PROJECT_NAME: Annotated[str, Field(description="Human friendly application name.")] = "Contract Management System"
    API_V1_STR: Annotated[str, Field(description="Prefix for API routes.")] = "/api"
    SECRET_KEY: Annotated[str, Field(description="Secret key used to sign JWT tokens.")] = "change-me"

    ACCESS_TOKEN_EXPIRE_MINUTES: Annotated[int, Field(description="Default expiration time for access tokens in minutes.")] = 30
    REFRESH_TOKEN_EXPIRE_DAYS: Annotated[int, Field(description="Default expiration time for refresh tokens in days.")] = 7

    # Usar banco da raiz onde estão os 252 contratos existentes
    SQLALCHEMY_DATABASE_URI: Annotated[str, Field(description="Database connection string.")] = "sqlite+aiosqlite:////home/sschulze/projects/vertrag-mgs/contracts.db"

    # listas com default_factory (mantém Field, agora visível para type checker)
    BACKEND_CORS_ORIGINS: Annotated[
        List[AnyHttpUrl],
        Field(description="List of origins allowed by CORS."),
    ] = Field(
        default_factory=lambda: [
            cast(AnyHttpUrl, "http://localhost:5173"),
            cast(AnyHttpUrl, "http://si-server.mshome.net:5173"),
            cast(AnyHttpUrl, "http://localhost:3000"),
        ],
    )
    
         
    # SMTP
    SMTP_HOST: Annotated[str, Field(description="SMTP server host / Servidor SMTP")] = "localhost"
    SMTP_PORT: Annotated[int, Field(description="SMTP server port / Porta SMTP")] = 587
    SMTP_USER: Annotated[str, Field(description="SMTP username / Usuário SMTP")] = ""
    SMTP_PASSWORD: Annotated[str, Field(description="SMTP password / Senha SMTP")] = ""
    SMTP_USE_TLS: Annotated[bool, Field(description="Use TLS for SMTP / Usar TLS para SMTP")] = True

    # Upload
    MAX_FILE_SIZE: Annotated[int, Field(description="Maximum file size in bytes / Tamanho máximo do arquivo em bytes")] = 10 * 1024 * 1024
    UPLOAD_DIR: Annotated[str, Field(description="Upload directory / Diretório de upload")] = "uploads"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()
