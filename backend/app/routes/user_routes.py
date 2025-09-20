# app/users/user_router.py

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.service.user_service import UserService, get_user_service
from app.models.user_model import CreateUserSchema
from app.core.security import RoleChecker
from app.models.user_model import UserRole

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post(
    "/",
    summary="Register a New User",
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: CreateUserSchema,
    service: UserService = Depends(get_user_service)
):
    """
    Register a new user. The user can specify their role upon creation.
    """
    result = service.create_user(data)
    return JSONResponse(status_code=result["status_code"], content=result)

@router.get(
    "/{item_id}",
    summary="Get User by ID (Admin Only)",
    dependencies=[Depends(RoleChecker([UserRole.ADMIN]))]
)
def get_user(
    item_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Retrieve a user's public details by their ID.
    """
    result = service.get_user_by_id(item_id)
    return JSONResponse(status_code=result["status_code"], content=result)