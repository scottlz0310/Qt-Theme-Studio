"""
テーマエディターのテスト

このモジュールは、ThemeEditorクラスの単体テストを実装します。
"""

import pytest
import sys
from unittest.mock import Mock, patch

# テスト対象のインポート
from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.adapters.theme_adapter import ThemeAdapter
from qt_theme_studio.views.theme_editor import ThemeEditor, ColorPicker


class TestColorPicker:
    """ColorPickerクラスのテスト"""
    
    @pytest.fixture
    def mock_qt_modules(self):
        """モックQtモジュールを作成"""
        mock_modules = {
            'QtWidgets': Mock(),
            'QtCore': Mock(),
            'QtGui': Mock()
        }
        
        # QColorのモック
        mock_color = Mock()
        mock_color.name.return_value = "#ffffff"
        mock_color.red.return_value = 255
        mock_color.green.return_value = 255
        mock_color.blue.return_value = 255
        mock_color.isValid.return_value = True
        mock_modules['QtGui'].QColor.return_value = mock_color
        
        return mock_modules
    
    def test_color_picker_initialization(self, mock_qt_modules):
        """カラーピッカーの初期化テスト"""
        color_picker = ColorPicker(mock_qt_modules)
        
        assert color_picker.qt_modules == mock_qt_modules
        assert color_picker.widget is None
        assert color_picker.color_changed_callback is None
    
    def test_color_picker_widget_creation(self, mock_qt_modules):
        """カラーピッカーウィジェット作成テスト"""
        color_picker = ColorPicker(mock_qt_modules)
        
        # ウィジェット作成をモック
        mock_widget = Mock()
        mock_qt_modules['QtWidgets'].QGroupBox.return_value = mock_widget
        
        widget = color_picker.create_widget()
        
        assert widget is not None
        assert color_picker.widget == widget
        # QGroupBoxは複数回呼ばれる（メインとRGB値グループ）ので、呼び出し回数のみ確認
        assert mock_qt_modules['QtWidgets'].QGroupBox.call_count >= 1
    
    def test_color_change_callback(self, mock_qt_modules):
        """色変更コールバックテスト"""
        color_picker = ColorPicker(mock_qt_modules)
        
        # コールバック関数をモック
        callback_mock = Mock()
        color_picker.set_color_changed_callback(callback_mock)
        
        assert color_picker.color_changed_callback == callback_mock
        
        # 色変更をシミュレート
        color_picker._notify_color_changed()
        callback_mock.assert_called_once_with("#ffffff", "background")


# FontSelectorとPropertyEditorクラスは現在実装されていないため、テストをスキップ
# TODO: 将来的にこれらのクラスが実装されたら、テストを追加する


class TestThemeEditor:
    """ThemeEditorクラスのテスト"""
    
    @pytest.fixture
    def mock_qt_adapter(self):
        """モックQtAdapterを作成"""
        mock_adapter = Mock(spec=QtAdapter)
        mock_modules = {
            'QtWidgets': Mock(),
            'QtCore': Mock(),
            'QtGui': Mock()
        }
        mock_adapter.get_qt_modules.return_value = mock_modules
        return mock_adapter
    
    @pytest.fixture
    def mock_theme_adapter(self):
        """モックThemeAdapterを作成"""
        return Mock(spec=ThemeAdapter)
    
    def test_theme_editor_initialization(self, mock_qt_adapter, mock_theme_adapter):
        """テーマエディターの初期化テスト"""
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        assert theme_editor.qt_adapter == mock_qt_adapter
        assert theme_editor.theme_adapter == mock_theme_adapter
        assert theme_editor.widget is None
        assert theme_editor.color_picker is None
        assert theme_editor.theme_changed_callback is None
    
    def test_theme_editor_widget_creation(self, mock_qt_adapter, mock_theme_adapter):
        """テーマエディターウィジェット作成テスト"""
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        # ウィジェット作成をモック
        mock_widget = Mock()
        mock_qt_modules = mock_qt_adapter.get_qt_modules.return_value
        mock_qt_modules['QtWidgets'].QWidget.return_value = mock_widget
        
        # Qt.ItemFlag.ItemIsEditableのモック
        mock_qt_modules['QtCore'].Qt.ItemFlag.ItemIsEditable = 2
        
        # QTreeWidgetItemのモック
        mock_tree_item = Mock()
        mock_tree_item.flags.return_value = 7
        mock_qt_modules['QtWidgets'].QTreeWidgetItem.return_value = mock_tree_item
        
        widget = theme_editor.create_widget()
        
        assert widget is not None
        assert theme_editor.widget == widget
        assert theme_editor.color_picker is not None
    
    def test_theme_data_get_set(self, mock_qt_adapter, mock_theme_adapter):
        """テーマデータの取得・設定テスト"""
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        # テストテーマデータ
        test_theme = {
            'name': 'テストテーマ',
            'version': '1.0.0',
            'colors': {
                'primary': '#0078d4',
                'background': '#ffffff'
            },
            'fonts': {
                'default': {
                    'family': 'Arial',
                    'size': 12,
                    'bold': False,
                    'italic': False
                }
            },
            'properties': {}
        }
        
        # テーマデータを設定
        theme_editor.load_theme(test_theme)
        
        # テーマデータを取得
        result = theme_editor.get_theme_data()
        
        assert result['name'] == test_theme['name']
        assert result['version'] == test_theme['version']
        assert result['colors'] == test_theme['colors']
        assert result['fonts'] == test_theme['fonts']
    
    def test_theme_reset(self, mock_qt_adapter, mock_theme_adapter):
        """テーマリセットテスト"""
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        # カスタムテーマを設定
        custom_theme = {
            'name': 'カスタムテーマ',
            'version': '2.0.0',
            'colors': {'primary': '#ff0000'}
        }
        theme_editor.load_theme(custom_theme)
        
        # テーマをリセット
        theme_editor.reset_theme()
        
        # デフォルト値に戻っていることを確認
        result = theme_editor.get_theme_data()
        assert result['name'] == '新しいテーマ'
        assert result['version'] == '1.0.0'
        assert 'background' in result['colors']
        assert 'text' in result['colors']
        assert 'primary' in result['colors']
        assert 'secondary' in result['colors']
    
    def test_theme_changed_callback(self, mock_qt_adapter, mock_theme_adapter):
        """テーマ変更コールバックテスト"""
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        # コールバック関数をモック
        callback_mock = Mock()
        theme_editor.set_theme_changed_callback(callback_mock)
        
        assert theme_editor.theme_changed_callback == callback_mock
        
        # テーマ変更をシミュレート
        theme_editor._notify_theme_changed()
        callback_mock.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])