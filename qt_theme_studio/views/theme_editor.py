"""
統合テーマエディター

このモジュールは、Qt-Theme-Studioの統合テーマエディターを実装します。
カラーピッカー、フォント選択、プロパティエディターのUIを提供し、
直感的なビジュアルインターフェースでテーマプロパティを編集できます。
"""

import logging
from typing import Any, Dict, Optional, List, Callable

from ..adapters.qt_adapter import QtAdapter
from ..adapters.theme_adapter import ThemeAdapter
from ..logger import get_logger, LogCategory


class ColorPicker:
    """カラーピッカーコンポーネント
    
    色選択、16進値入力、RGB値入力の複数の方法を提供します。
    """
    
    def __init__(self, qt_modules: Dict[str, Any], parent=None):
        """カラーピッカーを初期化します
        
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
        self.color_button: Optional[Any] = None
        self.hex_input: Optional[Any] = None
        self.rgb_inputs: Dict[str, Any] = {}
        self.current_color = self.QtGui.QColor(255, 255, 255)  # デフォルト白色
        
        # コールバック
        self.color_changed_callback: Optional[Callable[[str], None]] = None
        
    def create_widget(self) -> Any:
        """カラーピッカーウィジェットを作成します
        
        Returns:
            QWidget: カラーピッカーウィジェット
        """
        self.widget = self.QtWidgets.QGroupBox("色選択")
        layout = self.QtWidgets.QVBoxLayout(self.widget)
        
        # カラーボタン
        color_button_layout = self.QtWidgets.QHBoxLayout()
        color_button_label = self.QtWidgets.QLabel("色:")
        self.color_button = self.QtWidgets.QPushButton()
        self.color_button.setFixedSize(60, 30)
        self.color_button.setStyleSheet(f"background-color: {self.current_color.name()};")
        self.color_button.clicked.connect(self._open_color_dialog)
        
        color_button_layout.addWidget(color_button_label)
        color_button_layout.addWidget(self.color_button)
        color_button_layout.addStretch()
        layout.addLayout(color_button_layout)
        
        # 16進値入力
        hex_layout = self.QtWidgets.QHBoxLayout()
        hex_label = self.QtWidgets.QLabel("16進値:")
        self.hex_input = self.QtWidgets.QLineEdit()
        self.hex_input.setText(self.current_color.name())
        self.hex_input.setPlaceholderText("#FFFFFF")
        self.hex_input.textChanged.connect(self._on_hex_changed)
        
        hex_layout.addWidget(hex_label)
        hex_layout.addWidget(self.hex_input)
        layout.addLayout(hex_layout)
        
        # RGB値入力
        rgb_group = self.QtWidgets.QGroupBox("RGB値")
        rgb_layout = self.QtWidgets.QGridLayout(rgb_group)
        
        # R, G, B スピンボックス
        for i, component in enumerate(['R', 'G', 'B']):
            label = self.QtWidgets.QLabel(f"{component}:")
            spinbox = self.QtWidgets.QSpinBox()
            spinbox.setRange(0, 255)
            
            # QColorのメソッド名を正しく使用
            if component == 'R':
                spinbox.setValue(self.current_color.red())
            elif component == 'G':
                spinbox.setValue(self.current_color.green())
            elif component == 'B':
                spinbox.setValue(self.current_color.blue())
                
            spinbox.valueChanged.connect(self._on_rgb_changed)
            
            rgb_layout.addWidget(label, i, 0)
            rgb_layout.addWidget(spinbox, i, 1)
            self.rgb_inputs[component.lower()] = spinbox
        
        layout.addWidget(rgb_group)
        
        self.logger.debug("カラーピッカーウィジェットを作成しました", LogCategory.UI)
        return self.widget
    
    def _open_color_dialog(self) -> None:
        """カラーダイアログを開きます"""
        color = self.QtWidgets.QColorDialog.getColor(
            self.current_color, 
            self.parent, 
            "色を選択"
        )
        
        if color.isValid():
            self.set_color(color)
    
    def _on_hex_changed(self) -> None:
        """16進値入力の変更を処理します"""
        hex_text = self.hex_input.text().strip()
        
        # 16進値の検証
        if hex_text.startswith('#') and len(hex_text) in [4, 7]:  # #RGB or #RRGGBB
            try:
                color = self.QtGui.QColor(hex_text)
                if color.isValid():
                    self.current_color = color
                    self._update_ui_from_color()
                    self._notify_color_changed()
            except Exception as e:
                self.logger.debug(f"無効な16進値: {hex_text}, エラー: {str(e)}", LogCategory.UI)
    
    def _on_rgb_changed(self) -> None:
        """RGB値入力の変更を処理します"""
        try:
            r = self.rgb_inputs['r'].value()
            g = self.rgb_inputs['g'].value()
            b = self.rgb_inputs['b'].value()
            
            self.current_color = self.QtGui.QColor(r, g, b)
            self._update_ui_from_color()
            self._notify_color_changed()
            
        except Exception as e:
            self.logger.debug(f"RGB値の更新に失敗: {str(e)}", LogCategory.UI)
    
    def _update_ui_from_color(self) -> None:
        """現在の色からUIを更新します"""
        if not self.widget:
            return
        
        # カラーボタンの更新
        if self.color_button:
            self.color_button.setStyleSheet(f"background-color: {self.current_color.name()};")
        
        # 16進値入力の更新
        if self.hex_input:
            self.hex_input.blockSignals(True)
            self.hex_input.setText(self.current_color.name())
            self.hex_input.blockSignals(False)
        
        # RGB値入力の更新
        for component in ['r', 'g', 'b']:
            if component in self.rgb_inputs:
                spinbox = self.rgb_inputs[component]
                spinbox.blockSignals(True)
                
                # QColorのメソッド名を正しく使用
                if component == 'r':
                    spinbox.setValue(self.current_color.red())
                elif component == 'g':
                    spinbox.setValue(self.current_color.green())
                elif component == 'b':
                    spinbox.setValue(self.current_color.blue())
                    
                spinbox.blockSignals(False)
    
    def _notify_color_changed(self) -> None:
        """色変更をコールバックに通知します"""
        if self.color_changed_callback:
            self.color_changed_callback(self.current_color.name())
    
    def set_color(self, color: Any) -> None:
        """色を設定します
        
        Args:
            color: QColor オブジェクト
        """
        if isinstance(color, self.QtGui.QColor) and color.isValid():
            self.current_color = color
            self._update_ui_from_color()
            self._notify_color_changed()
    
    def get_color(self) -> str:
        """現在の色を16進値で取得します
        
        Returns:
            str: 16進値カラーコード
        """
        return self.current_color.name()
    
    def set_color_changed_callback(self, callback: Callable[[str], None]) -> None:
        """色変更コールバックを設定します
        
        Args:
            callback: 色変更時に呼び出されるコールバック関数
        """
        self.color_changed_callback = callback


class FontSelector:
    """フォント選択コンポーネント
    
    フォントファミリー、サイズ、スタイルの選択機能を提供します。
    """
    
    def __init__(self, qt_modules: Dict[str, Any], parent=None):
        """フォントセレクターを初期化します
        
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
        self.family_combo: Optional[Any] = None
        self.size_spinbox: Optional[Any] = None
        self.bold_checkbox: Optional[Any] = None
        self.italic_checkbox: Optional[Any] = None
        self.preview_label: Optional[Any] = None
        
        # 現在のフォント
        self.current_font = self.QtGui.QFont()
        
        # コールバック
        self.font_changed_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    
    def create_widget(self) -> Any:
        """フォントセレクターウィジェットを作成します
        
        Returns:
            QWidget: フォントセレクターウィジェット
        """
        self.widget = self.QtWidgets.QGroupBox("フォント選択")
        layout = self.QtWidgets.QVBoxLayout(self.widget)
        
        # フォントファミリー選択
        family_layout = self.QtWidgets.QHBoxLayout()
        family_label = self.QtWidgets.QLabel("フォント:")
        self.family_combo = self.QtWidgets.QFontComboBox()
        self.family_combo.setCurrentFont(self.current_font)
        self.family_combo.currentFontChanged.connect(self._on_font_changed)
        
        family_layout.addWidget(family_label)
        family_layout.addWidget(self.family_combo)
        layout.addLayout(family_layout)
        
        # フォントサイズ選択
        size_layout = self.QtWidgets.QHBoxLayout()
        size_label = self.QtWidgets.QLabel("サイズ:")
        self.size_spinbox = self.QtWidgets.QSpinBox()
        self.size_spinbox.setRange(6, 72)
        self.size_spinbox.setValue(self.current_font.pointSize())
        self.size_spinbox.valueChanged.connect(self._on_font_changed)
        
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spinbox)
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # フォントスタイル選択
        style_layout = self.QtWidgets.QHBoxLayout()
        self.bold_checkbox = self.QtWidgets.QCheckBox("太字")
        self.bold_checkbox.setChecked(self.current_font.bold())
        self.bold_checkbox.toggled.connect(self._on_font_changed)
        
        self.italic_checkbox = self.QtWidgets.QCheckBox("斜体")
        self.italic_checkbox.setChecked(self.current_font.italic())
        self.italic_checkbox.toggled.connect(self._on_font_changed)
        
        style_layout.addWidget(self.bold_checkbox)
        style_layout.addWidget(self.italic_checkbox)
        style_layout.addStretch()
        layout.addLayout(style_layout)
        
        # フォントプレビュー
        preview_group = self.QtWidgets.QGroupBox("プレビュー")
        preview_layout = self.QtWidgets.QVBoxLayout(preview_group)
        
        self.preview_label = self.QtWidgets.QLabel("サンプルテキスト Sample Text 123")
        self.preview_label.setFont(self.current_font)
        self.preview_label.setAlignment(self.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                border: 1px solid #cccccc;
                background-color: white;
            }
        """)
        
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)
        
        self.logger.debug("フォントセレクターウィジェットを作成しました", LogCategory.UI)
        return self.widget
    
    def _on_font_changed(self) -> None:
        """フォント変更を処理します"""
        if not self.widget:
            return
        
        # 現在のフォント設定を取得
        family = self.family_combo.currentFont().family()
        size = self.size_spinbox.value()
        bold = self.bold_checkbox.isChecked()
        italic = self.italic_checkbox.isChecked()
        
        # フォントを更新
        self.current_font = self.QtGui.QFont(family, size)
        self.current_font.setBold(bold)
        self.current_font.setItalic(italic)
        
        # プレビューを更新
        if self.preview_label:
            self.preview_label.setFont(self.current_font)
        
        # コールバックを呼び出し
        self._notify_font_changed()
    
    def _notify_font_changed(self) -> None:
        """フォント変更をコールバックに通知します"""
        if self.font_changed_callback:
            font_data = {
                'family': self.current_font.family(),
                'size': self.current_font.pointSize(),
                'bold': self.current_font.bold(),
                'italic': self.current_font.italic()
            }
            self.font_changed_callback(font_data)
    
    def set_font(self, font_data: Dict[str, Any]) -> None:
        """フォントを設定します
        
        Args:
            font_data: フォント設定辞書
        """
        if not self.widget:
            return
        
        # フォント設定を適用
        family = font_data.get('family', 'Arial')
        size = font_data.get('size', 12)
        bold = font_data.get('bold', False)
        italic = font_data.get('italic', False)
        
        self.current_font = self.QtGui.QFont(family, size)
        self.current_font.setBold(bold)
        self.current_font.setItalic(italic)
        
        # UIを更新
        self.family_combo.blockSignals(True)
        self.family_combo.setCurrentFont(self.current_font)
        self.family_combo.blockSignals(False)
        
        self.size_spinbox.blockSignals(True)
        self.size_spinbox.setValue(size)
        self.size_spinbox.blockSignals(False)
        
        self.bold_checkbox.blockSignals(True)
        self.bold_checkbox.setChecked(bold)
        self.bold_checkbox.blockSignals(False)
        
        self.italic_checkbox.blockSignals(True)
        self.italic_checkbox.setChecked(italic)
        self.italic_checkbox.blockSignals(False)
        
        # プレビューを更新
        if self.preview_label:
            self.preview_label.setFont(self.current_font)
    
    def get_font_data(self) -> Dict[str, Any]:
        """現在のフォント設定を取得します
        
        Returns:
            Dict[str, Any]: フォント設定辞書
        """
        return {
            'family': self.current_font.family(),
            'size': self.current_font.pointSize(),
            'bold': self.current_font.bold(),
            'italic': self.current_font.italic()
        }
    
    def set_font_changed_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """フォント変更コールバックを設定します
        
        Args:
            callback: フォント変更時に呼び出されるコールバック関数
        """
        self.font_changed_callback = callback


class PropertyEditor:
    """プロパティエディターコンポーネント
    
    テーマの各種プロパティを編集するためのインターフェースを提供します。
    """
    
    def __init__(self, qt_modules: Dict[str, Any], parent=None):
        """プロパティエディターを初期化します
        
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
        self.property_tree: Optional[Any] = None
        self.properties: Dict[str, Any] = {}
        
        # コールバック
        self.property_changed_callback: Optional[Callable[[str, Any], None]] = None
    
    def create_widget(self) -> Any:
        """プロパティエディターウィジェットを作成します
        
        Returns:
            QWidget: プロパティエディターウィジェット
        """
        self.widget = self.QtWidgets.QGroupBox("プロパティ")
        layout = self.QtWidgets.QVBoxLayout(self.widget)
        
        # プロパティツリー
        self.property_tree = self.QtWidgets.QTreeWidget()
        self.property_tree.setHeaderLabels(["プロパティ", "値"])
        self.property_tree.setAlternatingRowColors(True)
        self.property_tree.itemChanged.connect(self._on_property_changed)
        
        # 基本的なプロパティカテゴリを追加
        self._setup_default_properties()
        
        layout.addWidget(self.property_tree)
        
        # プロパティ追加ボタン
        button_layout = self.QtWidgets.QHBoxLayout()
        add_button = self.QtWidgets.QPushButton("プロパティ追加")
        add_button.clicked.connect(self._add_custom_property)
        
        remove_button = self.QtWidgets.QPushButton("プロパティ削除")
        remove_button.clicked.connect(self._remove_property)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.logger.debug("プロパティエディターウィジェットを作成しました", LogCategory.UI)
        return self.widget
    
    def _setup_default_properties(self) -> None:
        """デフォルトプロパティを設定します"""
        # 基本プロパティカテゴリ
        categories = {
            "基本設定": {
                "テーマ名": "",
                "バージョン": "1.0.0",
                "作成者": ""
            },
            "色設定": {
                "背景色": "#ffffff",
                "テキスト色": "#000000",
                "プライマリ色": "#0078d4",
                "セカンダリ色": "#6c757d"
            },
            "サイズ設定": {
                "フォントサイズ": "12",
                "ボタン高さ": "32",
                "マージン": "8"
            }
        }
        
        for category_name, properties in categories.items():
            category_item = self.QtWidgets.QTreeWidgetItem([category_name, ""])
            category_item.setFlags(category_item.flags() & ~self.QtCore.Qt.ItemFlag.ItemIsEditable)
            self.property_tree.addTopLevelItem(category_item)
            
            for prop_name, prop_value in properties.items():
                prop_item = self.QtWidgets.QTreeWidgetItem([prop_name, str(prop_value)])
                prop_item.setFlags(prop_item.flags() | self.QtCore.Qt.ItemFlag.ItemIsEditable)
                category_item.addChild(prop_item)
                self.properties[f"{category_name}.{prop_name}"] = prop_value
        
        # すべてのカテゴリを展開
        self.property_tree.expandAll()
    
    def _on_property_changed(self, item: Any, column: int) -> None:
        """プロパティ変更を処理します
        
        Args:
            item: 変更されたアイテム
            column: 変更された列
        """
        if column != 1:  # 値列のみ処理
            return
        
        parent = item.parent()
        if not parent:  # カテゴリアイテムは無視
            return
        
        category_name = parent.text(0)
        prop_name = item.text(0)
        prop_value = item.text(1)
        
        full_prop_name = f"{category_name}.{prop_name}"
        self.properties[full_prop_name] = prop_value
        
        # コールバックを呼び出し
        if self.property_changed_callback:
            self.property_changed_callback(full_prop_name, prop_value)
        
        self.logger.debug(f"プロパティが変更されました: {full_prop_name} = {prop_value}", LogCategory.UI)
    
    def _add_custom_property(self) -> None:
        """カスタムプロパティを追加します"""
        dialog = self.QtWidgets.QDialog(self.parent)
        dialog.setWindowTitle("プロパティ追加")
        dialog.setModal(True)
        
        layout = self.QtWidgets.QFormLayout(dialog)
        
        name_input = self.QtWidgets.QLineEdit()
        name_input.setPlaceholderText("プロパティ名")
        
        value_input = self.QtWidgets.QLineEdit()
        value_input.setPlaceholderText("初期値")
        
        category_combo = self.QtWidgets.QComboBox()
        # 既存のカテゴリを追加
        for i in range(self.property_tree.topLevelItemCount()):
            category_combo.addItem(self.property_tree.topLevelItem(i).text(0))
        
        layout.addRow("カテゴリ:", category_combo)
        layout.addRow("プロパティ名:", name_input)
        layout.addRow("初期値:", value_input)
        
        # ボタン
        button_box = self.QtWidgets.QDialogButtonBox(
            self.QtWidgets.QDialogButtonBox.StandardButton.Ok |
            self.QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)
        
        if dialog.exec() == self.QtWidgets.QDialog.DialogCode.Accepted:
            category_name = category_combo.currentText()
            prop_name = name_input.text().strip()
            prop_value = value_input.text().strip()
            
            if prop_name:
                # カテゴリアイテムを検索
                category_item = None
                for i in range(self.property_tree.topLevelItemCount()):
                    item = self.property_tree.topLevelItem(i)
                    if item.text(0) == category_name:
                        category_item = item
                        break
                
                if category_item:
                    # 新しいプロパティアイテムを追加
                    prop_item = self.QtWidgets.QTreeWidgetItem([prop_name, prop_value])
                    prop_item.setFlags(prop_item.flags() | self.QtCore.Qt.ItemFlag.ItemIsEditable)
                    category_item.addChild(prop_item)
                    
                    full_prop_name = f"{category_name}.{prop_name}"
                    self.properties[full_prop_name] = prop_value
                    
                    self.logger.info(f"カスタムプロパティを追加しました: {full_prop_name}", LogCategory.UI)
    
    def _remove_property(self) -> None:
        """選択されたプロパティを削除します"""
        current_item = self.property_tree.currentItem()
        if not current_item or not current_item.parent():
            return
        
        parent = current_item.parent()
        category_name = parent.text(0)
        prop_name = current_item.text(0)
        full_prop_name = f"{category_name}.{prop_name}"
        
        # 確認ダイアログ
        reply = self.QtWidgets.QMessageBox.question(
            self.parent,
            "プロパティ削除",
            f"プロパティ '{prop_name}' を削除しますか？",
            self.QtWidgets.QMessageBox.StandardButton.Yes |
            self.QtWidgets.QMessageBox.StandardButton.No,
            self.QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == self.QtWidgets.QMessageBox.StandardButton.Yes:
            parent.removeChild(current_item)
            if full_prop_name in self.properties:
                del self.properties[full_prop_name]
            
            self.logger.info(f"プロパティを削除しました: {full_prop_name}", LogCategory.UI)
    
    def set_properties(self, properties: Dict[str, Any]) -> None:
        """プロパティを設定します
        
        Args:
            properties: プロパティ辞書
        """
        self.properties.update(properties)
        
        # UIを更新
        for full_prop_name, value in properties.items():
            if '.' in full_prop_name:
                category_name, prop_name = full_prop_name.split('.', 1)
                
                # カテゴリとプロパティアイテムを検索
                for i in range(self.property_tree.topLevelItemCount()):
                    category_item = self.property_tree.topLevelItem(i)
                    if category_item.text(0) == category_name:
                        for j in range(category_item.childCount()):
                            prop_item = category_item.child(j)
                            if prop_item.text(0) == prop_name:
                                prop_item.setText(1, str(value))
                                break
                        break
    
    def get_properties(self) -> Dict[str, Any]:
        """現在のプロパティを取得します
        
        Returns:
            Dict[str, Any]: プロパティ辞書
        """
        return self.properties.copy()
    
    def set_property_changed_callback(self, callback: Callable[[str, Any], None]) -> None:
        """プロパティ変更コールバックを設定します
        
        Args:
            callback: プロパティ変更時に呼び出されるコールバック関数
        """
        self.property_changed_callback = callback


class ThemeEditor:
    """統合テーマエディタークラス
    
    カラーピッカー、フォント選択、プロパティエディターを統合し、
    直感的なビジュアルインターフェースでテーマプロパティを編集します。
    """
    
    def __init__(self, qt_adapter: QtAdapter, theme_adapter: ThemeAdapter):
        """テーマエディターを初期化します
        
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
        self.color_picker: Optional[ColorPicker] = None
        self.font_selector: Optional[FontSelector] = None
        self.property_editor: Optional[PropertyEditor] = None
        
        # 現在のテーマデータ
        self.current_theme: Dict[str, Any] = {
            'name': '新しいテーマ',
            'version': '1.0.0',
            'colors': {},
            'fonts': {},
            'properties': {}
        }
        
        # リアルタイムプレビュー連携
        self.preview_update_timer: Optional[Any] = None
        self.preview_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        # コールバック
        self.theme_changed_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        
        self.logger.info("テーマエディターを初期化しました", LogCategory.UI)
    
    def create_widget(self) -> Any:
        """テーマエディターウィジェットを作成します
        
        Returns:
            QWidget: テーマエディターウィジェット
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
        
        # カラーピッカーを作成
        self.color_picker = ColorPicker(self.qt_modules, self.widget)
        color_widget = self.color_picker.create_widget()
        self.color_picker.set_color_changed_callback(self._on_color_changed)
        content_layout.addWidget(color_widget)
        
        # フォントセレクターを作成
        self.font_selector = FontSelector(self.qt_modules, self.widget)
        font_widget = self.font_selector.create_widget()
        self.font_selector.set_font_changed_callback(self._on_font_changed)
        content_layout.addWidget(font_widget)
        
        # プロパティエディターを作成
        self.property_editor = PropertyEditor(self.qt_modules, self.widget)
        property_widget = self.property_editor.create_widget()
        self.property_editor.set_property_changed_callback(self._on_property_changed)
        content_layout.addWidget(property_widget)
        
        # ストレッチを追加
        content_layout.addStretch()
        
        # スクロールエリアにコンテンツを設定
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # リアルタイムプレビュー更新タイマーを設定
        self._setup_preview_update_timer()
        
        self.logger.info("テーマエディターウィジェットを作成しました", LogCategory.UI)
        return self.widget
    
    def _on_color_changed(self, color: str) -> None:
        """色変更を処理します
        
        Args:
            color: 変更された色（16進値）
        """
        # 現在選択されている色プロパティを更新
        # 実際の実装では、どの色プロパティが選択されているかを管理する必要があります
        self.current_theme['colors']['primary'] = color
        self._notify_theme_changed()
        
        self.logger.debug(f"色が変更されました: {color}", LogCategory.UI)
    
    def _on_font_changed(self, font_data: Dict[str, Any]) -> None:
        """フォント変更を処理します
        
        Args:
            font_data: 変更されたフォントデータ
        """
        self.current_theme['fonts']['default'] = font_data
        self._notify_theme_changed()
        
        self.logger.debug(f"フォントが変更されました: {font_data}", LogCategory.UI)
    
    def _on_property_changed(self, property_name: str, value: Any) -> None:
        """プロパティ変更を処理します
        
        Args:
            property_name: プロパティ名
            value: 新しい値
        """
        # プロパティをテーマデータに反映
        if property_name.startswith('基本設定.'):
            prop_key = property_name.replace('基本設定.', '').lower().replace(' ', '_')
            if prop_key == 'テーマ名':
                self.current_theme['name'] = value
            elif prop_key == 'バージョン':
                self.current_theme['version'] = value
        elif property_name.startswith('色設定.'):
            color_key = property_name.replace('色設定.', '').lower().replace(' ', '_')
            self.current_theme['colors'][color_key] = value
        else:
            self.current_theme['properties'][property_name] = value
        
        self._notify_theme_changed()
        
        self.logger.debug(f"プロパティが変更されました: {property_name} = {value}", LogCategory.UI)
    
    def _notify_theme_changed(self) -> None:
        """テーマ変更をコールバックに通知します"""
        if self.theme_changed_callback:
            self.theme_changed_callback(self.current_theme.copy())
    
    def load_theme(self, theme_data: Dict[str, Any]) -> None:
        """テーマデータを読み込みます
        
        Args:
            theme_data: 読み込むテーマデータ
        """
        self.current_theme = theme_data.copy()
        
        # UIコンポーネントを更新
        if self.color_picker and 'colors' in theme_data:
            colors = theme_data['colors']
            if 'primary' in colors:
                color = self.QtGui.QColor(colors['primary'])
                self.color_picker.set_color(color)
        
        if self.font_selector and 'fonts' in theme_data:
            fonts = theme_data['fonts']
            if 'default' in fonts:
                self.font_selector.set_font(fonts['default'])
        
        if self.property_editor:
            # プロパティを設定
            properties = {}
            
            # 基本設定
            properties['基本設定.テーマ名'] = theme_data.get('name', '')
            properties['基本設定.バージョン'] = theme_data.get('version', '1.0.0')
            
            # 色設定
            if 'colors' in theme_data:
                for color_name, color_value in theme_data['colors'].items():
                    properties[f'色設定.{color_name}'] = color_value
            
            # その他のプロパティ
            if 'properties' in theme_data:
                properties.update(theme_data['properties'])
            
            self.property_editor.set_properties(properties)
        
        self.logger.info(f"テーマを読み込みました: {theme_data.get('name', '無名')}", LogCategory.UI)
    
    def get_theme_data(self) -> Dict[str, Any]:
        """現在のテーマデータを取得します
        
        Returns:
            Dict[str, Any]: テーマデータ
        """
        return self.current_theme.copy()
    
    def set_theme_changed_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """テーマ変更コールバックを設定します
        
        Args:
            callback: テーマ変更時に呼び出されるコールバック関数
        """
        self.theme_changed_callback = callback
    
    def reset_theme(self) -> None:
        """テーマをデフォルト状態にリセットします"""
        self.current_theme = {
            'name': '新しいテーマ',
            'version': '1.0.0',
            'colors': {
                'background': '#ffffff',
                'text': '#000000',
                'primary': '#0078d4',
                'secondary': '#6c757d'
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
        
        # UIを更新
        self.load_theme(self.current_theme)
        
        self.logger.info("テーマをリセットしました", LogCategory.UI)
    
    def _setup_preview_update_timer(self) -> None:
        """プレビュー更新タイマーを設定します"""
        self.preview_update_timer = self.QtCore.QTimer()
        self.preview_update_timer.setSingleShot(True)
        self.preview_update_timer.timeout.connect(self._update_preview_callbacks)
        
        self.logger.debug("プレビュー更新タイマーを設定しました", LogCategory.UI)
    
    def _notify_theme_changed(self) -> None:
        """テーマ変更をコールバックに通知します"""
        if self.theme_changed_callback:
            self.theme_changed_callback(self.current_theme.copy())
        
        # リアルタイムプレビュー更新をスケジュール
        self._schedule_preview_update()
    
    def _schedule_preview_update(self) -> None:
        """プレビュー更新をスケジュールします（デバウンス処理）"""
        if self.preview_update_timer and self.preview_callbacks:
            self.preview_update_timer.stop()
            self.preview_update_timer.start(100)  # 100msのデバウンス
            
            self.logger.debug("プレビュー更新をスケジュールしました", LogCategory.UI)
    
    def _update_preview_callbacks(self) -> None:
        """プレビューコールバックを更新します"""
        if not self.preview_callbacks:
            return
        
        start_time = self.QtCore.QTime.currentTime()
        
        try:
            theme_copy = self.current_theme.copy()
            
            # すべてのプレビューコールバックを呼び出し
            for callback in self.preview_callbacks:
                try:
                    callback(theme_copy)
                except Exception as e:
                    self.logger.error(f"プレビューコールバックでエラーが発生しました: {str(e)}", LogCategory.UI)
            
            # 処理時間を計算
            end_time = self.QtCore.QTime.currentTime()
            elapsed_ms = start_time.msecsTo(end_time)
            
            self.logger.debug(f"プレビューを更新しました（処理時間: {elapsed_ms}ms）", LogCategory.UI)
            
            # 500ms以内の更新保証をチェック
            if elapsed_ms > 500:
                self.logger.warning(f"プレビュー更新が500msを超えました: {elapsed_ms}ms", LogCategory.UI)
                
        except Exception as e:
            self.logger.error(f"プレビュー更新中にエラーが発生しました: {str(e)}", LogCategory.UI)
    
    def add_preview_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """プレビューコールバックを追加します
        
        Args:
            callback: プレビュー更新時に呼び出されるコールバック関数
        """
        if callback not in self.preview_callbacks:
            self.preview_callbacks.append(callback)
            self.logger.debug("プレビューコールバックを追加しました", LogCategory.UI)
    
    def remove_preview_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """プレビューコールバックを削除します
        
        Args:
            callback: 削除するコールバック関数
        """
        if callback in self.preview_callbacks:
            self.preview_callbacks.remove(callback)
            self.logger.debug("プレビューコールバックを削除しました", LogCategory.UI)
    
    def connect_to_preview_window(self, preview_window) -> None:
        """プレビューウィンドウと連携します
        
        Args:
            preview_window: PreviewWindowインスタンス
        """
        if hasattr(preview_window, 'update_preview'):
            self.add_preview_callback(preview_window.update_preview)
            self.logger.info("プレビューウィンドウと連携しました", LogCategory.UI)
        else:
            self.logger.warning("プレビューウィンドウにupdate_previewメソッドがありません", LogCategory.UI)
    
    def disconnect_from_preview_window(self, preview_window) -> None:
        """プレビューウィンドウとの連携を解除します
        
        Args:
            preview_window: PreviewWindowインスタンス
        """
        if hasattr(preview_window, 'update_preview'):
            self.remove_preview_callback(preview_window.update_preview)
            self.logger.info("プレビューウィンドウとの連携を解除しました", LogCategory.UI)
    
    def save_theme(self, file_path: str = None) -> bool:
        """テーマをqt-theme-manager形式で保存します
        
        Args:
            file_path: 保存先のファイルパス（Noneの場合はダイアログを表示）
            
        Returns:
            bool: 保存が成功した場合True
        """
        try:
            # ファイルパスが指定されていない場合はダイアログを表示
            if not file_path:
                file_path, _ = self.QtWidgets.QFileDialog.getSaveFileName(
                    self.widget,
                    "テーマを保存",
                    f"{self.current_theme.get('name', '新しいテーマ')}.json",
                    "JSONファイル (*.json);;すべてのファイル (*)"
                )
                
                if not file_path:
                    return False  # ユーザーがキャンセルした場合
            
            # テーマデータを検証
            validation_result = self.theme_adapter.validate_theme(self.current_theme)
            if not validation_result['is_valid']:
                error_messages = "\\n".join(validation_result['errors'])
                self.QtWidgets.QMessageBox.warning(
                    self.widget,
                    "テーマ検証エラー",
                    f"テーマデータに問題があります:\\n{error_messages}"
                )
                return False
            
            # テーマを保存
            success = self.theme_adapter.save_theme(self.current_theme, file_path)
            
            if success:
                # 保存成功時の日本語メッセージ表示
                self._show_save_success_message(file_path)
                self.logger.info(f"テーマを保存しました: {file_path}", LogCategory.UI)
                return True
            else:
                self._show_save_error_message("テーマの保存に失敗しました")
                return False
                
        except Exception as e:
            error_message = f"テーマ保存中にエラーが発生しました: {str(e)}"
            self.logger.error(error_message, LogCategory.UI)
            self._show_save_error_message(error_message)
            return False
    
    def save_theme_as(self) -> bool:
        """テーマに名前を付けて保存します
        
        Returns:
            bool: 保存が成功した場合True
        """
        return self.save_theme()  # ファイルパスを指定しないことで、常にダイアログを表示
    
    def _show_save_success_message(self, file_path: str) -> None:
        """保存成功時の日本語メッセージを表示します
        
        Args:
            file_path: 保存されたファイルのパス
        """
        import os
        file_name = os.path.basename(file_path)
        
        # 成功メッセージダイアログを表示
        msg_box = self.QtWidgets.QMessageBox(self.widget)
        msg_box.setWindowTitle("保存完了")
        msg_box.setIcon(self.QtWidgets.QMessageBox.Icon.Information)
        msg_box.setText(f"テーマ '{self.current_theme.get('name', '無名')}' を正常に保存しました。")
        msg_box.setDetailedText(f"保存場所: {file_path}")
        msg_box.setInformativeText(f"ファイル名: {file_name}")
        
        # ボタンを日本語に設定
        msg_box.setStandardButtons(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button = msg_box.button(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button.setText("OK")
        
        msg_box.exec()
        
        self.logger.info(f"保存成功メッセージを表示しました: {file_name}", LogCategory.UI)
    
    def _show_save_error_message(self, error_message: str) -> None:
        """保存エラー時の日本語メッセージを表示します
        
        Args:
            error_message: エラーメッセージ
        """
        # エラーメッセージダイアログを表示
        msg_box = self.QtWidgets.QMessageBox(self.widget)
        msg_box.setWindowTitle("保存エラー")
        msg_box.setIcon(self.QtWidgets.QMessageBox.Icon.Critical)
        msg_box.setText("テーマの保存に失敗しました。")
        msg_box.setDetailedText(error_message)
        msg_box.setInformativeText("ファイルパスやアクセス権限を確認してください。")
        
        # ボタンを日本語に設定
        msg_box.setStandardButtons(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button = msg_box.button(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button.setText("OK")
        
        msg_box.exec()
        
        self.logger.error(f"保存エラーメッセージを表示しました: {error_message}", LogCategory.UI)
    
    def export_theme(self, format: str = 'json', file_path: str = None) -> bool:
        """テーマを指定された形式でエクスポートします
        
        Args:
            format: エクスポート形式 ('json', 'qss', 'css')
            file_path: 保存先のファイルパス（Noneの場合はダイアログを表示）
            
        Returns:
            bool: エクスポートが成功した場合True
        """
        try:
            format = format.lower()
            
            # ファイル拡張子とフィルターを設定
            extensions = {
                'json': ('json', 'JSONファイル (*.json)'),
                'qss': ('qss', 'QSSファイル (*.qss)'),
                'css': ('css', 'CSSファイル (*.css)')
            }
            
            if format not in extensions:
                raise ValueError(f"サポートされていないエクスポート形式: {format}")
            
            ext, file_filter = extensions[format]
            
            # ファイルパスが指定されていない場合はダイアログを表示
            if not file_path:
                default_name = f"{self.current_theme.get('name', '新しいテーマ')}.{ext}"
                file_path, _ = self.QtWidgets.QFileDialog.getSaveFileName(
                    self.widget,
                    f"テーマを{format.upper()}形式でエクスポート",
                    default_name,
                    f"{file_filter};;すべてのファイル (*)"
                )
                
                if not file_path:
                    return False  # ユーザーがキャンセルした場合
            
            # テーマをエクスポート
            exported_content = self.theme_adapter.export_theme(self.current_theme, format)
            
            # ファイルに書き込み
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(exported_content)
            
            # エクスポート成功時のメッセージ表示
            self._show_export_success_message(file_path, format)
            self.logger.info(f"テーマを{format.upper()}形式でエクスポートしました: {file_path}", LogCategory.UI)
            return True
            
        except Exception as e:
            error_message = f"テーマエクスポート中にエラーが発生しました: {str(e)}"
            self.logger.error(error_message, LogCategory.UI)
            self._show_save_error_message(error_message)
            return False
    
    def _show_export_success_message(self, file_path: str, format: str) -> None:
        """エクスポート成功時の日本語メッセージを表示します
        
        Args:
            file_path: エクスポートされたファイルのパス
            format: エクスポート形式
        """
        import os
        file_name = os.path.basename(file_path)
        
        # 成功メッセージダイアログを表示
        msg_box = self.QtWidgets.QMessageBox(self.widget)
        msg_box.setWindowTitle("エクスポート完了")
        msg_box.setIcon(self.QtWidgets.QMessageBox.Icon.Information)
        msg_box.setText(f"テーマを{format.upper()}形式で正常にエクスポートしました。")
        msg_box.setDetailedText(f"保存場所: {file_path}")
        msg_box.setInformativeText(f"ファイル名: {file_name}")
        
        # ボタンを日本語に設定
        msg_box.setStandardButtons(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button = msg_box.button(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button.setText("OK")
        
        msg_box.exec()
        
        self.logger.info(f"エクスポート成功メッセージを表示しました: {file_name}", LogCategory.UI)
    
    def load_theme_from_file(self, file_path: str = None) -> bool:
        """ファイルからテーマを読み込みます
        
        Args:
            file_path: 読み込むファイルのパス（Noneの場合はダイアログを表示）
            
        Returns:
            bool: 読み込みが成功した場合True
        """
        try:
            # ファイルパスが指定されていない場合はダイアログを表示
            if not file_path:
                file_path, _ = self.QtWidgets.QFileDialog.getOpenFileName(
                    self.widget,
                    "テーマファイルを開く",
                    "",
                    "テーマファイル (*.json *.qss *.css);;JSONファイル (*.json);;QSSファイル (*.qss);;CSSファイル (*.css);;すべてのファイル (*)"
                )
                
                if not file_path:
                    return False  # ユーザーがキャンセルした場合
            
            # テーマファイルを読み込み
            theme_data = self.theme_adapter.load_theme(file_path)
            
            # テーマを適用
            self.load_theme(theme_data)
            
            # 読み込み成功時のメッセージ表示
            self._show_load_success_message(file_path)
            self.logger.info(f"テーマファイルを読み込みました: {file_path}", LogCategory.UI)
            return True
            
        except Exception as e:
            error_message = f"テーマファイル読み込み中にエラーが発生しました: {str(e)}"
            self.logger.error(error_message, LogCategory.UI)
            self._show_load_error_message(error_message)
            return False
    
    def _show_load_success_message(self, file_path: str) -> None:
        """読み込み成功時の日本語メッセージを表示します
        
        Args:
            file_path: 読み込まれたファイルのパス
        """
        import os
        file_name = os.path.basename(file_path)
        
        # 成功メッセージダイアログを表示
        msg_box = self.QtWidgets.QMessageBox(self.widget)
        msg_box.setWindowTitle("読み込み完了")
        msg_box.setIcon(self.QtWidgets.QMessageBox.Icon.Information)
        msg_box.setText(f"テーマ '{self.current_theme.get('name', '無名')}' を正常に読み込みました。")
        msg_box.setDetailedText(f"読み込み元: {file_path}")
        msg_box.setInformativeText(f"ファイル名: {file_name}")
        
        # ボタンを日本語に設定
        msg_box.setStandardButtons(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button = msg_box.button(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button.setText("OK")
        
        msg_box.exec()
        
        self.logger.info(f"読み込み成功メッセージを表示しました: {file_name}", LogCategory.UI)
    
    def _show_load_error_message(self, error_message: str) -> None:
        """読み込みエラー時の日本語メッセージを表示します
        
        Args:
            error_message: エラーメッセージ
        """
        # エラーメッセージダイアログを表示
        msg_box = self.QtWidgets.QMessageBox(self.widget)
        msg_box.setWindowTitle("読み込みエラー")
        msg_box.setIcon(self.QtWidgets.QMessageBox.Icon.Critical)
        msg_box.setText("テーマファイルの読み込みに失敗しました。")
        msg_box.setDetailedText(error_message)
        msg_box.setInformativeText("ファイル形式やファイルの内容を確認してください。")
        
        # ボタンを日本語に設定
        msg_box.setStandardButtons(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button = msg_box.button(self.QtWidgets.QMessageBox.StandardButton.Ok)
        ok_button.setText("OK")
        
        msg_box.exec()
        
        self.logger.error(f"読み込みエラーメッセージを表示しました: {error_message}", LogCategory.UI)
    
    def get_widget(self) -> Optional[Any]:
        """テーマエディターウィジェットを取得します
        
        Returns:
            Optional[QWidget]: テーマエディターウィジェット
        """
        return self.widget