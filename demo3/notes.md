# 项目学习笔记（demo3）

记录 demo3 学习中遇到的重要问题与答案。

---

## 1. `GENERATED_FILES_DIR = Path(__file__).resolve().parent / "generated_files"` 是什么意思？

**答：** 这行代码用于定义一个路径变量，指向**当前脚本文件所在目录下的 `generated_files` 子目录**。

逐部分拆解：

| 部分 | 含义 |
|------|------|
| `Path(__file__)` | 当前脚本文件的路径对象 |
| `.resolve()` | 解析为绝对路径，并消除 `..`、`.` 等符号 |
| `.parent` | 当前文件的父目录 |
| `/ "generated_files"` | 拼接子目录名 |

例如：
- 若当前脚本是 `demo3/tool_demo.py`
- 则 `GENERATED_FILES_DIR` 指向 `demo3/generated_files`

`/` 在 `pathlib.Path` 中用于拼接路径，比字符串拼接更跨平台。

---

*记录时间：2026-07-28*
