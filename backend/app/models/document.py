"""Document model"""
from sqlalchemy import Column, String, BigInteger, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(BigInteger)
    s3_key = Column(String(500), nullable=False)
    mime_type = Column(String(100))
    ocr_text = Column(Text)
    ai_summary = Column(Text)
    ai_classification = Column(String(100))  # 'invoice', 'receipt', 'contract', etc.
    ai_extracted_data = Column(JSONB)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="documents")
