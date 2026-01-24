"""Task schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TaskCreate(BaseModel):
    """Task creation schema"""
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 0
    estimated_duration: Optional[int] = None


class TaskUpdate(BaseModel):
    """Task update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    estimated_duration: Optional[int] = None


class TaskResponse(BaseModel):
    """Task response schema"""
    id: str
    title: str
    description: Optional[str]
    source_type: Optional[str]
    priority: int
    due_date: Optional[datetime]
    estimated_duration: Optional[int]
    status: str
    ai_generated: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Task list response schema"""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
