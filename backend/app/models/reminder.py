"""Reminder model"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Reminder(Base):
    """Reminder model"""
    __tablename__ = "reminders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    reminder_type = Column(String(50), nullable=False)  # 'task_due', 'calendar', 'habit'
    title = Column(String(255), nullable=False)
    message = Column(Text)
    trigger_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_sent = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    task = relationship("Task", back_populates="reminders")
