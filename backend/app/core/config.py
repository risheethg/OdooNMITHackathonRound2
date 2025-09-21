import os
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

class Settings(BaseSettings):
    """
    Manages all application settings by loading them from environment variables
    or a .env file. It includes validation to ensure required files exist.
    """
    
    # --- MongoDB Settings
    MONGO_URI: str
    MONGO_DB_NAME: str
    LOGGER: int = logging.INFO 

    
    # Configure Pydantic to load from a .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Create a single, reusable instance of the settings
settings = Settings()