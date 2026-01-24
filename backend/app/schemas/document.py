"""Document schemas"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Document upload response schema"""
    id: str
    file_name: str
    file_type: str
    file_size: Optional[int]
    uploaded_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Document response schema"""
    id: str
    file_name: str
    file_type: str
    file_size: Optional[int]
    mime_type: Optional[str]
    ocr_text: Optional[str]
    ai_summary: Optional[str]
    ai_classification: Optional[str]
    ai_extracted_data: Optional[Dict[str, Any]]
    uploaded_at: datetime
    processed_at: Optional[datetime]
    presigned_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Document list response schema"""
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int
