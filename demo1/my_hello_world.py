from __future__ import annotations

import json
import os
from dotenv import load_dotenv

import requests

load_dotenv()

API_URL = os.getenv("API_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def build_messages() -> list[dict[str, str]]:
    """构造对话列表"""
    return [
        {
            "role": "system",
            "content": (
                "你是一个面向初学者的 Python 和 agent 助手。"
                "回答时尽量简洁、友好，并在必要时给出清晰步骤。"
            )
        },
        {
            "role": "user",
            "content": "请用一句话介绍什么是 Agent，并给出一个生活中的类别。"
        }
    ]

def call_llm(api_key: str, messages: list[dict[str, str]]) -> dict:
    """
    调用 DeepSeek Chat Completions 接口。
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "thinking" : {"type": "disabled"},
        "max_tokens": 200,
        "temperature": 0.7
    }

    response = requests.post(
        url=API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


def main() -> None:
    """程序入口"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError(
            "缺少环境变量 DEEPSEEK_API_KEY，请在 .env 文件中设置。"
            '$env:DEEPSEEK_API_KEY="你的 API Key"'
        )

    messages = build_messages()

    print("=== 发送给模型的消息 ===")
    print(json.dumps(
        messages,
        ensure_ascii=False,
        indent=2
    ))

    result = call_llm(
        api_key=api_key,
        messages=messages
    )

    print("=== 模型返回的完整响应 ===")
    print(type(result), "\n")
    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ))

    answer = result["choices"][0]["message"]["content"]
    print("\n=== 模型回复 ===")
    print(answer)

    usage = result.get("usage")
    if usage:
        print("\n=== Token 用量 ===")
        print(json.dumps(
            usage,
            ensure_ascii=False,
        ))

if __name__ == "__main__":
    main()