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
    ai_priority_score: int
    created_at: datetime
    
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
