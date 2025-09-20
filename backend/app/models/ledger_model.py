from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .base_model import BaseDBModel, BaseCreateModel

class StockLedgerEntry(BaseDBModel):
    """Stock ledger entry for tracking inventory movements"""
    product_id: str = Field(..., description="ID of the product")
    quantity_change: int = Field(..., description="Positive for production, negative for consumption")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the transaction occurred")
    reason: str = Field(..., description="Reason for stock change")
    manufacturing_order_id: Optional[str] = Field(None, description="Related manufacturing order ID")

class StockLedgerEntryCreate(BaseCreateModel):
    """Model for creating stock ledger entries"""
    product_id: str = Field(..., description="ID of the product")
    quantity_change: int = Field(..., description="Positive for production, negative for consumption")
    reason: str = Field(..., description="Reason for stock change")
    manufacturing_order_id: Optional[str] = Field(None, description="Related manufacturing order ID")
