"""Notification service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from app.models.notification import Notification
from app.models.user import User
import structlog

logger = structlog.get_logger()


class NotificationService:
    """Notification service"""
    
    async def create_notification(
        self,
        db: AsyncSession,
        user: User,
        notification_type: str,
        title: str,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a notification"""
        notification = Notification(
            id=uuid.uuid4(),
            user_id=user.id,
            type=notification_type,
            title=title,
            message=message,
            data=data or {},
            is_read=False
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        return notification
    
    async def list_notifications(
        self,
        db: AsyncSession,
        user: User,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Notification], int, int]:
        """List user's notifications"""
        offset = (page - 1) * page_size
        
        query = select(Notification).where(Notification.user_id == user.id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        # Get total count
        count_query = select(Notification).where(Notification.user_id == user.id)
        if unread_only:
            count_query = count_query.where(Notification.is_read == False)
        
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Get unread count
        unread_result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user.id,
                    Notification.is_read == False
                )
            )
        )
        unread_count = len(unread_result.scalars().all())
        
        # Get paginated results
        query = query.order_by(Notification.created_at.desc())
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        return notifications, total, unread_count
    
    async def mark_read(
        self,
        db: AsyncSession,
        notification_id: str,
        user: User
    ) -> bool:
        """Mark notification as read"""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == uuid.UUID(notification_id),
                    Notification.user_id == user.id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.is_read = True
            await db.commit()
            return True
        
        return False
    
    async def delete_notification(
        self,
        db: AsyncSession,
        notification_id: str,
        user: User
    ) -> bool:
        """Delete notification"""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == uuid.UUID(notification_id),
                    Notification.user_id == user.id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            await db.delete(notification)
            await db.commit()
            return True
        
        return False


# Global notification service instance
notification_service = NotificationService()
