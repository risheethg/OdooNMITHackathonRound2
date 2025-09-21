import os
import logging
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages all application settings by loading them from environment variables
    or a .env file. It includes validation to ensure required files exist.
    """
    
    # --- MongoDB Settings
    MONGO_URI: str
    MONGO_DB_NAME: str
    
    # --- Logger Settings
    LOGGER: int = logging.INFO 
    
    # --- JWT Settings
    secret_key: str
    access_token_expire_minutes: int = 60 * 24 * 8  # 8 days

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        Validates that the SECRET_KEY is provided and not empty.
        """
        if not v or len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be provided and be at least 32 characters long. "
                "Generate one with: openssl rand -hex 32"
            )
        return v
    
    # Configure Pydantic to load from a .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()