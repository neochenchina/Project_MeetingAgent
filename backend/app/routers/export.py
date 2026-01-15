"""
匯出 API 路由
"""
from typing import Annotated
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.transcript import Transcript
from app.utils.auth import get_current_user
from app.services.export import export_to_pdf, export_to_docx, export_to_markdown


router = APIRouter(prefix="/api/export", tags=["匯出"])


async def get_transcript_or_404(
    transcript_id: int,
    current_user: User,
    db: AsyncSession,
) -> Transcript:
    """取得轉錄記錄或回傳 404"""
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
            detail="沒有內容可匯出",
        )

    return transcript


@router.get("/{transcript_id}/pdf")
async def export_pdf(
    transcript_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """匯出為 PDF"""
    transcript = await get_transcript_or_404(transcript_id, current_user, db)

    # 產生 PDF
    pdf_buffer = export_to_pdf(transcript)

    filename = f"{transcript.title or 'transcript'}.pdf"
    return StreamingResponse(
        BytesIO(pdf_buffer),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{transcript_id}/docx")
async def export_docx(
    transcript_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """匯出為 Word"""
    transcript = await get_transcript_or_404(transcript_id, current_user, db)

    # 產生 DOCX
    docx_buffer = export_to_docx(transcript)

    filename = f"{transcript.title or 'transcript'}.docx"
    return StreamingResponse(
        BytesIO(docx_buffer),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{transcript_id}/md")
async def export_md(
    transcript_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """匯出為 Markdown"""
    transcript = await get_transcript_or_404(transcript_id, current_user, db)

    # 產生 Markdown
    md_content = export_to_markdown(transcript)

    filename = f"{transcript.title or 'transcript'}.md"
    return StreamingResponse(
        BytesIO(md_content.encode("utf-8")),
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
