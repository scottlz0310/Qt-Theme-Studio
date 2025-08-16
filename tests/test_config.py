"""
設定管理システムのテスト

ApplicationSettings、SettingsManager、UserPreferences、WorkspaceManagerの
テストを行います。
"""

import tempfile
import unittest
from unittest.mock import Mock, patch

from qt_theme_studio.config import (
    ApplicationSettings,
    SettingsManager,
    UserPreferences,
    WorkspaceManager,
    get_default_settings,
)


class TestApplicationSettings(unittest.TestCase):
    """ApplicationSettingsクラスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.settings = ApplicationSettings(config_dir=self.temp_dir)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """初期化のテスト"""
        self.assertIsInstance(self.settings, ApplicationSettings)
        self.assertTrue(self.settings.config_dir.exists())
        self.assertEqual(self.settings.config_dir, Path(self.temp_dir))

    def test_load_default_settings(self):
        """デフォルト設定の読み込みテスト"""
        settings_data = self.settings.load_settings()

        # デフォルト設定が含まれていることを確認
        self.assertIn('window', settings_data)
        self.assertIn('theme', settings_data)
        self.assertIn('editor', settings_data)
        self.assertIn('ui', settings_data)
        self.assertIn('export', settings_data)

        # 設定ファイルが作成されていることを確認
        self.assertTrue(self.settings.settings_file.exists())

    def test_save_and_load_settings(self):
        """設定の保存と読み込みテスト"""
        test_settings = {
            'window': {'width': 1000, 'height': 600},
            'theme': {'recent_themes': ['/test/theme.json']},
            'test_key': 'test_value'
        }

        # 設定を保存
        self.settings.save_settings(test_settings)

        # 新しいインスタンスで読み込み
        new_settings = ApplicationSettings(config_dir=self.temp_dir)
        loaded_settings = new_settings.load_settings()

        # 保存した値が正しく読み込まれることを確認
        self.assertEqual(loaded_settings['window']['width'], 1000)
        self.assertEqual(loaded_settings['theme']['recent_themes'], ['/test/theme.json'])
        self.assertEqual(loaded_settings['test_key'], 'test_value')

    def test_recent_themes_management(self):
        """最近使用したテーマリストの管理テスト"""
        # テーマファイルを作成
        theme_file = Path(self.temp_dir) / "test_theme.json"
        theme_file.write_text('{"name": "test"}')

        # テーマを追加
        self.settings.add_recent_theme(str(theme_file))
        recent_themes = self.settings.get_recent_themes()

        self.assertEqual(len(recent_themes), 1)
        self.assertEqual(recent_themes[0], str(theme_file.absolute()))

        # 同じテーマを再度追加（重複しないことを確認）
        self.settings.add_recent_theme(str(theme_file))
        recent_themes = self.settings.get_recent_themes()
        self.assertEqual(len(recent_themes), 1)

        # テーマを削除
        self.settings.remove_recent_theme(str(theme_file))
        recent_themes = self.settings.get_recent_themes()
        self.assertEqual(len(recent_themes), 0)

    def test_get_set_setting(self):
        """設定値の取得・設定テスト"""
        # 設定値を設定
        self.settings.set_setting('window.width', 1500)
        self.settings.set_setting('theme.auto_save', False)

        # 設定値を取得
        width = self.settings.get_setting('window.width')
        auto_save = self.settings.get_setting('theme.auto_save')

        self.assertEqual(width, 1500)
        self.assertEqual(auto_save, False)

        # 存在しないキーのデフォルト値テスト
        non_existent = self.settings.get_setting('non.existent', 'default')
        self.assertEqual(non_existent, 'default')

    def test_reset_to_defaults(self):
        """デフォルト値へのリセットテスト"""
        # カスタム設定を保存
        self.settings.set_setting('window.width', 2000)

        # デフォルトにリセット
        self.settings.reset_to_defaults()

        # デフォルト値が復元されることを確認
        default_settings = get_default_settings()
        width = self.settings.get_setting('window.width')
        self.assertEqual(width, default_settings['window']['width'])


class TestSettingsManager(unittest.TestCase):
    """SettingsManagerクラスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        # QtAdapterをモック
        self.qt_adapter_mock = Mock()
        self.qt_core_mock = Mock()
        self.qsettings_mock = Mock()

        self.qt_adapter_mock.get_qt_modules.return_value = {
            'QtCore': self.qt_core_mock
        }
        self.qt_core_mock.QSettings.return_value = self.qsettings_mock

    @patch('qt_theme_studio.config.persistence.QtAdapter')
    def test_initialization(self, mock_qt_adapter):
        """初期化のテスト"""
        mock_qt_adapter.return_value = self.qt_adapter_mock

        settings_manager = SettingsManager()

        self.assertIsInstance(settings_manager, SettingsManager)
        mock_qt_adapter.assert_called_once()
        self.qt_adapter_mock.get_qt_modules.assert_called_once()

    @patch('qt_theme_studio.config.persistence.QtAdapter')
    def test_save_load_value(self, mock_qt_adapter):
        """値の保存・読み込みテスト"""
        mock_qt_adapter.return_value = self.qt_adapter_mock

        settings_manager = SettingsManager()

        # 値を保存
        settings_manager.save_value('test_key', 'test_value')
        self.qsettings_mock.setValue.assert_called_with('test_key', 'test_value')
        self.qsettings_mock.sync.assert_called()

        # 値を読み込み
        self.qsettings_mock.value.return_value = 'test_value'
        value = settings_manager.load_value('test_key', 'default')
        self.qsettings_mock.value.assert_called_with('test_key', 'default')
        self.assertEqual(value, 'test_value')


class TestUserPreferences(unittest.TestCase):
    """UserPreferencesクラスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.settings_manager_mock = Mock()
        self.user_preferences = UserPreferences(self.settings_manager_mock)

    def test_get_set_preference(self):
        """設定の取得・設定テスト"""
        # 設定を保存
        self.user_preferences.set_preference('ui/theme', 'dark')
        self.settings_manager_mock.save_value.assert_called_with('preferences/ui/theme', 'dark')

        # 設定を取得
        self.settings_manager_mock.load_value.return_value = 'dark'
        theme = self.user_preferences.get_preference('ui/theme')
        self.settings_manager_mock.load_value.assert_called_with('preferences/ui/theme', 'default')
        self.assertEqual(theme, 'dark')

    def test_default_values(self):
        """デフォルト値のテスト"""
        # デフォルト値が設定されているキーをテスト
        self.settings_manager_mock.load_value.return_value = 'ja'
        self.user_preferences.get_preference('ui/language')

        # デフォルト値が使用されることを確認
        self.settings_manager_mock.load_value.assert_called_with('preferences/ui/language', 'ja')


class TestWorkspaceManager(unittest.TestCase):
    """WorkspaceManagerクラスのテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.settings_manager_mock = Mock()
        self.workspace_manager = WorkspaceManager(self.settings_manager_mock)

    def test_save_load_workspace(self):
        """ワークスペースの保存・読み込みテスト"""
        workspace_data = {
            'open_files': ['/path/to/file1.json', '/path/to/file2.json'],
            'active_file': '/path/to/file1.json',
            'recent_files': ['/path/to/recent.json'],
            'editor_state': {'zoom': 100}
        }

        # ワークスペースを保存
        self.workspace_manager.save_workspace(workspace_data)

        # 保存メソッドが呼ばれることを確認
        self.settings_manager_mock.begin_group.assert_called_with('workspace')
        self.settings_manager_mock.save_value.assert_any_call('open_files', workspace_data['open_files'])
        self.settings_manager_mock.save_value.assert_any_call('active_file', workspace_data['active_file'])
        self.settings_manager_mock.end_group.assert_called()
        self.settings_manager_mock.sync.assert_called()

        # ワークスペースを読み込み
        self.settings_manager_mock.load_value.side_effect = lambda key, default: workspace_data.get(key.split('/')[-1], default)
        loaded_data = self.workspace_manager.load_workspace()

        # 読み込みメソッドが呼ばれることを確認
        self.settings_manager_mock.begin_group.assert_called_with('workspace')
        self.assertEqual(loaded_data['open_files'], workspace_data['open_files'])
        self.assertEqual(loaded_data['active_file'], workspace_data['active_file'])


if __name__ == '__main__':
    unittest.main()
