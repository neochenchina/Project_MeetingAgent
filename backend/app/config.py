"""
應用程式設定
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """應用設定"""

    # 應用資訊
    APP_NAME: str = "語音摘要助手"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 資料庫
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/database.db"

    # JWT 設定
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # 檔案上傳
    UPLOAD_DIR: Path = Path("data/uploads")
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB

    # Ollama 設定
    OLLAMA_API_URL: str = "http://localhost:11434"
    DEFAULT_LLM_MODEL: str = "qwen2.5:14b"

    # Whisper 設定
    WHISPER_MODEL: str = "mlx-community/whisper-large-v3-mlx"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()

# 確保上傳目錄存在
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
