"""
語音轉文字服務
"""
from typing import Union, Optional
import mlx_whisper
from pathlib import Path

from app.config import settings


def transcribe_audio(audio_path: Union[str, Path], language: Optional[str] = None) -> dict:
    """
    將音檔轉換為文字

    Args:
        audio_path: 音檔路徑
        language: 語言代碼，None 表示自動偵測

    Returns:
        dict: 包含 text, language, segments
    """
    result = mlx_whisper.transcribe(
        str(audio_path),
        path_or_hf_repo=settings.WHISPER_MODEL,
        language=language,
        verbose=False
    )

    # 處理分段資訊
    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": seg.get("start", 0),
            "end": seg.get("end", 0),
            "text": seg.get("text", "").strip(),
        })

    return {
        "text": result.get("text", ""),
        "language": result.get("language", "unknown"),
        "segments": segments,
    }


def get_audio_duration(audio_path: Union[str, Path]) -> float:
    """
    取得音檔時長（秒）

    使用 ffprobe 取得音檔資訊
    """
    import subprocess
    import json

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                str(audio_path)
            ],
            capture_output=True,
            text=True
        )
        info = json.loads(result.stdout)
        return float(info.get("format", {}).get("duration", 0))
    except Exception:
        return 0.0
