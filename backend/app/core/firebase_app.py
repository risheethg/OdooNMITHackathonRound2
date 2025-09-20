import firebase_admin

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK.
    
    The SDK automatically discovers credentials via the 
    GOOGLE_APPLICATION_CREDENTIALS environment variable set in docker-compose.yml.
    """
    print("Initializing Firebase App...") # This is the log message we saw
    
    # By calling initialize_app() with no arguments, the SDK looks for the
    # standard environment variable. We no longer need to manually load
    # the certificate from a path.
    firebase_admin.initialize_app()