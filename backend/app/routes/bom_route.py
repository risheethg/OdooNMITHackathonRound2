from fastapi import APIRouter, Depends, status, HTTPException, Request
from pymongo.database import Database
from bson import ObjectId
from ..core.db_connection import get_db
from ..utils.response_model import Response
from ..core.logger import logs # New import
from ..models.bom_model import BOM
from ..repo.bom_repo import BOMRepository
from ..repo.product_repo import ProductRepository
from ..service.bom_service import BOMService
import inspect
import os
import logging

def get_bom_service(db: Database = Depends(get_db)) -> BOMService:
    service = BOMService(db)
    return service

router = APIRouter(
    prefix="/boms",
    tags=["BOMs"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_bom(
    bom: BOM,
    request: Request,
    service: BOMService = Depends(get_bom_service)
):
    """
    Defines a new Bill of Materials (BOM) for a finished product.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Creating a new BOM...", loggName=log_info, pid=os.getpid(), request=request, body=bom)
    
    result = service.create_bom(bom)
    created_bom = service.repo.get_by_id(str(result.inserted_id))

    logs.define_logger(level=logging.INFO, message="BOM created successfully.", loggName=log_info, pid=os.getpid(), request=request, response=created_bom)
    
    return Response.success(
        data=created_bom,
        message="BOM created successfully.",
        status_code=status.HTTP_201_CREATED
    )
