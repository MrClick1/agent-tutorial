"""第 1 课的离线检查：无需第三方包、API Key 或网络。

检查结果用于反馈练习进度，不代表已经掌握相应知识点。
"""

from copy import deepcopy
from pathlib import Path
import sys

from lesson_01_messages import add_message, trim_messages


def sample_messages():
    return [
        {"role": "system", "content": "你是 Python 学习助手。"},
        {"role": "user", "content": "第一问"},
        {"role": "assistant", "content": "第一答"},
        {"role": "user", "content": "第二问"},
        {"role": "assistant", "content": "第二答"},
    ]


def check_add_message():
    messages = [{"role": "system", "content": "学习助手"}]
    returned = add_message(messages, "user", "  我想学习 Python  ")
    expected = [
        {"role": "system", "content": "学习助手"},
        {"role": "user", "content": "  我想学习 Python  "},
    ]
    assert messages == expected, "应保留已有消息，并往原列表追加消息字典"
    assert returned is None, "add_message 的返回值应为 None"


def check_trim(max_turns, expected_indices, only_system=False):
    messages = sample_messages()
    if only_system:
        messages = messages[:1]
    before = deepcopy(messages)
    expected = [before[index] for index in expected_indices]
    actual = trim_messages(messages, max_turns)
    assert isinstance(actual, list), "返回值应是列表"
    assert actual == expected, "期望 {!r}，实际 {!r}".format(expected, actual)
    assert messages == before, "trim_messages 不应改变输入列表或消息内容"
    assert actual is not messages, "应返回新的外层列表"


def check_empty():
    messages = []
    actual = trim_messages(messages, 2)
    assert actual == [], "空输入应返回空列表"
    assert actual is not messages, "空输入也应返回新的列表"


def check_negative(empty=False):
    messages = [] if empty else sample_messages()
    before = deepcopy(messages)
    try:
        trim_messages(messages, -1)
    except ValueError:
        assert messages == before, "抛出异常时也不应修改输入"
        return
    raise AssertionError("负数轮数应抛出 ValueError")


def run_checks():
    cases = [
        ("追加消息与 None 返回值", check_add_message),
        ("只保留最近一轮", lambda: check_trim(1, [0, 3, 4])),
        ("轮数正好等于上限", lambda: check_trim(2, [0, 1, 2, 3, 4])),
        ("轮数不足时完整保留", lambda: check_trim(4, [0, 1, 2, 3, 4])),
        ("零轮只保留 system", lambda: check_trim(0, [0])),
        ("只有 system 的输入", lambda: check_trim(1, [0], only_system=True)),
        ("空列表与新对象", check_empty),
        ("负数轮数", check_negative),
        ("空输入与负数轮数", lambda: check_negative(empty=True)),
    ]
    passed = 0
    for name, check in cases:
        try:
            check()
        except NotImplementedError as exc:
            print("[待完成] {}：{}".format(name, exc))
        except Exception as exc:
            print("[未通过] {}：{}: {}".format(name, type(exc).__name__, exc))
        else:
            passed += 1
            print("[通过] {}".format(name))
    print("\n通过 {}/{} 项。".format(passed, len(cases)))
    if passed == len(cases):
        print("接下来请解释：为什么新列表仍可能共享内部的字典？")
    else:
        print("打开练习文件：{}".format(Path(__file__).with_name("lesson_01_messages.py")))
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(run_checks())
