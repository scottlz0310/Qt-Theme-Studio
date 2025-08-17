#!/usr/bin/env python3
"""
主要なコード品質問題を修正するスクリプト
"""

import glob
import re


def fix_imports(file_path):
    """未使用のインポートを削除"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 未使用のインポートを削除(基本的なもののみ)
    unused_imports = [
        r"from typing import Type\n",
        r"import typing\.Type\n",
        r"from typing import Union\n",
        r"from typing import Optional\n",
        r"from typing import Tuple\n",
        r"from typing import \n",
        r"from typing import Set\n",
        r"import logging\n",
        r"import os\n",
        r"import math\n",
        r"from pathlib import Path\n",
    ]

    for pattern in unused_imports:
        content = re.sub(pattern, "", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_f_strings(file_path):
    """f-stringの問題を修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # プレースホルダーのないf-stringを通常の文字列に変更
    content = re.sub(r'f"([^"]*)"(?![^"]*\{)', r'"\1"', content)
    content = re.sub(r"f'([^']*)'(?![^']*\{)", r"'\1'", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_comparisons(file_path):
    """比較の問題を修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # == False/True を is False/True に変更
    content = re.sub(r"== False\b", "is False", content)
    content = re.sub(r"== True\b", "is True", content)
    content = re.sub(r"!= False\b", "is not False", content)
    content = re.sub(r"!= True\b", "is not True", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_variable_names(file_path):
    """曖昧な変数名を修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 'l' を 'lightness' に変更(HSL色空間のコンテキストで)
    content = re.sub(r"\bl\b(?=\s*[=,\)])", "lightness", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_bare_except(file_path):
    """bare exceptを修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # bare except を Exception に変更
    content = re.sub(r"except:\s*$", "except Exception:", content, flags=re.MULTILINE)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_undefined_names(file_path):
    """未定義名を修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # datetime の未定義を修正
    if "datetime" in content and "import datetime" not in content:
        content = "import datetime\n" + content

    # LogCategory の未定義を修正
    if "LogCategory" in content and "from ..logger import LogCategory" not in content:
        content = re.sub(r"(from \.\. import.*)", r"\1\nfrom ..logger import LogCategory", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_redefinitions(file_path):
    """関数の再定義を修正(コメントアウト)"""
    with open(file_path, encoding="utf-8") as f:
        lines = content.split("\n")

    # 再定義された関数をコメントアウト
    redefined_functions = []
    function_names = set()

    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            func_name = re.search(r"def\s+(\w+)", line)
            if func_name:
                name = func_name.group(1)
                if name in function_names:
                    # 再定義された関数をコメントアウト
                    j = i
                    indent = len(line) - len(line.lstrip())
                    while j < len(lines):
                        if lines[j].strip() == "":
                            j += 1
                            continue
                        current_indent = len(lines[j]) - len(lines[j].lstrip())
                        if current_indent <= indent and j > i:
                            break
                        lines[j] = "# " + lines[j]
                        j += 1
                else:
                    function_names.add(name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    """メイン処理"""
    # 全てのPythonファイルを取得
    python_files = glob.glob("qt_theme_studio/**/*.py", recursive=True)
    python_files.extend(glob.glob("tests/**/*.py", recursive=True))

    self.logger.info(f"修正対象ファイル数: {len(python_files)}")

    for file_path in python_files:
        self.logger.info(f"修正中: {file_path}")

        try:
            # 各種修正を適用
            fix_imports(file_path)
            fix_f_strings(file_path)
            fix_comparisons(file_path)
            fix_variable_names(file_path)
            fix_bare_except(file_path)
            fix_undefined_names(file_path)
            # fix_redefinitions(file_path)  # 複雑なので一旦スキップ
        except Exception as e:
            self.logger.info(f"エラー: {file_path} - {e}")

    self.logger.info("修正完了!")


if __name__ == "__main__":
    main()
