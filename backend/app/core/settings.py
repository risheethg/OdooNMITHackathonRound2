from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Settings class to manage environment variables for the application.
    It automatically reads variables from a .env file.
    """
    # MongoDB connection string.
    MONGO_URI: str = "mongodb://localhost:27017/"

    # The name of the database to use.
    MONGO_DB_NAME: str = "manufacturing_db"

    class Config:
        # Specifies the file from which to load the environment variables.
        env_file = ".env"

# Create a single instance of the settings to be used throughout the application.
# This pattern ensures that the .env file is read only once.
settings = Settings()
