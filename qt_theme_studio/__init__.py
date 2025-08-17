"""
Qt-Theme-Studio: 統合テーマエディターGUIアプリケーション

Qtアプリケーション(PyQt5/PyQt6/PySide6)向けの統合テーマエディターです。
qt-theme-managerライブラリを基盤として、直感的なビジュアルインターフェースで
テーマの作成・編集・管理を行います。
"""

__version__ = "0.1.0"
__author__ = "Qt-Theme-Studio Team"
__description__ = "統合テーマエディターGUIアプリケーション"

# アダプターのインポート
from .adapters.qt_adapter import QtAdapter

# カスタム例外クラスのインポート
from .adapters.theme_adapter import (
    ThemeAdapter,
    ThemeExportError,
    ThemeLoadError,
    ThemeManagerError,
    ThemeSaveError,
    ThemeValidationError,
)

# ジェネレーターのインポート
from .generators.theme_generator import ThemeGenerator

# ログシステムのインポート
from .logger import (
    LogCategory,
    LogContext,
    LogLevel,
    QtThemeStudioLogger,
    get_logger,
    log_application_shutdown,
    log_application_startup,
    log_file_operation,
    log_function_call,
    log_user_action,
    setup_logging,
)

# ビューのインポート
from .views.main_window import QtThemeStudioMainWindow
from .views.preview import PreviewWindow, WidgetShowcase

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    # アダプター
    "ThemeAdapter",
    "QtAdapter",
    # ジェネレーター
    "ThemeGenerator",
    # ビュー
    "QtThemeStudioMainWindow",
    "WidgetShowcase",
    "PreviewWindow",
    # 例外クラス
    "ThemeManagerError",
    "ThemeLoadError",
    "ThemeSaveError",
    "ThemeExportError",
    "ThemeValidationError",
    # ログシステム
    "LogLevel",
    "LogCategory",
    "LogContext",
    "QtThemeStudioLogger",
    "get_logger",
    "setup_logging",
    "log_function_call",
    "log_user_action",
    "log_file_operation",
    "log_application_startup",
    "log_application_shutdown",
]
