# 项目学习笔记（demo5）

记录 demo5 学习中遇到的重要问题与答案。

---

## 1. 为什么 `trim_messages()` 里用 `max_turns * 4`？

**答：** 因为一轮完整 ReAct 循环通常产生 4 条消息：

1. `user`：用户请求
2. `assistant`：模型决定调用工具
3. `tool`：工具执行结果
4. `assistant`：模型基于工具结果回复

所以 `max_turns * 4` 才能保留最近 `max_turns` 轮完整上下文。

---

## 2. demo5 整体架构

| 文件 | 作用 |
|------|------|
| `config.py` | 配置常量（API URL、模型名、最大步数等） |
| `state.py` | Agent 状态管理 |
| `tools.py` | 工具定义与执行 |
| `llm.py` | 封装大模型 API 调用 |
| `agent.py` | ReAct 核心循环 |
| `react_demo.py` | 程序入口，处理用户输入 |

---

## 3. ReAct 核心思想

ReAct = Reasoning（推理）+ Acting（行动）

1. **模型看到当前状态，决定下一步**
2. **如果需要工具，就调用工具**
3. **程序执行工具，把结果反馈给模型**
4. **模型基于工具结果继续推理，直到完成**

和 demo4 的区别：demo4 用固定 action 分支控制流程，demo5 让模型自己决定是否需要工具、用什么工具。

---

## 4. `tools.py` 的作用

### `build_tools()`

把可用工具以 OpenAI/DeepSeek 兼容格式告诉模型，每个工具包含：

- `name`：工具名
- `description`：工具用途
- `parameters`：参数说明
- `required`：必填参数

demo5 提供三个工具：`create_text_file`、`read_text_file`、`list_files`。

### `execute_tool_call()`

根据模型返回的工具调用信息，解析参数并执行对应函数，返回：

- `tool_name`：执行的工具名
- `tool_result`：执行结果字典

---

## 5. `agent.py` 主循环流程

```
for loop in range(1, MAX_AGENT_LOOPS + 1):
    1. 组装 runtime messages（system + state + 历史）
    2. 调用 call_llm()
    3. 如果模型返回 tool_calls：
         - 执行工具
         - 把工具结果写回 messages
         - continue 继续下一轮
    4. 如果模型没有 tool_calls：
         - 得到最终答案
         - return 返回给用户
```

---

## 6. `state.py` 和 `messages` 的分工

| 类型 | 作用 |
|------|------|
| `state` | 程序内部维护的结构化事实，如 `last_created_path`、`completed` |
| `messages` | 发给大模型的会话上下文，包含 user、assistant、tool 消息 |

`agent.py` 每次循环会把 `state` 包装成一条 `state_message`，让模型知道当前进度。

---

*记录时间：2026-07-29*
