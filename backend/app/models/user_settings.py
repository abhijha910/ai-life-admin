"""User settings model"""
from sqlalchemy import Column, String, Time, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class UserSettings(Base):
    """User settings model"""
    __tablename__ = "user_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    notification_preferences = Column(JSONB, default={})
    ai_preferences = Column(JSONB, default={})
    daily_plan_time = Column(Time, default="08:00:00")
    timezone = Column(String(50), default="UTC")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="settings")
