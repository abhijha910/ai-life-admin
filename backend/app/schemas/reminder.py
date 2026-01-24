"""Reminder schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReminderCreate(BaseModel):
    """Reminder creation schema"""
    task_id: Optional[str] = None
    reminder_type: str
    title: str
    message: Optional[str] = None
    trigger_at: datetime


class ReminderUpdate(BaseModel):
    """Reminder update schema"""
    title: Optional[str] = None
    message: Optional[str] = None
    trigger_at: Optional[datetime] = None


class ReminderResponse(BaseModel):
    """Reminder response schema"""
    id: str
    task_id: Optional[str]
    reminder_type: str
    title: str
    message: Optional[str]
    trigger_at: datetime
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReminderListResponse(BaseModel):
    """Reminder list response schema"""
    reminders: List[ReminderResponse]
    total: int
