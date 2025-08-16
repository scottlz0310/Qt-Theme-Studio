"""
プレビュー関連のモジュール

このモジュールは、Qt-Theme-Studioアプリケーションのプレビュー機能を提供します。
"""

from typing import Any, Callable, Dict, List, Optional

from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.adapters.theme_adapter import ThemeAdapter
from qt_theme_studio.logger import LogCategory, get_logger


class WidgetShowcase:
    """ウィジェットショーケースコンポーネント

    包括的なQtウィジェットセット（QPushButton、QLineEdit、QComboBox等）のプレビュー表示を提供します。
    """

    def __init__(self, qt_modules: Dict[str, Any], parent=None):
        """ウィジェットショーケースを初期化します

        Args:
            qt_modules: Qtモジュール辞書
            parent: 親ウィジェット
        """
        self.qt_modules = qt_modules
        self.QtWidgets = qt_modules["QtWidgets"]
        self.QtCore = qt_modules["QtCore"]
        self.QtGui = qt_modules["QtGui"]
        self.parent = parent
        self.logger = get_logger()

        # UI要素
        self.widget: Optional[Any] = None
        self.widgets: Dict[str, Any] = {}

    def create_widget(self) -> Any:
        """ウィジェットショーケースを作成します

        Returns:
            QWidget: ウィジェットショーケース
        """
        self.widget = self.QtWidgets.QWidget()
        layout = self.QtWidgets.QVBoxLayout(self.widget)

        # スクロールエリアを作成
        scroll_area = self.QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            self.QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        scroll_area.setVerticalScrollBarPolicy(
            self.QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # スクロール可能なコンテンツウィジェット
        content_widget = self.QtWidgets.QWidget()
        content_layout = self.QtWidgets.QVBoxLayout(content_widget)

        # 各ウィジェットカテゴリを作成
        self._create_button_widgets(content_layout)
        self._create_input_widgets(content_layout)
        self._create_selection_widgets(content_layout)
        self._create_display_widgets(content_layout)
        self._create_container_widgets(content_layout)
        self._create_progress_widgets(content_layout)

        # ストレッチを追加
        content_layout.addStretch()

        # スクロールエリアにコンテンツを設定
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        self.logger.debug("ウィジェットショーケースを作成しました", LogCategory.UI)
        return self.widget

    def _create_button_widgets(self, layout: Any) -> None:
        """ボタンウィジェットを作成します"""
        group = self.QtWidgets.QGroupBox("ボタン")
        group_layout = self.QtWidgets.QHBoxLayout(group)

        # QPushButton
        push_button = self.QtWidgets.QPushButton("プッシュボタン")
        push_button.setToolTip("これはプッシュボタンです")
        group_layout.addWidget(push_button)
        self.widgets["push_button"] = push_button

        # QPushButton (無効)
        disabled_button = self.QtWidgets.QPushButton("無効ボタン")
        disabled_button.setEnabled(False)
        group_layout.addWidget(disabled_button)
        self.widgets["disabled_button"] = disabled_button

        # QPushButton (デフォルト)
        default_button = self.QtWidgets.QPushButton("デフォルトボタン")
        default_button.setDefault(True)
        group_layout.addWidget(default_button)
        self.widgets["default_button"] = default_button

        # QToolButton
        tool_button = self.QtWidgets.QToolButton()
        tool_button.setText("ツール")
        tool_button.setToolButtonStyle(
            self.QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon
        )
        group_layout.addWidget(tool_button)
        self.widgets["tool_button"] = tool_button

        group_layout.addStretch()
        layout.addWidget(group)

    def _create_input_widgets(self, layout: Any) -> None:
        """入力ウィジェットを作成します"""
        group = self.QtWidgets.QGroupBox("入力")
        group_layout = self.QtWidgets.QGridLayout(group)

        # QLineEdit
        line_edit_label = self.QtWidgets.QLabel("テキスト入力:")
        line_edit = self.QtWidgets.QLineEdit()
        line_edit.setPlaceholderText("テキストを入力してください")
        line_edit.setText("サンプルテキスト")
        group_layout.addWidget(line_edit_label, 0, 0)
        group_layout.addWidget(line_edit, 0, 1)
        self.widgets["line_edit"] = line_edit

        # QTextEdit
        text_edit_label = self.QtWidgets.QLabel("複数行テキスト:")
        text_edit = self.QtWidgets.QTextEdit()
        text_edit.setPlainText("複数行の\\nサンプルテキスト\\nです。")
        text_edit.setMaximumHeight(80)
        group_layout.addWidget(text_edit_label, 1, 0)
        group_layout.addWidget(text_edit, 1, 1)
        self.widgets["text_edit"] = text_edit

        # QSpinBox
        spinbox_label = self.QtWidgets.QLabel("数値入力:")
        spinbox = self.QtWidgets.QSpinBox()
        spinbox.setRange(0, 100)
        spinbox.setValue(50)
        group_layout.addWidget(spinbox_label, 2, 0)
        group_layout.addWidget(spinbox, 2, 1)
        self.widgets["spinbox"] = spinbox

        layout.addWidget(group)

    def _create_selection_widgets(self, layout: Any) -> None:
        """選択ウィジェットを作成します"""
        group = self.QtWidgets.QGroupBox("選択")
        group_layout = self.QtWidgets.QGridLayout(group)

        # QComboBox
        combo_label = self.QtWidgets.QLabel("コンボボックス:")
        combo = self.QtWidgets.QComboBox()
        combo.addItems(["オプション1", "オプション2", "オプション3"])
        combo.setCurrentIndex(1)
        group_layout.addWidget(combo_label, 0, 0)
        group_layout.addWidget(combo, 0, 1)
        self.widgets["combo"] = combo

        # QCheckBox
        checkbox1 = self.QtWidgets.QCheckBox("チェックボックス1")
        checkbox1.setChecked(True)
        checkbox2 = self.QtWidgets.QCheckBox("チェックボックス2")
        checkbox3 = self.QtWidgets.QCheckBox("無効チェックボックス")
        checkbox3.setEnabled(False)

        group_layout.addWidget(checkbox1, 1, 0)
        group_layout.addWidget(checkbox2, 1, 1)
        group_layout.addWidget(checkbox3, 1, 2)
        self.widgets["checkbox1"] = checkbox1
        self.widgets["checkbox2"] = checkbox2
        self.widgets["checkbox3"] = checkbox3

        # QRadioButton
        radio1 = self.QtWidgets.QRadioButton("ラジオボタン1")
        radio1.setChecked(True)
        radio2 = self.QtWidgets.QRadioButton("ラジオボタン2")
        radio3 = self.QtWidgets.QRadioButton("ラジオボタン3")

        group_layout.addWidget(radio1, 2, 0)
        group_layout.addWidget(radio2, 2, 1)
        group_layout.addWidget(radio3, 2, 2)
        self.widgets["radio1"] = radio1
        self.widgets["radio2"] = radio2
        self.widgets["radio3"] = radio3

        layout.addWidget(group)

    def _create_display_widgets(self, layout: Any) -> None:
        """表示ウィジェットを作成します"""
        group = self.QtWidgets.QGroupBox("表示")
        group_layout = self.QtWidgets.QVBoxLayout(group)

        # QLabel
        label = self.QtWidgets.QLabel("これはラベルです。長いテキストの表示例。")
        label.setWordWrap(True)
        group_layout.addWidget(label)
        self.widgets["label"] = label

        # QListWidget
        list_widget = self.QtWidgets.QListWidget()
        list_widget.addItems(["アイテム1", "アイテム2", "アイテム3", "アイテム4"])
        list_widget.setCurrentRow(1)
        list_widget.setMaximumHeight(100)
        group_layout.addWidget(list_widget)
        self.widgets["list_widget"] = list_widget

        # QTreeWidget
        tree_widget = self.QtWidgets.QTreeWidget()
        tree_widget.setHeaderLabels(["名前", "値"])

        root_item = self.QtWidgets.QTreeWidgetItem(["ルート", ""])
        child1 = self.QtWidgets.QTreeWidgetItem(["子1", "値1"])
        child2 = self.QtWidgets.QTreeWidgetItem(["子2", "値2"])
        root_item.addChild(child1)
        root_item.addChild(child2)
        tree_widget.addTopLevelItem(root_item)
        tree_widget.expandAll()
        tree_widget.setMaximumHeight(100)

        group_layout.addWidget(tree_widget)
        self.widgets["tree_widget"] = tree_widget

        layout.addWidget(group)

    def _create_container_widgets(self, layout: Any) -> None:
        """コンテナウィジェットを作成します"""
        group = self.QtWidgets.QGroupBox("コンテナ")
        group_layout = self.QtWidgets.QHBoxLayout(group)

        # QTabWidget
        tab_widget = self.QtWidgets.QTabWidget()

        tab1 = self.QtWidgets.QWidget()
        tab1_layout = self.QtWidgets.QVBoxLayout(tab1)
        tab1_layout.addWidget(self.QtWidgets.QLabel("タブ1の内容"))
        tab1_layout.addWidget(self.QtWidgets.QPushButton("タブ1ボタン"))
        tab_widget.addTab(tab1, "タブ1")

        tab2 = self.QtWidgets.QWidget()
        tab2_layout = self.QtWidgets.QVBoxLayout(tab2)
        tab2_layout.addWidget(self.QtWidgets.QLabel("タブ2の内容"))
        tab2_layout.addWidget(self.QtWidgets.QCheckBox("タブ2チェック"))
        tab_widget.addTab(tab2, "タブ2")

        tab_widget.setMaximumHeight(150)
        group_layout.addWidget(tab_widget)
        self.widgets["tab_widget"] = tab_widget

        # QGroupBox (ネスト)
        nested_group = self.QtWidgets.QGroupBox("ネストグループ")
        nested_layout = self.QtWidgets.QVBoxLayout(nested_group)
        nested_layout.addWidget(self.QtWidgets.QLabel("ネストされた内容"))
        nested_layout.addWidget(
            self.QtWidgets.QSlider(self.QtCore.Qt.Orientation.Horizontal)
        )

        group_layout.addWidget(nested_group)
        self.widgets["nested_group"] = nested_group

        layout.addWidget(group)

    def _create_progress_widgets(self, layout: Any) -> None:
        """プログレスウィジェットを作成します"""
        group = self.QtWidgets.QGroupBox("プログレス")
        group_layout = self.QtWidgets.QVBoxLayout(group)

        # QProgressBar
        progress_bar = self.QtWidgets.QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(65)
        group_layout.addWidget(progress_bar)
        self.widgets["progress_bar"] = progress_bar

        # QSlider
        slider_layout = self.QtWidgets.QHBoxLayout()
        slider_label = self.QtWidgets.QLabel("スライダー:")
        slider = self.QtWidgets.QSlider(self.QtCore.Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(30)
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(slider)
        group_layout.addLayout(slider_layout)
        self.widgets["slider"] = slider

        layout.addWidget(group)

    def get_all_widgets(self) -> Dict[str, Any]:
        """すべてのウィジェットを取得します

        Returns:
            Dict[str, Any]: ウィジェット辞書
        """
        return self.widgets.copy()

    def apply_theme_to_widgets(self, theme_data: Dict[str, Any]) -> None:
        """ウィジェットにテーマを適用します

        Args:
            theme_data: テーマデータ
        """
        if not self.widget or not theme_data:
            return

        # 基本的なスタイルシートを生成
        stylesheet = self._generate_stylesheet_from_theme(theme_data)
        
        # デバッグ情報を出力
        print("生成されたスタイルシート:")
        print(stylesheet)
        print(f"ウィジェット: {self.widget}")
        print(f"ウィジェットのクラス: {type(self.widget)}")

        # ウィジェット全体にスタイルシートを適用
        self.widget.setStyleSheet(stylesheet)
        
        # スタイルシートが効かない場合の代替手段: パレットを直接操作
        self._apply_theme_via_palette(theme_data)

        # デバッグ: 実際のウィジェットの色を確認
        self._debug_widget_colors()
        
        self.logger.debug("ウィジェットにテーマを適用しました", LogCategory.UI)
    
    def _apply_theme_via_palette(self, theme_data: Dict[str, Any]) -> None:
        """パレットを直接操作してテーマを適用（スタイルシートの代替手段）"""
        if not self.widget or not theme_data:
            return
        
        try:
            colors = theme_data.get("colors", {})
            if not colors:
                return
            
            # 新しいパレットを作成
            palette = self.widget.palette()
            
            # 背景色を設定
            if "background" in colors:
                bg_color = self.QtGui.QColor(colors["background"])
                palette.setColor(palette.ColorRole.Window, bg_color)
                palette.setColor(palette.ColorRole.Base, bg_color)
                palette.setColor(palette.ColorRole.Button, bg_color)
                palette.setColor(palette.ColorRole.Light, bg_color)
                palette.setColor(palette.ColorRole.Mid, bg_color)
                palette.setColor(palette.ColorRole.Dark, bg_color)
            
            # テキスト色を設定
            if "text" in colors:
                text_color = self.QtGui.QColor(colors["text"])
                palette.setColor(palette.ColorRole.WindowText, text_color)
                palette.setColor(palette.ColorRole.Text, text_color)
                palette.setColor(palette.ColorRole.ButtonText, text_color)
            
            # プライマリ色を設定
            if "primary" in colors:
                primary_color = self.QtGui.QColor(colors["primary"])
                palette.setColor(palette.ColorRole.Highlight, primary_color)
                palette.setColor(palette.ColorRole.Link, primary_color)
            
            # パレットをウィジェットに適用
            self.widget.setPalette(palette)
            
            # 子ウィジェットにもパレットを適用
            for child in self.widget.findChildren(self.QtWidgets.QWidget):
                try:
                    child.setPalette(palette)
                except:
                    pass
            
            # 強制的に再描画を実行
            self.widget.update()
            self.widget.repaint()
            
            # 子ウィジェットも再描画
            for child in self.widget.findChildren(self.QtWidgets.QWidget):
                try:
                    child.update()
                    child.repaint()
                except:
                    pass
            
            print("パレットを直接操作してテーマを適用し、強制再描画を実行しました")
            
        except Exception as e:
            print(f"パレット操作でエラー: {e}")
    
    def _debug_widget_colors(self):
        """ウィジェットの実際の色をデバッグ出力"""
        if not self.widget:
            return
        
        try:
            # ウィジェットのパレットを取得
            palette = self.widget.palette()
            
            print("\n=== ウィジェットの実際の色 ===")
            print(f"ウィジェット: {self.widget}")
            print(f"ウィジェットのクラス: {type(self.widget)}")
            
            # 背景色
            bg_color = palette.color(palette.ColorRole.Window)
            print(f"背景色 (Window): {bg_color.name()}")
            
            # テキスト色
            text_color = palette.color(palette.ColorRole.WindowText)
            print(f"テキスト色 (WindowText): {text_color.name()}")
            
            # ベース色
            base_color = palette.color(palette.ColorRole.Base)
            print(f"ベース色 (Base): {base_color.name()}")
            
            # ベーステキスト色
            base_text_color = palette.color(palette.ColorRole.Text)
            print(f"ベーステキスト色 (Text): {base_text_color.name()}")
            
            # ボタン色
            button_color = palette.color(palette.ColorRole.Button)
            print(f"ボタン色 (Button): {button_color.name()}")
            
            # ボタンテキスト色
            button_text_color = palette.color(palette.ColorRole.ButtonText)
            print(f"ボタンテキスト色 (ButtonText): {button_text_color.name()}")
            
            # スタイルシートの状態
            stylesheet = self.widget.styleSheet()
            print(f"現在のスタイルシート: {stylesheet[:200]}...")
            
            # スタイルシートの有効性をチェック
            print("\n--- スタイルシートの有効性チェック ---")
            print(f"スタイルシートが空: {not bool(stylesheet)}")
            print(f"スタイルシートの長さ: {len(stylesheet)}")
            
            # ウィジェットのスタイル状態
            print(f"ウィジェットのスタイル: {self.widget.style()}")
            print(f"ウィジェットのスタイルオブジェクト: {self.widget.style().objectName()}")
            
            # スタイルシートが無効化されていないか
            print(f"スタイルシートが無効: {self.widget.property('styleSheetDisabled')}")
            
            # ウィジェットのプロパティ
            print(f"ウィジェットのプロパティ: {self.widget.dynamicPropertyNames()}")
            
            # Qtのスタイルエンジンの状態
            print("\n--- Qtスタイルエンジンの状態 ---")
            print(f"QApplicationのスタイル: {self.QtWidgets.QApplication.instance().style().objectName()}")
            print(f"ウィジェットのスタイルシートプロパティ: "
                  f"{self.widget.property('styleSheet')}")
            print(f"ウィジェットのスタイルシートが空: {not bool(self.widget.styleSheet())}")
            
            # 強制的にスタイルシートを再適用
            print("\n--- スタイルシートの強制再適用 ---")
            self.widget.setStyleSheet("")  # 一旦クリア
            self.widget.setStyleSheet(stylesheet)  # 再適用
            print("スタイルシートを強制再適用しました")
            
            # 再適用後の状態を確認
            print(f"再適用後のスタイルシート: {self.widget.styleSheet()[:100]}...")
            
            # 子ウィジェットの色も確認
            print("\n--- 子ウィジェットの色 ---")
            for child in self.widget.findChildren(self.QtWidgets.QWidget):
                try:
                    child_palette = child.palette()
                    child_bg = child_palette.color(child_palette.ColorRole.Window)
                    child_text = child_palette.color(child_palette.ColorRole.WindowText)
                    
                    # 子ウィジェットのスタイルシートもチェック
                    child_stylesheet = child.styleSheet()
                    has_custom_style = bool(child_stylesheet)
                    
                    # ウィジェットの詳細情報
                    child_visible = child.isVisible()
                    child_enabled = child.isEnabled()
                    child_geometry = child.geometry()
                    
                    print(f"子ウィジェット {type(child).__name__}: "
                          f"背景={child_bg.name()}, テキスト={child_text.name()}, "
                          f"カスタムスタイル={has_custom_style}, "
                          f"表示={child_visible}, 有効={child_enabled}, "
                          f"位置=({child_geometry.x()},{child_geometry.y()}) "
                          f"サイズ=({child_geometry.width()}x{child_geometry.height()})")
                    
                    # カスタムスタイルがある場合は詳細を表示
                    if has_custom_style:
                        print(f"  → カスタムスタイルシート: {child_stylesheet[:100]}...")
                        
                except Exception as e:
                    print(f"子ウィジェット {type(child).__name__}: エラー - {e}")
            
            print("=" * 40)
            
        except Exception as e:
            print(f"色のデバッグ中にエラー: {e}")

    def _generate_stylesheet_from_theme(self, theme_data: Dict[str, Any]) -> str:
        """テーマデータからスタイルシートを生成します（qt-theme-manager使用）

        Args:
            theme_data: テーマデータ

        Returns:
            str: 生成されたスタイルシート
        """
        try:
            # qt-theme-managerのStylesheetGeneratorを使用
            import qt_theme_manager
            
            # テーマ設定をqt-theme-manager形式に変換
            theme_config = self._convert_to_qt_theme_manager_format(theme_data)
            
            # 基本モードでスタイルシート生成（プレビュー用）
            generator = qt_theme_manager.StylesheetGenerator(theme_config, advanced_mode=False)
            stylesheet = generator.generate_qss()
            
            self.logger.debug("qt-theme-managerでスタイルシートを生成しました", LogCategory.UI)
            return stylesheet
            
        except Exception as e:
            self.logger.error(
                f"qt-theme-managerでのスタイルシート生成に失敗: {e}", 
                LogCategory.UI
            )
            # エラーの場合は空のスタイルシートを返す
            return ""
    
    def _convert_to_qt_theme_manager_format(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Qt-Theme-Studio形式をqt-theme-manager形式に変換"""
        try:
            colors = theme_data.get("colors", {})
            
            # qt-theme-managerの標準形式に変換
            theme_config = {
                "name": theme_data.get("name", "Unknown"),
                "display_name": theme_data.get("display_name", theme_data.get("name", "Unknown")),
                "description": theme_data.get("description", ""),
                "primaryColor": colors.get("primary", "#007acc"),
                "accentColor": colors.get("accent", colors.get("primary", "#007acc")),
                "backgroundColor": colors.get("background", "#ffffff"),
                "textColor": colors.get("text", "#333333"),
                "button": {
                    "background": colors.get("button_background", colors.get("primary", "#007acc")),
                    "text": colors.get("button_text", colors.get("text", "#ffffff")),
                    "hover": colors.get("button_hover", colors.get("accent", "#007acc")),
                    "pressed": colors.get("button_pressed", colors.get("secondary", "#6c757d")),
                    "border": colors.get("button_border", colors.get("border", "#dee2e6"))
                },
                "panel": {
                    "background": colors.get("panel_background", colors.get("background", "#ffffff")),
                    "border": colors.get("panel_border", colors.get("border", "#dee2e6")),
                    "header": {
                        "background": colors.get("header_background", colors.get("surface", "#f8f9fa")),
                        "text": colors.get("header_text", colors.get("text", "#333333")),
                        "border": colors.get("header_border", colors.get("border", "#dee2e6"))
                    },
                    "zebra": {
                        "alternate": colors.get("zebra_alternate", colors.get("surface", "#f8f9fa"))
                    }
                },
                "text": {
                    "primary": colors.get("text_primary", colors.get("text", "#333333")),
                    "secondary": colors.get("text_secondary", colors.get("text_muted", "#6c757d")),
                    "muted": colors.get("text_muted", "#6c757d"),
                    "heading": colors.get("text_heading", colors.get("text", "#333333")),
                    "link": colors.get("text_link", colors.get("primary", "#007acc")),
                    "success": colors.get("text_success", colors.get("success", "#28a745")),
                    "warning": colors.get("text_warning", colors.get("warning", "#ffc107")),
                    "error": colors.get("text_error", colors.get("error", "#dc3545"))
                },
                "input": {
                    "background": colors.get("input_background", colors.get("background", "#ffffff")),
                    "text": colors.get("input_text", colors.get("text", "#333333")),
                    "border": colors.get("input_border", colors.get("border", "#dee2e6")),
                    "focus": colors.get("input_focus", colors.get("primary", "#007acc")),
                    "placeholder": colors.get("input_placeholder", colors.get("text_muted", "#6c757d"))
                },
                "toolbar": {
                    "background": colors.get("toolbar_background", colors.get("surface", "#f8f9fa")),
                    "text": colors.get("toolbar_text", colors.get("text", "#333333")),
                    "border": colors.get("toolbar_border", colors.get("border", "#dee2e6")),
                    "button": {
                        "background": colors.get("toolbar_button_background", colors.get("background", "#ffffff")),
                        "text": colors.get("toolbar_button_text", colors.get("text", "#333333")),
                        "hover": colors.get("toolbar_button_hover", colors.get("primary", "#007acc")),
                        "pressed": colors.get("toolbar_button_pressed", colors.get("surface", "#e9ecef"))
                    }
                },
                "status": {
                    "background": colors.get("status_background", colors.get("surface", "#f8f9fa")),
                    "text": colors.get("status_text", colors.get("text_secondary", "#6c757d")),
                    "border": colors.get("status_border", colors.get("border", "#dee2e6"))
                }
            }
            
            return theme_config
            
        except Exception as e:
            self.logger.error(f"テーマ形式変換に失敗: {e}", LogCategory.UI)
            # フォールバック: 基本的な色設定のみ
            return {
                "name": "Fallback Theme",
                "display_name": "フォールバックテーマ",
                "description": "エラー時のフォールバックテーマ",
                "primaryColor": "#007acc",
                "backgroundColor": "#ffffff",
                "textColor": "#333333"
            }


class PreviewWindow:
    """ライブプレビューウィンドウクラス

    包括的なQtウィジェットセットのプレビュー表示と、500ms以内のリアルタイム更新機能を提供します。
    """

    def __init__(self, qt_adapter: QtAdapter, theme_adapter: ThemeAdapter):
        """プレビューウィンドウを初期化します

        Args:
            qt_adapter: Qt フレームワークアダプター
            theme_adapter: テーマアダプター
        """
        self.qt_adapter = qt_adapter
        self.theme_adapter = theme_adapter
        self.logger = get_logger()

        # Qtモジュールを取得
        self.qt_modules = qt_adapter.get_qt_modules()
        self.QtWidgets = self.qt_modules["QtWidgets"]
        self.QtCore = self.qt_modules["QtCore"]
        self.QtGui = self.qt_modules["QtGui"]

        # UI要素
        self.widget: Optional[Any] = None
        self.widget_showcase: Optional[WidgetShowcase] = None

        # 更新管理
        self.update_timer: Optional[Any] = None
        self.pending_theme_data: Optional[Dict[str, Any]] = None

        # コールバック
        self.theme_applied_callback: Optional[Callable[[Dict[str, Any]], None]] = None

        self.logger.info("プレビューウィンドウを初期化しました", LogCategory.UI)

    def create_widget(self) -> Any:
        """プレビューウィンドウウィジェットを作成します

        Returns:
            QWidget: プレビューウィンドウウィジェット
        """
        self.widget = self.QtWidgets.QWidget()
        layout = self.QtWidgets.QVBoxLayout(self.widget)

        # ヘッダー
        header_layout = self.QtWidgets.QHBoxLayout()
        title_label = self.QtWidgets.QLabel("ライブプレビュー")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 5px;")

        # プレビュー画像エクスポートボタン
        export_button = self.QtWidgets.QPushButton("画像エクスポート")
        export_button.setToolTip("プレビューをPNG形式で保存します")
        export_button.clicked.connect(self.export_preview_image)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(export_button)
        layout.addLayout(header_layout)

        # ウィジェットショーケースを作成
        self.widget_showcase = WidgetShowcase(self.qt_modules, self.widget)
        showcase_widget = self.widget_showcase.create_widget()
        layout.addWidget(showcase_widget)

        # 更新タイマーを初期化
        self._setup_update_timer()

        self.logger.info(
            "プレビューウィンドウウィジェットを作成しました", LogCategory.UI
        )
        return self.widget

    def _setup_update_timer(self) -> None:
        """更新タイマーを設定します"""
        self.update_timer = self.QtCore.QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._apply_pending_theme)

        self.logger.debug("更新タイマーを設定しました", LogCategory.UI)

    def update_preview(self, theme_data: Dict[str, Any]) -> None:
        """プレビューを更新します（500ms以内の更新保証とデバウンス処理）

        Args:
            theme_data: 適用するテーマデータ
        """
        if not self.widget or not theme_data:
            return

        # 保留中のテーマデータを更新
        self.pending_theme_data = theme_data.copy()

        # タイマーを再開（デバウンス処理）
        if self.update_timer:
            self.update_timer.stop()
            self.update_timer.start(100)  # 100msのデバウンス

        self.logger.debug("プレビュー更新をスケジュールしました", LogCategory.UI)

    def _apply_pending_theme(self) -> None:
        """保留中のテーマを適用します"""
        if not self.pending_theme_data or not self.widget_showcase:
            return

        start_time = self.QtCore.QTime.currentTime()

        try:
            # ウィジェットショーケースにテーマを適用
            self.widget_showcase.apply_theme_to_widgets(self.pending_theme_data)

            # 適用完了のコールバックを呼び出し
            if self.theme_applied_callback:
                self.theme_applied_callback(self.pending_theme_data)

            # 処理時間を計算
            end_time = self.QtCore.QTime.currentTime()
            elapsed_ms = start_time.msecsTo(end_time)

            self.logger.debug(
                "プレビューを更新しました（処理時間: {elapsed_ms}ms）", LogCategory.UI
            )

            # 500ms以内の更新保証をチェック
            if elapsed_ms > 500:
                self.logger.warning(
                    "プレビュー更新が500msを超えました: {elapsed_ms}ms", LogCategory.UI
                )

        except Exception:
            self.logger.error(
                "プレビュー更新中にエラーが発生しました: {str()}", LogCategory.UI
            )
        finally:
            self.pending_theme_data = None

    def export_preview_image(self) -> None:
        """プレビュー画像をPNG形式でエクスポートします"""
        if not self.widget:
            return

        try:
            # ファイル保存ダイアログを表示
            file_path, _ = self.QtWidgets.QFileDialog.getSaveFileName(
                self.widget,
                "プレビュー画像を保存",
                "preview.png",
                "PNG画像 (*.png);;すべてのファイル (*)",
            )

            if file_path:
                # ウィジェットのスクリーンショットを取得
                pixmap = self.widget.grab()

                # PNG形式で保存
                if pixmap.save(file_path, "PNG"):
                    self.logger.info(
                        "プレビュー画像を保存しました: {file_path}", LogCategory.UI
                    )

                    # 成功メッセージを表示
                    self.QtWidgets.QMessageBox.information(
                        self.widget,
                        "エクスポート完了",
                        "プレビュー画像を保存しました:\\n{file_path}",
                    )
                else:
                    raise Exception("画像の保存に失敗しました")

        except Exception:
            self.logger.error(
                "プレビュー画像のエクスポートに失敗しました: {str()}", LogCategory.UI
            )

            # エラーメッセージを表示
            self.QtWidgets.QMessageBox.critical(
                self.widget,
                "エクスポートエラー",
                "プレビュー画像のエクスポートに失敗しました:\\n{str()}",
            )

    def get_widget_showcase(self) -> Optional[WidgetShowcase]:
        """ウィジェットショーケースを取得します

        Returns:
            Optional[WidgetShowcase]: ウィジェットショーケース
        """
        return self.widget_showcase

    def set_theme_applied_callback(
        self, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """テーマ適用コールバックを設定します

        Args:
            callback: テーマ適用時に呼び出されるコールバック関数
        """
        self.theme_applied_callback = callback

    def get_widget(self) -> Optional[Any]:
        """プレビューウィンドウウィジェットを取得します

        Returns:
            Optional[QWidget]: プレビューウィンドウウィジェット
        """
        return self.widget

    def test_responsive_layout(self, sizes: List[tuple] = None) -> Dict[str, Any]:
        """レスポンシブレイアウトテストを実行します

        Args:
            sizes: テストするウィンドウサイズのリスト [(width, height), ...]

        Returns:
            Dict[str, Any]: テスト結果
        """
        if not self.widget:
            return {"error": "プレビューウィンドウが作成されていません"}

        if sizes is None:
            sizes = [(800, 600), (1024, 768), (1280, 1024), (1920, 1080)]

        results = {"tested_sizes": [], "layout_issues": [], "performance_data": []}

        original_size = self.widget.size()

        try:
            for width, height in sizes:
                start_time = self.QtCore.QTime.currentTime()

                # ウィンドウサイズを変更
                self.widget.resize(width, height)

                # レイアウトの更新を強制
                self.widget.updateGeometry()
                self.widget.repaint()

                # 処理時間を計算
                end_time = self.QtCore.QTime.currentTime()
                elapsed_ms = start_time.msecsTo(end_time)

                results["tested_sizes"].append((width, height))
                results["performance_data"].append(
                    {"size": (width, height), "update_time_ms": elapsed_ms}
                )

                # レイアウトの問題をチェック（基本的な検証）
                if elapsed_ms > 100:  # 100ms以上かかった場合は問題として記録
                    results["layout_issues"].append(
                        {
                            "size": (width, height),
                            "issue": "レイアウト更新が遅い: {elapsed_ms}ms",
                        }
                    )

            self.logger.info(
                "レスポンシブレイアウトテストを完了しました: {len(sizes)}サイズ",
                LogCategory.UI,
            )

        except Exception:
            results["error"] = str()
            self.logger.error(
                "レスポンシブレイアウトテストでエラーが発生しました: {str()}",
                LogCategory.UI,
            )
        finally:
            # 元のサイズに戻す
            self.widget.resize(original_size)

        return results
