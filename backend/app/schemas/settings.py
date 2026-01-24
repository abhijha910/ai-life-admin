"""Settings schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import time, datetime


class UserSettingsUpdate(BaseModel):
    """User settings update schema"""
    notification_preferences: Optional[Dict[str, Any]] = None
    ai_preferences: Optional[Dict[str, Any]] = None
    daily_plan_time: Optional[time] = None
    timezone: Optional[str] = None


class UserSettingsResponse(BaseModel):
    """User settings response schema"""
    notification_preferences: Dict[str, Any]
    ai_preferences: Dict[str, Any]
    daily_plan_time: time
    timezone: str
    updated_at: datetime
    
    class Config:
        from_attributes = True
