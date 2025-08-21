"""
ロガーの単体テスト

Qt-Theme-Studioの高機能ロガーのテストを行います
"""

import json
import logging
from datetime import datetime
from unittest.mock import Mock, patch

from qt_theme_studio.logger import (
    LogCategory,
    LogContext,
    LogLevel,
    QtThemeStudioLogger,
    StructuredFormatter,
    get_logger,
    log_application_shutdown,
    log_application_startup,
    log_file_operation,
    log_function_call,
    log_user_action,
    setup_logging,
)


class TestLogLevel:
    """LogLevel列挙型のテスト"""

    def test_log_level_values(self):
        """ログレベルの値が正しく定義されているかテスト"""
        assert LogLevel.DEBUG.value == 1
        assert LogLevel.INFO.value == 2
        assert LogLevel.WARNING.value == 3
        assert LogLevel.ERROR.value == 4
        assert LogLevel.CRITICAL.value == 5


class TestLogCategory:
    """LogCategory列挙型のテスト"""

    def test_log_category_values(self):
        """ログカテゴリの値が正しく定義されているかテスト"""
        assert LogCategory.GENERAL.value == 1
        assert LogCategory.UI.value == 2
        assert LogCategory.THEME.value == 3
        assert LogCategory.PERFORMANCE.value == 4
        assert LogCategory.ERROR.value == 5
        assert LogCategory.SECURITY.value == 6


class TestLogContext:
    """LogContextクラスのテスト"""

    def test_init(self):
        """初期化のテスト"""
        context = LogContext(test_key="test_value")
        assert context.context["test_key"] == "test_value"
        assert isinstance(context.timestamp, datetime)
        assert context.session_id.startswith("session_")

    def test_add_context(self):
        """コンテキスト追加のテスト"""
        context = LogContext(initial_key="initial_value")
        context.add_context(new_key="new_value")

        assert context.context["initial_key"] == "initial_value"
        assert context.context["new_key"] == "new_value"

    def test_to_dict(self):
        """辞書変換のテスト"""
        context = LogContext(test_key="test_value")
        result = context.to_dict()

        assert "session_id" in result
        assert "timestamp" in result
        assert result["test_key"] == "test_value"
        assert isinstance(result["timestamp"], str)


class TestStructuredFormatter:
    """StructuredFormatterクラスのテスト"""

    def test_format_basic(self):
        """基本的なフォーマットのテスト"""
        formatter = StructuredFormatter()

        # 実際のLogRecordオブジェクトを作成
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_module.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # 必要な属性を設定
        record.funcName = "test_function"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "test_module"
        assert log_data["function"] == "test_function"
        assert log_data["line"] == 42

    def test_format_with_category(self):
        """カテゴリ付きフォーマットのテスト"""
        formatter = StructuredFormatter()

        # 実際のLogRecordオブジェクトを作成
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_module.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # 必要な属性を設定
        record.funcName = "test_function"
        record.category = LogCategory.THEME

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["category"] == 3  # LogCategory.THEME.value

    def test_format_with_context(self):
        """コンテキスト付きフォーマットのテスト"""
        formatter = StructuredFormatter()

        # 実際のLogRecordオブジェクトを作成
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_module.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # 必要な属性を設定
        record.funcName = "test_function"

        # コンテキストを設定
        context = LogContext(test_key="test_value")
        record.context = context

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "context" in log_data
        assert log_data["context"]["test_key"] == "test_value"


class TestQtThemeStudioLogger:
    """QtThemeStudioLoggerクラスのテスト"""

    def setup_method(self):
        """各テストメソッドの前処理"""
        # 既存のハンドラーをクリア
        import logging

        logging.getLogger("test_logger").handlers.clear()

        self.logger = QtThemeStudioLogger("test_logger")

    def test_init(self):
        """初期化のテスト"""
        assert self.logger.name == "test_logger"
        assert self.logger.logger.name == "test_logger"
        assert self.logger.logger.level == logging.DEBUG

    def test_debug_log(self):
        """デバッグログのテスト"""
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.debug("Debug message", LogCategory.THEME)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == logging.DEBUG
            assert call_args[0][1] == "Debug message"
            assert call_args[1]["extra"]["category"] == LogCategory.THEME

    def test_info_log(self):
        """情報ログのテスト"""
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.info("Info message", LogCategory.UI)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == logging.INFO
            assert call_args[0][1] == "Info message"
            assert call_args[1]["extra"]["category"] == LogCategory.UI

    def test_warning_log(self):
        """警告ログのテスト"""
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.warning("Warning message", LogCategory.PERFORMANCE)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == logging.WARNING
            assert call_args[0][1] == "Warning message"
            assert call_args[1]["extra"]["category"] == LogCategory.PERFORMANCE

    def test_error_log(self):
        """エラーログのテスト"""
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.error("Error message", LogCategory.ERROR)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == logging.ERROR
            assert call_args[0][1] == "Error message"
            assert call_args[1]["extra"]["category"] == LogCategory.ERROR

    def test_critical_log(self):
        """重大エラーログのテスト"""
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.critical("Critical message", LogCategory.ERROR)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == logging.CRITICAL
            assert call_args[0][1] == "Critical message"
            assert call_args[1]["extra"]["category"] == LogCategory.ERROR

    def test_log_with_context(self):
        """コンテキスト付きログのテスト"""
        context = LogContext(test_key="test_value")

        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.info("Message with context", LogCategory.GENERAL, context)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[1]["extra"]["context"] == context

    def test_log_theme_operation(self):
        """テーマ操作ログのテスト"""
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.log_theme_operation("load", "test_theme")

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert "テーマ操作: load - test_theme" in call_args[0][1]
            assert call_args[1]["extra"]["category"] == LogCategory.THEME

    def test_log_ui_operation(self):
        """UI操作ログのテスト"""
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.log_ui_operation("click", "test_button")

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert "UI操作: click - test_button" in call_args[0][1]
            assert call_args[1]["extra"]["category"] == LogCategory.UI

    def test_log_performance(self):
        """パフォーマンスログのテスト"""
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.log_performance("test_operation", 1.5)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            expected_msg = "パフォーマンス: test_operation - 1.500秒"
            assert expected_msg in call_args[0][1]
            perf_data = call_args[1]["extra"]["performance_data"]
            assert perf_data["operation"] == "test_operation"
            assert call_args[1]["extra"]["performance_data"]["duration"] == 1.5

    def test_performance_timer(self):
        """パフォーマンスタイマーのテスト"""
        with patch.object(self.logger, "log_performance") as mock_log_perf:
            with self.logger.performance_timer("test_operation"):
                pass  # 何もしない

            mock_log_perf.assert_called_once()
            call_args = mock_log_perf.call_args
            assert call_args[0][0] == "test_operation"
            assert isinstance(call_args[0][1], float)

    def test_log_exception(self):
        """例外ログのテスト"""
        exception = ValueError("Test exception")

        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.log_exception("Test error", exception)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert "Test error: Test exception" in call_args[0][1]
            assert call_args[1]["extra"]["category"] == LogCategory.ERROR


class TestLoggerFunctions:
    """ロガー関数のテスト"""

    def setup_method(self):
        """各テストメソッドの前処理"""
        # グローバルロガーをリセット
        import qt_theme_studio.logger

        qt_theme_studio.logger._global_logger = None

    def test_get_logger(self):
        """get_logger関数のテスト"""
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")

        assert logger1 is logger2  # シングルトン
        assert logger1.name == "test_logger"

    def test_setup_logging(self):
        """setup_logging関数のテスト"""
        with patch("qt_theme_studio.logger.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            setup_logging(LogLevel.DEBUG)

            mock_logger.logger.setLevel.assert_called_once_with(logging.DEBUG)

    def test_log_function_call(self):
        """log_function_call関数のテスト"""
        with patch("qt_theme_studio.logger.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_function_call("test_function", param1="value1")

            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args
            assert "関数呼び出し: test_function" in call_args[0][0]
            # カテゴリは第2引数として渡される
            assert call_args[0][1] == LogCategory.GENERAL

    def test_log_user_action(self):
        """log_user_action関数のテスト"""
        with patch("qt_theme_studio.logger.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_user_action("test_action", user_id="user123")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "ユーザーアクション: test_action" in call_args[0][0]
            # カテゴリは第2引数として渡される
            assert call_args[0][1] == LogCategory.UI

    def test_log_file_operation(self):
        """log_file_operation関数のテスト"""
        with patch("qt_theme_studio.logger.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_file_operation("read", "/path/to/file.txt")

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert "ファイル操作: read - /path/to/file.txt" in call_args[0][0]
            # カテゴリは第2引数として渡される
            assert call_args[0][1] == LogCategory.GENERAL

    def test_log_application_startup(self):
        """log_application_startup関数のテスト"""
        with patch("qt_theme_studio.logger.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_application_startup()

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[0][0] == "アプリケーション起動"
            # カテゴリは第2引数として渡される
            assert call_args[0][1] == LogCategory.GENERAL

    def test_log_application_shutdown(self):
        """log_application_shutdown関数のテスト"""
        with patch("qt_theme_studio.logger.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_application_shutdown()

            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args
            assert call_args[0][0] == "アプリケーション終了"
            # カテゴリは第2引数として渡される
            assert call_args[0][1] == LogCategory.GENERAL
