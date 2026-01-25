"""Task routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import date
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services.task_service import task_service

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task"""
    task = await task_service.create_task(db, current_user, task_data)
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        source_type=task.source_type,
        priority=task.priority,
        due_date=task.due_date,
        estimated_duration=task.estimated_duration,
        status=task.status,
        ai_generated=task.ai_generated,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query(None),
    due_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's tasks"""
    tasks, total = await task_service.list_tasks(
        db,
        current_user,
        status,
        due_date,
        page,
        page_size
    )
    
    # Convert tasks to response format - explicitly convert UUIDs to strings
    task_responses = [
        TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            source_type=task.source_type,
            priority=task.priority,
            due_date=task.due_date,
            estimated_duration=task.estimated_duration,
            status=task.status,
            ai_generated=task.ai_generated,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
        for task in tasks
    ]
    
    return TaskListResponse(
        tasks=task_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get task details"""
    task = await task_service.get_task(db, task_id, current_user)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        source_type=task.source_type,
        priority=task.priority,
        due_date=task.due_date,
        estimated_duration=task.estimated_duration,
        status=task.status,
        ai_generated=task.ai_generated,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update task"""
    task = await task_service.update_task(db, task_id, current_user, task_data)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        source_type=task.source_type,
        priority=task.priority,
        due_date=task.due_date,
        estimated_duration=task.estimated_duration,
        status=task.status,
        ai_generated=task.ai_generated,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete task"""
    success = await task_service.delete_task(db, task_id, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark task as completed"""
    task = await task_service.complete_task(db, task_id, current_user)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        source_type=task.source_type,
        priority=task.priority,
        due_date=task.due_date,
        estimated_duration=task.estimated_duration,
        status=task.status,
        ai_generated=task.ai_generated,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.get("/predict", response_model=TaskListResponse)
async def predict_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-predicted tasks for today"""
    from datetime import date
    tasks, total = await task_service.list_tasks(
        db,
        current_user,
        status="pending",
        due_date=date.today(),
        page=1,
        page_size=50
    )
    
    # Convert tasks to response format - explicitly convert UUIDs to strings
    task_responses = [
        TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            source_type=task.source_type,
            priority=task.priority,
            due_date=task.due_date,
            estimated_duration=task.estimated_duration,
            status=task.status,
            ai_generated=task.ai_generated,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
        for task in tasks
    ]
    
    return TaskListResponse(
        tasks=task_responses,
        total=total,
        page=1,
        page_size=50
    )
