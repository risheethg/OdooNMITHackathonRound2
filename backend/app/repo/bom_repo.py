from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.results import InsertOneResult
from .base import BaseRepository

class BOMRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(collection=db["boms"])
