"""第 5 课：把工具调用及执行结果写入消息历史。
对应 demo6/framework/runtime.py 的工具分支。
不调用真实模型，无需 API Key。填写三个 TODO 后运行本文件。
练习注册表返回结果字典；项目原版返回 (工具名, 结果)，这里沿用第 4 课接口。
"""
from __future__ import annotations

import json
from lesson_04_tool_registry import ToolRegistry, add, multiply


def record_tool_round(messages: list[dict], assistant_message: dict,
                      registry: ToolRegistry) -> None:
    tool_calls = assistant_message["tool_calls"]

    # TODO 1：把模型的工具调用意图加入 messages。
    # 字典字段：role="assistant"、content=assistant_message.get("content")、
    # tool_calls=tool_calls。使用 messages.append(...)。
    messages.append({
        "role": "assistant",
        "content": assistant_message.get("content"),
        "tool_calls": tool_calls
    })

    for tool_call in tool_calls:
        # 调用 registry.execute_tool_call(tool_call)，保存到 tool_result。
        tool_result = registry.execute_tool_call(tool_call)

        # 把工具结果加入 messages。
        # 字典字段：role="tool"、tool_call_id=tool_call["id"]、
        # content=json.dumps(tool_result, ensure_ascii=False)。
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(
                tool_result,
                ensure_ascii=False,
            )
        })


def make_call(call_id: str, name: str, arguments: str) -> dict:
    return {"id": call_id, "type": "function",
            "function": {"name": name, "arguments": arguments}}


def make_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(add)
    registry.register(multiply)
    return registry


def check_single_call():
    messages = [{"role": "user", "content": "计算 3 加 5"}]
    call = make_call("call_add_1", "add", '{"a": 3, "b": 5}')
    assistant = {"role": "assistant", "content": None, "tool_calls": [call]}
    record_tool_round(messages, assistant, make_registry())
    assert len(messages) == 3, "应保留用户消息，再添加调用意图和工具结果"
    assert messages[1] == assistant, "第二条应记录 assistant 的工具调用意图"
    assert messages[2]["role"] == "tool"
    assert messages[2]["tool_call_id"] == "call_add_1", "结果必须对应调用 ID"
    assert isinstance(messages[2]["content"], str), "content 应为 JSON 字符串"
    assert json.loads(messages[2]["content"]) == {"ok": True, "result": 8}
    print(json.dumps(messages, ensure_ascii=False, indent=2))


def check_multiple_calls():
    calls = [make_call("call_1", "add", '{"a": 3, "b": 5}'),
             make_call("call_2", "multiply", '{"a": 3}')]
    messages = []
    record_tool_round(messages, {"content": None, "tool_calls": calls}, make_registry())
    assert [m["role"] for m in messages] == ["assistant", "tool", "tool"]
    assert [m["tool_call_id"] for m in messages[1:]] == ["call_1", "call_2"]
    assert [json.loads(m["content"])["result"] for m in messages[1:]] == [8, 6]


def check_error_result():
    messages = []
    call = make_call("call_missing", "divide", '{}')
    record_tool_round(messages, {"content": None, "tool_calls": [call]}, make_registry())
    assert json.loads(messages[-1]["content"]) == {"ok": False, "error": "未知工具：divide"}
    assert messages[-1]["tool_call_id"] == "call_missing"


def main() -> int:
    checks = [("单工具消息闭环", check_single_call),
              ("多工具结果关联", check_multiple_calls),
              ("失败结果也回写", check_error_result)]
    passed = 0
    for label, check in checks:
        try:
            check()
        except Exception as exc:
            print(f"[需完成] {label}：{type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"[通过] {label}")
    print(f"通过 {passed}/{len(checks)} 项")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
