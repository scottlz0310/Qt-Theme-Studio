"""
Qt-Theme-Studio エラーハンドラーのテスト

このモジュールは、Qt-Theme-Studioのエラーハンドラーをテストします。
"""

import json
import tempfile
from unittest.mock import MagicMock

import pytest

from qt_theme_studio.error_handler import ErrorHandler
from qt_theme_studio.exceptions import (
    ApplicationCrashError,
    ConfigurationError,
    QtFrameworkNotFoundError,
    ThemeLoadError,
    ThemeSaveError,
)


class TestErrorHandler:
    """ErrorHandlerクラスのテスト"""

    def setup_method(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.mock_logger = MagicMock()
        self.error_handler = ErrorHandler(self.mock_logger)

        # テスト用のディレクトリを設定
        self.error_handler.backup_directory = Path(self.temp_dir) / "backups"
        self.error_handler.crash_reports_directory = Path(self.temp_dir) / "crash_reports"
        self.error_handler.backup_directory.mkdir(parents=True, exist_ok=True)
        self.error_handler.crash_reports_directory.mkdir(parents=True, exist_ok=True)

    def test_initialization(self):
        """エラーハンドラー初期化のテスト"""
        assert self.error_handler.logger == self.mock_logger
        assert self.error_handler.backup_directory.exists()
        assert self.error_handler.crash_reports_directory.exists()

    def test_register_recovery_callback(self):
        """復旧コールバック登録のテスト"""
        callback = MagicMock()
        self.error_handler.register_recovery_callback("test_error", callback)

        assert "test_error" in self.error_handler.recovery_callbacks
        assert self.error_handler.recovery_callbacks["test_error"] == callback

    def test_handle_qt_framework_error(self):
        """Qtフレームワークエラー処理のテスト"""
        attempted_frameworks = ["PySide6", "PyQt6", "PyQt5"]
        error = QtFrameworkNotFoundError(attempted_frameworks=attempted_frameworks)

        result = self.error_handler.handle_qt_framework_error(error)

        assert result["title"] == "Qtフレームワークが見つかりません"
        assert result["attempted_frameworks"] == attempted_frameworks
        assert "recovery_actions" in result
        assert len(result["recovery_actions"]) == 3

        # ログが記録されることを確認
        self.mock_logger.log_error.assert_called_once()

    def test_handle_theme_load_error(self):
        """テーマ読み込みエラー処理のテスト"""
        file_path = "/test/theme.json"
        original_error = FileNotFoundError("File not found")
        error = ThemeLoadError("テーマファイルが見つかりません", file_path=file_path, original_error=original_error)

        result = self.error_handler.handle_theme_load_error(error)

        assert result["title"] == "テーマの読み込みエラー"
        assert result["file_path"] == file_path
        assert result["original_error"] == str(original_error)
        assert "recovery_actions" in result

        # ログが記録されることを確認
        self.mock_logger.log_error.assert_called_once()

    def test_handle_theme_save_error(self):
        """テーマ保存エラー処理のテスト"""
        file_path = "/test/theme.json"
        error = ThemeSaveError("テーマの保存に失敗しました", file_path=file_path)

        result = self.error_handler.handle_theme_save_error(error)

        assert result["title"] == "テーマの保存エラー"
        assert result["file_path"] == file_path
        assert "recovery_actions" in result

        # 代替保存場所が提案されることを確認
        recovery_actions = result["recovery_actions"]
        save_action = next((action for action in recovery_actions if action["action"] == "save_to_alternative_path"), None)
        assert save_action is not None
        assert "alternative_paths" in save_action

    def test_handle_configuration_error(self):
        """設定エラー処理のテスト"""
        config_key = "theme_directory"
        config_file = "/test/config.json"
        error = ConfigurationError("設定の読み込みに失敗しました", config_key=config_key, config_file=config_file)

        result = self.error_handler.handle_configuration_error(error)

        assert result["title"] == "設定エラー"
        assert result["config_key"] == config_key
        assert result["config_file"] == config_file
        assert "recovery_actions" in result

        # リセットと復元のアクションが含まれることを確認
        recovery_actions = result["recovery_actions"]
        action_types = [action["action"] for action in recovery_actions]
        assert "reset_to_default" in action_types
        assert "restore_from_backup" in action_types

    def test_handle_application_crash(self):
        """アプリケーションクラッシュ処理のテスト"""
        crash_context = {
            "current_theme": {"name": "test_theme", "colors": {"primary": "#000000"}},
            "window_state": {"width": 800, "height": 600}
        }
        error = ApplicationCrashError("予期しないエラーが発生しました", crash_context=crash_context)

        result = self.error_handler.handle_application_crash(error)

        assert result["title"] == "アプリケーションクラッシュ"
        assert "crash_report" in result
        assert "auto_save_result" in result
        assert "recovery_actions" in result

        # クラッシュレポートファイルが作成されることを確認
        crash_report = result["crash_report"]
        if crash_report["success"]:
            report_file = Path(crash_report["file_path"])
            assert report_file.exists()

    def test_handle_generic_error(self):
        """一般的なエラー処理のテスト"""
        error = ValueError("予期しないエラー")

        result = self.error_handler.handle_generic_error(error)

        assert result["title"] == "予期しないエラー"
        assert result["error_type"] == "ValueError"
        assert "traceback" in result
        assert "recovery_actions" in result

    def test_find_backup_files(self):
        """バックアップファイル検索のテスト"""
        # テスト用のバックアップファイルを作成
        original_file = "theme.json"
        backup_file1 = self.error_handler.backup_directory / "{original_file}.20231201_120000.backup"
        backup_file2 = self.error_handler.backup_directory / "{original_file}.20231201_130000.backup"

        backup_file1.write_text("backup1")
        backup_file2.write_text("backup2")

        backup_files = self.error_handler._find_backup_files(original_file)

        assert len(backup_files) == 2
        # 新しい順にソートされることを確認
        assert backup_files[0]["created_time"] >= backup_files[1]["created_time"]

    def test_get_default_themes(self):
        """デフォルトテーマ取得のテスト"""
        default_themes = self.error_handler._get_default_themes()

        assert len(default_themes) > 0
        assert all("name" in theme and "path" in theme for theme in default_themes)

    def test_suggest_alternative_save_paths(self):
        """代替保存パス提案のテスト"""
        original_path = "/original/path/theme.json"

        alternatives = self.error_handler._suggest_alternative_save_paths(original_path)

        assert len(alternatives) > 0
        assert all(isinstance(path, str) for path in alternatives)
        assert any("Documents" in path for path in alternatives)

    def test_create_backup(self):
        """バックアップ作成のテスト"""
        file_path = "/test/theme.json"
        data = {"name": "test_theme", "colors": {"primary": "#000000"}}

        result = self.error_handler.create_backup(file_path, data)

        assert result is True

        # バックアップファイルが作成されることを確認
        backup_files = list(self.error_handler.backup_directory.glob("theme.json.*.backup"))
        assert len(backup_files) > 0

        # バックアップファイルの内容を確認
        with open(backup_files[0], 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
            assert backup_data == data

    def test_generate_crash_report(self):
        """クラッシュレポート生成のテスト"""
        crash_context = {"current_theme": "test_theme"}
        error = ApplicationCrashError("テストクラッシュ", crash_context=crash_context)

        result = self.error_handler._generate_crash_report(error)

        if result["success"]:
            assert "file_path" in result
            assert "report" in result

            # レポートファイルが作成されることを確認
            report_file = Path(result["file_path"])
            assert report_file.exists()

            # レポート内容を確認
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                assert "timestamp" in report_data
                assert "error_message" in report_data
                assert "crash_context" in report_data
                assert "system_info" in report_data

    def test_attempt_auto_save(self):
        """自動保存試行のテスト"""
        crash_context = {
            "current_theme": {"name": "test_theme", "colors": {"primary": "#000000"}},
            "window_state": {"width": 800, "height": 600}
        }

        result = self.error_handler._attempt_auto_save(crash_context)

        if result["success"]:
            assert len(result["saved_files"]) > 0

            # 自動保存ファイルが作成されることを確認
            for saved_file in result["saved_files"]:
                assert Path(saved_file).exists()


if __name__ == "__main__":
    pytest.main([__file__])
