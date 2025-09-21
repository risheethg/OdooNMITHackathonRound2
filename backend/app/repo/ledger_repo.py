import inspect
from typing import List, Dict
from pymongo.database import Database
from ..core.logger import logs
from .base import BaseRepository

class StockLedgerRepository(BaseRepository):
    """
    Handles database operations for the stock_ledger collection.
    """
    def __init__(self, db: Database):
        
            super().__init__(collection=db["ledger"])
