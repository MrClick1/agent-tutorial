# 项目学习笔记（demo4）

记录 demo4 学习中遇到的重要问题与答案。

---

## 1. `build_state_message()` 函数的作用是什么？

**答：** 把当前任务状态整理成一条消息，发给模型，由模型决定下一步动作。

### 参数

| 参数 | 含义 |
|------|------|
| `user_goal` | 用户最初的目标 |
| `state` | 当前任务状态字典 |
| `step_logs` | 已执行步骤的日志列表 |

### 内部逻辑

1. `step_log_text` — 把步骤日志拼接成列表文本；无日志时显示 `- 暂无`
2. `tool_result_text` — 把 `tool_result` 转成 JSON 字符串；无结果时显示 `null`
3. `content` — 用 f-string 拼接完整提示，包含用户目标、当前状态、已执行步骤、以及要求模型返回的 JSON 格式
4. 返回 `{"role": "user", "content": content}`

这是 Agent 中典型的**状态反馈 + 下一步决策**模式。

---

## 2. `response.json()`、`json.dumps()`、`json.loads()` 之间的区别

### 功能对比

| 方法/函数 | 作用 | 方向 | 输入 | 输出 |
|-----------|------|------|------|------|
| `response.json()` | 把 HTTP 响应中的 JSON 文本解析为 Python 对象 | 字符串 → Python 对象 | `requests.Response` 响应体 | Python dict/list 等 |
| `json.loads(s)` | 把 JSON 字符串解析为 Python 对象 | 字符串 → Python 对象 | JSON JSON 字符串 | Python dict/list 等 |
| `json.dumps(obj)` | 把 Python 对象转为 JSON 字符串 | Python 对象 → 字符串 | Python dict/list 等 | JSON 字符串 |

### 关系说明

- `response.json()` 内部其实调用了 `json.loads(response.text)`。
- `json.loads()` 和 `json.dumps()` 互为逆操作：一个把 JSON 字符串变成 Python 对象，一个把 Python 对象变成 JSON 字符串。

### 示例

```python
import json
import requests

response = requests.post(url, json=payload)

# 解析响应 JSON → Python 字典
data = response.json()

# Python 字典 → JSON 字符串
text = json.dumps(data, ensure_ascii=False, indent=2)

# JSON 字符串 → Python 字典
obj = json.loads(text)
```

---

## 3. 为什么 `raw_content` 可能是任意内容，却要解析出 `action` 字段？

**答：** 因为 prompt 已经明确要求模型只返回一个 JSON 对象，其中包含 `action` 字段。程序期望模型遵守这个约定。

在 [`build_state_message()`](demo4/planning_demo.py#L107-L147) 中，prompt 明确写了：

```text
请只返回一个 JSON 对象，字段如下：
{
  "step_summary": "...",
  "action": "decide_path | draft_content | create_file | finish",
  ...
}
```

后续代码要用 `action` 决定下一步：

```python
if action == "decide_path": ...
if action == "draft_content": ...
if action == "create_file": ...
if action == "finish": ...
```

所以 `parse_json_response()` 做了三层校验，把不确定的模型输出变成可安全使用的数据结构：

1. 去掉 markdown 代码块包装
2. `json.loads()` 解析成 Python 对象
3. `isinstance(data, dict)` 确保是字典，否则 `data.get("action")` 会报错

---

## 4. `if not isinstance(data, dict): raise ValueError(...)` 的作用

**答：** 检查模型返回的 JSON 解析后是否是一个 Python 字典（对象），如果不是就抛出异常。

`json.loads()` 可能解析出的类型：

- 字典 `{"action": "finish"}` ✅ 期望
- 列表 `["finish"]` ❌
- 字符串 `"finish"` ❌
- 数字、布尔值等 ❌

这个检查保证后续 `data.get("action")` 能安全执行。

---

*记录时间：2026-07-28*
