"""
メインウィンドウのテスト

このモジュールは、MainWindowクラスの基本機能をテストします。
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

# テスト対象のインポート
from qt_theme_studio.views.main_window import MainWindow
from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.config.settings import ApplicationSettings


class TestMainWindow:
    """MainWindowクラスのテストクラス"""
    
    @pytest.fixture
    def mock_qt_adapter(self):
        """モックQtAdapterを作成"""
        adapter = Mock(spec=QtAdapter)
        
        # モックQtモジュール
        mock_qt_modules = {
            'QtWidgets': Mock(),
            'QtCore': Mock(),
            'QtGui': Mock(),
            'framework': 'PySide6'
        }
        
        # QMainWindowのモック
        mock_main_window = Mock()
        mock_qt_modules['QtWidgets'].QMainWindow.return_value = mock_main_window
        
        # QActionのモック
        mock_qt_modules['QtGui'].QAction = Mock()
        
        # QKeySequenceのモック
        mock_key_sequence = Mock()
        mock_key_sequence.StandardKey = Mock()
        mock_key_sequence.StandardKey.New = "Ctrl+N"
        mock_key_sequence.StandardKey.Open = "Ctrl+O"
        mock_key_sequence.StandardKey.Save = "Ctrl+S"
        mock_key_sequence.StandardKey.SaveAs = "Ctrl+Shift+S"
        mock_key_sequence.StandardKey.Quit = "Ctrl+Q"
        mock_key_sequence.StandardKey.Undo = "Ctrl+Z"
        mock_key_sequence.StandardKey.Redo = "Ctrl+Y"
        mock_key_sequence.StandardKey.FullScreen = "F11"
        mock_key_sequence.StandardKey.HelpContents = "F1"
        mock_qt_modules['QtGui'].QKeySequence = mock_key_sequence
        
        # QMessageBoxのモック
        mock_message_box = Mock()
        mock_message_box.StandardButton = Mock()
        mock_message_box.StandardButton.Yes = 1
        mock_message_box.StandardButton.No = 2
        mock_message_box.question.return_value = mock_message_box.StandardButton.No
        mock_qt_modules['QtWidgets'].QMessageBox = mock_message_box
        
        # QWidgetのモック
        mock_qt_modules['QtWidgets'].QWidget = Mock()
        
        # QHBoxLayoutのモック
        mock_qt_modules['QtWidgets'].QHBoxLayout = Mock()
        
        # QLabelのモック
        mock_qt_modules['QtWidgets'].QLabel = Mock()
        
        # QApplicationのモック
        mock_app = Mock()
        mock_app.primaryScreen.return_value.availableGeometry.return_value.center.return_value = Mock()
        mock_qt_modules['QtWidgets'].QApplication = mock_app
        
        # Qtのモック
        mock_qt = Mock()
        mock_qt.AlignmentFlag = Mock()
        mock_qt.AlignmentFlag.AlignCenter = 1
        mock_qt.ToolButtonStyle = Mock()
        mock_qt.ToolButtonStyle.ToolButtonTextUnderIcon = 1
        mock_qt_modules['QtCore'].Qt = mock_qt
        
        adapter.get_qt_modules.return_value = mock_qt_modules
        adapter.get_framework_info.return_value = {'name': 'PySide6', 'version': '6.0.0'}
        
        return adapter
    
    @pytest.fixture
    def mock_settings(self):
        """モックApplicationSettingsを作成"""
        settings = Mock(spec=ApplicationSettings)
        settings.get_setting.return_value = 1200  # デフォルト値
        settings.get_recent_themes.return_value = []
        
        # モック設定管理
        mock_settings_manager = Mock()
        mock_user_preferences = Mock()
        mock_workspace_manager = Mock()
        
        settings.get_settings_manager.return_value = mock_settings_manager
        settings.get_user_preferences.return_value = mock_user_preferences
        settings.get_workspace_manager.return_value = mock_workspace_manager
        settings.restore_window_state.return_value = True
        
        return settings
    
    @pytest.fixture
    def main_window(self, mock_qt_adapter, mock_settings):
        """MainWindowインスタンスを作成"""
        with patch('qt_theme_studio.views.main_window.get_logger') as mock_logger:
            mock_logger.return_value = Mock()
            # MainWindowの実際のコンストラクタに合わせて引数を追加
            mock_theme_adapter = Mock()
            mock_i18n_manager = Mock()
            mock_file_handler = Mock()
            mock_accessibility_manager = Mock()
            
            return MainWindow(
                mock_qt_adapter, 
                mock_theme_adapter,
                mock_settings,
                mock_i18n_manager,
                mock_file_handler,
                mock_accessibility_manager
            )
    
    def test_init(self, main_window, mock_qt_adapter, mock_settings):
        """初期化のテスト"""
        assert main_window.qt_adapter == mock_qt_adapter
        assert main_window.settings == mock_settings
        # 初期化時にcreate_window()が呼ばれるため、main_windowはNoneではない
        assert main_window.main_window is not None
        assert isinstance(main_window.actions, dict)
    
    def test_create_window(self, main_window):
        """ウィンドウ作成のテスト"""
        window = main_window.create_window()
        
        assert window is not None
        assert main_window.main_window is not None
        assert main_window.is_created() is True
    
    def test_create_window_idempotent(self, main_window):
        """ウィンドウ作成の冪等性テスト"""
        window1 = main_window.create_window()
        window2 = main_window.create_window()
        
        assert window1 is window2
    
    def test_setup_window_properties(self, main_window):
        """ウィンドウプロパティ設定のテスト"""
        main_window.create_window()
        
        # ウィンドウタイトルが設定されていることを確認
        main_window.main_window.setWindowTitle.assert_called_with("Qt-Theme-Studio - テーマエディター")
        
        # ウィンドウサイズが設定されていることを確認
        main_window.main_window.resize.assert_called()
        
        # 最小サイズが設定されていることを確認
        main_window.main_window.setMinimumSize.assert_called_with(800, 600)
    
    def test_menu_creation(self, main_window):
        """メニュー作成のテスト"""
        main_window.create_window()
        
        # メニューバーが取得されていることを確認
        main_window.main_window.menuBar.assert_called()
        
        # 主要なアクションが作成されていることを確認
        expected_actions = [
            'new_theme', 'open_theme', 'save_theme', 'save_as_theme', 'exit',
            'undo', 'redo', 'preferences', 'reset_workspace',
            'theme_editor', 'zebra_editor', 'theme_gallery', 'theme_templates',
            'live_preview', 'toolbar', 'statusbar', 'fullscreen',
            'accessibility_check', 'contrast_calculator', 'export_preview',
            'help', 'user_manual', 'about', 'about_qt'
        ]
        
        for action_name in expected_actions:
            assert action_name in main_window.actions
    
    def test_toolbar_setup(self, main_window):
        """ツールバー設定のテスト"""
        main_window.create_window()
        
        # ツールバーが追加されていることを確認
        main_window.main_window.addToolBar.assert_called_with("メインツールバー")
    
    def test_status_bar_setup(self, main_window):
        """ステータスバー設定のテスト"""
        main_window.create_window()
        
        # ステータスバーが取得されていることを確認
        main_window.main_window.statusBar.assert_called()
    
    def test_get_action(self, main_window):
        """アクション取得のテスト"""
        main_window.create_window()
        
        # 存在するアクションの取得
        action = main_window.get_action('new_theme')
        assert action is not None
        
        # 存在しないアクションの取得
        action = main_window.get_action('nonexistent')
        assert action is None
    
    def test_set_status_message(self, main_window):
        """ステータスメッセージ設定のテスト"""
        main_window.create_window()
        
        main_window.set_status_message("テストメッセージ", 1000)
        
        # ステータスバーにメッセージが設定されていることを確認
        main_window.status_bar.showMessage.assert_called_with("テストメッセージ", 1000)
    
    def test_update_theme_status(self, main_window):
        """テーマステータス更新のテスト"""
        main_window.create_window()
        
        main_window.update_theme_status("テストテーマ")
        
        # テーマラベルが更新されていることを確認
        main_window.status_theme_label.setText.assert_called_with("テーマ: テストテーマ")
    
    def test_set_actions_enabled(self, main_window):
        """アクション有効/無効設定のテスト"""
        main_window.create_window()
        
        main_window.set_actions_enabled(['save_theme', 'save_as_theme'], True)
        
        # アクションが有効化されていることを確認
        main_window.actions['save_theme'].setEnabled.assert_called_with(True)
        main_window.actions['save_as_theme'].setEnabled.assert_called_with(True)
    
    def test_connect_action(self, main_window):
        """アクション接続のテスト"""
        main_window.create_window()
        
        mock_slot = Mock()
        result = main_window.connect_action('new_theme', mock_slot)
        
        assert result is True
        main_window.actions['new_theme'].triggered.connect.assert_called_with(mock_slot)
    
    def test_connect_nonexistent_action(self, main_window):
        """存在しないアクション接続のテスト"""
        main_window.create_window()
        
        mock_slot = Mock()
        result = main_window.connect_action('nonexistent', mock_slot)
        
        assert result is False
    
    def test_toggle_toolbar(self, main_window):
        """ツールバー表示切り替えのテスト"""
        main_window.create_window()
        
        main_window.toggle_toolbar(False)
        
        main_window.tool_bar.setVisible.assert_called_with(False)
        main_window.actions['toolbar'].setChecked.assert_called_with(False)
    
    def test_toggle_statusbar(self, main_window):
        """ステータスバー表示切り替えのテスト"""
        main_window.create_window()
        
        main_window.toggle_statusbar(False)
        
        main_window.status_bar.setVisible.assert_called_with(False)
        main_window.actions['statusbar'].setChecked.assert_called_with(False)
    
    def test_reset_workspace_cancel(self, main_window):
        """ワークスペースリセットキャンセルのテスト"""
        main_window.create_window()
        
        # キャンセルを選択
        main_window.QtWidgets.QMessageBox.question.return_value = \
            main_window.QtWidgets.QMessageBox.StandardButton.No
        
        main_window.reset_workspace()
        
        # 確認ダイアログが表示されることを確認
        main_window.QtWidgets.QMessageBox.question.assert_called()
    
    def test_reset_workspace_confirm(self, main_window):
        """ワークスペースリセット実行のテスト"""
        main_window.create_window()
        
        # 実行を選択
        main_window.QtWidgets.QMessageBox.question.return_value = \
            main_window.QtWidgets.QMessageBox.StandardButton.Yes
        
        main_window.reset_workspace()
        
        # 確認ダイアログが表示されることを確認
        main_window.QtWidgets.QMessageBox.question.assert_called()
    
    def test_save_window_state(self, main_window):
        """ウィンドウ状態保存のテスト"""
        main_window.create_window()
        
        main_window.save_window_state()
        
        # 設定管理の保存メソッドが呼ばれることを確認
        main_window.settings.save_window_state.assert_called_with(main_window.main_window)
    
    def test_show(self, main_window):
        """ウィンドウ表示のテスト"""
        main_window.create_window()
        
        main_window.show()
        
        main_window.main_window.show.assert_called()
    
    def test_close(self, main_window):
        """ウィンドウクローズのテスト"""
        main_window.create_window()
        main_window.main_window.close.return_value = True
        
        result = main_window.close()
        
        assert result is True
        main_window.main_window.close.assert_called()
    
    def test_get_window(self, main_window):
        """ウィンドウインスタンス取得のテスト"""
        # 初期化時に既にウィンドウが作成されている
        assert main_window.get_window() is not None
        
        # 同じインスタンスが返されることを確認
        window1 = main_window.get_window()
        window2 = main_window.get_window()
        assert window1 is window2
    
    def test_save_layout_state(self, main_window):
        """レイアウト状態保存のテスト"""
        main_window.create_window()
        
        # モックの設定
        main_window.main_window.saveGeometry.return_value = b'geometry_data'
        main_window.main_window.saveState.return_value = b'state_data'
        main_window.main_window.isMaximized.return_value = False
        main_window.main_window.isFullScreen.return_value = False
        
        layout_state = main_window.save_layout_state()
        
        assert 'window' in layout_state
        assert 'toolbar' in layout_state
        assert 'statusbar' in layout_state
        assert 'actions' in layout_state
    
    def test_get_current_workspace_state(self, main_window):
        """現在のワークスペース状態取得のテスト"""
        main_window.create_window()
        
        workspace_state = main_window.get_current_workspace_state()
        
        assert 'layout' in workspace_state
        assert 'current_theme' in workspace_state
        assert 'editor_state' in workspace_state
        assert 'preview_state' in workspace_state


if __name__ == '__main__':
    pytest.main([__file__])