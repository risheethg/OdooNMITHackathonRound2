import firebase_admin
from firebase_admin import credentials
from app.core.settings import settings
import os
from pathlib import Path  # <-- Import the Path object

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK using a robust absolute path.
    """
    # Prevent re-initialization which causes crashes on hot-reload
    if not firebase_admin._apps:
        print("Initializing Firebase App...")
        
        cred = None
        
        # Explicit path from .env takes precedence for local development
        if settings.FIREBASE_CREDENTIALS_PATH:
            
            # --- START OF MODIFICATION ---
            
            # This logic converts your relative path from .env into an absolute path.
            # It assumes your .env path is relative to the project's root directory.
            
            # 1. Get the directory of the current file (e.g., /path/to/project/app/core)
            current_dir = Path(__file__).parent
            
            # 2. Navigate up to the project root. 
            #    If this file is in `app/core/`, the root is two levels up.
            #    Adjust `.parent.parent` if your file is in a different location.
            project_root = current_dir.resolve().parent.parent
            
            # 3. Join the project root with the relative path from your settings.
            absolute_path = project_root / settings.FIREBASE_CREDENTIALS_PATH
            
            print(f"Constructed absolute path to credentials: {absolute_path}")
            
            # 4. Check if the file exists at the new absolute path.
            if absolute_path.exists():
                print(f"✅ Credentials file found at: {absolute_path}")
                cred = credentials.Certificate(absolute_path)
            else:
                print(f"❌ WARNING: Credentials file NOT found at '{absolute_path}'.")
                print("    Please check that FIREBASE_CREDENTIALS_PATH in your .env file is correct.")
                print("    The path should be relative to your project root directory.")

            # --- END OF MODIFICATION ---

        # Fallback to GOOGLE_APPLICATION_CREDENTIALS if the explicit path failed
        if not cred and os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            print("Found Firebase credentials in GOOGLE_APPLICATION_CREDENTIALS env var.")
            # Let the SDK handle it automatically by passing None
        elif not cred:
            print("No explicit Firebase credentials found. Relying on default environment discovery.")

        # If cred is None, the SDK will attempt its default discovery process.
        firebase_admin.initialize_app(cred)