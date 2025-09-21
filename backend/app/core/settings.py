import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Manages all application settings by loading them from environment variables
    or a .env file.
    """
    
    # --- MongoDB Settings
    MONGO_URI: str
    MONGO_DB_NAME: str
    
    # --- Logger Settings
    LOGGER: int = logging.INFO

    # Configure Pydantic to load from a .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
