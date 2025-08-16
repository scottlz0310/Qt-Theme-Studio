"""
Qt-Theme-Studio 例外クラスのテスト

このモジュールは、Qt-Theme-Studioの例外クラスをテストします。
"""

import pytest

from qt_theme_studio.exceptions import (
    AccessibilityError,
    ApplicationCrashError,
    ExportError,
    QtFrameworkNotFoundError,
    ThemeLoadError,
    ThemeStudioException,
    ThemeValidationError,
)


class TestThemeStudioException:
    """ThemeStudioException基底クラスのテスト"""

    def test_basic_exception(self):
        """基本的な例外作成のテスト"""
        message = "テストエラーメッセージ"
        exception = ThemeStudioException(message)

        assert str(exception) == message
        assert exception.message == message
        assert exception.error_code is None
        assert exception.details == {}

    def test_exception_with_error_code(self):
        """エラーコード付き例外のテスト"""
        message = "テストエラーメッセージ"
        error_code = "TEST_ERROR"
        exception = ThemeStudioException(message, error_code=error_code)

        assert str(exception) == "[{error_code}] {message}"
        assert exception.error_code == error_code

    def test_exception_with_details(self):
        """詳細情報付き例外のテスト"""
        message = "テストエラーメッセージ"
        details = {"key1": "value1", "key2": "value2"}
        exception = ThemeStudioException(message, details=details)

        assert exception.details == details

    def test_to_dict(self):
        """辞書変換のテスト"""
        message = "テストエラーメッセージ"
        error_code = "TEST_ERROR"
        details = {"key1": "value1"}
        exception = ThemeStudioException(message, error_code=error_code, details=details)

        result = exception.to_dict()
        expected = {
            "type": "ThemeStudioException",
            "message": message,
            "error_code": error_code,
            "details": details
        }

        assert result == expected


class TestQtFrameworkNotFoundError:
    """QtFrameworkNotFoundError例外のテスト"""

    def test_default_message(self):
        """デフォルトメッセージのテスト"""
        exception = QtFrameworkNotFoundError()

        assert "利用可能なQtフレームワークが見つかりません" in str(exception)
        assert exception.error_code == "QT_FRAMEWORK_NOT_FOUND"

    def test_with_attempted_frameworks(self):
        """試行フレームワーク情報付きのテスト"""
        attempted = ["PySide6", "PyQt6", "PyQt5"]
        exception = QtFrameworkNotFoundError(attempted_frameworks=attempted)

        assert exception.attempted_frameworks == attempted
        assert exception.details["attempted_frameworks"] == attempted

    def test_installation_guide(self):
        """インストール手順のテスト"""
        exception = QtFrameworkNotFoundError()
        guide = exception.get_installation_guide()

        assert "PySide6" in guide
        assert "PyQt6" in guide
        assert "PyQt5" in guide
        assert "pip install" in guide


class TestThemeLoadError:
    """ThemeLoadError例外のテスト"""

    def test_basic_theme_load_error(self):
        """基本的なテーマ読み込みエラーのテスト"""
        message = "テーマファイルが見つかりません"
        exception = ThemeLoadError(message)

        assert exception.message == message
        assert exception.error_code == "THEME_LOAD_ERROR"

    def test_with_file_path(self):
        """ファイルパス付きのテスト"""
        message = "テーマファイルが見つかりません"
        file_path = "/path/to/theme.json"
        exception = ThemeLoadError(message, file_path=file_path)

        assert exception.file_path == file_path
        assert exception.details["file_path"] == file_path

    def test_with_original_error(self):
        """元の例外付きのテスト"""
        message = "テーマファイルが見つかりません"
        original_error = FileNotFoundError("File not found")
        exception = ThemeLoadError(message, original_error=original_error)

        assert exception.original_error == original_error
        assert exception.details["original_error"] == str(original_error)


class TestThemeValidationError:
    """ThemeValidationError例外のテスト"""

    def test_basic_validation_error(self):
        """基本的な検証エラーのテスト"""
        message = "テーマの検証に失敗しました"
        exception = ThemeValidationError(message)

        assert exception.message == message
        assert exception.error_code == "THEME_VALIDATION_ERROR"

    def test_with_validation_errors(self):
        """検証エラーリスト付きのテスト"""
        message = "テーマの検証に失敗しました"
        validation_errors = ["必須プロパティが不足", "色形式が無効"]
        exception = ThemeValidationError(message, validation_errors=validation_errors)

        assert exception.validation_errors == validation_errors
        assert exception.details["validation_errors"] == validation_errors

    def test_with_theme_name(self):
        """テーマ名付きのテスト"""
        message = "テーマの検証に失敗しました"
        theme_name = "テストテーマ"
        exception = ThemeValidationError(message, theme_name=theme_name)

        assert exception.theme_name == theme_name
        assert exception.details["theme_name"] == theme_name


class TestExportError:
    """ExportError例外のテスト"""

    def test_basic_export_error(self):
        """基本的なエクスポートエラーのテスト"""
        message = "エクスポートに失敗しました"
        exception = ExportError(message)

        assert exception.message == message
        assert exception.error_code == "EXPORT_ERROR"

    def test_with_export_format(self):
        """エクスポート形式付きのテスト"""
        message = "エクスポートに失敗しました"
        export_format = "JSON"
        exception = ExportError(message, export_format=export_format)

        assert exception.export_format == export_format
        assert exception.details["export_format"] == export_format


class TestAccessibilityError:
    """AccessibilityError例外のテスト"""

    def test_basic_accessibility_error(self):
        """基本的なアクセシビリティエラーのテスト"""
        message = "アクセシビリティ検証に失敗しました"
        exception = AccessibilityError(message)

        assert exception.message == message
        assert exception.error_code == "ACCESSIBILITY_ERROR"

    def test_with_wcag_level(self):
        """WCAGレベル付きのテスト"""
        message = "アクセシビリティ検証に失敗しました"
        wcag_level = "AA"
        exception = AccessibilityError(message, wcag_level=wcag_level)

        assert exception.wcag_level == wcag_level
        assert exception.details["wcag_level"] == wcag_level

    def test_with_colors(self):
        """色情報付きのテスト"""
        message = "アクセシビリティ検証に失敗しました"
        colors = ["#ffff", "#000000"]
        exception = AccessibilityError(message, colors=colors)

        assert exception.colors == colors
        assert exception.details["colors"] == colors


class TestApplicationCrashError:
    """ApplicationCrashError例外のテスト"""

    def test_basic_crash_error(self):
        """基本的なクラッシュエラーのテスト"""
        message = "アプリケーションがクラッシュしました"
        exception = ApplicationCrashError(message)

        assert exception.message == message
        assert exception.error_code == "APPLICATION_CRASH"

    def test_with_crash_context(self):
        """クラッシュコンテキスト付きのテスト"""
        message = "アプリケーションがクラッシュしました"
        crash_context = {"current_theme": "test_theme", "window_state": "maximized"}
        exception = ApplicationCrashError(message, crash_context=crash_context)

        assert exception.crash_context == crash_context
        assert "current_theme" in exception.details
        assert "window_state" in exception.details


if __name__ == "__main__":
    pytest.main([__file__])
