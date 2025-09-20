from fastapi import HTTPException, status
from pymongo.results import InsertOneResult
from ..repo.product_repo import ProductRepository
from ..models.product_model import ProductCreate

class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def create_product(self, product_in: ProductCreate) -> InsertOneResult:
        """
        Creates a new product in the database after checking for duplicates.
        """
        # Convert the name to lowercase for a case-insensitive lookup
        product_name_lower = product_in.name.lower()
        
        # Check if a product with the same name already exists
        existing_product = self.repo.get_by_name(product_name_lower)
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with name '{product_in.name}' already exists."
            )
        
        # If no duplicate, proceed with creation. The repository will handle the lowercase conversion.
        return self.repo.create(product_in.model_dump())

    def get_all_products(self):
        """Get all products from the database."""
        return self.repo.get_all()

    def get_product_by_id(self, product_id: str):
        """Get a specific product by ID."""
        product = self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID '{product_id}' not found."
            )
        return product
