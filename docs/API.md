# API 文件

本文件說明世德會議助理的 API 端點規格與使用方式。

## 基本資訊

- **基礎 URL**：`http://localhost:7860`
- **API 格式**：RESTful
- **回應格式**：JSON

---

## 端點列表

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/` | 取得 Web 介面 |
| GET | `/health` | 健康檢查 |
| POST | `/process` | 處理音檔（轉錄 + 摘要） |

---

## 端點詳細說明

### GET /

取得 Web 應用程式介面。

**回應**

- **Content-Type**：`text/html`
- **狀態碼**：`200 OK`

**說明**

回傳完整的單頁 HTML 應用程式，包含音檔上傳、摘要風格選擇等功能。

---

### GET /health

檢查服務運作狀態與 Ollama 連線狀態。

**回應**

- **Content-Type**：`application/json`
- **狀態碼**：`200 OK`

**回應範例**

```json
{
  "status": "ok",
  "ollama": {
    "available": true,
    "models": ["qwen2.5:14b", "llama3:8b"]
  }
}
```

**回應欄位說明**

| 欄位 | 類型 | 說明 |
|------|------|------|
| `status` | string | 服務狀態，固定為 `"ok"` |
| `ollama.available` | boolean | Ollama 服務是否可用 |
| `ollama.models` | array | 已安裝的 Ollama 模型列表 |

---

### POST /process

上傳音檔進行語音轉文字與摘要生成。

**請求**

- **Content-Type**：`multipart/form-data`

**請求參數**

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `file` | file | 是 | 音檔（支援 MP3, WAV, M4A, OGG, FLAC） |
| `style` | string | 否 | 摘要風格，預設為 `"meeting"` |

**摘要風格選項**

| 值 | 說明 |
|------|------|
| `meeting` | 會議摘要（包含摘要、重點、待辦事項、決議） |
| `article` | 文章摘要（約 100 字摘要 + 關鍵詞） |
| `brief` | 簡短摘要（3 句話以內） |

**成功回應**

- **Content-Type**：`application/json`
- **狀態碼**：`200 OK`

```json
{
  "success": true,
  "transcript": "完整的轉錄文字...",
  "transcript_with_timestamps": "[00:00 - 00:05] 第一段文字\n[00:05 - 00:10] 第二段文字...",
  "summary": "## 摘要\n會議主要討論了...\n\n## 重點\n- 重點一\n- 重點二\n\n## 待辦事項\n- 待辦一",
  "language": "zh"
}
```

**成功回應欄位說明**

| 欄位 | 類型 | 說明 |
|------|------|------|
| `success` | boolean | 處理是否成功 |
| `transcript` | string | 完整的轉錄文字（不含時間軸） |
| `transcript_with_timestamps` | string | 帶時間軸的轉錄文字 |
| `summary` | string | AI 生成的摘要（Markdown 格式） |
| `language` | string | 偵測到的語言代碼（如 `zh`、`en`） |

**錯誤回應**

- **Content-Type**：`application/json`
- **狀態碼**：`200 OK`（錯誤透過 JSON 內容表示）

```json
{
  "success": false,
  "error": "錯誤訊息說明"
}
```

**常見錯誤訊息**

| 錯誤訊息 | 說明 |
|----------|------|
| `Ollama 服務未啟動，請執行: ollama serve` | Ollama 服務未啟動 |
| `轉錄結果為空，請確認音檔內容` | 音檔無法辨識或無語音內容 |

---

## 使用範例

### cURL 範例

**健康檢查**

```bash
curl http://localhost:7860/health
```

**處理音檔（會議摘要）**

```bash
curl -X POST http://localhost:7860/process \
  -F "file=@meeting.mp3" \
  -F "style=meeting"
```

**處理音檔（簡短摘要）**

```bash
curl -X POST http://localhost:7860/process \
  -F "file=@meeting.mp3" \
  -F "style=brief"
```

### Python 範例

```python
import requests

# 健康檢查
response = requests.get("http://localhost:7860/health")
print(response.json())

# 處理音檔
with open("meeting.mp3", "rb") as f:
    files = {"file": f}
    data = {"style": "meeting"}
    response = requests.post(
        "http://localhost:7860/process",
        files=files,
        data=data
    )

result = response.json()

if result["success"]:
    print("轉錄結果：")
    print(result["transcript_with_timestamps"])
    print("\n摘要：")
    print(result["summary"])
else:
    print(f"錯誤：{result['error']}")
```

### JavaScript 範例

```javascript
// 健康檢查
const healthCheck = async () => {
  const response = await fetch('http://localhost:7860/health');
  const data = await response.json();
  console.log(data);
};

// 處理音檔
const processAudio = async (file, style = 'meeting') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('style', style);

  const response = await fetch('http://localhost:7860/process', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();

  if (result.success) {
    console.log('轉錄結果：', result.transcript_with_timestamps);
    console.log('摘要：', result.summary);
  } else {
    console.error('錯誤：', result.error);
  }
};
```

---

## 時間軸格式說明

轉錄結果中的 `transcript_with_timestamps` 欄位使用以下格式：

```
[MM:SS - MM:SS] 文字內容
```

**範例**

```
[00:00 - 00:08] 各位好，今天的會議主要討論三個議題。
[00:08 - 00:15] 第一個議題是關於新產品的上市時間。
[00:15 - 00:22] 經過討論，我們決定將上市時間延後到下個月。
```

**欄位說明**

- 開始時間與結束時間以 `MM:SS` 格式表示
- 每一行代表一個語音片段（segment）
- 片段劃分由 Whisper 模型自動判斷

---

## 錯誤處理

### HTTP 狀態碼

本 API 在應用層錯誤時仍回傳 HTTP 200，錯誤資訊透過 JSON 回應中的 `success` 欄位與 `error` 欄位表示。

### 建議的錯誤處理流程

```python
response = requests.post("http://localhost:7860/process", ...)

# 檢查 HTTP 層錯誤
response.raise_for_status()

# 檢查應用層錯誤
result = response.json()
if not result.get("success"):
    error_message = result.get("error", "未知錯誤")
    # 處理錯誤...
```

---

## 效能考量

- **檔案大小限制**：建議單檔不超過 500MB
- **處理時間**：依音檔長度而定，約 1-5 分鐘
- **並行處理**：服務使用執行緒池（max_workers=2）處理請求
- **暫存檔案**：上傳的音檔會在處理完成後自動刪除

---

## 版本資訊

- **API 版本**：POC v1.0
- **最後更新**：2026-01-15
