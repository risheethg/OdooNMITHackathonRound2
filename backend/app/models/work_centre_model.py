from pydantic import Field
from typing import Optional
from .base_model import BaseDBModel, BaseCreateModel

class WorkCentre(BaseDBModel):
    """Work centre with complete database fields"""
    name: str = Field(..., description="The unique name of the work centre")
    description: Optional[str] = Field(None, description="Brief description of the work centre's purpose")
    cost_per_hour: Optional[float] = Field(None, gt=0, description="Operational cost per hour")

class CreateWorkCentreSchema(BaseCreateModel):
    """Schema for creating work centres"""
    name: str = Field(..., description="The unique name of the work centre")
    description: Optional[str] = Field(None, description="Brief description of the work centre's purpose")
    cost_per_hour: Optional[float] = Field(None, gt=0, description="Operational cost per hour")

# Alias for backward compatibility
WorkCentreResponseSchema = WorkCentre