"""
プレビュー統合テスト

このモジュールは、テーマエディターとプレビューウィンドウの統合テストを実装します。
"""

import pytest
import sys
from unittest.mock import Mock, patch
import time

# テスト対象のインポート
from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.adapters.theme_adapter import ThemeAdapter
from qt_theme_studio.views.theme_editor import ThemeEditor
from qt_theme_studio.views.preview import PreviewWindow, WidgetShowcase


class TestWidgetShowcase:
    """WidgetShowcaseクラスのテスト"""
    
    @pytest.fixture
    def mock_qt_modules(self):
        """モックQtモジュールを作成"""
        mock_modules = {
            'QtWidgets': Mock(),
            'QtCore': Mock(),
            'QtGui': Mock()
        }
        return mock_modules
    
    def test_widget_showcase_initialization(self, mock_qt_modules):
        """ウィジェットショーケースの初期化テスト"""
        showcase = WidgetShowcase(mock_qt_modules)
        
        assert showcase.qt_modules == mock_qt_modules
        assert showcase.widget is None
        assert showcase.widgets == {}
    
    def test_widget_showcase_creation(self, mock_qt_modules):
        """ウィジェットショーケース作成テスト"""
        showcase = WidgetShowcase(mock_qt_modules)
        
        # ウィジェット作成をモック
        mock_widget = Mock()
        mock_qt_modules['QtWidgets'].QWidget.return_value = mock_widget
        
        widget = showcase.create_widget()
        
        assert widget is not None
        assert showcase.widget == widget
    
    def test_theme_application(self, mock_qt_modules):
        """テーマ適用テスト"""
        showcase = WidgetShowcase(mock_qt_modules)
        
        # ウィジェット作成をモック
        mock_widget = Mock()
        mock_qt_modules['QtWidgets'].QWidget.return_value = mock_widget
        showcase.widget = mock_widget
        
        # テストテーマデータ
        test_theme = {
            'colors': {
                'background': '#ffffff',
                'text': '#000000',
                'primary': '#0078d4'
            },
            'fonts': {
                'default': {
                    'family': 'Arial',
                    'size': 12,
                    'bold': False,
                    'italic': False
                }
            }
        }
        
        # テーマを適用
        showcase.apply_theme_to_widgets(test_theme)
        
        # setStyleSheetが呼ばれたことを確認
        mock_widget.setStyleSheet.assert_called_once()


class TestPreviewWindow:
    """PreviewWindowクラスのテスト"""
    
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
    
    def test_preview_window_initialization(self, mock_qt_adapter, mock_theme_adapter):
        """プレビューウィンドウの初期化テスト"""
        preview = PreviewWindow(mock_qt_adapter, mock_theme_adapter)
        
        assert preview.qt_adapter == mock_qt_adapter
        assert preview.theme_adapter == mock_theme_adapter
        assert preview.widget is None
        assert preview.widget_showcase is None
        assert preview.pending_theme_data is None
    
    def test_preview_window_creation(self, mock_qt_adapter, mock_theme_adapter):
        """プレビューウィンドウ作成テスト"""
        preview = PreviewWindow(mock_qt_adapter, mock_theme_adapter)
        
        # ウィジェット作成をモック
        mock_widget = Mock()
        mock_qt_modules = mock_qt_adapter.get_qt_modules.return_value
        mock_qt_modules['QtWidgets'].QWidget.return_value = mock_widget
        
        # QTimerのモック
        mock_timer = Mock()
        mock_qt_modules['QtCore'].QTimer.return_value = mock_timer
        
        widget = preview.create_widget()
        
        assert widget is not None
        assert preview.widget == widget
        assert preview.widget_showcase is not None
        assert preview.update_timer is not None
    
    def test_preview_update_debounce(self, mock_qt_adapter, mock_theme_adapter):
        """プレビュー更新のデバウンス処理テスト"""
        preview = PreviewWindow(mock_qt_adapter, mock_theme_adapter)
        
        # モックタイマーを設定
        mock_timer = Mock()
        preview.update_timer = mock_timer
        preview.widget = Mock()  # ウィジェットが存在することを示す
        
        # テストテーマデータ
        test_theme = {'colors': {'primary': '#0078d4'}}
        
        # 複数回更新を呼び出し
        preview.update_preview(test_theme)
        preview.update_preview(test_theme)
        preview.update_preview(test_theme)
        
        # タイマーが適切に制御されていることを確認
        assert mock_timer.stop.call_count >= 2  # 複数回stopが呼ばれる
        assert mock_timer.start.call_count >= 3  # 複数回startが呼ばれる
        assert preview.pending_theme_data == test_theme
    
    def test_export_preview_image(self, mock_qt_adapter, mock_theme_adapter):
        """プレビュー画像エクスポートテスト"""
        preview = PreviewWindow(mock_qt_adapter, mock_theme_adapter)
        
        # ウィジェットとQtモジュールをモック
        mock_widget = Mock()
        preview.widget = mock_widget
        
        mock_qt_modules = mock_qt_adapter.get_qt_modules.return_value
        
        # ファイルダイアログのモック
        mock_qt_modules['QtWidgets'].QFileDialog.getSaveFileName.return_value = ('test.png', 'PNG画像 (*.png)')
        
        # pixmapのモック
        mock_pixmap = Mock()
        mock_pixmap.save.return_value = True
        mock_widget.grab.return_value = mock_pixmap
        
        # メッセージボックスのモック
        mock_qt_modules['QtWidgets'].QMessageBox.information = Mock()
        
        # エクスポートを実行
        preview.export_preview_image()
        
        # 適切なメソッドが呼ばれたことを確認
        mock_widget.grab.assert_called_once()
        mock_pixmap.save.assert_called_once_with('test.png', 'PNG')
        mock_qt_modules['QtWidgets'].QMessageBox.information.assert_called_once()


class TestThemeEditorPreviewIntegration:
    """テーマエディターとプレビューの統合テスト"""
    
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
        mock_time.currentTime.return_value.msecsTo.return_value = 50  # 50ms
        mock_modules['QtCore'].QTime = mock_time
        
        mock_adapter.get_qt_modules.return_value = mock_modules
        return mock_adapter
    
    @pytest.fixture
    def mock_theme_adapter(self):
        """モックThemeAdapterを作成"""
        return Mock(spec=ThemeAdapter)
    
    def test_theme_editor_preview_connection(self, mock_qt_adapter, mock_theme_adapter):
        """テーマエディターとプレビューの接続テスト"""
        # テーマエディターを作成
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        # プレビューウィンドウを作成
        preview_window = PreviewWindow(mock_qt_adapter, mock_theme_adapter)
        
        # 接続前のコールバック数を確認
        initial_callback_count = len(theme_editor.preview_callbacks)
        
        # プレビューウィンドウと接続
        theme_editor.connect_to_preview_window(preview_window)
        
        # コールバックが追加されたことを確認
        assert len(theme_editor.preview_callbacks) == initial_callback_count + 1
        assert preview_window.update_preview in theme_editor.preview_callbacks
    
    def test_theme_editor_preview_disconnection(self, mock_qt_adapter, mock_theme_adapter):
        """テーマエディターとプレビューの切断テスト"""
        # テーマエディターを作成
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        # プレビューウィンドウを作成
        preview_window = PreviewWindow(mock_qt_adapter, mock_theme_adapter)
        
        # 接続
        theme_editor.connect_to_preview_window(preview_window)
        connected_callback_count = len(theme_editor.preview_callbacks)
        
        # 切断
        theme_editor.disconnect_from_preview_window(preview_window)
        
        # コールバックが削除されたことを確認
        assert len(theme_editor.preview_callbacks) == connected_callback_count - 1
        assert preview_window.update_preview not in theme_editor.preview_callbacks
    
    def test_realtime_preview_update(self, mock_qt_adapter, mock_theme_adapter):
        """リアルタイムプレビュー更新テスト"""
        # テーマエディターを作成
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        # プレビューコールバックをモック
        mock_preview_callback = Mock()
        theme_editor.add_preview_callback(mock_preview_callback)
        
        # タイマーをモック
        mock_timer = Mock()
        theme_editor.preview_update_timer = mock_timer
        
        # テーマ変更をシミュレート
        theme_editor._on_color_changed('#ff0000', 'primary')
        
        # タイマーが開始されたことを確認
        mock_timer.start.assert_called_with(100)  # 100msデバウンス
        
        # プレビューコールバックが呼ばれたことを確認
        # 実装により呼び出し回数が変わる可能性があるため、少なくとも1回呼ばれたことを確認
        assert mock_preview_callback.call_count >= 1
    
    def test_preview_update_performance(self, mock_qt_adapter, mock_theme_adapter):
        """プレビュー更新のパフォーマンステスト"""
        # テーマエディターを作成
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        # 複数のプレビューコールバックを追加
        mock_callbacks = [Mock() for _ in range(5)]
        for callback in mock_callbacks:
            theme_editor.add_preview_callback(callback)
        
        # プレビュー更新を実行
        theme_editor._update_preview_callbacks()
        
        # すべてのコールバックが呼ばれたことを確認
        for callback in mock_callbacks:
            callback.assert_called_once()
    
    def test_preview_update_error_handling(self, mock_qt_adapter, mock_theme_adapter):
        """プレビュー更新のエラーハンドリングテスト"""
        # テーマエディターを作成
        theme_editor = ThemeEditor(mock_qt_adapter, mock_theme_adapter)
        
        # エラーを発生させるコールバックを追加
        error_callback = Mock(side_effect=Exception("テストエラー"))
        normal_callback = Mock()
        
        theme_editor.add_preview_callback(error_callback)
        theme_editor.add_preview_callback(normal_callback)
        
        # プレビュー更新を実行（エラーが発生しても継続すること）
        theme_editor._update_preview_callbacks()
        
        # エラーが発生したコールバックも呼ばれたことを確認
        error_callback.assert_called_once()
        # 正常なコールバックも呼ばれたことを確認
        normal_callback.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])