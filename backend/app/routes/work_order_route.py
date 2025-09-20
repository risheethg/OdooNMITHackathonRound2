# app/work_orders/work_order_router.py

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from .work_order_service import WorkOrderService, get_work_order_service
from .work_order_schema import CreateWorkOrderSchema, UpdateWorkOrderStatusSchema

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
    Create a new Work Order. The `workCenterId` in the payload must correspond
    to a Work Centre that has been created beforehand.
    """
    result = service.create_work_order(data)
    return JSONResponse(status_code=result["status_code"], content=result)

# --- New Endpoint Added ---
@router.get("/")
def get_all_work_orders(
    service: WorkOrderService = Depends(get_work_order_service)
):
    """
    Retrieve a list of all Work Orders.
    """
    result = service.get_all_work_orders()
    return JSONResponse(status_code=result["status_code"], content=result)

@router.get("/{item_id}")
def get_work_order(
    item_id: str,
    service: WorkOrderService = Depends(get_work_order_service)
):
    result = service.get_work_order_by_id(item_id)
    return JSONResponse(status_code=result["status_code"], content=result)

@router.patch("/{item_id}/status")
def update_work_order_status(
    item_id: str,
    data: UpdateWorkOrderStatusSchema,
    service: WorkOrderService = Depends(get_work_order_service)
):
    result = service.update_work_order_status(item_id, data)
    return JSONResponse(status_code=result["status_code"], content=result)