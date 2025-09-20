import firebase_admin
from .config import settings
from firebase_admin import credentials

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK.
    
    It loads credentials from a service account file specified by
    the `get_firebase_credentials` config function.
    """
    print("Initializing Firebase App...") # This is the log message we saw
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
        firebase_admin.initialize_app(cred)