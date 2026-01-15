"""
使用者相關 Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """註冊請求"""
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """登入請求"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """使用者回應"""
    id: int
    email: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token 回應"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 內容"""
    user_id: Optional[int] = None
