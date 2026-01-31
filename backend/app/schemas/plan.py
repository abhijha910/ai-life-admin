"""Daily plan schemas"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class PlanTask(BaseModel):
    """Plan task schema"""
    task_id: str
    title: str
    priority: int
    risk_level: int = 0
    consequences: Optional[str] = None
    estimated_duration: int
    original_duration: Optional[int] = None
    scheduled_time: Optional[datetime]
    source: str


class DailyPlanResponse(BaseModel):
    """Daily plan response schema"""
    date: date
    tasks: List[PlanTask]
    total_duration: int
    priority_breakdown: Dict[str, int]
    overload_info: Optional[Dict[str, Any]] = None
    ai_recommendations: Optional[str] = None
    generated_at: datetime
