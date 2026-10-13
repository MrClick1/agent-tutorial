"""第 10 课：工作区路径校验与精确代码替换。
对应 demo7/coding_tools.py 的 resolve_safe_path、replace_text_in_file。
路径校验已提供，填写两个 TODO。检查只修改临时测试文件。
运行：python -X utf8 -B Python-Agent练习/lesson_10_replace_code.py
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json


def resolve_safe_path(workspace: Path, relative_path: str) -> Path:
    cleaned = relative_path.strip().replace("\\", "/")
    if not cleaned:
        raise ValueError("路径不能为空")
    relative = Path(cleaned)
    if relative.is_absolute():
        raise ValueError("不能传入绝对路径")
    base = workspace.resolve()
    target = (base / relative).resolve()
    if target != base and base not in target.parents:
        raise ValueError("不允许访问工作区之外的路径")
    return target


def replace_text_in_file(workspace, relative_path, old_text, new_text,
                         expected_occurrences):
    try:
        target = resolve_safe_path(workspace, relative_path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    if not target.is_file():
        return {"ok": False, "error": "目标文件不存在或不是文件"}
    # 额外基础校验：练习中只允许非空旧文本和正整数预期次数。
    if not old_text or type(expected_occurrences) is not int or expected_occurrences < 1:
        return {"ok": False, "error": "旧文本不能为空，预期次数必须为正整数"}
    original = target.read_text(encoding="utf-8")

    # TODO A：用 original.count(old_text) 得到 occurrences。
    # 次数不等于 expected_occurrences 时，立即返回：
    # {"ok": False, "error": "目标文本出现次数不符合预期"}
    # 失败时不要写文件。
    occurrences = original.count(old_text)
    if occurrences != expected_occurrences:
        return {
            "ok": False,
            "error": "目标文本出现次数不符合预期"
        }
    

    # TODO B：用 original.replace(old_text, new_text) 取得 updated，
    # 用 target.write_text(updated, encoding="utf-8") 写回文件；
    # 返回 ok=True、replaced_occurrences=occurrences、
    # context_updates={"last_modified_relative_path": relative_path} 的字典。
    updated = original.replace(old_text, new_text)
    target.write_text(updated, encoding="utf-8")

    return {
        "ok": True,
        "replaced_occurrences": occurrences,
        "context_updates": {
            "last_modified_relative_path": relative_path,
        }
    }


# 以下检查只操作临时目录，不修改 demo7 的实际工作区。
def check_replace():
    with TemporaryDirectory() as directory:
        workspace = Path(directory)
        path = workspace / "app.py"
        original = "timeout = 10\n# timeout = 10\n"
        path.write_text(original, encoding="utf-8")

        # 两处命中却声称预期一处：应拒绝且保持文件不变。
        result = replace_text_in_file(workspace, "app.py", "timeout = 10", "timeout = 30", 1)
        assert result == {"ok": False, "error": "目标文本出现次数不符合预期"}
        assert path.read_text(encoding="utf-8") == original, "校验失败不应修改文件"

        # 预期两处：执行替换并核对真实文件内容。
        result = replace_text_in_file(workspace, "app.py", "timeout = 10", "timeout = 30", 2)
        assert result == {"ok": True, "replaced_occurrences": 2,
                          "context_updates": {"last_modified_relative_path": "app.py"}}
        assert path.read_text(encoding="utf-8") == "timeout = 30\n# timeout = 30\n"
        print(json.dumps(result, ensure_ascii=False, indent=2))

        result = replace_text_in_file(workspace, "../outside.py", "x", "y", 1)
        assert result["ok"] is False and "工作区之外" in result["error"]
        result = replace_text_in_file(workspace, "missing.py", "x", "y", 1)
        assert result["ok"] is False
        result = replace_text_in_file(workspace, "app.py", "missing", "y", 1)
        assert result["ok"] is False
    print("[通过] 次数不符不写入、正确替换、越界拒绝及目标不存在")


if __name__ == "__main__":
    check_replace()
