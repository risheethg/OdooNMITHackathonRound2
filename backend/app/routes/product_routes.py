from fastapi import APIRouter, Depends, status, Request
from pymongo.database import Database
from ..core.db_connection import get_db
from ..utils.response_model import Response
from ..core.logger import logs 
from ..models.product_model import Product
from ..models.product_model import Product
from ..repo.product_repo import ProductRepository
from ..service.product_service import ProductService
import inspect
import os
import logging

def get_product_service(db: Database = Depends(get_db)) -> ProductService:
    repo = ProductRepository(db)
    return ProductService(repo)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    product: Product, # Reverted to use the full Product model
    request: Request,
    service: ProductService = Depends(get_product_service)
):
    """
    Creates a new product in the system.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Creating a new product...", loggName=log_info, pid=os.getpid(), request=request, body=product)
    
    result = service.create_product(product)
    created_product = service.repo.get_by_id(str(result.inserted_id))

    # ✅ Convert ObjectId to str before returning
    if created_product and "_id" in created_product:
        created_product["_id"] = str(created_product["_id"])

    logs.define_logger(level=logging.INFO, message="Product created successfully.", loggName=log_info, pid=os.getpid(), request=request, response=created_product)
    
    return Response.success(
        data=created_product,
        message="Product created successfully.",
        status_code=status.HTTP_201_CREATED
    )
