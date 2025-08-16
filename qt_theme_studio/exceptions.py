"""
Qt-Theme-Studio カスタム例外クラス

このモジュールは、Qt-Theme-Studioアプリケーションで使用される
すべてのカスタム例外クラスを定義します。
"""

from typing import Any, Dict, Optional


class ThemeStudioException(Exception):
    """
    Qt-Theme-Studio基底例外クラス

    すべてのQt-Theme-Studio固有の例外の基底クラスです。
    日本語エラーメッセージとエラーコードをサポートします。
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        例外を初期化します

        Args:
            message: 日本語エラーメッセージ
            error_code: エラーコード（オプション）
            details: エラー詳細情報（オプション）
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        """文字列表現を返します"""
        if self.error_code:
            return "[{self.error_code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """例外情報を辞書形式で返します"""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class QtFrameworkNotFoundError(ThemeStudioException):
    """
    Qtフレームワーク未検出エラー

    PySide6、PyQt6、PyQt5のいずれも検出されない場合に発生します。
    """

    def __init__(
        self,
        message: str = "利用可能なQtフレームワークが見つかりません",
        attempted_frameworks: Optional[list] = None,
    ):
        """
        Qtフレームワーク未検出エラーを初期化します

        Args:
            message: エラーメッセージ
            attempted_frameworks: 検出を試行したフレームワークのリスト
        """
        details = {}
        if attempted_frameworks:
            details["attempted_frameworks"] = attempted_frameworks

        super().__init__(
            message=message, error_code="QT_FRAMEWORK_NOT_FOUND", details=details
        )
        self.attempted_frameworks = attempted_frameworks or []

    def get_installation_guide(self) -> str:
        """インストール手順を返します"""
        return (
            "以下のいずれかのQtフレームワークをインストールしてください:\n"
            "1. PySide6 (推奨): pip install PySide6\n"
            "2. PyQt6: pip install PyQt6\n"
            "3. PyQt5: pip install PyQt5"
        )


class ThemeLoadError(ThemeStudioException):
    """
    テーマ読み込みエラー

    テーマファイルの読み込みに失敗した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        テーマ読み込みエラーを初期化します

        Args:
            message: エラーメッセージ
            file_path: 読み込みに失敗したファイルパス
            original_error: 元の例外
        """
        details = {}
        if file_path:
            details["file_path"] = file_path
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=message, error_code="THEME_LOAD_ERROR", details=details
        )
        self.file_path = file_path
        self.original_error = original_error


class ThemeSaveError(ThemeStudioException):
    """
    テーマ保存エラー

    テーマファイルの保存に失敗した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        テーマ保存エラーを初期化します

        Args:
            message: エラーメッセージ
            file_path: 保存に失敗したファイルパス
            original_error: 元の例外
        """
        details = {}
        if file_path:
            details["file_path"] = file_path
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=message, error_code="THEME_SAVE_ERROR", details=details
        )
        self.file_path = file_path
        self.original_error = original_error


class ThemeValidationError(ThemeStudioException):
    """
    テーマ検証エラー

    テーマの検証に失敗した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        validation_errors: Optional[list] = None,
        theme_name: Optional[str] = None,
    ):
        """
        テーマ検証エラーを初期化します

        Args:
            message: エラーメッセージ
            validation_errors: 検証エラーのリスト
            theme_name: テーマ名
        """
        details = {}
        if validation_errors:
            details["validation_errors"] = validation_errors
        if theme_name:
            details["theme_name"] = theme_name

        super().__init__(
            message=message, error_code="THEME_VALIDATION_ERROR", details=details
        )
        self.validation_errors = validation_errors or []
        self.theme_name = theme_name


class ExportError(ThemeStudioException):
    """
    エクスポートエラー

    テーマのエクスポートに失敗した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        export_format: Optional[str] = None,
        file_path: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        エクスポートエラーを初期化します

        Args:
            message: エラーメッセージ
            export_format: エクスポート形式
            file_path: エクスポート先ファイルパス
            original_error: 元の例外
        """
        details = {}
        if export_format:
            details["export_format"] = export_format
        if file_path:
            details["file_path"] = file_path
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(message=message, error_code="EXPORT_ERROR", details=details)
        self.export_format = export_format
        self.file_path = file_path
        self.original_error = original_error


class ImportError(ThemeStudioException):
    """
    インポートエラー

    テーマのインポートに失敗した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        import_format: Optional[str] = None,
        file_path: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        インポートエラーを初期化します

        Args:
            message: エラーメッセージ
            import_format: インポート形式
            file_path: インポート元ファイルパス
            original_error: 元の例外
        """
        details = {}
        if import_format:
            details["import_format"] = import_format
        if file_path:
            details["file_path"] = file_path
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(message=message, error_code="IMPORT_ERROR", details=details)
        self.import_format = import_format
        self.file_path = file_path
        self.original_error = original_error


class ConfigurationError(ThemeStudioException):
    """
    設定エラー

    アプリケーション設定の読み込みや保存に失敗した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        設定エラーを初期化します

        Args:
            message: エラーメッセージ
            config_key: 設定キー
            config_file: 設定ファイルパス
            original_error: 元の例外
        """
        details = {}
        if config_key:
            details["config_key"] = config_key
        if config_file:
            details["config_file"] = config_file
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=message, error_code="CONFIGURATION_ERROR", details=details
        )
        self.config_key = config_key
        self.config_file = config_file
        self.original_error = original_error


class PreviewError(ThemeStudioException):
    """
    プレビューエラー

    テーマプレビューの生成や更新に失敗した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        widget_type: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        プレビューエラーを初期化します

        Args:
            message: エラーメッセージ
            widget_type: ウィジェットタイプ
            original_error: 元の例外
        """
        details = {}
        if widget_type:
            details["widget_type"] = widget_type
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(message=message, error_code="PREVIEW_ERROR", details=details)
        self.widget_type = widget_type
        self.original_error = original_error


class AccessibilityError(ThemeStudioException):
    """
    アクセシビリティエラー

    アクセシビリティ検証や色コントラスト計算に失敗した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        wcag_level: Optional[str] = None,
        colors: Optional[list] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        アクセシビリティエラーを初期化します

        Args:
            message: エラーメッセージ
            wcag_level: WCAGレベル
            colors: 色のリスト
            original_error: 元の例外
        """
        details = {}
        if wcag_level:
            details["wcag_level"] = wcag_level
        if colors:
            details["colors"] = colors
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=message, error_code="ACCESSIBILITY_ERROR", details=details
        )
        self.wcag_level = wcag_level
        self.colors = colors or []
        self.original_error = original_error


class ApplicationCrashError(ThemeStudioException):
    """
    アプリケーションクラッシュエラー

    アプリケーションの予期しないクラッシュが発生した場合に発生します。
    """

    def __init__(
        self,
        message: str,
        crash_context: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        アプリケーションクラッシュエラーを初期化します

        Args:
            message: エラーメッセージ
            crash_context: クラッシュ時のコンテキスト情報
            original_error: 元の例外
        """
        details = {}
        if crash_context:
            details.update(crash_context)
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=message, error_code="APPLICATION_CRASH", details=details
        )
        self.crash_context = crash_context or {}
        self.original_error = original_error
