#!/usr/bin/env python3
"""
print文をロガー呼び出しに一括変換するスクリプト
"""

import re
from pathlib import Path

def replace_prints_in_file(file_path: Path) -> int:
    """ファイル内のprint文をロガー呼び出しに変換"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # ファイルにロガーが定義されているかチェック
        has_logger = 'self.logger' in content or 'logger' in content
        
        if not has_logger:
            return 0
        
        # print文をロガー呼び出しに変換
        original_content = content
        
        # 成功メッセージ（✓）→ info
        content = re.sub(
            r'print\(f?"✓\s*([^"]+)"\)',
            r'self.logger.info(f"\1")',
            content
        )
        
        # 警告メッセージ（⚠）→ warning
        content = re.sub(
            r'print\(f?"⚠\s*([^"]+)"\)',
            r'self.logger.warning(f"\1")',
            content
        )
        
        # エラーメッセージ（❌）→ error
        content = re.sub(
            r'print\(f?"❌\s*([^"]+)"\)',
            r'self.logger.error(f"\1")',
            content
        )
        
        # デバッグメッセージ（数字.）→ debug
        content = re.sub(
            r'print\(f?"(\d+\.\s*[^"]+)"\)',
            r'self.logger.debug(f"\1")',
            content
        )
        
        # その他のprint文→ info
        content = re.sub(
            r'print\(f?"([^"]+)"\)',
            r'self.logger.info(f"\1")',
            content
        )
        
        # 変数を含むprint文→ info
        content = re.sub(
            r'print\(f"([^"]+)"\)',
            r'self.logger.info(f"\1")',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return 1
        return 0
    except Exception as e:
        self.logger.info(f"エラー: {file_path} - {e}")
        return 0

def main():
    """メイン処理"""
    project_root = Path(__file__).parent.parent
    python_files = list(project_root.rglob("*.py"))
    
    self.logger.info(f"Pythonファイル数: {len(python_files)}")
    
    fixed_count = 0
    for file_path in python_files:
        if "venv" in str(file_path) or ".git" in str(file_path):
            continue
        
        if replace_prints_in_file(file_path):
            self.logger.info(f"修正: {file_path.relative_to(project_root)}")
            fixed_count += 1
    
    self.logger.info(f"\n修正完了: {fixed_count}ファイル")

if __name__ == "__main__":
    main()
