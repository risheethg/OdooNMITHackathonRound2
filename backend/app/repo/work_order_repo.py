# app/repo/work_order_repo.py

from typing import List, Dict, Any
from pymongo.database import Database
from pymongo import ASCENDING
from app.repo.base import BaseRepository 

class WorkOrderRepository(BaseRepository):
    """
    Repository for the 'work_orders' collection, with specific query methods.
    """
    def __init__(self, db: Database):
        # First, get the specific collection object from the database instance.
        work_orders_collection = db["work_orders"]
        
        # Now, pass that collection object to the parent's constructor.
        super().__init__(collection=work_orders_collection)

    def find_by_mo_id(self, mo_id: str) -> List[Dict[str, Any]]:
        """
        Finds all work orders associated with a given Manufacturing Order ID.
        sorted by their sequence.
        """
        cursor = self.collection.find({"mo_id": mo_id}).sort("sequence", ASCENDING)
        docs = list(cursor)
        return self._convert_ids_to_strings(docs)