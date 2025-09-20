from ..repo.product_repo import ProductRepository
from ..models.product_model import Product
from pymongo.results import InsertOneResult

class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    def create_product(self, product: Product) -> InsertOneResult:
        product_data = product.dict(by_alias=True)
        return self.repo.create(product_data)