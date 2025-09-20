import inspect
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from ..repo.manufacture_repo import ManufacturingOrderRepository
from ..repo.product_repo import ProductRepository
from ..repo.bom_repo import BOMRepository
from ..repo.ledger_repo import StockLedgerRepository
from ..models.manufacture import ManufacturingOrderCreate, ManufacturingOrder, WorkOrder, BillOfMaterials
from ..models.ledger_model import StockLedgerEntryCreate
from ..core.logger import logs
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
        if "_id" in bom_data:
            del bom_data["_id"]
            
        bom = BillOfMaterials(
            product_id=bom_data["finishedProductId"],
            components=bom_data.get("components", []),
            operations=bom_data.get("operations", [])
        )

        work_orders_to_create = []
        for op in bom.operations:
            work_order = WorkOrder(
                operation_name=op.get('name', op.get('operation_name', 'Unknown Operation')),
                work_center_id=op.get('work_center_id', 'default_work_center')
            )
            work_orders_to_create.append(work_order)
        
        new_mo_model = ManufacturingOrder(
                product_id=order_data.product_id,
                quantity_to_produce=order_data.quantity,
                bom_snapshot=bom,
                work_orders=work_orders_to_create
        )
        
        mo_dict_to_save = new_mo_model.model_dump(by_alias=True, exclude_none=True)
        # Add the new stalled flag
        mo_dict_to_save['is_stalled'] = False
        
        result = self.mo_repo.create(mo_dict_to_save)
        created_id = str(result.inserted_id)
        
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
        logs.define_logger(20, f"Completing manufacturing order: {mo_id}", loggName=inspect.stack()[0])
        
        order = self.mo_repo.get_by_id(mo_id)
        if not order:
            raise HTTPException(status_code=404, detail="Manufacturing Order not found.")
        
        if order.get("status") == "done":
            raise HTTPException(status_code=400, detail="Manufacturing Order is already completed.")
        
        if order.get("status") != "in_progress":
            raise HTTPException(status_code=400, detail="Manufacturing Order must be in progress to complete.")
        
        bom_snapshot = order.get("bom_snapshot", {})
        quantity_to_produce = order.get("quantity_to_produce", 0)
        
        ledger_entries = []
        for component in bom_snapshot.get("components", []):
            component_id = component.get("productId")
            component_qty = component.get("quantity", 0)
            total_consumption = component_qty * quantity_to_produce
            
            consumption_entry = StockLedgerEntryCreate(
                product_id=component_id,
                quantity_change=-total_consumption,
                reason=f"Consumption for MO-{mo_id}",
                manufacturing_order_id=mo_id
            )
            ledger_entries.append(consumption_entry.model_dump())
        
        production_entry = StockLedgerEntryCreate(
            product_id=bom_snapshot.get("product_id"),
            quantity_change=quantity_to_produce,
            reason=f"Production from MO-{mo_id}",
            manufacturing_order_id=mo_id
        )
        ledger_entries.append(production_entry.model_dump())
        
        for entry in ledger_entries:
            if "_id" in entry and entry["_id"] is None:
                del entry["_id"]
            self.stock_repo.create(entry)
        
        self.mo_repo.update(mo_id, {"status": "done", "completed_at": datetime.utcnow()})
        
        logs.define_logger(20, f"Manufacturing order {mo_id} completed successfully", loggName=inspect.stack()[0])
        
        return {"message": "Manufacturing Order completed successfully", "mo_id": mo_id}

    async def check_for_stalled_manufacturing_orders(self):
        """
        A background task to identify and flag manufacturing orders that have been
        in the 'in_progress' state for too long.
        """
        stalled_threshold = datetime.now(timezone.utc) - timedelta(hours=48)
        
        stalled_orders = self.mo_repo.find_many({
            "status": "in_progress",
            "updatedAt": {"$lt": stalled_threshold},
            "is_stalled": False
        })
        
        if stalled_orders:
            for order in stalled_orders:
                self.mo_repo.update(str(order['_id']), {"is_stalled": True})
                print(f"Polling: Flagged stalled manufacturing order: {order.get('_id')}")
