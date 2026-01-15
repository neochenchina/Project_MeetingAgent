"""
轉錄記錄相關 Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel


class TranscriptCreate(BaseModel):
    """建立轉錄請求"""
    title: Optional[str] = None
    summary_style: str = "meeting"


class TranscriptUpdate(BaseModel):
    """更新轉錄請求"""
    title: Optional[str] = None
    summary_style: Optional[str] = None


class TranscriptSegment(BaseModel):
    """轉錄分段"""
    start: float
    end: float
    text: str
    speaker: Optional[str] = None


class TranscriptResponse(BaseModel):
    """轉錄記錄回應"""
    id: int
    title: Optional[str]
    original_filename: str
    audio_duration: Optional[float]
    language: Optional[str]
    transcript_text: Optional[str]
    transcript_segments: Optional[List[Dict]]
    speakers: Optional[List[Dict]]
    summary: Optional[str]
    summary_style: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TranscriptListResponse(BaseModel):
    """轉錄記錄列表回應"""
    id: int
    title: Optional[str]
    original_filename: str
    audio_duration: Optional[float]
    language: Optional[str]
    status: str
    summary_style: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessingStatus(BaseModel):
    """處理狀態"""
    status: str
    progress: int = 0
    message: str = ""
