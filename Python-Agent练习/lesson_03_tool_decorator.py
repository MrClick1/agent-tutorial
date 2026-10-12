"""第 3 课：实现简化版 @tool 装饰器。

对应项目：demo6/framework/decorators.py。
本题只支持不带配置参数的 @tool，带 description 的写法留到后续。
只修改 tool() 中的三个 TODO，其他部分是准备好的辅助代码。
运行：python lesson_03_tool_decorator.py
"""

from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Callable, get_type_hints


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict
    handler: Callable[..., dict]


def build_parameters(func: Callable) -> dict:
    """准备好的辅助函数：支持具有 str/int 注解的普通参数。"""
    signature = inspect.signature(func)
    hints = get_type_hints(func)
    mapping = {str: "string", int: "integer"}
    properties = {}
    required = []
    for name, parameter in signature.parameters.items():
        properties[name] = {"type": mapping[hints[name]]}
        if parameter.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": properties, "required": required}


def tool(func: Callable) -> Callable:
    """生成工具定义、附加到函数，最后返回原函数。"""
    tool_name = func.__name__
    tool_description = inspect.getdoc(func) or ""
    tool_parameters = build_parameters(func)

    # 创建 ToolDefinition，使用上面三个变量，并令 handler 指向 func。
    definition = ToolDefinition(
        name=tool_name,
        description=tool_description,
        parameters=tool_parameters,
        handler=func,
    )

    # 这是辅助提示，不需要修改。
    if definition is Ellipsis:
        raise NotImplementedError("请先完成 TODO 1：创建 ToolDefinition")

    # 将 definition 保存到 func 的 __tool_definition__ 属性。
    # 提示：setattr(对象, "属性名", 属性值)，也可以直接给属性赋值。
    # func.__setattr__("__tool_definition__", definition)
    setattr(func, "__tool_definition__", definition)

    # 返回原来的函数对象，不要执行函数。
    return func


def add(a: int, b: int) -> dict:
    """计算两个整数的和。"""
    return {"ok": True, "result": a + b}


def multiply(a: int, b: int = 2) -> dict:
    """计算两个整数的积，第二个数默认是 2。"""
    return {"ok": True, "result": a * b}


def main() -> int:
    try:
        # decorated_add = tool(add) 与定义函数时使用 @tool 对应。
        decorated_add = tool(add)
        decorated_multiply = tool(multiply)
    except NotImplementedError as exc:
        print(f"[待填写] {exc}")
        return 1
    except Exception as exc:
        print(f"[需修改] 装饰过程：{type(exc).__name__}: {exc}")
        return 1

    def check_identity():
        assert decorated_add is add, "本题要求返回原函数对象"
        assert decorated_multiply is multiply, "第二个工具也应返回原函数"

    def check_definition():
        for func in (add, multiply):
            definition = getattr(func, "__tool_definition__", None)
            assert isinstance(definition, ToolDefinition), "函数应携带 ToolDefinition"
            assert definition.name == func.__name__, "应读取每个函数自身的名称"
            assert definition.description == inspect.getdoc(func), "应读取每个函数的文档说明"
            assert definition.handler is func, "handler 应指向原函数"

    def check_schema():
        definition = add.__tool_definition__
        assert definition.parameters == {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        }, "add 的参数 schema 不正确"
        assert multiply.__tool_definition__.parameters["required"] == ["a"], "b 有默认值，不应必填"

    def check_execution():
        assert decorated_add(a=3, b=5) == {"ok": True, "result": 8}, "原函数应继续正常执行"
        assert decorated_multiply(a=3) == {"ok": True, "result": 6}, "应保留函数默认参数"
        assert add.__tool_definition__.handler(**{"a": 3, "b": 5}) == {"ok": True, "result": 8}

    checks = [
        ("返回原函数", check_identity),
        ("工具定义及 handler", check_definition),
        ("参数 schema", check_schema),
        ("装饰后仍能执行", check_execution),
    ]
    passed = 0
    for label, check in checks:
        try:
            check()
        except Exception as exc:
            print(f"[需修改] {label}：{type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"[通过] {label}")
    print(f"\n通过 {passed}/{len(checks)} 项。")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())