"""
Qt-Theme-Studio ログシステムのテスト

このモジュールは、Qt-Theme-Studioのログシステムをテストします。
"""

import json
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest

from qt_theme_studio.logger import (
    JapaneseFormatter,
    LogCategory,
    Logger,
    get_logger,
    setup_logging,
)
from qt_theme_studio.logging_utils import (
    LogContext,
    log_function_call,
    log_performance,
    log_user_action,
)


class TestJapaneseFormatter:
    """JapaneseFormatterのテスト"""

    def test_format_basic_message(self):
        """基本的なメッセージフォーマットのテスト"""
        
        formatter = JapaneseFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="テストメッセージ",
            args=(),
            exc_info=None
        )
        record.category = LogCategory.SYSTEM.value

        formatted = formatter.format(record)

        assert "情報" in formatted
        assert "システム" in formatted
        assert "テストメッセージ" in formatted

    def test_format_with_exception(self):
        """例外情報付きフォーマットのテスト"""
        
        formatter = JapaneseFormatter()

        try:
            raise ValueError("テスト例外")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="エラーが発生しました",
                args=(),
                exc_info=sys.exc_info()  # 実際の例外情報を設定
            )
            record.category = LogCategory.ERROR.value

            formatted = formatter.format(record)

            assert "エラー" in formatted
            assert "例外詳細" in formatted
            assert "ValueError" in formatted


class TestLogger:
    """Loggerクラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = Logger("test_logger", self.temp_dir)

    def test_logger_initialization(self):
        """ロガー初期化のテスト"""
        assert self.logger.name == "test_logger"
        assert self.logger.log_directory == Path(self.temp_dir)
        assert self.logger.log_directory.exists()

    def test_basic_logging(self):
        """基本的なログ出力のテスト"""
        self.logger.info("テスト情報メッセージ")
        self.logger.warning("テスト警告メッセージ")
        self.logger.error("テストエラーメッセージ")

        # ログファイルが作成されることを確認
        log_file = self.logger.log_directory / "qt_theme_studio.log"
        assert log_file.exists()

    def test_log_with_category(self):
        """カテゴリ付きログのテスト"""
        self.logger.info("テストメッセージ", LogCategory.USER_ACTION)

        # ログファイルの内容を確認
        log_file = self.logger.log_directory / "qt_theme_studio.log"
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "ユーザー操作" in content

    def test_log_error_with_exception(self):
        """例外付きエラーログのテスト"""
        try:
            raise ValueError("テスト例外")
        except ValueError as e:
            self.logger.log_error("例外が発生しました", e)

        # エラーログファイルが作成されることを確認
        error_log_file = self.logger.log_directory / "errors.log"
        assert error_log_file.exists()

    def test_log_user_action(self):
        """ユーザー操作ログのテスト"""
        action = "テーマを保存"
        details = {"theme_name": "テストテーマ", "file_path": "/test/path"}

        self.logger.log_user_action(action, details)

        # ユーザー操作履歴に追加されることを確認
        history = self.logger.get_user_action_history()
        assert len(history) == 1
        assert history[0]["action"] == action
        assert history[0]["details"] == details

        # ユーザー操作ログファイルが作成されることを確認
        user_action_log_file = self.logger.log_directory / "user_actions.log"
        assert user_action_log_file.exists()

    def test_performance_timer(self):
        """パフォーマンス測定のテスト"""
        operation = "テスト操作"

        self.logger.start_performance_timer(operation)
        time.sleep(0.1)  # 0.1秒待機
        duration = self.logger.end_performance_timer(operation)

        assert duration >= 0.1

        # パフォーマンスログファイルが作成されることを確認
        performance_log_file = self.logger.log_directory / "performance.log"
        assert performance_log_file.exists()

    def test_log_theme_operation(self):
        """テーマ操作ログのテスト"""
        operation = "テーマ読み込み"
        theme_name = "テストテーマ"

        self.logger.log_theme_operation(operation, theme_name)

        # ログファイルの内容を確認
        log_file = self.logger.log_directory / "qt_theme_studio.log"
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert operation in content
            assert theme_name in content

    def test_log_file_operation(self):
        """ファイル操作ログのテスト"""
        operation = "ファイル保存"
        file_path = "/test/file.json"

        self.logger.log_file_operation(operation, file_path, success=True)

        # ログファイルの内容を確認
        log_file = self.logger.log_directory / "qt_theme_studio.log"
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert operation in content
            assert file_path in content
            assert "成功" in content

    def test_export_logs(self):
        """ログエクスポートのテスト"""
        # いくつかのログを出力
        self.logger.info("テストメッセージ1")
        self.logger.log_user_action("テスト操作", {"key": "value"})

        # エクスポート
        export_file = Path(self.temp_dir) / "exported_logs.json"
        result = self.logger.export_logs(str(export_file))

        assert result is True
        assert export_file.exists()

        # エクスポートされたファイルの内容を確認
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert "export_timestamp" in data
            assert "user_actions" in data
            assert "log_files" in data


class TestLoggingUtils:
    """ログユーティリティのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        # グローバルロガーをテスト用に設定
        with patch('qt_theme_studio.logging_utils.get_logger') as mock_get_logger:
            self.mock_logger = MagicMock()
            mock_get_logger.return_value = self.mock_logger

    def test_log_function_call_decorator(self):
        """関数呼び出しログデコレーターのテスト"""
        @log_function_call(LogCategory.SYSTEM)
        def test_function(x, y):
            return x + y

        with patch('qt_theme_studio.logging_utils.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            result = test_function(1, 2)

            assert result == 3
            assert mock_logger.debug.called

    def test_log_performance_decorator(self):
        """パフォーマンスログデコレーターのテスト"""
        @log_performance("テスト操作")
        def test_function():
            time.sleep(0.01)
            return "完了"

        with patch('qt_theme_studio.logging_utils.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            result = test_function()

            assert result == "完了"
            assert mock_logger.start_performance_timer.called
            assert mock_logger.end_performance_timer.called

    def test_log_user_action_decorator(self):
        """ユーザー操作ログデコレーターのテスト"""
        @log_user_action("テストアクション")
        def test_function(param1, param2="default"):
            return "{param1}_{param2}"

        with patch('qt_theme_studio.logging_utils.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            result = test_function("test", param2="value")

            assert result == "test_value"
            assert mock_logger.log_user_action.called

    def test_log_context_manager(self):
        """ログコンテキストマネージャーのテスト"""
        with patch('qt_theme_studio.logging_utils.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            with LogContext("テスト操作", LogCategory.SYSTEM) as ctx:
                ctx.log("中間処理")
                time.sleep(0.01)

            # デバッグログが呼ばれることを確認
            assert mock_logger.debug.call_count >= 2  # 開始と終了

    def test_log_context_manager_with_exception(self):
        """例外発生時のログコンテキストマネージャーのテスト"""
        with patch('qt_theme_studio.logging_utils.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            with pytest.raises(ValueError):
                with LogContext("テスト操作", LogCategory.SYSTEM):
                    raise ValueError("テスト例外")

            # エラーログが呼ばれることを確認
            assert mock_logger.error.called


class TestGlobalLogger:
    """グローバルロガーのテスト"""

    def test_get_logger_singleton(self):
        """グローバルロガーのシングルトン動作のテスト"""
        logger1 = get_logger()
        logger2 = get_logger()

        assert logger1 is logger2

    def test_setup_logging(self):
        """ログシステム初期化のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = setup_logging(temp_dir, "DEBUG")

            assert logger is not None
            assert logger.log_directory == Path(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
