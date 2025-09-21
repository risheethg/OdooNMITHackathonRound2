from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.security import get_current_user
from app.models.user_model import User, CreateUserSchema
from app.service.user_service import UserService, get_user_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    data: CreateUserSchema,
    service: UserService = Depends(get_user_service)
):
    """
    Register a new user.
    This creates a user in Firebase Authentication and in the local database.
    """
    result = service.create_user(data)
    return JSONResponse(status_code=result["status_code"], content=result)

@router.post("/login", response_model=User)
async def login(
    current_user: User = Depends(get_current_user)
):
    """
    Handles user "login" for our backend.
    The client should provide a valid Firebase ID token in the Authorization header as a Bearer token.
    If the token is valid and the user exists in our database, this returns their profile.
    """
    return current_user

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Fetches the profile for the currently authenticated user.
    """
    return current_user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user():
    """
    Client-side responsibility. This endpoint is a placeholder.
    The client should discard the Firebase ID token.
    """
    return None