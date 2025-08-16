"""
テーマギャラリーUI実装

このモジュールは、保存されたテーマの一覧表示、サムネイル生成、
検索・フィルタリング機能を提供するテーマギャラリーUIを実装します。
"""

import json
import re
from typing import Any, Dict, List

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPainter, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..logger import Logger
from ..services.import_service import ImportError, ThemeImportService


class ThemeCard(QFrame):
    """テーマカード表示ウィジェット"""

    theme_selected = Signal(str)  # テーマパス
    theme_deleted = Signal(str)  # テーマパス

    def __init__(self, theme_path: str, theme_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.theme_path = theme_path
        self.theme_data = theme_data
        self.logger = Logger()

        self.setup_ui()
        self.generate_thumbnail()

    def setup_ui(self):
        """UIセットアップ"""
        self.setFrameStyle(QFrame.Box)
        self.setFixedSize(200, 250)
        self.setStyleSheet(
            """
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 8px;
                background-color: white;
            }
            QFrame:hover {
                border: 2px solid palette(highlight);
                background-color: palette(alternate-base);
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # サムネイル表示エリア
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(180, 120)
        self.thumbnail_label.setStyleSheet(
            """
            QLabel {
                border: 1px solid palette(mid);
                border-radius: 4px;
                background-color: palette(base);
            }
        """
        )
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setText("プレビュー生成中...")
        layout.addWidget(self.thumbnail_label)

        # テーマ名
        theme_name = self.theme_data.get("name", Path(self.theme_path).stem)
        self.name_label = QLabel(theme_name)
        self.name_label.setFont(QFont("", 10, QFont.Bold))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        # テーマ情報
        self.theme_data.get("version", "不明")
        self.info_label = QLabel("バージョン: {version}")
        self.info_label.setFont(QFont("", 8))
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # 作成日時
        if "created_at" in self.theme_data:
            self.theme_data["created_at"]
            self.date_label = QLabel("作成: {created_at}")
            self.date_label.setFont(QFont("", 8))
            self.date_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.date_label)

        # ボタンエリア
        button_layout = QHBoxLayout()

        self.select_button = QPushButton("選択")
        self.select_button.clicked.connect(self.on_select_clicked)
        button_layout.addWidget(self.select_button)

        self.delete_button = QPushButton("削除")
        self.delete_button.setStyleSheet("QPushButton { color: red; }")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

    def generate_thumbnail(self):
        """サムネイル生成"""
        try:
            # 簡易的なサムネイル生成（色情報を基に）
            colors = self.theme_data.get("colors", {})
            if colors:
                thumbnail = self.create_color_thumbnail(colors)
                self.thumbnail_label.setPixmap(thumbnail)
            else:
                self.thumbnail_label.setText("プレビュー\n利用不可")

        except Exception as e:
            self.logger.log_error("サムネイル生成エラー: {str(e)}", e)
            self.thumbnail_label.setText("プレビュー\nエラー")

    def create_color_thumbnail(self, colors: Dict[str, str]) -> QPixmap:
        """色情報からサムネイル作成"""
        pixmap = QPixmap(180, 120)
        painter = QPainter(pixmap)

        try:
            # 主要色を抽出
            primary = colors.get("primary", "#0078d4")
            secondary = colors.get("secondary", "#106ebe")
            background = colors.get("background", "#fffff")
            surface = colors.get("surface", "#f5f5f5")
            text_color = colors.get("text", "#000000")
            text_secondary = colors.get("text_secondary", "#666666")

            # 背景色
            painter.fillRect(0, 0, 180, 120, background)

            # プライマリ色のバー（上部）
            painter.fillRect(0, 0, 180, 25, primary)
            # プライマリ色の説明テキスト
            painter.setPen(self._get_contrast_color(primary))
            painter.setFont(QFont("", 7))
            painter.drawText(5, 18, "プライマリ色")

            # セカンダリ色のバー
            painter.fillRect(0, 25, 180, 25, secondary)
            # セカンダリ色の説明テキスト
            painter.setPen(self._get_contrast_color(secondary))
            painter.drawText(5, 43, "セカンダリ色")

            # サーフェス色のエリア
            painter.fillRect(0, 50, 180, 70, surface)

            # テキスト色のサンプル表示
            painter.setPen(text_color)
            painter.setFont(QFont("", 8))
            painter.drawText(10, 65, "テキスト色")

            # セカンダリテキスト色のサンプル
            painter.setPen(text_secondary)
            painter.setFont(QFont("", 7))
            painter.drawText(10, 78, "セカンダリテキスト")

            # 簡単なウィジェット風の描画
            painter.fillRect(10, 85, 50, 20, primary)  # ボタン風
            painter.fillRect(70, 85, 100, 20, background)  # テキストフィールド風

            # ボタンとテキストフィールドの説明
            painter.setPen(self._get_contrast_color(primary))
            painter.setFont(QFont("", 6))
            painter.drawText(12, 98, "ボタン")

            painter.setPen(text_color)
            painter.drawText(72, 98, "テキストフィールド")

        finally:
            painter.end()

        return pixmap

    def _get_contrast_color(self, background_color: str) -> str:
        """背景色に対して適切なコントラストのテキスト色を返す"""
        try:
            # 簡易的なコントラスト計算
            # 16進数カラーをRGBに変換
            if background_color.startswith("#"):
                hex_color = background_color[1:]
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)

                    # 明度計算（簡易版）
                    brightness = (r * 299 + g * 587 + b * 114) / 1000

                    # 明度が高い場合は黒、低い場合は白を使用
                    return "#000000" if brightness > 128 else "#fffff"
        except Exception:
            pass

        # フォールバック
        return "#000000"

    def on_select_clicked(self):
        """選択ボタンクリック処理"""
        self.theme_selected.emit(self.theme_path)

    def on_delete_clicked(self):
        """削除ボタンクリック処理"""
        reply = QMessageBox.question(
            self,
            "テーマ削除確認",
            "テーマ '{self.theme_data.get('name', 'Unknown')}' を削除しますか？\n"
            "この操作は元に戻せません。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.theme_deleted.emit(self.theme_path)


class ThemeLoader(QThread):
    """テーマ読み込み用ワーカースレッド"""

    theme_loaded = Signal(str, dict)  # パス, データ
    loading_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, theme_directory: str):
        super().__init__()
        self.theme_directory = theme_directory
        self.logger = Logger()

    def run(self):
        """テーマファイル読み込み実行"""
        try:
            theme_dir = Path(self.theme_directory)
            if not theme_dir.exists():
                theme_dir.mkdir(parents=True, exist_ok=True)

            # JSONファイルを検索
            for theme_file in theme_dir.glob("*.json"):
                try:
                    with open(theme_file, "r", encoding="utf-8") as f:
                        theme_data = json.load(f)
                    self.theme_loaded.emit(str(theme_file), theme_data)
                except Exception as e:
                    self.logger.log_error(
                        "テーマファイル読み込みエラー: {theme_file}", e
                    )

        except Exception:
            self.error_occurred.emit("テーマディレクトリアクセスエラー: {str(e)}")
        finally:
            self.loading_finished.emit()


class ThemeGallery(QWidget):
    """テーマギャラリーメインウィジェット"""

    theme_selected = Signal(str)  # 選択されたテーマパス

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger()
        self.theme_cards = []
        self.all_themes = []  # 全テーマデータ
        self.filtered_themes = []  # フィルタ後のテーマデータ

        # サービス初期化
        self.import_service = ThemeImportService()

        # デフォルトテーマディレクトリ
        self.theme_directory = os.path.join(
            os.path.expanduser("~"), ".qt_theme_studio", "themes"
        )

        self.setup_ui()
        self.load_themes()

    def setup_ui(self):
        """UIセットアップ"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ヘッダー
        header_layout = QHBoxLayout()

        title_label = QLabel("テーマギャラリー")
        title_label.setFont(QFont("", 14, QFont.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # インポートボタン
        self.import_button = QPushButton("テーマをインポート")
        self.import_button.clicked.connect(self.on_import_clicked)
        header_layout.addWidget(self.import_button)

        # 更新ボタン
        self.refresh_button = QPushButton("更新")
        self.refresh_button.clicked.connect(self.load_themes)
        header_layout.addWidget(self.refresh_button)

        layout.addLayout(header_layout)

        # 検索・フィルターエリア
        filter_layout = QHBoxLayout()

        # 検索ボックス
        search_label = QLabel("検索:")
        filter_layout.addWidget(search_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("テーマ名で検索...")
        self.search_edit.textChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.search_edit)

        # フィルターコンボボックス
        filter_label = QLabel("フィルター:")
        filter_layout.addWidget(filter_label)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            ["すべて", "最近作成", "最近更新", "名前順", "バージョン順"]
        )
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # スクロールエリア
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # テーマカード表示エリア
        self.cards_widget = QWidget()
        self.cards_layout = QGridLayout(self.cards_widget)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll_area.setWidget(self.cards_widget)
        layout.addWidget(self.scroll_area)

        # ステータスラベル
        self.status_label = QLabel("テーマを読み込み中...")
        layout.addWidget(self.status_label)

    def load_themes(self):
        """テーマ読み込み開始"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不定進行
        self.status_label.setText("テーマを読み込み中...")

        # 既存のカードをクリア
        self.clear_theme_cards()

        # ワーカースレッドでテーマ読み込み
        self.theme_loader = ThemeLoader(self.theme_directory)
        self.theme_loader.theme_loaded.connect(self.on_theme_loaded)
        self.theme_loader.loading_finished.connect(self.on_loading_finished)
        self.theme_loader.error_occurred.connect(self.on_loading_error)
        self.theme_loader.start()

    def on_theme_loaded(self, theme_path: str, theme_data: Dict[str, Any]):
        """テーマ読み込み完了処理"""
        self.all_themes.append((theme_path, theme_data))

    def on_loading_finished(self):
        """全テーマ読み込み完了処理"""
        self.progress_bar.setVisible(False)
        self.filtered_themes = self.all_themes.copy()
        self.update_theme_display()

        count = len(self.all_themes)
        self.status_label.setText("{count} 個のテーマが見つかりました")

        self.logger.log_user_action("テーマギャラリー読み込み完了", {"count": count})

    def on_loading_error(self, error_message: str):
        """読み込みエラー処理"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("エラー: {error_message}")

        QMessageBox.warning(
            self,
            "テーマ読み込みエラー",
            "テーマの読み込み中にエラーが発生しました:\n{error_message}",
        )

    def clear_theme_cards(self):
        """テーマカードクリア"""
        for card in self.theme_cards:
            card.setParent(None)
            card.deleteLater()
        self.theme_cards.clear()
        self.all_themes.clear()

    def update_theme_display(self):
        """テーマ表示更新"""
        # 既存のカードをクリア
        for card in self.theme_cards:
            card.setParent(None)
            card.deleteLater()
        self.theme_cards.clear()

        # フィルタ後のテーマでカード作成
        row, col = 0, 0
        max_cols = 4  # 1行あたりの最大カード数

        for theme_path, theme_data in self.filtered_themes:
            card = ThemeCard(theme_path, theme_data)
            card.theme_selected.connect(self.on_theme_selected)
            card.theme_deleted.connect(self.on_theme_deleted)

            self.cards_layout.addWidget(card, row, col)
            self.theme_cards.append(card)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def on_search_changed(self, text: str):
        """検索テキスト変更処理"""
        self.apply_filters()

    def on_filter_changed(self, filter_type: str):
        """フィルター変更処理"""
        self.apply_filters()

    def apply_filters(self):
        """フィルター適用"""
        search_text = self.search_edit.text().lower()
        filter_type = self.filter_combo.currentText()

        # 検索フィルター適用
        if search_text:
            self.filtered_themes = [
                (path, data)
                for path, data in self.all_themes
                if search_text in data.get("name", "").lower()
                or search_text in Path(path).stem.lower()
            ]
        else:
            self.filtered_themes = self.all_themes.copy()

        # ソートフィルター適用
        if filter_type == "最近作成":
            self.filtered_themes.sort(
                key=lambda x: x[1].get("created_at", ""), reverse=True
            )
        elif filter_type == "最近更新":
            self.filtered_themes.sort(
                key=lambda x: x[1].get("updated_at", ""), reverse=True
            )
        elif filter_type == "名前順":
            self.filtered_themes.sort(
                key=lambda x: x[1].get("name", Path(x[0]).stem).lower()
            )
        elif filter_type == "バージョン順":
            self.filtered_themes.sort(
                key=lambda x: x[1].get("version", "0.0.0"), reverse=True
            )

        self.update_theme_display()

        len(self.filtered_themes)
        self.status_label.setText("{count} 個のテーマが表示されています")

    def on_theme_selected(self, theme_path: str):
        """テーマ選択処理"""
        self.theme_selected.emit(theme_path)
        self.logger.log_user_action("テーマ選択", {"path": theme_path})

    def on_theme_deleted(self, theme_path: str):
        """テーマ削除処理"""
        try:
            os.remove(theme_path)
            self.logger.log_user_action("テーマ削除", {"path": theme_path})

            # リストから削除
            self.all_themes = [
                (path, data) for path, data in self.all_themes if path != theme_path
            ]
            self.apply_filters()

            QMessageBox.information(self, "削除完了", "テーマが正常に削除されました。")

        except Exception as e:
            self.logger.log_error("テーマ削除エラー: {str(e)}", e)
            QMessageBox.critical(
                self, "削除エラー", "テーマの削除中にエラーが発生しました:\n{str(e)}"
            )

    def on_import_clicked(self):
        """インポートボタンクリック処理"""
        supported_formats = self.import_service.get_supported_formats()
        format_filter = (
            "テーマファイル (" + " ".join(["*{fmt}" for fmt in supported_formats]) + ")"
        )
        format_filter += ";;JSON ファイル (*.json)"
        format_filter += ";;QSS ファイル (*.qss)"
        format_filter += ";;CSS ファイル (*.css)"
        format_filter += ";;すべてのファイル (*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, "テーマファイルを選択", "", format_filter
        )

        if file_path:
            try:
                # プログレスバー表示
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)
                self.status_label.setText("テーマをインポート中...")

                # ファイルの内容を確認
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)

                # 複数テーマの場合は選択ダイアログを表示
                if isinstance(content, list) and len(content) > 1:
                    selected_themes = self.show_theme_selection_dialog(content)
                    if not selected_themes:
                        return  # ユーザーがキャンセルした場合
                else:
                    # 単一テーマまたは配列の最初のテーマ
                    selected_themes = [
                        content[0] if isinstance(content, list) else content
                    ]

                # 選択されたテーマをインポート
                imported_count = 0
                for theme_data in selected_themes:
                    try:
                        # テーマデータの正規化
                        normalized_theme = self.import_service.normalize_json_theme(
                            theme_data
                        )

                        # インポート検証
                        validation_errors = self.import_service.validate_imported_theme(
                            normalized_theme
                        )
                        if validation_errors:
                            error_msg = (
                                "テーマ '{normalized_theme.get('name', '不明')}' "
                                "に問題があります:\n" + "\n".join(validation_errors)
                            )
                            QMessageBox.warning(self, "テーマ検証警告", error_msg)

                        # テーマファイルを保存
                        self.save_imported_theme(normalized_theme, file_path)
                        imported_count += 1

                    except Exception as e:
                        self.logger.log_error(
                            "テーマ '{theme_data.get('name', '不明')}' "
                            "のインポートエラー: {str(e)}",
                            e,
                        )
                        QMessageBox.warning(
                            self,
                            "インポート警告",
                            "テーマ '{theme_data.get('name', '不明')}' "
                            "のインポートに失敗しました:\n{str(e)}",
                        )

                # ギャラリーを更新
                self.load_themes()

                if imported_count > 0:
                    QMessageBox.information(
                        self,
                        "インポート完了",
                        "{imported_count} 個のテーマが正常にインポートされました。",
                    )
                else:
                    QMessageBox.warning(
                        self, "インポート完了", "インポートされたテーマはありません。"
                    )

            except ImportError as e:
                self.logger.log_error("テーマインポートエラー: {str(e)}", e)
                QMessageBox.critical(
                    self,
                    "インポートエラー",
                    "テーマのインポート中にエラーが発生しました:\n{str(e)}",
                )
            except Exception as e:
                self.logger.log_error("予期しないインポートエラー: {str(e)}", e)
                QMessageBox.critical(
                    self,
                    "予期しないエラー",
                    "予期しないエラーが発生しました:\n{str(e)}",
                )
            finally:
                self.progress_bar.setVisible(False)

    def show_theme_selection_dialog(
        self, themes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        複数テーマの選択ダイアログを表示

        Args:
            themes: テーマのリスト

        Returns:
            選択されたテーマのリスト
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("インポートするテーマを選択")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout()

        # 説明ラベル
        info_label = QLabel(
            "{len(themes)} 個のテーマが見つかりました。"
            "インポートするテーマを選択してください。"
        )
        layout.addWidget(info_label)

        # テーマリスト
        theme_list = QListWidget()
        theme_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        for theme in themes:
            theme.get("display_name", theme.get("name", "不明"))
            description = theme.get("description", "")
            theme.get("version", "")

            item_text = "{name} (v{version})"
            if description:
                item_text += "\n{description}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, theme)
            theme_list.addItem(item)

        layout.addWidget(theme_list)

        # 全選択/全解除ボタン
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("全選択")
        deselect_all_btn = QPushButton("全解除")

        select_all_btn.clicked.connect(lambda: self.select_all_themes(theme_list))
        deselect_all_btn.clicked.connect(lambda: self.deselect_all_themes(theme_list))

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # OK/キャンセルボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        # デフォルトで最初のテーマを選択
        if theme_list.count() > 0:
            theme_list.item(0).setSelected(True)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_items = theme_list.selectedItems()
            return [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]

        return []

    def select_all_themes(self, theme_list: QListWidget):
        """すべてのテーマを選択"""
        for i in range(theme_list.count()):
            theme_list.item(i).setSelected(True)

    def deselect_all_themes(self, theme_list: QListWidget):
        """すべてのテーマの選択を解除"""
        for i in range(theme_list.count()):
            theme_list.item(i).setSelected(False)

    def save_imported_theme(self, theme_data: Dict[str, Any], original_path: str):
        """
        インポートされたテーマを保存

        Args:
            theme_data: テーマデータ
            original_path: 元のファイルパス
        """
        try:
            # テーマディレクトリの確保
            theme_dir = Path(self.theme_directory)
            theme_dir.mkdir(parents=True, exist_ok=True)

            # 保存ファイル名の生成
            theme_name = theme_data["name"]
            safe_name = re.sub(r"[^\w\-_\.]", "_", theme_name)  # 安全なファイル名に変換
            save_path = theme_dir / "{safe_name}.json"

            # 重複チェック
            counter = 1
            while save_path.exists():
                save_path = theme_dir / "{safe_name}_{counter}.json"
                counter += 1

            # JSONファイルとして保存
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(theme_data, f, ensure_ascii=False, indent=2)

            self.logger.log_user_action(
                "インポートテーマ保存",
                {"original": original_path, "saved": str(save_path)},
            )

        except Exception:
            raise ImportError("インポートテーマの保存エラー: {str(e)}")

    def get_theme_directory(self) -> str:
        """テーマディレクトリパス取得"""
        return self.theme_directory

    def set_theme_directory(self, directory: str):
        """テーマディレクトリパス設定"""
        self.theme_directory = directory
        self.load_themes()
