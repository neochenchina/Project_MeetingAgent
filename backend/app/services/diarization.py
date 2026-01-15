"""
說話者辨識服務

注意：pyannote-audio 需要 Hugging Face API Token
首次使用需要到 https://huggingface.co/pyannote/speaker-diarization-3.1 同意使用條款
"""
from pathlib import Path
from typing import Optional, Union, List, Dict

# 說話者辨識功能標記（需要額外設定才能啟用）
DIARIZATION_AVAILABLE = False


def check_diarization_available() -> bool:
    """檢查說話者辨識是否可用"""
    try:
        from pyannote.audio import Pipeline
        return True
    except ImportError:
        return False


def diarize_audio(
    audio_path: Union[str, Path],
    hf_token: Optional[str] = None,
    num_speakers: Optional[int] = None,
) -> List[Dict]:
    """
    進行說話者辨識

    Args:
        audio_path: 音檔路徑
        hf_token: Hugging Face API Token
        num_speakers: 說話者數量（可選）

    Returns:
        list: 說話者分段列表 [{"start": 0.0, "end": 1.5, "speaker": "SPEAKER_00"}, ...]
    """
    if not check_diarization_available():
        return []

    try:
        from pyannote.audio import Pipeline
        import torch

        # 載入模型
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token
        )

        # 使用 MPS（Apple Silicon）或 CPU
        device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        pipeline.to(device)

        # 執行辨識
        if num_speakers:
            diarization = pipeline(str(audio_path), num_speakers=num_speakers)
        else:
            diarization = pipeline(str(audio_path))

        # 轉換格式
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })

        return segments

    except Exception as e:
        print(f"說話者辨識失敗: {e}")
        return []


def merge_transcript_with_speakers(
    transcript_segments: List[Dict],
    speaker_segments: List[Dict],
) -> List[Dict]:
    """
    合併轉錄分段與說話者資訊

    Args:
        transcript_segments: 轉錄分段
        speaker_segments: 說話者分段

    Returns:
        list: 合併後的分段
    """
    if not speaker_segments:
        return transcript_segments

    merged = []
    for seg in transcript_segments:
        seg_start = seg.get("start", 0)
        seg_end = seg.get("end", 0)
        seg_mid = (seg_start + seg_end) / 2

        # 找出對應的說話者
        speaker = None
        for sp in speaker_segments:
            if sp["start"] <= seg_mid <= sp["end"]:
                speaker = sp["speaker"]
                break

        merged.append({
            **seg,
            "speaker": speaker or "UNKNOWN"
        })

    return merged
