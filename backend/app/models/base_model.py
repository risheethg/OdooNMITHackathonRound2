from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
import json

class BaseDBModel(BaseModel):
    """Base model for all database entities with common fields"""
    id: Optional[str] = Field(default=None, alias="_id", description="Unique identifier")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    @field_validator('id', mode='before')
    @classmethod
    def validate_object_id(cls, v: Any) -> str:
        """Convert ObjectId to string"""
        if isinstance(v, ObjectId):
            return str(v)
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class BaseCreateModel(BaseModel):
    """Base model for creation requests (without auto-generated fields)"""
    
    model_config = {
        "str_strip_whitespace": True
    }
