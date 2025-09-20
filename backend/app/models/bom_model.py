from typing import List, Optional
from pydantic import BaseModel, Field

class BOMComponent(BaseModel):
    """
    Represents a single component (raw material or sub-assembly)
    and its required quantity for a Bill of Materials.
    """
    productId: str
    quantity: int = Field(..., gt=0)

class BOMOperation(BaseModel):
    """
    Represents a single manufacturing step in a Bill of Materials.
    """
    name: str
    duration: int = Field(..., gt=0) # Duration in minutes

class BOM(BaseModel):
    """
    Represents the complete Bill of Materials document in MongoDB,
    including its components and manufacturing operations.
    """
    id: Optional[str] = Field(None, alias="_id")
    finishedProductId: str = Field(...)
    components: List[BOMComponent]
    operations: List[BOMOperation]
    recipe: str

    class Config:
        json_encoders = {str: str}
        arbitrary_types_allowed = True
        validate_by_name = True

class BOMCreate(BaseModel):
    """
    Model for creating a new BOM from a simplified input.
    """
    finishedProductId: str = Field(...)
    productName: str
    quantity: int = Field(..., gt=0)
