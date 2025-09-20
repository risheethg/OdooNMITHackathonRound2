from .base import BaseRepository
from pymongo.database import Database

class ManufacturingOrderRepository(BaseRepository):
    """
    Repository specifically for handling database operations for the
    'manufacturing_orders' collection.
    """
    def __init__(self, db: Database):
        
            super().__init__(collection=db["manufacturing_orders"])
        

    def find_by_product(self, product_id: str):
        """Find all manufacturing orders for a specific product"""
        return self.get_all({"product_id": product_id})