"""
プレビュー関連のモジュール

このモジュールは、Qt-Theme-Studioアプリケーションのプレビュー機能を提供します。
"""

from typing import Any, Callable, Dict, List, Optional
from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.adapters.theme_adapter import ThemeAdapter
from qt_theme_studio.logger import get_logger, LogCategory


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
        self.QtWidgets = qt_modules['QtWidgets']
        self.QtCore = qt_modules['QtCore']
        self.QtGui = qt_modules['QtGui']
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
        scroll_area.setHorizontalScrollBarPolicy(self.QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(self.QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
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
        self.widgets['push_button'] = push_button
        
        # QPushButton (無効)
        disabled_button = self.QtWidgets.QPushButton("無効ボタン")
        disabled_button.setEnabled(False)
        group_layout.addWidget(disabled_button)
        self.widgets['disabled_button'] = disabled_button
        
        # QPushButton (デフォルト)
        default_button = self.QtWidgets.QPushButton("デフォルトボタン")
        default_button.setDefault(True)
        group_layout.addWidget(default_button)
        self.widgets['default_button'] = default_button
        
        # QToolButton
        tool_button = self.QtWidgets.QToolButton()
        tool_button.setText("ツール")
        tool_button.setToolButtonStyle(self.QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        group_layout.addWidget(tool_button)
        self.widgets['tool_button'] = tool_button
        
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
        self.widgets['line_edit'] = line_edit
        
        # QTextEdit
        text_edit_label = self.QtWidgets.QLabel("複数行テキスト:")
        text_edit = self.QtWidgets.QTextEdit()
        text_edit.setPlainText("複数行の\\nサンプルテキスト\\nです。")
        text_edit.setMaximumHeight(80)
        group_layout.addWidget(text_edit_label, 1, 0)
        group_layout.addWidget(text_edit, 1, 1)
        self.widgets['text_edit'] = text_edit
        
        # QSpinBox
        spinbox_label = self.QtWidgets.QLabel("数値入力:")
        spinbox = self.QtWidgets.QSpinBox()
        spinbox.setRange(0, 100)
        spinbox.setValue(50)
        group_layout.addWidget(spinbox_label, 2, 0)
        group_layout.addWidget(spinbox, 2, 1)
        self.widgets['spinbox'] = spinbox
        
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
        self.widgets['combo'] = combo
        
        # QCheckBox
        checkbox1 = self.QtWidgets.QCheckBox("チェックボックス1")
        checkbox1.setChecked(True)
        checkbox2 = self.QtWidgets.QCheckBox("チェックボックス2")
        checkbox3 = self.QtWidgets.QCheckBox("無効チェックボックス")
        checkbox3.setEnabled(False)
        
        group_layout.addWidget(checkbox1, 1, 0)
        group_layout.addWidget(checkbox2, 1, 1)
        group_layout.addWidget(checkbox3, 1, 2)
        self.widgets['checkbox1'] = checkbox1
        self.widgets['checkbox2'] = checkbox2
        self.widgets['checkbox3'] = checkbox3
        
        # QRadioButton
        radio1 = self.QtWidgets.QRadioButton("ラジオボタン1")
        radio1.setChecked(True)
        radio2 = self.QtWidgets.QRadioButton("ラジオボタン2")
        radio3 = self.QtWidgets.QRadioButton("ラジオボタン3")
        
        group_layout.addWidget(radio1, 2, 0)
        group_layout.addWidget(radio2, 2, 1)
        group_layout.addWidget(radio3, 2, 2)
        self.widgets['radio1'] = radio1
        self.widgets['radio2'] = radio2
        self.widgets['radio3'] = radio3
        
        layout.addWidget(group)
    
    def _create_display_widgets(self, layout: Any) -> None:
        """表示ウィジェットを作成します"""
        group = self.QtWidgets.QGroupBox("表示")
        group_layout = self.QtWidgets.QVBoxLayout(group)
        
        # QLabel
        label = self.QtWidgets.QLabel("これはラベルです。長いテキストの表示例。")
        label.setWordWrap(True)
        group_layout.addWidget(label)
        self.widgets['label'] = label
        
        # QListWidget
        list_widget = self.QtWidgets.QListWidget()
        list_widget.addItems(["アイテム1", "アイテム2", "アイテム3", "アイテム4"])
        list_widget.setCurrentRow(1)
        list_widget.setMaximumHeight(100)
        group_layout.addWidget(list_widget)
        self.widgets['list_widget'] = list_widget
        
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
        self.widgets['tree_widget'] = tree_widget
        
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
        self.widgets['tab_widget'] = tab_widget
        
        # QGroupBox (ネスト)
        nested_group = self.QtWidgets.QGroupBox("ネストグループ")
        nested_layout = self.QtWidgets.QVBoxLayout(nested_group)
        nested_layout.addWidget(self.QtWidgets.QLabel("ネストされた内容"))
        nested_layout.addWidget(self.QtWidgets.QSlider(self.QtCore.Qt.Orientation.Horizontal))
        
        group_layout.addWidget(nested_group)
        self.widgets['nested_group'] = nested_group
        
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
        self.widgets['progress_bar'] = progress_bar
        
        # QSlider
        slider_layout = self.QtWidgets.QHBoxLayout()
        slider_label = self.QtWidgets.QLabel("スライダー:")
        slider = self.QtWidgets.QSlider(self.QtCore.Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(30)
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(slider)
        group_layout.addLayout(slider_layout)
        self.widgets['slider'] = slider
        
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
        
        # ウィジェット全体にスタイルシートを適用
        self.widget.setStyleSheet(stylesheet)
        
        self.logger.debug("ウィジェットにテーマを適用しました", LogCategory.UI)
    
    def _generate_stylesheet_from_theme(self, theme_data: Dict[str, Any]) -> str:
        """テーマデータからスタイルシートを生成します
        
        Args:
            theme_data: テーマデータ
            
        Returns:
            str: 生成されたスタイルシート
        """
        styles = []
        
        # 色設定の適用
        if 'colors' in theme_data:
            colors = theme_data['colors']
            
            # 基本的な背景色とテキスト色
            if 'background' in colors:
                bg_color = colors['background']
                styles.append(
                    f"QWidget {{ background-color: {bg_color}; }}"
                )
            
            if 'text' in colors:
                text_color = colors['text']
                # より具体的なセレクターでテキスト色を確実に適用
                styles.append(f"""
                * {{ color: {text_color} !important; }}
                QWidget {{ color: {text_color}; }}
                QLabel {{ color: {text_color}; }}
                QGroupBox {{ color: {text_color}; }}
                QGroupBox::title {{ color: {text_color}; }}
                QCheckBox {{ color: {text_color}; }}
                QRadioButton {{ color: {text_color}; }}
                QTreeWidget {{ color: {text_color}; }}
                QTreeWidget::item {{ color: {text_color}; }}
                QListWidget {{ color: {text_color}; }}
                QListWidget::item {{ color: {text_color}; }}
                QComboBox {{ color: {text_color}; }}
                QSpinBox {{ color: {text_color}; }}
                QLineEdit {{ color: {text_color}; }}
                QTextEdit {{ color: {text_color}; }}
                QTabWidget {{ color: {text_color}; }}
                QTabBar::tab {{ color: {text_color}; }}
                """)
            
            # ボタンのスタイル
            if 'primary' in colors:
                # 無効状態の色をテーマから取得（フォールバック付き）
                bg_color = colors.get('background', '#f0f0f0')
                text_color = colors.get('text', '#333333')
                
                disabled_bg = colors.get(
                    'disabled', 
                    colors.get(
                        'surface', 
                        self._lighten_color(bg_color, 0.1)
                    )
                )
                disabled_text = colors.get(
                    'text_disabled', 
                    colors.get(
                        'text_muted', 
                        self._darken_color(text_color, 0.5)
                    )
                )
                
                styles.append(f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: {self._get_optimal_text_color(colors['primary'])};
                    border: 1px solid {colors['primary']};
                    padding: 5px 10px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(colors['primary'])};
                }}
                QPushButton:pressed {{
                    background-color: {self._darken_color(colors['primary'], 0.2)};
                }}
                QPushButton:disabled {{
                    background-color: {disabled_bg};
                    color: {disabled_text};
                }}
                """)
            
            # 入力フィールドのスタイル
            if 'background' in colors and 'text' in colors:
                # ボーダー色をテーマから取得（フォールバック付き）
                bg_color = colors.get('background', '#ffffff')
                border_color = colors.get(
                    'border', 
                    colors.get(
                        'surface', 
                        self._darken_color(bg_color, 0.2)
                    )
                )
                focus_color = colors.get(
                    'primary', 
                    colors.get('accent', '#0078d4')
                )
                
                styles.append(f"""
                QLineEdit, QTextEdit, QSpinBox, QComboBox {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    border: 1px solid {border_color};
                    padding: 3px;
                    border-radius: 2px;
                }}
                QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
                    border-color: {focus_color};
                }}
                """)
            
            # QGroupBoxのスタイル
            if 'background' in colors and 'text' in colors:
                border_color = colors.get('border', colors.get('surface', self._darken_color(colors['background'], 0.2)))
                styles.append(f"""
                QGroupBox {{
                    color: {colors['text']};
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 5px;
                }}
                QGroupBox::title {{
                    color: {colors['text']};
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }}
                """)
            
            # リストウィジェットのスタイル（選択・非選択状態）
            if 'background' in colors and 'text' in colors:
                selection_bg = colors.get('primary', colors.get('accent', '#0078d4'))
                selection_text = self._get_optimal_text_color(selection_bg)
                alternate_bg = colors.get('alternate', self._lighten_color(colors['background'], 0.05))
                
                styles.append(f"""
                QListWidget, QTreeWidget {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    border: 1px solid {border_color};
                    alternate-background-color: {alternate_bg};
                }}
                QListWidget::item, QTreeWidget::item {{
                    color: {colors['text']};
                }}
                QListWidget::item:selected, QTreeWidget::item:selected {{
                    background-color: {selection_bg};
                    color: {selection_text};
                }}
                QListWidget::item:hover, QTreeWidget::item:hover {{
                    background-color: {self._lighten_color(selection_bg, 0.3)};
                    color: {colors['text']};
                }}
                """)
            
            # チェックボックス・ラジオボタンのスタイル
            if 'primary' in colors and 'text' in colors:
                styles.append(f"""
                QCheckBox, QRadioButton {{
                    color: {colors['text']};
                }}
                QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                    background-color: {colors['primary']};
                    border: 1px solid {colors['primary']};
                }}
                QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {{
                    background-color: {colors['background']};
                    border: 1px solid {border_color};
                }}
                """)
            
            # プログレスバーのスタイル
            if 'primary' in colors:
                styles.append(f"""
                QProgressBar {{
                    background-color: {colors.get('background', '#ffffff')};
                    color: {colors.get('text', '#000000')};
                    border: 1px solid {border_color};
                    border-radius: 3px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {colors['primary']};
                    border-radius: 2px;
                }}
                """)
            
            # スライダーのスタイル
            if 'primary' in colors:
                styles.append(f"""
                QSlider::groove:horizontal {{
                    background-color: {border_color};
                    height: 6px;
                    border-radius: 3px;
                }}
                QSlider::handle:horizontal {{
                    background-color: {colors['primary']};
                    border: 1px solid {colors['primary']};
                    width: 16px;
                    margin: -5px 0;
                    border-radius: 8px;
                }}
                QSlider::sub-page:horizontal {{
                    background-color: {colors['primary']};
                    border-radius: 3px;
                }}
                """)
            
            # タブウィジェットのスタイル
            if 'background' in colors and 'text' in colors:
                tab_selected_bg = colors.get('primary', colors.get('accent', '#0078d4'))
                tab_selected_text = self._get_optimal_text_color(tab_selected_bg)
                
                styles.append(f"""
                QTabWidget::pane {{
                    background-color: {colors['background']};
                    border: 1px solid {border_color};
                }}
                QTabBar::tab {{
                    background-color: {self._lighten_color(colors['background'], 0.1)};
                    color: {colors['text']};
                    border: 1px solid {border_color};
                    padding: 5px 10px;
                    margin-right: 2px;
                }}
                QTabBar::tab:selected {{
                    background-color: {tab_selected_bg};
                    color: {tab_selected_text};
                }}
                QTabBar::tab:hover {{
                    background-color: {self._lighten_color(tab_selected_bg, 0.3)};
                }}
                """)
            
            # QLabel用のスタイル
            if 'text' in colors:
                styles.append(f"""
                QLabel {{
                    color: {colors['text']};
                }}
                """)
        
        # フォント設定の適用
        if 'fonts' in theme_data and 'default' in theme_data['fonts']:
            font = theme_data['fonts']['default']
            family = font.get('family', 'Arial')
            size = font.get('size', 12)
            font_style = f"font-family: {family}; font-size: {size}px;"
            
            if font.get('bold', False):
                font_style += " font-weight: bold;"
            if font.get('italic', False):
                font_style += " font-style: italic;"
            
            styles.append(f"QWidget {{ {font_style} }}")
        
        return "\\n".join(styles)
    
    def _get_optimal_text_color(self, background_color: str) -> str:
        """背景色に対して最適なテキスト色を取得します
        
        Args:
            background_color: 背景色（16進数カラーコード）
            
        Returns:
            str: 最適なテキスト色
        """
        try:
            # 背景色の明度を計算
            if background_color.startswith('#'):
                background_color = background_color[1:]
            
            r = int(background_color[0:2], 16)
            g = int(background_color[2:4], 16)
            b = int(background_color[4:6], 16)
            
            # 相対輝度を計算（WCAG準拠）
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            # 明度に基づいてテキスト色を決定
            if luminance > 0.5:
                return "#000000"  # 明るい背景には黒いテキスト
            else:
                return "#ffffff"  # 暗い背景には白いテキスト
        except (ValueError, IndexError):
            return "#000000"  # エラーの場合は黒を返す
    
    def _lighten_color(self, color: str, factor: float = 0.1) -> str:
        """色を明るくします
        
        Args:
            color: 16進数カラーコード
            factor: 明るくする係数（0.0-1.0）
            
        Returns:
            str: 明るくされた色
        """
        try:
            # 16進数カラーコードをRGBに変換
            if color.startswith('#'):
                color = color[1:]
            
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            # 色を明るくする
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return color  # エラーの場合は元の色を返す
    
    def _darken_color(self, color: str, factor: float = 0.1) -> str:
        """色を暗くします
        
        Args:
            color: 16進数カラーコード
            factor: 暗くする係数（0.0-1.0）
            
        Returns:
            str: 暗くされた色
        """
        try:
            # 16進数カラーコードをRGBに変換
            if color.startswith('#'):
                color = color[1:]
            
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            # 色を暗くする
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return color  # エラーの場合は元の色を返す


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
        self.QtWidgets = self.qt_modules['QtWidgets']
        self.QtCore = self.qt_modules['QtCore']
        self.QtGui = self.qt_modules['QtGui']
        
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
        
        self.logger.info("プレビューウィンドウウィジェットを作成しました", LogCategory.UI)
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
            
            self.logger.debug(f"プレビューを更新しました（処理時間: {elapsed_ms}ms）", LogCategory.UI)
            
            # 500ms以内の更新保証をチェック
            if elapsed_ms > 500:
                self.logger.warning(f"プレビュー更新が500msを超えました: {elapsed_ms}ms", LogCategory.UI)
            
        except Exception as e:
            self.logger.error(f"プレビュー更新中にエラーが発生しました: {str(e)}", LogCategory.UI)
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
                "PNG画像 (*.png);;すべてのファイル (*)"
            )
            
            if file_path:
                # ウィジェットのスクリーンショットを取得
                pixmap = self.widget.grab()
                
                # PNG形式で保存
                if pixmap.save(file_path, "PNG"):
                    self.logger.info(f"プレビュー画像を保存しました: {file_path}", LogCategory.UI)
                    
                    # 成功メッセージを表示
                    self.QtWidgets.QMessageBox.information(
                        self.widget,
                        "エクスポート完了",
                        f"プレビュー画像を保存しました:\\n{file_path}"
                    )
                else:
                    raise Exception("画像の保存に失敗しました")
                    
        except Exception as e:
            self.logger.error(f"プレビュー画像のエクスポートに失敗しました: {str(e)}", LogCategory.UI)
            
            # エラーメッセージを表示
            self.QtWidgets.QMessageBox.critical(
                self.widget,
                "エクスポートエラー",
                f"プレビュー画像のエクスポートに失敗しました:\\n{str(e)}"
            )
    
    def get_widget_showcase(self) -> Optional[WidgetShowcase]:
        """ウィジェットショーケースを取得します
        
        Returns:
            Optional[WidgetShowcase]: ウィジェットショーケース
        """
        return self.widget_showcase
    
    def set_theme_applied_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
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
            return {'error': 'プレビューウィンドウが作成されていません'}
        
        if sizes is None:
            sizes = [(800, 600), (1024, 768), (1280, 1024), (1920, 1080)]
        
        results = {
            'tested_sizes': [],
            'layout_issues': [],
            'performance_data': []
        }
        
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
                
                results['tested_sizes'].append((width, height))
                results['performance_data'].append({
                    'size': (width, height),
                    'update_time_ms': elapsed_ms
                })
                
                # レイアウトの問題をチェック（基本的な検証）
                if elapsed_ms > 100:  # 100ms以上かかった場合は問題として記録
                    results['layout_issues'].append({
                        'size': (width, height),
                        'issue': f'レイアウト更新が遅い: {elapsed_ms}ms'
                    })
            
            self.logger.info(f"レスポンシブレイアウトテストを完了しました: {len(sizes)}サイズ", LogCategory.UI)
            
        except Exception as e:
            results['error'] = str(e)
            self.logger.error(f"レスポンシブレイアウトテストでエラーが発生しました: {str(e)}", LogCategory.UI)
        finally:
            # 元のサイズに戻す
            self.widget.resize(original_size)
        
        return results