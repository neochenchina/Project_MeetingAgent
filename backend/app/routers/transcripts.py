"""
轉錄記錄 API 路由
"""
from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.transcript import Transcript
from app.schemas.transcript import (
    TranscriptResponse,
    TranscriptListResponse,
    TranscriptUpdate,
)
from app.utils.auth import get_current_user
from app.utils.file import is_valid_audio_file, save_upload_file, delete_file
from app.services.stt import transcribe_audio, get_audio_duration
from app.services.summarizer import generate_summary
from app.config import settings


router = APIRouter(prefix="/api/transcripts", tags=["轉錄"])


async def process_transcript(transcript_id: int, file_path: Path, db_url: str):
    """背景處理轉錄任務"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    # 使用同步連線處理背景任務
    sync_engine = create_engine(db_url.replace("+aiosqlite", ""))

    with Session(sync_engine) as db:
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        if not transcript:
            return

        try:
            # 更新狀態為處理中
            transcript.status = "processing"
            db.commit()

            # 取得音檔時長
            transcript.audio_duration = get_audio_duration(file_path)

            # 語音轉文字
            result = transcribe_audio(file_path)
            transcript.transcript_text = result["text"]
            transcript.transcript_segments = result["segments"]
            transcript.language = result["language"]

            # 生成摘要
            if result["text"].strip():
                transcript.summary = generate_summary(result["text"], transcript.summary_style)

            # 更新狀態為完成
            transcript.status = "completed"
            db.commit()

        except Exception as e:
            transcript.status = "failed"
            transcript.summary = f"處理失敗: {str(e)}"
            db.commit()

        finally:
            # 刪除暫存檔案
            delete_file(file_path)


@router.post("", response_model=TranscriptResponse, status_code=status.HTTP_201_CREATED)
async def create_transcript(
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
    title: str = Form(None),
    summary_style: str = Form("meeting"),
):
    """上傳音檔並建立轉錄任務"""
    # 驗證檔案類型
    if not is_valid_audio_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支援的音檔格式",
        )

    # 儲存檔案
    file_path, unique_filename = await save_upload_file(file, current_user.id)

    # 建立轉錄記錄
    transcript = Transcript(
        user_id=current_user.id,
        title=title or file.filename,
        original_filename=file.filename,
        summary_style=summary_style,
        status="pending",
    )
    db.add(transcript)
    await db.commit()
    await db.refresh(transcript)

    # 啟動背景處理
    background_tasks.add_task(
        process_transcript,
        transcript.id,
        file_path,
        settings.DATABASE_URL.replace("+aiosqlite", ""),
    )

    return transcript


@router.get("", response_model=list[TranscriptListResponse])
async def list_transcripts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 20,
):
    """取得使用者的轉錄記錄列表"""
    result = await db.execute(
        select(Transcript)
        .where(Transcript.user_id == current_user.id)
        .order_by(Transcript.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{transcript_id}", response_model=TranscriptResponse)
async def get_transcript(
    transcript_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """取得單筆轉錄記錄"""
    result = await db.execute(
        select(Transcript).where(
            Transcript.id == transcript_id,
            Transcript.user_id == current_user.id,
        )
    )
    transcript = result.scalar_one_or_none()

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到此記錄",
        )

    return transcript


@router.patch("/{transcript_id}", response_model=TranscriptResponse)
async def update_transcript(
    transcript_id: int,
    update_data: TranscriptUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """更新轉錄記錄"""
    result = await db.execute(
        select(Transcript).where(
            Transcript.id == transcript_id,
            Transcript.user_id == current_user.id,
        )
    )
    transcript = result.scalar_one_or_none()

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到此記錄",
        )

    # 更新欄位
    if update_data.title is not None:
        transcript.title = update_data.title
    if update_data.summary_style is not None:
        transcript.summary_style = update_data.summary_style

    await db.commit()
    await db.refresh(transcript)

    return transcript


@router.delete("/{transcript_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transcript(
    transcript_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """刪除轉錄記錄"""
    result = await db.execute(
        select(Transcript).where(
            Transcript.id == transcript_id,
            Transcript.user_id == current_user.id,
        )
    )
    transcript = result.scalar_one_or_none()

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到此記錄",
        )

    await db.delete(transcript)
    await db.commit()


@router.post("/{transcript_id}/regenerate", response_model=TranscriptResponse)
async def regenerate_summary(
    transcript_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    summary_style: str = Form("meeting"),
):
    """重新生成摘要"""
    result = await db.execute(
        select(Transcript).where(
            Transcript.id == transcript_id,
            Transcript.user_id == current_user.id,
        )
    )
    transcript = result.scalar_one_or_none()

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到此記錄",
        )

    if not transcript.transcript_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="沒有轉錄內容可供摘要",
        )

    # 重新生成摘要
    transcript.summary_style = summary_style
    transcript.summary = generate_summary(transcript.transcript_text, summary_style)

    await db.commit()
    await db.refresh(transcript)

    return transcript
