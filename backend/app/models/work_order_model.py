# app/work_orders/work_order_schema.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from bson import ObjectId

# Enum for controlled vocabulary for the status field
class WorkOrderStatus(str, Enum):
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    CANCELED = "Canceled"

# Base model with common fields, now using 'str' for IDs
class WorkOrderBase(BaseModel):
    name: str = Field(..., description="The name or title of the work order, e.g., 'Assembly for MO-101'")
    manufacturingOrderId: str = Field(..., description="The ID of the parent Manufacturing Order")
    status: WorkOrderStatus = Field(default=WorkOrderStatus.PLANNED, description="The current status of the work order")
    expectedDuration: int = Field(..., description="Estimated time in minutes to complete the work")
    workCenterId: Optional[str] = Field(None, description="The ID of the Work Center where this task is performed")

# Schema for creating a new work order (request body)
class CreateWorkOrderSchema(WorkOrderBase):
    pass

# Schema for updating the status of a work order
class UpdateWorkOrderStatusSchema(BaseModel):
    status: WorkOrderStatus = Field(..., description="The new status for the work order")

# Schema for the response model (what the API returns)
class WorkOrderResponseSchema(WorkOrderBase):
    # The 'alias' field is crucial. It tells Pydantic to populate our 'id' field
    # with the value from the '_id' field in the MongoDB document.
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: datetime

    class Config:
        # This configuration helps Pydantic work with MongoDB's _id field
        populate_by_name = True
        # This ensures that any ObjectId types are automatically converted to strings
        json_encoders = {ObjectId: str}