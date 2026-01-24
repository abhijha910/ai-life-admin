"""Processing log model"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class ProcessingLog(Base):
    """Processing log model"""
    __tablename__ = "processing_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String(50))  # 'email', 'document'
    entity_id = Column(UUID(as_uuid=True))
    processing_type = Column(String(50))  # 'ocr', 'nlp', 'classification'
    status = Column(String(50))  # 'pending', 'processing', 'completed', 'failed'
    error_message = Column(Text)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="processing_logs")
