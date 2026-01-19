"""
摘要生成模組
使用 Ollama API 呼叫本地 LLM 生成結構化摘要
"""

import requests
import json
from typing import Optional


OLLAMA_API_URL = "http://192.168.1.213:11434/api/generate"
DEFAULT_MODEL = "qwen3:32b-q4_K_M"


def summarize(
    text: str,
    model: str = DEFAULT_MODEL,
    style: str = "meeting"
) -> str:
    """
    生成文字摘要

    Args:
        text: 要摘要的文字內容
        model: Ollama 模型名稱
        style: 摘要風格 ('meeting', 'article', 'brief')

    Returns:
        str: 結構化的摘要內容
    """

    # 根據風格選擇不同的 prompt
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
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # 降低隨機性以獲得更一致的輸出
                    "num_predict": 2048  # 最大輸出長度
                }
            },
            timeout=120  # 較長的超時時間，因為大模型推理需要時間
        )

        response.raise_for_status()
        result = response.json()
        return result.get("response", "摘要生成失敗")

    except requests.exceptions.ConnectionError:
        return "錯誤：無法連接 Ollama 服務。請確認 Ollama 已啟動 (ollama serve)"
    except requests.exceptions.Timeout:
        return "錯誤：摘要生成超時，請稍後再試"
    except Exception as e:
        return f"錯誤：{str(e)}"


def check_ollama_status() -> dict:
    """
    檢查 Ollama 服務狀態

    Returns:
        dict: 包含 available (bool) 和 models (list)
    """
    try:
        response = requests.get("http://192.168.1.213:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return {"available": True, "models": models}
    except:
        pass

    return {"available": False, "models": []}


if __name__ == "__main__":
    # 檢查 Ollama 狀態
    status = check_ollama_status()
    print(f"Ollama 狀態: {'可用' if status['available'] else '不可用'}")
    if status['models']:
        print(f"已安裝模型: {', '.join(status['models'])}")

    # 測試摘要功能
    test_text = """
    今天的會議主要討論了三個議題。
    第一，關於新產品的上市時間，決定延後到下個月。
    第二，行銷預算需要增加 20%，已經獲得財務部門同意。
    第三，需要招聘兩位新的工程師來支援開發工作。
    會議結束前，大家同意下週再開一次進度追蹤會議。
    """

    if status['available']:
        print("\n測試摘要生成...")
        result = summarize(test_text)
        print(result)
