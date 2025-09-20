from firebase_admin import firestore
from google.cloud.firestore_v1.async_client import AsyncClient

def get_firestore_client() -> AsyncClient:
    """
    Returns an authenticated Firestore client instance.
    
    The firebase_admin.initialize_app() call in main.py handles the
    authentication, so we can just get the client here.
    """
    return firestore.client()