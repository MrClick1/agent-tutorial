from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
# DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 一轮对话包括 user 和 assitant 两条消息
# 这里保留 4 轮对话
MAX_TURNS = 4


def create_system_message() -> dict[str, str]:
    """创建 system prompt """
    return {
        "role": "system",
        "content": (
            "你是一个面向初学者的 Python 和 agent 助手。"
            "请使用简洁、友好、清晰的中文回答。"
            "如果用户的问题依赖上文，请结合对话历史继续回答。"
        ),
    }


def trim_messages(messages: list[dict[str, str]], max_turns: int) -> list[dict[str, str]]:
    """
    裁剪对话历史，只保留 system prompt 和最近若干轮对话。

    保留第 1 条 system 消息，剩余消息只保留最近 max_turns 轮。
    """

    if not messages:
        return messages

    system_message = messages[0]
    recent_messages = messages[1:]
    max_message_count = max_turns * 2

    if (len(recent_messages) > max_message_count):
        recent_messages = recent_messages[-max_message_count:]

    return [system_message, *recent_messages]


def call_llm(api_key: str, messages: list[dict[str, str]]) -> str:
    """
    调用 DeepSeek LLM API，获取模型的回答。
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "messages": messages,
        "model": MODEL_NAME,
        "stream": False,
        "thinking": {"type": "disabled"},
        "max_tokens": 300,
        "temperature": 0.7,
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"]


def main() -> None:
    """程序入口"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "缺少环境变量 DEEPSEEK_API_KEY，请先在 PowerShell 中执行："
            ' $env:DEEPSEEK_API_KEY="你的 API Key"'
        )
    
    messages: list[dict[str, str]] = [create_system_message()]

    print("Memory Demo 已启动。输入 exit 或 quit 结束。")
    print(f"当前会保留最近 {MAX_TURNS} 轮对话历史。")

    while True:
        user_input = input("\n你：").strip()

        if not user_input:
            print("请输入内容。")
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("对话结束。")
            break

        # 先把用户输入加入记忆中
        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        # 避免历史越来越长，，发送前先裁剪一次
        messages = trim_messages(messages, MAX_TURNS)

        try:
            answer = call_llm(
                api_key=api_key,
                messages=messages
            )
        except requests.RequestException as exc:
            print(f"\n请求失败：{exc}")
            # 这次请求失败时，把
