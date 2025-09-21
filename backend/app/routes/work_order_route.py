# app/api/routes/wo_router.py

from fastapi import APIRouter, Depends, status, Body, Query
from typing import Dict, Any, List

from pymongo.database import Database
from app.core.db_connection import get_db # Assuming a dependency to get the DB
from app.service.work_order_service import WorkOrderService
from app.models.work_order_model import WorkOrderUpdate, WorkOrderInDB
from app.core.security import RoleChecker
from app.models.user_model import UserRole

router = APIRouter(
    prefix="/work-orders",
    tags=["Work Orders"]
)

@router.get(
    "/",
    summary="Get All Work Orders",
    description="Retrieves a list of all work orders. Can be filtered by `mo_id` to see the sequence of subprocesses and their statuses for a specific manufacturing order.",
    response_model=List[WorkOrderInDB],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker([
        UserRole.OPERATOR, UserRole.MANUFACTURING_MANAGER, UserRole.ADMIN
    ]))]
)
def get_all_work_orders(
    mo_id: str = Query(None, description="Filter work orders by Manufacturing Order ID"),
    db: Database = Depends(get_db)
):
    service = WorkOrderService(db)
    return service.get_work_orders(mo_id=mo_id)

@router.patch(
    "/{wo_id}/status",
    summary="Update Work Order Status (The Trigger)",
    description="Updates a WO's status. If all WOs for an MO become 'done', the parent MO is automatically completed.",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RoleChecker([
        UserRole.OPERATOR, UserRole.MANUFACTURING_MANAGER, UserRole.ADMIN
    ]))]
)
async def update_work_order_status(
    wo_id: str,
    update_data: WorkOrderUpdate,
    db: Database = Depends(get_db)
):
    service = WorkOrderService(db)
    return await service.update_work_order_status(wo_id, update_data.status)