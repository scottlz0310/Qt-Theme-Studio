"""
テーマギャラリーUI実装

このモジュールは、保存されたテーマの一覧表示、サムネイル生成、
検索・フィルタリング機能を提供するテーマギャラリーUIを実装します。
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QLabel, QPushButton, QLineEdit,
    QComboBox, QFrame, QSizePolicy, QMessageBox,
    QFileDialog, QProgressBar, QSplitter
)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QPainter, QFont, QIcon

from ..logger import Logger
from ..exceptions import ThemeStudioException
from ..services.import_service import ThemeImportService, ImportError


class ThemeCard(QFrame):
    """テーマカード表示ウィジェット"""
    
    theme_selected = Signal(str)  # テーマパス
    theme_deleted = Signal(str)   # テーマパス
    
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
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 8px;
                background-color: white;
            }
            QFrame:hover {
                border: 2px solid #0078d4;
                background-color: #f5f5f5;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # サムネイル表示エリア
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(180, 120)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                border: 1px solid #dddddd;
                border-radius: 4px;
                background-color: #f9f9f9;
            }
        """)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setText("プレビュー生成中...")
        layout.addWidget(self.thumbnail_label)
        
        # テーマ名
        theme_name = self.theme_data.get('name', Path(self.theme_path).stem)
        self.name_label = QLabel(theme_name)
        self.name_label.setFont(QFont("", 10, QFont.Bold))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        
        # テーマ情報
        version = self.theme_data.get('version', '不明')
        self.info_label = QLabel(f"バージョン: {version}")
        self.info_label.setFont(QFont("", 8))
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # 作成日時
        if 'created_at' in self.theme_data:
            created_at = self.theme_data['created_at']
            self.date_label = QLabel(f"作成: {created_at}")
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
            colors = self.theme_data.get('colors', {})
            if colors:
                thumbnail = self.create_color_thumbnail(colors)
                self.thumbnail_label.setPixmap(thumbnail)
            else:
                self.thumbnail_label.setText("プレビュー\n利用不可")
                
        except Exception as e:
            self.logger.log_error(f"サムネイル生成エラー: {str(e)}", e)
            self.thumbnail_label.setText("プレビュー\nエラー")
            
    def create_color_thumbnail(self, colors: Dict[str, str]) -> QPixmap:
        """色情報からサムネイル作成"""
        pixmap = QPixmap(180, 120)
        painter = QPainter(pixmap)
        
        try:
            # 主要色を抽出
            primary = colors.get('primary', '#0078d4')
            secondary = colors.get('secondary', '#106ebe')
            background = colors.get('background', '#ffffff')
            surface = colors.get('surface', '#f5f5f5')
            
            # 背景色
            painter.fillRect(0, 0, 180, 120, background)
            
            # プライマリ色のバー
            painter.fillRect(0, 0, 180, 30, primary)
            
            # セカンダリ色のバー
            painter.fillRect(0, 30, 180, 30, secondary)
            
            # サーフェス色のエリア
            painter.fillRect(0, 60, 180, 60, surface)
            
            # 簡単なウィジェット風の描画
            painter.fillRect(10, 70, 50, 20, primary)  # ボタン風
            painter.fillRect(70, 70, 100, 20, background)  # テキストフィールド風
            
        finally:
            painter.end()
            
        return pixmap
        
    def on_select_clicked(self):
        """選択ボタンクリック処理"""
        self.theme_selected.emit(self.theme_path)
        
    def on_delete_clicked(self):
        """削除ボタンクリック処理"""
        reply = QMessageBox.question(
            self, 
            "テーマ削除確認",
            f"テーマ '{self.theme_data.get('name', 'Unknown')}' を削除しますか？\n"
            "この操作は元に戻せません。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
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
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                    self.theme_loaded.emit(str(theme_file), theme_data)
                except Exception as e:
                    self.logger.log_error(f"テーマファイル読み込みエラー: {theme_file}", e)
                    
        except Exception as e:
            self.error_occurred.emit(f"テーマディレクトリアクセスエラー: {str(e)}")
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
            os.path.expanduser("~"), 
            ".qt_theme_studio", 
            "themes"
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
        self.import_button.clicked.connect(self.import_theme)
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
        self.filter_combo.addItems([
            "すべて",
            "最近作成",
            "最近更新",
            "名前順",
            "バージョン順"
        ])
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
        self.status_label.setText(f"{count} 個のテーマが見つかりました")
        
        self.logger.log_user_action("テーマギャラリー読み込み完了", {"count": count})
        
    def on_loading_error(self, error_message: str):
        """読み込みエラー処理"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"エラー: {error_message}")
        
        QMessageBox.warning(
            self,
            "テーマ読み込みエラー",
            f"テーマの読み込み中にエラーが発生しました:\n{error_message}"
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
                (path, data) for path, data in self.all_themes
                if search_text in data.get('name', '').lower() or
                   search_text in Path(path).stem.lower()
            ]
        else:
            self.filtered_themes = self.all_themes.copy()
            
        # ソートフィルター適用
        if filter_type == "最近作成":
            self.filtered_themes.sort(
                key=lambda x: x[1].get('created_at', ''), 
                reverse=True
            )
        elif filter_type == "最近更新":
            self.filtered_themes.sort(
                key=lambda x: x[1].get('updated_at', ''), 
                reverse=True
            )
        elif filter_type == "名前順":
            self.filtered_themes.sort(
                key=lambda x: x[1].get('name', Path(x[0]).stem).lower()
            )
        elif filter_type == "バージョン順":
            self.filtered_themes.sort(
                key=lambda x: x[1].get('version', '0.0.0'),
                reverse=True
            )
            
        self.update_theme_display()
        
        count = len(self.filtered_themes)
        self.status_label.setText(f"{count} 個のテーマが表示されています")
        
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
                (path, data) for path, data in self.all_themes 
                if path != theme_path
            ]
            self.apply_filters()
            
            QMessageBox.information(
                self,
                "削除完了",
                "テーマが正常に削除されました。"
            )
            
        except Exception as e:
            self.logger.log_error(f"テーマ削除エラー: {str(e)}", e)
            QMessageBox.critical(
                self,
                "削除エラー",
                f"テーマの削除中にエラーが発生しました:\n{str(e)}"
            )
            
    def import_theme(self):
        """テーマインポート"""
        # サポートされる形式のフィルター作成
        supported_formats = self.import_service.get_supported_formats()
        format_filter = "テーマファイル (" + " ".join([f"*{fmt}" for fmt in supported_formats]) + ")"
        format_filter += ";;JSON ファイル (*.json)"
        format_filter += ";;QSS ファイル (*.qss)"
        format_filter += ";;CSS ファイル (*.css)"
        format_filter += ";;すべてのファイル (*)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "テーマファイルを選択",
            "",
            format_filter
        )
        
        if file_path:
            try:
                # プログレスバー表示
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)
                self.status_label.setText("テーマをインポート中...")
                
                # テーマインポート実行
                imported_theme = self.import_service.import_theme(file_path)
                
                # インポート検証
                validation_errors = self.import_service.validate_imported_theme(imported_theme)
                if validation_errors:
                    error_msg = "インポートされたテーマに問題があります:\n" + "\n".join(validation_errors)
                    QMessageBox.warning(self, "テーマ検証警告", error_msg)
                
                # テーマファイルを保存
                self.save_imported_theme(imported_theme, file_path)
                
                # ギャラリーを更新
                self.load_themes()
                
                QMessageBox.information(
                    self,
                    "インポート完了",
                    f"テーマ '{imported_theme['name']}' が正常にインポートされました。"
                )
                
            except ImportError as e:
                self.logger.log_error(f"テーマインポートエラー: {str(e)}", e)
                QMessageBox.critical(
                    self,
                    "インポートエラー",
                    f"テーマのインポート中にエラーが発生しました:\n{str(e)}"
                )
            except Exception as e:
                self.logger.log_error(f"予期しないインポートエラー: {str(e)}", e)
                QMessageBox.critical(
                    self,
                    "予期しないエラー",
                    f"予期しないエラーが発生しました:\n{str(e)}"
                )
            finally:
                self.progress_bar.setVisible(False)
                
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
            theme_name = theme_data['name']
            safe_name = re.sub(r'[^\w\-_\.]', '_', theme_name)  # 安全なファイル名に変換
            save_path = theme_dir / f"{safe_name}.json"
            
            # 重複チェック
            counter = 1
            while save_path.exists():
                save_path = theme_dir / f"{safe_name}_{counter}.json"
                counter += 1
                
            # JSONファイルとして保存
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, ensure_ascii=False, indent=2)
                
            self.logger.log_user_action(
                "インポートテーマ保存", 
                {"original": original_path, "saved": str(save_path)}
            )
            
        except Exception as e:
            raise ImportError(f"インポートテーマの保存エラー: {str(e)}")
                
    def get_theme_directory(self) -> str:
        """テーマディレクトリパス取得"""
        return self.theme_directory
        
    def set_theme_directory(self, directory: str):
        """テーマディレクトリパス設定"""
        self.theme_directory = directory
        self.load_themes()