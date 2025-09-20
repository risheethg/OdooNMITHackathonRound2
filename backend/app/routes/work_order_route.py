# app/work_orders/work_order_router.py

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from app.service.work_order_service import WorkOrderService, get_work_order_service
from app.models.work_order_model import CreateWorkOrderSchema, UpdateWorkOrderStatusSchema

# Create a new router for work orders with a specific prefix and tags for documentation
router = APIRouter(
    prefix="/work-orders",
    tags=["Work Orders"]
)

@router.post("/")
def create_work_order(
    data: CreateWorkOrderSchema,
    service: WorkOrderService = Depends(get_work_order_service)
):
    """
    Create a new Work Order.
    
    This endpoint receives work order data, passes it to the service layer for creation,
    and returns the result with a 201 Created status code on success.
    """
    result = service.create_work_order(data)
    return JSONResponse(status_code=result["status_code"], content=result)


@router.get("/{item_id}")
def get_work_order(
    item_id: str,
    service: WorkOrderService = Depends(get_work_order_service)
):
    """
    Retrieve a single Work Order by its unique ID.
    
    Returns the work order details or a 404 Not Found error if it doesn't exist.
    """
    result = service.get_work_order_by_id(item_id)
    return JSONResponse(status_code=result["status_code"], content=result)


@router.patch("/{item_id}/status")
def update_work_order_status(
    item_id: str,
    data: UpdateWorkOrderStatusSchema,
    service: WorkOrderService = Depends(get_work_order_service)
):
    """
    Update the status of a specific Work Order.
    
    This is a partial update focused only on the 'status' field.
    """
    result = service.update_work_order_status(item_id, data)
    return JSONResponse(status_code=result["status_code"], content=result)