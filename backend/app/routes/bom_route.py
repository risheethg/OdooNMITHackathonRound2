from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from pymongo.database import Database
from bson import ObjectId
from ..core.db_connection import get_db
from ..utils.response_model import Response, response
from ..core.logger import logs # New import
from ..models.bom_model import BOM, BOMComponent, BOMCreate
from ..repo.bom_repo import BOMRepository
from ..repo.product_repo import ProductRepository
from ..service.bom_service import BOMService
from ..core.security import RoleChecker
from ..models.user_model import UserRole

import inspect
import os
import logging

def get_bom_service(db: Database = Depends(get_db)) -> BOMService:
    bom_repo = BOMRepository(db)
    product_repo = ProductRepository(db)
    return BOMService(bom_repo, product_repo)

router = APIRouter(
    prefix="/boms",
    tags=["BOMs"],
    dependencies=[Depends(RoleChecker([UserRole.MANUFACTURING_MANAGER, UserRole.ADMIN]))]
)

from app.models.bom_model import BOM, BOMCreate

@router.post("/", summary="Create New BOM")
async def create_bom(request: Request, bom_data: BOMCreate, service: BOMService = Depends(get_bom_service)):
    """
    Create a new Bill of Materials (BOM).
    
    The system will automatically generate:
    - _id: Unique identifier
    - created_at: Creation timestamp
    - updated_at: Last modified timestamp
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Creating a new BOM...", loggName=log_info, pid=os.getpid(), request=request, body=bom_data)
    
    try:
        result = service.create_bom(bom_data)
        created_bom = service.bom_repo.get_by_id(str(result.inserted_id))
        
        logs.define_logger(level=logging.INFO, message="BOM created successfully.", loggName=log_info, pid=os.getpid(), request=request, response=created_bom)
        
        return Response.success(
            data=created_bom,
            message="BOM created successfully.",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        logs.define_logger(level=logging.ERROR, message=f"Failed to create BOM: {e}", loggName=log_info, pid=os.getpid(), request=request)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_boms(
    request: Request,
    service: BOMService = Depends(get_bom_service)
):
    """
    Get all Bills of Materials.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Fetching all BOMs...", loggName=log_info, pid=os.getpid(), request=request)
    
    boms = service.get_all_boms()
    
    logs.define_logger(level=logging.INFO, message="BOMs fetched successfully.", loggName=log_info, pid=os.getpid(), request=request)
    
    return Response.success(
        data=boms,
        message="BOMs fetched successfully.",
        status_code=status.HTTP_200_OK
    )

@router.get("/{bom_id}", status_code=status.HTTP_200_OK)
def get_bom_by_id(
    bom_id: str,
    request: Request,
    service: BOMService = Depends(get_bom_service)
):
    """
    Get a specific BOM by ID.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message=f"Fetching BOM with ID: {bom_id}", loggName=log_info, pid=os.getpid(), request=request)
    
    bom = service.get_bom_by_id(bom_id)
    
    logs.define_logger(level=logging.INFO, message="BOM fetched successfully.", loggName=log_info, pid=os.getpid(), request=request, response=bom)
    
    return Response.success(
        data=bom,
        message="BOM fetched successfully.",
        status_code=status.HTTP_200_OK
    )

@router.get("/product/{product_id}", status_code=status.HTTP_200_OK)
def get_bom_by_product_id(
    product_id: str,
    request: Request,
    service: BOMService = Depends(get_bom_service)
):
    """
    Get BOM for a specific product.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message=f"Fetching BOM for product ID: {product_id}", loggName=log_info, pid=os.getpid(), request=request)
    
    bom = service.get_bom_by_product_id(product_id)
    
    logs.define_logger(level=logging.INFO, message="BOM fetched successfully.", loggName=log_info, pid=os.getpid(), request=request, response=bom)
    
    return Response.success(
        data=bom,
        message="BOM fetched successfully.",
        status_code=status.HTTP_200_OK
    )
