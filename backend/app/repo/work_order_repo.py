# app/work_orders/work_order_repo.py

from pymongo.database import Database
from app.repo.base import BaseRepository
from app.core.db_connection import get_db

class WorkOrderRepository(BaseRepository):
    """
    Repository for Work Order specific database operations.
    It inherits generic CRUD methods from BaseRepository.
    """
    def __init__(self, db: Database):
        """
        Initializes the repository with the 'work_orders' collection.
        
        Args:
            db (Database): The database instance.
        """
        super().__init__(db["work_orders"])

# Dependency function to get a repository instance
def get_work_order_repo() -> WorkOrderRepository:
    """
    Returns an instance of the WorkOrderRepository.
    This function can be used as a dependency in FastAPI routes.
    """
    db = get_db()
    return WorkOrderRepository(db)