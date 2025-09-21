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
    # --- Firebase Settings
    # Defaults to 'serviceAccountToken.json' if the env var is not set.
    GOOGLE_APPLICATION_CREDENTIALS: str = "serviceAccountToken.json"

    @field_validator("GOOGLE_APPLICATION_CREDENTIALS")
    @classmethod
    def validate_firebase_creds(cls, v: str) -> str:
        """
        Validates that the Firebase service account file exists at the given path.
        """
        if not os.path.exists(v):
            raise FileNotFoundError(
                f"Firebase credentials file not found at: '{v}'. "
                "Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable "
                "or place the file in the project's root directory."
            )
        return v
    
    # Configure Pydantic to load from a .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False  # <-- Add this line
    )

# Create a single, reusable instance of the settings
settings = Settings()