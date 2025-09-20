import inspect
import os
from typing import Dict, Any, List
from fastapi import HTTPException
from app.repo.product_repo import ProductRepository
from app.repo.ledger_repo import StockLedgerRepository
from app.core.logger import logs

class InventoryService:
    def __init__(self, product_repo: ProductRepository, ledger_repo: StockLedgerRepository):
        self.product_repo = product_repo
        self.ledger_repo = ledger_repo

    def check_stock_for_bom(self, bom_components: List[Dict[str, Any]], quantity_to_produce: int):
        """
        Checks if sufficient stock exists for all components in a Bill of Materials (BOM)
        for a given quantity of finished goods.
        """
        logs.define_logger(20, "Checking stock for BOM", loggName=inspect.stack()[0], pid=os.getpid())
        for component in bom_components:
            product_id = component.get("productId")
            required_quantity = component.get("quantity") * quantity_to_produce
            
            product = self.product_repo.get_by_id(str(product_id))
            if not product:
                logs.define_logger(40, f"Component product not found: {product_id}", loggName=inspect.stack()[0], pid=os.getpid())
                raise HTTPException(status_code=404, detail=f"Component product ID {product_id} not found.")

            current_stock = product.get("current_quantity", 0)
            if current_stock < required_quantity:
                logs.define_logger(40, f"Insufficient stock for component {product.get('name')}", loggName=inspect.stack()[0], pid=os.getpid())
                raise HTTPException(status_code=400, detail=f"Insufficient stock for component '{product.get('name')}'. Required: {required_quantity}, Available: {current_stock}")
        
        logs.define_logger(20, "Stock check passed", loggName=inspect.stack()[0], pid=os.getpid())
        return True

    def get_stock_availability(self) -> List[Dict[str, Any]]:
        """
        Retrieves the current stock availability for all products by
        calling the aggregation method in the Ledger Repository.
        """
        logs.define_logger(20, "Getting stock availability from ledger repo", loggName=inspect.stack()[0], pid=os.getpid())
        
        try:
            results = self.ledger_repo.get_stock_availability()
            logs.define_logger(20, "Stock availability retrieved successfully", loggName=inspect.stack()[0], pid=os.getpid())
            return results
        except Exception as e:
            logs.define_logger(50, f"Error retrieving stock availability: {e}", loggName=inspect.stack()[0], pid=os.getpid())
            raise HTTPException(status_code=500, detail=str(e))
