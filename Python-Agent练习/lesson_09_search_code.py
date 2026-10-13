"""第 9 课：实现 Coding Agent 的代码搜索工具。
对应 demo7/coding_tools.py 的 search_text。
路径边界及测试文件已经准备好，填写 search_text 中的两个 TODO。
运行：python -X utf8 -B Python-Agent练习/lesson_09_search_code.py
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json


def search_text(query: str, workspace: Path) -> dict:
    matches = []
    for path in sorted(workspace.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        # TODO A：遍历 text.splitlines()，用 enumerate(..., start=1) 取得行号和行内容。
        # 当 query in line 时，将一个字典加入 matches，包含：
        # relative_path：path.relative_to(workspace).as_posix()
        # line_number：当前行号
        # line：当前行内容
        for line_number, line in enumerate(text.splitlines(), start=1):
            if query in line:
                matches.append({
                    "relative_path": path.relative_to(workspace).as_posix(),
                    "line_number": line_number,
                    "line": line,
                })

    # TODO B：返回结果字典，字段为：
    # ok=True、query=query、matches=matches、match_count=len(matches)、
    # context_updates={"last_search_query": query}。
    return {
        "ok": True,
        "query": query,
        "matches": matches,
        "match_count": len(matches),
        "context_updates": {
            "last_search_query": query,
        }
    }


# 以下检查在临时目录中准备文件，不修改项目业务代码。
def check_search():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "sub").mkdir()
        (root / "app.py").write_text("name = 'demo'\n# TODO: fix login\n", encoding="utf-8")
        (root / "sub" / "utils.py").write_text("# helper\n# TODO: add test\n", encoding="utf-8")
        (root / "binary.bin").write_bytes(b"\xff\xfe")
        expected = [
            {"relative_path": "app.py", "line_number": 2, "line": "# TODO: fix login"},
            {"relative_path": "sub/utils.py", "line_number": 2, "line": "# TODO: add test"},
        ]
        result = search_text("TODO", root)
        assert result == {"ok": True, "query": "TODO", "matches": expected,
                          "match_count": 2, "context_updates": {"last_search_query": "TODO"}}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        missing = search_text("not_found", root)
        assert missing["matches"] == [] and missing["match_count"] == 0
    print("[通过] 多文件命中、行号、二进制跳过及无命中结果")


if __name__ == "__main__":
    check_search()
