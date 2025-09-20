from fastapi import APIRouter, Query, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pymongo.database import Database
import inspect
import os
import logging

from app.models.manufacture import ManufacturingOrderCreate
from app.service.manufacture_service import ManufacturingOrderService
from app.core.db_connection import get_db
from app.core.logger import logs
from app.utils.response_model import response
from app.core.security import RoleChecker
from app.models.user_model import UserRole

router = APIRouter(
    prefix="/manufacturing-orders",
    tags=["Manufacturing Orders"],
    dependencies=[Depends(RoleChecker([UserRole.MANUFACTURING_MANAGER, UserRole.ADMIN]))]
)

def get_mo_service(db: Database = Depends(get_db)) -> ManufacturingOrderService:
    return ManufacturingOrderService(db)

@router.post("/")
async def create_order(request: Request, order_data: ManufacturingOrderCreate, service: ManufacturingOrderService = Depends(get_mo_service)):
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Creating a new manufacturing order...", loggName=log_info, pid=os.getpid(), request=request, body=order_data)
    
    try:
        created_data = await service.create_manufacturing_order(order_data)
        
        logs.define_logger(level=logging.INFO, message="Manufacturing order created successfully.", loggName=log_info, pid=os.getpid(), request=request, response=created_data)
        
        final_response = response.success(
            data=created_data,
            message="Manufacturing Order created successfully",
            status_code=201
        )
        return JSONResponse(status_code=201, content=final_response)
    
    except HTTPException as he:
        logs.define_logger(level=logging.ERROR, message=f"Failed to create manufacturing order: {he.detail}", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=he.status_code, content=response.failure(message=he.detail, status_code=he.status_code))
    
    except Exception as e:
        logs.define_logger(level=logging.ERROR, message=f"Unexpected error creating manufacturing order: {e}", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=500, content=response.failure(message="An unexpected server error occurred.", status_code=500))

@router.get("/")
async def get_all_orders(request: Request, status: str | None = Query(None), service: ManufacturingOrderService = Depends(get_mo_service)):
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Fetching all manufacturing orders...", loggName=log_info, pid=os.getpid(), request=request)
    
    try:
        orders = await service.get_all_manufacturing_orders(status)
        
        logs.define_logger(level=logging.INFO, message="Manufacturing orders fetched successfully.", loggName=log_info, pid=os.getpid(), request=request)
        
        return response.success(
            data=orders,
            message="Manufacturing Orders fetched successfully",
            status_code=200
        )

    except Exception as e:
        logs.define_logger(level=logging.ERROR, message=f"Unexpected error fetching manufacturing orders: {e}", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=500, content=response.failure(message="An unexpected server error occurred.", status_code=500))

@router.get("/{mo_id}")
async def get_order_by_id(request: Request, mo_id: str, service: ManufacturingOrderService = Depends(get_mo_service)):
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message=f"Fetching manufacturing order with ID: {mo_id}", loggName=log_info, pid=os.getpid(), request=request)
    
    try:
        order = await service.get_manufacturing_order_by_id(mo_id)
        
        logs.define_logger(level=logging.INFO, message="Manufacturing order fetched successfully.", loggName=log_info, pid=os.getpid(), request=request, response=order)
        
        return response.success(
            data=order,
            message="Manufacturing Orders fetched successfully",
            status_code=200
        )
        
    except HTTPException as he:
        logs.define_logger(level=logging.ERROR, message=f"Failed to fetch manufacturing order: {he.detail}", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=he.status_code, content=response.failure(message=he.detail, status_code=he.status_code))
    
    except Exception as e:
        logs.define_logger(level=logging.ERROR, message=f"Unexpected error fetching manufacturing order: {e}", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=500, content=response.failure(message="An unexpected server error occurred.", status_code=500))

@router.delete("/{mo_id}")
async def delete_order(request: Request, mo_id: str, service: ManufacturingOrderService = Depends(get_mo_service)):
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message=f"Deleting manufacturing order with ID: {mo_id}", loggName=log_info, pid=os.getpid(), request=request)
    
    try:
        await service.delete_manufacturing_order(mo_id)
        
        logs.define_logger(level=logging.INFO, message="Manufacturing order deleted successfully.", loggName=log_info, pid=os.getpid(), request=request)
        
        return JSONResponse(status_code=200, content=response.success(data=None, message="Manufacturing Order deleted successfully."))
        
    except HTTPException as he:
        logs.define_logger(level=logging.ERROR, message=f"Failed to delete manufacturing order: {he.detail}", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=he.status_code, content=response.failure(message=he.detail, status_code=he.status_code))
    
    except Exception as e:
        logs.define_logger(level=logging.ERROR, message=f"Unexpected error deleting manufacturing order: {e}", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=500, content=response.failure(message="An unexpected server error occurred.", status_code=500))

@router.patch("/{mo_id}/complete")
async def complete_manufacturing_order(request: Request, mo_id: str, service: ManufacturingOrderService = Depends(get_mo_service)):
    """
    Complete a manufacturing order and automatically update inventory.
    This is the critical route that triggers automatic inventory updates.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message=f"Completing manufacturing order with ID: {mo_id}", loggName=log_info, pid=os.getpid(), request=request)
    
    try:
        result = await service.complete_manufacturing_order(mo_id)
        
        logs.define_logger(level=logging.INFO, message="Manufacturing order completed successfully.", loggName=log_info, pid=os.getpid(), request=request, response=result)
        
        return response.success(
            data=result,
            message="Manufacturing Order completed successfully",
            status_code=200
        )

    
    except HTTPException as he:
        logs.define_logger(level=logging.ERROR, message=f"Failed to complete manufacturing order: {he.detail}", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=he.status_code, content=response.failure(message=he.detail, status_code=he.status_code))
    
    except Exception as e:
        logs.define_logger(level=logging.ERROR, message=f"Unexpected error completing manufacturing order: {e}", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=500, content=response.failure(message="An unexpected server error occurred.", status_code=500))