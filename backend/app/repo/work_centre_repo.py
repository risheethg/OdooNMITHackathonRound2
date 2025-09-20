# app/work_centres/work_centre_repo.py

from pymongo.database import Database
from app.repo.base import BaseRepository
from app.core.db_connection import get_db

class WorkCentreRepository(BaseRepository):
    """
    Repository for Work Centre specific database operations.
    """
    def __init__(self, db: Database):
        """
        Initializes the repository with the 'work_centres' collection.
        """
        super().__init__(db["work_centres"])

def get_work_centre_repo() -> WorkCentreRepository:
    """
    Returns an instance of the WorkCentreRepository for dependency injection.
    """
    db = get_db()
    return WorkCentreRepository(db)