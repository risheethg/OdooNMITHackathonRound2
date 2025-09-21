import inspect
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
import logging
import os
from app.core.db_connection import get_db
from app.core.logger import logs
from app.utils.response_model import response
from app.service.inventory_service import InventoryService
from pymongo.database import Database
from datetime import datetime


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


def get_inventory_service(db: Database = Depends(get_db)) -> InventoryService:
    return InventoryService(db)


@router.get("/availability", summary="Get Current Inventory Stock Availability")
async def get_current_inventory_availability(request: Request, inventory_service: InventoryService = Depends(get_inventory_service)):
    log_info = inspect.stack()[0]
    logs.define_logger(level=logging.INFO, message="Fetching current inventory availability...", loggName=log_info, pid=os.getpid(), request=request)
    try:
        availability = await inventory_service.get_current_stock_levels()

        # Serialize datetime fields if any (generally none here)
        for entry in availability:
            for key, val in entry.items():
                if isinstance(val, datetime):
                    entry[key] = val.isoformat()

        final_response = response.success(
            data=availability,
            message="Current inventory availability retrieved successfully"
        )
        logs.define_logger(level=logging.INFO, message="Inventory availability fetched successfully.", loggName=log_info, pid=os.getpid(), request=request)
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(level=logging.ERROR, message=f"Error getting inventory availability: {e}", loggName=log_info, pid=os.getpid(), request=request)
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)
