"""
語音摘要助手 - FastAPI 主應用
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import auth_router, transcripts_router, export_router
from app.services.summarizer import check_ollama_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時
    print(f"啟動 {settings.APP_NAME} v{settings.APP_VERSION}")

    # 初始化資料庫
    await init_db()
    print("資料庫初始化完成")

    # 檢查 Ollama
    ollama_status = check_ollama_status()
    if ollama_status["available"]:
        print(f"Ollama 服務正常，模型: {', '.join(ollama_status['models'])}")
    else:
        print("警告: Ollama 服務未啟動")

    yield

    # 關閉時
    print("應用關閉")


# 建立 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(auth_router)
app.include_router(transcripts_router)
app.include_router(export_router)


@app.get("/")
async def root():
    """首頁"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    ollama_status = check_ollama_status()
    return {
        "status": "ok",
        "ollama": ollama_status,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
