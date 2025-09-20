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


    def get_stock_availability(self) -> List[Dict]:
        """
        Calculates the current stock level for all products using an aggregation pipeline.

        Returns:
            List[Dict]: A list of dictionaries, each containing 'product_id' and 'current_stock'.
        """
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$product_id",
                        "current_stock": {"$sum": "$quantity_change"}
                    }
                },
                {
                    "$project": {
                        "product_id": "$_id",
                        "_id": 0,
                        "current_stock": 1
                    }
                }
            ]
            cursor = self.collection.aggregate(pipeline)
            results = cursor.to_list(length=None)
            return results
        except Exception as e:
            logs.define_logger(50, f"Error in get_stock_availability: {e}", loggName=inspect.stack()[0])
            raise
