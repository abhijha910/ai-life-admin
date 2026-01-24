"""Notification schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class NotificationResponse(BaseModel):
    """Notification response schema"""
    id: str
    type: str
    title: str
    message: Optional[str]
    data: Optional[Dict[str, Any]]
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Notification list response schema"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
