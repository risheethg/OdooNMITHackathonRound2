from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from .base import BaseRepository

class ProductRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(collection=db["products"])

    def get_by_name(self, name: str) -> dict | None:
        """
        Retrieves a product document by its name.
        Returns the document if found, otherwise None.
        """
        return self.collection.find_one({"name": name.lower()})
