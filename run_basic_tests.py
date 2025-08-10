#!/usr/bin/env python3
"""
Qt Adapterの基本テスト実行スクリプト

pytestを使わずに基本的なテストを実行します。
"""

import sys
import os
import unittest.mock as mock
from unittest.mock import patch, MagicMock

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qt_theme_studio.adapters.qt_adapter import QtAdapter, QtFrameworkNotFoundError

def test_qt_adapter_basic():
    """Qt Adapterの基本機能テスト"""
    print("Qt Adapter基本機能テスト開始...")
    
    # 初期化テスト
    adapter = QtAdapter()
    assert adapter._detected_framework is None
    assert adapter._qt_modules is None
    assert adapter._application is None
    assert not adapter.is_initialized
    print("✓ 初期化テスト成功")
    
    # フレームワーク検出テスト（モック使用）
    with patch('builtins.__import__') as mock_import:
        # PySide6が検出される場合
        def side_effect(name):
            if name == 'PySide6':
                return MagicMock()
            raise ImportError(f"No module named '{name}'")
        
        mock_import.side_effect = side_effect
        
        framework = adapter.detect_qt_framework()
        assert framework == 'PySide6'
        assert adapter._detected_framework == 'PySide6'
        print("✓ PySide6検出テスト成功")
    
    # エラーハンドリングテスト
    adapter2 = QtAdapter()
    with patch('builtins.__import__') as mock_import:
        mock_import.side_effect = ImportError("No module found")
        
        try:
            adapter2.detect_qt_framework()
            assert False, "例外が発生するはずです"
        except QtFrameworkNotFoundError as e:
            assert "利用可能なQtフレームワークが見つかりません" in str(e)
            print("✓ エラーハンドリングテスト成功")
    
    # モジュール取得テスト
    adapter3 = QtAdapter()
    with patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.detect_qt_framework') as mock_detect:
        mock_detect.return_value = 'PySide6'
        
        # PySide6モジュールをモック
        mock_qtwidgets = MagicMock()
        mock_qtcore = MagicMock()
        mock_qtgui = MagicMock()
        
        with patch.dict('sys.modules', {
            'PySide6': MagicMock(),
            'PySide6.QtWidgets': mock_qtwidgets,
            'PySide6.QtCore': mock_qtcore,
            'PySide6.QtGui': mock_qtgui,
        }):
            modules = adapter3.get_qt_modules()
            
            assert modules['framework'] == 'PySide6'
            assert 'QtWidgets' in modules
            assert 'QtCore' in modules
            assert 'QtGui' in modules
            print("✓ モジュール取得テスト成功")
    
    print("\n✅ すべての基本テストが成功しました！")
    return True

def test_qt_adapter_frameworks():
    """各フレームワークの検出テスト"""
    print("\n各フレームワーク検出テスト開始...")
    
    frameworks = ['PySide6', 'PyQt6', 'PyQt5']
    
    for target_framework in frameworks:
        adapter = QtAdapter()
        
        with patch('builtins.__import__') as mock_import:
            def side_effect(name):
                if name == target_framework:
                    return MagicMock()
                raise ImportError(f"No module named '{name}'")
            
            mock_import.side_effect = side_effect
            
            framework = adapter.detect_qt_framework()
            assert framework == target_framework
            print(f"✓ {target_framework}検出テスト成功")
    
    print("✅ フレームワーク検出テストが完了しました！")
    return True

if __name__ == "__main__":
    try:
        success1 = test_qt_adapter_basic()
        success2 = test_qt_adapter_frameworks()
        
        if success1 and success2:
            print("\n🎉 すべてのテストが成功しました！")
            sys.exit(0)
        else:
            print("\n❌ テストに失敗しました")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ テスト実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)