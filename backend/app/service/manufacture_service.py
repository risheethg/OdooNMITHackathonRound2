import inspect
from typing import List, Dict, Any

from fastapi import HTTPException
from repository.manufacturing_order_repository import ManufacturingOrderRepository
from models.manufacturing_order import ManufacturingOrderCreate, ManufacturingOrder, WorkOrder, BillOfMaterials
from core.logger import logs

# --- Mock Repositories (Replace with your actual imports) ---
class MockRepo:
    def get_by_id(self, id): return None
    def find_one(self, query): return {"product_id": "mock_prod", "components": [], "operations": []}
class MockStockLedgerRepo:
    def get_current_stock_for_product(self, product_id): return 1000
ProductRepository = MockRepo
BomRepository = MockRepo
StockLedgerRepository = MockStockLedgerRepo
# --- End Mocks ---

class ManufacturingOrderService:
    """
    Handles business logic for MOs. Returns raw data or raises HTTPErrors.
    """
    def __init__(self):
        self.mo_repo = ManufacturingOrderRepository()
        self.product_repo = ProductRepository()
        self.bom_repo = BomRepository()
        self.stock_repo = StockLedgerRepository()

    async def create_manufacturing_order(self, order_data: ManufacturingOrderCreate) -> Dict[str, Any]:
        logs.define_logger(20, "Executing create_manufacturing_order service", loggName=inspect.stack()[0])
        
        bom_data = self.bom_repo.find_one({"product_id": order_data.product_id})
        if not bom_data:
            raise HTTPException(status_code=404, detail="Bill of Materials not found for this product.")
        
        bom = BillOfMaterials(**bom_data)

        # (Stock check logic would go here, raising HTTPException if insufficient)

        work_orders_to_create = [WorkOrder(operation_name=op['name'], work_center_id=op.get('work_center_id', 'default')) for op in bom.operations]
        
        new_mo_model = ManufacturingOrder(
            product_id=order_data.product_id,
            quantity_to_produce=order_data.quantity,
            bom_snapshot=bom,
            work_orders=work_orders_to_create
        )
        mo_dict_to_save = new_mo_model.model_dump(by_alias=True, exclude_none=True)
        del mo_dict_to_save['_id']
        
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
