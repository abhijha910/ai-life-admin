"""Email models"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class EmailAccount(Base):
    """Email account model for connected email providers"""
    __tablename__ = "email_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)  # 'gmail', 'outlook', 'imap'
    email_address = Column(String(255), nullable=False)
    access_token_encrypted = Column(Text)
    refresh_token_encrypted = Column(Text)
    provider_account_id = Column(String(255))
    last_sync_at = Column(DateTime(timezone=True))
    sync_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="email_accounts")
    email_items = relationship("EmailItem", back_populates="email_account", cascade="all, delete-orphan")


class EmailItem(Base):
    """Email item model"""
    __tablename__ = "email_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_account_id = Column(UUID(as_uuid=True), ForeignKey("email_accounts.id", ondelete="CASCADE"), nullable=False)
    provider_message_id = Column(String(255), unique=True, nullable=False, index=True)
    subject = Column(Text)
    sender_email = Column(String(255))
    sender_name = Column(String(255))
    body_text = Column(Text)
    body_html = Column(Text)
    received_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_read = Column(Boolean, default=False)
    is_important = Column(Boolean, default=False)
    ai_summary = Column(Text)
    ai_extracted_tasks = Column(JSONB)
    ai_extracted_dates = Column(JSONB)
    ai_priority_score = Column(Integer, default=0, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    email_account = relationship("EmailAccount", back_populates="email_items")
