"""
pytest共通設定ファイル

このファイルには、すべてのテストで共有される設定とフィクスチャが含まれています。
"""

import os
import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# テスト用の環境変数設定
os.environ["QT_THEME_STUDIO_TESTING"] = "true"
os.environ["QT_THEME_STUDIO_LOG_LEVEL"] = "DEBUG"


# テスト用の設定
@pytest.fixture(scope="session")
def test_config() -> dict[str, Any]:
    """テスト用の基本設定"""
    return {
        "theme_dir": str(project_root / "themes"),
        "temp_dir": str(project_root / "tests" / "temp"),
        "log_level": "DEBUG",
        "testing": True
    }


@pytest.fixture(scope="session")
def sample_theme_data() -> dict[str, Any]:
    """サンプルテーマデータ"""
    return {
        "name": "Test Theme",
        "version": "1.0.0",
        "description": "テスト用テーマ",
        "colors": {
            "primary": "#007acc",
            "secondary": "#6c757d",
            "background": "#ffffff",
            "text": "#212529"
        },
        "fonts": {
            "default": "Arial",
            "size": 12
        }
    }


@pytest.fixture
def mock_qt_app() -> Generator[MagicMock, None, None]:
    """Qtアプリケーションのモック"""
    with patch("PySide6.QtWidgets.QApplication") as mock_app:
        mock_app.instance.return_value = MagicMock()
        yield mock_app


@pytest.fixture
def mock_theme_manager() -> Generator[MagicMock, None, None]:
    """qt-theme-managerのモック"""
    with patch("qt_theme_studio.adapters.theme_adapter.ThemeManager") as mock_manager:
        mock_manager.return_value = MagicMock()
        yield mock_manager


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """一時ディレクトリ"""
    return tmp_path


@pytest.fixture(autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """テスト環境の自動セットアップ"""
    # テスト前の処理
    yield
    # テスト後のクリーンアップ処理
