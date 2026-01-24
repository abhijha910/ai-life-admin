"""Settings routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.settings import UserSettingsUpdate, UserSettingsResponse
import uuid

router = APIRouter()


@router.get("", response_model=UserSettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user settings"""
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create default settings
        settings = UserSettings(
            id=uuid.uuid4(),
            user_id=current_user.id,
            notification_preferences={},
            ai_preferences={}
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings


@router.put("", response_model=UserSettingsResponse)
async def update_settings(
    settings_data: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user settings"""
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = UserSettings(
            id=uuid.uuid4(),
            user_id=current_user.id
        )
        db.add(settings)
    
    # Update fields
    if settings_data.notification_preferences is not None:
        settings.notification_preferences = settings_data.notification_preferences
    if settings_data.ai_preferences is not None:
        settings.ai_preferences = settings_data.ai_preferences
    if settings_data.daily_plan_time is not None:
        settings.daily_plan_time = settings_data.daily_plan_time
    if settings_data.timezone is not None:
        settings.timezone = settings_data.timezone
    
    await db.commit()
    await db.refresh(settings)
    
    return settings
