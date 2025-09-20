import inspect
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from core.logger import logs
from app.service.ledger_service import StockLedgerService
from app.utils.response_model import response

router = APIRouter(
    prefix="/stock-ledger",
    tags=["Stock Ledger"]
)

stock_ledger_service = StockLedgerService()

@router.get("/", summary="Get Stock Ledger History")
async def get_stock_ledger_history(request: Request):
    """
    Retrieves the complete, chronological history of all inventory movements.
    """
    try:
        history = await stock_ledger_service.get_ledger_history()
        
        final_response = response.success(
            data=history,
            message="Stock ledger history retrieved successfully"
        )
        logs.define_logger(20, "Stock ledger history request successful", request=request, response=final_response)
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(50, f"Error getting stock ledger history: {e}", request=request, loggName=inspect.stack()[0])
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)


@router.get("/availability", summary="Get Current Stock Availability")
async def get_stock_availability(request: Request):
    """
    Provides a real-time summary of the current stock level for every product.
    This is calculated by summing all historical movements.
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
