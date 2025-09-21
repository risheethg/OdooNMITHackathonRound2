import inspect
from datetime import datetime, timedelta
from pymongo.database import Database
from typing import List
from app.core.logger import logs
from app.repo.manufacture_repo import ManufacturingOrderRepository
from app.models.analytics_model import StatusOverview, AverageCycleTime, ThroughputDataPoint

class AnalyticsService:
    """
    Contains the business logic for calculating analytics and KPIs.
    """
    def __init__(self, db: Database):
        self.mo_repository = ManufacturingOrderRepository(db)

    async def get_status_overview(self) -> StatusOverview:
        """
        Calculates the count of Manufacturing Orders for each status.
        """
        try:
            logs.define_logger(20, "Calculating status overview.", loggName=inspect.stack()[0])
            pipeline = [
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }
                }
            ]
            results = await self.mo_repository.aggregate(pipeline)
            
            overview_data = {item['_id']: item['count'] for item in results}
            return StatusOverview(**overview_data)
        except Exception as e:
            logs.define_logger(50, f"Error in get_status_overview: {e}", loggName=inspect.stack()[0])
            raise

    async def get_production_throughput(self, days: int = 7) -> List[ThroughputDataPoint]:
        """
        Calculates the number of completed MOs per day for the last N days.
        """
        try:
            logs.define_logger(20, f"Calculating production throughput for last {days} days.", loggName=inspect.stack()[0])
            start_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "status": "done",
                        "completed_at": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {"format": "%Y-%m-%d", "date": "$completed_at"}
                        },
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}},
                {
                    "$project": {
                        "date": "$_id",
                        "count": 1,
                        "_id": 0
                    }
                }
            ]
            results = await self.mo_repository.aggregate(pipeline)
            return [ThroughputDataPoint(**item) for item in results]
        except Exception as e:
            logs.define_logger(50, f"Error in get_production_throughput: {e}", loggName=inspect.stack()[0])
            raise

    async def get_average_cycle_time(self) -> AverageCycleTime:
        """
        Calculates the average time from creation to completion for all 'done' orders.
        """
        try:
            logs.define_logger(20, "Calculating average cycle time.", loggName=inspect.stack()[0])
            pipeline = [
                {
                    "$match": {
                        "status": "done",
                        "completed_at": {"$ne": None} # Ensure completion date exists
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "avg_duration_ms": {
                            "$avg": {
                                "$subtract": ["$completed_at", "$created_at"]
                            }
                        },
                        "count": {"$sum": 1}
                    }
                }
            ]
            results = await self.mo_repository.aggregate(pipeline)

            if not results:
                return AverageCycleTime(average_hours=0, average_minutes=0, total_orders_calculated=0)
            
            avg_ms = results[0]['avg_duration_ms']
            avg_seconds = avg_ms / 1000
            avg_minutes = avg_seconds / 60
            avg_hours = avg_minutes / 60
            
            return AverageCycleTime(
                average_hours=round(avg_hours, 2),
                average_minutes=round(avg_minutes, 2),
                total_orders_calculated=results[0]['count']
            )
        except Exception as e:
            logs.define_logger(50, f"Error in get_average_cycle_time: {e}", loggName=inspect.stack()[0])
            raise
