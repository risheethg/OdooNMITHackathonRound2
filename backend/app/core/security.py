from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

# Import the User model and the user repository
from app.models.user_models import User, UserRole
from app.repo.users_repo import users_repo

oauth2_scheme = HTTPBearer()

def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> dict:
    """
    Dependency to get and verify the Firebase ID token.
    It returns the raw decoded token dictionary.
    
    Use this for endpoints like /register where you only need the token
    to be valid, but don't need the user to exist in your database yet.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during token verification: {e}",
        )


async def get_current_active_user(
    decoded_token: dict = Depends(get_current_user_token)
) -> User:
    """
    A dependency that:
    1. Verifies the token using `get_current_user_token`.
    2. Fetches the user's profile from your Firestore database.
    3. Checks if the user exists and is active.
    
    Use this for all endpoints that require an authenticated user
    who already has a profile in your database (e.g., /me, /login, etc.).
    """
    user_uid = decoded_token.get("uid")
    if not user_uid:
        raise HTTPException(status_code=400, detail="User ID (uid) not found in token.")
    
    # Fetch the user from Firestore
    user = await users_repo.get(uid=user_uid)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please complete registration.",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user account is inactive.")
        
    return user


class RoleChecker:
    """
    A dependency class to check for user roles.
    This is used as a factory to create a dependency that checks
    if the current user has any of the required roles.
    
    Usage:
    @app.get("/admin", dependencies=[Depends(RoleChecker(["admin"]))])
    """
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)):
        if not any(role in self.allowed_roles for role in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have the required permissions. Allowed roles: {', '.join(self.allowed_roles)}"
            )