"""Reminder routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.reminder import ReminderCreate, ReminderUpdate, ReminderResponse, ReminderListResponse
from app.services.reminder_service import reminder_service

router = APIRouter()


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a reminder"""
    reminder = await reminder_service.create_reminder(db, current_user, reminder_data)
    return reminder


@router.get("", response_model=ReminderListResponse)
async def list_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List upcoming reminders"""
    reminders = await reminder_service.get_upcoming_reminders(db, current_user)
    
    return ReminderListResponse(
        reminders=reminders,
        total=len(reminders)
    )


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    reminder_data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update reminder"""
    # Implementation would update reminder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented"
    )


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete reminder"""
    # Implementation would delete reminder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented"
    )
