"""
Qtアダプターの単体テスト

Qtフレームワークとの統合をテストします
"""

from unittest.mock import Mock, patch

from qt_theme_studio.adapters.qt_adapter import QtAdapter


class TestQtAdapter:
    """QtAdapterクラスのテスト"""

    def setup_method(self) -> None:
        """各テストメソッドの前処理"""
        self.adapter = QtAdapter()

    def test_init(self) -> None:
        """初期化のテスト"""
        assert self.adapter is not None

    def test_detect_qt_framework(self) -> None:
        """Qtフレームワーク検出のテスト"""
        result = self.adapter.detect_qt_framework()
        assert isinstance(result, str)
        assert result in ["PySide6", "PyQt6", "PyQt5", "unknown"]

    def test_get_qt_modules(self) -> None:
        """Qtモジュール取得のテスト"""
        # 実際の実装では、detect_qt_frameworkが呼ばれる
        with patch.object(self.adapter, "_detected_framework", "PySide6"):
            result = self.adapter.get_qt_modules()
            assert isinstance(result, dict)
            assert "QtWidgets" in result

    def test_create_application(self) -> None:
        """アプリケーション作成のテスト"""
        # 完全にモック化して、実際のQtアプリケーションを作成しない
        with (
            patch.object(self.adapter, "_detected_framework", "PySide6"),
            patch.object(
                self.adapter,
                "_qt_modules",
                {"QtWidgets": Mock(), "QtCore": Mock(), "QtGui": Mock()},
            ),
            patch("sys.argv", ["test"]),
        ):
            # get_qt_modulesメソッドをモック化
            with patch.object(self.adapter, "get_qt_modules") as mock_get_modules:
                mock_get_modules.return_value = {
                    "QtWidgets": Mock(),
                    "QtCore": Mock(),
                    "QtGui": Mock(),
                }
                result = self.adapter.create_application("Test App")
                assert result is not None

    def test_get_framework_info(self) -> None:
        """フレームワーク情報取得のテスト"""
        result = self.adapter.get_framework_info()
        assert isinstance(result, dict)
        assert "name" in result
        assert "version" in result

    def test_is_initialized(self) -> None:
        """初期化状態の確認テスト"""
        # is_initializedはプロパティなので、()は不要
        assert self.adapter.is_initialized is False

        with patch.object(self.adapter, "_detected_framework", "PySide6"):
            with patch.object(self.adapter, "_qt_modules", {"QtWidgets": Mock()}):
                assert self.adapter.is_initialized is True

    def test_application(self) -> None:
        """アプリケーションインスタンス取得のテスト"""
        # applicationはプロパティなので、()は不要
        assert self.adapter.application is None

        mock_app = Mock()
        with patch.object(self.adapter, "_application", mock_app):
            assert self.adapter.application == mock_app
