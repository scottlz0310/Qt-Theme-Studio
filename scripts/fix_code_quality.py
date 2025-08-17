#!/usr/bin/env python3
"""
コード品質の問題を一括修正するスクリプト
"""

import os
import re
import glob


def fix_whitespace_issues(file_path):
    """空白行の問題を修正"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 空白行の空白を削除
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # 空白のみの行は空行にする
        if line.strip() == '':
            fixed_lines.append('')
        else:
            # 行末の空白を削除
            fixed_lines.append(line.rstrip())
    
    # ファイル末尾に改行を追加
    if fixed_lines and fixed_lines[-1] != '':
        fixed_lines.append('')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))


def fix_long_lines(file_path):
    """長い行を修正(基本的な修正のみ)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # 88文字を超える行の基本的な修正
        if len(line) > 88:
            # コメント行の場合
            if line.strip().startswith('#'):
                # コメントを分割
                indent = len(line) - len(line.lstrip())
                prefix = ' ' * indent + '# '
                comment_text = line.strip()[1:].strip()
                
                if len(prefix + comment_text) > 88:
                    # 長いコメントを分割
                    words = comment_text.split()
                    current_line = prefix
                    
                    for word in words:
                        if len(current_line + word + ' ') <= 88:
                            if current_line == prefix:
                                current_line += word
                            else:
                                current_line += ' ' + word
                        else:
                            fixed_lines.append(current_line)
                            current_line = prefix + word
                    
                    if current_line != prefix:
                        fixed_lines.append(current_line)
                    continue
            
            # 文字列リテラルの場合の基本的な修正
            if '"""' in line or "'''" in line:
                fixed_lines.append(line)
                continue
                
            # その他の長い行はそのまま(手動修正が必要)
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))


def fix_comparison_issues(file_path):
    """比較の問題を修正"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # == False を is False に変更
    content = re.sub(r'== False\b', 'is False', content)
    # == True を is True に変更
    content = re.sub(r'== True\b', 'is True', content)
    # != False を is not False に変更
    content = re.sub(r'!= False\b', 'is not False', content)
    # != True を is not True に変更
    content = re.sub(r'!= True\b', 'is not True', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def fix_f_string_issues(file_path):
    """f-stringの問題を修正"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # f-stringでプレースホルダーがない場合を検出
        if re.search(r'f["\'][^"\']*["\']', line) and '{' not in line:
            # f-stringのfを削除
            line = re.sub(r'\bf(["\'])', r'\1', line)
        
        fixed_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))


def main():
    """メイン処理"""
    # テストファイルを取得
    test_files = glob.glob('tests/test_*.py')
    
    print(f"修正対象ファイル数: {len(test_files)}")
    
    for file_path in test_files:
        print(f"修正中: {file_path}")
        
        # 各種修正を適用
        fix_whitespace_issues(file_path)
        fix_long_lines(file_path)
        fix_comparison_issues(file_path)
        fix_f_string_issues(file_path)
    
    print("修正完了!")


if __name__ == '__main__':
    main()