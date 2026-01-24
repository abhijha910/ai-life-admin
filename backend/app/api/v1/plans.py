"""Daily plan routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.plan import DailyPlanResponse
from app.services.task_service import task_service
from app.ai_engine.plan_generator import plan_generator
from app.models.user_settings import UserSettings
from sqlalchemy import select

router = APIRouter()


@router.get("/today", response_model=DailyPlanResponse)
async def get_today_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get today's action plan"""
    return await get_plan_for_date(date.today(), current_user, db)


@router.get("/{target_date}", response_model=DailyPlanResponse)
async def get_plan_for_date(
    target_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get plan for a specific date"""
    # Get all tasks
    tasks, _ = await task_service.list_tasks(
        db,
        current_user,
        status="pending",
        due_date=None,
        page=1,
        page_size=1000
    )
    
    # Convert tasks to dict format
    task_dicts = []
    for task in tasks:
        task_dicts.append({
            "id": str(task.id),
            "title": task.title,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "estimated_duration": task.estimated_duration or 60,
            "source_type": task.source_type or "manual"
        })
    
    # Get user settings
    settings_result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    user_settings = settings_result.scalar_one_or_none()
    
    preferences = {}
    if user_settings:
        preferences = {
            "daily_plan_time": user_settings.daily_plan_time,
            "ai_preferences": user_settings.ai_preferences or {}
        }
    
    # Generate plan
    plan = await plan_generator.generate_plan(
        task_dicts,
        target_date,
        preferences
    )
    
    return plan


@router.post("/regenerate")
async def regenerate_plan(
    target_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Regenerate plan with AI"""
    target = target_date or date.today()
    
    # Get all tasks
    tasks, _ = await task_service.list_tasks(
        db,
        current_user,
        status="pending",
        due_date=None,
        page=1,
        page_size=1000
    )
    
    # Convert tasks to dict format
    task_dicts = []
    for task in tasks:
        task_dicts.append({
            "id": str(task.id),
            "title": task.title,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "estimated_duration": task.estimated_duration or 60,
            "source_type": task.source_type or "manual"
        })
    
    # Get user settings
    settings_result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    user_settings = settings_result.scalar_one_or_none()
    
    preferences = {}
    if user_settings:
        preferences = {
            "daily_plan_time": user_settings.daily_plan_time,
            "ai_preferences": user_settings.ai_preferences or {}
        }
    
    # Generate plan
    plan = await plan_generator.generate_plan(
        task_dicts,
        target,
        preferences
    )
    
    return plan
