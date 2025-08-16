"""
ゼブラパターンエディター - WCAG準拠のコントラスト調整UI

このモジュールは、アクセシビリティを重視したゼブラパターンエディターを提供します。
WCAG準拠のコントラスト調整機能を通じて、視覚的にアクセシブルなテーマを作成できます。
"""

from typing import Any, Dict, Tuple

from qt_theme_studio.adapters.qt_adapter import QtAdapter

# Qt モジュールの動的インポート
qt_adapter = QtAdapter()
qt_modules = qt_adapter.get_qt_modules()

QtWidgets = qt_modules["QtWidgets"]
QtCore = qt_modules["QtCore"]
QtGui = qt_modules["QtGui"]

logger = logging.getLogger(__name__)


class ColorUtils:
    """色計算とアクセシビリティのためのユーティリティクラス"""

    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """16進色をRGBタプルに変換"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """RGBを16進色に変換"""
        return "#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def get_luminance(hex_color: str) -> float:
        """WCAGガイドラインに従って相対輝度を計算"""
        r, g, b = ColorUtils.hex_to_rgb(hex_color)
        # 0-1の範囲に変換
        r, g, b = r / 255.0, g / 255.0, b / 255.0

        # ガンマ補正を適用
        def gamma_correct(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = map(gamma_correct, [r, g, b])

        # 輝度を計算
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    @staticmethod
    def get_contrast_ratio(color1: str, color2: str) -> float:
        """2つの色のコントラスト比を計算"""
        l1 = ColorUtils.get_luminance(color1)
        l2 = ColorUtils.get_luminance(color2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def is_accessible(bg_color: str, text_color: str, level: str = "AA") -> bool:
        """色の組み合わせがWCAGアクセシビリティ基準を満たすかチェック"""
        contrast = ColorUtils.get_contrast_ratio(bg_color, text_color)
        if level == "AAA":
            return contrast >= 7.0  # AAA基準
        else:
            return contrast >= 4.5  # AA基準

    @staticmethod
    def get_optimal_text_color(bg_color: str) -> str:
        """指定された背景色に対して最適なテキスト色（黒または白）を取得"""
        luminance = ColorUtils.get_luminance(bg_color)
        return "#000000" if luminance > 0.5 else "#fffff"

    @staticmethod
    def adjust_brightness(hex_color: str, factor: float) -> str:
        """色の明度を調整（-1.0から1.0）"""
        import colorsys

        r, g, b = ColorUtils.hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

        # 明度を調整
        v = max(0, min(1, v + factor))
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return ColorUtils.rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))


class ColorSliderGroup(QtWidgets.QWidget):
    """色調整用のスライダーグループ"""

    colorChanged = QtCore.Signal(str)

    def __init__(self, title: str, initial_color: str = "#fffff", parent=None):
        super().__init__(parent)
        self.title = title
        self.color = initial_color
        self.setup_ui()
        self.update_from_hex(initial_color)

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # タイトルと色プレビュー
        header_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel(self.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # 色プレビューボタン
        self.color_preview = QtWidgets.QPushButton()
        self.color_preview.setFixedSize(60, 25)
        self.color_preview.clicked.connect(self.choose_color)
        header_layout.addWidget(self.color_preview)

        layout.addLayout(header_layout)

        # RGBスライダー
        slider_layout = QtWidgets.QGridLayout()
        self.sliders = {}
        self.spinboxes = {}

        for i, (name, color) in enumerate(
            [("R", "red"), ("G", "green"), ("B", "blue")]
        ):
            label = QtWidgets.QLabel(name)
            label.setFixedWidth(15)

            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            slider.setRange(0, 255)
            slider.valueChanged.connect(self.update_color)

            spinbox = QtWidgets.QSpinBox()
            spinbox.setRange(0, 255)
            spinbox.setFixedWidth(60)
            spinbox.valueChanged.connect(self.update_color)

            # スライダーとスピンボックスを連携
            slider.valueChanged.connect(spinbox.setValue)
            spinbox.valueChanged.connect(slider.setValue)

            slider_layout.addWidget(label, i, 0)
            slider_layout.addWidget(slider, i, 1)
            slider_layout.addWidget(spinbox, i, 2)

            self.sliders[name.lower()] = slider
            self.spinboxes[name.lower()] = spinbox

        layout.addLayout(slider_layout)

        # 16進入力
        hex_layout = QtWidgets.QHBoxLayout()
        hex_layout.addWidget(QtWidgets.QLabel("Hex:"))
        self.hex_input = QtWidgets.QLineEdit()
        self.hex_input.setMaxLength(7)
        self.hex_input.textChanged.connect(self.update_from_hex_input)
        hex_layout.addWidget(self.hex_input)

        layout.addLayout(hex_layout)

    def choose_color(self):
        """カラーダイアログを開く"""
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.color))
        if color.isValid():
            self.update_from_hex(color.name())

    def update_color(self):
        """スライダー値から色を更新"""
        r = self.sliders["r"].value()
        g = self.sliders["g"].value()
        b = self.sliders["b"].value()

        self.color = ColorUtils.rgb_to_hex(r, g, b)
        self.update_preview()
        self.hex_input.setText(self.color)
        self.colorChanged.emit(self.color)

    def update_from_hex(self, hex_color: str):
        """16進色からスライダーを更新"""
        if not hex_color.startswith("#") or len(hex_color) != 7:
            return

        try:
            r, g, b = ColorUtils.hex_to_rgb(hex_color)

            # シグナルをブロックして無限ループを防ぐ
            for slider in self.sliders.values():
                slider.blockSignals(True)
            for spinbox in self.spinboxes.values():
                spinbox.blockSignals(True)

            self.sliders["r"].setValue(r)
            self.sliders["g"].setValue(g)
            self.sliders["b"].setValue(b)

            # シグナルのブロックを解除
            for slider in self.sliders.values():
                slider.blockSignals(False)
            for spinbox in self.spinboxes.values():
                spinbox.blockSignals(False)

            self.color = hex_color
            self.hex_input.setText(hex_color)
            self.update_preview()
            self.colorChanged.emit(self.color)

        except ValueError:
            pass

    def update_from_hex_input(self, text: str):
        """16進入力フィールドから色を更新"""
        if text.startswith("#") and len(text) == 7:
            self.update_from_hex(text)

    def update_preview(self):
        """色プレビューボタンを更新"""
        ColorUtils.get_optimal_text_color(self.color)
        # ボーダー色をテーマから取得（フォールバック付き）
        border_color = getattr(self, "theme_border_color", "#ccc")

        self.color_preview.setStyleSheet(
            """
            QPushButton {{
                background-color: {self.color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 3px;
                font-weight: bold;
            }}
        """
        )
        self.color_preview.setText(self.color.upper())

    def get_color(self) -> str:
        """現在の色を16進で取得"""
        return self.color


class ContrastChecker(QtWidgets.QWidget):
    """コンパクトなコントラストチェッカーウィジェット"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # タイトル
        title = QtWidgets.QLabel("コントラストチェック")
        title.setStyleSheet("font-weight: bold; font-size: 12px; margin-bottom: 5px;")
        layout.addWidget(title)

        # コンパクトなプレビューエリア
        self.preview = QtWidgets.QLabel("サンプルテキスト")
        self.preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview.setFixedHeight(50)
        self.preview.setStyleSheet(
            """
            QLabel {
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 14px;
                font-weight: bold;
            }
        """
        )
        layout.addWidget(self.preview)

        # コンパクトなコントラスト情報
        info_layout = QtWidgets.QHBoxLayout()

        self.contrast_label = QtWidgets.QLabel("0.00:1")
        self.contrast_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        info_layout.addWidget(QtWidgets.QLabel("比率:"))
        info_layout.addWidget(self.contrast_label)

        info_layout.addWidget(QtWidgets.QLabel("|"))

        self.wcag_aa_label = QtWidgets.QLabel("❌")
        info_layout.addWidget(QtWidgets.QLabel("AA:"))
        info_layout.addWidget(self.wcag_aa_label)

        self.wcag_aaa_label = QtWidgets.QLabel("❌")
        info_layout.addWidget(QtWidgets.QLabel("AAA:"))
        info_layout.addWidget(self.wcag_aaa_label)

        info_layout.addStretch()
        layout.addLayout(info_layout)

        # 簡潔な推奨事項
        self.recommendation = QtWidgets.QLabel("")
        self.recommendation.setWordWrap(True)
        self.recommendation.setStyleSheet("font-size: 10px; margin-top: 3px;")
        layout.addWidget(self.recommendation)

    def check_contrast(self, bg_color: str, text_color: str):
        """背景色とテキスト色のコントラストをチェック（コンパクト版）"""
        contrast = ColorUtils.get_contrast_ratio(bg_color, text_color)
        aa_pass = ColorUtils.is_accessible(bg_color, text_color, "AA")
        aaa_pass = ColorUtils.is_accessible(bg_color, text_color, "AAA")

        # プレビューを更新
        self.preview.setStyleSheet(
            """
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 14px;
                font-weight: bold;
            }}
        """
        )

        # 情報を更新
        self.contrast_label.setText("{contrast:.1f}:1")
        self.wcag_aa_label.setText("✅" if aa_pass else "❌")
        self.wcag_aaa_label.setText("✅" if aaa_pass else "❌")

        # 簡潔な推奨事項
        if contrast >= 7.0:
            rec = "優秀なコントラスト"
        elif contrast >= 4.5:
            rec = "良好なコントラスト"
        elif contrast >= 3.0:
            rec = "改善が必要"
        else:
            rec = "コントラスト不足"

        self.recommendation.setText(rec)


class AutoThemeGenerator(QtWidgets.QWidget):
    """
    オートテーマジェネレーター

    WCAG準拠の色ペア自動生成機能を提供します。
    基本色を選択するだけで、アクセシブルなテーマカラーを自動生成できます。
    """

    colors_changed = QtCore.Signal(dict)  # 色変更シグナル
    theme_apply_requested = QtCore.Signal(dict)  # テーマ適用要求シグナル

    def __init__(self, qt_adapter=None, parent=None):
        super().__init__(parent)

        # Qtアダプターを保存
        self.qt_adapter = qt_adapter

        # 現在の色設定
        self.current_colors = {"background": "#fffff", "primary": "#007acc"}

        # テーマのボーダー色を初期化
        self.theme_border_color = "#ccc"

        # 生成されたテーマカラー
        self.generated_theme_colors = {}

        # コントラストチェッカー
        self.contrast_checker = ContrastChecker()

        # 更新タイマーを初期化
        self.update_timer = QtCore.QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._on_update_timeout)

        # UIを初期化
        self.setup_ui()
        self.load_default_colors()

    def set_theme_border_color(self, border_color: str):
        """テーマのボーダー色を設定します

        Args:
            border_color: ボーダー色（16進数カラーコード）
        """
        self.theme_border_color = border_color
        # プレビューを更新
        self.update_preview()

    def setup_ui(self):
        """UIセットアップ（改良版）"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)

        # タイトル
        title = QtWidgets.QLabel("オートテーマジェネレーター")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # 説明
        description = QtWidgets.QLabel(
            "基本色を選択して「自動生成」ボタンでWCAG準拠のテーマカラーを自動生成します。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin-bottom: 15px;")
        layout.addWidget(description)

        # メインスプリッター（水平分割）
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)

        # 左パネル：コントロール
        self.controls_layout = QtWidgets.QVBoxLayout()
        self.setup_controls_panel(main_splitter)

        # スプリッターの比率を設定（プレビューパネルは削除）
        # main_splitter.setSizes([400, 300])  # プレビューパネルがないので不要

    def setup_controls_panel(self, parent):
        """コントロールパネルの設定"""
        # テーマ情報セクション
        theme_info_group = QtWidgets.QGroupBox("テーマ情報")
        theme_info_layout = QtWidgets.QVBoxLayout()

        # テーマ名入力
        theme_name_layout = QtWidgets.QHBoxLayout()
        theme_name_layout.addWidget(QtWidgets.QLabel("テーマ名:"))
        self.theme_name_input = QtWidgets.QLineEdit()
        self.theme_name_input.setPlaceholderText("テーマ名を入力してください")
        self.theme_name_input.setFocusPolicy(
            QtCore.Qt.FocusPolicy.StrongFocus
        )  # フォーカス可能に設定

        theme_name_layout.addWidget(self.theme_name_input)
        theme_info_layout.addLayout(theme_name_layout)

        # テーマ概要入力
        theme_desc_layout = QtWidgets.QHBoxLayout()
        theme_desc_layout.addWidget(QtWidgets.QLabel("テーマ概要:"))
        self.theme_description_input = QtWidgets.QTextEdit()
        self.theme_description_input.setPlaceholderText(
            "テーマの概要を入力してください"
        )
        self.theme_description_input.setMaximumHeight(60)
        self.theme_description_input.setFocusPolicy(
            QtCore.Qt.FocusPolicy.StrongFocus
        )  # フォーカス可能に設定

        theme_desc_layout.addWidget(self.theme_description_input)
        theme_info_layout.addLayout(theme_desc_layout)

        theme_info_group.setLayout(theme_info_layout)

        # 色調整用スライダーグループ
        color_sliders_group = QtWidgets.QGroupBox("色調整")
        color_sliders_layout = QtWidgets.QVBoxLayout()

        # 背景色スライダー
        self.bg_slider = ColorSliderGroup("背景色", "#fffff", self)
        self.bg_slider.colorChanged.connect(
            lambda color: self.update_color("background", color)
        )
        color_sliders_layout.addWidget(self.bg_slider)

        # プライマリ色スライダー
        self.primary_slider = ColorSliderGroup("プライマリ色", "#007acc", self)
        self.primary_slider.colorChanged.connect(
            lambda color: self.update_color("primary", color)
        )
        color_sliders_layout.addWidget(self.primary_slider)

        color_sliders_group.setLayout(color_sliders_layout)

        # テーマ生成ボタン
        generate_buttons_layout = QtWidgets.QHBoxLayout()

        # WCAG AA準拠テーマ生成
        aa_button = QtWidgets.QPushButton("WCAG AA準拠テーマ生成")
        aa_button.clicked.connect(lambda: self.auto_generate_theme("AA"))
        generate_buttons_layout.addWidget(aa_button)

        # WCAG AAA準拠テーマ生成
        aaa_button = QtWidgets.QPushButton("WCAG AAA準拠テーマ生成")
        aaa_button.clicked.connect(lambda: self.auto_generate_theme("AAA"))
        generate_buttons_layout.addWidget(aaa_button)

        # 調和色テーマ生成
        harmony_button = QtWidgets.QPushButton("調和色テーマ生成")
        harmony_button.clicked.connect(self.generate_harmonious_palette)
        generate_buttons_layout.addWidget(harmony_button)

        # メインテーマに適用ボタン
        apply_button = QtWidgets.QPushButton("メインテーマに適用")
        apply_button.clicked.connect(self.apply_to_main_theme)
        apply_button.setStyleSheet(
            """
            QPushButton {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: palette(dark);
            }
        """
        )

        # 左パネルのウィジェットを作成
        left_panel = QtWidgets.QWidget()
        left_panel.setLayout(self.controls_layout)
        self.controls_layout.addWidget(theme_info_group)
        self.controls_layout.addWidget(color_sliders_group)
        self.controls_layout.addLayout(generate_buttons_layout)
        self.controls_layout.addWidget(apply_button)

        # 親ウィジェットに追加
        parent.addWidget(left_panel)

        # コントロールパネル設定完了後に遅延処理で入力フィールドを有効化
        QtCore.QTimer.singleShot(200, self._enable_input_fields)

    def setup_preview_panel(self, parent):
        """統合プレビューパネルのセットアップ（無効化 - ライブプレビューを使用）"""
        # プレビューパネルは削除 - メインウィンドウのライブプレビューを使用
        # コントラストチェッカーのみ保持
        preview_widget = QtWidgets.QWidget()
        parent.addWidget(preview_widget)
        layout = QtWidgets.QVBoxLayout(preview_widget)

        # タイトル
        title = QtWidgets.QLabel("テーマ生成コントロール")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # コントラストチェッカー（コンパクト版）
        self.contrast_checker = ContrastChecker()
        layout.addWidget(self.contrast_checker)

        # 生成されたテーマカラー表示
        pairs_group = QtWidgets.QGroupBox("生成されたテーマカラー")
        pairs_layout = QtWidgets.QVBoxLayout(pairs_group)

        # 色ペア用スクロールエリア
        pairs_scroll = QtWidgets.QScrollArea()
        pairs_widget = QtWidgets.QWidget()
        self.pairs_layout = QtWidgets.QVBoxLayout(pairs_widget)

        pairs_scroll.setWidget(pairs_widget)
        pairs_scroll.setWidgetResizable(True)
        pairs_scroll.setMaximumHeight(150)
        pairs_layout.addWidget(pairs_scroll)

        layout.addWidget(pairs_group)

        # 改善提案（コンパクト版）
        suggestions_group = QtWidgets.QGroupBox("改善提案")
        suggestions_layout = QtWidgets.QVBoxLayout(suggestions_group)

        self.suggestions_text = QtWidgets.QTextEdit()
        self.suggestions_text.setMaximumHeight(60)
        self.suggestions_text.setReadOnly(True)
        self.suggestions_text.setPlaceholderText(
            "テーマ生成を実行すると分析結果が表示されます。"
        )
        self.suggestions_text.setStyleSheet("font-size: 11px;")
        suggestions_layout.addWidget(self.suggestions_text)

        layout.addWidget(suggestions_group)

        # 注記を追加
        note_label = QtWidgets.QLabel(
            "※ プレビューはメインウィンドウの「ライブプレビュー」をご確認ください"
        )
        note_label.setStyleSheet(
            "font-size: 10px; font-style: italic; margin-top: 10px;"
        )
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

    def create_comprehensive_preview(self) -> QtWidgets.QWidget:
        """包括的なプレビューウィジェットを作成（無効化 - ライブプレビューを使用）"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # プレビューは削除 - 代わりに説明ラベルを表示
        info_label = QtWidgets.QLabel(
            "プレビューはメインウィンドウの「ライブプレビュー」をご確認ください"
        )
        info_label.setStyleSheet("font-style: italic; padding: 20px;")
        info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        return widget

    def get_color_data(self) -> Dict[str, Dict[str, str]]:
        """現在の色データを取得"""
        return self.current_colors.copy()

    def set_color_data(self, colors_data: Dict[str, str]):
        """色データを設定"""
        self.current_colors.update(colors_data)

        # UIを更新
        if "background" in colors_data:
            self.bg_slider.update_from_hex(colors_data["background"])
        if "primary" in colors_data:
            self.primary_slider.update_from_hex(colors_data["primary"])

        # プレビューを更新
        self.update_preview()

    def load_theme_data(self, theme_data: Dict[str, Any]) -> None:
        """テーマデータを読み込んでUIに反映"""
        try:
            # テーマ名を設定
            theme_name = theme_data.get("name", "")
            if hasattr(self, "theme_name_input") and self.theme_name_input:
                self.theme_name_input.setText(theme_name)

            # テーマ説明を設定
            theme_desc = theme_data.get("description", "")
            if (
                hasattr(self, "theme_description_input")
                and self.theme_description_input
            ):
                self.theme_description_input.setPlainText(theme_desc)

            # 色データを設定
            colors = theme_data.get("colors", {})
            if colors:
                color_data = {
                    "background": colors.get("background", "#fffff"),
                    "primary": colors.get("primary", "#007acc"),
                }
                self.set_color_data(color_data)

            # 生成されたテーマカラーをクリア（新しいテーマなので）
            self.generated_theme_colors = {}

            # プレビューを更新
            self.update_preview()

            self.logger.info(
                "テーマデータを読み込みました: {theme_name}", LogCategory.UI
            )

        except Exception:
            self.logger.error("テーマデータ読み込みに失敗: {str(e)}", LogCategory.ERROR)

    def apply_to_main_theme(self):
        """生成されたテーマをメインテーマエディターに適用"""
        # テーマ名の入力チェック
        theme_name = self.theme_name_input.text().strip()
        if not theme_name:
            QtWidgets.QMessageBox.warning(
                self, "入力エラー", "テーマ名を入力してください。"
            )
            self.theme_name_input.setFocus()
            return

        # テーマ生成チェック
        if not self.generated_theme_colors:
            QtWidgets.QMessageBox.warning(
                self,
                "テーマ未生成",
                "まずテーマ生成ボタンをクリックしてテーマを生成してください。",
            )
            return

        # メインテーマ形式に変換
        main_theme_data = self.convert_to_main_theme_format()

        # メインテーマエディターに適用するシグナルを発信
        self.theme_apply_requested.emit(main_theme_data)

        QtWidgets.QMessageBox.information(
            self,
            "テーマ適用完了",
            "テーマ「{theme_name}」（{len(self.generated_theme_colors)}色）をメインエディターに適用しました。\n"
            "ファイルメニューから保存できます。",
        )

        logger.info(
            "生成テーマ「{theme_name}」をメインエディターに適用しました: {len(self.generated_theme_colors)}色"
        )

    def convert_to_main_theme_format(self) -> dict:
        """生成されたテーマをメインテーマエディター形式に変換"""
        # ユーザーが色調整スライダーで編集した色を取得
        bg_color = (
            self.bg_slider.get_color()
            if hasattr(self, "bg_slider")
            else self.current_colors.get("background", "#fffff")
        )
        primary_color = (
            self.primary_slider.get_color()
            if hasattr(self, "primary_slider")
            else self.current_colors.get("primary", "#007acc")
        )

        # ユーザー入力からテーマ情報を取得
        theme_name = self.theme_name_input.text().strip() or "自動生成テーマ"
        theme_description = (
            self.theme_description_input.toPlainText().strip()
            or "オートテーマジェネレーターで生成されたWCAG準拠テーマ"
        )

        # 基本テーマデータ
        theme_data = {
            "name": theme_name,
            "version": "1.0.0",
            "description": theme_description,
            "colors": {
                "background": bg_color,
                "text": ColorUtils.get_optimal_text_color(bg_color),
                "primary": primary_color,
                "accent": ColorUtils.adjust_brightness(primary_color, 0.2),
            },
            "fonts": {
                "default": {
                    "family": "Arial",
                    "size": 12,
                    "bold": False,
                    "italic": False,
                }
            },
            "properties": {},
        }

        # 生成された色ペアを統合
        for name, colors in self.generated_theme_colors.items():
            # 色ペア名をキーに変換
            key_name = (
                name.lower().replace("テキスト", "").replace("メッセージ", "").strip()
            )

            if "通常" in name:
                theme_data["colors"]["text"] = colors["foreground"]
                theme_data["colors"]["background"] = colors["background"]
            elif "リンク" in name:
                theme_data["colors"]["link"] = colors["foreground"]
            elif "選択" in name:
                theme_data["colors"]["selection"] = colors["background"]
                theme_data["colors"]["selection_text"] = colors["foreground"]
            elif "無効" in name:
                theme_data["colors"]["disabled"] = colors["foreground"]
            elif "エラー" in name:
                theme_data["colors"]["error"] = colors["foreground"]
            elif "成功" in name:
                theme_data["colors"]["success"] = colors["foreground"]
            elif "警告" in name:
                theme_data["colors"]["warning"] = colors["foreground"]
            elif "類似色" in name or "補色" in name or "三色配色" in name:
                # 調和色の場合
                color_key = "harmony_{key_name.replace(' ', '_')}"
                theme_data["colors"][color_key] = colors["foreground"]

        return theme_data

    def apply_accessibility_preset(self, level: str):
        """アクセシビリティプリセットを適用（互換性のため）"""
        self.auto_generate_theme(level)

    def update_color(self, color_key: str, hex_color: str):
        """色を更新"""
        self.current_colors[color_key] = hex_color

        # コントラストチェッカーを更新
        if "background" in self.current_colors and "primary" in self.current_colors:
            self.contrast_checker.check_contrast(
                self.current_colors["background"], self.current_colors["primary"]
            )

        # 遅延更新でプレビューを更新
        self.update_timer.start(200)

        # 色変更をMainWindowに通知
        self.colors_changed.emit(self.current_colors)

    def auto_generate_theme(self, level: str):
        """WCAG準拠でテーマを自動生成"""
        logger.info("WCAG {level}準拠でテーマを自動生成します")

        bg_color = self.current_colors.get("background", "#fffff")
        primary_color = self.current_colors.get("primary", "#007acc")

        # 最適なテキスト色を計算
        optimal_text = ColorUtils.get_optimal_text_color(bg_color)

        # プライマリ色のコントラストをチェックし、必要に応じて調整
        primary_contrast = ColorUtils.get_contrast_ratio(bg_color, primary_color)
        required_contrast = 7.0 if level == "AAA" else 4.5

        adjusted_primary = primary_color
        if primary_contrast < required_contrast:
            # 明度を調整してコントラストを改善
            bg_luminance = ColorUtils.get_luminance(bg_color)
            adjustment = -0.3 if bg_luminance > 0.5 else 0.3

            for i in range(10):  # 最大10回調整を試行
                adjusted_primary = ColorUtils.adjust_brightness(
                    primary_color, adjustment * (i + 1)
                )
                if (
                    ColorUtils.get_contrast_ratio(bg_color, adjusted_primary)
                    >= required_contrast
                ):
                    break

        # 色ペアを生成
        color_pairs = {
            "通常テキスト": {"foreground": optimal_text, "background": bg_color},
            "リンクテキスト": {"foreground": adjusted_primary, "background": bg_color},
            "選択テキスト": {
                "foreground": ColorUtils.get_optimal_text_color(adjusted_primary),
                "background": adjusted_primary,
            },
            "無効テキスト": {
                "foreground": ColorUtils.adjust_brightness(optimal_text, 0.4),
                "background": bg_color,
            },
            "エラーテキスト": {
                "foreground": (
                    "#d32f2" if ColorUtils.get_luminance(bg_color) > 0.5 else "#f44336"
                ),
                "background": bg_color,
            },
            "成功テキスト": {
                "foreground": (
                    "#2e7d32" if ColorUtils.get_luminance(bg_color) > 0.5 else "#4caf50"
                ),
                "background": bg_color,
            },
            "警告テキスト": {
                "foreground": (
                    "#f57c00" if ColorUtils.get_luminance(bg_color) > 0.5 else "#ff9800"
                ),
                "background": bg_color,
            },
        }

        # エラー色と成功色のコントラストも調整
        for pair_name in ["エラーテキスト", "成功テキスト", "警告テキスト"]:
            if pair_name in color_pairs:
                fg_color = color_pairs[pair_name]["foreground"]
                contrast = ColorUtils.get_contrast_ratio(bg_color, fg_color)

                if contrast < required_contrast:
                    # コントラストが不十分な場合は調整
                    bg_luminance = ColorUtils.get_luminance(bg_color)
                    adjustment = -0.4 if bg_luminance > 0.5 else 0.4

                    for i in range(10):
                        adjusted_color = ColorUtils.adjust_brightness(
                            fg_color, adjustment * (i + 1)
                        )
                        if (
                            ColorUtils.get_contrast_ratio(bg_color, adjusted_color)
                            >= required_contrast
                        ):
                            color_pairs[pair_name]["foreground"] = adjusted_color
                            break

        # 生成されたテーマカラーを保存
        self.generated_theme_colors = color_pairs.copy()

        # UIを更新
        self.update_color_pairs_display(color_pairs)
        self.update_suggestions(level, color_pairs)

        # シグナルを発信
        self.colors_changed.emit(color_pairs)

    def _on_update_timeout(self):
        """更新タイマーのタイムアウトハンドラー"""
        # プレビューを更新
        if hasattr(self, "contrast_checker"):
            self.contrast_checker.check_contrast(
                self.current_colors.get("background", "#fffff"),
                self.current_colors.get("primary", "#007acc"),
            )

    def generate_harmonious_palette(self):
        """調和色パレットを生成"""
        import colorsys

        primary_color = self.current_colors.get("primary", "#007acc")
        bg_color = self.current_colors.get("background", "#fffff")

        # プライマリ色から調和色を生成
        r, g, b = ColorUtils.hex_to_rgb(primary_color)
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

        # 類似色（±30度）
        analogous1_h = (h + 0.083) % 1.0  # +30度
        analogous2_h = (h - 0.083) % 1.0  # -30度

        # 補色（180度）
        complement_h = (h + 0.5) % 1.0

        # 三色配色（120度）
        triadic1_h = (h + 0.333) % 1.0
        triadic2_h = (h + 0.667) % 1.0

        # 色を生成
        harmonious_colors = {}
        for name, hue in [
            ("類似色1", analogous1_h),
            ("類似色2", analogous2_h),
            ("補色", complement_h),
            ("三色配色1", triadic1_h),
            ("三色配色2", triadic2_h),
        ]:
            r, g, b = colorsys.hsv_to_rgb(hue, s * 0.8, v * 0.9)
            color = ColorUtils.rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))

            # コントラストをチェックして調整
            contrast = ColorUtils.get_contrast_ratio(bg_color, color)
            if contrast < 4.5:
                # コントラストが不十分な場合は明度を調整
                bg_luminance = ColorUtils.get_luminance(bg_color)
                adjustment = -0.3 if bg_luminance > 0.5 else 0.3
                color = ColorUtils.adjust_brightness(color, adjustment)

            harmonious_colors[name] = {"foreground": color, "background": bg_color}

        # 生成されたテーマカラーを保存
        self.generated_theme_colors = harmonious_colors.copy()

        # UIを更新
        self.update_color_pairs_display(harmonious_colors)
        self.update_suggestions("調和色", harmonious_colors)

        # シグナルを発信
        self.colors_changed.emit(harmonious_colors)

        QtWidgets.QMessageBox.information(
            self,
            "調和色テーマ生成完了",
            "プライマリ色 ({primary_color}) から調和色テーマを生成しました。",
        )

    def update_color_pairs_display(self, color_pairs: dict):
        """色ペア表示を更新（改良版）"""
        # 既存のウィジェットをクリア
        for i in reversed(range(self.pairs_layout.count())):
            child = self.pairs_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # ヘッダーを追加
        header_widget = self.create_pairs_header()
        self.pairs_layout.addWidget(header_widget)

        # 新しい色ペアを表示
        for name, colors in color_pairs.items():
            pair_widget = self.create_color_pair_widget(name, colors)
            self.pairs_layout.addWidget(pair_widget)

        # 統計情報を追加
        stats_widget = self.create_pairs_statistics(color_pairs)
        self.pairs_layout.addWidget(stats_widget)

        self.pairs_layout.addStretch()

    def create_pairs_header(self) -> QtWidgets.QWidget:
        """色ペアリストのヘッダーを作成"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)

        # ヘッダーラベル
        headers = ["名前", "プレビュー", "比率", "WCAG"]
        widths = [80, 100, 40, 30]

        for header, width in zip(headers, widths):
            label = QtWidgets.QLabel(header)
            label.setFixedWidth(width)
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                """
                QLabel {
                    font-weight: bold;
                    font-size: 10px;
                    color: palette(text);
                    background-color: palette(base);
                    border: 1px solid palette(mid);
                    padding: 2px;
                }
            """
            )
            layout.addWidget(label)

        return widget

    def create_pairs_statistics(self, color_pairs: dict) -> QtWidgets.QWidget:
        """色ペアの統計情報を作成"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 統計を計算
        len(color_pairs)
        aa_compliant = sum(
            1
            for colors in color_pairs.values()
            if ColorUtils.is_accessible(
                colors["background"], colors["foreground"], "AA"
            )
        )
        aaa_compliant = sum(
            1
            for colors in color_pairs.values()
            if ColorUtils.is_accessible(
                colors["background"], colors["foreground"], "AAA"
            )
        )

        # 統計表示
        stats_text = """
📊 統計情報:
• 総色ペア数: {total_pairs}
• WCAG AA準拠: {aa_compliant}/{total_pairs} ({aa_compliant/total_pairs*100:.0f}%)
• WCAG AAA準拠: {aaa_compliant}/{total_pairs} ({aaa_compliant/total_pairs*100:.0f}%)
        """.strip()

        stats_label = QtWidgets.QLabel(stats_text)
        stats_label.setStyleSheet(
            """
            QLabel {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                color: palette(text);
            }
        """
        )
        layout.addWidget(stats_label)

        return widget

    def create_color_pair_widget(self, name: str, colors: dict) -> QtWidgets.QWidget:
        """色ペアウィジェットを作成"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # 名前ラベル
        name_label = QtWidgets.QLabel(name)
        name_label.setFixedWidth(80)
        name_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        layout.addWidget(name_label)

        # プレビュー
        preview = QtWidgets.QLabel("サンプル")
        preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        preview.setFixedSize(100, 25)
        preview.setStyleSheet(
            """
            QLabel {{
                background-color: {colors['background']};
                color: {colors['foreground']};
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
            }}
        """
        )
        layout.addWidget(preview)

        # コントラスト比
        contrast = ColorUtils.get_contrast_ratio(
            colors["background"], colors["foreground"]
        )
        contrast_label = QtWidgets.QLabel("{contrast:.1f}:1")
        contrast_label.setFixedWidth(40)
        contrast_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        contrast_label.setStyleSheet("font-size: 10px;")
        layout.addWidget(contrast_label)

        # WCAG適合
        aa_pass = ColorUtils.is_accessible(
            colors["background"], colors["foreground"], "AA"
        )
        aaa_pass = ColorUtils.is_accessible(
            colors["background"], colors["foreground"], "AAA"
        )

        wcag_label = QtWidgets.QLabel(
            "AAA" if aaa_pass else ("AA" if aa_pass else "❌")
        )
        wcag_label.setFixedWidth(30)
        wcag_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        wcag_label.setStyleSheet(
            """
            font-size: 10px; 
            font-weight: bold;
            color: {'green' if aaa_pass else ('orange' if aa_pass else 'red')};
        """
        )
        layout.addWidget(wcag_label)

        return widget

    def update_suggestions(self, level: str, color_pairs: dict):
        """改善提案を更新"""
        suggestions = []

        if level in ["AA", "AAA"]:
            suggestions.append("✅ WCAG {level}準拠の色ペアを生成しました")

            # 各色ペアの評価
            for name, colors in color_pairs.items():
                contrast = ColorUtils.get_contrast_ratio(
                    colors["background"], colors["foreground"]
                )
                if contrast >= 7.0:
                    suggestions.append("• {name}: 優秀 ({contrast:.1f}:1)")
                elif contrast >= 4.5:
                    suggestions.append("• {name}: 良好 ({contrast:.1f}:1)")
                else:
                    suggestions.append("• {name}: 要改善 ({contrast:.1f}:1)")

        elif level == "調和色":
            suggestions.append("🎨 調和色パレットを生成しました")
            suggestions.append("• 類似色: 統一感のある配色")
            suggestions.append("• 補色: 強いコントラスト")
            suggestions.append("• 三色配色: バランスの取れた配色")

        suggestions.append("")
        suggestions.append("💡 ヒント:")
        suggestions.append("• 生成された色はテーマエディターで微調整できます")
        suggestions.append("• 重要な情報には高コントラストの色を使用してください")

        self.suggestions_text.setPlainText("\n".join(suggestions))

    def load_default_colors(self):
        """デフォルト色を読み込み"""
        self.current_colors = {"background": "#fffff", "primary": "#007acc"}

        # 初期コントラストチェック
        self.contrast_checker.check_contrast(
            self.current_colors["background"], self.current_colors["primary"]
        )

    def update_preview(self):
        """統合プレビューを更新（無効化 - ライブプレビューを使用）"""
        # プレビューエリアは削除されたため、何もしない
        # メインウィンドウのライブプレビューが自動更新される

    def apply_theme_to_preview(self):
        """生成されたテーマをプレビューに適用"""
        bg_color = self.current_colors.get("background", "#fffff")
        primary_color = self.current_colors.get("primary", "#007acc")
        ColorUtils.get_optimal_text_color(bg_color)

        # 基本スタイルシート
        base_stylesheet = """
            /* 基本色設定 */
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
            }}
            
            /* ラベル */
            QLabel {{
                color: {text_color};
            }}
            
            QLabel[class="heading"] {{
                color: {primary_color};
                font-size: 16px;
                font-weight: bold;
            }}
            
            QLabel[class="secondary"] {{
                color: {ColorUtils.adjust_brightness(text_color, 0.3)};
            }}
            
            QLabel[class="muted"] {{
                color: {ColorUtils.adjust_brightness(text_color, 0.5)};
            }}
            
            QLabel[class="success"] {{
                color: {self.current_colors.get('success', self.current_colors.get('text_success', '#2e7d32'))};
            }}
            
            QLabel[class="warning"] {{
                color: {self.current_colors.get('warning', self.current_colors.get('text_warning', '#f57c00'))};
            }}
            
            QLabel[class="error"] {{
                color: {self.current_colors.get('error', self.current_colors.get('text_error', '#d32f2'))};
            }}
            
            QLabel[class="link"] {{
                color: {primary_color};
                text-decoration: underline;
            }}
            
            /* ボタン */
            QPushButton {{
                background-color: {ColorUtils.adjust_brightness(bg_color, -0.1)};
                color: {text_color};
                border: 1px solid {ColorUtils.adjust_brightness(bg_color, -0.2)};
                padding: 6px 12px;
                border-radius: 4px;
            }}
            
            QPushButton:hover {{
                background-color: {ColorUtils.adjust_brightness(bg_color, -0.15)};
            }}
            
            QPushButton:pressed {{
                background-color: {ColorUtils.adjust_brightness(bg_color, -0.2)};
            }}
            
            QPushButton[class="primary"] {{
                background-color: {primary_color};
                color: {ColorUtils.get_optimal_text_color(primary_color)};
                border: 1px solid {ColorUtils.adjust_brightness(primary_color, -0.2)};
            }}
            
            QPushButton[class="primary"]:hover {{
                background-color: {ColorUtils.adjust_brightness(primary_color, 0.1)};
            }}
            
            QPushButton:disabled {{
                background-color: {ColorUtils.adjust_brightness(bg_color, -0.05)};
                color: {ColorUtils.adjust_brightness(text_color, 0.5)};
                border: 1px solid {ColorUtils.adjust_brightness(bg_color, -0.1)};
            }}
            
            /* 入力フィールド */
            QLineEdit {{
                background-color: {ColorUtils.adjust_brightness(bg_color, 0.05)};
                color: {text_color};
                border: 1px solid {ColorUtils.adjust_brightness(bg_color, -0.2)};
                padding: 4px 8px;
                border-radius: 3px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {primary_color};
            }}
            
            /* コンボボックス */
            QComboBox {{
                background-color: {ColorUtils.adjust_brightness(bg_color, 0.05)};
                color: {text_color};
                border: 1px solid {ColorUtils.adjust_brightness(bg_color, -0.2)};
                padding: 4px 8px;
                border-radius: 3px;
            }}
            
            QComboBox:hover {{
                border: 1px solid {primary_color};
            }}
            
            QComboBox::drop-down {{
                border: none;
            }}
            
            QComboBox::down-arrow {{
                border: 2px solid {text_color};
                border-top: none;
                border-right: none;
                width: 6px;
                height: 6px;
            }}
            
            /* リストウィジェット（ゼブラスタイル） */
            QListWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {ColorUtils.adjust_brightness(bg_color, -0.2)};
                border-radius: 3px;
            }}
            
            QListWidget::item {{
                padding: 4px 8px;
                border-bottom: 1px solid {ColorUtils.adjust_brightness(bg_color, -0.1)};
            }}
            
            QListWidget::item:alternate {{
                background-color: {ColorUtils.adjust_brightness(bg_color, -0.03)};
            }}
            
            QListWidget::item:selected {{
                background-color: {primary_color};
                color: {ColorUtils.get_optimal_text_color(primary_color)};
            }}
            
            QListWidget::item:hover {{
                background-color: {ColorUtils.adjust_brightness(primary_color, 0.3)};
            }}
            
            /* テキストエディット */
            QTextEdit {{
                background-color: {ColorUtils.adjust_brightness(bg_color, 0.02)};
                color: {text_color};
                border: 1px solid {ColorUtils.adjust_brightness(bg_color, -0.2)};
                border-radius: 3px;
                padding: 4px;
            }}
            
            /* グループボックス */
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ColorUtils.adjust_brightness(bg_color, -0.2)};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {primary_color};
            }}
        """

        # プレビューエリアにスタイルシートを適用
        self.preview_area.setStyleSheet(base_stylesheet)

        # 色が変更されたことをログに記録
        logger.info(
            "プレビューを更新しました: 背景={bg_color}, プライマリ={primary_color}"
        )

    def _enable_input_fields(self):
        """入力フィールドを有効化"""
        if hasattr(self, "theme_name_input"):
            self.theme_name_input.setReadOnly(False)
            self.theme_name_input.setEnabled(True)
            self.theme_name_input.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            self.theme_name_input.setAcceptDrops(True)
            # フォーカスを設定して確実にアクティブにする
            self.theme_name_input.setFocus()
            logger.info("テーマ名入力フィールドを有効化しました")

        if hasattr(self, "theme_description_input"):
            self.theme_description_input.setReadOnly(False)
            self.theme_description_input.setEnabled(True)
            self.theme_description_input.setFocusPolicy(
                QtCore.Qt.FocusPolicy.StrongFocus
            )
            self.theme_description_input.setAcceptDrops(True)
            logger.info("テーマ概要入力フィールドを有効化しました")

    def load_theme(self, theme_data: dict):
        """読み込まれたテーマデータからスライダーの値を更新

        Args:
            theme_data: テーマデータ辞書
        """
        try:
            logger.info("オートテーマジェネレーターにテーマデータを読み込み中...")

            # テーマ名と説明を設定
            if "name" in theme_data and hasattr(self, "theme_name_input"):
                self.theme_name_input.setText(theme_data["name"])
                logger.debug("テーマ名を設定: {theme_data['name']}")

            if "description" in theme_data and hasattr(self, "theme_description_input"):
                self.theme_description_input.setPlainText(theme_data["description"])
                logger.debug("テーマ説明を設定: {theme_data['description']}")

            # 色情報を抽出してスライダーに反映
            colors = theme_data.get("colors", {})

            # 背景色を設定
            background_color = colors.get("background", colors.get("window", "#fffff"))
            if background_color and hasattr(self, "bg_slider"):
                self.bg_slider.update_from_hex(background_color)
                self.current_colors["background"] = background_color
                logger.debug("背景色を設定: {background_color}")

            # プライマリ色を設定（複数の候補から選択）
            primary_candidates = [
                colors.get("primary"),
                colors.get("accent"),
                colors.get("highlight"),
                colors.get("selection"),
                colors.get("link"),
                colors.get("button"),
                "#007acc",  # デフォルト値
            ]

            primary_color = None
            for candidate in primary_candidates:
                if candidate and candidate != background_color:
                    primary_color = candidate
                    break

            if primary_color and hasattr(self, "primary_slider"):
                self.primary_slider.update_from_hex(primary_color)
                self.current_colors["primary"] = primary_color
                logger.debug("プライマリ色を設定: {primary_color}")

            # コントラストチェッカーを更新
            if hasattr(self, "contrast_checker"):
                self.contrast_checker.check_contrast(
                    self.current_colors.get("background", "#fffff"),
                    self.current_colors.get("primary", "#007acc"),
                )

            # プレビューを更新
            self.update_preview()

            # 色変更シグナルを発信
            self.colors_changed.emit(self.current_colors)

            logger.info(
                "テーマデータの読み込み完了: 背景={self.current_colors.get('background')}, プライマリ={self.current_colors.get('primary')}"
            )

        except Exception:
            logger.error("テーマデータの読み込みに失敗しました: {str(e)}")
            # エラーが発生してもデフォルト値で継続
            self.load_default_colors()
