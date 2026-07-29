# 项目学习笔记（demo6）

记录 demo6 学习中遇到的重要问题与答案。

---

## 1. demo6 的整体架构

demo6 分为两层：

### framework/ 子包（通用框架层）

| 文件 | 职责 |
|------|------|
| `agent_types.py` | 定义 `ToolDefinition` 数据类 |
| `decorators.py` | 实现 `@tool` 装饰器 |
| `tool_registry.py` | 工具注册、schema 生成、工具执行 |
| `message_store.py` | 消息存储与历史裁剪 |
| `runtime.py` | `AgentRuntime`：核心 ReAct 循环 |
| `llm.py` | 调用 DeepSeek API |
| `helpers.py` | `create_runtime()` 工厂函数 |
| `mcp_adapter.py` | MCP 协议适配 |

### demo 外层（业务层）

| 文件 | 职责 |
|------|------|
| `config.py` | 业务配置 |
| `builtin_tools.py` | 用 `@tool` 定义文件工具 |
| `framework_demo.py` | 程序入口 |

---

## 2. demo6 相比 demo5 的进步

### `@tool` 装饰器定义工具

无需手写 JSON schema：

```python
@tool(description="Create a text file under demo6/generated_files.")
def create_text_file(relative_path: str, content: str, overwrite: bool) -> dict[str, Any]:
    ...
```

`@tool` 自动：
- 取函数名作为工具名
- 取 docstring/描述
- 根据类型注解生成 JSON Schema

### `ToolRegistry` 统一管理工具

```python
registry = ToolRegistry()
registry.register(create_text_file)
registry.register_many(...)
registry.register_tools_from_module(builtin_tools)
```

### `MessageStore` 独立管理消息

```python
message_store = MessageStore(max_turns=6)
message_store.append({"role": "user", "content": user_goal})
```

插入和裁剪逻辑集中在这里。

### `AgentRuntime` 通用运行时

不再写死业务字段，通用 state 结构：

```python
{
    "goal": goal,
    "shared_context": {},
    "last_tool_name": None,
    "last_tool_result": None,
    "completed": False,
    "loop_count": 0,
}
```

具体业务状态通过工具的 `context_updates` 写入 `shared_context`。

---

## 3. `context_updates` 是什么？

工具返回值里可以带一个 `context_updates` 字段：

```python
return {
    "ok": True,
    "path": str(target_path),
    "context_updates": {
        "last_created_relative_path": relative_path,
    },
}
```

`AgentRuntime` 会自动把它合并到 `state["shared_context"]`，让模型知道上下文变化。

---

## 4. ReAct 主循环（runtime.run）

```python
for loop in range(1, max_loops + 1):
    1. 组装 messages（system + 历史 + 当前运行时状态）
    2. 调用 LLM
    3. 如果有 tool_calls：
         - 把 assistant 工具调用意图写入消息
         - 执行工具
         - 工具结果写入 state 和消息
         - continue 下一轮
    4. 如果没有 tool_calls：
         - 得到最终答案
         - 写入消息
         - return 最终答案
```

---

## 5. 一句话总结

> demo6 不再只是写一个 Agent，而是写一个**可以反复使用的 Agent 框架**，把工具定义、消息管理、执行循环标准化。

---

*记录时间：2026-07-29*
