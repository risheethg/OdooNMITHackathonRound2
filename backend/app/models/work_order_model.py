from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from .base_model import BaseDBModel, BaseCreateModel

# Enum for controlled vocabulary for the status field
class WorkOrderStatus(str, Enum):
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    CANCELED = "Canceled"

class WorkOrder(BaseDBModel):
    """Work order with complete database fields"""
    name: str = Field(..., description="The name or title of the work order")
    manufacturingOrderId: str = Field(..., description="The ID of the parent Manufacturing Order")
    status: WorkOrderStatus = Field(default=WorkOrderStatus.PLANNED, description="Current status")
    expectedDuration: int = Field(..., description="Estimated time in minutes")
    workCenterId: Optional[str] = Field(None, description="Work Center ID where task is performed")

class CreateWorkOrderSchema(BaseCreateModel):
    """Schema for creating a new work order"""
    name: str = Field(..., description="The name or title of the work order")
    manufacturingOrderId: str = Field(..., description="The ID of the parent Manufacturing Order")
    expectedDuration: int = Field(..., description="Estimated time in minutes")
    workCenterId: Optional[str] = Field(None, description="Work Center ID where task is performed")

class UpdateWorkOrderStatusSchema(BaseModel):
    """Schema for updating work order status"""
    status: WorkOrderStatus = Field(..., description="The new status for the work order")

# Alias for backward compatibility
WorkOrderResponseSchema = WorkOrder