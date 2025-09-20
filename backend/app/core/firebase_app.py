import firebase_admin
from firebase_admin import credentials
from app.core.settings import settings
import os

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK.
    
    The SDK discovers credentials in the following order:
    1. The path specified by the `FIREBASE_CREDENTIALS_PATH` in the .env file.
    2. The path specified by the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.
    3. Default credentials from the environment (for services like Google App Engine).
    """
    # Prevent re-initialization which causes crashes on hot-reload
    if not firebase_admin._apps:
        print("Initializing Firebase App...")
        
        cred = None
        # Explicit path from .env takes precedence for local development
        if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            print(f"Found Firebase credentials at: {settings.FIREBASE_CREDENTIALS_PATH}")
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            print("Found Firebase credentials in GOOGLE_APPLICATION_CREDENTIALS env var.")
            # Let the SDK handle it automatically by passing None
        else:
            print("No explicit Firebase credentials found. Relying on default environment discovery.")

        # If cred is None, the SDK will attempt its default discovery process.
        firebase_admin.initialize_app(cred)