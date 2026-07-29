# 项目学习笔记（demo7）

记录 demo7 学习中遇到的重要问题与答案。

---

## 1. demo7 是什么？

**答：** demo7 是在 demo6 的小型 Agent 框架基础上，实现的一个**本地 Coding Agent**，专门用于观察、搜索和修改本地代码。

---

## 2. 文件结构

| 文件 | 作用 |
|------|------|
| `config.py` | 配置：工作区目录、最大循环次数、记忆轮数 |
| `coding_tools.py` | 定义 coding agent 专用工具 |
| `coding_runtime.py` | 继承 `AgentRuntime` 做场景化定制 |
| `coding_agent_demo.py` | 程序入口 |
| `project_workspace/` | 演示目标项目 |

---

## 3. 工具分类

### 观察型工具

| 工具名 | 作用 |
|--------|------|
| `list_files` | 列出工作区文件 |
| `read_text_file` | 读取文件内容 |
| `search_text` | 在工作区中搜索文本 |
| `search_files_by_name` | 按文件名搜索 |

### 修改型工具

| 工具名 | 作用 |
|--------|------|
| `replace_text_in_file` | 精确字符串替换 |
| `write_text_file` | 写入完整文件 |

---

## 4. `replace_text_in_file` 的安全设计

要求模型提供：

- `relative_path`：目标文件
- `old_text`：旧文本
- `new_text`：新文本
- `expected_occurrences`：预期替换次数

如果 `old_text` 在文件中实际出现次数 ≠ 预期次数，就拒绝执行，防止误替换。

---

## 5. `CodingAgentRuntime` 的定制

继承自 demo6 的 `AgentRuntime`，只覆写了三个方法：

| 方法 | 作用 |
|------|------|
| `create_coding_system_message()` | 强调“先观察，再修改” |
| `create_state()` |把工作区路径写入 `shared_context` |
| `build_runtime_message()` | 每轮提示：先定位代码，再做修改 |

体现了 demo6 框架的目标：**少量覆写即可适配不同场景**。

---

## 6. Coding Agent 典型工作流

```
用户：给 greet_user 加一个空名字处理

[循环 1] search_text("greet_user")
[循环 2] read_text_file("app.py")
[循环 3] replace_text_in_file("app.py", old, new, expected=1)
[循环 4] 给出最终答复
```

---

## 7. 一句话总结

> demo7 在 demo6 框架上做了一个**本地 coding agent**，核心工作流是：**先观察代码 → 定位问题 → 精确修改 → 验证结果**。

---

*记录时间：2026-07-29*
