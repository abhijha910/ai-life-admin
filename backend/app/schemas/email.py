"""Email schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime


class EmailAccountCreate(BaseModel):
    """Email account connection schema"""
    provider: str  # 'gmail', 'outlook', 'imap'
    email_address: EmailStr
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class EmailAccountResponse(BaseModel):
    """Email account response schema"""
    id: str
    provider: str
    email_address: str
    last_sync_at: Optional[datetime]
    sync_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailItemResponse(BaseModel):
    """Email item response schema"""
    id: str
    subject: Optional[str]
    sender_email: Optional[str]
    sender_name: Optional[str]
    body_text: Optional[str]
    received_at: datetime
    is_read: bool
    is_important: bool
    ai_summary: Optional[str]
    ai_extracted_tasks: Optional[Dict[str, Any]]
    ai_extracted_dates: Optional[Dict[str, Any]]
    ai_priority_score: Optional[int] = None
    created_at: datetime
    
    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to response, handling UUID conversion"""
        data = {
            "id": str(obj.id),
            "subject": obj.subject,
            "sender_email": obj.sender_email,
            "sender_name": obj.sender_name,
            "body_text": obj.body_text,
            "received_at": obj.received_at,
            "is_read": obj.is_read,
            "is_important": obj.is_important,
            "ai_summary": obj.ai_summary,
            "ai_extracted_tasks": obj.ai_extracted_tasks,
            "ai_extracted_dates": obj.ai_extracted_dates,
            "ai_priority_score": obj.ai_priority_score,
            "created_at": obj.created_at,
        }
        return cls(**data)
    
    class Config:
        from_attributes = True


class EmailListResponse(BaseModel):
    """Email list response schema"""
    emails: List[EmailItemResponse]
    total: int
    page: int
    page_size: int


class EmailSyncRequest(BaseModel):
    """Email sync request schema"""
    account_id: Optional[str] = None  # If None, sync all accounts
