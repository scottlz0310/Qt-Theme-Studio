"""
CLI機能の単体テスト

Qt-Theme-StudioのCLI機能のテストを行います
"""

import json
from unittest.mock import Mock, patch

import pytest

from qt_theme_studio.cli import ci_report, main, quality_check, test_theme


class TestQualityCheck:
    """quality_check関数のテスト"""

    def test_quality_check_valid_theme(self, tmp_path):
        """有効なテーマファイルの品質チェック"""
        # テスト用テーマファイル作成
        theme_file = tmp_path / "valid_theme.json"
        theme_data = {
            "name": "Test Theme",
            "colors": {"primary": "#007acc", "background": "#ffffff"},
        }
        theme_file.write_text(json.dumps(theme_data))

        # 品質チェック実行
        result = quality_check(str(theme_file))
        assert result == 0

    def test_quality_check_invalid_theme(self, tmp_path):
        """無効なテーマファイルの品質チェック"""
        # 必須フィールドが不足したテーマファイル
        theme_file = tmp_path / "invalid_theme.json"
        theme_data = {"description": "Missing required fields"}
        theme_file.write_text(json.dumps(theme_data))

        # 品質チェック実行
        result = quality_check(str(theme_file))
        assert result == 1

    def test_quality_check_nonexistent_file(self):
        """存在しないファイルの品質チェック"""
        result = quality_check("nonexistent_file.json")
        assert result == 1

    def test_quality_check_invalid_json(self, tmp_path):
        """無効なJSONファイルの品質チェック"""
        theme_file = tmp_path / "invalid.json"
        theme_file.write_text("invalid json content")

        result = quality_check(str(theme_file))
        assert result == 1


class TestTestTheme:
    """test_theme関数のテスト"""

    def test_test_theme_valid(self, tmp_path):
        """有効なテーマファイルのテスト"""
        theme_file = tmp_path / "test_theme.json"
        theme_data = {
            "name": "Test Theme",
            "colors": {"primary": "#007acc", "background": "#ffffff"},
        }
        theme_file.write_text(json.dumps(theme_data))

        # qt_theme_managerのモック化
        with patch("qt_theme_studio.cli.qt_theme_manager") as mock_qtm:
            mock_qtm.ThemeLoader.return_value = Mock()
            mock_qtm.StylesheetGenerator.return_value = Mock()

            result = test_theme(str(theme_file))
            assert result == 0

    def test_test_theme_qt_manager_error(self, tmp_path):
        """qt-theme-managerエラー時のテスト"""
        theme_file = tmp_path / "test_theme.json"
        theme_data = {"name": "Test Theme", "colors": {"primary": "#007acc"}}
        theme_file.write_text(json.dumps(theme_data))

        # qt_theme_managerでエラーが発生する場合
        with patch("qt_theme_studio.cli.qt_theme_manager") as mock_qtm:
            mock_qtm.ThemeLoader.side_effect = Exception("Qt error")

            result = test_theme(str(theme_file))
            assert result == 0  # CI環境では成功扱い

    def test_test_theme_invalid_file(self):
        """無効なファイルのテスト"""
        result = test_theme("nonexistent_file.json")
        assert result == 1


class TestCiReport:
    """ci_report関数のテスト"""

    def test_ci_report_generation(self, tmp_path):
        """CI/CDレポート生成テスト"""
        # テスト用テーマファイル
        theme_file = tmp_path / "theme.json"
        theme_data = {
            "name": "Test Theme",
            "version": "1.0.0",
            "colors": {
                "primary": "#007acc",
                "secondary": "#6c757d",
                "background": "#ffffff",
                "text": "#000000",
                "accent": "#0078d4",
                "surface": "#f8f9fa",
            },
            "fonts": {"default": {"family": "Arial", "size": 12}},
            "metadata": {"author": "Test Author"},
        }
        theme_file.write_text(json.dumps(theme_data))

        # レポート出力ファイル
        output_file = tmp_path / "report.json"

        # レポート生成実行
        result = ci_report(str(theme_file), str(output_file))
        assert result == 0

        # レポートファイルの確認
        assert output_file.exists()
        report_data = json.loads(output_file.read_text())

        assert "ci_summary" in report_data
        assert report_data["ci_summary"]["overall_status"] == "PASS"
        assert report_data["ci_summary"]["quality_score"] == 100.0
        assert "generated_at" in report_data
        assert report_data["theme_file"] == str(theme_file)

    def test_ci_report_low_quality_theme(self, tmp_path):
        """低品質テーマのCI/CDレポート"""
        # 最小限のテーマファイル
        theme_file = tmp_path / "minimal_theme.json"
        theme_data = {"name": "Minimal Theme"}
        theme_file.write_text(json.dumps(theme_data))

        output_file = tmp_path / "report.json"

        result = ci_report(str(theme_file), str(output_file))
        assert result == 0

        report_data = json.loads(output_file.read_text())
        assert report_data["ci_summary"]["overall_status"] == "PASS"  # 70点以上
        assert report_data["ci_summary"]["quality_score"] == 75.0

    def test_ci_report_error(self):
        """CI/CDレポート生成エラー"""
        result = ci_report("nonexistent_file.json")
        assert result == 1


class TestMain:
    """main関数のテスト"""

    def test_main_no_args(self):
        """引数なしでの実行"""
        with patch("sys.argv", ["cli.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_quality_check(self, tmp_path):
        """quality-checkコマンドのテスト"""
        theme_file = tmp_path / "theme.json"
        theme_data = {"name": "Test", "colors": {"primary": "#007acc"}}
        theme_file.write_text(json.dumps(theme_data))

        with patch("sys.argv", ["cli.py", "quality-check", str(theme_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_test_command(self, tmp_path):
        """testコマンドのテスト"""
        theme_file = tmp_path / "theme.json"
        theme_data = {"name": "Test", "colors": {"primary": "#007acc"}}
        theme_file.write_text(json.dumps(theme_data))

        with patch("sys.argv", ["cli.py", "test", str(theme_file)]):
            with patch("qt_theme_studio.cli.qt_theme_manager"):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    def test_main_ci_report_command(self, tmp_path):
        """ci-reportコマンドのテスト"""
        theme_file = tmp_path / "theme.json"
        theme_data = {"name": "Test", "colors": {"primary": "#007acc"}}
        theme_file.write_text(json.dumps(theme_data))

        with patch("sys.argv", ["cli.py", "ci-report", str(theme_file)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_ci_report_with_output(self, tmp_path):
        """ci-reportコマンド（出力ファイル指定）のテスト"""
        theme_file = tmp_path / "theme.json"
        theme_data = {"name": "Test", "colors": {"primary": "#007acc"}}
        theme_file.write_text(json.dumps(theme_data))

        output_file = tmp_path / "custom_report.json"

        with patch(
            "sys.argv",
            ["cli.py", "ci-report", str(theme_file), "--output", str(output_file)],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_unknown_command(self):
        """不明なコマンドのテスト"""
        with patch("sys.argv", ["cli.py", "unknown-command"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_insufficient_args(self):
        """引数不足のテスト"""
        with patch("sys.argv", ["cli.py", "quality-check"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


class TestIntegration:
    """統合テスト"""

    def test_full_workflow(self, tmp_path):
        """完全ワークフローテスト"""
        # 高品質テーマファイル作成
        theme_file = tmp_path / "workflow_theme.json"
        theme_data = {
            "name": "Workflow Theme",
            "version": "1.0.0",
            "colors": {
                "primary": "#007acc",
                "secondary": "#6c757d",
                "background": "#ffffff",
                "text": "#000000",
                "accent": "#0078d4",
                "surface": "#f8f9fa",
            },
            "fonts": {"default": {"family": "Arial", "size": 12}},
            "metadata": {
                "author": "Test Author",
                "description": "Test theme for workflow",
            },
        }
        theme_file.write_text(json.dumps(theme_data))

        # 1. 品質チェック
        assert quality_check(str(theme_file)) == 0

        # 2. テーマテスト
        with patch("qt_theme_studio.cli.qt_theme_manager"):
            assert test_theme(str(theme_file)) == 0

        # 3. CI/CDレポート生成
        report_file = tmp_path / "workflow_report.json"
        assert ci_report(str(theme_file), str(report_file)) == 0

        # レポート内容確認
        report_data = json.loads(report_file.read_text())
        assert report_data["ci_summary"]["overall_status"] == "PASS"
        assert report_data["ci_summary"]["quality_score"] == 100.0
