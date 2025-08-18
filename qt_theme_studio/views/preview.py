"""
プレビュー関連のモジュール

このモジュールは、Qt-Theme-Studioアプリケーションのプレビュー機能を提供します。
"""

from contextlib import suppress
from typing import Any, Callable, Optional

from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.adapters.theme_adapter import ThemeAdapter
from qt_theme_studio.logger import LogCategory, get_logger


class WidgetShowcase:
    """ウィジェットショーケースコンポーネント

    包括的なQtウィジェットセット(QPushButton、QLineEdit、QComboBox等)のプレビュー表示を提供します。
    """

    def __init__(self, qt_modules: dict[str, Any], parent=None):
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
        self.widgets: dict[str, Any] = {}

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

    def get_all_widgets(self) -> dict[str, Any]:
        """すべてのウィジェットを取得します

        Returns: dict[str, Any]: ウィジェット辞書
        """
        return self.widgets.copy()

    def apply_theme_to_widgets(self, theme_data: dict[str, Any]) -> None:
        """ウィジェットにテーマを適用します

        Args:
            theme_data: テーマデータ
        """
        if not self.widget or not theme_data:
            return

        # 基本的なスタイルシートを生成
        stylesheet = self._generate_stylesheet_from_theme(theme_data)

        # デバッグ情報を出力
        self.logger.info("生成されたスタイルシート:")
        self.logger.info(stylesheet)
        self.logger.info(f"ウィジェット: {self.widget}")
        self.logger.info(f"ウィジェットのクラス: {type(self.widget)}")

        # ウィジェット全体にスタイルシートを適用
        self.widget.setStyleSheet(stylesheet)

        # 個別のウィジェットにテーマを適用
        self._apply_theme_to_individual_widgets(theme_data)

        # スタイルシートが効かない場合の代替手段: パレットを直接操作
        self._apply_theme_via_palette(theme_data)

        # デバッグ: 実際のウィジェットの色を確認
        self._debug_widget_colors()

        self.logger.debug("ウィジェットにテーマを適用しました", LogCategory.UI)

    def _apply_theme_to_individual_widgets(self, theme_data: dict[str, Any]) -> None:
        """個別のウィジェットにテーマを適用"""
        if not self.widget or not theme_data:
            return

        try:
            colors = theme_data.get("colors", {})
            if not colors:
                return

            # 各ウィジェットタイプ別のスタイルシートを生成
            button_stylesheet = self._generate_button_stylesheet(colors)
            input_stylesheet = self._generate_input_stylesheet(colors)
            selection_stylesheet = self._generate_selection_stylesheet(colors)
            display_stylesheet = self._generate_display_stylesheet(colors)
            container_stylesheet = self._generate_container_stylesheet(colors)
            progress_stylesheet = self._generate_progress_stylesheet(colors)

            # 各ウィジェットに個別のスタイルシートを適用
            for widget_name, widget in self.widgets.items():
                try:
                    if "button" in widget_name.lower():
                        widget.setStyleSheet(button_stylesheet)
                    elif any(
                        keyword in widget_name.lower()
                        for keyword in ["input", "edit", "line"]
                    ):
                        widget.setStyleSheet(input_stylesheet)
                    elif any(
                        keyword in widget_name.lower()
                        for keyword in ["combo", "list", "table"]
                    ):
                        widget.setStyleSheet(selection_stylesheet)
                    elif any(
                        keyword in widget_name.lower()
                        for keyword in ["label", "text", "group"]
                    ):
                        widget.setStyleSheet(display_stylesheet)
                    elif any(
                        keyword in widget_name.lower()
                        for keyword in ["frame", "widget", "area"]
                    ):
                        widget.setStyleSheet(container_stylesheet)
                    elif any(
                        keyword in widget_name.lower()
                        for keyword in ["progress", "bar", "slider"]
                    ):
                        widget.setStyleSheet(progress_stylesheet)
                    else:
                        # デフォルトスタイル
                        widget.setStyleSheet(self._generate_default_stylesheet(colors))
                except Exception as e:
                    self.logger.debug(
                        f"ウィジェット {widget_name} へのスタイル適用エラー: {e}"
                    )

            self.logger.info("個別ウィジェットにテーマを適用しました")

        except Exception as e:
            self.logger.error(f"個別ウィジェットへのテーマ適用エラー: {e}")

    def _generate_button_stylesheet(self, colors: dict[str, str]) -> str:
        """ボタン用のスタイルシートを生成"""
        primary = colors.get("primary", "#007acc")
        button_bg = colors.get("button_background", primary)
        button_text = colors.get("button_text", "#ffffff")
        button_hover = colors.get("button_hover", colors.get("accent", primary))

        return f"""
        QPushButton {{
            background-color: {button_bg};
            color: {button_text};
            border: 2px solid {button_bg};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
        }}
        QPushButton:hover {{
            background-color: {button_hover};
            border-color: {button_hover};
        }}
        QPushButton:pressed {{
            background-color: {colors.get("button_pressed", button_hover)};
        }}
        QPushButton:disabled {{
            background-color: {colors.get("disabled_background", "#cccccc")};
            color: {colors.get("disabled_text", "#666666")};
            border-color: {colors.get("disabled_border", "#cccccc")};
        }}
        """

    def _generate_input_stylesheet(self, colors: dict[str, str]) -> str:
        """入力ウィジェット用のスタイルシートを生成"""
        input_bg = colors.get("input_background", colors.get("background", "#ffffff"))
        input_text = colors.get("input_text", colors.get("text", "#333333"))
        input_border = colors.get("input_border", colors.get("primary", "#007acc"))

        return f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {input_bg};
            color: {input_text};
            border: 2px solid {input_border};
            border-radius: 4px;
            padding: 6px;
            selection-background-color: {colors.get("selection_background", colors.get("primary", "#007acc"))};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors.get("focus_border", colors.get("accent", input_border))};
            border-width: 3px;
        }}
        """

    def _generate_selection_stylesheet(self, colors: dict[str, str]) -> str:
        """選択ウィジェット用のスタイルシートを生成"""
        selection_bg = colors.get(
            "selection_background", colors.get("primary", "#007acc")
        )
        selection_text = colors.get("selection_text", "#ffffff")

        return f"""
        QComboBox, QListWidget, QTableWidget {{
            background-color: {colors.get("input_background", colors.get("background", "#ffffff"))};
            color: {colors.get("input_text", colors.get("text", "#333333"))};
            border: 2px solid {colors.get("input_border", colors.get("primary", "#007acc"))};
            border-radius: 4px;
            padding: 4px;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors.get("text", "#333333")};
        }}
        QComboBox QAbstractItemView {{
            background-color: {colors.get("input_background", colors.get("background", "#ffffff"))};
            color: {colors.get("input_text", colors.get("text", "#333333"))};
            selection-background-color: {selection_bg};
            selection-color: {selection_text};
        }}
        """

    def _generate_display_stylesheet(self, colors: dict[str, str]) -> str:
        """表示ウィジェット用のスタイルシートを生成"""
        return f"""
        QLabel, QGroupBox {{
            color: {colors.get("text", "#333333")};
            background-color: transparent;
        }}
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {colors.get("border", colors.get("primary", "#007acc"))};
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
        }}
        """

    def _generate_container_stylesheet(self, colors: dict[str, str]) -> str:
        """コンテナウィジェット用のスタイルシートを生成"""
        return f"""
        QFrame, QWidget {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
        }}
        QScrollArea {{
            background-color: {colors.get("background", "#ffffff")};
            border: 1px solid {colors.get("border", colors.get("primary", "#007acc"))};
            border-radius: 4px;
        }}
        QTabWidget::pane {{
            border: 1px solid {colors.get("border", colors.get("primary", "#007acc"))};
            background-color: {colors.get("background", "#ffffff")};
        }}
        QTabBar::tab {{
            background-color: {colors.get("input_background", colors.get("background", "#f0f0f0"))};
            color: {colors.get("text", "#333333")};
            border: 1px solid {colors.get("border", colors.get("primary", "#007acc"))};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 16px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
            border-bottom: 1px solid {colors.get("background", "#ffffff")};
        }}
        QTabBar::tab:hover {{
            background-color: {colors.get("input_background", colors.get("background", "#f0f0f0"))};
        }}
        QScrollBar:vertical {{
            background-color: {colors.get("scrollbar_background", colors.get("background", "#f0f0f0"))};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {colors.get("scrollbar_handle", colors.get("primary", "#007acc"))};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {colors.get("scrollbar_handle_hover", colors.get("accent", colors.get("primary", "#007acc")))};
        }}
        """

    def _generate_progress_stylesheet(self, colors: dict[str, str]) -> str:
        """プログレスウィジェット用のスタイルシートを生成"""
        return f"""
        QProgressBar, QSlider {{
            background-color: {colors.get("progress_background", colors.get("background", "#f0f0f0"))};
            border: 1px solid {colors.get("border", colors.get("primary", "#007acc"))};
            border-radius: 4px;
        }}
        QProgressBar::chunk {{
            background-color: {colors.get("progress_fill", colors.get("primary", "#007acc"))};
            border-radius: 3px;
        }}
        QSlider::groove:horizontal {{
            background-color: {colors.get("slider_groove", colors.get("background", "#f0f0f0"))};
            border: 1px solid {colors.get("border", colors.get("primary", "#007acc"))};
            border-radius: 2px;
            height: 8px;
        }}
        QSlider::handle:horizontal {{
            background-color: {colors.get("slider_handle", colors.get("primary", "#007acc"))};
            border: 2px solid {colors.get("slider_handle_border", colors.get("primary", "#007acc"))};
            border-radius: 8px;
            width: 16px;
            margin: -4px 0;
        }}
        """

    def _generate_default_stylesheet(self, colors: dict[str, str]) -> str:
        """デフォルトのスタイルシートを生成"""
        return f"""
        QWidget {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
        }}
        QMainWindow {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
        }}
        QMenuBar {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
            border-bottom: 1px solid {colors.get("border", colors.get("primary", "#007acc"))};
        }}
        QMenuBar::item {{
            background-color: transparent;
            color: {colors.get("text", "#333333")};
            padding: 4px 8px;
        }}
        QMenuBar::item:selected {{
            background-color: {colors.get("selection_background", colors.get("primary", "#007acc"))};
            color: {colors.get("selection_text", "#ffffff")};
        }}
        QMenu {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
            border: 1px solid {colors.get("border", colors.get("primary", "#007acc"))};
            border-radius: 4px;
        }}
        QMenu::item {{
            background-color: transparent;
            color: {colors.get("text", "#333333")};
            padding: 6px 20px;
        }}
        QMenu::item:selected {{
            background-color: {colors.get("selection_background", colors.get("primary", "#007acc"))};
            color: {colors.get("selection_text", "#ffffff")};
        }}
        QToolBar {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
            border: 1px solid {colors.get("border", colors.get("primary", "#007acc"))};
            border-radius: 4px;
            spacing: 2px;
        }}
        QToolButton {{
            background-color: {colors.get("button_background", colors.get("primary", "#007acc"))};
            color: {colors.get("button_text", "#ffffff")};
            border: 1px solid {colors.get("button_border", colors.get("primary", "#007acc"))};
            border-radius: 4px;
            padding: 4px 8px;
            margin: 1px;
        }}
        QToolButton:hover {{
            background-color: {colors.get("button_hover", colors.get("accent", colors.get("primary", "#007acc")))};
            border-color: {colors.get("button_hover", colors.get("accent", colors.get("primary", "#007acc")))};
        }}
        QToolButton:pressed {{
            background-color: {colors.get("button_pressed", colors.get("primary", "#007acc"))};
        }}
        QStatusBar {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
            border-top: 1px solid {colors.get("border", colors.get("primary", "#007acc"))};
        }}
        """

    def _apply_theme_via_palette(self, theme_data: dict[str, Any]) -> None:
        """パレットを直接操作してテーマを適用(スタイルシートの代替手段)"""
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
                with suppress(Exception):
                    child.setPalette(palette)

            # 強制的に再描画を実行
            self.widget.update()
            self.widget.repaint()

            # 子ウィジェットも再描画
            for child in self.widget.findChildren(self.QtWidgets.QWidget):
                with suppress(Exception):
                    child.update()
                    child.repaint()

            self.logger.info(
                "パレットを直接操作してテーマを適用し、強制再描画を実行しました"
            )

        except Exception as e:
            self.logger.info(f"パレット操作でエラー: {e}")

    def _debug_widget_colors(self):
        """ウィジェットの実際の色をデバッグ出力"""
        if not self.widget:
            return

        try:
            # ウィジェットのパレットを取得
            palette = self.widget.palette()

            self.logger.info("\n=== ウィジェットの実際の色 ===")
            self.logger.info(f"ウィジェット: {self.widget}")
            self.logger.info(f"ウィジェットのクラス: {type(self.widget)}")

            # 背景色
            bg_color = palette.color(palette.ColorRole.Window)
            self.logger.info(f"背景色 (Window): {bg_color.name()}")

            # テキスト色
            text_color = palette.color(palette.ColorRole.WindowText)
            self.logger.info(f"テキスト色 (WindowText): {text_color.name()}")

            # ベース色
            base_color = palette.color(palette.ColorRole.Base)
            self.logger.info(f"ベース色 (Base): {base_color.name()}")

            # ベーステキスト色
            base_text_color = palette.color(palette.ColorRole.Text)
            self.logger.info(f"ベーステキスト色 (Text): {base_text_color.name()}")

            # ボタン色
            button_color = palette.color(palette.ColorRole.Button)
            self.logger.info(f"ボタン色 (Button): {button_color.name()}")

            # ボタンテキスト色
            button_text_color = palette.color(palette.ColorRole.ButtonText)
            self.logger.info(
                f"ボタンテキスト色 (ButtonText): {button_text_color.name()}"
            )

            # スタイルシートの状態
            stylesheet = self.widget.styleSheet()
            self.logger.info(f"現在のスタイルシート: {stylesheet[:200]}...")

            # スタイルシートの有効性をチェック
            self.logger.info("\n--- スタイルシートの有効性チェック ---")
            self.logger.info(f"スタイルシートが空: {not bool(stylesheet)}")
            self.logger.info(f"スタイルシートの長さ: {len(stylesheet)}")

            # ウィジェットのスタイル状態
            self.logger.info(f"ウィジェットのスタイル: {self.widget.style()}")
            self.logger.info(
                f"ウィジェットのスタイルオブジェクト: {self.widget.style().objectName()}"
            )

            # スタイルシートが無効化されていないか
            self.logger.info(
                f"スタイルシートが無効: {self.widget.property('styleSheetDisabled')}"
            )

            # ウィジェットのプロパティ
            self.logger.info(
                f"ウィジェットのプロパティ: {self.widget.dynamicPropertyNames()}"
            )

            # Qtのスタイルエンジンの状態
            self.logger.info("\n--- Qtスタイルエンジンの状態 ---")
            self.logger.info(
                f"QApplicationのスタイル: {self.QtWidgets.QApplication.instance().style().objectName()}"
            )
            self.logger.info(
                f"ウィジェットのスタイルシートプロパティ: "
                f"{self.widget.property('styleSheet')}"
            )
            self.logger.info(
                f"ウィジェットのスタイルシートが空: {not bool(self.widget.styleSheet())}"
            )

            # 強制的にスタイルシートを再適用
            self.logger.info("\n--- スタイルシートの強制再適用 ---")
            self.widget.setStyleSheet("")  # 一旦クリア
            self.widget.setStyleSheet(stylesheet)  # 再適用
            self.logger.info("スタイルシートを強制再適用しました")

            # 再適用後の状態を確認
            self.logger.info(
                f"再適用後のスタイルシート: {self.widget.styleSheet()[:100]}..."
            )

            # 子ウィジェットの色も確認
            self.logger.info("\n--- 子ウィジェットの色 ---")
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

                    self.logger.info(
                        f"子ウィジェット {type(child).__name__}: "
                        f"背景={child_bg.name()}, テキスト={child_text.name()}, "
                        f"カスタムスタイル={has_custom_style}, "
                        f"表示={child_visible}, 有効={child_enabled}, "
                        f"位置=({child_geometry.x()},{child_geometry.y()}) "
                        f"サイズ=({child_geometry.width()}x{child_geometry.height()})"
                    )

                    # カスタムスタイルがある場合は詳細を表示
                    if has_custom_style:
                        self.logger.info(
                            f"  → カスタムスタイルシート: {child_stylesheet[:100]}..."
                        )

                except Exception as e:
                    self.logger.info(
                        f"子ウィジェット {type(child).__name__}: エラー - {e}"
                    )

            self.logger.info("=" * 40)

        except Exception as e:
            self.logger.info(f"色のデバッグ中にエラー: {e}")

    def _generate_stylesheet_from_theme(self, theme_data: dict[str, Any]) -> str:
        """テーマデータからスタイルシートを生成します(qt-theme-manager使用)

        Args:
            theme_data: テーマデータ

        Returns:
            str: 生成されたスタイルシート
        """
        try:
            # qt-theme-managerのStylesheetGeneratorを使用
            import qt_theme_manager

            # 基本モードでスタイルシート生成(プレビュー用)
            generator = qt_theme_manager.StylesheetGenerator(
                self._convert_to_qt_theme_manager_format(theme_data),
                advanced_mode=False,
            )
            stylesheet = generator.generate_qss()

            self.logger.debug(
                "qt-theme-managerでスタイルシートを生成しました", LogCategory.UI
            )
            return stylesheet

        except Exception as e:
            self.logger.error(
                f"qt-theme-managerでのスタイルシート生成に失敗: {e}", LogCategory.UI
            )
            # エラーの場合は空のスタイルシートを返す
            return ""

    def _convert_to_qt_theme_manager_format(
        self, theme_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Qt-Theme-Studio形式をqt-theme-manager形式に変換"""
        try:
            colors = theme_data.get("colors", {})

            return {
                "name": theme_data.get("name", "Unknown"),
                "display_name": theme_data.get(
                    "display_name", theme_data.get("name", "Unknown")
                ),
                "description": theme_data.get("description", ""),
                "primaryColor": colors.get("primary", "#007acc"),
                "accentColor": colors.get("accent", colors.get("primary", "#007acc")),
                "backgroundColor": colors.get("background", "#ffffff"),
                "textColor": colors.get("text", "#333333"),
                "button": {
                    "background": colors.get(
                        "button_background", colors.get("primary", "#007acc")
                    ),
                    "text": colors.get("button_text", colors.get("text", "#ffffff")),
                },
                "input": {
                    "background": colors.get(
                        "input_background", colors.get("background", "#ffffff")
                    ),
                    "text": colors.get("input_text", colors.get("text", "#333333")),
                    "border": colors.get(
                        "input_border", colors.get("primary", "#007acc")
                    ),
                },
                "status": {
                    "background": colors.get(
                        "status_background", colors.get("background", "#ffffff")
                    ),
                    "text": colors.get("status_text", colors.get("text", "#333333")),
                    "border": colors.get("status_border", "#dee2e6"),
                },
            }

        except Exception as e:
            self.logger.error(f"テーマ形式変換に失敗: {e}", LogCategory.UI)
            # フォールバック: 基本的な色設定のみ
            return {
                "name": "Fallback Theme",
                "display_name": "フォールバックテーマ",
                "description": "エラー時のフォールバックテーマ",
                "primaryColor": "#007acc",
                "backgroundColor": "#ffffff",
                "textColor": "#333333",
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
        self.pending_theme_data: Optional[dict[str, Any]] = None

        # コールバック
        self.theme_applied_callback: Optional[Callable[[dict[str, Any]], None]] = None

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

    def update_preview(self, theme_data: dict[str, Any]) -> None:
        """プレビューを更新します(500ms以内の更新保証とデバウンス処理)

        Args:
            theme_data: 適用するテーマデータ
        """
        if not self.widget or not theme_data:
            return

        # 保留中のテーマデータを更新
        self.pending_theme_data = theme_data.copy()

        # タイマーを再開(デバウンス処理)
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
                "プレビューを更新しました(処理時間: {elapsed_ms}ms)", LogCategory.UI
            )

            # 500ms以内の更新保証をチェック
            if elapsed_ms > 500:
                self.logger.warning(
                    "プレビュー更新が500msを超えました: {elapsed_ms}ms", LogCategory.UI
                )

        except Exception as e:
            self.logger.error(
                f"プレビュー更新中にエラーが発生しました: {e}", LogCategory.UI
            )
        finally:
            self.pending_theme_data = None

    def export_preview_image(self) -> None:
        """プレビュー画像をPNG形式でエクスポートします"""
        if not self.widget:
            return

        try:
            # ファイル保存ダイアログのパフォーマンス向上オプションを設定
            dialog = self.QtWidgets.QFileDialog(self.widget, "プレビュー画像を保存")
            dialog.setFileMode(self.QtWidgets.QFileDialog.FileMode.AnyFile)
            dialog.setNameFilter("PNG画像 (*.png);;すべてのファイル (*)")
            dialog.setViewMode(self.QtWidgets.QFileDialog.ViewMode.List)
            dialog.setDefaultSuffix("png")

            # WSL2環境でのフォーカス問題を解決するための設定
            dialog.setWindowModality(self.QtCore.Qt.WindowModality.ApplicationModal)
            dialog.setAttribute(
                self.QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating, False
            )
            dialog.setAttribute(self.QtCore.Qt.WidgetAttribute.WA_NativeWindow, True)

            # フォーカス設定を最適化
            dialog.setFocusPolicy(self.QtCore.Qt.FocusPolicy.StrongFocus)

            dialog.setOptions(
                self.QtWidgets.QFileDialog.Option.DontUseNativeDialog  # ネイティブダイアログを無効化
                | self.QtWidgets.QFileDialog.Option.DontResolveSymlinks  # シンボリックリンクの解決を無効化
            )

            if dialog.exec() == self.QtWidgets.QFileDialog.DialogCode.Accepted:
                file_path = dialog.selectedFiles()[0]
            else:
                return

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

        except Exception as e:
            self.logger.error(
                f"プレビュー画像のエクスポートに失敗しました: {e}", LogCategory.UI
            )

            # エラーメッセージを表示
            self.QtWidgets.QMessageBox.critical(
                self.widget,
                "エクスポートエラー",
                "プレビュー画像のエクスポートに失敗しました",
            )

    def get_widget_showcase(self) -> Optional[WidgetShowcase]:
        """ウィジェットショーケースを取得します

        Returns:
            Optional[WidgetShowcase]: ウィジェットショーケース
        """
        return self.widget_showcase

    def set_theme_applied_callback(
        self, callback: Callable[[dict[str, Any]], None]
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

    def test_responsive_layout(
        self, sizes: Optional[list[tuple]] = None
    ) -> dict[str, Any]:
        """レスポンシブレイアウトテストを実行します

        Args:
            sizes: テストするウィンドウサイズのリスト [(width, height), ...]

        Returns: dict[str, Any]: テスト結果
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

                # レイアウトの問題をチェック(基本的な検証)
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

        except Exception as e:
            results["error"] = str(e)
            self.logger.error(
                f"レスポンシブレイアウトテストでエラーが発生しました: {e}",
                LogCategory.UI,
            )
        finally:
            # 元のサイズに戻す
            self.widget.resize(original_size)

        return results
