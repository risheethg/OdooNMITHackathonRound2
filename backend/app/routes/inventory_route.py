from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.core.db_connection import get_db
from app.repo.product_repo import ProductRepository
from app.repo.ledger_repo import StockLedgerRepository
from app.service.inventory_service import InventoryService
from pymongo.database import Database

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)

def get_inventory_service(
    db: Database = Depends(get_db)
) -> InventoryService:
    # Directly instantiate ProductRepository and StockLedgerRepository
    product_repo = ProductRepository(db)
    ledger_repo = StockLedgerRepository(db)
    return InventoryService(product_repo, ledger_repo)

@router.get("/stock/availability", response_model=List[Dict[str, Any]])
async def get_stock_availability(
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """
    Retrieves the current stock availability for all products by
    calculating the total quantity from the stock ledger.
    """
    try:
        stock_report = await inventory_service.get_stock_availability_from_ledger()
        return stock_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))