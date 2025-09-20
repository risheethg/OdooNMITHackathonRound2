from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from ..core.db_connection import get_db
from ..models.product_model import Product
from ..repo.product_repo import ProductRepository
from ..service.product_service import ProductService

def get_product_service(db: Database = Depends(get_db)) -> ProductService:
    repo = ProductRepository(db)
    return ProductService(repo)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Product)
def create_product(
    product: Product,
    service: ProductService = Depends(get_product_service)
):
    """
    Creates a new product in the system.
    """
    result = service.create_product(product)
    created_product = service.repo.get_by_id(str(result.inserted_id))
    return created_product