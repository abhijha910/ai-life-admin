"""Task model"""
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    source_type = Column(String(50))  # 'email', 'document', 'manual'
    source_id = Column(UUID(as_uuid=True))  # reference to email_items or documents
    priority = Column(Integer, default=0)  # 0-100
    due_date = Column(DateTime(timezone=True), index=True)
    estimated_duration = Column(Integer)  # minutes
    status = Column(String(50), default="pending", index=True)  # 'pending', 'in_progress', 'completed', 'cancelled'
    ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")
