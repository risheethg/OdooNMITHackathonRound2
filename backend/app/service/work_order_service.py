# app/work_orders/work_order_service.py

import inspect
from datetime import datetime, timezone
from bson import ObjectId
from app.core.logger import logs
from app.core.response_model import response
from .work_order_repo import WorkOrderRepository, get_work_order_repo
from .work_order_schema import CreateWorkOrderSchema, UpdateWorkOrderStatusSchema, WorkOrderResponseSchema

class WorkOrderService:
    def __init__(self, repo: WorkOrderRepository):
        self.repo = repo

    def create_work_order(self, data: CreateWorkOrderSchema):
        """
        Creates a new work order.
        The payload should include the ID of a pre-existing Work Centre.
        """
        try:
            if not ObjectId.is_valid(data.manufacturingOrderId):
                return response.failure("Invalid manufacturingOrderId format", status_code=400)
            
            # This is the key part: We check if a workCenterId was provided and validate it.
            # This ID comes from a Work Centre that was created beforehand.
            if data.workCenterId and not ObjectId.is_valid(data.workCenterId):
                return response.failure("Invalid workCenterId format", status_code=400)

            work_order_data = data.model_dump()
            
            work_order_data["manufacturingOrderId"] = ObjectId(data.manufacturingOrderId)
            if data.workCenterId:
                work_order_data["workCenterId"] = ObjectId(data.workCenterId)

            now = datetime.now(timezone.utc)
            work_order_data["createdAt"] = now
            work_order_data["updatedAt"] = now

            result = self.repo.create(work_order_data)
            new_id = result.inserted_id
            
            logs.define_logger(level=20, loggName=inspect.stack()[0], message=f"Successfully created work order with ID: {new_id}")
            return response.success(data={"id": str(new_id)}, message="Work order created successfully", status_code=201)

        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error creating work order: {e}", body=data.model_dump_json())
            return response.failure(message=f"Failed to create work order: {e}", status_code=500)

    def get_all_work_orders(self):
        """
        Retrieves a list of all work orders.
        """
        try:
            work_order_docs = self.repo.get_all()
            results = [
                WorkOrderResponseSchema.model_validate(wo).model_dump(by_alias=True)
                for wo in work_order_docs
            ]
            return response.success(data=results)
        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error retrieving all work orders: {e}")
            return response.failure(message=f"An error occurred: {e}", status_code=500)
    
    # ... (get_work_order_by_id and update_work_order_status methods remain the same) ...
    def get_work_order_by_id(self, item_id: str):
        if not ObjectId.is_valid(item_id):
            return response.failure(message="Invalid work order ID format", status_code=400)

        try:
            work_order_doc = self.repo.get_by_id(item_id)
            if work_order_doc:
                validated_data = WorkOrderResponseSchema.model_validate(work_order_doc)
                return response.success(data=validated_data.model_dump(by_alias=True))
            else:
                return response.failure(message="Work order not found", status_code=404)

        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error retrieving work order {item_id}: {e}")
            return response.failure(message=f"An error occurred: {e}", status_code=500)

    def update_work_order_status(self, item_id: str, data: UpdateWorkOrderStatusSchema):
        if not ObjectId.is_valid(item_id):
            return response.failure(message="Invalid work order ID format", status_code=400)
            
        try:
            existing_work_order = self.repo.get_by_id(item_id)
            if not existing_work_order:
                return response.failure(message="Work order not found", status_code=404)

            update_data = {
                "status": data.status.value,
                "updatedAt": datetime.now(timezone.utc)
            }
            self.repo.update(item_id, update_data)
            
            logs.define_logger(level=20, loggName=inspect.stack()[0], message=f"Updated status for work order ID: {item_id} to {data.status.value}")
            return response.success(data=None, message="Work order status updated successfully")

        except Exception as e:
            logs.define_logger(level=40, loggName=inspect.stack()[0], message=f"Error updating work order {item_id}: {e}", body=data.model_dump_json())
            return response.failure(message=f"Failed to update work order status: {e}", status_code=500)
            
def get_work_order_service() -> WorkOrderService:
    repo = get_work_order_repo()
    return WorkOrderService(repo)