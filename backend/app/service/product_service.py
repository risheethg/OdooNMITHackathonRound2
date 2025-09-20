from fastapi import HTTPException, status
from ..repo.product_repo import ProductRepository
from ..models.product_model import Product, ProductCreate
from pymongo.results import InsertOneResult

class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def create_product(self, product: ProductCreate) -> InsertOneResult:
        """Creates a new product in the database."""
        return self.repo.create(product.model_dump())

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