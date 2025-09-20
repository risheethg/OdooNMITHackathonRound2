from pydantic import Field
from typing import Optional
from .base_model import BaseDBModel, BaseCreateModel

class Product(BaseDBModel):
    """Product model with complete database fields"""
    name: str = Field(..., description="Product name")
    type: str = Field(..., description="Product type (Raw Material, Finished Good, etc.)")
    description: Optional[str] = Field(None, description="Product description")

class ProductCreate(BaseCreateModel):
    """Model for creating products"""
    name: str = Field(..., description="Product name")
    type: str = Field(..., description="Product type (Raw Material, Finished Good, etc.)")
    description: Optional[str] = Field(None, description="Product description")
