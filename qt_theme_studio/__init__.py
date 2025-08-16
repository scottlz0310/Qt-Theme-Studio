"""
Qt-Theme-Studio: 統合テーマエディターGUIアプリケーション

Qtアプリケーション（PyQt5/PyQt6/PySide6）向けの統合テーマエディターです。
qt-theme-managerライブラリを基盤として、直感的なビジュアルインターフェースで
テーマの作成・編集・管理を行います。
"""

__version__ = "0.1.0"
__author__ = "Qt-Theme-Studio Team"
__description__ = "統合テーマエディターGUIアプリケーション"

from .error_handler import ErrorHandler

# エラーハンドリングとログシステムのインポート
from .exceptions import (
    AccessibilityError,
    ApplicationCrashError,
    ConfigurationError,
    ExportError,
    ImportError,
    PreviewError,
    QtFrameworkNotFoundError,
    ThemeLoadError,
    ThemeSaveError,
    ThemeStudioException,
    ThemeValidationError,
)
from .logger import LogCategory, Logger, LogLevel, get_logger, setup_logging
from .logging_utils import (
    LogContext,
    configure_exception_logging,
    log_application_shutdown,
    log_application_startup,
    log_file_operation,
    log_function_call,
    log_performance,
    log_theme_operation,
    log_user_action,
)

# メインアプリケーションクラスのインポート（main.pyが実装されるまでコメントアウト）
# from .main import ThemeStudioApplication

__all__ = [
    # "ThemeStudioApplication",
    "__version__",
    "__author__",
    "__description__",
    # 例外クラス
    "ThemeStudioException",
    "QtFrameworkNotFoundError",
    "ThemeLoadError",
    "ThemeSaveError",
    "ThemeValidationError",
    "ExportError",
    "ImportError",
    "ConfigurationError",
    "PreviewError",
    "AccessibilityError",
    "ApplicationCrashError",
    # エラーハンドラー
    "ErrorHandler",
    # ログシステム
    "Logger",
    "LogLevel",
    "LogCategory",
    "get_logger",
    "setup_logging",
    # ログユーティリティ
    "log_function_call",
    "log_performance",
    "log_user_action",
    "log_theme_operation",
    "log_file_operation",
    "LogContext",
    "configure_exception_logging",
    "log_application_startup",
    "log_application_shutdown",
]  # テスト用コメント
