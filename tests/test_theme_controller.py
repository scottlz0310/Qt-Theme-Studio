"""
テーマコントローラーのテスト

ThemeControllerクラスの機能をテストします。
特にUndo/Redo機能の動作を検証します。
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from qt_theme_studio.controllers.theme_controller import ThemeController, ThemePropertyChangeCommand
from qt_theme_studio.adapters.qt_adapter import QtFrameworkNotFoundError


class TestThemeController:
    """テーマコントローラーのテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        # Qtフレームワークが利用できない環境でのテスト用モック
        self.qt_modules_mock = {
            'QtWidgets': Mock(),
            'QtCore': Mock(),
            'QtGui': Mock(),
            'framework': 'PySide6'
        }
        
        # QUndoStackのモック
        self.undo_stack_mock = Mock()
        self.undo_stack_mock.setUndoLimit = Mock()
        self.undo_stack_mock.canUndo.return_value = False
        self.undo_stack_mock.canRedo.return_value = False
        self.undo_stack_mock.undoText.return_value = ""
        self.undo_stack_mock.redoText.return_value = ""
        self.undo_stack_mock.count.return_value = 0
        self.undo_stack_mock.index.return_value = 0
        self.undo_stack_mock.undoLimit.return_value = 50
        self.undo_stack_mock.isClean.return_value = True
        self.undo_stack_mock.indexChanged = Mock()
        self.undo_stack_mock.indexChanged.connect = Mock()
        
        # QTimerのモック
        self.timer_mock = Mock()
        self.timer_mock.setSingleShot = Mock()
        self.timer_mock.timeout = Mock()
        self.timer_mock.timeout.connect = Mock()
        self.timer_mock.start = Mock()
        self.timer_mock.stop = Mock()
        self.timer_mock.isActive.return_value = False
        
        # QObjectのモック（シグナル用）
        self.qobject_mock = Mock()
        self.qobject_mock.theme_changed = Mock()
        self.qobject_mock.property_changed = Mock()
        self.qobject_mock.undo_executed = Mock()
        self.qobject_mock.redo_executed = Mock()
        self.qobject_mock.preview_update_requested = Mock()
        
        # シグナルのemitメソッドをモック
        for signal in ['theme_changed', 'property_changed', 'undo_executed', 'redo_executed', 'preview_update_requested']:
            getattr(self.qobject_mock, signal).emit = Mock()
        
        self.qt_modules_mock['QtWidgets'].QUndoStack.return_value = self.undo_stack_mock
        self.qt_modules_mock['QtCore'].QTimer.return_value = self.timer_mock
        self.qt_modules_mock['QtCore'].QObject = Mock(return_value=self.qobject_mock)
        self.qt_modules_mock['QtCore'].Signal = Mock()
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_theme_controller_initialization(self, mock_theme_adapter, mock_qt_adapter):
        """テーマコントローラーの初期化テスト"""
        # QtAdapterのモック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        # ThemeAdapterのモック設定
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # 初期化の確認
        assert controller.current_theme is None
        assert controller.current_theme_path is None
        assert not controller.has_current_theme
        assert not controller.is_theme_modified
        
        # QtAdapterとThemeAdapterが正しく初期化されていることを確認
        mock_qt_adapter.assert_called_once()
        mock_theme_adapter.assert_called_once()
        qt_adapter_instance.get_qt_modules.assert_called_once()
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_create_new_theme(self, mock_theme_adapter, mock_qt_adapter):
        """新規テーマ作成テスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # 新規テーマを作成
        theme_name = "テストテーマ"
        theme_data = controller.create_new_theme(theme_name)
        
        # テーマデータの確認
        assert theme_data is not None
        assert theme_data['name'] == theme_name
        assert theme_data['version'] == "1.0.0"
        assert theme_data['type'] == "custom"
        assert 'colors' in theme_data
        assert 'fonts' in theme_data
        assert 'sizes' in theme_data
        assert 'metadata' in theme_data
        
        # コントローラーの状態確認
        assert controller.current_theme == theme_data
        assert controller.current_theme_path is None
        assert controller.has_current_theme
        
        # UndoStackがクリアされていることを確認（初期化時1回 + 新規テーマ作成時1回）
        assert self.undo_stack_mock.clear.call_count == 2
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_load_theme(self, mock_theme_adapter, mock_qt_adapter):
        """テーマ読み込みテスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        test_theme_data = {
            'name': '読み込みテストテーマ',
            'version': '1.0.0',
            'colors': {'primary': '#ff0000'}
        }
        theme_adapter_instance.load_theme.return_value = test_theme_data
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # テーマを読み込み
        test_path = Path("test_theme.json")
        loaded_theme = controller.load_theme(test_path)
        
        # 読み込み結果の確認
        assert loaded_theme == test_theme_data
        assert controller.current_theme == test_theme_data
        assert controller.current_theme_path == test_path
        assert controller.has_current_theme
        
        # ThemeAdapterのload_themeが呼ばれていることを確認
        theme_adapter_instance.load_theme.assert_called_once_with(test_path)
        
        # UndoStackがクリアされていることを確認（初期化時1回 + テーマ読み込み時1回）
        assert self.undo_stack_mock.clear.call_count == 2
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_save_theme(self, mock_theme_adapter, mock_qt_adapter):
        """テーマ保存テスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        theme_adapter_instance.save_theme.return_value = True
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # テーマを作成
        controller.create_new_theme("保存テストテーマ")
        
        # テーマを保存
        save_path = Path("saved_theme.json")
        result = controller.save_theme(save_path)
        
        # 保存結果の確認
        assert result is True
        assert controller.current_theme_path == save_path
        
        # ThemeAdapterのsave_themeが呼ばれていることを確認
        theme_adapter_instance.save_theme.assert_called_once()
        
        # メタデータが更新されていることを確認
        assert 'modified_at' in controller.current_theme['metadata']
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_change_theme_property(self, mock_theme_adapter, mock_qt_adapter):
        """テーマプロパティ変更テスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # テーマを作成
        controller.create_new_theme("プロパティ変更テストテーマ")
        
        # プロパティを変更
        old_color = controller.current_theme['colors']['primary']
        new_color = "#ff0000"
        result = controller.change_theme_property("colors.primary", new_color, "色変更テスト")
        
        # 変更結果の確認
        assert result is True
        
        # UndoStackにコマンドが追加されていることを確認
        self.undo_stack_mock.push.assert_called_once()
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_undo_redo_operations(self, mock_theme_adapter, mock_qt_adapter):
        """Undo/Redo操作テスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # Undo操作のテスト
        self.undo_stack_mock.canUndo.return_value = True
        result = controller.undo_last_action()
        assert result is True
        self.undo_stack_mock.undo.assert_called_once()
        
        # Redo操作のテスト
        self.undo_stack_mock.canRedo.return_value = True
        result = controller.redo_last_action()
        assert result is True
        self.undo_stack_mock.redo.assert_called_once()
        
        # Undoできない場合のテスト
        self.undo_stack_mock.canUndo.return_value = False
        result = controller.undo_last_action()
        assert result is False
        
        # Redoできない場合のテスト
        self.undo_stack_mock.canRedo.return_value = False
        result = controller.redo_last_action()
        assert result is False
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_clear_undo_history(self, mock_theme_adapter, mock_qt_adapter):
        """操作履歴クリアテスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # 操作履歴をクリア
        controller.clear_undo_history()
        
        # UndoStackのclearが呼ばれていることを確認
        # 初期化時に1回、clear_undo_history呼び出し時に1回の計2回呼ばれる
        assert self.undo_stack_mock.clear.call_count == 2
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_get_undo_history_info(self, mock_theme_adapter, mock_qt_adapter):
        """操作履歴情報取得テスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # 操作履歴情報を取得
        history_info = controller.get_undo_history_info()
        
        # 情報の確認
        assert isinstance(history_info, dict)
        assert 'can_undo' in history_info
        assert 'can_redo' in history_info
        assert 'undo_text' in history_info
        assert 'redo_text' in history_info
        assert 'count' in history_info
        assert 'index' in history_info
        assert 'limit' in history_info
        
        # 初期状態の確認
        assert history_info['can_undo'] is False
        assert history_info['can_redo'] is False
        assert history_info['limit'] == 50
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_theme_change_callbacks(self, mock_theme_adapter, mock_qt_adapter):
        """テーマ変更コールバックテスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # コールバック関数のモック
        callback_mock = Mock()
        
        # コールバックを追加
        controller.add_theme_change_callback(callback_mock)
        
        # テーマを作成（コールバックが呼ばれるはず）
        theme_data = controller.create_new_theme("コールバックテストテーマ")
        
        # コールバックが呼ばれていることを確認
        callback_mock.assert_called_once_with(theme_data)
        
        # コールバックを削除
        controller.remove_theme_change_callback(callback_mock)
        
        # 再度テーマを変更（コールバックは呼ばれないはず）
        callback_mock.reset_mock()
        controller.create_new_theme("コールバックテストテーマ2")
        
        # コールバックが呼ばれていないことを確認
        callback_mock.assert_not_called()
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_preview_update_callbacks(self, mock_theme_adapter, mock_qt_adapter):
        """プレビュー更新コールバックテスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # プレビュー更新コールバック関数のモック
        preview_callback_mock = Mock()
        
        # コールバックを追加
        controller.add_preview_update_callback(preview_callback_mock)
        
        # コールバックが追加されていることを確認
        assert preview_callback_mock in controller._preview_update_callbacks
        
        # プレビュー更新を直接実行（pending状態を設定）
        controller._pending_preview_update = True
        controller._execute_preview_update()
        
        # コールバックが呼ばれていることを確認
        preview_callback_mock.assert_called_once_with(controller.current_theme)
        
        # コールバックを削除
        controller.remove_preview_update_callback(preview_callback_mock)
        
        # コールバックが削除されていることを確認
        assert preview_callback_mock not in controller._preview_update_callbacks
        
        # 再度プレビュー更新を実行（コールバックは呼ばれないはず）
        preview_callback_mock.reset_mock()
        controller._pending_preview_update = True
        controller._execute_preview_update()
        
        # コールバックが呼ばれていないことを確認
        preview_callback_mock.assert_not_called()
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_undo_redo_callbacks(self, mock_theme_adapter, mock_qt_adapter):
        """Undo/Redoコールバックテスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # Undo/Redoコールバック関数のモック
        undo_redo_callback_mock = Mock()
        
        # コールバックを追加
        controller.add_undo_redo_callback(undo_redo_callback_mock)
        
        # Undo操作のテスト
        self.undo_stack_mock.canUndo.return_value = True
        self.undo_stack_mock.undoText.return_value = "テスト操作"
        controller.undo_last_action()
        
        # コールバックが呼ばれていることを確認
        undo_redo_callback_mock.assert_called_with("undo", "テスト操作")
        
        # Redo操作のテスト
        undo_redo_callback_mock.reset_mock()
        self.undo_stack_mock.canRedo.return_value = True
        self.undo_stack_mock.redoText.return_value = "テスト操作"
        controller.redo_last_action()
        
        # コールバックが呼ばれていることを確認
        undo_redo_callback_mock.assert_called_with("redo", "テスト操作")
        
        # コールバックを削除
        controller.remove_undo_redo_callback(undo_redo_callback_mock)
        
        # 再度Undo操作を実行（コールバックは呼ばれないはず）
        undo_redo_callback_mock.reset_mock()
        controller.undo_last_action()
        
        # コールバックが呼ばれていないことを確認
        undo_redo_callback_mock.assert_not_called()
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_force_preview_update(self, mock_theme_adapter, mock_qt_adapter):
        """プレビュー強制更新テスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # プレビュー更新コールバック関数のモック
        preview_callback_mock = Mock()
        controller.add_preview_update_callback(preview_callback_mock)
        
        # プレビューの強制更新を実行
        controller.force_preview_update()
        
        # コールバックが呼ばれていることを確認
        preview_callback_mock.assert_called_once_with(controller.current_theme)
    
    @patch('qt_theme_studio.controllers.theme_controller.QtAdapter')
    @patch('qt_theme_studio.controllers.theme_controller.ThemeAdapter')
    def test_get_preview_update_status(self, mock_theme_adapter, mock_qt_adapter):
        """プレビュー更新状態取得テスト"""
        # モック設定
        qt_adapter_instance = Mock()
        qt_adapter_instance.get_qt_modules.return_value = self.qt_modules_mock
        mock_qt_adapter.return_value = qt_adapter_instance
        
        theme_adapter_instance = Mock()
        mock_theme_adapter.return_value = theme_adapter_instance
        
        # テーマコントローラーを初期化
        controller = ThemeController()
        
        # プレビュー更新状態を取得
        status = controller.get_preview_update_status()
        
        # 状態の確認
        assert isinstance(status, dict)
        assert 'pending_update' in status
        assert 'timer_active' in status
        assert 'callback_count' in status
        
        # 初期状態の確認
        assert status['pending_update'] is False
        assert status['timer_active'] is False
        assert status['callback_count'] == 0


class TestThemePropertyChangeCommand:
    """テーマプロパティ変更コマンドのテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.mock_controller = Mock()
        self.mock_controller.current_theme = {
            'colors': {
                'primary': '#3498db'
            }
        }
        self.mock_controller._notify_theme_changed = Mock()
    
    def test_command_initialization(self):
        """コマンドの初期化テスト"""
        command = ThemePropertyChangeCommand(
            self.mock_controller,
            "colors.primary",
            "#3498db",
            "#ff0000",
            "色変更テスト"
        )
        
        assert command.theme_controller == self.mock_controller
        assert command.property_path == "colors.primary"
        assert command.old_value == "#3498db"
        assert command.new_value == "#ff0000"
        assert command.description == "色変更テスト"
    
    def test_command_redo_undo(self):
        """コマンドのRedo/Undoテスト"""
        command = ThemePropertyChangeCommand(
            self.mock_controller,
            "colors.primary",
            "#3498db",
            "#ff0000",
            "色変更テスト"
        )
        
        # Redo操作のテスト
        command.redo()
        
        # テーマが変更されていることを確認
        assert self.mock_controller.current_theme['colors']['primary'] == "#ff0000"
        self.mock_controller._notify_theme_changed.assert_called()
        
        # Undo操作のテスト
        self.mock_controller._notify_theme_changed.reset_mock()
        command.undo()
        
        # テーマが元に戻っていることを確認
        assert self.mock_controller.current_theme['colors']['primary'] == "#3498db"
        self.mock_controller._notify_theme_changed.assert_called()


if __name__ == '__main__':
    pytest.main([__file__])