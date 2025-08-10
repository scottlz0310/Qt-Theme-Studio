"""
テーマ管理コントローラー

このモジュールは、テーマの作成、読み込み、保存、編集操作を管理し、
QUndoStackを使用したUndo/Redo機能を提供します。
プレビューとの同期更新機能も含まれています。
"""

import logging
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path

from ..adapters.qt_adapter import QtAdapter, QtFrameworkNotFoundError
from ..adapters.theme_adapter import ThemeAdapter, ThemeManagerError
from ..logger import get_logger, LogCategory


class ThemePropertyChangeCommand:
    """テーマプロパティ変更コマンド
    
    QUndoCommandを継承し、テーマプロパティの変更操作を
    Undo/Redo可能なコマンドとして実装します。
    """
    
    def __init__(self, theme_controller: 'ThemeController', property_path: str, 
                 old_value: Any, new_value: Any, description: str = ""):
        """コマンドを初期化する
        
        Args:
            theme_controller: テーマコントローラーのインスタンス
            property_path: 変更するプロパティのパス（例: "colors.primary"）
            old_value: 変更前の値
            new_value: 変更後の値
            description: 操作の説明
        """
        # QUndoCommandは後で初期化するため、まず基本情報を保存
        self.theme_controller = theme_controller
        self.property_path = property_path
        self.old_value = old_value
        self.new_value = new_value
        self.description = description or f"プロパティ変更: {property_path}"
        self.logger = get_logger()
        
        # QUndoCommandの初期化は後で行う
        self._undo_command = None
    
    def initialize_qt_command(self, QUndoCommand):
        """QtのQUndoCommandを初期化する
        
        Args:
            QUndoCommand: QtのQUndoCommandクラス
        """
        class QtThemePropertyChangeCommand(QUndoCommand):
            def __init__(self, theme_command):
                super().__init__(theme_command.description)
                self.theme_command = theme_command
            
            def redo(self):
                self.theme_command.redo()
            
            def undo(self):
                self.theme_command.undo()
        
        self._undo_command = QtThemePropertyChangeCommand(self)
        return self._undo_command
    
    def redo(self):
        """変更を実行する（Redo操作）"""
        try:
            self._set_property_value(self.property_path, self.new_value)
            
            # プロパティ変更シグナルを発信
            if self.theme_controller._qt_object:
                self.theme_controller._qt_object.property_changed.emit(
                    self.property_path, self.old_value, self.new_value
                )
            
            self.logger.log_user_action(
                f"テーマプロパティ変更（Redo）",
                {
                    "property": self.property_path,
                    "old_value": str(self.old_value),
                    "new_value": str(self.new_value)
                }
            )
        except Exception as e:
            self.logger.error(f"Redo操作に失敗しました: {str(e)}", LogCategory.ERROR)
    
    def undo(self):
        """変更を取り消す（Undo操作）"""
        try:
            self._set_property_value(self.property_path, self.old_value)
            
            # プロパティ変更シグナルを発信
            if self.theme_controller._qt_object:
                self.theme_controller._qt_object.property_changed.emit(
                    self.property_path, self.new_value, self.old_value
                )
            
            self.logger.log_user_action(
                f"テーマプロパティ変更（Undo）",
                {
                    "property": self.property_path,
                    "old_value": str(self.new_value),
                    "new_value": str(self.old_value)
                }
            )
        except Exception as e:
            self.logger.error(f"Undo操作に失敗しました: {str(e)}", LogCategory.ERROR)
    
    def _set_property_value(self, property_path: str, value: Any):
        """プロパティ値を設定する
        
        Args:
            property_path: プロパティのパス（例: "colors.primary"）
            value: 設定する値
        """
        if not self.theme_controller.current_theme:
            raise ValueError("現在のテーマが設定されていません")
        
        # プロパティパスを分割
        path_parts = property_path.split('.')
        
        # テーマデータの該当箇所を取得
        current_data = self.theme_controller.current_theme
        for part in path_parts[:-1]:
            if part not in current_data:
                current_data[part] = {}
            current_data = current_data[part]
        
        # 値を設定
        current_data[path_parts[-1]] = value
        
        # プレビューの更新を通知
        self.theme_controller._notify_theme_changed()


class ThemeController:
    """テーマ管理コントローラー
    
    テーマの作成、読み込み、保存、編集操作を管理し、
    QUndoStackを使用したUndo/Redo機能を提供します。
    プレビューとの同期更新機能も含まれています。
    """
    
    def __init__(self):
        """テーマコントローラーを初期化する"""
        self.logger = get_logger()
        self.qt_adapter = QtAdapter()
        self.theme_adapter = ThemeAdapter()
        
        # 現在のテーマデータ
        self.current_theme: Optional[Dict[str, Any]] = None
        self.current_theme_path: Optional[Path] = None
        
        # Qt関連の初期化
        self._undo_stack = None
        self._qt_modules = None
        self._qt_object = None  # QObjectベースのシグナル/スロット用
        self._initialize_qt_components()
        
        # 変更通知のコールバック
        self._theme_change_callbacks: List[Callable] = []
        self._preview_update_callbacks: List[Callable] = []
        self._undo_redo_callbacks: List[Callable] = []
        
        # プレビュー更新の遅延処理用
        self._preview_update_timer = None
        self._pending_preview_update = False
        
        self.logger.info("テーマコントローラーを初期化しました", LogCategory.SYSTEM)
    
    def _initialize_qt_components(self):
        """Qt関連のコンポーネントを初期化する"""
        try:
            self._qt_modules = self.qt_adapter.get_qt_modules()
            QtWidgets = self._qt_modules['QtWidgets']
            QtCore = self._qt_modules['QtCore']
            
            # QUndoStackを初期化（最大50回の操作履歴）
            self._undo_stack = QtWidgets.QUndoStack()
            self._undo_stack.setUndoLimit(50)
            # 初期化時に履歴をクリア
            self._undo_stack.clear()
            
            # QObjectベースのシグナル/スロット用オブジェクトを作成
            class ThemeControllerSignals(QtCore.QObject):
                # シグナル定義
                theme_changed = QtCore.Signal(dict)
                property_changed = QtCore.Signal(str, object, object)  # path, old_value, new_value
                undo_executed = QtCore.Signal(str)  # undo_text
                redo_executed = QtCore.Signal(str)  # redo_text
                preview_update_requested = QtCore.Signal()
            
            self._qt_object = ThemeControllerSignals()
            
            # プレビュー更新用タイマーを初期化
            self._preview_update_timer = QtCore.QTimer()
            self._preview_update_timer.setSingleShot(True)
            self._preview_update_timer.timeout.connect(self._execute_preview_update)
            
            # UndoStackのシグナルに接続
            self._undo_stack.indexChanged.connect(self._on_undo_stack_changed)
            
            self.logger.info("Qt関連コンポーネントを初期化しました", LogCategory.SYSTEM)
            
        except QtFrameworkNotFoundError as e:
            self.logger.error(f"Qtフレームワークの初期化に失敗しました: {str(e)}", LogCategory.ERROR)
            raise
        except Exception as e:
            self.logger.error(f"Qt関連コンポーネントの初期化に失敗しました: {str(e)}", LogCategory.ERROR)
            raise
    
    def create_new_theme(self, theme_name: str = "新しいテーマ") -> Dict[str, Any]:
        """新規テーマを作成する
        
        Args:
            theme_name: テーマ名
            
        Returns:
            Dict[str, Any]: 作成されたテーマデータ
        """
        try:
            # 新しいテーマデータを作成
            new_theme = {
                "name": theme_name,
                "version": "1.0.0",
                "type": "custom",
                "colors": {
                    "primary": "#3498db",
                    "secondary": "#2ecc71",
                    "background": "#ffffff",
                    "surface": "#f8f9fa",
                    "text": "#2c3e50",
                    "text_secondary": "#7f8c8d",
                    "border": "#dee2e6",
                    "error": "#e74c3c",
                    "warning": "#f39c12",
                    "info": "#3498db",
                    "success": "#27ae60"
                },
                "fonts": {
                    "default": {
                        "family": "Arial",
                        "size": 10,
                        "weight": "normal"
                    },
                    "heading": {
                        "family": "Arial",
                        "size": 12,
                        "weight": "bold"
                    }
                },
                "sizes": {
                    "border_radius": 4,
                    "border_width": 1,
                    "padding": 8,
                    "margin": 4
                },
                "metadata": {
                    "created_at": self._get_current_timestamp(),
                    "modified_at": self._get_current_timestamp(),
                    "author": "Qt-Theme-Studio",
                    "description": f"{theme_name}の説明"
                }
            }
            
            # 現在のテーマとして設定
            self.current_theme = new_theme
            self.current_theme_path = None
            
            # 操作履歴をクリア（新しいテーマなので）
            self.clear_undo_history()
            
            self.logger.log_theme_operation("新規テーマ作成", theme_name)
            self.logger.log_user_action("新規テーマ作成", {"theme_name": theme_name})
            
            # 変更通知
            self._notify_theme_changed()
            
            return new_theme
            
        except Exception as e:
            self.logger.error(f"新規テーマの作成に失敗しました: {str(e)}", LogCategory.ERROR)
            raise
    
    def load_theme(self, theme_path: Union[str, Path]) -> Dict[str, Any]:
        """テーマファイルを読み込む
        
        Args:
            theme_path: テーマファイルのパス
            
        Returns:
            Dict[str, Any]: 読み込まれたテーマデータ
        """
        try:
            theme_path = Path(theme_path)
            
            # テーマアダプターを使用してテーマを読み込み
            theme_data = self.theme_adapter.load_theme(theme_path)
            
            # 現在のテーマとして設定
            self.current_theme = theme_data
            self.current_theme_path = theme_path
            
            # 操作履歴をクリア（新しいテーマを開いたので）
            self.clear_undo_history()
            
            theme_name = theme_data.get('name', theme_path.stem)
            self.logger.log_theme_operation("テーマ読み込み", theme_name, file_path=str(theme_path))
            self.logger.log_user_action("テーマ読み込み", {
                "theme_name": theme_name,
                "file_path": str(theme_path)
            })
            
            # 変更通知
            self._notify_theme_changed()
            
            return theme_data
            
        except Exception as e:
            self.logger.error(f"テーマの読み込みに失敗しました: {str(e)}", LogCategory.ERROR)
            raise
    
    def save_theme(self, theme_path: Optional[Union[str, Path]] = None) -> bool:
        """テーマファイルを保存する
        
        Args:
            theme_path: 保存先のパス（Noneの場合は現在のパスを使用）
            
        Returns:
            bool: 保存が成功した場合True
        """
        try:
            if not self.current_theme:
                raise ValueError("保存するテーマが設定されていません")
            
            # 保存パスの決定
            if theme_path:
                save_path = Path(theme_path)
                self.current_theme_path = save_path
            elif self.current_theme_path:
                save_path = self.current_theme_path
            else:
                raise ValueError("保存先のパスが指定されていません")
            
            # メタデータの更新
            if 'metadata' not in self.current_theme:
                self.current_theme['metadata'] = {}
            self.current_theme['metadata']['modified_at'] = self._get_current_timestamp()
            
            # テーマアダプターを使用してテーマを保存
            success = self.theme_adapter.save_theme(self.current_theme, save_path)
            
            if success:
                theme_name = self.current_theme.get('name', 'Unnamed')
                self.logger.log_theme_operation("テーマ保存", theme_name, file_path=str(save_path))
                self.logger.log_user_action("テーマ保存", {
                    "theme_name": theme_name,
                    "file_path": str(save_path)
                })
            
            return success
            
        except Exception as e:
            self.logger.error(f"テーマの保存に失敗しました: {str(e)}", LogCategory.ERROR)
            raise
    
    def change_theme_property(self, property_path: str, new_value: Any, 
                            description: str = "") -> bool:
        """テーマプロパティを変更する（Undo/Redo対応）
        
        Args:
            property_path: 変更するプロパティのパス（例: "colors.primary"）
            new_value: 新しい値
            description: 操作の説明
            
        Returns:
            bool: 変更が成功した場合True
        """
        try:
            if not self.current_theme:
                raise ValueError("現在のテーマが設定されていません")
            
            # 現在の値を取得
            old_value = self._get_property_value(property_path)
            
            # 値が同じ場合は何もしない
            if old_value == new_value:
                return True
            
            # 変更コマンドを作成
            command = ThemePropertyChangeCommand(
                self, property_path, old_value, new_value, description
            )
            
            # QtのQUndoCommandを初期化
            QtWidgets = self._qt_modules['QtWidgets']
            qt_command = command.initialize_qt_command(QtWidgets.QUndoCommand)
            
            # コマンドをUndoStackに追加（自動的にredo()が呼ばれる）
            self._undo_stack.push(qt_command)
            
            self.logger.log_user_action("テーマプロパティ変更", {
                "property": property_path,
                "old_value": str(old_value),
                "new_value": str(new_value),
                "description": description
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"テーマプロパティの変更に失敗しました: {str(e)}", LogCategory.ERROR)
            return False
    
    def undo_last_action(self) -> bool:
        """最後の操作を取り消す
        
        Returns:
            bool: Undo操作が成功した場合True
        """
        try:
            if not self._undo_stack or not self._undo_stack.canUndo():
                self.logger.info("取り消し可能な操作がありません", LogCategory.USER_ACTION)
                return False
            
            undo_text = self._undo_stack.undoText()
            self._undo_stack.undo()
            
            self.logger.log_user_action("Undo操作実行", {
                "undo_text": undo_text,
                "can_redo": self._undo_stack.canRedo()
            })
            
            # Undoシグナルを発信
            if self._qt_object:
                self._qt_object.undo_executed.emit(undo_text)
            
            # Undo/Redoコールバックを実行
            self._notify_undo_redo_callbacks("undo", undo_text)
            
            # プレビュー更新をスケジュール
            self._schedule_preview_update()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Undo操作に失敗しました: {str(e)}", LogCategory.ERROR)
            return False
    
    def redo_last_action(self) -> bool:
        """最後に取り消した操作を再実行する
        
        Returns:
            bool: Redo操作が成功した場合True
        """
        try:
            if not self._undo_stack or not self._undo_stack.canRedo():
                self.logger.info("再実行可能な操作がありません", LogCategory.USER_ACTION)
                return False
            
            redo_text = self._undo_stack.redoText()
            self._undo_stack.redo()
            
            self.logger.log_user_action("Redo操作実行", {
                "redo_text": redo_text,
                "can_undo": self._undo_stack.canUndo()
            })
            
            # Redoシグナルを発信
            if self._qt_object:
                self._qt_object.redo_executed.emit(redo_text)
            
            # Undo/Redoコールバックを実行
            self._notify_undo_redo_callbacks("redo", redo_text)
            
            # プレビュー更新をスケジュール
            self._schedule_preview_update()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Redo操作に失敗しました: {str(e)}", LogCategory.ERROR)
            return False
    
    def clear_undo_history(self) -> None:
        """操作履歴をクリアする"""
        try:
            if self._undo_stack:
                self._undo_stack.clear()
                self.logger.log_user_action("操作履歴クリア")
                
        except Exception as e:
            self.logger.error(f"操作履歴のクリアに失敗しました: {str(e)}", LogCategory.ERROR)
    
    def get_undo_history_info(self) -> Dict[str, Any]:
        """操作履歴の情報を取得する
        
        Returns:
            Dict[str, Any]: 操作履歴の情報
        """
        if not self._undo_stack:
            return {
                "can_undo": False,
                "can_redo": False,
                "undo_text": "",
                "redo_text": "",
                "count": 0,
                "index": 0,
                "limit": 0
            }
        
        return {
            "can_undo": self._undo_stack.canUndo(),
            "can_redo": self._undo_stack.canRedo(),
            "undo_text": self._undo_stack.undoText(),
            "redo_text": self._undo_stack.redoText(),
            "count": self._undo_stack.count(),
            "index": self._undo_stack.index(),
            "limit": self._undo_stack.undoLimit()
        }
    
    def add_theme_change_callback(self, callback: Callable) -> None:
        """テーマ変更通知のコールバックを追加する
        
        Args:
            callback: テーマが変更された時に呼び出される関数
        """
        if callback not in self._theme_change_callbacks:
            self._theme_change_callbacks.append(callback)
    
    def remove_theme_change_callback(self, callback: Callable) -> None:
        """テーマ変更通知のコールバックを削除する
        
        Args:
            callback: 削除するコールバック関数
        """
        if callback in self._theme_change_callbacks:
            self._theme_change_callbacks.remove(callback)
    
    def add_preview_update_callback(self, callback: Callable) -> None:
        """プレビュー更新通知のコールバックを追加する
        
        Args:
            callback: プレビューが更新される時に呼び出される関数
        """
        if callback not in self._preview_update_callbacks:
            self._preview_update_callbacks.append(callback)
    
    def remove_preview_update_callback(self, callback: Callable) -> None:
        """プレビュー更新通知のコールバックを削除する
        
        Args:
            callback: 削除するコールバック関数
        """
        if callback in self._preview_update_callbacks:
            self._preview_update_callbacks.remove(callback)
    
    def add_undo_redo_callback(self, callback: Callable) -> None:
        """Undo/Redo操作通知のコールバックを追加する
        
        Args:
            callback: Undo/Redo操作が実行された時に呼び出される関数
                     callback(operation: str, description: str)
        """
        if callback not in self._undo_redo_callbacks:
            self._undo_redo_callbacks.append(callback)
    
    def remove_undo_redo_callback(self, callback: Callable) -> None:
        """Undo/Redo操作通知のコールバックを削除する
        
        Args:
            callback: 削除するコールバック関数
        """
        if callback in self._undo_redo_callbacks:
            self._undo_redo_callbacks.remove(callback)
    
    def _notify_theme_changed(self) -> None:
        """テーマ変更をすべてのコールバックに通知する"""
        for callback in self._theme_change_callbacks:
            try:
                callback(self.current_theme)
            except Exception as e:
                self.logger.error(f"テーマ変更コールバックでエラーが発生しました: {str(e)}", LogCategory.ERROR)
        
        # Qtシグナルも発信
        if self._qt_object and self.current_theme:
            self._qt_object.theme_changed.emit(self.current_theme)
        
        # プレビュー更新もスケジュール
        self._schedule_preview_update()
    
    def _notify_preview_update_callbacks(self) -> None:
        """プレビュー更新をすべてのコールバックに通知する"""
        for callback in self._preview_update_callbacks:
            try:
                callback(self.current_theme)
            except Exception as e:
                self.logger.error(f"プレビュー更新コールバックでエラーが発生しました: {str(e)}", LogCategory.ERROR)
    
    def _notify_undo_redo_callbacks(self, operation: str, description: str) -> None:
        """Undo/Redo操作をすべてのコールバックに通知する
        
        Args:
            operation: 操作タイプ ("undo" または "redo")
            description: 操作の説明
        """
        for callback in self._undo_redo_callbacks:
            try:
                callback(operation, description)
            except Exception as e:
                self.logger.error(f"Undo/Redoコールバックでエラーが発生しました: {str(e)}", LogCategory.ERROR)
    
    def _schedule_preview_update(self) -> None:
        """プレビュー更新をスケジュールする（デバウンス処理）"""
        if not self._preview_update_timer:
            return
        
        self._pending_preview_update = True
        # 100msの遅延でプレビュー更新を実行（デバウンス処理）
        self._preview_update_timer.start(100)
    
    def _execute_preview_update(self) -> None:
        """プレビュー更新を実行する"""
        if not self._pending_preview_update:
            return
        
        self._pending_preview_update = False
        
        try:
            # プレビュー更新コールバックを実行
            self._notify_preview_update_callbacks()
            
            # Qtシグナルを発信
            if self._qt_object:
                self._qt_object.preview_update_requested.emit()
            
            self.logger.debug("プレビュー更新を実行しました", LogCategory.UI)
            
        except Exception as e:
            self.logger.error(f"プレビュー更新の実行に失敗しました: {str(e)}", LogCategory.ERROR)
    
    def _on_undo_stack_changed(self, index: int) -> None:
        """UndoStackのインデックス変更時に呼ばれるスロット
        
        Args:
            index: 新しいインデックス
        """
        try:
            # プレビュー更新をスケジュール
            self._schedule_preview_update()
            
            self.logger.debug(f"UndoStackインデックスが変更されました: {index}", LogCategory.SYSTEM)
            
        except Exception as e:
            self.logger.error(f"UndoStack変更処理でエラーが発生しました: {str(e)}", LogCategory.ERROR)
    
    def _get_property_value(self, property_path: str) -> Any:
        """プロパティ値を取得する
        
        Args:
            property_path: プロパティのパス（例: "colors.primary"）
            
        Returns:
            Any: プロパティの値
        """
        if not self.current_theme:
            raise ValueError("現在のテーマが設定されていません")
        
        # プロパティパスを分割
        path_parts = property_path.split('.')
        
        # テーマデータの該当箇所を取得
        current_data = self.current_theme
        for part in path_parts:
            if isinstance(current_data, dict) and part in current_data:
                current_data = current_data[part]
            else:
                return None
        
        return current_data
    
    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得する
        
        Returns:
            str: ISO形式のタイムスタンプ
        """
        import datetime
        return datetime.datetime.now().isoformat()
    
    @property
    def has_current_theme(self) -> bool:
        """現在のテーマが設定されているかどうかを返す
        
        Returns:
            bool: テーマが設定されている場合True
        """
        return self.current_theme is not None
    
    @property
    def is_theme_modified(self) -> bool:
        """テーマが変更されているかどうかを返す
        
        Returns:
            bool: テーマが変更されている場合True
        """
        if not self._undo_stack:
            return False
        return not self._undo_stack.isClean()
    
    @property
    def undo_stack(self):
        """QUndoStackインスタンスを返す（UIでの使用のため）
        
        Returns:
            QUndoStack: 操作履歴管理用のUndoStack
        """
        return self._undo_stack
    
    @property
    def signals(self):
        """Qtシグナルオブジェクトを返す（UIでの使用のため）
        
        Returns:
            ThemeControllerSignals: シグナル/スロット用のQObject
        """
        return self._qt_object
    
    def force_preview_update(self) -> None:
        """プレビューの即座更新を強制実行する"""
        try:
            if self._preview_update_timer and self._preview_update_timer.isActive():
                self._preview_update_timer.stop()
            
            # 強制更新の場合はpending状態を設定してから実行
            self._pending_preview_update = True
            self._execute_preview_update()
            
        except Exception as e:
            self.logger.error(f"プレビューの強制更新に失敗しました: {str(e)}", LogCategory.ERROR)
    
    def get_preview_update_status(self) -> Dict[str, Any]:
        """プレビュー更新の状態を取得する
        
        Returns:
            Dict[str, Any]: プレビュー更新の状態情報
        """
        return {
            "pending_update": self._pending_preview_update,
            "timer_active": self._preview_update_timer.isActive() if self._preview_update_timer else False,
            "callback_count": len(self._preview_update_callbacks)
        }