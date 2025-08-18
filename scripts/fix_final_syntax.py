#!/usr/bin/env python3
"""
残りの構文エラーを完全に修正するスクリプト
"""

import glob
import re


def fix_final_syntax(file_path):
    """構文エラーを完全に修正"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 空の変数名を修正
    content = re.sub(
        r"ColorUtils\.rgb_to_hex\(, , \)", "ColorUtils.rgb_to_hex(r, g, b)", content
    )
    content = re.sub(r"setValue\(\)", "setValue(value)", content)

    # その他の構文エラーを修正
    content = re.sub(r"\{str\(\)\}", "{str(e)}", content)
    content = re.sub(r"isinstance\(, ", "isinstance(e, ", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """メイン処理"""
    # 構文エラーがあるファイルを特定
    problem_files = [
        "qt_theme_studio/views/zebra_editor.py",
        "qt_theme_studio/services/import_service.py",
        "qt_theme_studio/utilities/accessibility_manager.py",
        "qt_theme_studio/utilities/japanese_file_handler.py",
        "qt_theme_studio/views/theme_gallery.py",
    ]

    print(f"修正対象ファイル数: {len(problem_files)}")

    for file_path in problem_files:
        if glob.glob(file_path):
            print(f"修正中: {file_path}")

            try:
                fix_final_syntax(file_path)
            except Exception as e:
                print(f"エラー: {file_path} - {e}")

    print("修正完了!")


if __name__ == "__main__":
    main()
