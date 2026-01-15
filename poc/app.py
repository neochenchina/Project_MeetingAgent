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
    <title>世德會議助理</title>
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
        .progress-container {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            margin-top: 15px;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 4px;
            width: 0%;
            transition: width 0.3s ease;
        }
        .timestamp {
            color: #667eea;
            font-weight: 600;
            font-family: monospace;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .result-header h3 {
            margin: 0;
            padding: 0;
            border: none;
        }
        .action-buttons {
            display: flex;
            gap: 8px;
        }
        .action-btn {
            padding: 8px 12px;
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s;
        }
        .action-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .action-btn.success {
            background: #4caf50;
            color: white;
            border-color: #4caf50;
        }
        .btn-icon {
            font-size: 14px;
        }
        .toast {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .toast.show {
            opacity: 1;
        }

        @media (max-width: 600px) {
            .header { padding: 20px; }
            .header h1 { font-size: 22px; }
            .content { padding: 20px; }
            .upload-area { padding: 25px; }
            .options { flex-direction: column; }
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
</head>
<body>
    <div id="toast" class="toast"></div>
    <div class="container">
        <div class="header">
            <h1>世德會議助理</h1>
            <p>上傳會議音檔，自動轉錄並生成結構化摘要</p>
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
                <div class="progress-container" id="progressContainer" style="display: none;">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
            </div>

            <div class="result-section" id="transcriptSection">
                <div class="result-header">
                    <h3>📝 轉錄結果</h3>
                    <div class="action-buttons">
                        <button class="action-btn" onclick="copyToClipboard('transcript')" title="複製到剪貼簿">
                            <span class="btn-icon">📋</span> 複製
                        </button>
                        <button class="action-btn" onclick="downloadPDF('transcript')" title="下載 PDF">
                            <span class="btn-icon">📄</span> 下載 PDF
                        </button>
                    </div>
                </div>
                <div class="result-box" id="transcriptResult"></div>
            </div>

            <div class="result-section" id="summarySection">
                <div class="result-header">
                    <h3>📋 摘要</h3>
                    <div class="action-buttons">
                        <button class="action-btn" onclick="copyToClipboard('summary')" title="複製到剪貼簿">
                            <span class="btn-icon">📋</span> 複製
                        </button>
                        <button class="action-btn" onclick="downloadPDF('summary')" title="下載 PDF">
                            <span class="btn-icon">📄</span> 下載 PDF
                        </button>
                    </div>
                </div>
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
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');

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

        // 獲取音檔長度（秒）
        async function getAudioDuration(file) {
            return new Promise((resolve) => {
                const audio = new Audio();
                audio.addEventListener('loadedmetadata', () => {
                    resolve(audio.duration);
                });
                audio.addEventListener('error', () => {
                    // 無法讀取時預設 60 秒
                    resolve(60);
                });
                audio.src = URL.createObjectURL(file);
            });
        }

        // 預估處理時間（秒）
        // 參考數據：5分鐘音檔約45秒，30分鐘約150秒，60分鐘約270秒
        // 公式：處理時間 ≈ 音檔長度(秒) × 0.075 + 20秒（摘要時間）
        function estimateProcessingTime(audioDurationSecs) {
            const transcribeTime = audioDurationSecs * 0.075;
            const summarizeTime = 20;
            return Math.max(30, transcribeTime + summarizeTime); // 最少 30 秒
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
            statusText.textContent = '分析音檔中...';
            progressText.textContent = '';
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loader"></span>處理中...';

            // 顯示進度條
            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';

            const formData = new FormData();
            const audioFile = fileInput.files[0];
            formData.append('file', audioFile);
            formData.append('style', document.getElementById('styleSelect').value);

            // 獲取音檔長度並預估處理時間
            const audioDuration = await getAudioDuration(audioFile);
            const estimatedTime = estimateProcessingTime(audioDuration);
            const audioDurationMins = Math.floor(audioDuration / 60);
            const audioDurationSecs = Math.floor(audioDuration % 60);

            let progressTimer = null;
            let seconds = 0;
            let currentProgress = 0;

            try {
                statusText.textContent = '正在進行語音轉文字...';
                progressText.textContent = `音檔長度: ${audioDurationMins}:${audioDurationSecs.toString().padStart(2, '0')} | 預估處理時間: ${Math.ceil(estimatedTime)} 秒`;

                // 進度條動畫：根據預估時間平滑增長到 95%
                const progressIncrement = 95 / estimatedTime; // 每秒增加的百分比
                progressTimer = setInterval(() => {
                    seconds++;
                    if (currentProgress < 95) {
                        // 使用非線性增長，前期快後期慢
                        const targetProgress = Math.min(95, (seconds / estimatedTime) * 95);
                        currentProgress += (targetProgress - currentProgress) * 0.3 + 0.5;
                        currentProgress = Math.min(95, currentProgress);
                        progressBar.style.width = currentProgress.toFixed(1) + '%';
                    }

                    // 更新狀態文字
                    const mins = Math.floor(seconds / 60);
                    const secs = seconds % 60;
                    const remaining = Math.max(0, Math.ceil(estimatedTime - seconds));

                    if (currentProgress < 80) {
                        statusText.textContent = '正在進行語音轉文字...';
                    } else {
                        statusText.textContent = '正在生成摘要...';
                    }

                    progressText.textContent = `已處理 ${mins}:${secs.toString().padStart(2, '0')} | 預估剩餘 ${remaining} 秒 | ${currentProgress.toFixed(0)}%`;
                }, 1000);

                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });

                clearInterval(progressTimer);

                const result = await response.json();

                if (result.success) {
                    // 完成進度條動畫
                    progressBar.style.transition = 'width 0.5s ease';
                    progressBar.style.width = '100%';

                    status.className = 'status show success';
                    statusText.textContent = '處理完成！';
                    const finalMins = Math.floor(seconds / 60);
                    const finalSecs = seconds % 60;
                    progressText.textContent = `完成！總耗時 ${finalMins}:${finalSecs.toString().padStart(2, '0')} | 語言: ${result.language || '自動偵測'}`;

                    // 儲存原始文字（用於複製和 PDF）
                    window.rawTranscript = result.transcript_with_timestamps || result.transcript;
                    window.rawSummary = result.summary;

                    // 顯示帶時間軸的逐字稿
                    transcriptResult.innerHTML = formatTranscript(window.rawTranscript);
                    transcriptSection.classList.add('show');

                    summaryResult.innerHTML = formatSummary(window.rawSummary);
                    summarySection.classList.add('show');

                    // 隱藏進度條
                    setTimeout(() => {
                        progressContainer.style.display = 'none';
                        progressBar.style.transition = '';
                    }, 1000);
                } else {
                    throw new Error(result.error || '處理失敗');
                }
            } catch (error) {
                if (progressTimer) clearInterval(progressTimer);
                progressContainer.style.display = 'none';
                status.className = 'status show error';
                statusText.textContent = '處理失敗';
                progressText.textContent = error.message;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '開始處理';
            }
        });

        function formatTranscript(text) {
            // 格式化帶時間軸的逐字稿
            return text
                .split('\\n')
                .map(line => {
                    // 匹配時間戳格式 [00:00 - 00:00]
                    const match = line.match(/^\\[(\\d{2}:\\d{2})\\s*-\\s*(\\d{2}:\\d{2})\\]\\s*(.*)$/);
                    if (match) {
                        return `<div style="margin-bottom: 8px;"><span class="timestamp">[${match[1]} - ${match[2]}]</span> ${match[3]}</div>`;
                    }
                    return line ? `<div style="margin-bottom: 8px;">${line}</div>` : '';
                })
                .join('');
        }

        function formatSummary(text) {
            // 簡單的 Markdown 轉 HTML
            return text
                .replace(/^## (.+)$/gm, '<h4>$1</h4>')
                .replace(/^- (.+)$/gm, '<li>$1</li>')
                .replace(/(<li>.*<\\/li>\\n?)+/g, '<ul>$&</ul>')
                .replace(/\\n/g, '<br>');
        }

        // 顯示 Toast 提示
        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }

        // 複製到剪貼簿
        async function copyToClipboard(type) {
            const text = type === 'transcript' ? window.rawTranscript : window.rawSummary;
            if (!text) {
                showToast('沒有可複製的內容');
                return;
            }
            try {
                await navigator.clipboard.writeText(text);
                showToast(type === 'transcript' ? '逐字稿已複製！' : '摘要已複製！');
            } catch (err) {
                // Fallback for older browsers
                const textarea = document.createElement('textarea');
                textarea.value = text;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast(type === 'transcript' ? '逐字稿已複製！' : '摘要已複製！');
            }
        }

        // 下載 PDF
        async function downloadPDF(type) {
            const text = type === 'transcript' ? window.rawTranscript : window.rawSummary;
            const title = type === 'transcript' ? '會議逐字稿' : '會議摘要';
            const filename = type === 'transcript' ? '逐字稿.pdf' : '摘要.pdf';

            if (!text) {
                showToast('沒有可下載的內容');
                return;
            }

            showToast('正在生成 PDF...');

            try {
                const { jsPDF } = window.jspdf;
                const pdf = new jsPDF('p', 'mm', 'a4');
                const pageWidth = 210;
                const pageHeight = 297;
                const margin = 20;
                const contentWidth = pageWidth - (margin * 2);
                const maxContentHeight = pageHeight - (margin * 2) - 60; // 預留標題空間

                // 將文字按行分割
                const lines = text.split('\\n');
                const firstPageLines = 35; // 第一頁（有標題）約 35 行
                const otherPageLines = 42; // 其他頁約 42 行，盡量排滿

                // 計算總頁數
                let remainingLines = lines.length;
                let totalPages = 1;
                remainingLines -= firstPageLines;
                if (remainingLines > 0) {
                    totalPages += Math.ceil(remainingLines / otherPageLines);
                }

                let currentLine = 0;
                const now = new Date();
                const dateStr = now.toLocaleString('zh-TW');

                for (let page = 0; page < totalPages; page++) {
                    if (page > 0) pdf.addPage();

                    const linesForThisPage = page === 0 ? firstPageLines : otherPageLines;

                    // 建立該頁的臨時容器
                    const tempDiv = document.createElement('div');
                    tempDiv.style.cssText = `
                        position: absolute;
                        left: -9999px;
                        top: 0;
                        width: 750px;
                        padding: 25px 30px;
                        background: white;
                        font-family: -apple-system, BlinkMacSystemFont, "Microsoft JhengHei", "微軟正黑體", "PingFang TC", sans-serif;
                        font-size: 13px;
                        line-height: 1.6;
                    `;

                    const startLine = currentLine;
                    const endLine = Math.min(currentLine + linesForThisPage, lines.length);
                    currentLine = endLine;
                    const pageContent = lines.slice(startLine, endLine).join('\\n');

                    // 第一頁顯示標題
                    const headerHtml = page === 0 ? `
                        <div style="text-align: center; margin-bottom: 15px;">
                            <h1 style="font-size: 22px; color: #333; margin-bottom: 8px;">${title}</h1>
                            <p style="color: #666; font-size: 11px;">產生時間：${dateStr} | 世德會議助理</p>
                        </div>
                        <hr style="border: none; border-top: 2px solid #667eea; margin: 15px 0;">
                    ` : '';

                    tempDiv.innerHTML = `
                        ${headerHtml}
                        <div style="white-space: pre-wrap; color: #333; font-size: 13px;">${pageContent.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>
                        <div style="text-align: center; margin-top: 20px; color: #999; font-size: 10px;">
                            第 ${page + 1} / ${totalPages} 頁
                        </div>
                    `;

                    document.body.appendChild(tempDiv);

                    // 使用 html2canvas 轉換為圖片
                    const canvas = await html2canvas(tempDiv, {
                        scale: 2,
                        useCORS: true,
                        logging: false,
                        backgroundColor: '#ffffff'
                    });

                    document.body.removeChild(tempDiv);

                    // 添加圖片到 PDF
                    const imgData = canvas.toDataURL('image/jpeg', 0.92);
                    const imgWidth = pageWidth - 10;
                    const imgHeight = (canvas.height * imgWidth) / canvas.width;

                    pdf.addImage(imgData, 'JPEG', 5, 5, imgWidth, Math.min(imgHeight, pageHeight - 10));
                }

                pdf.save(filename);
                showToast('PDF 已下載！');
            } catch (err) {
                console.error('PDF 生成失敗:', err);
                showToast('PDF 生成失敗，請稍後再試');
            }
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
            "transcript_with_timestamps": result.get("timestamped_text", ""),
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
