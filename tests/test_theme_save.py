"""
テーマ保存機能のテスト

このモジュールは、ThemeEditorのテーマ保存機能の単体テストを実装します。
"""

import tempfile
from unittest.mock import Mock

import pytest

# テスト対象のインポート
from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.adapters.theme_adapter import ThemeAdapter
from qt_theme_studio.views.theme_editor import ThemeEditor


class TestThemeSave:
    """テーマ保存機能のテスト"""

    @pytest.fixture
    def mock_qt_adapter(self):
        """モックQtAdapterを作成"""
        mock_adapter = Mock(spec=QtAdapter)
        mock_modules = {
            'QtWidgets': Mock(),
            'QtCore': Mock(),
            'QtGui': Mock()
        }

        # QTimerのモック
        mock_timer = Mock()
        mock_modules['QtCore'].QTimer.return_value = mock_timer

        # QTimeのモック
        mock_time = Mock()
        mock_time.currentTime.return_value = Mock()
        mock_time.currentTime.return_value.msecsTo.return_value = 50
        mock_modules['QtCore'].QTime = mock_time

        # QMessageBoxのモック
        mock_msgbox = Mock()
        mock_modules['QtWidgets'].QMessageBox.return_value = mock_msgbox
        mock_modules['QtWidgets'].QMessageBox.Icon = Mock()
        mock_modules['QtWidgets'].QMessageBox.StandardButton = Mock()

        # QFileDialogのモック
        mock_modules['QtWidgets'].QFileDialog = Mock()

        mock_adapter.get_qt_modules.return_value = mock_modules
        return mock_adapter

    @pytest.fixture
    def mock_theme_adapter(self):
        """モックThemeAdapterを作成"""
        mock_adapter = Mock(spec=ThemeAdapter)

        # validate_themeのモック
        mock_adapter.validate_theme.return_value = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # save_themeのモック
        mock_adapter.save_theme.return_value = True

        # export_themeのモック
        mock_adapter.export_theme.return_value = '{"name": "test_theme"}'

        # load_themeのモック
        mock_adapter.load_theme.return_value = {
            'name': 'テストテーマ',
            'version': '1.0.0',
            'colors': {'primary': '#0078d4'}
        }

        return mock_adapter

    @pytest.fixture
    def theme_editor(self, mock_qt_adapter, mock_theme_adapter):
        """テーマエディターのインスタンスを作成"""
        return ThemeEditor(mock_qt_adapter, mock_theme_adapter)

    def test_save_theme_with_file_path(self, theme_editor, mock_theme_adapter):
        """ファイルパス指定でのテーマ保存テスト"""
        # テストファイルパス
        test_file_path = "/tmp/test_theme.json"

        # テーマ保存を実行
        result = theme_editor.save_theme(test_file_path)

        # 保存が成功したことを確認
        assert result is True

        # theme_adapterのsave_themeが呼ばれたことを確認
        mock_theme_adapter.save_theme.assert_called_once_with(
            theme_editor.current_theme,
            test_file_path
        )

    def test_save_theme_with_dialog(self, theme_editor, mock_qt_adapter, mock_theme_adapter):
        """ダイアログでのテーマ保存テスト"""
        # ファイルダイアログのモック設定
        mock_qt_modules = mock_qt_adapter.get_qt_modules.return_value
        mock_qt_modules['QtWidgets'].QFileDialog.getSaveFileName.return_value = (
            "/tmp/dialog_theme.json",
            "JSONファイル (*.json)"
        )

        # テーマ保存を実行（ファイルパス未指定）
        result = theme_editor.save_theme()

        # 保存が成功したことを確認
        assert result is True

        # ファイルダイアログが呼ばれたことを確認
        mock_qt_modules['QtWidgets'].QFileDialog.getSaveFileName.assert_called_once()

        # theme_adapterのsave_themeが呼ばれたことを確認
        mock_theme_adapter.save_theme.assert_called_once()

    def test_save_theme_dialog_cancel(self, theme_editor, mock_qt_adapter, mock_theme_adapter):
        """ダイアログキャンセル時のテスト"""
        # ファイルダイアログのモック設定（キャンセル）
        mock_qt_modules = mock_qt_adapter.get_qt_modules.return_value
        mock_qt_modules['QtWidgets'].QFileDialog.getSaveFileName.return_value = ("", "")

        # テーマ保存を実行
        result = theme_editor.save_theme()

        # 保存がキャンセルされたことを確認
        assert result is False

        # theme_adapterのsave_themeが呼ばれていないことを確認
        mock_theme_adapter.save_theme.assert_not_called()

    def test_save_theme_validation_error(self, theme_editor, mock_qt_adapter, mock_theme_adapter):
        """テーマ検証エラー時のテスト"""
        # 検証エラーのモック設定
        mock_theme_adapter.validate_theme.return_value = {
            'is_valid': False,
            'errors': ['テーマ名が不正です', '色設定が不足しています'],
            'warnings': []
        }

        # テーマ保存を実行
        result = theme_editor.save_theme("/tmp/invalid_theme.json")

        # 保存が失敗したことを確認
        assert result is False

        # 警告メッセージが表示されたことを確認
        mock_qt_modules = mock_qt_adapter.get_qt_modules.return_value
        mock_qt_modules['QtWidgets'].QMessageBox.warning.assert_called_once()

        # theme_adapterのsave_themeが呼ばれていないことを確認
        mock_theme_adapter.save_theme.assert_not_called()

    def test_save_theme_adapter_error(self, theme_editor, mock_qt_adapter, mock_theme_adapter):
        """ThemeAdapter保存エラー時のテスト"""
        # 保存エラーのモック設定
        mock_theme_adapter.save_theme.return_value = False

        # テーマ保存を実行
        result = theme_editor.save_theme("/tmp/error_theme.json")

        # 保存が失敗したことを確認
        assert result is False

    def test_export_theme_json(self, theme_editor, mock_theme_adapter):
        """JSON形式でのテーマエクスポートテスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # テーマエクスポートを実行
            result = theme_editor.export_theme('json', temp_path)

            # エクスポートが成功したことを確認
            assert result is True

            # theme_adapterのexport_themeが呼ばれたことを確認
            mock_theme_adapter.export_theme.assert_called_once_with(
                theme_editor.current_theme,
                'json'
            )

            # ファイルが作成されたことを確認
            assert os.path.exists(temp_path)

        finally:
            # テンポラリファイルを削除
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_theme_qss(self, theme_editor, mock_theme_adapter):
        """QSS形式でのテーマエクスポートテスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qss', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # QSS形式のエクスポート内容をモック
            mock_theme_adapter.export_theme.return_value = "QPushButton { background-color: #0078d4; }"

            # テーマエクスポートを実行
            result = theme_editor.export_theme('qss', temp_path)

            # エクスポートが成功したことを確認
            assert result is True

            # theme_adapterのexport_themeが呼ばれたことを確認
            mock_theme_adapter.export_theme.assert_called_once_with(
                theme_editor.current_theme,
                'qss'
            )

        finally:
            # テンポラリファイルを削除
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_export_theme_invalid_format(self, theme_editor):
        """無効な形式でのエクスポートテスト"""
        # 無効な形式でエクスポートを実行
        result = theme_editor.export_theme('invalid_format', '/tmp/test.invalid')

        # エクスポートが失敗したことを確認
        assert result is False

    def test_load_theme_from_file(self, theme_editor, mock_theme_adapter):
        """ファイルからのテーマ読み込みテスト"""
        # テストファイルパス
        test_file_path = "/tmp/test_theme.json"

        # テーマ読み込みを実行
        result = theme_editor.load_theme_from_file(test_file_path)

        # 読み込みが成功したことを確認
        assert result is True

        # theme_adapterのload_themeが呼ばれたことを確認
        mock_theme_adapter.load_theme.assert_called_once_with(test_file_path)

        # テーマが適用されたことを確認
        assert theme_editor.current_theme['name'] == 'テストテーマ'

    def test_load_theme_from_file_with_dialog(self, theme_editor, mock_qt_adapter, mock_theme_adapter):
        """ダイアログでのテーマ読み込みテスト"""
        # ファイルダイアログのモック設定
        mock_qt_modules = mock_qt_adapter.get_qt_modules.return_value
        mock_qt_modules['QtWidgets'].QFileDialog.getOpenFileName.return_value = (
            "/tmp/dialog_theme.json",
            "JSONファイル (*.json)"
        )

        # テーマ読み込みを実行（ファイルパス未指定）
        result = theme_editor.load_theme_from_file()

        # 読み込みが成功したことを確認
        assert result is True

        # ファイルダイアログが呼ばれたことを確認
        mock_qt_modules['QtWidgets'].QFileDialog.getOpenFileName.assert_called_once()

        # theme_adapterのload_themeが呼ばれたことを確認
        mock_theme_adapter.load_theme.assert_called_once()

    def test_load_theme_dialog_cancel(self, theme_editor, mock_qt_adapter, mock_theme_adapter):
        """読み込みダイアログキャンセル時のテスト"""
        # ファイルダイアログのモック設定（キャンセル）
        mock_qt_modules = mock_qt_adapter.get_qt_modules.return_value
        mock_qt_modules['QtWidgets'].QFileDialog.getOpenFileName.return_value = ("", "")

        # テーマ読み込みを実行
        result = theme_editor.load_theme_from_file()

        # 読み込みがキャンセルされたことを確認
        assert result is False

        # theme_adapterのload_themeが呼ばれていないことを確認
        mock_theme_adapter.load_theme.assert_not_called()

    def test_save_theme_as(self, theme_editor, mock_qt_adapter, mock_theme_adapter):
        """名前を付けて保存のテスト"""
        # ファイルダイアログのモック設定
        mock_qt_modules = mock_qt_adapter.get_qt_modules.return_value
        mock_qt_modules['QtWidgets'].QFileDialog.getSaveFileName.return_value = (
            "/tmp/save_as_theme.json",
            "JSONファイル (*.json)"
        )

        # 名前を付けて保存を実行
        result = theme_editor.save_theme_as()

        # 保存が成功したことを確認
        assert result is True

        # ファイルダイアログが呼ばれたことを確認
        mock_qt_modules['QtWidgets'].QFileDialog.getSaveFileName.assert_called_once()

        # theme_adapterのsave_themeが呼ばれたことを確認
        mock_theme_adapter.save_theme.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
