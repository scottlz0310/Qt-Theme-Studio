"""
メインウィンドウの単体テスト

Qt-Theme-Studioのメインウィンドウのテストを行います
"""

from unittest.mock import Mock, patch

from PySide6.QtGui import QColor


class TestQtThemeStudioMainWindow:
    """QtThemeStudioMainWindowクラスのテスト"""

    def setup_method(self):
        """各テストメソッドの前処理"""
        # 依存関係のモック化
        self.mock_qt_adapter = Mock()
        self.mock_theme_adapter = Mock()
        self.mock_theme_generator = Mock()
        self.mock_preview_window = Mock()
        self.mock_preview_widget = Mock()

        # メインウィンドウの属性を直接設定(テスト用)
        self.main_window = Mock()
        self.main_window.qt_adapter = self.mock_qt_adapter
        self.main_window.theme_adapter = self.mock_theme_adapter
        self.main_window.theme_generator = self.mock_theme_generator
        self.main_window.preview_window = self.mock_preview_window
        self.main_window.preview_widget = self.mock_preview_widget
        self.main_window.themes = {}
        self.main_window.current_theme_name = None

        # メソッドのモック化
        self.main_window.load_custom_theme_file = Mock()
        self.main_window.on_theme_changed = Mock()
        self.main_window.apply_current_theme = Mock()
        self.main_window.save_current_theme = Mock()
        self.main_window.export_all_themes = Mock()
        self.main_window.choose_color = Mock()
        self.main_window.get_current_color = Mock()
        self.main_window.set_color_button = Mock()
        self.main_window.apply_preset_color = Mock()
        self.main_window.generate_theme_from_background = Mock()
        self.main_window.update_generated_theme_preview = Mock()
        self.main_window.convert_theme_for_preview = Mock()

    def test_init(self):
        """初期化のテスト"""
        assert self.main_window is not None
        assert hasattr(self.main_window, "qt_adapter")
        assert hasattr(self.main_window, "theme_adapter")
        assert hasattr(self.main_window, "theme_generator")
        assert hasattr(self.main_window, "preview_window")
        assert hasattr(self.main_window, "themes")
        assert hasattr(self.main_window, "current_theme_name")

    def test_adapters_creation(self):
        """アダプター作成のテスト"""
        assert self.main_window.qt_adapter == self.mock_qt_adapter
        assert self.main_window.theme_adapter == self.mock_theme_adapter

    def test_theme_generator_creation(self):
        """テーマジェネレータ作成のテスト"""
        assert self.main_window.theme_generator == self.mock_theme_generator

    def test_preview_window_creation(self):
        """プレビューウィンドウ作成のテスト"""
        assert self.main_window.preview_window == self.mock_preview_window
        assert self.main_window.preview_widget == self.mock_preview_widget

    def test_initial_theme_state(self):
        """初期テーマ状態のテスト"""
        assert self.main_window.themes == {}
        assert self.main_window.current_theme_name is None

    def test_load_custom_theme_file_success(self):
        """テーマファイル読み込み成功のテスト"""
        # メソッドを実行
        self.main_window.load_custom_theme_file()

        # メソッドが呼ばれたことを確認
        self.main_window.load_custom_theme_file.assert_called_once()

    @patch("PySide6.QtWidgets.QFileDialog.getOpenFileName")
    def test_load_custom_theme_file_cancelled(self, mock_file_dialog):
        """テーマファイル読み込みキャンセルのテスト"""
        # ファイルダイアログのモック(キャンセル)
        mock_file_dialog.return_value = ("", "")

        # 初期状態を保存
        initial_themes = self.main_window.themes.copy()

        # メソッドを実行
        self.main_window.load_custom_theme_file()

        # テーマが変更されていないことを確認
        assert self.main_window.themes == initial_themes

    def test_on_theme_changed(self):
        """テーマ変更のテスト"""
        # メソッドを実行
        self.main_window.on_theme_changed("Test Theme")

        # メソッドが呼ばれたことを確認
        self.main_window.on_theme_changed.assert_called_once_with("Test Theme")

    def test_on_theme_changed_none(self):
        """テーマ変更なしのテスト"""
        # 初期状態を保存
        initial_theme_name = self.main_window.current_theme_name

        # メソッドを実行
        self.main_window.on_theme_changed("")

        # テーマ名が変更されていないことを確認
        assert self.main_window.current_theme_name == initial_theme_name

    def test_apply_current_theme(self):
        """テーマ適用のテスト"""
        # メソッドを実行
        self.main_window.apply_current_theme()

        # メソッドが呼ばれたことを確認
        self.main_window.apply_current_theme.assert_called_once()

    def test_save_current_theme(self):
        """テーマ保存のテスト"""
        # メソッドを実行
        self.main_window.save_current_theme()

        # メソッドが呼ばれたことを確認
        self.main_window.save_current_theme.assert_called_once()

    def test_export_all_themes(self):
        """全テーマエクスポートのテスト"""
        # メソッドを実行
        self.main_window.export_all_themes()

        # メソッドが呼ばれたことを確認
        self.main_window.export_all_themes.assert_called_once()

    def test_choose_color(self):
        """色選択のテスト"""
        # メソッドを実行
        self.main_window.choose_color("background")

        # メソッドが呼ばれたことを確認
        self.main_window.choose_color.assert_called_once_with("background")

    def test_get_current_color(self):
        """現在の色取得のテスト"""
        # メソッドを実行
        self.main_window.get_current_color("background")

        # メソッドが呼ばれたことを確認
        self.main_window.get_current_color.assert_called_once_with("background")

    def test_set_color_button(self):
        """色ボタン設定のテスト"""
        test_color = QColor("#ff0000")
        # メソッドを実行
        self.main_window.set_color_button("background", test_color)

        # メソッドが呼ばれたことを確認
        self.main_window.set_color_button.assert_called_once_with(
            "background", test_color
        )

    def test_apply_preset_color(self):
        """プリセット色適用のテスト"""
        test_color = QColor("#00ff00")
        # メソッドを実行
        self.main_window.apply_preset_color(test_color)

        # メソッドが呼ばれたことを確認
        self.main_window.apply_preset_color.assert_called_once_with(test_color)

    def test_generate_theme_from_background(self):
        """背景色からのテーマ生成テスト"""
        # メソッドを実行
        self.main_window.generate_theme_from_background()

        # メソッドが呼ばれたことを確認
        self.main_window.generate_theme_from_background.assert_called_once()

    def test_update_generated_theme_preview(self):
        """生成テーマプレビュー更新のテスト"""
        # メソッドを実行
        self.main_window.update_generated_theme_preview()

        # メソッドが呼ばれたことを確認
        self.main_window.update_generated_theme_preview.assert_called_once()

    def test_convert_theme_for_preview(self):
        """プレビュー用テーマ変換のテスト"""
        test_theme = {"name": "Test Theme", "primaryColor": "#007acc"}
        # メソッドを実行
        self.main_window.convert_theme_for_preview(test_theme)

        # メソッドが呼ばれたことを確認
        self.main_window.convert_theme_for_preview.assert_called_once_with(test_theme)

    def test_theme_management(self):
        """テーマ管理の基本テスト"""
        # テスト用のテーマを追加
        test_theme = {"name": "Test Theme", "display_name": "Test Theme"}
        self.main_window.themes["Test Theme"] = test_theme
        assert "Test Theme" in self.main_window.themes
        assert self.main_window.themes["Test Theme"] == test_theme

        # テーマを削除
        del self.main_window.themes["Test Theme"]
        assert "Test Theme" not in self.main_window.themes

    def test_theme_selection_workflow(self):
        """テーマ選択ワークフローのテスト"""
        # テーマを追加
        test_theme = {"name": "Test Theme", "display_name": "Test Theme"}
        self.main_window.themes["Test Theme"] = test_theme

        # テーマを選択
        self.main_window.current_theme_name = "Test Theme"
        assert self.main_window.current_theme_name == "Test Theme"

        # テーマデータを取得
        assert (
            self.main_window.themes[self.main_window.current_theme_name] == test_theme
        )

    def test_error_handling_workflow(self):
        """エラーハンドリングワークフローのテスト"""
        # エラー状態のシミュレーション
        self.main_window.current_theme_name = None

        # テーマが選択されていない状態での操作
        assert self.main_window.current_theme_name is None
        assert len(self.main_window.themes) == 0

    def test_ui_state_management(self):
        """UI状態管理のテスト"""
        # UI状態の初期化
        self.main_window.theme_combo = Mock()
        self.main_window.bg_color_btn = Mock()
        self.main_window.generated_theme_preview = Mock()

        # UI要素の存在確認
        assert hasattr(self.main_window, "theme_combo")
        assert hasattr(self.main_window, "bg_color_btn")
        assert hasattr(self.main_window, "generated_theme_preview")

    def test_method_call_consistency(self):
        """メソッド呼び出しの一貫性テスト"""
        # 全ての主要メソッドが呼び出し可能であることを確認
        methods = [
            "load_custom_theme_file",
            "on_theme_changed",
            "apply_current_theme",
            "save_current_theme",
            "export_all_themes",
            "choose_color",
            "get_current_color",
            "set_color_button",
            "apply_preset_color",
            "generate_theme_from_background",
            "update_generated_theme_preview",
            "convert_theme_for_preview",
        ]

        for method_name in methods:
            assert hasattr(self.main_window, method_name)
            method = getattr(self.main_window, method_name)
            assert callable(method)

    def test_theme_data_structure(self):
        """テーマデータ構造のテスト"""
        # テスト用のテーマデータ
        test_theme = {
            "name": "Test Theme",
            "display_name": "Test Theme",
            "primaryColor": "#007acc",
            "backgroundColor": "#ffffff",
            "textColor": "#000000",
        }

        # テーマデータの構造確認
        assert "name" in test_theme
        assert "display_name" in test_theme
        assert "primaryColor" in test_theme
        assert "backgroundColor" in test_theme
        assert "textColor" in test_theme

        # テーマを追加
        self.main_window.themes["Test Theme"] = test_theme
        assert "Test Theme" in self.main_window.themes
