# app/core/security.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.database import Database
from typing import List

from app.core.db_connection import get_db
from app.core.auth import verify_token
from app.models.user_model import User, UserRole
from app.repo.user_repo import UserRepository

# This will be used to extract the Bearer token from the Authorization header
oauth2_scheme = HTTPBearer()

async def get_current_user(
    db: Database = Depends(get_db), 
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current user from a JWT token.
    Verifies the token, then fetches the user from the local database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify the JWT token
    user_id = verify_token(token.credentials)
    if user_id is None:
        raise credentials_exception
    
    # Fetch the user from the database
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if user is None:
        raise credentials_exception
    
    return User.model_validate(user)

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    A dependency that returns the current authenticated user.
    Use this for all endpoints that require an authenticated user.
    """
    return current_user

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
        return user