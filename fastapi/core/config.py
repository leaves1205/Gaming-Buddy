"""
Load all configuration values from fastapi/.env.

This file declares configuration keys and their types.
- Update database passwords and secrets in .env
- Declare a new setting here and add its value in .env
"""
# Standard-library path handling to locate .env
from pathlib import Path

# Base settings class and configuration options for loading .env
from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file lives in fastapi/, one level above this file, regardless of the working directory.
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")  # Set the .env path and encoding and ignore undeclared variables

    # Database
    db_host: str  # Database host
    db_port: int  # Database port
    db_user: str  # Database username
    db_password: str  # Database password
    db_name: str  # Database name

    # JWT tokens
    token_header: str  # Request header containing the token (Authorization)
    token_secret: str  # JWT signing key. Changing it invalidates all previously issued tokens.
    token_expire_minutes: int  # Token lifetime in minutes

    # API documentation
    docs_enabled: bool  # Enable the API documentation endpoints (/docs, /redoc, /openapi.json)

    # Upload base path
    profile: str  # Root directory for avatars and general uploads

    @property
    def database_url(self) -> str:
        """Build the SQLAlchemy database connection string"""
        return (  # Format: protocol://username:password@host:port/database?charset
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


settings = Settings()  # Load settings at import time. Other modules import settings from core.config.
