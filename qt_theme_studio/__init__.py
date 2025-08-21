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


# ジェネレーターのインポート(遅延読み込み)
def _get_theme_generator():
    """ThemeGeneratorを遅延読み込み"""
    from .generators.theme_generator import ThemeGenerator

    return ThemeGenerator


# 後方互換性のため
ThemeGenerator = None


# ビューのインポート(遅延読み込み)
def _get_main_window():
    """QtThemeStudioMainWindowを遅延読み込み"""
    from .views.main_window import QtThemeStudioMainWindow

    return QtThemeStudioMainWindow


def _get_preview_components():
    """PreviewWindow, WidgetShowcaseを遅延読み込み"""
    from .views.preview import PreviewWindow, WidgetShowcase

    return PreviewWindow, WidgetShowcase


# 後方互換性のため
QtThemeStudioMainWindow = None
PreviewWindow = None
WidgetShowcase = None


# 動的インポート関数
def __getattr__(name: str):
    """動的インポートによる遅延読み込み"""
    if name == "ThemeGenerator":
        return _get_theme_generator()
    if name == "QtThemeStudioMainWindow":
        return _get_main_window()
    if name == "PreviewWindow":
        return _get_preview_components()[0]
    if name == "WidgetShowcase":
        return _get_preview_components()[1]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "LogCategory",
    "LogContext",
    "LogLevel",
    "PreviewWindow",
    "QtAdapter",
    "QtThemeStudioLogger",
    "QtThemeStudioMainWindow",
    "ThemeAdapter",
    "ThemeExportError",
    "ThemeGenerator",
    "ThemeLoadError",
    "ThemeManagerError",
    "ThemeSaveError",
    "ThemeValidationError",
    "WidgetShowcase",
    "__author__",
    "__description__",
    "__version__",
    "get_logger",
    "log_application_shutdown",
    "log_application_startup",
    "log_file_operation",
    "log_function_call",
    "log_user_action",
    "setup_logging",
]
