# app/repo/wo_repo.py

from typing import List, Dict, Any, Optional
from pymongo.database import Database
from bson import ObjectId

# NOTE: This assumes you have a BaseRepository. If not, implement these methods directly.
from app.repo.base import BaseRepository # Assuming a base repository

class WorkOrderRepository(BaseRepository):
    """
    Repository for interacting with the 'work_orders' collection in MongoDB.
    """
    def __init__(self, db: Database):
        super().__init__(db, "work_orders")

    def find_by_mo_id(self, mo_id: str) -> List[Dict[str, Any]]:
        """Finds all work orders associated with a given Manufacturing Order ID."""
        return list(self.collection.find({"mo_id": mo_id}))