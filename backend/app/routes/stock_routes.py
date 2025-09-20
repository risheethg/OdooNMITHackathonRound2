import inspect
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.core.logger import logs
from app.service.ledger_service import StockLedgerService
from app.utils.response_model import response
from app.core.security import RoleChecker
from app.models.user_model import UserRole
from pymongo.database import Database
router = APIRouter(
    prefix="/stock",
    tags=["Stock"],
    dependencies=[Depends(RoleChecker([UserRole.INVENTORY_MANAGER, UserRole.ADMIN]))]
)

stock_ledger_service = StockLedgerService(db=Database)  # Pass the actual Database instance here

@router.get("/availability", summary="Get Current Stock Availability")
async def get_stock_availability(request: Request):
    """
    GET /stock/availability - matches the workflow description exactly.
    
    Returns current stock levels for all products.
    The backend calculates this by reading the entire history of transactions 
    from the stock_ledger, adds and subtracts all changes, and returns the 
    final up-to-the-second calculated total for each item.
    """
    try:
        availability = await stock_ledger_service.get_current_stock_levels()
        
        final_response = response.success(
            data=availability,
            message="Current stock availability retrieved successfully"
        )
        logs.define_logger(20, "Stock availability request successful", request=request, response=final_response)
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(50, f"Error getting stock availability: {e}", request=request, loggName=inspect.stack()[0])
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)