"""
語音轉文字模組 (Speech-to-Text)
使用 mlx-whisper 進行 Apple Silicon 優化的語音識別
"""

import mlx_whisper


def transcribe(audio_path: str, language: str = None) -> dict:
    """
    將音檔轉換為文字

    Args:
        audio_path: 音檔路徑 (支援 mp3, wav, m4a 等格式)
        language: 語言代碼，None 表示自動偵測

    Returns:
        dict: 包含 text (完整文字) 和 segments (分段資訊)
    """
    # 使用 MLX 優化的 Whisper large-v3 模型
    result = mlx_whisper.transcribe(
        audio_path,
        path_or_hf_repo="mlx-community/whisper-large-v3-mlx",
        language=language,  # None = 自動偵測語言
        verbose=False
    )

    return {
        "text": result["text"],
        "language": result.get("language", "unknown"),
        "segments": result.get("segments", [])
    }


def transcribe_with_timestamps(audio_path: str) -> str:
    """
    帶時間戳的轉錄，適合長音檔

    Returns:
        str: 帶時間戳的文字
    """
    result = mlx_whisper.transcribe(
        audio_path,
        path_or_hf_repo="mlx-community/whisper-large-v3-mlx",
        verbose=False
    )

    lines = []
    for segment in result.get("segments", []):
        start = segment.get("start", 0)
        end = segment.get("end", 0)
        text = segment.get("text", "").strip()

        # 格式化時間戳
        start_str = f"{int(start // 60):02d}:{int(start % 60):02d}"
        end_str = f"{int(end // 60):02d}:{int(end % 60):02d}"

        lines.append(f"[{start_str} - {end_str}] {text}")

    return "\n".join(lines)


if __name__ == "__main__":
    # 測試用
    import sys
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        print(f"正在轉錄: {audio_file}")
        result = transcribe(audio_file)
        print(f"偵測語言: {result['language']}")
        print(f"轉錄結果:\n{result['text']}")
