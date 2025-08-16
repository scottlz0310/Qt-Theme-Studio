"""
設定管理システムの統合テスト

ApplicationSettingsとQSettings統合機能の統合テストを行います。
"""

import tempfile
import unittest
from unittest.mock import Mock, patch

from qt_theme_studio.config import ApplicationSettings


class TestConfigIntegration(unittest.TestCase):
    """設定管理システムの統合テスト"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.settings = ApplicationSettings(config_dir=self.temp_dir)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_settings_workflow(self):
        """完全な設定ワークフローのテスト"""
        # 1. デフォルト設定の読み込み
        settings_data = self.settings.load_settings()
        self.assertIsInstance(settings_data, dict)
        self.assertIn('window', settings_data)

        # 2. 最近使用したテーマの管理
        theme_file = Path(self.temp_dir) / "test_theme.json"
        theme_file.write_text('{"name": "test_theme", "version": "1.0"}')

        self.settings.add_recent_theme(str(theme_file))
        recent_themes = self.settings.get_recent_themes()
        self.assertEqual(len(recent_themes), 1)
        self.assertIn(str(theme_file.absolute()), recent_themes)

        # 3. 設定値の変更
        self.settings.set_setting('window.width', 1600)
        self.settings.set_setting('theme.auto_save', False)

        # 4. 設定の保存と再読み込み
        current_settings = self.settings.settings
        self.settings.save_settings(current_settings)

        # 新しいインスタンスで確認
        new_settings = ApplicationSettings(config_dir=self.temp_dir)
        loaded_settings = new_settings.load_settings()

        self.assertEqual(loaded_settings['window']['width'], 1600)
        self.assertEqual(loaded_settings['theme']['auto_save'], False)
        self.assertEqual(len(new_settings.get_recent_themes()), 1)

    @patch('qt_theme_studio.config.persistence.QtAdapter')
    def test_qsettings_integration(self, mock_qt_adapter):
        """QSettings統合のテスト"""
        # QtAdapterをモック
        qt_core_mock = Mock()
        qsettings_mock = Mock()

        mock_qt_adapter.return_value.get_qt_modules.return_value = {
            'QtCore': qt_core_mock
        }
        qt_core_mock.QSettings.return_value = qsettings_mock

        # SettingsManagerの取得
        settings_manager = self.settings.get_settings_manager()
        self.assertIsNotNone(settings_manager)

        # UserPreferencesの取得
        user_preferences = self.settings.get_user_preferences()
        self.assertIsNotNone(user_preferences)

        # WorkspaceManagerの取得
        workspace_manager = self.settings.get_workspace_manager()
        self.assertIsNotNone(workspace_manager)

        # 同じインスタンスが返されることを確認（シングルトン的動作）
        self.assertIs(settings_manager, self.settings.get_settings_manager())
        self.assertIs(user_preferences, self.settings.get_user_preferences())
        self.assertIs(workspace_manager, self.settings.get_workspace_manager())

    @patch('qt_theme_studio.config.persistence.QtAdapter')
    def test_user_preferences_integration(self, mock_qt_adapter):
        """ユーザー設定統合のテスト"""
        # QtAdapterをモック
        qt_core_mock = Mock()
        qsettings_mock = Mock()

        mock_qt_adapter.return_value.get_qt_modules.return_value = {
            'QtCore': qt_core_mock
        }
        qt_core_mock.QSettings.return_value = qsettings_mock

        # ユーザー設定の保存・取得
        self.settings.set_user_preference('ui/theme', 'dark')

        qsettings_mock.value.return_value = 'dark'
        theme = self.settings.get_user_preference('ui/theme')

        # QSettingsが呼ばれることを確認
        qsettings_mock.setValue.assert_called()
        qsettings_mock.value.assert_called()
        self.assertEqual(theme, 'dark')

    @patch('qt_theme_studio.config.persistence.QtAdapter')
    def test_workspace_state_integration(self, mock_qt_adapter):
        """ワークスペース状態統合のテスト"""
        # QtAdapterをモック
        qt_core_mock = Mock()
        qsettings_mock = Mock()

        mock_qt_adapter.return_value.get_qt_modules.return_value = {
            'QtCore': qt_core_mock
        }
        qt_core_mock.QSettings.return_value = qsettings_mock

        # ワークスペース状態の保存・読み込み
        workspace_data = {
            'open_files': ['/test/file1.json', '/test/file2.json'],
            'active_file': '/test/file1.json',
            'recent_files': ['/test/recent.json']
        }

        self.settings.save_workspace_state(workspace_data)

        # QSettingsが呼ばれることを確認
        qsettings_mock.beginGroup.assert_called_with('workspace')
        qsettings_mock.setValue.assert_called()
        qsettings_mock.endGroup.assert_called()
        qsettings_mock.sync.assert_called()

        # ワークスペース状態の読み込み
        qsettings_mock.value.side_effect = lambda key, default: workspace_data.get(key, default)
        self.settings.load_workspace_state()

        # 読み込みメソッドが呼ばれることを確認
        qsettings_mock.beginGroup.assert_called_with('workspace')

    def test_settings_file_persistence(self):
        """設定ファイルの永続化テスト"""
        # 設定を変更
        self.settings.set_setting('window.width', 1800)
        self.settings.add_recent_theme('/test/theme1.json')

        # 設定ファイルが存在することを確認
        self.assertTrue(self.settings.settings_file.exists())

        # ファイル内容を確認
        import json
        with open(self.settings.settings_file, 'r', encoding='utf-8') as f:
            file_data = json.load(f)

        self.assertEqual(file_data['window']['width'], 1800)
        # recent_themesは存在しないファイルなので除外される

        # 新しいインスタンスで設定が復元されることを確認
        new_settings = ApplicationSettings(config_dir=self.temp_dir)
        loaded_data = new_settings.load_settings()

        self.assertEqual(loaded_data['window']['width'], 1800)

    def test_config_directory_creation(self):
        """設定ディレクトリの作成テスト"""
        # 存在しないディレクトリを指定
        non_existent_dir = Path(self.temp_dir) / "non_existent" / "config"

        # ApplicationSettingsを作成
        settings = ApplicationSettings(config_dir=non_existent_dir)

        # ディレクトリが作成されることを確認
        self.assertTrue(non_existent_dir.exists())
        self.assertTrue(settings.config_dir.exists())

    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 無効なJSONファイルを作成
        invalid_json_file = self.settings.settings_file
        invalid_json_file.write_text('invalid json content')

        # エラーが発生してもデフォルト設定が使用されることを確認
        settings_data = self.settings.load_settings()
        self.assertIsInstance(settings_data, dict)
        self.assertIn('window', settings_data)

        # 設定ファイルが修正されることを確認
        self.assertTrue(invalid_json_file.exists())

        # 再読み込みで正常に動作することを確認
        new_settings = ApplicationSettings(config_dir=self.temp_dir)
        new_data = new_settings.load_settings()
        self.assertIsInstance(new_data, dict)


if __name__ == '__main__':
    unittest.main()
