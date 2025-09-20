from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import JSONResponse
import inspect

from app.models.manufacture import ManufacturingOrderCreate
from app.service.manufacture_service import ManufacturingOrderService
from core.logger import logs
from app.utils.response_model import response

router = APIRouter(
    prefix="/manufacturing-orders",
    tags=["Manufacturing Orders"]
)

mo_service = ManufacturingOrderService()

@router.post("/")
async def create_order(request: Request, order_data: ManufacturingOrderCreate):
    log_message_prefix = "Create MO request"
    logs.define_logger(20, f"{log_message_prefix} received", request=request, loggName=inspect.stack()[0], body=order_data.model_dump())
    
    try:
        created_data = await mo_service.create_manufacturing_order(order_data)
        final_response = response.success(
            data=created_data,
            message="Manufacturing Order created successfully",
            status_code=201
        )
        return JSONResponse(status_code=201, content=final_response)
    
    except HTTPException as he:
        logs.define_logger(40, f"{log_message_prefix} failed: {he.detail}", request=request, loggName=inspect.stack()[0])
        return JSONResponse(status_code=he.status_code, content=response.failure(message=he.detail, status_code=he.status_code))
    
    except Exception as e:
        logs.define_logger(50, f"{log_message_prefix} failed with unexpected error: {e}", request=request, loggName=inspect.stack()[0])
        return JSONResponse(status_code=500, content=response.failure(message="An unexpected server error occurred.", status_code=500))

@router.get("/")
async def get_all_orders(request: Request, status: str | None = Query(None)):
    try:
        orders = await mo_service.get_all_manufacturing_orders(status)
        return JSONResponse(status_code=200, content=response.success(data=orders))
    
    except Exception as e:
        logs.define_logger(50, f"Get all MOs failed with unexpected error: {e}", request=request, loggName=inspect.stack()[0])
        return JSONResponse(status_code=500, content=response.failure(message="An unexpected server error occurred.", status_code=500))

@router.get("/{mo_id}")
async def get_order_by_id(request: Request, mo_id: str):
    try:
        order = await mo_service.get_manufacturing_order_by_id(mo_id)
        return JSONResponse(status_code=200, content=response.success(data=order))
        
    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content=response.failure(message=he.detail, status_code=he.status_code))
    
    except Exception as e:
        logs.define_logger(50, f"Get MO by ID {mo_id} failed with unexpected error: {e}", request=request, loggName=inspect.stack()[0])
        return JSONResponse(status_code=500, content=response.failure(message="An unexpected server error occurred.", status_code=500))

@router.delete("/{mo_id}")
async def delete_order(request: Request, mo_id: str):
    try:
        await mo_service.delete_manufacturing_order(mo_id)
        return JSONResponse(status_code=200, content=response.success(data=None, message="Manufacturing Order deleted successfully."))
        
    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content=response.failure(message=he.detail, status_code=he.status_code))
    
    except Exception as e:
        logs.define_logger(50, f"Delete MO {mo_id} failed with unexpected error: {e}", request=request, loggName=inspect.stack()[0])
        return JSONResponse(status_code=500, content=response.failure(message="An unexpected server error occurred.", status_code=500))

