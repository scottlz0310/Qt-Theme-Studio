#!/usr/bin/env python3
"""
全角括弧を半角括弧に一括変換するスクリプト
"""

from pathlib import Path


def fix_fullwidth_chars_in_file(file_path: Path) -> int:
    """ファイル内の全角括弧を半角括弧に変換"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # 全角括弧を半角括弧に変換
        original_content = content
        content = content.replace("(", "(")
        content = content.replace(")", ")")

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

        if fix_fullwidth_chars_in_file(file_path):
            print(f"修正: {file_path.relative_to(project_root)}")
            fixed_count += 1

    print(f"\n修正完了: {fixed_count}ファイル")


if __name__ == "__main__":
    main()
