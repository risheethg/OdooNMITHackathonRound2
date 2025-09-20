from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class StockLedgerEntry(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    product_id: str
    quantity_change: int  # Positive for production, negative for consumption
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: str  # e.g., "Consumption for MO-123", "Initial Stock"
    manufacturing_order_id: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
