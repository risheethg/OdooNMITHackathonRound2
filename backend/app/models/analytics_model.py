from pydantic import BaseModel
from typing import List, Optional

class StatusOverview(BaseModel):
    planned: int = 0
    in_progress: int = 0
    done: int = 0
    canceled: int = 0

class ThroughputDataPoint(BaseModel):
    date: str
    count: int

class ProductionThroughput(BaseModel):
    period: str
    data: List[ThroughputDataPoint]

class AverageCycleTime(BaseModel):
    average_hours: float
    average_minutes: float
    total_orders_calculated: int
