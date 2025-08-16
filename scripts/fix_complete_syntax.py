#!/usr/bin/env python3
"""
残りの構文エラーを完全に修正するスクリプト
"""

import re
import glob


def fix_complete_syntax(file_path):
    """構文エラーを完全に修正"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 空の変数名を修正
    content = re.sub(r', , b =', 'r, g, b =', content)
    content = re.sub(r', , b =', 'r, g, b =', content)
    content = re.sub(r'\[, , b\]', '[r, g, b]', content)
    
    # その他の構文エラーを修正
    content = re.sub(r'\{str\(\)\}', '{str(e)}', content)
    content = re.sub(r'isinstance\(, ', 'isinstance(e, ', content)
    
    # 空の変数参照を修正
    content = re.sub(r'0\.114 \* \)', '0.114 * b)', content)
    content = re.sub(r'255 - \) \* factor\)', '255 - r) * factor)', content)
    content = re.sub(r'255 - \) \* factor\)', '255 - g) * factor)', content)
    content = re.sub(r'255 - \) \* factor\)', '255 - b) * factor)', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    """メイン処理"""
    # 構文エラーがあるファイルを特定
    problem_files = [
        'qt_theme_studio/services/import_service.py',
        'qt_theme_studio/utilities/accessibility_manager.py',
        'qt_theme_studio/utilities/japanese_file_handler.py',
        'qt_theme_studio/views/theme_gallery.py',
        'qt_theme_studio/views/zebra_editor.py'
    ]
    
    print(f"修正対象ファイル数: {len(problem_files)}")
    
    for file_path in problem_files:
        if glob.glob(file_path):
            print(f"修正中: {file_path}")
            
            try:
                fix_complete_syntax(file_path)
            except Exception as e:
                print(f"エラー: {file_path} - {e}")
    
    print("修正完了!")


if __name__ == '__main__':
    main()
