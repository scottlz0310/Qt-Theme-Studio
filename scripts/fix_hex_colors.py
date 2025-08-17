#!/usr/bin/env python3
"""
5桁の16進数カラーコードを6桁に修正するスクリプト
"""

import glob
import re


def fix_hex_colors(file_path):
    """5桁の16進数カラーコードを6桁に修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 7桁の16進数カラーコードを6桁に修正(#fffffff -> #ffffff)
    content = re.sub(r"#fffffff(?=\b|$)", "#ffffff", content, flags=re.IGNORECASE)

    # 5桁の16進数カラーコードを6桁に修正(#fffff -> #ffffff)
    content = re.sub(r"#fffff(?=\b|$)", "#ffffff", content, flags=re.IGNORECASE)

    # その他の5桁の16進数カラーコードも修正
    content = re.sub(r"#([0-9a-fA-F]{5})(?=\b|$)", r"#\1\1", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """メイン処理"""
    # 全てのPythonファイルを取得
    python_files = glob.glob("qt_theme_studio/**/*.py", recursive=True)

    print(f"修正対象ファイル数: {len(python_files)}")

    for file_path in python_files:
        print(f"修正中: {file_path}")

        try:
            fix_hex_colors(file_path)
        except Exception as e:
            print(f"エラー: {file_path} - {e}")

    print("修正完了!")


if __name__ == "__main__":
    main()
