"""
モックオブジェクトフィクスチャ

テストで使用するモックオブジェクトとヘルパー関数
"""

from typing import Any
from unittest.mock import Mock


def create_mock_widget() -> Mock:
    """モックウィジェットを作成"""
    mock_widget = Mock()
    mock_widget.objectName.return_value = "test_widget"
    mock_widget.styleSheet.return_value = ""
    mock_widget.setStyleSheet = Mock()
    mock_widget.children.return_value = []
    return mock_widget


def create_mock_application() -> Mock:
    """モックQtアプリケーションを作成"""
    mock_app = Mock()
    mock_app.instance.return_value = mock_app
    mock_app.styleSheet.return_value = ""
    mock_app.setStyleSheet = Mock()
    return mock_app


def create_mock_theme_manager() -> Mock:
    """モックテーママネージャーを作成"""
    mock_manager = Mock()
    mock_manager.load_theme.return_value = {"name": "Test Theme"}
    mock_manager.apply_theme.return_value = True
    mock_manager.get_theme_names.return_value = ["Theme1", "Theme2"]
    mock_manager.save_theme.return_value = True
    return mock_manager


def create_mock_theme_data() -> dict[str, Any]:
    """モックテーマデータを作成"""
    return {
        "name": "Mock Theme",
        "version": "1.0.0",
        "colors": {
            "primary": "#007acc",
            "background": "#ffffff"
        }
    }


def create_mock_error_handler() -> Mock:
    """モックエラーハンドラーを作成"""
    mock_handler = Mock()
    mock_handler.handle_error.return_value = True
    mock_handler.log_error = Mock()
    mock_handler.show_error_dialog = Mock()
    return mock_handler
