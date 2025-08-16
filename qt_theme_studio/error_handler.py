"""
Qt-Theme-Studio エラーハンドリング戦略

このモジュールは、Qt-Theme-Studioアプリケーションのエラーハンドリング戦略を実装します。
各種エラーに対する適切な処理と復旧手順を提供します。
"""

import json
import traceback
from datetime import datetime
from typing import Any, Callable, Dict
from pathlib import Path

from .exceptions import (
    ApplicationCrashError,
    ConfigurationError,
    QtFrameworkNotFoundError,
    ThemeLoadError,
    ThemeSaveError,
)


class ErrorHandler:
    """
    エラーハンドリング戦略クラス

    各種エラーに対する適切な処理と復旧手順を提供します。
    """

    def __init__(self, logger=None):
        """
        エラーハンドラーを初期化します

        Args:
            logger: ログ出力用のロガーインスタンス
        """
        self.logger = logger
        self.recovery_callbacks: Dict[str, Callable] = {}
        self.backup_directory = Path.home() / ".qt_theme_studio" / "backups"
        self.crash_reports_directory = (
            Path.home() / ".qt_theme_studio" / "crash_reports"
        )

        # バックアップディレクトリを作成
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        self.crash_reports_directory.mkdir(parents=True, exist_ok=True)

    def register_recovery_callback(self, error_type: str, callback: Callable) -> None:
        """
        エラータイプに対する復旧コールバックを登録します

        Args:
            error_type: エラータイプ
            callback: 復旧処理のコールバック関数
        """
        self.recovery_callbacks[error_type] = callback

    def handle_qt_framework_error(
        self, error: QtFrameworkNotFoundError
    ) -> Dict[str, Any]:
        """
        Qtフレームワークエラーを処理します

        Args:
            error: Qtフレームワーク未検出エラー

        Returns:
            処理結果の辞書
        """
        if self.logger:
            self.logger.log_error(
                f"Qtフレームワークが検出されませんでした: {error.message}", error
            )

        # インストール手順を取得
        installation_guide = error.get_installation_guide()

        # エラー情報を構築
        error_info = {
            "title": "Qtフレームワークが見つかりません",
            "message": error.message,
            "installation_guide": installation_guide,
            "attempted_frameworks": error.attempted_frameworks,
            "recovery_actions": [
                {
                    "action": "install_pyside6",
                    "description": "PySide6をインストール (推奨)",
                    "command": "pip install PySide6",
                },
                {
                    "action": "install_pyqt6",
                    "description": "PyQt6をインストール",
                    "command": "pip install PyQt6",
                },
                {
                    "action": "install_pyqt5",
                    "description": "PyQt5をインストール",
                    "command": "pip install PyQt5",
                },
            ],
        }

        return error_info

    def handle_theme_load_error(self, error: ThemeLoadError) -> Dict[str, Any]:
        """
        テーマ読み込みエラーを処理します

        Args:
            error: テーマ読み込みエラー

        Returns:
            処理結果の辞書
        """
        if self.logger:
            self.logger.log_error(
                f"テーマの読み込みに失敗しました: {error.message}", error
            )

        recovery_actions = []

        # バックアップファイルの確認
        if error.file_path:
            backup_files = self._find_backup_files(error.file_path)
            if backup_files:
                recovery_actions.extend(
                    [
                        {
                            "action": "restore_from_backup",
                            "description": "バックアップから復元 ({len(backup_files)}個のバックアップが利用可能)",
                            "backup_files": backup_files,
                        }
                    ]
                )

        # 代替テーマの提案
        default_themes = self._get_default_themes()
        if default_themes:
            recovery_actions.append(
                {
                    "action": "use_default_theme",
                    "description": "デフォルトテーマを使用",
                    "default_themes": default_themes,
                }
            )

        # 新規テーマ作成の提案
        recovery_actions.append(
            {"action": "create_new_theme", "description": "新しいテーマを作成"}
        )

        error_info = {
            "title": "テーマの読み込みエラー",
            "message": error.message,
            "file_path": error.file_path,
            "original_error": (
                str(error.original_error) if error.original_error else None
            ),
            "recovery_actions": recovery_actions,
        }

        return error_info

    def handle_theme_save_error(self, error: ThemeSaveError) -> Dict[str, Any]:
        """
        テーマ保存エラーを処理します

        Args:
            error: テーマ保存エラー

        Returns:
            処理結果の辞書
        """
        if self.logger:
            self.logger.log_error(f"テーマの保存に失敗しました: {error.message}", error)

        recovery_actions = []

        # 代替保存場所の提案
        if error.file_path:
            alternative_paths = self._suggest_alternative_save_paths(error.file_path)
            recovery_actions.extend(
                [
                    {
                        "action": "save_to_alternative_path",
                        "description": "別の場所に保存",
                        "alternative_paths": alternative_paths,
                    }
                ]
            )

        # 一時保存の提案
        recovery_actions.append(
            {
                "action": "save_to_temp",
                "description": "一時ファイルとして保存",
                "temp_directory": str(self.backup_directory),
            }
        )

        error_info = {
            "title": "テーマの保存エラー",
            "message": error.message,
            "file_path": error.file_path,
            "original_error": (
                str(error.original_error) if error.original_error else None
            ),
            "recovery_actions": recovery_actions,
        }

        return error_info

    def handle_configuration_error(self, error: ConfigurationError) -> Dict[str, Any]:
        """
        設定エラーを処理します

        Args:
            error: 設定エラー

        Returns:
            処理結果の辞書
        """
        if self.logger:
            self.logger.log_error(f"設定エラーが発生しました: {error.message}", error)

        recovery_actions = [
            {
                "action": "reset_to_default",
                "description": "デフォルト設定にリセット",
                "config_key": error.config_key,
            },
            {
                "action": "restore_from_backup",
                "description": "設定ファイルをバックアップから復元",
            },
        ]

        error_info = {
            "title": "設定エラー",
            "message": error.message,
            "config_key": error.config_key,
            "config_file": error.config_file,
            "recovery_actions": recovery_actions,
        }

        return error_info

    def handle_application_crash(self, error: ApplicationCrashError) -> Dict[str, Any]:
        """
        アプリケーションクラッシュを処理します

        Args:
            error: アプリケーションクラッシュエラー

        Returns:
            処理結果の辞書
        """
        # クラッシュレポートを生成
        crash_report = self._generate_crash_report(error)

        if self.logger:
            self.logger.log_error(
                f"アプリケーションがクラッシュしました: {error.message}", error
            )

        # 作業内容の自動保存を試行
        auto_save_result = self._attempt_auto_save(error.crash_context)

        recovery_actions = [
            {
                "action": "restart_application",
                "description": "アプリケーションを再起動",
            },
            {
                "action": "restore_from_auto_save",
                "description": "自動保存から復元",
                "auto_save_available": auto_save_result["success"],
                "auto_save_files": auto_save_result.get("saved_files", []),
            },
            {
                "action": "send_crash_report",
                "description": "クラッシュレポートを送信",
                "crash_report_path": crash_report["file_path"],
            },
        ]

        error_info = {
            "title": "アプリケーションクラッシュ",
            "message": error.message,
            "crash_report": crash_report,
            "auto_save_result": auto_save_result,
            "recovery_actions": recovery_actions,
        }

        return error_info

    def handle_generic_error(self, error: Exception) -> Dict[str, Any]:
        """
        一般的なエラーを処理します

        Args:
            error: 例外オブジェクト

        Returns:
            処理結果の辞書
        """
        if self.logger:
            self.logger.log_error(
                f"予期しないエラーが発生しました: {str(error)}", error
            )

        error_info = {
            "title": "予期しないエラー",
            "message": str(error),
            "error_type": type(error).__name__,
            "traceback": traceback.format_exc(),
            "recovery_actions": [
                {"action": "retry_operation", "description": "操作を再試行"},
                {
                    "action": "restart_application",
                    "description": "アプリケーションを再起動",
                },
            ],
        }

        return error_info

    def _find_backup_files(self, original_file_path: str) -> list:
        """
        指定されたファイルのバックアップファイルを検索します

        Args:
            original_file_path: 元のファイルパス

        Returns:
            バックアップファイルのリスト
        """
        backup_files = []
        file_name = Path(original_file_path).name

        for backup_file in self.backup_directory.glob(f"{file_name}.*"):
            if backup_file.is_file():
                backup_files.append(
                    {
                        "path": str(backup_file),
                        "created_time": backup_file.stat().st_mtime,
                        "size": backup_file.stat().st_size,
                    }
                )

        # 作成時間でソート（新しい順）
        backup_files.sort(key=lambda x: x["created_time"], reverse=True)

        return backup_files

    def _get_default_themes(self) -> list:
        """
        利用可能なデフォルトテーマのリストを取得します

        Returns:
            デフォルトテーマのリスト
        """
        # TODO: 実際のデフォルトテーマディレクトリから取得
        return [
            {"name": "ライトテーマ", "path": "themes/light.json"},
            {"name": "ダークテーマ", "path": "themes/dark.json"},
            {"name": "ハイコントラストテーマ", "path": "themes/high_contrast.json"},
        ]

    def _suggest_alternative_save_paths(self, original_path: str) -> list:
        """
        代替保存パスを提案します

        Args:
            original_path: 元の保存パス

        Returns:
            代替パスのリスト
        """
        original_path_obj = Path(original_path)
        alternatives = []

        # ホームディレクトリ
        home_path = (
            Path.home() / "Documents" / "Qt-Theme-Studio" / original_path_obj.name
        )
        alternatives.append(str(home_path))

        # 一時ディレクトリ
        temp_path = self.backup_directory / original_path_obj.name
        alternatives.append(str(temp_path))

        # デスクトップ
        desktop_path = Path.home() / "Desktop" / original_path_obj.name
        alternatives.append(str(desktop_path))

        return alternatives

    def _generate_crash_report(self, error: ApplicationCrashError) -> Dict[str, Any]:
        """
        クラッシュレポートを生成します

        Args:
            error: アプリケーションクラッシュエラー

        Returns:
            クラッシュレポート情報
        """
        import datetime
        import platform
        import sys

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.crash_reports_directory / f"crash_report_{timestamp}.json"

        crash_report = {
            "timestamp": timestamp,
            "error_message": error.message,
            "error_type": type(error).__name__,
            "traceback": traceback.format_exc(),
            "crash_context": error.crash_context,
            "system_info": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "architecture": platform.architecture(),
            },
        }

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(crash_report, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "file_path": str(report_file),
                "report": crash_report,
            }
        except Exception:
            if self.logger:
                self.logger.log_error(
                    f"クラッシュレポートの生成に失敗しました: {str()}"
                )

            return {"success": False, "error": str(), "report": crash_report}

    def _attempt_auto_save(self, crash_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        作業内容の自動保存を試行します

        Args:
            crash_context: クラッシュ時のコンテキスト情報

        Returns:
            自動保存結果
        """
        saved_files = []

        try:
            # 現在編集中のテーマがある場合は保存
            if "current_theme" in crash_context:
                theme_data = crash_context["current_theme"]
                datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                auto_save_file = (
                    self.backup_directory / "auto_save_theme_{timestamp}.json"
                )

                with open(auto_save_file, "w", encoding="utf-8") as f:
                    json.dump(theme_data, f, ensure_ascii=False, indent=2)

                saved_files.append(str(auto_save_file))

            # ウィンドウ状態の保存
            if "window_state" in crash_context:
                window_state = crash_context["window_state"]
                datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                state_file = (
                    self.backup_directory / "auto_save_window_state_{timestamp}.json"
                )

                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(window_state, f, ensure_ascii=False, indent=2)

                saved_files.append(str(state_file))

            return {
                "success": True,
                "saved_files": saved_files,
                "message": "{len(saved_files)}個のファイルを自動保存しました",
            }

        except Exception:
            if self.logger:
                self.logger.log_error(f"自動保存に失敗しました: {str()}")

            return {"success": False, "error": str(), "saved_files": saved_files}

    def create_backup(self, file_path: str, data: Any) -> bool:
        """
        ファイルのバックアップを作成します

        Args:
            file_path: バックアップ対象のファイルパス
            data: バックアップするデータ

        Returns:
            バックアップ作成の成功/失敗
        """
        try:
            import datetime

            Path(file_path).name
            datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_directory / "{file_name}.{timestamp}.backup"

            if isinstance(data, (dict, list)):
                with open(backup_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(str(data))

            if self.logger:
                self.logger.log_user_action(
                    "バックアップ作成",
                    {"original_file": file_path, "backup_file": str(backup_file)},
                )

            return True

        except Exception:
            if self.logger:
                self.logger.log_error("バックアップの作成に失敗しました: {str()}")
            return False
