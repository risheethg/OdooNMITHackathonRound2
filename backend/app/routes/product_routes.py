from fastapi import APIRouter, Depends, status, Request
from pymongo.database import Database
from ..core.db_connection import get_db
from ..utils.response_model import Response
from ..core.logger import logs 
from ..models.product_model import Product, ProductCreate
from ..repo.product_repo import ProductRepository
from ..service.product_service import ProductService
from ..core.security import RoleChecker
from ..models.user_model import UserRole
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

@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    dependencies=[Depends(RoleChecker([UserRole.INVENTORY_MANAGER, UserRole.ADMIN]))]
)
def create_product(
    product: ProductCreate,  # Use ProductCreate instead of Product
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

    logs.define_logger(level=logging.INFO, message="Product created successfully.", loggName=log_info, pid=os.getpid(), request=request, response=created_product)
    
    return Response.success(
        data=created_product,
        message="Product created successfully.",
        status_code=status.HTTP_201_CREATED
    )

@router.get(
    "/", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker([UserRole.INVENTORY_MANAGER, UserRole.MANUFACTURING_MANAGER, UserRole.ADMIN]))]
)
def get_all_products(
    request: Request,
    service: ProductService = Depends(get_product_service)
):
    """
    Get all products from the system.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Fetching all products...", loggName=log_info, pid=os.getpid(), request=request)
    
    products = service.get_all_products()
    
    logs.define_logger(level=logging.INFO, message="Products fetched successfully.", loggName=log_info, pid=os.getpid(), request=request)
    
    return Response.success(
        data=products,
        message="Products fetched successfully.",
        status_code=status.HTTP_200_OK
    )

@router.get(
    "/{product_id}", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker([UserRole.INVENTORY_MANAGER, UserRole.MANUFACTURING_MANAGER, UserRole.ADMIN]))]
)
def get_product_by_id(
    product_id: str,
    request: Request,
    service: ProductService = Depends(get_product_service)
):
    """
    Get a specific product by ID.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message=f"Fetching product with ID: {product_id}", loggName=log_info, pid=os.getpid(), request=request)
    
    product = service.get_product_by_id(product_id)
    
    logs.define_logger(level=logging.INFO, message="Product fetched successfully.", loggName=log_info, pid=os.getpid(), request=request, response=product)
    
    return Response.success(
        data=product,
        message="Product fetched successfully.",
        status_code=status.HTTP_200_OK
    )
