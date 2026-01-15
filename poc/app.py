"""
語音摘要助手 - FastAPI Web 介面
POC 版本
"""

import os
import uuid
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from stt import transcribe
from summarizer import summarize, check_ollama_status

# 建立執行緒池處理 CPU 密集型任務
executor = ThreadPoolExecutor(max_workers=2)

app = FastAPI(title="語音摘要助手")

# 建立上傳目錄
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>語音摘要助手</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .content { padding: 30px; }
        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            transition: all 0.3s;
            cursor: pointer;
        }
        .upload-area:hover { border-color: #667eea; background: #f8f9ff; }
        .upload-area.dragover { border-color: #667eea; background: #f0f2ff; }
        .upload-icon { font-size: 48px; margin-bottom: 15px; }
        .file-input { display: none; }
        .file-name {
            margin-top: 15px;
            padding: 10px 15px;
            background: #e8f5e9;
            border-radius: 8px;
            color: #2e7d32;
            display: none;
        }
        .options {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .option-group { flex: 1; min-width: 200px; }
        .option-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        .option-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        .btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        .status.show { display: block; }
        .status.processing { background: #fff3e0; color: #e65100; }
        .status.success { background: #e8f5e9; color: #2e7d32; }
        .status.error { background: #ffebee; color: #c62828; }
        .result-section {
            margin-top: 25px;
            display: none;
        }
        .result-section.show { display: block; }
        .result-section h3 {
            margin-bottom: 15px;
            color: #333;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .result-box {
            background: #f5f5f5;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            white-space: pre-wrap;
            line-height: 1.8;
            max-height: 400px;
            overflow-y: auto;
        }
        .summary-box {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf6 100%);
        }
        .summary-box h4 { color: #667eea; margin: 15px 0 10px 0; }
        .summary-box ul { margin-left: 20px; }
        .summary-box li { margin: 8px 0; }
        .loader {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #fff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .progress-text { margin-top: 10px; font-size: 14px; }

        @media (max-width: 600px) {
            .header { padding: 20px; }
            .header h1 { font-size: 22px; }
            .content { padding: 20px; }
            .upload-area { padding: 25px; }
            .options { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>語音摘要助手</h1>
            <p>上傳中英文音檔，自動轉錄並生成結構化摘要</p>
        </div>

        <div class="content">
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" id="dropZone">
                    <div class="upload-icon">🎙️</div>
                    <p><strong>點擊上傳</strong> 或拖曳音檔到此處</p>
                    <p style="color: #888; margin-top: 10px; font-size: 14px;">支援 MP3, WAV, M4A, OGG, FLAC</p>
                    <input type="file" id="audioFile" name="file" accept="audio/*" class="file-input">
                    <div class="file-name" id="fileName"></div>
                </div>

                <div class="options">
                    <div class="option-group">
                        <label>摘要風格</label>
                        <select name="style" id="styleSelect">
                            <option value="meeting">會議摘要</option>
                            <option value="article">文章摘要</option>
                            <option value="brief">簡短摘要</option>
                        </select>
                    </div>
                </div>

                <button type="submit" class="btn" id="submitBtn">
                    開始處理
                </button>
            </form>

            <div class="status" id="status">
                <span class="loader"></span>
                <span id="statusText">處理中...</span>
                <div class="progress-text" id="progressText"></div>
            </div>

            <div class="result-section" id="transcriptSection">
                <h3>📝 轉錄結果</h3>
                <div class="result-box" id="transcriptResult"></div>
            </div>

            <div class="result-section" id="summarySection">
                <h3>📋 摘要</h3>
                <div class="result-box summary-box" id="summaryResult"></div>
            </div>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('audioFile');
        const fileName = document.getElementById('fileName');
        const form = document.getElementById('uploadForm');
        const submitBtn = document.getElementById('submitBtn');
        const status = document.getElementById('status');
        const statusText = document.getElementById('statusText');
        const progressText = document.getElementById('progressText');
        const transcriptSection = document.getElementById('transcriptSection');
        const summarySection = document.getElementById('summarySection');
        const transcriptResult = document.getElementById('transcriptResult');
        const summaryResult = document.getElementById('summaryResult');

        // 點擊上傳區域
        dropZone.addEventListener('click', () => fileInput.click());

        // 拖曳功能
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                showFileName(e.dataTransfer.files[0].name);
            }
        });

        // 檔案選擇
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                showFileName(fileInput.files[0].name);
            }
        });

        function showFileName(name) {
            fileName.textContent = '已選擇: ' + name;
            fileName.style.display = 'block';
        }

        // 表單提交
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!fileInput.files.length) {
                alert('請先選擇音檔');
                return;
            }

            // 重置顯示
            transcriptSection.classList.remove('show');
            summarySection.classList.remove('show');
            status.className = 'status show processing';
            statusText.textContent = '上傳中...';
            progressText.textContent = '';
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loader"></span>處理中...';

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('style', document.getElementById('styleSelect').value);

            try {
                // 更新狀態與計時器
                statusText.textContent = '正在進行語音轉文字...';
                progressText.textContent = '處理中，請耐心等待 (大檔案可能需要 3-5 分鐘)';

                // 顯示經過時間
                let seconds = 0;
                const timer = setInterval(() => {
                    seconds++;
                    const mins = Math.floor(seconds / 60);
                    const secs = seconds % 60;
                    progressText.textContent = `處理中... 已經過 ${mins}:${secs.toString().padStart(2, '0')}`;
                }, 1000);

                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });

                clearInterval(timer);

                const result = await response.json();

                if (result.success) {
                    status.className = 'status show success';
                    statusText.textContent = '處理完成！';
                    progressText.textContent = `語言: ${result.language || '自動偵測'}`;

                    transcriptResult.textContent = result.transcript;
                    transcriptSection.classList.add('show');

                    summaryResult.innerHTML = formatSummary(result.summary);
                    summarySection.classList.add('show');
                } else {
                    throw new Error(result.error || '處理失敗');
                }
            } catch (error) {
                if (typeof timer !== 'undefined') clearInterval(timer);
                status.className = 'status show error';
                statusText.textContent = '處理失敗';
                progressText.textContent = error.message;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '開始處理';
            }
        });

        function formatSummary(text) {
            // 簡單的 Markdown 轉 HTML
            return text
                .replace(/^## (.+)$/gm, '<h4>$1</h4>')
                .replace(/^- (.+)$/gm, '<li>$1</li>')
                .replace(/(<li>.*<\\/li>\\n?)+/g, '<ul>$&</ul>')
                .replace(/\\n/g, '<br>');
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    """首頁"""
    return HTML_TEMPLATE


@app.get("/health")
async def health_check():
    """健康檢查"""
    ollama_status = check_ollama_status()
    return {
        "status": "ok",
        "ollama": ollama_status
    }


@app.post("/process")
async def process_audio(
    file: UploadFile = File(...),
    style: str = Form("meeting")
):
    """處理音檔：轉錄 + 摘要"""

    # 檢查 Ollama
    ollama_status = check_ollama_status()
    if not ollama_status["available"]:
        return JSONResponse({
            "success": False,
            "error": "Ollama 服務未啟動，請執行: ollama serve"
        })

    # 儲存上傳檔案
    file_id = str(uuid.uuid4())[:8]
    file_ext = Path(file.filename).suffix
    file_path = UPLOAD_DIR / f"{file_id}{file_ext}"

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 語音轉文字 (使用執行緒池避免阻塞)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, transcribe, str(file_path))
        transcript = result["text"]
        language = result.get("language", "unknown")

        if not transcript.strip():
            return JSONResponse({
                "success": False,
                "error": "轉錄結果為空，請確認音檔內容"
            })

        # 生成摘要 (使用執行緒池避免阻塞)
        summarize_fn = partial(summarize, transcript, style=style)
        summary = await loop.run_in_executor(executor, summarize_fn)

        return JSONResponse({
            "success": True,
            "transcript": transcript,
            "summary": summary,
            "language": language
        })

    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })
    finally:
        # 清理暫存檔案
        if file_path.exists():
            file_path.unlink()


if __name__ == "__main__":
    print("檢查 Ollama 服務狀態...")
    status = check_ollama_status()

    if not status["available"]:
        print("⚠️  警告: Ollama 服務未啟動")
        print("請在另一個終端機執行: ollama serve")
        print("-" * 40)
    else:
        print(f"✅ Ollama 服務正常，已安裝模型: {', '.join(status['models'])}")

    print("\n🚀 啟動 Web 介面...")
    print("📱 請在瀏覽器開啟: http://localhost:7860")
    print("-" * 40)

    uvicorn.run(app, host="0.0.0.0", port=7860)
