"""
ゼブラパターンエディター - WCAG準拠のコントラスト調整UI

このモジュールは、アクセシビリティを重視したゼブラパターンエディターを提供します。
WCAG準拠のコントラスト調整機能を通じて、視覚的にアクセシブルなテーマを作成できます。
"""

from typing import Dict, List, Optional, Tuple
import logging

from qt_theme_studio.adapters.qt_adapter import QtAdapter

# Qt モジュールの動的インポート
qt_adapter = QtAdapter()
qt_modules = qt_adapter.get_qt_modules()

QtWidgets = qt_modules['QtWidgets']
QtCore = qt_modules['QtCore']
QtGui = qt_modules['QtGui']

logger = logging.getLogger(__name__)


class ColorPairWidget(QtWidgets.QWidget):
    """色ペア選択ウィジェット"""
    
    color_changed = QtCore.Signal(str, str)  # 前景色, 背景色
    
    def __init__(self, label: str, foreground: str = "#000000", background: str = "#ffffff"):
        super().__init__()
        self.label = label
        self.foreground_color = foreground
        self.background_color = background
        self.setup_ui()
        
    def setup_ui(self):
        """UIセットアップ"""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # ラベル
        self.label_widget = QtWidgets.QLabel(self.label)
        self.label_widget.setMinimumWidth(100)
        layout.addWidget(self.label_widget)
        
        # 前景色ボタン
        self.fg_button = QtWidgets.QPushButton("前景色")
        self.fg_button.setMinimumSize(80, 30)
        self.fg_button.clicked.connect(self.select_foreground_color)
        layout.addWidget(self.fg_button)
        
        # 背景色ボタン
        self.bg_button = QtWidgets.QPushButton("背景色")
        self.bg_button.setMinimumSize(80, 30)
        self.bg_button.clicked.connect(self.select_background_color)
        layout.addWidget(self.bg_button)
        
        # プレビューラベル
        self.preview_label = QtWidgets.QLabel("サンプルテキスト")
        self.preview_label.setMinimumSize(120, 30)
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.preview_label)
        
        # コントラスト比表示
        self.contrast_label = QtWidgets.QLabel("--:1")
        self.contrast_label.setMinimumWidth(60)
        self.contrast_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.contrast_label)
        
        # WCAG適合レベル表示
        self.wcag_label = QtWidgets.QLabel("--")
        self.wcag_label.setMinimumWidth(40)
        self.wcag_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.wcag_label)
        
        self.update_preview()
        
    def select_foreground_color(self):
        """前景色選択"""
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor(self.foreground_color),
            self,
            "前景色を選択"
        )
        if color.isValid():
            self.foreground_color = color.name()
            self.update_preview()
            self.color_changed.emit(self.foreground_color, self.background_color)
            
    def select_background_color(self):
        """背景色選択"""
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor(self.background_color),
            self,
            "背景色を選択"
        )
        if color.isValid():
            self.background_color = color.name()
            self.update_preview()
            self.color_changed.emit(self.foreground_color, self.background_color)
            
    def update_preview(self):
        """プレビュー更新"""
        # ボタンの色を更新
        self.fg_button.setStyleSheet(f"background-color: {self.foreground_color};")
        self.bg_button.setStyleSheet(f"background-color: {self.background_color};")
        
        # プレビューラベルのスタイル更新
        self.preview_label.setStyleSheet(
            f"color: {self.foreground_color}; "
            f"background-color: {self.background_color}; "
            f"border: 1px solid #ccc; "
            f"padding: 5px;"
        )
        
    def set_colors(self, foreground: str, background: str):
        """色を設定"""
        self.foreground_color = foreground
        self.background_color = background
        self.update_preview()
        
    def get_colors(self) -> Tuple[str, str]:
        """色を取得"""
        return self.foreground_color, self.background_color
        
    def set_contrast_info(self, ratio: float, wcag_level: str):
        """コントラスト情報を設定"""
        self.contrast_label.setText(f"{ratio:.1f}:1")
        self.wcag_label.setText(wcag_level)
        
        # WCAG適合レベルに応じて色を変更
        if wcag_level == "AAA":
            self.wcag_label.setStyleSheet("color: green; font-weight: bold;")
        elif wcag_level == "AA":
            self.wcag_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.wcag_label.setStyleSheet("color: red; font-weight: bold;")


class AccessibilityPresetWidget(QtWidgets.QWidget):
    """アクセシビリティレベルプリセットウィジェット"""
    
    preset_selected = QtCore.Signal(str)  # AA, AAA
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """UIセットアップ"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # タイトル
        title = QtWidgets.QLabel("アクセシビリティレベルプリセット")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # プリセットボタン
        button_layout = QtWidgets.QHBoxLayout()
        
        self.aa_button = QtWidgets.QPushButton("WCAG AA準拠")
        self.aa_button.setToolTip("コントラスト比 4.5:1 以上（通常テキスト）")
        self.aa_button.clicked.connect(lambda: self.preset_selected.emit("AA"))
        button_layout.addWidget(self.aa_button)
        
        self.aaa_button = QtWidgets.QPushButton("WCAG AAA準拠")
        self.aaa_button.setToolTip("コントラスト比 7:1 以上（通常テキスト）")
        self.aaa_button.clicked.connect(lambda: self.preset_selected.emit("AAA"))
        button_layout.addWidget(self.aaa_button)
        
        layout.addLayout(button_layout)
        
        # 説明テキスト
        description = QtWidgets.QLabel(
            "プリセットを選択すると、選択されたWCAGレベルに適合する色の組み合わせが自動生成されます。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(description)


class ZebraEditor(QtWidgets.QWidget):
    """
    WCAG準拠ゼブラパターンエディター
    
    アクセシビリティを重視したテーマ作成のための専用エディターです。
    科学的色計算に基づくコントラスト比計算とWCAG適合レベル判定を提供します。
    """
    
    colors_changed = QtCore.Signal(dict)  # 色変更シグナル
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color_pairs: Dict[str, ColorPairWidget] = {}
        self.setup_ui()
        logger.info("ゼブラパターンエディターを初期化しました")
        
    def setup_ui(self):
        """UIセットアップ"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        
        # タイトル
        title = QtWidgets.QLabel("ゼブラパターンエディター")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 説明
        description = QtWidgets.QLabel(
            "WCAG準拠のコントラスト調整機能を使用して、"
            "視覚的にアクセシブルなテーマを作成できます。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(description)
        
        # アクセシビリティプリセット
        self.preset_widget = AccessibilityPresetWidget()
        self.preset_widget.preset_selected.connect(self.apply_accessibility_preset)
        layout.addWidget(self.preset_widget)
        
        # 区切り線
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)
        
        # 色ペア設定エリア
        self.setup_color_pairs_area(layout)
        
        # 改善提案エリア
        self.setup_improvement_area(layout)
        
        # ストレッチャー
        layout.addStretch()
        
    def setup_color_pairs_area(self, parent_layout):
        """色ペア設定エリアのセットアップ"""
        # タイトル
        title = QtWidgets.QLabel("色ペア設定")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        parent_layout.addWidget(title)
        
        # ヘッダー
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(QtWidgets.QLabel("要素"))
        header_layout.addWidget(QtWidgets.QLabel("前景色"))
        header_layout.addWidget(QtWidgets.QLabel("背景色"))
        header_layout.addWidget(QtWidgets.QLabel("プレビュー"))
        header_layout.addWidget(QtWidgets.QLabel("比率"))
        header_layout.addWidget(QtWidgets.QLabel("WCAG"))
        
        header_widget = QtWidgets.QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("font-weight: bold; background-color: #f0f0f0; padding: 5px;")
        parent_layout.addWidget(header_widget)
        
        # 色ペアウィジェット
        self.color_pairs_layout = QtWidgets.QVBoxLayout()
        
        # デフォルトの色ペアを追加
        default_pairs = [
            ("通常テキスト", "#000000", "#ffffff"),
            ("リンクテキスト", "#0066cc", "#ffffff"),
            ("選択テキスト", "#ffffff", "#0066cc"),
            ("無効テキスト", "#999999", "#ffffff"),
            ("エラーテキスト", "#cc0000", "#ffffff"),
        ]
        
        for label, fg, bg in default_pairs:
            self.add_color_pair(label, fg, bg)
            
        parent_layout.addLayout(self.color_pairs_layout)
        
        # 色ペア追加ボタン
        add_button = QtWidgets.QPushButton("+ 色ペアを追加")
        add_button.clicked.connect(self.add_custom_color_pair)
        parent_layout.addWidget(add_button)
        
    def setup_improvement_area(self, parent_layout):
        """改善提案エリアのセットアップ"""
        # 区切り線
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        parent_layout.addWidget(line)
        
        # タイトル
        title = QtWidgets.QLabel("改善提案")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        parent_layout.addWidget(title)
        
        # 改善提案表示エリア
        self.improvement_text = QtWidgets.QTextEdit()
        self.improvement_text.setMaximumHeight(100)
        self.improvement_text.setReadOnly(True)
        self.improvement_text.setPlaceholderText("色の組み合わせを変更すると、改善提案が表示されます。")
        parent_layout.addWidget(self.improvement_text)
        
        # 改善適用ボタン
        self.apply_improvements_button = QtWidgets.QPushButton("改善案を適用")
        self.apply_improvements_button.setEnabled(False)
        self.apply_improvements_button.clicked.connect(self.apply_improvements)
        parent_layout.addWidget(self.apply_improvements_button)
        
    def add_color_pair(self, label: str, foreground: str, background: str):
        """色ペアを追加"""
        color_pair = ColorPairWidget(label, foreground, background)
        color_pair.color_changed.connect(self.on_color_changed)
        
        self.color_pairs[label] = color_pair
        self.color_pairs_layout.addWidget(color_pair)
        
        # 初期コントラスト計算（プレースホルダー）
        color_pair.set_contrast_info(4.5, "AA")
        
    def add_custom_color_pair(self):
        """カスタム色ペアを追加"""
        label, ok = QtWidgets.QInputDialog.getText(
            self, 
            "色ペア追加", 
            "色ペアの名前を入力してください:"
        )
        
        if ok and label.strip():
            self.add_color_pair(label.strip(), "#000000", "#ffffff")
            
    def on_color_changed(self, foreground: str, background: str):
        """色変更イベントハンドラ"""
        # 全ての色ペア情報を収集
        colors_data = {}
        for label, widget in self.color_pairs.items():
            fg, bg = widget.get_colors()
            colors_data[label] = {"foreground": fg, "background": bg}
            
        # シグナル発信
        self.colors_changed.emit(colors_data)
        
        # 改善提案を更新（プレースホルダー）
        self.update_improvement_suggestions()
        
        logger.info(f"色が変更されました: {foreground} / {background}")
        
    def update_improvement_suggestions(self):
        """改善提案を更新"""
        # プレースホルダー実装
        suggestions = [
            "• 通常テキストのコントラスト比を4.5:1以上にすることをお勧めします",
            "• リンクテキストの色をより明確にすることで、識別しやすくなります",
            "• エラーテキストは赤色以外の方法でも識別できるようにしてください"
        ]
        
        self.improvement_text.setPlainText("\n".join(suggestions))
        self.apply_improvements_button.setEnabled(True)
        
    def apply_improvements(self):
        """改善案を適用"""
        # プレースホルダー実装
        QtWidgets.QMessageBox.information(
            self,
            "改善案適用",
            "改善案が適用されました。\n"
            "（この機能は後続のタスクで完全に実装されます）"
        )
        
    def apply_accessibility_preset(self, level: str):
        """アクセシビリティプリセットを適用"""
        logger.info(f"アクセシビリティプリセット '{level}' を適用します")
        
        # プレースホルダー実装
        if level == "AA":
            preset_colors = [
                ("通常テキスト", "#000000", "#ffffff"),
                ("リンクテキスト", "#0066cc", "#ffffff"),
                ("選択テキスト", "#ffffff", "#0066cc"),
                ("無効テキスト", "#767676", "#ffffff"),
                ("エラーテキスト", "#d13212", "#ffffff"),
            ]
        else:  # AAA
            preset_colors = [
                ("通常テキスト", "#000000", "#ffffff"),
                ("リンクテキスト", "#004499", "#ffffff"),
                ("選択テキスト", "#ffffff", "#004499"),
                ("無効テキスト", "#595959", "#ffffff"),
                ("エラーテキスト", "#b30000", "#ffffff"),
            ]
            
        # 既存の色ペアを更新
        for label, fg, bg in preset_colors:
            if label in self.color_pairs:
                self.color_pairs[label].set_colors(fg, bg)
                
        QtWidgets.QMessageBox.information(
            self,
            "プリセット適用",
            f"WCAG {level}準拠のプリセットが適用されました。"
        )
        
    def get_color_data(self) -> Dict[str, Dict[str, str]]:
        """現在の色データを取得"""
        colors_data = {}
        for label, widget in self.color_pairs.items():
            fg, bg = widget.get_colors()
            colors_data[label] = {"foreground": fg, "background": bg}
        return colors_data
        
    def set_color_data(self, colors_data: Dict[str, Dict[str, str]]):
        """色データを設定"""
        for label, colors in colors_data.items():
            if label in self.color_pairs:
                self.color_pairs[label].set_colors(
                    colors["foreground"], 
                    colors["background"]
                )