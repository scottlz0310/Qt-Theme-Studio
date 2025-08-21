#!/usr/bin/env python3
"""
Qt-Theme-Studio メインモジュール
エントリーポイント用の軽量ラッパー
"""

import sys
from pathlib import Path


def main() -> None:
    """メインエントリーポイント"""
    # プロジェクトルートのmain.pyを実行
    main_script = Path(__file__).parent.parent / "main.py"

    if main_script.exists():
        # main.pyを実行
        exec(main_script.read_text(encoding="utf-8"))
    else:
        print("❌ main.pyが見つかりません")
        sys.exit(1)


if __name__ == "__main__":
    main()
