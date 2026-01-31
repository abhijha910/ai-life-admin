"""Task schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TaskCreate(BaseModel):
    """Task creation schema"""
    title: str
    description: Optional[str] = None
    consequences: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 0
    estimated_duration: Optional[int] = None
    dependency_id: Optional[str] = None
    goal_id: Optional[str] = None
    is_approved: bool = True
    ai_generated: bool = False


class TaskUpdate(BaseModel):
    """Task update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    consequences: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = None
    risk_level: Optional[int] = None
    status: Optional[str] = None
    estimated_duration: Optional[int] = None
    dependency_id: Optional[str] = None
    goal_id: Optional[str] = None
    is_approved: Optional[bool] = None


class TaskResponse(BaseModel):
    """Task response schema"""
    id: str
    title: str
    description: Optional[str]
    consequences: Optional[str]
    source_type: Optional[str]
    priority: int
    risk_level: int
    confidence_score: float
    due_date: Optional[datetime]
    estimated_duration: Optional[int]
    status: str
    ai_generated: bool
    is_approved: bool
    dependency_id: Optional[str] = None
    goal_id: Optional[str] = None
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
