# app/models/wo_model.py

from pydantic import BaseModel, Field
from typing import Literal
from app.models.base_model import BaseDBModel # Assuming this base model exists

class WorkOrderBase(BaseModel):
    """Base model for a Work Order, containing shared fields."""
    mo_id: str = Field(..., description="ID of the parent Manufacturing Order")
    operation_name: str = Field(..., description="Name of the operation (e.g., Assembly, Painting)")
    work_center_id: str = Field(..., description="Reference to the WorkCenter's ID")
    status: Literal["pending", "in_progress", "processing", "paused", "done"] = Field(default="pending")
    sequence: int = Field(default=0, description="The order of this task in the sequence")

class WorkOrderInDB(BaseDBModel, WorkOrderBase):
    """Work Order model as it is stored in the database."""
    pass

class WorkOrderUpdate(BaseModel):
    """Model for updating the status of a Work Order via PATCH request."""
    status: Literal["pending", "in_progress", "processing", "paused", "done"] = Field(..., description="The new status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "in_progress"
            }
        }
    }
    
class StartProcessPayload(BaseModel):
    """Defines the request body for the endpoint that starts the MO process."""
    mo_id: str = Field(..., description="The ID of the Manufacturing Order to start.")