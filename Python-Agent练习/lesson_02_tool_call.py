"""第 2 课：将模型给出的工具调用信息转换成 Python 函数调用。

项目对应：demo6/framework/tool_registry.py 的 execute_tool_call()。
本题先用字典直接保存函数，暂时省略 ToolDefinition 和装饰器。

任务：只补全 execute_tool_call() 中的三个 TODO。
流程：解析参数字符串 -> 按名称找函数 -> 展开参数并执行。
运行本文件即可检查，无需 API Key、网络或第三方依赖。

本题输入约定：工具名一定存在，参数一定是合法 JSON 对象，
参数名与函数匹配。异常处理留到下一步练习。
"""

from __future__ import annotations

import json


def add(a: int, b: int) -> dict:
    """示例工具：计算两数之和。"""
    # 检验类型
    if type(a) is not int or type(b) is not int:
        raise TypeError("a 和 b 必须是整数")

    return {"ok": True, "result": a + b}


def multiply(a: int, b: int) -> dict:
    """示例工具：计算两数之积，用于检查是否按名称选择函数。"""
    return {"ok": True, "result": a * b}


# 字典中的值是函数对象，不是函数执行后的结果。
tools = {"add": add, "multiply": multiply}


def execute_tool_call(tool_call: dict) -> dict:
    """执行一条工具调用，返回工具函数产生的结果字典。"""
    function_info = tool_call["function"]

    # TODO 1：读取 function_info 的 arguments 字段，将 JSON 字符串解析成字典。
    try:
        arguments = json.loads(function_info["arguments"])
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error": "工具参数不是合法 JSON"
        }

    # TODO 2：读取 function_info 的 name 字段，从 tools 中取出对应函数。
    # handler = tools[function_info["name"]]
    handler = tools.get(function_info["name"])

    if handler is None:
        return {
            "ok": False,
            "error": f"未知工具：{function_info["name"]}"
        }

    # TODO 3：将 arguments 展开成关键字参数，调用 handler，取得返回值。
    try:
        result = handler(**arguments)
    except TypeError as exc:
        return {
            "ok": False,
            "error": f"工具调用失败：{exc}"
        }


    # 下方为练习辅助代码，不需要修改。
    if arguments is Ellipsis or handler is Ellipsis or result is Ellipsis:
        raise NotImplementedError("请补全上面的三个 TODO，用实际代码替换 ...")
    return result


def main() -> int:
    """用三条模拟模型响应检查实现；不调用真实模型。"""
    cases = [
        (
            "add：3 + 5",
            {"function": {"name": "add", "arguments": '{"a": 3, "b": 5}'}},
            {"ok": True, "result": 8},
        ),
        (
            "add：更换参数为 -2 和 7",
            {"function": {"name": "add", "arguments": '{"a": -2, "b": 7}'}},
            {"ok": True, "result": 5},
        ),
        (
            "multiply：按名称切换工具，3 × 4",
            {"function": {"name": "multiply", "arguments": '{"a": 3, "b": 4}'}},
            {"ok": True, "result": 12},
        ),
    ]
    passed = 0
    for label, tool_call, expected in cases:
        try:
            actual = execute_tool_call(tool_call)
        except NotImplementedError as exc:
            print(f"[待填写] {label}：{exc}")
        except Exception as exc:
            print(f"[需修改] {label}：{type(exc).__name__}: {exc}")
        else:
            if actual == expected:
                passed += 1
                print(f"[通过] {label} -> {actual}")
            else:
                print(f"[需修改] {label}：期望 {expected}，实际 {actual}")
    print(f"\n通过 {passed}/{len(cases)} 项。")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())