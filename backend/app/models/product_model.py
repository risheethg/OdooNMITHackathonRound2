from typing import Optional
from pydantic import BaseModel, Field

class Product(BaseModel):
    """
    Represents a product document in MongoDB.
    
    The 'id' is now a string to avoid using ObjectId in the model directly.
    The 'type' field is a simple string, with no predefined values.
    """
    name: str = Field(...)
    type: str = Field(...)

    class Config:
        # Allows Pydantic to handle non-primitive types like ObjectId.
        # This is needed to handle the `_id` field from MongoDB.
        arbitrary_types_allowed = True
        # Pydantic V2 syntax for aliased fields
        validate_by_name = True
