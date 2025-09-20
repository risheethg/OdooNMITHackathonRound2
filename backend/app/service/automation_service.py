import asyncio
import inspect
from typing import Dict, List
from pymongo.database import Database
from app.core.logger import logs
from app.repo.work_order_repo import WorkOrderRepository
from app.service.work_order_service import WorkOrderService

class AutomationService:
    """
    Contains the business logic for polling and automating manufacturing processes.
    """
    def __init__(self, db: Database):
        self.db = db
        self.wo_repo = WorkOrderRepository(db)
        self.wo_service = WorkOrderService(db)

    async def _simulate_and_complete_wo(self, wo: Dict):
        """
        Simulates a single work order being processed and marks it as done.
        This is a helper for the main polling task.
        """
        wo_id = str(wo["_id"])
        
        try:
            # Optimistically "lock" the WO by changing its status to 'processing'
            # This prevents other polling cycles from picking up the same job.
            self.wo_repo.update(wo_id, {"status": "processing"})
            logs.define_logger(20, f"AUTOMATION: Simulating work for WO {wo_id} for 30 seconds...", loggName=inspect.stack()[0])
            
            # Simulate the time it takes to perform the work
            await asyncio.sleep(30)
            
            logs.define_logger(20, f"AUTOMATION: Work for WO {wo_id} finished. Updating status to 'done'.", loggName=inspect.stack()[0])
            
            # Use the WorkOrderService to properly update the status to 'done'.
            # This service contains the crucial logic to advance the workflow to the next WO or complete the parent MO.
            await self.wo_service.update_work_order_status(wo_id=wo_id, new_status="done")

        except Exception as e:
            logs.define_logger(40, f"AUTOMATION: Error processing WO {wo_id}: {e}. Setting status back to 'pending'.", loggName=inspect.stack()[0])
            # If something goes wrong, reset the status so it can be picked up again or handled manually.
            self.wo_repo.update(wo_id, {"status": "pending"})


    async def polling_task(self):
        """
        The main task to be registered with the PollingService.
        It finds work orders that are 'in_progress' and processes them concurrently.
        """
        work_orders_to_process = self.wo_repo.get_all({"status": "in_progress"})
        
        if not work_orders_to_process:
            return # Nothing to do in this cycle

        processing_tasks = [self._simulate_and_complete_wo(wo) for wo in work_orders_to_process]
        await asyncio.gather(*processing_tasks)