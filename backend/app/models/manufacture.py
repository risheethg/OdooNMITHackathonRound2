from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

# Assuming you have a BOM model defined elsewhere, but for context:
# from .bom import BillOfMaterials 

class BillOfMaterials(BaseModel):
    # This is a placeholder to make the MO model work.
    # In your actual code, you would import your real BOM model.
    product_id: str
    components: List[dict]
    operations: List[dict]

class WorkOrder(BaseModel):
    """
    Represents a single task or step within a larger Manufacturing Order.
    """
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    operation_name: str
    work_center_id: str  # Reference to a WorkCenter's ID
    status: Literal["pending", "in_progress", "paused", "done"] = "pending"

class ManufacturingOrder(BaseModel):
    """
    Represents a full production job to create a specific quantity of a product.
    """
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    product_id: str  # The finished good to produce
    quantity_to_produce: int
    status: Literal["planned", "in_progress", "done", "canceled"] = "planned"
    bom_snapshot: BillOfMaterials  # A copy of the BOM at the time of creation
    work_orders: List[WorkOrder] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ManufacturingOrderCreate(BaseModel):
    """
    Defines the shape of the input data required to create a new MO.
    """
    product_id: str
    quantity: int

# We need this for BSON ObjectId conversion
from bson import ObjectId
class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
