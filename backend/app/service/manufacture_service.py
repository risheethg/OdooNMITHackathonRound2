import inspect
from typing import List, Dict, Any

from fastapi import HTTPException
from ..repo.manufacture_repo import ManufacturingOrderRepository
from ..repo.product_repo import ProductRepository
from ..repo.bom_repo import BOMRepository
from ..repo.ledger_repo import StockLedgerRepository
from ..repo.work_centre_repo import WorkCentreRepository
from ..repo.work_order_repo import WorkOrderRepository
from ..models.manufacture import ManufacturingOrderCreate, ManufacturingOrder, WorkOrder, BillOfMaterials
from ..models.ledger_model import StockLedgerEntryCreate
from ..core.logger import logs
from ..utils.websocket_manager import connection_manager
from datetime import datetime, timezone
from pymongo.database import Database

class ManufacturingOrderService:
    """
    Handles business logic for MOs. Returns raw data or raises HTTPErrors.
    """
    def __init__(self, db: Database):
        self.mo_repo = ManufacturingOrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.bom_repo = BOMRepository(db)
        self.stock_repo = StockLedgerRepository(db)
        self.wc_repo = WorkCentreRepository(db)
        self.wo_repo = WorkOrderRepository(db)

    async def create_manufacturing_order(self, order_data: ManufacturingOrderCreate) -> Dict[str, Any]:
        logs.define_logger(20, "Executing create_manufacturing_order service", loggName=inspect.stack()[0])
        
        # Get BOM for the product
        bom_data = self.bom_repo.find_one({"finishedProductId": order_data.product_id})
        if not bom_data:
            raise HTTPException(status_code=404, detail="Bill of Materials not found for this product.")
        
        # Validate product exists
        product = self.product_repo.get_by_id(order_data.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")

        # Convert MongoDB document to BillOfMaterials model
        # Remove MongoDB _id and convert the document
        if "_id" in bom_data:
            del bom_data["_id"]
            
        # Map the BOM fields properly
        bom = BillOfMaterials(
            product_id=bom_data["finishedProductId"],
            components=bom_data.get("components", []),
            operations=bom_data.get("operations", [])
        )

        # Create work orders from BOM operations
        work_orders_to_create = []
        for i, op in enumerate(bom.operations):
            operation_name = op.get('name', op.get('operation_name', 'Unknown Operation'))
            
            # Find work center by operation name
            work_center = self.wc_repo.find_one({"operation": operation_name})
            if not work_center:
                raise HTTPException(status_code=404, detail=f"Work Center for operation '{operation_name}' not found.")

            work_order = WorkOrder(
                operation_name=operation_name,
                work_center_id=str(work_center["_id"]),
                sequence=i
            )
            work_orders_to_create.append(work_order)
        
        new_mo_model = ManufacturingOrder(
                mo_id='1234',  # Will be set by MongoDB
                product_id=order_data.product_id,
                quantity_to_produce=order_data.quantity,
                bom_snapshot=bom,
                work_orders=work_orders_to_create,
                
        )
        
        # Convert the model to a dictionary for MongoDB
        mo_dict_to_save = new_mo_model.model_dump(by_alias=True, exclude_none=True)
        
        # REMOVED: del mo_dict_to_save['_id'] -> This line caused the error

        # Create the document in the database
        result = self.mo_repo.create(mo_dict_to_save)
        created_id = str(result.inserted_id)

        # --- AUTOMATION STEP 1: Create and immediately start the process ---

        # Now create the corresponding documents in the 'work_orders' collection
        first_wo_id = None
        for wo_model in work_orders_to_create:
            # The wo_model is a Pydantic model, convert it to a dict
            wo_data = wo_model.model_dump(exclude_none=True)
            wo_data['mo_id'] = created_id
            wo_result = self.wo_repo.create(wo_data)
            if wo_data.get("sequence") == 0:
                first_wo_id = str(wo_result.inserted_id)

        # Automatically set the MO and the first WO to 'in_progress'
        if first_wo_id:
            self.mo_repo.update(created_id, {"status": "in_progress"})
            self.wo_repo.update(first_wo_id, {"status": "in_progress"})
            logs.define_logger(20, f"Automatically started MO {created_id} and first WO {first_wo_id}", loggName=inspect.stack()[0])
            # Broadcast MO + first WO started
            ts = datetime.now(timezone.utc).isoformat()
            await connection_manager.send_to_topic(
                project_id=created_id,
                topic="mo_status",
                data={
                    "event": "manufacturing_order_started",
                    "mo_id": created_id,
                    "status": "in_progress",
                    "timestamp": ts,
                },
            )
            await connection_manager.send_to_topic(
                project_id=first_wo_id,
                topic="wo_status",
                data={
                    "event": "work_order_auto_started",
                    "mo_id": created_id,
                    "work_order_id": first_wo_id,
                    "previous_status": "pending",
                    "status": "in_progress",
                    "timestamp": ts,
                },
            )
        
        return {"mo_id": created_id}

    async def get_all_manufacturing_orders(self, status: str | None = None) -> List[Dict[str, Any]]:
        query = {}
        if status:
            query["status"] = status
        orders = self.mo_repo.get_all(query)
        for order in orders:
            order["_id"] = str(order["_id"])
        return orders

    async def get_manufacturing_order_by_id(self, mo_id: str) -> Dict[str, Any]:
        order = self.mo_repo.get_by_id(mo_id)
        if not order:
            raise HTTPException(status_code=404, detail="Manufacturing Order not found.")
        order["_id"] = str(order["_id"])
        return order
    
    async def delete_manufacturing_order(self, mo_id: str) -> None:
        order = self.mo_repo.get_by_id(mo_id)
        if not order:
            raise HTTPException(status_code=404, detail="Manufacturing Order not found.")
        
        if order.get("status") in ["in_progress", "done"]:
            raise HTTPException(status_code=400, detail="Cannot delete an order that is in progress or completed.")
        
        self.mo_repo.delete(mo_id)
        return

    async def complete_manufacturing_order(self, mo_id: str) -> Dict[str, Any]:
        """
        Complete a manufacturing order and automatically update inventory.
        """
        logs.define_logger(20, f"Completing manufacturing order: {mo_id}", loggName=inspect.stack()[0])
        
        # Get the manufacturing order
        order = self.mo_repo.get_by_id(mo_id)
        if not order:
            raise HTTPException(status_code=404, detail="Manufacturing Order not found.")
        
        if order.get("status") == "done":
            raise HTTPException(status_code=400, detail="Manufacturing Order is already completed.")
        
        if order.get("status") != "in_progress":
            raise HTTPException(status_code=400, detail="Manufacturing Order must be in progress to complete.")
        
        # Get BOM snapshot from the order
        bom_snapshot = order.get("bom_snapshot", {})
        quantity_to_produce = order.get("quantity_to_produce", 0)
        
        # Create stock ledger entries for component consumption (negative entries)
        ledger_entries = []
        for component in bom_snapshot.get("components", []):
            component_id = component.get("productId")
            component_qty = component.get("quantity", 0)
            total_consumption = component_qty * quantity_to_produce
            
            # Create negative entry for component consumption
            consumption_entry = StockLedgerEntryCreate(
                product_id=component_id,
                quantity_change=-total_consumption,
                reason=f"Consumption for MO-{mo_id}",
                manufacturing_order_id=mo_id
            )
            ledger_entries.append(consumption_entry.model_dump())
        
        # Create stock ledger entry for finished product (positive entry)
        production_entry = StockLedgerEntryCreate(
            product_id=bom_snapshot.get("product_id"),
            quantity_change=quantity_to_produce,
            reason=f"Production from MO-{mo_id}",
            manufacturing_order_id=mo_id
        )
        ledger_entries.append(production_entry.model_dump())
        
        # Insert all ledger entries
        for entry in ledger_entries:
            if "_id" in entry and entry["_id"] is None:
                del entry["_id"]
            self.stock_repo.create(entry)
        
        # Update MO status to done
        self.mo_repo.update(mo_id, {"status": "done"})
        
        logs.define_logger(20, f"Manufacturing order {mo_id} completed successfully", loggName=inspect.stack()[0])
        # Broadcast MO completion
        ts = datetime.now(timezone.utc).isoformat()
        await connection_manager.send_to_topic(
            project_id=mo_id,
            topic="mo_status",
            data={
                "event": "manufacturing_order_completed",
                "mo_id": mo_id,
                "status": "done",
                "timestamp": ts,
            },
        )
        
        return {"message": "Manufacturing Order completed successfully", "mo_id": mo_id}