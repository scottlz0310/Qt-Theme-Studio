#!/usr/bin/env python3
"""
型注釈のDict/Listをdict/listに一括変換するスクリプト
"""

import re
from pathlib import Path


def fix_type_annotations_in_file(file_path: Path) -> int:
    """ファイル内の型注釈を修正"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # dict → dict
        content = re.sub(r"typing\.Dict", "dict", content)
        content = re.sub(
            r"from typing import.*.*",
            lambda m: m.group(0)
            .replace("", "")
            .replace(",", ",")
            .replace("]", "]")
            .replace("[", "["),
            content,
        )

        # list → list
        content = re.sub(r"typing\.List", "list", content)
        content = re.sub(
            r"from typing import.*.*",
            lambda m: m.group(0)
            .replace("", "")
            .replace(",", ",")
            .replace("]", "]")
            .replace("[", "["),
            content,
        )

        # Dict → dict (型注釈のみ)
        content = re.sub(r"(\w+):\s*Dict\[", r"\1: dict[", content)
        content = re.sub(r"->\s*Dict\[", r"-> dict[", content)

        # List → list (型注釈のみ)
        content = re.sub(r"(\w+):\s*List\[", r"\1: list[", content)
        content = re.sub(r"->\s*List\[", r"-> list[", content)

        # 空のimport文を削除
        content = re.sub(r"from typing import\s*$", "", content, flags=re.MULTILINE)
        content = re.sub(r"from typing import\s*\n", "\n", content, flags=re.MULTILINE)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return 1
        return 0
    except Exception as e:
        print(f"エラー: {file_path} - {e}")
        return 0


def main():
    """メイン処理"""
    project_root = Path(__file__).parent.parent
    python_files = list(project_root.rglob("*.py"))

    print(f"Pythonファイル数: {len(python_files)}")

    fixed_count = 0
    for file_path in python_files:
        if "venv" in str(file_path) or ".git" in str(file_path):
            continue

        if fix_type_annotations_in_file(file_path):
            print(f"修正: {file_path.relative_to(project_root)}")
            fixed_count += 1

    print(f"\n修正完了: {fixed_count}ファイル")


if __name__ == "__main__":
    main()
