"""第 6 课：一次写完最小 Agent 主循环。
对应 demo6/framework/runtime.py；使用模拟模型，不需要网络或 API Key。
直接复用已完成的第 4 课，不依赖第 5 课是否完成。
运行：python -X utf8 -B Python-Agent练习/lesson_06_agent_runtime.py
"""
from __future__ import annotations

import json
from lesson_04_tool_registry import ToolRegistry, add, multiply


def execute_and_record(messages, assistant_message, registry):
    """已提供的消息回写逻辑，专注练习主循环。"""
    calls = assistant_message["tool_calls"]
    messages.append({"role": "assistant",
                     "content": assistant_message.get("content"),
                     "tool_calls": calls})
    for call in calls:
        result = registry.execute_tool_call(call)
        messages.append({"role": "tool", "tool_call_id": call["id"],
                         "content": json.dumps(result, ensure_ascii=False)})


def run_agent(goal, registry, call_model, max_loops=4):
    messages = [{"role": "user", "content": goal}]
    tools = registry.build_tools_payload()

    for _ in range(max_loops):
        assistant_message = call_model(messages, tools)
        tool_calls = assistant_message.get("tool_calls") or []

        # TODO A：有工具调用时，执行 execute_and_record(...)，然后继续下一轮。
        # 提示：用 if tool_calls: 判断；执行后用 continue。
        if tool_calls:
            execute_and_record(
                messages,
                assistant_message,
                registry,
            )
            continue

        # TODO B：没有工具调用时，取 content（为空则用“任务已处理完成。”），
        # 把 role=assistant、content=final_answer 的消息加入 messages，
        # 最后 return final_answer。
        final_answer = assistant_message.get("content") or "任务已处理完成。"

        messages.append({
            "role": "assistant",
            "content": final_answer,
        })

        return final_answer

    raise RuntimeError("超过最大循环次数")


class FakeModel:
    """先请求计算，再读取工具结果作答，并检查消息关联。"""
    def __init__(self):
        self.calls = 0

    def __call__(self, messages, tools):
        self.calls += 1
        assert tools and tools[0]["type"] == "function"
        if self.calls == 1:
            assert messages == [{"role": "user", "content": "计算 3 加 5"}]
            return {"content": None, "tool_calls": [{
                "id": "call_add_1", "type": "function",
                "function": {"name": "add", "arguments": '{"a": 3, "b": 5}'}}]}
        assert self.calls == 2, "拿到最终回答后应停止调用模型"
        assert [m["role"] for m in messages] == ["user", "assistant", "tool"]
        assert messages[1]["tool_calls"][0]["id"] == messages[2]["tool_call_id"]
        value = json.loads(messages[2]["content"])["result"]
        return {"content": f"3 加 5 等于 {value}", "tool_calls": []}


def make_registry():
    registry = ToolRegistry()
    registry.register(add)
    registry.register(multiply)
    return registry


def check_tool_loop():
    model = FakeModel()
    answer = run_agent("计算 3 加 5", make_registry(), model)
    assert answer == "3 加 5 等于 8", f"实际答案：{answer!r}"
    assert model.calls == 2
    print("  两次模型调用：请求工具 → 根据结果回答")


def check_direct_answer():
    history = []
    def model(messages, tools):
        history.append(messages)
        return {"content": "你好"}  # 没有 tool_calls 字段
    assert run_agent("打个招呼", make_registry(), model) == "你好"
    assert len(history) == 1
    assert history[0][-1] == {"role": "assistant", "content": "你好"}


def check_loop_limit():
    count = 0
    def model(messages, tools):
        nonlocal count
        count += 1
        return {"content": None, "tool_calls": [{
            "id": f"call_{count}", "type": "function",
            "function": {"name": "multiply", "arguments": '{"a": 3}'}}]}
    try:
        run_agent("持续请求工具", make_registry(), model, max_loops=2)
    except RuntimeError as exc:
        assert str(exc) == "超过最大循环次数"
    else:
        raise AssertionError("达到上限应抛出 RuntimeError")
    assert count == 2, "上限计数的是模型调用次数"


def main():
    checks = [("完整工具闭环", check_tool_loop),
              ("直接回答并结束", check_direct_answer),
              ("循环上限", check_loop_limit)]
    passed = 0
    for name, check in checks:
        try:
            check()
        except Exception as exc:
            print(f"[需完成] {name}：{type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"[通过] {name}")
    print(f"通过 {passed}/{len(checks)} 项")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
