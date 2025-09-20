# app/services/wo_service.py

import inspect
from typing import Dict, Any

from fastapi import HTTPException, status
from pymongo.database import Database

from app.repo.work_order_repo import WorkOrderRepository
from app.repo.manufacture_repo import ManufacturingOrderRepository
from app.service.manufacture_service import ManufacturingOrderService 
from app.core.logger import logs 

class WorkOrderService:
    """
    Handles business logic for Work Orders, including the trigger for completing a
    Manufacturing Order.
    """
    def __init__(self, db: Database):
        self.wo_repo = WorkOrderRepository(db)
        self.mo_repo = ManufacturingOrderRepository(db)
        # Instantiate MO service to use its 'complete' method, ensuring inventory logic is reused
        self.mo_service = ManufacturingOrderService(db)

    async def start_manufacturing_process(self, mo_id: str) -> Dict[str, Any]:
        """
        Starts the process for a given MO by updating its status and the status
        of its first work order.
        """
        logs.info(f"Attempting to start process for MO ID: {mo_id}")

        # 1. Validate the Manufacturing Order
        mo = self.mo_repo.get_by_id(mo_id)
        if not mo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Manufacturing Order {mo_id} not found.")
        
        if mo.get("status") != "planned":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"MO must be in 'planned' state. Current state: {mo.get('status')}")

        # 2. Find associated Work Orders
        work_orders = self.wo_repo.find_by_mo_id(mo_id)
        if not work_orders:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No work orders found for this MO. Cannot start process.")

        # 3. Update statuses
        self.mo_repo.update(mo_id, {"status": "in_progress"})
        first_wo_id = str(work_orders[0]["_id"])
        self.wo_repo.update(first_wo_id, {"status": "in_progress"})

        logs.info(f"Process for MO {mo_id} started. First WO {first_wo_id} is now 'in_progress'.")

        return {"message": "Manufacturing process started successfully.", "mo_id": mo_id, "first_wo_id": first_wo_id}

    async def update_work_order_status(self, wo_id: str, new_status: str) -> Dict[str, Any]:
        """
        Updates a WO's status. If the new status is 'done', it checks if the parent MO
        can be completed.
        """
        logs.info(f"Updating WO {wo_id} to status '{new_status}'")

        # 1. Validate and fetch the Work Order
        work_order = self.wo_repo.get_by_id(wo_id)
        if not work_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Work Order {wo_id} not found.")

        # 2. Update the status
        self.wo_repo.update(wo_id, {"status": new_status})

        # 3. If WO is done, check if the parent MO is now complete (the "trigger")
        if new_status == "done":
            mo_id = work_order["mo_id"]
            all_wos_for_mo = self.wo_repo.find_by_mo_id(mo_id)
            
            # Check if all WOs for this parent MO are now done
            if all(wo.get("status") == "done" for wo in all_wos_for_mo):
                logs.info(f"All WOs for MO {mo_id} are done. Triggering MO completion.")
                await self.mo_service.complete_manufacturing_order(mo_id)
                return {
                    "message": f"Work Order completed, which triggered completion of parent MO.",
                    "wo_id": wo_id,
                    "mo_id": mo_id
                }

        updated_wo = self.wo_repo.get_by_id(wo_id)
        updated_wo["_id"] = str(updated_wo["_id"])
        return updated_wo