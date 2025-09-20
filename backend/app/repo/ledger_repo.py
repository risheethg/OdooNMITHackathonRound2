import inspect
from typing import List, Dict
from core.logger import logs
from repo.base import BaseRepository

class StockLedgerRepository(BaseRepository):
    """
    Handles database operations for the stock_ledger collection.
    """
    def __init__(self, collection_name: str = "stock_ledger"):
        super().__init__(collection_name)

    async def get_stock_availability(self) -> List[Dict]:
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
            results = await cursor.to_list(length=None)
            return results
        except Exception as e:
            logs.define_logger(50, f"Error in get_stock_availability: {e}", loggName=inspect.stack()[0])
            raise
