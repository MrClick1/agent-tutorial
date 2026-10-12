"""第 4 课：将工具管理逻辑组织成 ToolRegistry 类。

对应项目：demo6/framework/tool_registry.py。
复用第 3 课已经完成的 ToolDefinition 和 tool 装饰器。
本题只接受装饰后的函数，真实项目还支持直接注册 ToolDefinition。

填写顺序：register -> build_tools_payload -> execute_tool_call。
用你的实现替换三个 TODO 中的 raise NotImplementedError。
只修改这三个位置，其余代码已准备好。
运行：python lesson_04_tool_registry.py
"""

from __future__ import annotations

import json

from lesson_03_tool_decorator import ToolDefinition, tool


@tool
def add(a: int, b: int) -> dict:
    """计算两个整数的和。"""
    if type(a) is not int or type(b) is not int:
        raise TypeError("a 和 b 必须是整数")
    return {"ok": True, "result": a + b}


@tool
def multiply(a: int, b: int = 2) -> dict:
    """计算两个整数的积，第二个数默认是 2。"""
    if type(a) is not int or type(b) is not int:
        raise TypeError("a 和 b 必须是整数")
    return {"ok": True, "result": a * b}


class ToolRegistry:
    def __init__(self):
        # 每次创建实例，都会建立属于该实例的工具字典。
        self._tools = {}

    def register(self, func):
        """从函数读取工具定义，再以工具名称为键保存。"""
        definition = getattr(func, "__tool_definition__", None)
        if not isinstance(definition, ToolDefinition):
            raise TypeError("请传入使用 @tool 装饰过的函数")

        # 1：把 definition 放进 self._tools，键是 definition.name。
        self._tools[definition.name] = definition

    def build_tools_payload(self) -> list[dict]:
        """返回发给模型的工具说明列表，不包含 handler。"""
        # 遍历 self._tools.values()，逐个生成并加入列表：
        # {"type": "function", "function": {
        #     "name": ..., "description": ..., "parameters": ...
        # }}
        # 最后返回这个列表，空注册表返回 []。
        payload = []
        for definition in self._tools.values():
            payload.append({
                "type": "function",
                "function": {
                    "name": definition.name,
                    "description": definition.description,
                    "parameters": definition.parameters,
                }
            })

        return payload

    def execute_tool_call(self, tool_call: dict) -> dict:
        """解析模型参数、找到工具、执行并返回结果。"""
        function_info = tool_call["function"]
        tool_name = function_info["name"]
        try:
            arguments = json.loads(function_info["arguments"])
        except json.JSONDecodeError:
            return {"ok": False, "error": "工具参数不是合法 JSON"}

        definition = self._tools.get(tool_name)
        if definition is None:
            return {"ok": False, "error": f"未知工具：{tool_name}"}

        try:
            # 使用 definition.handler 执行工具，展开 arguments 并返回结果。
            return definition.handler(**arguments)
        except TypeError as exc:
            return {"ok": False, "error": f"工具调用失败：{exc}"}


# 以下是准备好的检查代码，不需要修改。
def make_call(name, arguments):
    return {"function": {"name": name, "arguments": arguments}}


def check_registration():
    registry = ToolRegistry()
    registry.register(add)
    registry.register(multiply)
    assert set(registry._tools) == {"add", "multiply"}, "应按工具名称保存两份定义"
    assert registry._tools["add"] is add.__tool_definition__, "应保存工具定义对象"
    print("  注册后的键：", list(registry._tools))


def check_isolation():
    first = ToolRegistry()
    second = ToolRegistry()
    first.register(add)
    second.register(multiply)
    assert set(first._tools) == {"add"}, "不同注册表实例不应共享字典"
    assert set(second._tools) == {"multiply"}, "第二个实例应只保存自己的工具"


def check_payload():
    registry = ToolRegistry()
    assert registry.build_tools_payload() == [], "空注册表的工具说明应为空列表"
    registry.register(add)
    registry.register(multiply)
    payload = registry.build_tools_payload()
    expected = [
        {"type": "function", "function": {
            "name": func.__tool_definition__.name,
            "description": func.__tool_definition__.description,
            "parameters": func.__tool_definition__.parameters,
        }}
        for func in (add, multiply)
    ]
    assert payload == expected, "工具说明的结构或内容不正确"
    json.dumps(payload, ensure_ascii=False)  # 函数对象不能直接作为 JSON 发送。


def check_execution():
    registry = ToolRegistry()
    registry.register(add)
    registry.register(multiply)
    cases = [
        ("add", '{"a": 3, "b": 5}', {"ok": True, "result": 8}),
        ("multiply", '{"a": 3}', {"ok": True, "result": 6}),
        ("divide", '{"a": 6, "b": 2}', {"ok": False, "error": "未知工具：divide"}),
        ("add", '{"a": 3', {"ok": False, "error": "工具参数不是合法 JSON"}),
        ("add", '{"a": "3", "b": 5}', {"ok": False, "error": "工具调用失败：a 和 b 必须是整数"}),
    ]
    for name, arguments, expected in cases:
        actual = registry.execute_tool_call(make_call(name, arguments))
        assert actual == expected, f"{name}: 期望 {expected}，实际 {actual}"


def main() -> int:
    checks = [
        ("注册工具", check_registration),
        ("实例拥有独立字典", check_isolation),
        ("生成模型工具说明", check_payload),
        ("执行工具与错误处理", check_execution),
    ]
    passed = 0
    for label, check in checks:
        try:
            check()
        except NotImplementedError as exc:
            print(f"[待填写] {label}：{exc}")
        except Exception as exc:
            print(f"[需修改] {label}：{type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"[通过] {label}")
    print(f"\n通过 {passed}/{len(checks)} 项。")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())