#!/usr/bin/env python3
"""
インポート問題を一括修正するスクリプト
"""

import glob
import re


def fix_common_imports(file_path):
    """一般的なインポート問題を修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 必要なインポートを追加
    imports_to_add = []

    # Path の使用をチェック
    if "Path(" in content and "from pathlib import Path" not in content:
        imports_to_add.append("from pathlib import Path")

    # logging の使用をチェック
    if "logging.getLogger" in content and "import logging" not in content:
        imports_to_add.append("import logging")

    # os の使用をチェック
    if ("os.path" in content or "os.environ" in content or "os.makedirs" in content) and "import os" not in content:
        imports_to_add.append("import os")

    # datetime の使用をチェック
    if "datetime.now" in content and "from datetime import datetime" not in content:
        imports_to_add.append("from datetime import datetime")

    # math の使用をチェック
    if "math." in content and "import math" not in content:
        imports_to_add.append("import math")

    # インポートを追加
    if imports_to_add:
        # 既存のインポート文の後に追加
        lines = content.split("\n")
        insert_index = 0

        for i, line in enumerate(lines):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                insert_index = i + 1
            elif line.strip() == "" and insert_index > 0:
                break

        # インポートを挿入
        for imp in reversed(imports_to_add):
            lines.insert(insert_index, imp)

        content = "\n".join(lines)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_unused_variables(file_path):
    """未使用変数を修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 未使用変数を適切に処理
    # 例外処理の 'e' は '_' に変更
    content = re.sub(r"except Exception as e:", "except Exception as _:", content)
    content = re.sub(r"except Exception as e\n", "except Exception as _:\n", content)

    # その他の未使用変数は削除
    content = re.sub(r",\s*e(?=\s*[,\)])", "", content)
    content = re.sub(r",\s*r(?=\s*[,\)])", "", content)
    content = re.sub(r",\s*g(?=\s*[,\)])", "", content)
    content = re.sub(r",\s*b(?=\s*[,\)])", "", content)

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
            # 各種修正を適用
            fix_common_imports(file_path)
            fix_unused_variables(file_path)
        except Exception as e:
            print(f"エラー: {file_path} - {e}")

    print("修正完了!")


if __name__ == "__main__":
    main()
