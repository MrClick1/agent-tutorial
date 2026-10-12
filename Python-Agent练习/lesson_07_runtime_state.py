"""第 7 课：更新任务状态，并组装下一轮模型请求。
对应 demo6/framework/runtime.py 的 update_state_from_tool_result、build_runtime_messages。
无需 API Key。填写两个 TODO 后运行本文件。
"""
from __future__ import annotations

import json


def create_state(goal):
    return {"goal": goal, "shared_context": {}, "last_tool_name": None,
            "last_tool_result": None, "completed": False, "loop_count": 0}


def update_state(state, tool_name, tool_result):
    # TODO A：记录 last_tool_name、last_tool_result；
    # 用 get 取出 context_updates，只有它是 dict 时，
    # 才用 state["shared_context"].update(...) 合并。
    state["last_tool_name"] = tool_name
    state["last_tool_result"] = tool_result
    
    context_updates = tool_result.get("context_updates")

    if isinstance(context_updates, dict):
        state["shared_context"].update(context_updates)


def build_runtime_message(state):
    # 简化项目中的状态消息：JSON 文本保留相同的数据流。
    return {"role": "user", "content": "当前任务状态：\n" +
            json.dumps(state, ensure_ascii=False)}


def build_request_messages(system_message, history, state):
    # TODO B：返回一个新列表，顺序为：
    # system_message、history 中的每条消息、build_runtime_message(state)。
    # 不修改原 history；可使用列表拼接或列表中的 *history 展开。
    messages = []
    messages.append(system_message)
    # messages.append(history)
    messages.extend(history)    # 对 history 中逐个元素加入 messages
    messages.append(build_runtime_message(state))

    return messages

def check_merge():
    state = create_state("读取文件并生成摘要")
    first = {"ok": True, "context_updates": {
        "file_path": "notes.txt", "file_content": "旧正文"}}
    update_state(state, "read_file", first)
    second = {"ok": True, "context_updates": {
        "file_content": "新正文", "summary": "Agent 的工作流程"}}
    update_state(state, "summarize", second)
    assert state["shared_context"] == {
        "file_path": "notes.txt", "file_content": "新正文", "summary": "Agent 的工作流程"}
    assert state["last_tool_name"] == "summarize"
    assert state["last_tool_result"] == second
    assert state["completed"] is False, "一次工具执行不代表整个任务已完成"
    print(json.dumps(state, ensure_ascii=False, indent=2))


def check_optional_updates():
    state = create_state("测试")
    for result in ({"ok": False, "error": "读取失败"},
                   {"ok": True, "context_updates": None},
                   {"ok": True, "context_updates": [1, 2]}):
        update_state(state, "example", result)
        assert state["shared_context"] == {}
        assert state["last_tool_result"] == result


def check_request():
    state = create_state("读取文件")
    state["shared_context"]["file_content"] = "正文"
    system = {"role": "system", "content": "你是任务助手"}
    history = [{"role": "user", "content": "读取 notes.txt"},
               {"role": "assistant", "content": "准备读取"}]
    original = list(history)
    messages = build_request_messages(system, history, state)
    assert messages == [system] + history + [build_runtime_message(state)]
    assert history == original, "组装请求不应向历史追加临时状态消息"
    assert messages is not history
    assert "正文" in messages[-1]["content"]
    assert build_request_messages(system, [], state) == [system, build_runtime_message(state)]


def main():
    checks = [("状态合并与覆盖", check_merge),
              ("没有有效更新数据", check_optional_updates),
              ("下一轮消息顺序", check_request)]
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
