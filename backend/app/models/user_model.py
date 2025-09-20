from pydantic import Field, EmailStr
from enum import Enum
from .base_model import BaseDBModel, BaseCreateModel

class UserRole(str, Enum):
    ADMIN = "Admin"
    MANUFACTURING_MANAGER = "Manufacturing Manager"
    OPERATOR = "Operator"
    INVENTORY_MANAGER = "Inventory Manager"

class User(BaseDBModel):
    """User with complete database fields"""
    email: EmailStr = Field(..., description="The user's email address")
    role: UserRole = Field(..., description="The user's role")
    password_hash: str = Field(..., description="Hashed password")

class CreateUserSchema(BaseCreateModel):
    """Schema for creating users"""
    email: EmailStr = Field(..., description="The user's email address")
    role: UserRole = Field(..., description="The user's role")
    password: str = Field(..., min_length=8, description="The user's password (min 8 characters)")

# Alias for backward compatibility
UserResponseSchema = User