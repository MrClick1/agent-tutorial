"""第 1 课：用列表和字典管理 Agent 的短期记忆。

源码对应：D:/Code/Python/agent-projects/agent-tutorial/demo2/my_memory_demo.py
后续衔接：demo6/framework/message_store.py

学习节奏：自己写函数 -> 运行检查 -> 解释语法 -> 改需求后重新写。
后续练习：工具参数与 JSON、MessageStore 类、asyncio、工具注册与装饰器、Runtime。

本题只处理普通聊天：首条是 system，后面是完整的 user/assistant 对话对。
例如 [system, user1, assistant1, user2, assistant2] 共两轮。
工具消息和未完成的一轮对话，留到 Runtime 练习另行处理。

先实现 add_message，再实现 trim_messages。只修改两个 TODO 区域。
检查命令（在本目录打开终端）：python check_01_messages.py
"""

from __future__ import annotations


def add_message(
    messages: list[dict[str, str]], role: str, content: str
) -> None:
    """往原列表追加一条包含 role 和 content 的字典。

    保留 content 的原始内容，不需要校验或去空格。
    这个函数修改原列表，不返回新列表。
    """
    # TODO：构造字典，然后使用列表的 append 方法。
    raise NotImplementedError("请先实现 add_message")


def trim_messages(
    messages: list[dict[str, str]], max_turns: int
) -> list[dict[str, str]]:
    """返回 system 消息和最近 max_turns 轮普通聊天。

    要求：
    1. max_turns < 0 时抛出 ValueError，包括 messages 为空的情况。
    2. messages 为空时返回一个新的空列表。
    3. 非空时始终保留第一条 system 消息。
    4. max_turns == 0 时只保留 system 消息。
    5. 轮数不足时保留所有消息；轮数过多时保留最近的若干轮。
    6. 不改变传入的列表，返回的外层列表必须是新对象。
       本题允许共享内部的消息字典，不要求深拷贝。

    提示：一轮有两条消息，可以先计算需要保留的消息数。
    可以先写普通 if 和切片；不要求使用 * 解包或列表推导式。
    """
    # TODO：处理边界情况，选取最近消息，组装新列表并返回。
    raise NotImplementedError("请实现 trim_messages")
