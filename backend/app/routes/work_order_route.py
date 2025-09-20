# app/api/routes/wo_router.py

from fastapi import APIRouter, Depends, status, Body
from typing import Dict, Any

from pymongo.database import Database
from app.core.db_connection import get_db # Assuming a dependency to get the DB
from app.service.work_order_service import WorkOrderService
from app.models.work_order_model import WorkOrderUpdate, StartProcessPayload

router = APIRouter(
    prefix="/work-orders",
    tags=["Work Orders"]
)

@router.post(
    "/start-process",
    summary="Start a Manufacturing Process",
    description="Triggers the start of a planned MO, setting its status to 'in_progress'.",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK
)
async def start_manufacturing_process(
    payload: StartProcessPayload,
    db: Database = Depends(get_db)
):
    service = WorkOrderService(db)
    return await service.start_manufacturing_process(payload.mo_id)

@router.patch(
    "/{wo_id}/status",
    summary="Update Work Order Status (The Trigger)",
    description="Updates a WO's status. If all WOs for an MO become 'done', the parent MO is automatically completed.",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK
)
async def update_work_order_status(
    wo_id: str,
    update_data: WorkOrderUpdate,
    db: Database = Depends(get_db)
):
    service = WorkOrderService(db)
    return await service.update_work_order_status(wo_id, update_data.status)