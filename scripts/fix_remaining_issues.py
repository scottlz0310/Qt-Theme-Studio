#!/usr/bin/env python3
"""
残りの主要な問題を修正するスクリプト
"""

import glob
import re


def fix_undefined_names(file_path):
    """未定義名の問題を修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 例外処理の 'e' を適切に処理
    content = re.sub(r"except Exception as _:", "except Exception:", content)
    content = re.sub(r"except Exception as _", "except Exception", content)

    # 未使用変数を削除
    content = re.sub(r",\s*e(?=\s*[,\)])", "", content)
    content = re.sub(r",\s*r(?=\s*[,\)])", "", content)
    content = re.sub(r",\s*g(?=\s*[,\)])", "", content)
    content = re.sub(r",\s*b(?=\s*[,\)])", "", content)

    # 変数名の '_' を適切な名前に変更
    content = re.sub(r"\b_\b(?=\s*[,\)])", "", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_long_lines(file_path):
    """長い行を修正"""
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    modified = False
    for i, line in enumerate(lines):
        if len(line.rstrip()) > 88:
            # 長い行を分割
            if "#" in line and line.find("#") < 88:
                # コメントがある場合はコメントの前で分割
                comment_start = line.find("#")
                if comment_start > 70:  # コメントが長すぎる場合
                    lines[i] = line[:70] + "\\\n    " + line[70:comment_start] + "\\\n    " + line[comment_start:]
                    modified = True
            elif len(line) > 88 and not line.strip().startswith("#"):
                # 長い行を適切な位置で分割
                if line.count("(") > line.count(")"):
                    # 括弧が開いている場合は括弧の後で分割
                    last_open = line.rfind("(")
                    if last_open > 70:
                        lines[i] = line[:last_open+1] + "\\\n    " + line[last_open+1:]
                        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)


def main():
    """メイン処理"""
    # 全てのPythonファイルを取得
    python_files = glob.glob("qt_theme_studio/**/*.py", recursive=True)

    print(f"修正対象ファイル数: {len(python_files)}")

    for file_path in python_files:
        print(f"修正中: {file_path}")

        try:
            # 各種修正を適用
            fix_undefined_names(file_path)
            fix_long_lines(file_path)
        except Exception as e:
            print(f"エラー: {file_path} - {e}")

    print("修正完了!")


if __name__ == "__main__":
    main()
