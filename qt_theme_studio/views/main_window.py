#!/usr/bin/env python3
"""
Qt-Theme-Studio メインウィンドウ
クリーンなアーキテクチャによる高度なテーマ管理・生成・編集
"""

from pathlib import Path
from typing import Any, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.adapters.theme_adapter import ThemeAdapter
from qt_theme_studio.generators.theme_generator import ThemeGenerator
from qt_theme_studio.logger import get_logger
from qt_theme_studio.views.preview import PreviewWindow


class QtThemeStudioMainWindow(QMainWindow):
    """Qt-Theme-Studio メインウィンドウ"""

    def __init__(self) -> None:
        super().__init__()

        # ロガーを初期化
        self.logger = get_logger()
        self.logger.info("QtThemeStudioMainWindow初期化開始...")

        self.setWindowTitle("Qt-Theme-Studio - 高度なテーマ管理・生成・編集")
        self.setGeometry(100, 100, 1800, 1200)

        # ウィンドウ設定を最適化
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.logger.debug("ウィンドウ基本設定完了")

        try:
            self.logger.debug("アダプター作成中...")
            # アダプターを作成
            self.qt_adapter = QtAdapter()
            self.theme_adapter = ThemeAdapter()
            self.logger.debug("アダプター作成完了")

            self.logger.debug("PreviewWindow作成中...")
            # PreviewWindowを作成
            self.preview_window = PreviewWindow(self.qt_adapter, self.theme_adapter)
            self.preview_widget = self.preview_window.create_widget()
            self.logger.debug("PreviewWindow作成完了")

            self.logger.debug("テーマジェネレータ作成中...")
            # テーマジェネレータを作成
            self.theme_generator = ThemeGenerator()
            self.logger.debug("テーマジェネレータ作成完了")

            self.logger.debug("テーマ管理初期化中...")
            # テーマ管理
            self.themes: dict[str, dict] = {}  # テーマ辞書
            self.current_theme_name: Union[str, None] = None
            self.logger.debug("テーマ管理初期化完了")

            self.logger.debug("UIセットアップ中...")
            self.setup_menu_bar()
            self.setup_ui()
            self.logger.debug("UIセットアップ完了")

            self.logger.info("QtThemeStudioMainWindow初期化完了!")

        except Exception as e:
            self.logger.error(f"初期化エラー: {e}")
            self.logger.error(f"エラータイプ: {type(e).__name__}")
            import traceback

            traceback.print_exc()

    def setup_menu_bar(self) -> None:
        """メニューバーをセットアップ"""
        menubar = self.menuBar()

        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル(&F)")

        # テーマ読み込み
        load_action = file_menu.addAction("テーマファイル読み込み(&L)")
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_custom_theme_file)

        # テーマ保存
        save_action = file_menu.addAction("テーマ保存(&S)")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current_theme)

        file_menu.addSeparator()

        # 全テーマエクスポート
        export_action = file_menu.addAction("全テーマエクスポート(&E)")
        export_action.triggered.connect(self.export_all_themes)

        file_menu.addSeparator()

        # 終了
        exit_action = file_menu.addAction("終了(&X)")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        # テーマメニュー
        theme_menu = menubar.addMenu("テーマ(&T)")

        # テーマ適用
        apply_action = theme_menu.addAction("テーマ適用(&A)")
        apply_action.setShortcut("Ctrl+T")
        apply_action.triggered.connect(self.apply_current_theme)

        # ワンクリック生成
        generate_action = theme_menu.addAction("ワンクリック生成(&G)")
        generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self.generate_theme_from_background)

        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ(&H)")

        # バージョン情報
        about_action = help_menu.addAction("Qt-Theme-Studioについて(&A)")
        about_action.triggered.connect(self.show_about)

    def setup_ui(self) -> None:
        """UIをセットアップ"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # テーマ管理パネル
        theme_panel = QWidget()
        theme_layout = QHBoxLayout(theme_panel)

        # テーマ読み込みボタン
        load_btn = QPushButton("テーマファイル読み込み")
        load_btn.clicked.connect(self.load_custom_theme_file)
        theme_layout.addWidget(load_btn)

        # テーマ選択ボタン
        self.theme_button = QToolButton()
        self.theme_button.setText("テーマを選択")
        self.theme_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.theme_menu = QMenu()
        self.theme_button.setMenu(self.theme_menu)
        theme_layout.addWidget(QLabel("テーマ選択:"))
        theme_layout.addWidget(self.theme_button)

        # テーマ適用ボタン
        apply_btn = QPushButton("テーマ適用")
        apply_btn.clicked.connect(self.apply_current_theme)
        theme_layout.addWidget(apply_btn)

        # 保存・エクスポート機能
        save_btn = QPushButton("テーマ保存")
        save_btn.clicked.connect(self.save_current_theme)
        theme_layout.addWidget(save_btn)

        export_all_btn = QPushButton("全テーマエクスポート")
        export_all_btn.clicked.connect(self.export_all_themes)
        theme_layout.addWidget(export_all_btn)

        theme_layout.addStretch()
        layout.addWidget(theme_panel)

        # メインコンテンツエリア(テーマジェネレータとプレビューを横並び)
        content_layout = QHBoxLayout()

        # テーマジェネレータ(左側)
        generator_group = self.create_theme_generator()
        content_layout.addWidget(generator_group, 1)

        # プレビュー(右側)
        content_layout.addWidget(self.preview_widget, 2)
        layout.addLayout(content_layout)

    def create_theme_generator(self) -> QGroupBox:
        """テーマジェネレータを作成"""
        group = QGroupBox("🎨 ワンクリックテーマジェネレータ")
        layout = QVBoxLayout(group)

        # ワンクリックテーマ生成
        quick_group = QGroupBox("ワンクリックテーマ生成")
        quick_layout = QVBoxLayout(quick_group)

        # 背景色選択(メイン)
        bg_layout = QHBoxLayout()
        bg_layout.addWidget(QLabel("背景色を選択:"))
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(80, 40)
        self.bg_color_btn.setStyleSheet(
            "background-color: #ffffff; border: 2px solid #ccc;"
        )
        self.bg_color_btn.clicked.connect(lambda: self.choose_color("background"))
        bg_layout.addWidget(self.bg_color_btn)

        # ワンクリック生成ボタン
        quick_generate_btn = QPushButton("🎨 ワンクリックでテーマ生成")
        quick_generate_btn.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 10px;"
        )
        quick_generate_btn.clicked.connect(self.generate_theme_from_background)
        bg_layout.addWidget(quick_generate_btn)
        bg_layout.addStretch()
        quick_layout.addLayout(bg_layout)

        # プリセットテーマ
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("プリセット:"))

        preset_themes = self.theme_generator.get_preset_themes()
        for _theme_id, theme_info in preset_themes.items():
            preset_btn = QPushButton(theme_info["name"])
            color = theme_info["background"]
            is_dark = self.theme_generator.is_dark_color(color)
            preset_btn.setStyleSheet(
                f"background-color: {color}; "
                f"color: {'white' if is_dark else 'black'}; "
                f"padding: 5px;"
            )
            preset_btn.clicked.connect(
                lambda _checked, c=color: self.apply_preset_color(c)
            )
            preset_layout.addWidget(preset_btn)

        quick_layout.addLayout(preset_layout)
        layout.addWidget(quick_group)

        # 生成されたテーマのプレビュー
        preview_group = QGroupBox("生成テーマプレビュー")
        preview_layout = QVBoxLayout(preview_group)
        self.generated_theme_preview = QTextEdit()
        self.generated_theme_preview.setMaximumHeight(200)
        self.generated_theme_preview.setReadOnly(True)
        preview_layout.addWidget(self.generated_theme_preview)
        layout.addWidget(preview_group)

        layout.addStretch()
        return group

    def choose_color(self, color_type: str) -> None:
        """色選択ダイアログを表示"""
        current_color = self.get_current_color(color_type)

        # 色選択ダイアログをインスタンス化して適切な親子関係を設定
        color_dialog = QColorDialog(current_color, self)

        # ダイアログを表示
        if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
            color = color_dialog.currentColor()
            if color.isValid():
                self.set_color_button(color_type, color)

    def get_current_color(self, color_type: str) -> QColor:
        """現在の色を取得"""
        if color_type == "background":
            btn = self.bg_color_btn
            style = btn.styleSheet()
            if "background-color:" in style:
                color_str = style.split("background-color:")[1].split(";")[0].strip()
                return QColor(color_str)
        return QColor("#000000")

    def set_color_button(self, color_type: str, color: QColor) -> None:
        """色ボタンの色を設定"""
        if color_type == "background":
            self.bg_color_btn.setStyleSheet(
                f"background-color: {color.name()}; border: 2px solid #ccc;"
            )

    def apply_preset_color(self, color: str) -> None:
        """プリセット色を適用"""
        self.logger.info(f"プリセット色適用: {color}")

        # 背景色ボタンの色を更新
        self.set_color_button("background", QColor(color))

        # 自動的にテーマを生成
        self.generate_theme_from_background()

        self.logger.info(f"プリセット色 {color} からテーマ生成完了")

    def generate_theme_from_background(self) -> None:
        """背景色から自動的にテーマを生成"""
        try:
            bg_color = self.get_current_color("background")
            self.logger.info(f"背景色からテーマ生成開始: {bg_color.name()}")

            # テーマジェネレータでテーマを生成
            theme_data = self.theme_generator.generate_theme_from_background(bg_color)

            # テーマを追加
            theme_name = f"auto_{len(self.themes)}"
            theme_data["name"] = theme_name

            self.themes[theme_name] = theme_data
            self.add_theme_to_menu(theme_name, theme_data["display_name"])

            # 生成されたテーマを選択
            self.current_theme_name = theme_name
            self.theme_button.setText(theme_data["display_name"])

            # テーマを適用
            self.apply_current_theme()

            # 生成されたテーマのプレビューを更新
            self.update_generated_theme_preview()

            self.logger.info(
                f"ワンクリックでテーマ「{theme_name}」を生成・適用しました"
            )

            # 成功メッセージを表示
            QMessageBox.information(
                self,
                "テーマ生成完了",
                f"背景色から自動的にテーマを生成しました!\n\n"
                f"テーマ名: {theme_data['display_name']}\n"
                f"背景色: {bg_color.name()}\n"
                f"プライマリ色: {theme_data['primaryColor']}\n"
                f"テキスト色: {theme_data['textColor']}",
            )

        except Exception as e:
            self.logger.error(f"ワンクリックテーマ生成エラー: {e}")
            QMessageBox.critical(
                self, "エラー", f"テーマの自動生成に失敗しました:\n{e!s}"
            )

    def update_generated_theme_preview(self) -> None:
        """生成テーマのプレビューを更新"""
        if self.current_theme_name and self.current_theme_name in self.themes:
            theme = self.themes[self.current_theme_name]
            import json

            theme_json = json.dumps(theme, indent=2, ensure_ascii=False)
            self.generated_theme_preview.setPlainText(theme_json)

    def load_custom_theme_file(self) -> None:
        """カスタムテーマファイルを読み込み"""
        try:
            # ファイルダイアログを設定
            dialog = QFileDialog(self, "テーマファイルを選択")
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            dialog.setNameFilter("JSON Files (*.json)")
            dialog.setViewMode(QFileDialog.ViewMode.List)

            # ファイルダイアログを表示
            if dialog.exec() == QFileDialog.DialogCode.Accepted:
                file_path = dialog.selectedFiles()[0]
                self._load_theme_from_file(file_path)

        except Exception as e:
            self.logger.error(f"ファイルダイアログ作成エラー: {e}")
            QMessageBox.critical(
                self, "エラー", f"ファイルダイアログの作成に失敗しました:\n{e!s}"
            )

    def _load_theme_from_file(self, file_path: str) -> None:
        """ファイルからテーマを読み込み"""
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                import json

                theme_data = json.load(f)

            # 単一テーマか複数テーマかを判定
            if "available_themes" in theme_data:
                # 複数テーマファイル
                available_themes = theme_data.get("available_themes", {})
                for theme_name, theme_config in available_themes.items():
                    if theme_name not in self.themes:
                        self.themes[theme_name] = theme_config
                        self.add_theme_to_menu(
                            theme_name, theme_config.get("display_name", theme_name)
                        )
            else:
                # 単一テーマファイル
                theme_name = theme_data.get("name", f"custom_{len(self.themes)}")
                if theme_name not in self.themes:
                    self.themes[theme_name] = theme_data
                    self.add_theme_to_menu(
                        theme_name, theme_data.get("display_name", theme_name)
                    )

            self.logger.info(f"カスタムテーマを読み込みました: {file_path}")

            # 成功メッセージを表示
            QMessageBox.information(
                self, "読み込み完了", f"カスタムテーマを読み込みました:\n{file_path}"
            )

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON形式エラー: {e}")
            QMessageBox.critical(
                self,
                "ファイル形式エラー",
                f"JSONファイルの形式が正しくありません:\n{e!s}",
            )
        except Exception as e:
            self.logger.error(f"ファイル読み込みエラー: {e}")
            QMessageBox.critical(
                self, "読み込みエラー", f"ファイルの読み込みに失敗しました:\n{e!s}"
            )

    def add_theme_to_menu(self, theme_name: str, display_name: str) -> None:
        """テーマをメニューに追加"""
        action = self.theme_menu.addAction(display_name)
        action.triggered.connect(
            lambda: self.on_theme_selected(theme_name, display_name)
        )

    def on_theme_selected(self, theme_name: str, display_name: str) -> None:
        """テーマが選択された時の処理"""
        self.current_theme_name = theme_name
        self.theme_button.setText(display_name)

        self.logger.info(f"テーマ選択: {display_name} -> {theme_name}")
        self.apply_current_theme()

    def apply_current_theme(self) -> None:
        """現在選択されているテーマを適用"""
        if self.current_theme_name and self.current_theme_name in self.themes:
            theme_config = self.themes[self.current_theme_name]

            self.logger.info(
                f"\n=== テーマ適用: {theme_config.get('display_name', self.current_theme_name)} ==="
            )
            self.logger.info(f"テーマ設定: {theme_config}")

            # qt-theme-manager形式のテーマをプレビュー用形式に変換
            converted_theme = self.convert_theme_for_preview(theme_config)
            self.logger.info(f"変換後のテーマ: {converted_theme}")

            # メインウィンドウにもテーマを適用
            self._apply_theme_to_main_window(converted_theme)

            # プレビューウィンドウにテーマを適用
            self.preview_window.apply_theme(converted_theme)

            self.logger.info(
                f"テーマ「{theme_config.get('display_name', self.current_theme_name)}」を適用完了"
            )

    def _apply_theme_to_main_window(self, theme_data: dict[str, Any]) -> None:
        """メインウィンドウにテーマを適用"""
        try:
            colors = theme_data.get("colors", {})
            if not colors:
                return

            # メインウィンドウ用のスタイルシートを生成
            main_window_stylesheet = self._generate_main_window_stylesheet(colors)

            # メインウィンドウ全体にスタイルシートを適用
            self.setStyleSheet(main_window_stylesheet)

            # 中央ウィジェットにもスタイルシートを適用
            central_widget = self.centralWidget()
            if central_widget:
                central_widget.setStyleSheet(main_window_stylesheet)

            self.logger.info("メインウィンドウにテーマを適用しました")

        except Exception as e:
            self.logger.error(f"メインウィンドウへのテーマ適用エラー: {e}")

    def _generate_main_window_stylesheet(self, colors: dict[str, str]) -> str:
        """メインウィンドウ用のスタイルシートを生成"""
        return f"""
        QMainWindow {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
        }}
        QWidget {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
        }}
        QGroupBox {{
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
            border: 2px solid {colors.get("border", colors.get("primary", "#007acc"))};
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            background-color: {colors.get("background", "#ffffff")};
            color: {colors.get("text", "#333333")};
        }}
        QPushButton {{
            background-color: {colors.get("button_background", colors.get("primary", "#007acc"))};
            color: {colors.get("button_text", "#ffffff")};
            border: 2px solid {colors.get("button_background", colors.get("primary", "#007acc"))};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 20px;
        }}
        QPushButton:hover {{
            background-color: {colors.get("button_hover", colors.get("accent", colors.get("primary", "#007acc")))};
            border-color: {colors.get("button_hover", colors.get("accent", colors.get("primary", "#007acc")))};
        }}
        QPushButton:pressed {{
            background-color: {colors.get("button_pressed", colors.get("primary", "#007acc"))};
        }}
        QPushButton:disabled {{
            background-color: {colors.get("disabled_background", "#cccccc")};
            color: {colors.get("disabled_text", "#666666")};
            border-color: {colors.get("disabled_border", "#cccccc")};
        }}
        QComboBox {{
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
            selection-background-color: {colors.get("selection_background", colors.get("primary", "#007acc"))};
            selection-color: {colors.get("selection_text", "#ffffff")};
        }}
        QLabel {{
            background-color: transparent;
            color: {colors.get("text", "#333333")};
        }}
        QTextEdit {{
            background-color: {colors.get("input_background", colors.get("background", "#ffffff"))};
            color: {colors.get("input_text", colors.get("text", "#333333"))};
            border: 2px solid {colors.get("input_border", colors.get("primary", "#007acc"))};
            border-radius: 4px;
            padding: 6px;
        }}
        """

    def convert_theme_for_preview(self, theme_config: dict[str, Any]) -> dict[str, Any]:
        """qt-theme-manager形式のテーマをプレビュー用形式に変換"""
        try:
            # プレビュー機能が期待する形式に変換

            return {
                "name": theme_config.get("display_name", self.current_theme_name),
                "colors": {
                    "background": theme_config.get("backgroundColor", "#ffffff"),
                    "text": theme_config.get("textColor", "#333333"),
                    "primary": theme_config.get("primaryColor", "#007acc"),
                    "accent": theme_config.get(
                        "accentColor", theme_config.get("primaryColor", "#007acc")
                    ),
                },
            }

        except Exception as e:
            self.logger.error(f"テーマ変換エラー: {e}")
            import traceback

            traceback.print_exc()
            # エラーの場合は元のテーマをそのまま返す
            return theme_config

    def save_current_theme(self) -> None:
        """現在選択されているテーマを保存"""
        if self.current_theme_name and self.current_theme_name in self.themes:
            try:
                # ファイル保存ダイアログを設定
                dialog = QFileDialog(self, "テーマを保存")
                dialog.setFileMode(QFileDialog.FileMode.AnyFile)
                dialog.setNameFilter("JSON Files (*.json)")
                dialog.setViewMode(QFileDialog.ViewMode.List)
                dialog.setDefaultSuffix("json")

                # ファイル保存ダイアログを表示

                if dialog.exec() == QFileDialog.DialogCode.Accepted:
                    file_path = dialog.selectedFiles()[0]
                else:
                    return

                if file_path:
                    theme_data = self.themes[self.current_theme_name]

                    # テーマデータを保存
                    with Path(file_path).open("w", encoding="utf-8") as f:
                        import json

                        json.dump(theme_data, f, indent=2, ensure_ascii=False)

                    self.logger.info(
                        f"テーマ「{self.current_theme_name}」を保存しました: {file_path}"
                    )

                    # 成功メッセージを表示
                    QMessageBox.information(
                        self,
                        "保存完了",
                        f"テーマ「{self.current_theme_name}」を保存しました:\n{file_path}",
                    )
            except Exception as e:
                self.logger.error(f"テーマ保存エラー: {e}")
                QMessageBox.critical(
                    self, "保存エラー", f"テーマの保存に失敗しました:\n{e!s}"
                )
        else:
            self.logger.warning("保存するテーマが選択されていません")
            QMessageBox.warning(self, "警告", "保存するテーマが選択されていません")

    def export_all_themes(self) -> None:
        """全テーマをエクスポート"""
        if not self.themes:
            self.logger.warning("エクスポートするテーマがありません")
            QMessageBox.warning(self, "警告", "エクスポートするテーマがありません")
            return

        try:
            # フォルダ選択ダイアログを設定
            dialog = QFileDialog(self, "エクスポート先フォルダを選択")
            dialog.setFileMode(QFileDialog.FileMode.Directory)
            dialog.setViewMode(QFileDialog.ViewMode.List)

            # フォルダ選択ダイアログを表示
            dialog.setOptions(QFileDialog.Option.ShowDirsOnly)

            if dialog.exec() == QFileDialog.DialogCode.Accepted:
                folder_path = dialog.selectedFiles()[0]
            else:
                return

            if folder_path:
                exported_count = 0

                for theme_name, theme_data in self.themes.items():
                    # 各テーマを個別ファイルとして保存
                    file_path = Path(folder_path) / f"{theme_name}.json"

                    with Path(file_path).open("w", encoding="utf-8") as f:
                        import json

                        json.dump(theme_data, f, indent=2, ensure_ascii=False)

                    exported_count += 1

                self.logger.info(
                    f"{exported_count}個のテーマをエクスポートしました: {folder_path}"
                )

                # 成功メッセージを表示
                QMessageBox.information(
                    self,
                    "エクスポート完了",
                    f"{exported_count}個のテーマをエクスポートしました:\n{folder_path}",
                )
        except Exception as e:
            self.logger.error(f"テーマエクスポートエラー: {e}")
            QMessageBox.critical(
                self,
                "エクスポートエラー",
                f"テーマのエクスポートに失敗しました:\n{e!s}",
            )

    def show_about(self) -> None:
        """バージョン情報を表示"""
        QMessageBox.about(
            self,
            "Qt-Theme-Studioについて",
            "<h3>Qt-Theme-Studio v0.1.0</h3>"
            "<p>統合テーマエディターGUIアプリケーション</p>"
            "<p>Qtアプリケーション(PyQt5/PyQt6/PySide6)向けの<br>"
            "直感的なビジュアルインターフェースでテーマの作成・編集・管理を行います。</p>"
            "<p><b>主要機能:</b></p>"
            "<ul>"
            "<li>統合テーマエディター</li>"
            "<li>ゼブラパターンエディター</li>"
            "<li>ライブプレビューシステム</li>"
            "<li>スマートテーマ管理</li>"
            "<li>アクセシビリティ対応</li>"
            "</ul>"
            "<p>© 2024 Qt-Theme-Studio Team</p>",
        )
