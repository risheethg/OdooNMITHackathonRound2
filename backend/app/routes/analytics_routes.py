import inspect
import logging
import os
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import JSONResponse

from app.app.core.logger import logs
from app.service.analytics_service import AnalyticsService
from app.utils.response_model import response
from app.core.db_connection import get_db
from app.models.analytics_model import ProductionThroughput
from app.core.security import RoleChecker
from app.models.user_model import UserRole
from app.core.db_connection import get_db
from pymongo.database import Database

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics Dashboard"],
    dependencies=[Depends(RoleChecker([UserRole.ADMIN]))]
)

def get_service(db: Database = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)

@router.get("/overview", summary="Get Status Overview KPIs")
async def get_status_overview(request: Request, service: AnalyticsService = Depends(get_service)):
    """
    Provides a high-level overview of Manufacturing Orders by status.
    """
    try:
        overview = await service.get_status_overview()
        final_response = response.success(data=overview.model_dump(), message="Status overview retrieved successfully")
        logs.define_logger(logging.INFO, "Status overview request successful", request=request, response=final_response, loggName=inspect.stack()[0], pid=os.getpid())
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(logging.ERROR, f"Error getting status overview: {e}", request=request, loggName=inspect.stack()[0], pid=os.getpid())
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)


@router.get("/throughput", summary="Get Production Throughput")
async def get_production_throughput(request: Request, period_days: int = Query(7, ge=1, le=365), service: AnalyticsService = Depends(get_service)):
    """
    Retrieves the number of completed orders per day for a given period.
    """
    try:
        throughput_data = await service.get_production_throughput(days=period_days)
        
        data_to_return = ProductionThroughput(
            period=f"Last {period_days} days",
            data=throughput_data
        )
        
        final_response = response.success(data=data_to_return.model_dump(), message="Production throughput retrieved successfully")
        logs.define_logger(logging.INFO, "Production throughput request successful", request=request, response=final_response, loggName=inspect.stack()[0], pid=os.getpid())
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(logging.ERROR, f"Error getting production throughput: {e}", request=request, loggName=inspect.stack()[0], pid=os.getpid())
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)


@router.get("/cycle-time", summary="Get Average Cycle Time")
async def get_average_cycle_time(request: Request, service: AnalyticsService = Depends(get_service)):
    """
    Calculates the average time it takes to complete a manufacturing order.
    """
    try:
        cycle_time = await service.get_average_cycle_time()
        final_response = response.success(data=cycle_time.model_dump(), message="Average cycle time retrieved successfully")
        logs.define_logger(logging.INFO, "Average cycle time request successful", request=request, response=final_response, loggName=inspect.stack()[0], pid=os.getpid())
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(logging.ERROR, f"Error getting average cycle time: {e}", request=request, loggName=inspect.stack()[0], pid=os.getpid())
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)
