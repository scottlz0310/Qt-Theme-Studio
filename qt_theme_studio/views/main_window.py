#!/usr/bin/env python3
"""
Qt-Theme-Studio メインウィンドウ
クリーンなアーキテクチャによる高度なテーマ管理・生成・編集
"""

from pathlib import Path

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
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

    def __init__(self):
        super().__init__()

        # ロガーを初期化
        self.logger = get_logger()
        self.logger.info("QtThemeStudioMainWindow初期化開始...")

        self.setWindowTitle("Qt-Theme-Studio - 高度なテーマ管理・生成・編集")
        self.setGeometry(100, 100, 1800, 1200)
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
            self.themes = {}  # テーマ辞書
            self.current_theme_name = None
            self.logger.debug("テーマ管理初期化完了")

            self.logger.debug("UIセットアップ中...")
            self.setup_ui()
            self.logger.debug("UIセットアップ完了")

            self.logger.info("QtThemeStudioMainWindow初期化完了!")

        except Exception as e:
            self.logger.error(f"初期化エラー: {e}")
            self.logger.error(f"エラータイプ: {type(e).__name__}")
            import traceback
            traceback.print_exc()

    def setup_ui(self):
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

        # テーマ選択コンボボックス
        self.theme_combo = QComboBox()
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(QLabel("テーマ選択:"))
        theme_layout.addWidget(self.theme_combo)

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

    def create_theme_generator(self):
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
        self.bg_color_btn.setStyleSheet("background-color: #ffffff; border: 2px solid #ccc;")
        self.bg_color_btn.clicked.connect(lambda: self.choose_color("background"))
        bg_layout.addWidget(self.bg_color_btn)

        # ワンクリック生成ボタン
        quick_generate_btn = QPushButton("🎨 ワンクリックでテーマ生成")
        quick_generate_btn.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
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
                lambda c=color: self.apply_preset_color(c)
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

    def choose_color(self, color_type):
        """色選択ダイアログを表示"""
        current_color = self.get_current_color(color_type)
        color = QColorDialog.getColor(current_color, self)

        if color.isValid():
            self.set_color_button(color_type, color)

    def get_current_color(self, color_type):
        """現在の色を取得"""
        if color_type == "background":
            btn = self.bg_color_btn
            style = btn.styleSheet()
            if "background-color:" in style:
                color_str = style.split("background-color:")[1].split(";")[0].strip()
                return QColor(color_str)
        return QColor("#000000")

    def set_color_button(self, color_type, color):
        """色ボタンの色を設定"""
        if color_type == "background":
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()}; border: 2px solid #ccc;")

    def apply_preset_color(self, color):
        """プリセット色を適用"""
        self.set_color_button("background", QColor(color))
        # 自動的にテーマを生成
        self.generate_theme_from_background()

    def generate_theme_from_background(self):
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
            self.theme_combo.addItem(theme_data["display_name"])

            # 生成されたテーマを選択
            self.current_theme_name = theme_name
            self.theme_combo.setCurrentText(theme_data["display_name"])

            # テーマを適用
            self.apply_current_theme()

            # 生成されたテーマのプレビューを更新
            self.update_generated_theme_preview()

            self.logger.info(f"ワンクリックでテーマ「{theme_name}」を生成・適用しました")

            # 成功メッセージを表示
            QMessageBox.information(
                self, "テーマ生成完了",
                f"背景色から自動的にテーマを生成しました!\n\n"
                f"テーマ名: {theme_data['display_name']}\n"
                f"背景色: {bg_color.name()}\n"
                f"プライマリ色: {theme_data['primaryColor']}\n"
                f"テキスト色: {theme_data['textColor']}"
            )

        except Exception as e:
            self.logger.error(f"ワンクリックテーマ生成エラー: {e}")
            QMessageBox.critical(
                self, "エラー",
                f"テーマの自動生成に失敗しました:\n{e!s}"
            )

    def update_generated_theme_preview(self):
        """生成テーマのプレビューを更新"""
        if self.current_theme_name and self.current_theme_name in self.themes:
            theme = self.themes[self.current_theme_name]
            import json
            theme_json = json.dumps(theme, indent=2, ensure_ascii=False)
            self.generated_theme_preview.setPlainText(theme_json)

    def load_custom_theme_file(self):
        """カスタムテーマファイルを読み込み"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "テーマファイルを選択",
                "",
                "JSON Files (*.json)"
            )

            if file_path:
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
                                self.theme_combo.addItem(theme_config.get("display_name", theme_name))
                    else:
                        # 単一テーマファイル
                        theme_name = theme_data.get("name", f"custom_{len(self.themes)}")
                        if theme_name not in self.themes:
                            self.themes[theme_name] = theme_data
                            self.theme_combo.addItem(theme_data.get("display_name", theme_name))

                    self.logger.info(f"カスタムテーマを読み込みました: {file_path}")

                    # 成功メッセージを表示
                    QMessageBox.information(
                        self, "読み込み完了",
                        f"カスタムテーマを読み込みました:\n{file_path}"
                    )

                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON形式エラー: {e}")
                    QMessageBox.critical(
                        self, "ファイル形式エラー",
                        f"JSONファイルの形式が正しくありません:\n{e!s}"
                    )
                except Exception as e:
                    self.logger.error(f"ファイル読み込みエラー: {e}")
                    QMessageBox.critical(
                        self, "読み込みエラー",
                        f"ファイルの読み込みに失敗しました:\n{e!s}"
                    )

        except Exception as e:
            self.logger.error(f"ファイル選択エラー: {e}")
            QMessageBox.critical(
                self, "エラー",
                f"ファイル選択でエラーが発生しました:\n{e!s}"
            )
            import traceback
            traceback.print_exc()

    def on_theme_changed(self, display_name):
        """テーマ選択が変更された時の処理"""
        # display_nameからtheme_nameを逆引き
        for theme_name, theme_config in self.themes.items():
            if theme_config.get("display_name", theme_name) == display_name:
                self.current_theme_name = theme_name
                break

    def apply_current_theme(self):
        """現在選択されているテーマを適用"""
        if self.current_theme_name and self.current_theme_name in self.themes:
            theme_config = self.themes[self.current_theme_name]

            self.logger.info(f"\n=== テーマ適用: {theme_config.get('display_name', self.current_theme_name)} ===")
            self.logger.info(f"テーマ設定: {theme_config}")

            # qt-theme-manager形式のテーマをプレビュー用形式に変換
            converted_theme = self.convert_theme_for_preview(theme_config)
            self.logger.info(f"変換後のテーマ: {converted_theme}")

            # プレビューにテーマを適用
            self.preview_window.update_preview(converted_theme)

            self.logger.info("テーマをプレビューに適用しました")
        else:
            self.logger.warning("適用するテーマが選択されていません")

    def convert_theme_for_preview(self, theme_config):
        """qt-theme-manager形式のテーマをプレビュー用形式に変換"""
        try:
            # プレビュー機能が期待する形式に変換

            return {
                "name": theme_config.get("display_name", self.current_theme_name),
                "colors": {
                    "background": theme_config.get("backgroundColor", "#ffffff"),
                    "text": theme_config.get("textColor", "#333333"),
                    "primary": theme_config.get("primaryColor", "#007acc"),
                    "accent": theme_config.get("accentColor", theme_config.get("primaryColor", "#007acc")),
                },
            }

        except Exception as e:
            self.logger.error(f"テーマ変換エラー: {e}")
            import traceback
            traceback.print_exc()
            # エラーの場合は元のテーマをそのまま返す
            return theme_config

    def save_current_theme(self):
        """現在選択されているテーマを保存"""
        if self.current_theme_name and self.current_theme_name in self.themes:
            try:
                # ファイル保存ダイアログを表示
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "テーマを保存",
                    f"{self.current_theme_name}.json",
                    "JSON Files (*.json)"
                )

                if file_path:
                    theme_data = self.themes[self.current_theme_name]

                    # テーマデータを保存
                    with Path(file_path).open("w", encoding="utf-8") as f:
                        import json
                        json.dump(theme_data, f, indent=2, ensure_ascii=False)

                    self.logger.info(f"テーマ「{self.current_theme_name}」を保存しました: {file_path}")

                    # 成功メッセージを表示
                    QMessageBox.information(
                        self, "保存完了",
                        f"テーマ「{self.current_theme_name}」を保存しました:\n{file_path}"
                    )
            except Exception as e:
                self.logger.error(f"テーマ保存エラー: {e}")
                QMessageBox.critical(
                    self, "保存エラー",
                    f"テーマの保存に失敗しました:\n{e!s}"
                )
        else:
            self.logger.warning("保存するテーマが選択されていません")
            QMessageBox.warning(
                self, "警告",
                "保存するテーマが選択されていません"
            )

    def export_all_themes(self):
        """全テーマをエクスポート"""
        if not self.themes:
            self.logger.warning("エクスポートするテーマがありません")
            QMessageBox.warning(
                self, "警告",
                "エクスポートするテーマがありません"
            )
            return

        try:
            # フォルダ選択ダイアログを表示
            folder_path = QFileDialog.getExistingDirectory(
                self, "エクスポート先フォルダを選択"
            )

            if folder_path:
                exported_count = 0

                for theme_name, theme_data in self.themes.items():
                    # 各テーマを個別ファイルとして保存
                    file_path = Path(folder_path) / f"{theme_name}.json"

                    with Path(file_path).open("w", encoding="utf-8") as f:
                        import json
                        json.dump(theme_data, f, indent=2, ensure_ascii=False)

                    exported_count += 1

                self.logger.info(f"{exported_count}個のテーマをエクスポートしました: {folder_path}")

                # 成功メッセージを表示
                QMessageBox.information(
                    self, "エクスポート完了",
                    f"{exported_count}個のテーマをエクスポートしました:\n{folder_path}"
                )
        except Exception as e:
            self.logger.error(f"テーマエクスポートエラー: {e}")
            QMessageBox.critical(
                self, "エクスポートエラー",
                f"テーマのエクスポートに失敗しました:\n{e!s}"
            )
