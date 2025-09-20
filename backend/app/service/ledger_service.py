import inspect
from fastapi import HTTPException
from typing import List, Dict

from app.core.logger import logs
from app.repo.ledger_repo import StockLedgerRepository

class StockLedgerService:
    """
    Contains the business logic for the stock ledger.
    """
    def __init__(self):
        self.repository = StockLedgerRepository()

    async def get_ledger_history(self) -> List[Dict]:
        """
        Retrieves the entire history of stock movements.
        """
        logs.define_logger(20, "Fetching stock ledger history.", loggName=inspect.stack()[0])
        history = await self.repository.get_all()
        if not history:
            return []
        return history

    async def get_current_stock_levels(self) -> List[Dict]:
        """
        Calculates and retrieves the current stock levels for all products.
        """
        logs.define_logger(20, "Calculating current stock levels.", loggName=inspect.stack()[0])
        availability = await self.repository.get_stock_availability()
        if not availability:
            # If there are no ledger entries, it means stock is zero for all items.
            return []
        return availability