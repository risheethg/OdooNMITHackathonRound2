import inspect
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse

from core.logger import logs
from app.service.analytics_service import AnalyticsService
from app.utils.response_model import response
from app.models.analytics_model import ProductionThroughput
from app.core.security import RoleChecker
from app.models.user_model import UserRole

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics Dashboard"],
    dependencies=[Depends(RoleChecker([UserRole.ADMIN]))]
)

analytics_service = AnalyticsService()

@router.get("/overview", summary="Get Status Overview KPIs")
async def get_status_overview(request: Request):
    """
    Provides a high-level overview of Manufacturing Orders by status.
    """
    try:
        overview = await analytics_service.get_status_overview()
        
        final_response = response.success(data=overview.dict(), message="Status overview retrieved successfully")
        logs.define_logger(20, "Status overview request successful", request=request, response=final_response)
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(50, f"Error getting status overview: {e}", request=request, loggName=inspect.stack()[0])
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)


@router.get("/throughput", summary="Get Production Throughput")
async def get_production_throughput(request: Request, period_days: int = 7):
    """
    Retrieves the number of completed orders per day for a given period.
    """
    try:
        throughput_data = await analytics_service.get_production_throughput(days=period_days)
        
        data_to_return = ProductionThroughput(
            period=f"Last {period_days} days",
            data=throughput_data
        )
        
        final_response = response.success(data=data_to_return.dict(), message="Production throughput retrieved successfully")
        logs.define_logger(20, "Production throughput request successful", request=request, response=final_response)
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(50, f"Error getting production throughput: {e}", request=request, loggName=inspect.stack()[0])
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)


@router.get("/cycle-time", summary="Get Average Cycle Time")
async def get_average_cycle_time(request: Request):
    """
    Calculates the average time it takes to complete a manufacturing order.
    """
    try:
        cycle_time = await analytics_service.get_average_cycle_time()
        
        final_response = response.success(data=cycle_time.dict(), message="Average cycle time retrieved successfully")
        logs.define_logger(20, "Average cycle time request successful", request=request, response=final_response)
        return JSONResponse(status_code=200, content=final_response)

    except Exception as e:
        logs.define_logger(50, f"Error getting average cycle time: {e}", request=request, loggName=inspect.stack()[0])
        final_response = response.failure(message=f"An unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content=final_response)
