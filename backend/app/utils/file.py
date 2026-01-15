"""
檔案處理工具
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile

from app.config import settings


ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".aac"}


def is_valid_audio_file(filename: str) -> bool:
    """檢查是否為有效的音檔"""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_AUDIO_EXTENSIONS


async def save_upload_file(file: UploadFile, user_id: int) -> tuple[Path, str]:
    """
    儲存上傳的檔案

    Args:
        file: 上傳的檔案
        user_id: 使用者 ID

    Returns:
        tuple: (儲存路徑, 唯一檔名)
    """
    # 建立使用者專屬目錄
    user_dir = settings.UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    # 產生唯一檔名
    ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = user_dir / unique_filename

    # 儲存檔案
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return file_path, unique_filename


def delete_file(file_path: Path) -> bool:
    """刪除檔案"""
    try:
        if file_path.exists():
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False


def get_file_size(file_path: Path) -> int:
    """取得檔案大小（bytes）"""
    return file_path.stat().st_size if file_path.exists() else 0
