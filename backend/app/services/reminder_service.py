"""Reminder service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
import uuid
from app.models.reminder import Reminder
from app.models.user import User
from app.schemas.reminder import ReminderCreate, ReminderUpdate
import structlog

logger = structlog.get_logger()


class ReminderService:
    """Reminder service"""
    
    async def create_reminder(
        self,
        db: AsyncSession,
        user: User,
        reminder_data: ReminderCreate
    ) -> Reminder:
        """Create a reminder"""
        reminder = Reminder(
            id=uuid.uuid4(),
            user_id=user.id,
            task_id=uuid.UUID(reminder_data.task_id) if reminder_data.task_id else None,
            reminder_type=reminder_data.reminder_type,
            title=reminder_data.title,
            message=reminder_data.message,
            trigger_at=reminder_data.trigger_at,
            is_sent=False
        )
        
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)
        
        return reminder
    
    async def get_upcoming_reminders(
        self,
        db: AsyncSession,
        user: User,
        limit: int = 50
    ) -> List[Reminder]:
        """Get upcoming reminders"""
        now = datetime.now()
        
        result = await db.execute(
            select(Reminder)
            .where(
                and_(
                    Reminder.user_id == user.id,
                    Reminder.trigger_at >= now,
                    Reminder.is_sent == False
                )
            )
            .order_by(Reminder.trigger_at.asc())
            .limit(limit)
        )
        
        return result.scalars().all()
    
    async def mark_sent(
        self,
        db: AsyncSession,
        reminder_id: str
    ) -> bool:
        """Mark reminder as sent"""
        result = await db.execute(
            select(Reminder).where(Reminder.id == uuid.UUID(reminder_id))
        )
        reminder = result.scalar_one_or_none()
        
        if reminder:
            reminder.is_sent = True
            reminder.sent_at = datetime.now()
            await db.commit()
            return True
        
        return False


# Global reminder service instance
reminder_service = ReminderService()
