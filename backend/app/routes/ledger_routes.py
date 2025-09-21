import inspect
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
import os
from app.core.db_connection import get_db
from app.core.logger import logs
from app.service.ledger_service import StockLedgerService
from app.utils.response_model import response
from app.core.security import RoleChecker
from app.models.user_model import UserRole
from pymongo.database import Database
from datetime import datetime

router = APIRouter(
    prefix="/stock-ledger",
    tags=["Stock Ledger"],
    dependencies=[Depends(RoleChecker([UserRole.INVENTORY_MANAGER, UserRole.ADMIN]))]
)

def get_stock_ledger_service(db: Database = Depends(get_db)) -> StockLedgerService:
    return StockLedgerService(db) # Pass the actual Database instance here

def ensure_serializable(data):
    """
    Converts all datetime fields in a list of records to ISO strings for JSON serializability.
    """
    for entry in data:
        for key, val in entry.items():
            if isinstance(val, datetime):
                entry[key] = val.isoformat()
    return data

@router.get("/", summary="Get Stock Ledger History")
async def get_stock_ledger_history(request: Request, stock_ledger_service: StockLedgerService = Depends(get_stock_ledger_service)):
    """
    Retrieves the complete, chronological history of all inventory movements.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Fetching stock ledger history...", loggName=log_info, pid=os.getpid(), request=request)
    try:
        history = await stock_ledger_service.get_ledger_history()
        # Serialize datetime fields
        history = ensure_serializable(history)

        final_response = response.success(
            data=history,
            message="Stock ledger history retrieved successfully"
        )
        logs.define_logger(level=logging.INFO, message="Stock ledger history fetched successfully.", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(level=logging.ERROR, message=f"Error getting stock ledger history: {e}", loggName=log_info, pid=os.getpid(), request=request)
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)

@router.get("/availability", summary="Get Current Stock Availability")
async def get_stock_availability(request: Request, stock_ledger_service: StockLedgerService = Depends(get_stock_ledger_service)):
    """
    Provides a real-time summary of the current stock level for every product.
    This is calculated by summing all historical movements.
    """
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Fetching current stock availability...", loggName=log_info, pid=os.getpid(), request=request)
    try:
        availability = await stock_ledger_service.get_current_stock_levels()
        # Serialize datetime fields (if availability ever contains any datetimes)
        availability = ensure_serializable(availability)

        final_response = response.success(
            data=availability,
            message="Current stock availability retrieved successfully"
        )
        logs.define_logger(level=logging.INFO, message="Stock availability fetched successfully.", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(level=logging.ERROR, message=f"Error getting stock availability: {e}", loggName=log_info, pid=os.getpid(), request=request)
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)
