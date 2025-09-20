# app/users/user_repo.py

from pymongo.database import Database
from typing import Optional, Dict, Any
from app.repo.base import BaseRepository
from app.core.db_connection import get_db

class UserRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db["users"])

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single user document by their email address.
        """
        return self.collection.find_one({"email": email})

def get_user_repo() -> UserRepository:
    db = get_db()
    return UserRepository(db)