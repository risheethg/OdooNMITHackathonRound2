# app/users/user_router.py

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.service.user_service import UserService, get_user_service
from app.models.user_model import CreateUserSchema

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/")
def create_user(
    data: CreateUserSchema,
    service: UserService = Depends(get_user_service)
):
    """
    Register a new user.
    """
    result = service.create_user(data)
    return JSONResponse(status_code=result["status_code"], content=result)

@router.get("/{item_id}")
def get_user(
    item_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Retrieve a user's public details by their ID.
    """
    result = service.get_user_by_id(item_id)
    return JSONResponse(status_code=result["status_code"], content=result)