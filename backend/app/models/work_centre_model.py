# app/work_centres/work_centre_schema.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId

class WorkCentreBase(BaseModel):
    name: str = Field(..., description="The unique name of the work centre, e.g., 'Assembly Line 1'")
    description: Optional[str] = Field(None, description="A brief description of the work centre's purpose")
    cost_per_hour: Optional[float] = Field(None, gt=0, description="The operational cost of running this work centre per hour")

class CreateWorkCentreSchema(WorkCentreBase):
    pass

class WorkCentreResponseSchema(WorkCentreBase):
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}