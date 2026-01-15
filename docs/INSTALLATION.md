# 安裝指南

本文件提供世德會議助理的完整安裝步驟。

## 目錄

- [環境需求](#環境需求)
- [安裝步驟](#安裝步驟)
- [Ollama 設定](#ollama-設定)
- [模型下載](#模型下載)
- [驗證安裝](#驗證安裝)
- [常見問題](#常見問題)

---

## 環境需求

### 硬體需求

| 項目 | 最低需求 | 建議配置 |
|------|----------|----------|
| 處理器 | Apple Silicon M1 | M2 Pro 或更新 |
| 記憶體 | 16GB RAM | 32GB RAM |
| 儲存空間 | 20GB 可用空間 | 50GB 可用空間 |

**注意事項**

- 本專案使用 MLX 框架，僅支援 Apple Silicon 晶片（M1/M2/M3 系列）
- Intel Mac 無法執行本專案

### 軟體需求

| 項目 | 版本 |
|------|------|
| macOS | 13.0 (Ventura) 或更新 |
| Python | 3.9 或更新 |
| Ollama | 最新版本 |

---

## 安裝步驟

### 步驟 1：安裝 Python

確認系統已安裝 Python 3.9+：

```bash
python3 --version
```

如果尚未安裝，可透過 Homebrew 安裝：

```bash
# 安裝 Homebrew（如果尚未安裝）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安裝 Python
brew install python@3.11
```

### 步驟 2：複製專案

```bash
git clone <repository-url>
cd meeting_agent
```

### 步驟 3：建立虛擬環境

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate
```

**提示**：每次開啟新的終端機視窗時，都需要執行 `source venv/bin/activate` 來啟動虛擬環境。

### 步驟 4：安裝依賴套件

```bash
pip install --upgrade pip
pip install -r poc/requirements.txt
```

**安裝的主要套件**

| 套件 | 用途 |
|------|------|
| mlx-whisper | Apple Silicon 優化的語音識別 |
| fastapi | Web API 框架 |
| uvicorn | ASGI 伺服器 |
| requests | HTTP 客戶端（呼叫 Ollama API） |

---

## Ollama 設定

### 安裝 Ollama

**方法一：官方安裝腳本**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**方法二：Homebrew**

```bash
brew install ollama
```

**方法三：手動下載**

前往 [Ollama 官網](https://ollama.com/download) 下載 macOS 版本並安裝。

### 啟動 Ollama 服務

```bash
ollama serve
```

**注意事項**

- Ollama 服務需要持續運行，建議開一個獨立的終端機視窗
- 預設監聽端口為 `11434`
- 可透過設定環境變數 `OLLAMA_HOST` 來更改監聽位址

### 驗證 Ollama 服務

```bash
curl http://localhost:11434/api/tags
```

若服務正常運行，會回傳已安裝的模型列表。

---

## 模型下載

### 下載 LLM 模型（Ollama）

本專案預設使用 `qwen2.5:14b` 模型：

```bash
ollama pull qwen2.5:14b
```

**模型大小**：約 9GB

**其他可選模型**

| 模型 | 大小 | 說明 |
|------|------|------|
| `qwen2.5:7b` | ~5GB | 較快速，品質稍低 |
| `qwen2.5:14b` | ~9GB | 建議使用（預設） |
| `qwen2.5:32b` | ~20GB | 最佳品質，需較多記憶體 |
| `llama3:8b` | ~5GB | 英文表現較佳 |

**切換模型**

如需使用其他模型，修改 `poc/summarizer.py` 中的 `DEFAULT_MODEL` 變數：

```python
DEFAULT_MODEL = "qwen2.5:32b"  # 改為想使用的模型
```

### 下載 Whisper 模型（自動）

Whisper 模型會在首次執行時自動下載：

- **模型名稱**：`mlx-community/whisper-large-v3-mlx`
- **模型大小**：約 3GB
- **儲存位置**：`~/.cache/huggingface/`

首次執行時會看到下載進度：

```
Downloading model mlx-community/whisper-large-v3-mlx...
```

---

## 驗證安裝

### 1. 檢查 Python 環境

```bash
source venv/bin/activate
python -c "import mlx_whisper; print('mlx-whisper OK')"
python -c "import fastapi; print('fastapi OK')"
```

### 2. 檢查 Ollama 服務

```bash
curl http://localhost:11434/api/tags
```

### 3. 啟動應用程式

```bash
cd poc
python app.py
```

若一切正常，會看到以下輸出：

```
檢查 Ollama 服務狀態...
✅ Ollama 服務正常，已安裝模型: qwen2.5:14b

🚀 啟動 Web 介面...
📱 請在瀏覽器開啟: http://localhost:7860
----------------------------------------
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
```

### 4. 測試 Web 介面

開啟瀏覽器，前往 http://localhost:7860，應該可以看到上傳介面。

---

## 常見問題

### Q1: 出現 `ModuleNotFoundError: No module named 'mlx'`

**原因**：未安裝 MLX 框架或不是在 Apple Silicon Mac 上執行

**解決方法**：

```bash
# 確認是 Apple Silicon Mac
uname -m  # 應該顯示 arm64

# 重新安裝 mlx-whisper
pip install --upgrade mlx-whisper
```

### Q2: Ollama 服務無法連接

**原因**：Ollama 服務未啟動或端口被佔用

**解決方法**：

```bash
# 確認 Ollama 服務狀態
curl http://localhost:11434/api/tags

# 如果無回應，啟動服務
ollama serve

# 如果端口被佔用，檢查佔用程序
lsof -i :11434
```

### Q3: 模型下載速度很慢

**原因**：網路問題或 Hugging Face 伺服器擁塞

**解決方法**：

```bash
# 設定 Hugging Face 鏡像（如果在中國大陸）
export HF_ENDPOINT=https://hf-mirror.com

# 重新執行程式以下載模型
```

### Q4: 記憶體不足

**原因**：同時執行 Whisper 和 Ollama 需要大量記憶體

**解決方法**：

1. 關閉其他佔用記憶體的應用程式
2. 使用較小的 Ollama 模型（如 `qwen2.5:7b`）
3. 升級 Mac 記憶體（如果可能）

### Q5: 轉錄結果為空或品質不佳

**原因**：音檔品質問題或格式不支援

**解決方法**：

1. 確認音檔可以正常播放
2. 嘗試轉換為 WAV 或 MP3 格式
3. 確保音檔有清晰的語音內容
4. 減少背景雜訊

### Q6: 首次執行時卡住

**原因**：正在下載 Whisper 模型

**解決方法**：

耐心等待下載完成（約 3GB），可以在終端機看到下載進度。下載完成後，後續執行會快很多。

---

## 開發環境設定（選用）

如果需要進行開發，建議安裝以下工具：

```bash
# 安裝開發依賴
pip install black flake8 pytest

# 格式化程式碼
black poc/

# 檢查程式碼風格
flake8 poc/
```

---

## 下一步

安裝完成後，請參考以下文件：

- [README.md](../README.md) - 專案總覽與快速開始
- [API.md](API.md) - API 端點說明
- [ARCHITECTURE.md](ARCHITECTURE.md) - 系統架構說明
