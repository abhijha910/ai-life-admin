"""Life Graph and Action Suggestion models"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class Goal(Base):
    """Long-term life goals"""
    __tablename__ = "goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    category = Column(String(100))  # 'career', 'health', 'finance', 'personal'
    target_date = Column(DateTime(timezone=True))
    status = Column(String(50), default="active")
    
    tasks = relationship("Task", backref="goal")

class Institution(Base):
    """External institutions (Banks, Employers, etc.)"""
    __tablename__ = "institutions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(500), nullable=False)
    type = Column(String(100))  # 'bank', 'employer', 'government', 'insurance'
    contact_info = Column(Text)

class Relationship(Base):
    """Important people in the user's life"""
    __tablename__ = "relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(500), nullable=False)
    role = Column(String(100))  # 'family', 'vip', 'manager', 'colleague'
    importance_level = Column(Integer, default=50)

class ActionSuggestion(Base):
    """AI-generated action suggestions (Action Cards)"""
    __tablename__ = "action_suggestions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100))  # 'follow_up', 'stalled_task', 'risk_mitigation'
    source_id = Column(UUID(as_uuid=True))
    title = Column(String(500), nullable=False)
    description = Column(Text)
    draft_content = Column(Text)
    action_label = Column(String(100))
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
