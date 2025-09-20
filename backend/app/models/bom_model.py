from pydantic import BaseModel, Field
from typing import List, Optional
from .base_model import BaseDBModel, BaseCreateModel

class BOMComponent(BaseModel):
    productId: str = Field(..., description="Product ID of the component")
    quantity: int = Field(..., gt=0, description="Quantity of component needed")

class BOMOperation(BaseModel):
    name: str = Field(..., description="Name of the operation")
    duration: int = Field(..., gt=0, description="Duration in minutes")

class BOM(BaseDBModel):
    """Bill of Materials with complete database fields"""
    finishedProductId: str = Field(..., description="Product ID of the finished product")
    components: List[BOMComponent] = Field(..., description="List of components required")
    operations: List[BOMOperation] = Field(..., description="List of operations required")
    recipe: Optional[str] = Field(None, description="Recipe description")

class BOMCreate(BaseCreateModel):
    """Model for creating BOMs"""
    finishedProductId: str = Field(..., description="Product ID of the finished product")
    components: List[BOMComponent] = Field(..., description="List of components required")
    operations: List[BOMOperation] = Field(..., description="List of operations required") 
    recipe: Optional[str] = Field(None, description="Recipe description")

    model_config = {
        "json_schema_extra": {
            "example": {
                "finishedProductId": "wooden_table_001",
                "components": [
                    {"productId": "wooden_leg_001", "quantity": 4},
                    {"productId": "wooden_top_001", "quantity": 1},
                    {"productId": "screws_001", "quantity": 12}
                ],
                "operations": [
                    {"name": "Assembly", "duration": 60},
                    {"name": "Painting", "duration": 30}
                ],
                "recipe": "Standard wooden table assembly process"
            }
        }
    }

    model_config = {
        "json_schema_extra": {
            "example": {
                "finishedProductId": "wooden_table_001",
                "components": [
                    {"productId": "wooden_leg_001", "quantity": 4},
                    {"productId": "wooden_top_001", "quantity": 1},
                    {"productId": "screws_001", "quantity": 12}
                ],
                "operations": [
                    {"name": "Assembly", "duration": 60},
                    {"name": "Painting", "duration": 30}
                ],
                "recipe": "Standard wooden table assembly process"
            }
        }
    }