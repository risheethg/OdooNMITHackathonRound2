from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BaseDBModel(BaseModel):
    """Base model for all database entities with common fields"""
    id: Optional[str] = Field(default=None, alias="_id", description="Unique identifier")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True
    }

class BaseCreateModel(BaseModel):
    """Base model for creation requests (without auto-generated fields)"""
    
    model_config = {
        "str_strip_whitespace": True
    }
