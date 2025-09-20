# app/services/wo_service.py

import inspect
from typing import Dict, Any, List

from fastapi import HTTPException, status, Request # Import Request
from pymongo.database import Database

# Correct the import paths according to your project structure
from ..repo.work_order_repo import WorkOrderRepository
from ..repo.manufacture_repo import ManufacturingOrderRepository
from ..service.manufacture_service import ManufacturingOrderService 
from ..core.logger import logs 

class WorkOrderService:
    """
    Handles business logic for Work Orders, including the trigger for completing a
    Manufacturing Order.
    """
    def __init__(self, db: Database):
        self.wo_repo = WorkOrderRepository(db)
        self.mo_repo = ManufacturingOrderRepository(db)
        self.mo_service = ManufacturingOrderService(db)

    def get_work_orders(self, mo_id: str = None) -> List[Dict[str, Any]]:
        """
        Retrieves work orders. If mo_id is provided, it fetches work orders for
        that specific manufacturing order, sorted by sequence. Otherwise, it
        fetches all work orders.
        """
        if mo_id:
            logs.define_logger(
                level=20,
                message=f"Fetching work orders for MO ID: {mo_id}",
                loggName=inspect.stack()[0]
            )
            # find_by_mo_id already sorts by sequence
            return self.wo_repo.find_by_mo_id(mo_id)
        else:
            logs.define_logger(
                level=20,
                message="Fetching all work orders",
                loggName=inspect.stack()[0]
            )
            # get_all does not sort, which is fine for a general listing.
            return self.wo_repo.get_all()

    async def update_work_order_status(self, wo_id: str, new_status: str, request: Request = None) -> Dict[str, Any]:
        """
        Updates a WO's status. If the new status is 'done', it checks if the parent MO
        can be completed.
        """
        logs.define_logger(
            level=20,
            message=f"Updating WO {wo_id} to status '{new_status}'",
            loggName=inspect.stack()[0],
            request=request
        )

        # 1. Validate and fetch the Work Order
        work_order = self.wo_repo.get_by_id(wo_id)
        if not work_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Work Order {wo_id} not found.")

        # Prevent re-processing a 'done' order
        if work_order.get("status") == "done":
            return {"message": "Work Order is already completed.", "wo_id": wo_id}

        # 2. Update the status
        self.wo_repo.update(wo_id, {"status": new_status})

        # 3. If WO is done, automate the next step
        if new_status == "done":
            mo_id = work_order["mo_id"]
            all_wos_for_mo = self.wo_repo.find_by_mo_id(mo_id)
            
            # First, check if all work orders for the MO are now complete
            if all(wo.get("status") == "done" for wo in all_wos_for_mo):
                logs.define_logger(
                    level=20,
                    message=f"All WOs for MO {mo_id} are done. Triggering MO completion.",
                    loggName=inspect.stack()[0],
                    request=request
                )
                await self.mo_service.complete_manufacturing_order(mo_id)
                return {"message": f"Final Work Order completed, which triggered completion of parent MO.", "wo_id": wo_id, "mo_id": mo_id}
            
            # If not all are done, find the next sequential WO and start it
            else:
                completed_wo_index = -1
                for i, wo in enumerate(all_wos_for_mo):
                    if str(wo["_id"]) == wo_id:
                        completed_wo_index = i
                        break
                
                # If there is a next work order in the sequence, start it
                if completed_wo_index != -1 and completed_wo_index < len(all_wos_for_mo) - 1:
                    next_wo = all_wos_for_mo[completed_wo_index + 1]
                    if next_wo.get("status") == "pending":
                        next_wo_id = str(next_wo["_id"])
                        self.wo_repo.update(next_wo_id, {"status": "in_progress"})
                        logs.define_logger(
                            level=20,
                            message=f"WO {wo_id} completed. Automatically starting next WO {next_wo_id}.",
                            loggName=inspect.stack()[0],
                            request=request
                        )
                        return {"message": f"Work Order {wo_id} completed. Next work order {next_wo_id} started.", "wo_id": wo_id, "next_wo_id_started": next_wo_id}

        # For any other status update, or if no further automation was triggered,
        # return the updated work order.
        return self.wo_repo.get_by_id(wo_id)