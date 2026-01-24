"""Authentication schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    full_name: Optional[str]
    timezone: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
