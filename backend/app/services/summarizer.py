"""
摘要生成服務
"""
import requests
from app.config import settings


def check_ollama_status() -> dict:
    """檢查 Ollama 服務狀態"""
    try:
        response = requests.get(f"{settings.OLLAMA_API_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return {"available": True, "models": models}
    except Exception:
        pass
    return {"available": False, "models": []}


def generate_summary(text: str, style: str = "meeting") -> str:
    """
    生成摘要

    Args:
        text: 要摘要的文字
        style: 摘要風格 (meeting, article, brief)

    Returns:
        str: 摘要內容
    """
    prompts = {
        "meeting": f"""你是一位專業的會議記錄助手。請將以下會議/對話內容整理成結構化摘要。

內容：
{text}

請用以下格式輸出（使用繁體中文）：

## 摘要
（2-3 句話概述主要內容）

## 重點
- 重點1
- 重點2
- 重點3
（列出 3-5 個重點）

## 待辦事項
（如果有提到需要執行的事項，列出來；如果沒有，可以省略此段）

## 決議
（如果有做出決定，列出來；如果沒有，可以省略此段）
""",

        "article": f"""請將以下內容整理成簡潔的摘要（繁體中文）：

內容：
{text}

請輸出：
1. 一段話摘要（約 100 字）
2. 3-5 個關鍵詞
""",

        "brief": f"""請用 3 句話以內摘要以下內容（繁體中文）：

{text}
"""
    }

    prompt = prompts.get(style, prompts["meeting"])

    try:
        response = requests.post(
            f"{settings.OLLAMA_API_URL}/api/generate",
            json={
                "model": settings.DEFAULT_LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 2048
                }
            },
            timeout=180
        )
        response.raise_for_status()
        return response.json().get("response", "摘要生成失敗")
    except requests.exceptions.ConnectionError:
        return "錯誤：無法連接 Ollama 服務"
    except requests.exceptions.Timeout:
        return "錯誤：摘要生成超時"
    except Exception as e:
        return f"錯誤：{str(e)}"
