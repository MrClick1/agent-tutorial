"""第 8 课：继承 Runtime，扩展 Coding Agent 状态。
对应 demo7/coding_runtime.py 的 create_state 方法。
只填写子类 create_state；无需网络或 API Key。
运行：python -X utf8 -B Python-Agent练习/lesson_08_runtime_inheritance.py
"""
from __future__ import annotations

import json


class AgentRuntime:
    """已提供的通用 Runtime，不需要修改。"""
    def create_state(self, goal):
        return {
            "goal": goal,
            "shared_context": {},
            "last_tool_name": None,
            "last_tool_result": None,
            "completed": False,
            "loop_count": 0,
        }

    def start(self, goal):
        # 模拟项目 run 方法的第一步。
        # self 是子类实例时，会调用子类重写的 create_state。
        return self.create_state(goal)


class CodingAgentRuntime(AgentRuntime):
    def create_state(self, goal):
        # TODO：
        # 1. 使用 super().create_state(goal) 取得父类创建的 state。
        # 2. 在 state["shared_context"] 中加入 workspace_dir，
        #    值为 "project_workspace"。
        # 3. 返回 state。
        # 用你的实现替换下面的占位异常。
        state = super().create_state(goal)
        state["shared_context"]["workspace_dir"] = "project_workspace"

        return state


# 以下检查代码不用修改。
def check_extended_state():
    state = CodingAgentRuntime().create_state("修改 app.py")
    assert state["goal"] == "修改 app.py"
    assert state["shared_context"] == {"workspace_dir": "project_workspace"}
    for key, value in {"last_tool_name": None, "last_tool_result": None,
                       "completed": False, "loop_count": 0}.items():
        assert key in state and state[key] == value, f"父类字段 {key} 应保留"
    print(json.dumps(state, ensure_ascii=False, indent=2))


def check_parent_unchanged():
    CodingAgentRuntime().create_state("代码任务")
    assert AgentRuntime().create_state("普通任务")["shared_context"] == {}


def check_inherited_method():
    runtime = CodingAgentRuntime()
    state = runtime.start("检查 app.py")
    assert state["shared_context"]["workspace_dir"] == "project_workspace", (
        "继承的 start 应通过 self 调用子类 create_state")
    assert state["goal"] == "检查 app.py"
    other = runtime.start("第二个任务")
    assert other is not state, "不同任务应创建不同状态"
    assert other["shared_context"] is not state["shared_context"]


def main():
    checks = [("扩展状态并保留父类字段", check_extended_state),
              ("不改变父类行为", check_parent_unchanged),
              ("继承方法调用子类实现", check_inherited_method)]
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
