#!/usr/bin/env python3
"""
メインウィンドウとコンポーネント統合のテスト

このスクリプトは、task16で実装したメインウィンドウとコンポーネント統合機能をテストします。
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.adapters.theme_adapter import ThemeAdapter
from qt_theme_studio.config.settings import ApplicationSettings
from qt_theme_studio.views.main_window import MainWindow
from qt_theme_studio.views.theme_editor import ThemeEditor
from qt_theme_studio.views.zebra_editor import ZebraEditor
from qt_theme_studio.views.preview import PreviewWindow
from qt_theme_studio.logger import get_logger, LogCategory


def test_component_integration():
    """コンポーネント統合をテストします"""
    logger = get_logger()
    logger.info("コンポーネント統合テストを開始します", LogCategory.TEST)
    
    try:
        # Qt アダプターを初期化
        qt_adapter = QtAdapter()
        qt_modules = qt_adapter.get_qt_modules()
        
        # アプリケーションを作成
        app = qt_modules['QtWidgets'].QApplication(sys.argv)
        
        # テーマアダプターを初期化
        theme_adapter = ThemeAdapter()
        
        # 設定管理を初期化
        settings = ApplicationSettings()
        
        # メインウィンドウを作成
        main_window = MainWindow(qt_adapter, theme_adapter, settings)
        
        # コンポーネントを作成
        theme_editor = ThemeEditor(qt_adapter, theme_adapter)
        zebra_editor = ZebraEditor()
        preview_window = PreviewWindow(qt_adapter, theme_adapter)
        
        # コンポーネントを統合
        main_window.integrate_components(theme_editor, zebra_editor, preview_window)
        
        # テストテーマデータを設定
        test_theme_data = {
            'name': 'テスト統合テーマ',
            'version': '1.0.0',
            'colors': {
                'background': '#f0f0f0',
                'text': '#333333',
                'primary': '#007acc',
                'secondary': '#6c757d'
            },
            'fonts': {
                'default': {
                    'family': 'Arial',
                    'size': 14,
                    'bold': False,
                    'italic': False
                }
            },
            'properties': {
                'test_property': 'test_value'
            }
        }
        
        # テーマデータを設定
        main_window.set_theme_data(test_theme_data)
        
        # メインウィンドウを表示
        main_window.show()
        
        logger.info("コンポーネント統合テストが完了しました", LogCategory.TEST)
        logger.info("メインウィンドウが表示されました。手動でテストしてください。", LogCategory.TEST)
        
        # アプリケーションを実行
        return app.exec()
        
    except Exception as e:
        logger.error(f"コンポーネント統合テストでエラーが発生しました: {str(e)}", LogCategory.TEST)
        return 1


if __name__ == "__main__":
    exit_code = test_component_integration()
    sys.exit(exit_code)