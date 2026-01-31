"""Task model"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, ForeignKey, func
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
    consequences = Column(Text)  # Level 2: What happens if missed
    source_type = Column(String(50))  # 'email', 'document', 'manual'
    source_id = Column(UUID(as_uuid=True))  # reference to email_items or documents
    priority = Column(Integer, default=0)  # 0-100
    risk_level = Column(Integer, default=0)  # Level 3: 0-100 predicted risk
    confidence_score = Column(Float, default=1.0)  # Level 2: AI certainty 0-1
    due_date = Column(DateTime(timezone=True), index=True)
    estimated_duration = Column(Integer)  # minutes
    status = Column(String(50), default="pending", index=True)  # 'pending', 'in_progress', 'completed', 'cancelled'
    ai_generated = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)  # Level 7: Approval layer
    dependency_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")
    blocked_by = relationship("Task", remote_side=[id], backref="blocking")
