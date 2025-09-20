from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime
from .base_model import BaseDBModel, BaseCreateModel

class BillOfMaterials(BaseModel):
    """Simplified BOM model for manufacturing orders"""
    product_id: str
    components: List[dict]
    operations: List[dict]

class WorkOrder(BaseDBModel):
    """Represents a single task or step within a larger Manufacturing Order"""
    operation_name: str = Field(..., description="Name of the operation")
    work_center_id: str = Field(..., description="Reference to a WorkCenter's ID")
    status: Literal["pending", "in_progress", "paused", "done"] = Field(default="pending")

class ManufacturingOrder(BaseDBModel):
    """Represents a full production job to create a specific quantity of a product"""
    product_id: str = Field(..., description="The finished good to produce")
    quantity_to_produce: int = Field(..., description="Quantity to produce")
    status: Literal["planned", "in_progress", "done", "cancelled"] = Field(default="planned")
    bom_snapshot: BillOfMaterials = Field(..., description="A copy of the BOM at the time of creation")
    work_orders: List[WorkOrder] = Field(default=[], description="List of work orders")

class ManufacturingOrderCreate(BaseCreateModel):
    """Defines the shape of the input data required to create a new MO"""
    product_id: str = Field(..., description="Product ID to manufacture")
    quantity: int = Field(..., gt=0, description="Quantity to produce")
