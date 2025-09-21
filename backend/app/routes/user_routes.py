from fastapi import APIRouter, Depends, status, HTTPException
from app.service.user_service import UserService, get_user_service
from app.models.user_model import CreateUserSchema, UserLogin, UserRole, User, UserResponse
from app.core.security import RoleChecker, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    summary="Register a New User",
    status_code=status.HTTP_201_CREATED,
    response_model=dict
)
def register_user(
    data: CreateUserSchema,
    service: UserService = Depends(get_user_service)
):
    """
    Register a new user. The user can specify their role upon creation.
    """
    result = service.create_user(data)
    if not result.get("success", False):
        raise HTTPException(
            status_code=result.get("status_code", 400),
            detail=result.get("message", "Registration failed")
        )
    return result

@router.post(
    "/login",
    summary="Login User",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
def login_user(
    data: UserLogin,
    service: UserService = Depends(get_user_service)
):
    """
    Login user with email and password. Returns JWT token.
    """
    result = service.login_user(data)
    if not result.get("success", False):
        raise HTTPException(
            status_code=result.get("status_code", 401),
            detail=result.get("message", "Login failed")
        )
    return result

@router.get(
    "/me",
    summary="Get Current User Profile",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current user's profile information.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role
    )

# User management routes (for admins)
user_router = APIRouter(
    prefix="/users",
    tags=["User Management"]
)

@user_router.get(
    "/{item_id}",
    summary="Get User by ID (Admin Only)",
    dependencies=[Depends(RoleChecker([UserRole.ADMIN]))],
    response_model=UserResponse
)
def get_user(
    item_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Retrieve a user's public details by their ID.
    """
    result = service.get_user_by_id(item_id)
    if not result.get("success", False):
        raise HTTPException(
            status_code=result.get("status_code", 404),
            detail=result.get("message", "User not found")
        )
    return result["data"]