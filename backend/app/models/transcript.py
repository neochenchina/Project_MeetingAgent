"""
轉錄記錄模型
"""
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Transcript(Base):
    """轉錄記錄資料表"""

    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # 基本資訊
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    audio_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # 轉錄內容
    transcript_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript_segments: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # 說話者資訊
    speakers: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # 摘要
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_style: Mapped[str] = mapped_column(String(50), default="meeting")

    # 狀態
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processing, completed, failed

    # 時間戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # 關聯
    user: Mapped["User"] = relationship("User", back_populates="transcripts")

    def __repr__(self):
        return f"<Transcript(id={self.id}, title={self.title})>"
