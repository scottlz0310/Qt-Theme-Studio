"""
Qt-Theme-Studio 高機能ロガー

構造化ログ、パフォーマンス測定、エラートラッキング機能を提供します。
"""

import json
import logging
import time
import traceback
from contextlib import contextmanager
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional, Union


class LogLevel(Enum):
    """ログレベルの定義"""
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class LogCategory(Enum):
    """ログカテゴリの定義"""
    GENERAL = auto()
    UI = auto()
    THEME = auto()
    PERFORMANCE = auto()
    ERROR = auto()
    SECURITY = auto()


class LogContext:
    """ログコンテキスト情報"""

    def __init__(self, **kwargs):
        self.context = kwargs
        self.timestamp = datetime.now()
        self.session_id = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """セッションIDを生成"""
        return f"session_{int(time.time())}"

    def add_context(self, **kwargs):
        """コンテキスト情報を追加"""
        self.context.update(kwargs)

    def to_dict(self) -> dict[str, Any]:
        """辞書形式でコンテキスト情報を取得"""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            **self.context
        }


class StructuredFormatter(logging.Formatter):
    """構造化ログフォーマッター"""

    def format(self, record: logging.LogRecord) -> str:
        """ログレコードを構造化形式でフォーマット"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # カスタム属性を追加
        if hasattr(record, "category"):
            log_entry["category"] = record.category.value if hasattr(record.category, "value") else str(record.category)

        if hasattr(record, "context"):
            log_entry["context"] = record.context.to_dict() if hasattr(record.context, "to_dict") else record.context

        if hasattr(record, "performance_data"):
            log_entry["performance"] = record.performance_data

        return json.dumps(log_entry, ensure_ascii=False, indent=2)


class QtThemeStudioLogger:
    """Qt-Theme-Studio専用ロガー"""

    def __init__(self, name: str = "qt_theme_studio"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # ハンドラーの設定
        self._setup_handlers()

        # パフォーマンス測定用
        self._performance_timers = {}

    def _setup_handlers(self):
        """ログハンドラーを設定"""
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)

        # ファイルハンドラー(構造化ログ)
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log",
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        structured_formatter = StructuredFormatter()
        file_handler.setFormatter(structured_formatter)

        # ハンドラーを追加
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def _log_with_category(self, level: int, message: str, category: LogCategory,
                          context: Optional[LogContext] = None, **kwargs):
        """カテゴリ付きでログを出力"""
        extra = {"category": category}
        if context:
            extra["context"] = context

        # パフォーマンスデータがある場合
        if "performance_data" in kwargs:
            extra["performance_data"] = kwargs["performance_data"]

        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, category: LogCategory = LogCategory.GENERAL,
              context: Optional[LogContext] = None, **kwargs):
        """デバッグログ"""
        self._log_with_category(logging.DEBUG, message, category, context, **kwargs)

    def info(self, message: str, category: LogCategory = LogCategory.GENERAL,
             context: Optional[LogContext] = None, **kwargs):
        """情報ログ"""
        self._log_with_category(logging.INFO, message, category, context, **kwargs)

    def warning(self, message: str, category: LogCategory = LogCategory.GENERAL,
                context: Optional[LogContext] = None, **kwargs):
        """警告ログ"""
        self._log_with_category(logging.WARNING, message, category, context, **kwargs)

    def error(self, message: str, category: LogCategory = LogCategory.ERROR,
              context: Optional[LogContext] = None, **kwargs):
        """エラーログ"""
        self._log_with_category(logging.ERROR, message, category, context, **kwargs)

    def critical(self, message: str, category: LogCategory = LogCategory.ERROR,
                 context: Optional[LogContext] = None, **kwargs):
        """重大エラーログ"""
        self._log_with_category(logging.CRITICAL, message, category, context, **kwargs)

    def log_theme_operation(self, operation: str, theme_name: str,
                           context: Optional[LogContext] = None, **kwargs):
        """テーマ操作のログ"""
        message = f"テーマ操作: {operation} - {theme_name}"
        self.info(message, LogCategory.THEME, context, **kwargs)

    def log_ui_operation(self, operation: str, widget_name: str,
                         context: Optional[LogContext] = None, **kwargs):
        """UI操作のログ"""
        message = f"UI操作: {operation} - {widget_name}"
        self.info(message, LogCategory.UI, context, **kwargs)

    def log_performance(self, operation: str, duration: float,
                        context: Optional[LogContext] = None, **kwargs):
        """パフォーマンスログ"""
        message = f"パフォーマンス: {operation} - {duration:.3f}秒"
        self.info(message, LogCategory.PERFORMANCE, context,
                 performance_data={"operation": operation, "duration": duration}, **kwargs)

    @contextmanager
    def performance_timer(self, operation: str, context: Optional[LogContext] = None):
        """パフォーマンス測定用コンテキストマネージャー"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.log_performance(operation, duration, context)

    def log_exception(self, message: str, exception: Exception,
                      context: Optional[LogContext] = None, **kwargs):
        """例外ログ"""
        error_details = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc()
        }

        self.error(f"{message}: {exception!s}", LogCategory.ERROR, context,
                  performance_data=error_details, **kwargs)


# グローバルロガーインスタンス
_global_logger = None


def get_logger(name: str = "qt_theme_studio") -> QtThemeStudioLogger:
    """ロガーインスタンスを取得"""
    global _global_logger
    if _global_logger is None:
        _global_logger = QtThemeStudioLogger(name)
    return _global_logger


def setup_logging(log_level: LogLevel = LogLevel.INFO,
                  log_file: Optional[Union[str, Path]] = None):
    """ログ設定を初期化"""
    logger = get_logger()

    # ログレベルの設定
    level_map = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
        LogLevel.CRITICAL: logging.CRITICAL,
    }

    logger.logger.setLevel(level_map[log_level])

    # カスタムログファイルの設定
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        structured_formatter = StructuredFormatter()
        file_handler.setFormatter(structured_formatter)

        logger.logger.addHandler(file_handler)


# 便利な関数
def log_function_call(func_name: str, **kwargs):
    """関数呼び出しのログ"""
    logger = get_logger()
    context = LogContext(function=func_name, **kwargs)
    logger.debug(f"関数呼び出し: {func_name}", LogCategory.GENERAL, context)


def log_user_action(action: str, user_id: Optional[str] = None, **kwargs):
    """ユーザーアクションのログ"""
    logger = get_logger()
    context = LogContext(action=action, user_id=user_id, **kwargs)
    logger.info(f"ユーザーアクション: {action}", LogCategory.UI, context)


def log_file_operation(operation: str, file_path: str, **kwargs):
    """ファイル操作のログ"""
    logger = get_logger()
    context = LogContext(operation=operation, file_path=file_path, **kwargs)
    logger.info(f"ファイル操作: {operation} - {file_path}", LogCategory.GENERAL, context)


def log_application_startup():
    """アプリケーション起動のログ"""
    logger = get_logger()
    context = LogContext(event="application_startup")
    logger.info("アプリケーション起動", LogCategory.GENERAL, context)


def log_application_shutdown():
    """アプリケーション終了のログ"""
    logger = get_logger()
    context = LogContext(event="application_shutdown")
    logger.info("アプリケーション終了", LogCategory.GENERAL, context)

