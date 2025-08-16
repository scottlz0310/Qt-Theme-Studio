"""
統合テーマエディター

このモジュールは、Qt-Theme-Studioの統合テーマエディターを実装します。
カラーピッカーのUIを提供し、
直感的なビジュアルインターフェースでテーマプロパティを編集できます。
"""

from typing import Any, Dict, Optional, List, Callable

from ..adapters.qt_adapter import QtAdapter
from ..adapters.theme_adapter import ThemeAdapter
from ..logger import get_logger, LogCategory


class ColorPicker:
    """カラーピッカーコンポーネント
    
    色選択と適用するスタイルの選択を提供します。
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
        self.style_combo: Optional[Any] = None
        self.apply_button: Optional[Any] = None
        self.current_color = self.QtGui.QColor(255, 255, 255)  # デフォルト白色
        self.current_style = "background"  # デフォルトスタイル
        
        # コールバック
        self.color_changed_callback: Optional[Callable[[str, str], None]] = None
        
    def create_widget(self) -> Any:
        """カラーピッカーウィジェットを作成します
        
        Returns:
            QWidget: カラーピッカーウィジェット
        """
        # QGroupBoxを使用してタイトルを表示
        self.widget = self.QtWidgets.QGroupBox("マニュアル編集")
        # よりコンパクトな高さに調整
        self.widget.setMaximumHeight(80)  # 高さを制限（横並びなので高さを削減）
        self.widget.setMinimumHeight(60)   # 最小高さも設定
        layout = self.QtWidgets.QVBoxLayout(self.widget)
        
        # カラーボタン、スタイル選択、適用ボタンを横並びに配置
        color_selection_layout = self.QtWidgets.QHBoxLayout()
        
        # 色ラベル
        color_label = self.QtWidgets.QLabel("色:")
        color_label.setFixedWidth(30)
        
        # カラーボタン
        self.color_button = self.QtWidgets.QPushButton()
        self.color_button.setFixedSize(60, 30)
        self.color_button.setStyleSheet(
            f"background-color: {self.current_color.name()};"
        )
        self.color_button.clicked.connect(self._open_color_dialog)
        
        # スタイル選択ドロップダウン
        style_label = self.QtWidgets.QLabel("適用:")
        style_label.setFixedWidth(40)
        
        self.style_combo = self.QtWidgets.QComboBox()
        self.style_combo.addItems([
            "背景色", "テキスト色", "プライマリ色", "セカンダリ色", 
            "ボーダー色", "アクセント色", "エラー色", "警告色", "成功色"
        ])
        self.style_combo.setCurrentText("背景色")
        self.style_combo.currentTextChanged.connect(self._on_style_changed)
        
        # 適用ボタン
        self.apply_button = self.QtWidgets.QPushButton("確定")
        self.apply_button.clicked.connect(self._apply_color)
        
        # すべての要素を横並びに配置
        color_selection_layout.addWidget(color_label)
        color_selection_layout.addWidget(self.color_button)
        color_selection_layout.addWidget(style_label)
        color_selection_layout.addWidget(self.style_combo)
        color_selection_layout.addWidget(self.apply_button)
        color_selection_layout.addStretch()
        
        layout.addLayout(color_selection_layout)
        
        self.logger.debug("カラーピッカーウィジェットを作成しました", 
                          LogCategory.UI)
        return self.widget
    
    def _apply_color(self) -> None:
        """選択された色とスタイルを適用します"""
        self._notify_color_changed()
    
    def _open_color_dialog(self) -> None:
        """カラーダイアログを開きます"""
        color = self.QtWidgets.QColorDialog.getColor(
            self.current_color, 
            self.parent, 
            "色を選択"
        )
        
        if color.isValid():
            self.set_color(color)
    
    def _on_style_changed(self, style_text: str) -> None:
        """スタイル選択の変更を処理します"""
        # 日本語から英語のスタイル名に変換
        style_mapping = {
            "背景色": "background",
            "テキスト色": "text",
            "プライマリ色": "primary",
            "セカンダリ色": "secondary",
            "ボーダー色": "border",
            "アクセント色": "accent",
            "エラー色": "error",
            "警告色": "warning",
            "成功色": "success"
        }
        
        self.current_style = style_mapping.get(style_text, "background")
        # スタイル変更時は即座に適用せず、適用ボタンで確定
        # self._notify_color_changed() を削除
    
    def _update_ui_from_color(self) -> None:
        """現在の色からUIを更新します"""
        if not self.widget:
            return
        
        # カラーボタンの更新
        if self.color_button:
            self.color_button.setStyleSheet(
                f"background-color: {self.current_color.name()};"
            )
    
    def _notify_color_changed(self) -> None:
        """色変更をコールバックに通知します"""
        if self.color_changed_callback:
            self.color_changed_callback(
                self.current_color.name(), 
                self.current_style
            )
    
    def set_color(self, color: Any) -> None:
        """色を設定します
        
        Args:
            color: QColor オブジェクト
        """
        if isinstance(color, self.QtGui.QColor) and color.isValid():
            self.current_color = color
            self._update_ui_from_color()
            # 色変更時は即座に適用せず、適用ボタンで確定
            # self._notify_color_changed() を削除
    
    def get_color(self) -> str:
        """現在の色を16進値で取得します
        
        Returns:
            str: 16進色値
        """
        return self.current_color.name()
    
    def get_style(self) -> str:
        """現在選択されているスタイルを取得します
        
        Returns:
            str: スタイル名
        """
        return self.current_style
    
    def set_style(self, style: str) -> None:
        """スタイルを設定します
        
        Args:
            style: 設定するスタイル
        """
        self.current_style = style
        
        # スタイル名を日本語に変換してドロップダウンに設定
        style_mapping = {
            "background": "背景色",
            "text": "テキスト色", 
            "primary": "プライマリ色",
            "secondary": "セカンダリ色",
            "border": "ボーダー色",
            "accent": "アクセント色",
            "error": "エラー色",
            "warning": "警告色",
            "success": "成功色"
        }
        
        if style in style_mapping:
            self.style_combo.setCurrentText(style_mapping[style])
    
    def set_color_changed_callback(self, 
                                 callback: Callable[[str, str], None]) -> None:
        """色変更コールバックを設定します
        
        Args:
            callback: 色変更時に呼び出されるコールバック関数
                      引数: (color_hex: str, style: str)
        """
        self.color_changed_callback = callback












class ThemeEditor:
    """統合テーマエディタークラス
    
    カラーピッカーを統合し、
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
        
        # MainWindowへの参照
        self.main_window_reference: Optional[Any] = None
        
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
    
    def set_main_window_reference(self, main_window: Any) -> None:
        """MainWindowへの参照を設定します
        
        Args:
            main_window: MainWindowインスタンス
        """
        self.main_window_reference = main_window
        self.logger.debug("MainWindow参照を設定しました", LogCategory.UI)
    
    def create_widget(self) -> Any:
        """テーマエディターウィジェットを作成します
        
        Returns:
            QWidget: テーマエディターウィジェット
        """
        self.widget = self.QtWidgets.QWidget()
        # カラーピッカーの高さ（80px）に合わせて調整
        self.widget.setMaximumHeight(100)  # カラーピッカー + マージン
        self.widget.setMinimumHeight(80)  # 最小高さも設定
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
        
        # ストレッチを追加（色選択ウィジェットを下に押し下げる）
        content_layout.addStretch()
        
        # カラーピッカーを作成（一番下に配置）
        self.color_picker = ColorPicker(self.qt_modules, self.widget)
        color_widget = self.color_picker.create_widget()
        self.color_picker.set_color_changed_callback(self._on_color_changed)
        content_layout.addWidget(color_widget)
        
        # スクロールエリアにコンテンツを設定
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # リアルタイムプレビュー更新タイマーを設定
        self._setup_preview_update_timer()
        
        self.logger.info("テーマエディターウィジェットを作成しました", 
                          LogCategory.UI)
        return self.widget
    
    def _on_color_changed(self, color: str, style: str) -> None:
        """色変更を処理します
        
        Args:
            color: 変更された色（16進値）
            style: 適用するスタイル
        """
        # 現在選択されている色プロパティを更新
        self.current_theme['colors'][style] = color
        
        # テーマ変更を通知（MainWindowのcurrent_theme_dataも更新される）
        self._notify_theme_changed()
        
        # プレビューコールバックも直接呼び出し（即座に反映）
        self._update_preview_callbacks()
        
        # MainWindowのcurrent_theme_dataも直接更新
        if hasattr(self, 'main_window_reference') and hasattr(self.main_window_reference, 'current_theme_data'):
            main_window = self.main_window_reference
            if hasattr(main_window, 'current_theme_data'):
                if 'colors' not in main_window.current_theme_data:
                    main_window.current_theme_data['colors'] = {}
                main_window.current_theme_data['colors'][style] = color
                
                # MainWindowのプレビューも直接更新
                if hasattr(main_window, 'preview_window_instance'):
                    preview = main_window.preview_window_instance
                    if hasattr(preview, 'update_preview'):
                        preview.update_preview(main_window.current_theme_data)
                
                # テーマが変更されたので未保存状態に設定
                if hasattr(main_window, '_set_theme_saved_state'):
                    main_window._set_theme_saved_state(False)
        
        self.logger.debug(f"色が変更されました: {color}, スタイル: {style}", LogCategory.UI)
    

    
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
            
            # 最初に見つかった有効な色を設定（優先順位付き）
            priority_colors = ['primary', 'background', 'text', 'secondary', 'accent', 'border', 'error', 'warning', 'success']
            
            for style_name in priority_colors:
                if style_name in colors:
                    color_value = colors[style_name]
                    try:
                        # 色を設定
                        self.color_picker.set_color(self.QtGui.QColor(color_value))
                        self.color_picker.set_style(style_name)
                        break  # 最初の有効な色で停止
                    except Exception as e:
                        self.logger.warning(f"色設定に失敗: {style_name}={color_value} - {str(e)}", LogCategory.UI)
                        continue
        
        # テーマ変更を通知
        self._notify_theme_changed()
        
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
            }
        }
        
        # UIを更新
        self.load_theme(self.current_theme)
        
        self.logger.info("テーマをリセットしました", LogCategory.UI)
    
    def set_color_property(self, property_name: str, color_value: str) -> None:
        """色プロパティを設定します
        
        Args:
            property_name: 色プロパティ名（例: 'primary', 'background'）
            color_value: 色の値（16進値、例: '#ff0000'）
        """
        if 'colors' not in self.current_theme:
            self.current_theme['colors'] = {}
        
        # 色プロパティを更新
        self.current_theme['colors'][property_name] = color_value
        
        # カラーピッカーのUIも更新
        if self.color_picker:
            try:
                self.color_picker.set_color(self.QtGui.QColor(color_value))
                self.color_picker.set_style(property_name)
            except Exception as e:
                self.logger.warning(f"カラーピッカーの更新に失敗: {str(e)}", LogCategory.UI)
        
        # テーマ変更を通知
        self._notify_theme_changed()
        
        self.logger.debug(f"色プロパティを設定しました: {property_name}={color_value}", LogCategory.UI)
    
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