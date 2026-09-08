# 项目学习笔记（demo8）

记录 demo8 学习中遇到的重要问题与答案。

---

## 1. demo8 是什么？

**答：** demo8 在 demo6/7 基础上引入了 **Workflow（工作流）编排层**，把 coding agent 任务拆成固定节点，按有向图执行。

---

## 2. 文件结构

| 层级 | 文件 | 作用 |
|------|------|------|
| framework/ | `node.py` | 节点基类 |
| framework/ | `workflow.py` | workflow 流转引擎 |
| framework/ | `context.py` | 上下文基类 |
| 业务层 | `nodes.py` | 具体节点实现 |
| 业务层 | `example_context.py` | code 场景上下文 |
| 业务层 | `tools.py` | coding 专用工具 |
| 业务层 | `workflow_demo.py` | 程序入口 |

---

## 3. 节点与职责

| 节点 | 职责 |
|------|------|
| `ClassifyNode` | 判断用户输入属于哪类任务 |
| `InspectNode` | 观察/搜索代码 |
| `PlanNode` | 制定修改计划 |
| `ApplyNode` | 执行修改 |
| `VerifyNode` | 验证修改结果 |
| `ReportNode` | 输出最终报告 |

---

## 4. 节点连接方式

```python
classify.connect("inspect", inspect)
inspect.connect("plan", plan)
inspect.connect("report", report)
plan.connect("apply", apply_node)
apply_node.connect("verify", verify)
verify.connect("report", report)
```

每个节点执行后返回下一个节点名字符串，workflow 根据名字路由。

---

## 5. Workflow 主循环流程

```python
current = start_node
for step in range(max_steps):
    next_node_name, logs = current.execute(ctx)  # 执行当前节点
    if next_node_name is None:
        break                                    # 结束 workflow
    current = current.neighbors[next_node_name]  # 跳到下一个节点
```

---

## 6. Context 的作用

`WorkflowContext` 是跨节点共享的状态容器，保存：

- `goal`：用户目标
- `workspace_dir`：工作区目录
- `target_file`：定位到的文件
- `plan`：修改计划
- `logs`：执行日志

每个节点读写同一个 `ctx`，实现状态传递。

---

## 7. 与 demo7 的区别

| demo7 | demo8 |
|-------|-------|
| LLM 自由决定下一步工具 | 流程固定为预定义节点 |
| ReAct 循环 | Workflow 有向图 |
| 适合灵活任务 | 适合结构化、可拆步骤的任务 |
| 工具调用驱动 | 节点执行驱动 |

---

## 8. 一句话总结

> demo8 用 **Workflow 把 Agent 任务节点化、流程化**，适合需要明确阶段（分类→观察→计划→执行→验证→报告）的场景。

---

*记录时间：2026-07-31*
