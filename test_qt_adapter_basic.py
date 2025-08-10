#!/usr/bin/env python3
"""
Qt Adapterの基本動作テスト

このスクリプトは、Qt Adapterが正常に動作するかを確認するための簡単なテストです。
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qt_theme_studio.adapters.qt_adapter import QtAdapter, QtFrameworkNotFoundError

def test_qt_adapter():
    """Qt Adapterの基本機能をテストする"""
    print("Qt Adapter基本動作テスト開始...")
    
    try:
        # Qt Adapterインスタンス作成
        adapter = QtAdapter()
        print("✓ Qt Adapterインスタンスを作成しました")
        
        # フレームワーク検出テスト
        framework = adapter.detect_qt_framework()
        print(f"✓ 検出されたフレームワーク: {framework}")
        
        # モジュール取得テスト
        modules = adapter.get_qt_modules()
        print(f"✓ Qtモジュールを取得しました: {list(modules.keys())}")
        
        # フレームワーク情報取得テスト
        info = adapter.get_framework_info()
        print(f"✓ フレームワーク情報: {info}")
        
        # 初期化状態確認
        print(f"✓ 初期化状態: {adapter.is_initialized}")
        
        # QApplication作成テスト（実際のGUIアプリケーションではないので、作成のみ）
        print("QApplication作成テスト...")
        app = adapter.create_application("Test-App")
        print(f"✓ QApplicationを作成しました: {app}")
        
        print("\n✅ すべてのテストが成功しました！")
        return True
        
    except QtFrameworkNotFoundError as e:
        print(f"❌ Qtフレームワークエラー: {e}")
        print("PySide6、PyQt6、またはPyQt5をインストールしてください。")
        return False
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qt_adapter()
    sys.exit(0 if success else 1)