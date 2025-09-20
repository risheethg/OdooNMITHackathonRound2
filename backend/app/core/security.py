# app/core/security.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.database import Database
from typing import List

from firebase_admin import auth, exceptions

from app.core.db_connection import get_db
from app.models.user_model import User, UserRole
from app.repo.user_repo import UserRepository

# This will be used to extract the Bearer token from the Authorization header
oauth2_scheme = HTTPBearer()

async def get_current_user(
    db: Database = Depends(get_db), 
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current user from a Firebase ID token.
    Verifies the token, then fetches the user from the local database.
    """
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        uid = decoded_token.get("uid")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials: UID not found in token.",
            )
    except exceptions.FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}",
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_uid(uid)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found in our system. Please register first.",
        )
    
    return User.model_validate(user)

class RoleChecker:
    """
    Dependency that checks if the current user has one of the allowed roles.
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource."
            )