from .base import BaseRepository
from core.db_connection import get_db

class ManufacturingOrderRepository(BaseRepository):
    """
    Repository specifically for handling database operations for the
    'manufacturing_orders' collection.
    """
    def __init__(self):
        # Obtain the database instance
        db = get_db()
        # Initialize the BaseRepository with the 'manufacturing_orders' collection
        super().__init__(db.get_collection("manufacturing_orders"))

    # You can add any Manufacturing Order specific database methods here.
    # For example, a method to find all orders for a specific product:
    #
    # def find_by_product(self, product_id: str):
    #     return self.get_all({"product_id": product_id})