import inspect
from typing import List, Dict
from pymongo.database import Database
from app.repo.ledger_repo import StockLedgerRepository
from app.core.logger import logs

class InventoryService:
    """
    Service dedicated to inventory-related business logic,
    such as calculating current stock availability from ledger data.
    """
    def __init__(self, db: Database):
        self.ledger_repo = StockLedgerRepository(db)

    async def get_current_stock_levels(self) -> List[Dict]:
        logs.define_logger(20, "Calculating current stock levels in InventoryService.", loggName=inspect.stack()[0])
        ledger_entries = self.ledger_repo.get_all()
        if not ledger_entries:
            return []

        stock_levels = {}
        for entry in ledger_entries:
            pid = entry.get("product_id")
            qty_change = entry.get("quantity_change", 0)
            if pid is None:
                continue
            stock_levels[pid] = stock_levels.get(pid, 0) + qty_change

        # Convert result to a list of dicts for response
        result = [{"product_id": pid, "current_stock": qty} for pid, qty in stock_levels.items()]
        return result
