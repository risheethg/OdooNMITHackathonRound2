# app/users/user_schema.py

from pydantic import BaseModel, Field, EmailStr
from enum import Enum
from bson import ObjectId

class UserRole(str, Enum):
    ADMIN = "Admin"
    MANUFACTURING_MANAGER = "Manufacturing Manager"
    OPERATOR = "Operator"
    INVENTORY_MANAGER = "Inventory Manager"

class UserBase(BaseModel):
    # Instead of user_id, we'll use email as it's a natural unique identifier
    email: EmailStr = Field(..., description="The user's email address.")
    role: UserRole = Field(..., description="The user's role, which determines their permissions.")

class CreateUserSchema(UserBase):
    password: str = Field(..., min_length=8, description="The user's password (min 8 characters).")

class UserResponseSchema(UserBase):
    id: str = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}