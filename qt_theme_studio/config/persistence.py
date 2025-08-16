"""
設定永続化機能

このモジュールは、QSettingsを使用したウィンドウ状態の保存・復元機能と
ユーザー設定のデフォルト値管理を提供します。
"""

from typing import Any, Dict, Optional
import logging

from ..adapters.qt_adapter import QtAdapter


class SettingsManager:
    """設定永続化管理クラス

    QSettingsを使用してウィンドウ状態、レイアウト設定、ユーザー設定の
    永続化を行います。
    """

    def __init__(
        self, organization: str = "QtThemeStudio", application: str = "Settings"
    ):
        """SettingsManagerを初期化する

        Args:
            organization (str): 組織名（デフォルト: "QtThemeStudio"）
            application (str): アプリケーション名（デフォルト: "Settings"）
        """
        self.logger = logging.getLogger(__name__)
        self._qt_adapter = QtAdapter()

        # QSettingsインスタンスの初期化
        try:
            qt_modules = self._qt_adapter.get_qt_modules()
            QtCore = qt_modules["QtCore"]
            self._settings = QtCore.QSettings(organization, application)
            self.logger.info("QSettingsを初期化しました: {organization}/{application}")
        except Exception:
            self.logger.error("QSettingsの初期化に失敗しました: {str()}")
            raise

    def save_window_state(self, window) -> None:
        """ウィンドウ状態を保存する

        Args:
            window: QMainWindowインスタンス
        """
        try:
            # ウィンドウのジオメトリを保存
            self._settings.setValue("window/geometry", window.saveGeometry())

            # ウィンドウの状態（ツールバー、ドック等）を保存
            self._settings.setValue("window/windowState", window.saveState())

            # 最大化状態を保存
            self._settings.setValue("window/maximized", window.isMaximized())

            # 設定を同期
            self._settings.sync()

            self.logger.info("ウィンドウ状態を保存しました")

        except Exception:
            self.logger.error("ウィンドウ状態の保存に失敗しました: {str()}")
            raise

    def restore_window_state(self, window) -> bool:
        """ウィンドウ状態を復元する

        Args:
            window: QMainWindowインスタンス

        Returns:
            bool: 復元に成功した場合True
        """
        try:
            # ジオメトリの復元
            geometry = self._settings.value("window/geometry")
            if geometry:
                window.restoreGeometry(geometry)
                self.logger.debug("ウィンドウジオメトリを復元しました")

            # ウィンドウ状態の復元
            window_state = self._settings.value("window/windowState")
            if window_state:
                window.restoreState(window_state)
                self.logger.debug("ウィンドウ状態を復元しました")

            # 最大化状態の復元
            maximized = self._settings.value("window/maximized", False, type=bool)
            if maximized:
                window.showMaximized()
                self.logger.debug("ウィンドウを最大化状態で復元しました")

            self.logger.info("ウィンドウ状態の復元が完了しました")
            return True

        except Exception:
            self.logger.error("ウィンドウ状態の復元に失敗しました: {str()}")
            return False

    def save_splitter_state(self, splitter, name: str) -> None:
        """スプリッターの状態を保存する

        Args:
            splitter: QSplitterインスタンス
            name (str): スプリッターの識別名
        """
        try:
            self._settings.setValue("splitters/{name}", splitter.saveState())
            self._settings.sync()
            self.logger.debug("スプリッター状態を保存しました: {name}")
        except Exception:
            self.logger.error("スプリッター状態の保存に失敗しました ({name}): {str()}")

    def restore_splitter_state(self, splitter, name: str) -> bool:
        """スプリッターの状態を復元する

        Args:
            splitter: QSplitterインスタンス
            name (str): スプリッターの識別名

        Returns:
            bool: 復元に成功した場合True
        """
        try:
            state = self._settings.value("splitters/{name}")
            if state:
                splitter.restoreState(state)
                self.logger.debug("スプリッター状態を復元しました: {name}")
                return True
            return False
        except Exception:
            self.logger.error("スプリッター状態の復元に失敗しました ({name}): {str()}")
            return False

    def save_dock_state(self, main_window) -> None:
        """ドックウィジェットの状態を保存する

        Args:
            main_window: QMainWindowインスタンス
        """
        try:
            # ドックウィジェットの状態を保存
            dock_state = main_window.saveState()
            self._settings.setValue("docks/state", dock_state)

            # 各ドックウィジェットの可視性を保存
            for dock in main_window.findChildren(main_window.__class__.__bases__[0]):
                if hasattr(dock, "objectName") and dock.objectName():
                    dock.objectName()
                    self._settings.setValue(
                        "docks/{dock_name}/visible", dock.isVisible()
                    )
                    self._settings.setValue(
                        "docks/{dock_name}/floating", dock.isFloating()
                    )

            self._settings.sync()
            self.logger.info("ドックウィジェット状態を保存しました")

        except Exception:
            self.logger.error("ドックウィジェット状態の保存に失敗しました: {str()}")

    def restore_dock_state(self, main_window) -> bool:
        """ドックウィジェットの状態を復元する

        Args:
            main_window: QMainWindowインスタンス

        Returns:
            bool: 復元に成功した場合True
        """
        try:
            # ドックウィジェットの状態を復元
            dock_state = self._settings.value("docks/state")
            if dock_state:
                main_window.restoreState(dock_state)
                self.logger.debug("ドックウィジェット状態を復元しました")
                return True
            return False

        except Exception:
            self.logger.error("ドックウィジェット状態の復元に失敗しました: {str()}")
            return False

    def save_value(self, key: str, value: Any) -> None:
        """設定値を保存する

        Args:
            key (str): 設定キー
            value (Any): 設定値
        """
        try:
            self._settings.setValue(key, value)
            self._settings.sync()
            self.logger.debug("設定値を保存しました: {key}")
        except Exception:
            self.logger.error("設定値の保存に失敗しました ({key}): {str()}")

    def load_value(
        self, key: str, default: Any = None, value_type: Optional[type] = None
    ) -> Any:
        """設定値を読み込む

        Args:
            key (str): 設定キー
            default (Any): デフォルト値
            value_type (Optional[type]): 値の型（型変換用）

        Returns:
            Any: 設定値
        """
        try:
            if value_type:
                return self._settings.value(key, default, type=value_type)
            else:
                return self._settings.value(key, default)
        except Exception:
            self.logger.error("設定値の読み込みに失敗しました ({key}): {str()}")
            return default

    def remove_value(self, key: str) -> None:
        """設定値を削除する

        Args:
            key (str): 設定キー
        """
        try:
            self._settings.remove(key)
            self._settings.sync()
            self.logger.debug("設定値を削除しました: {key}")
        except Exception:
            self.logger.error("設定値の削除に失敗しました ({key}): {str()}")

    def contains(self, key: str) -> bool:
        """設定キーが存在するかチェックする

        Args:
            key (str): 設定キー

        Returns:
            bool: キーが存在する場合True
        """
        try:
            return self._settings.contains(key)
        except Exception:
            self.logger.error("設定キーの確認に失敗しました ({key}): {str()}")
            return False

    def clear_all(self) -> None:
        """すべての設定を削除する"""
        try:
            self._settings.clear()
            self._settings.sync()
            self.logger.info("すべての設定を削除しました")
        except Exception:
            self.logger.error("設定の削除に失敗しました: {str()}")

    def get_all_keys(self) -> list:
        """すべての設定キーを取得する

        Returns:
            list: 設定キーのリスト
        """
        try:
            return self._settings.allKeys()
        except Exception:
            self.logger.error("設定キーの取得に失敗しました: {str()}")
            return []

    def begin_group(self, prefix: str) -> None:
        """設定グループを開始する

        Args:
            prefix (str): グループのプレフィックス
        """
        self._settings.beginGroup(prefix)

    def end_group(self) -> None:
        """設定グループを終了する"""
        self._settings.endGroup()

    def sync(self) -> None:
        """設定を同期する（ディスクに書き込み）"""
        try:
            self._settings.sync()
            self.logger.debug("設定を同期しました")
        except Exception:
            self.logger.error("設定の同期に失敗しました: {str()}")

    def get_file_path(self) -> str:
        """設定ファイルのパスを取得する

        Returns:
            str: 設定ファイルのパス
        """
        try:
            return self._settings.fileName()
        except Exception:
            self.logger.error("設定ファイルパスの取得に失敗しました: {str()}")
            return ""


class UserPreferences:
    """ユーザー設定管理クラス

    ユーザー固有の設定（テーマ、言語、エディター設定等）を管理します。
    """

    def __init__(self, settings_manager: SettingsManager):
        """UserPreferencesを初期化する

        Args:
            settings_manager (SettingsManager): 設定管理インスタンス
        """
        self.logger = logging.getLogger(__name__)
        self._settings = settings_manager

        # デフォルト設定値
        self._defaults = {
            "ui/theme": "default",
            "ui/language": "ja",
            "ui/font_family": "",
            "ui/font_size": 9,
            "ui/show_tooltips": True,
            "ui/show_status_bar": True,
            "editor/show_preview": True,
            "editor/preview_update_delay": 100,
            "editor/show_zebra_editor": True,
            "editor/wcag_level": "AA",
            "editor/undo_limit": 50,
            "export/default_format": "json",
            "export/include_metadata": True,
            "accessibility/show_contrast_warnings": True,
            "accessibility/auto_suggest_improvements": True,
            "performance/enable_caching": True,
            "performance/lazy_loading": True,
        }

    def get_preference(self, key: str, default: Any = None) -> Any:
        """ユーザー設定を取得する

        Args:
            key (str): 設定キー
            default (Any): デフォルト値

        Returns:
            Any: 設定値
        """
        # デフォルト値を確認
        if default is None and key in self._defaults:
            default = self._defaults[key]

        return self._settings.load_value("preferences/{key}", default)

    def set_preference(self, key: str, value: Any) -> None:
        """ユーザー設定を保存する

        Args:
            key (str): 設定キー
            value (Any): 設定値
        """
        self._settings.save_value("preferences/{key}", value)
        self.logger.debug("ユーザー設定を保存しました: {key} = {value}")

    def reset_preferences(self) -> None:
        """ユーザー設定をデフォルト値にリセットする"""
        try:
            # preferences グループを削除
            self._settings.begin_group("preferences")
            keys = self._settings.get_all_keys()
            for key in keys:
                self._settings.remove_value(key)
            self._settings.end_group()

            # デフォルト値を設定
            for key, value in self._defaults.items():
                self.set_preference(key, value)

            self._settings.sync()
            self.logger.info("ユーザー設定をデフォルト値にリセットしました")

        except Exception:
            self.logger.error("ユーザー設定のリセットに失敗しました: {str()}")

    def export_preferences(self) -> Dict[str, Any]:
        """ユーザー設定をエクスポートする

        Returns:
            Dict[str, Any]: ユーザー設定の辞書
        """
        preferences = {}
        try:
            self._settings.begin_group("preferences")
            keys = self._settings.get_all_keys()
            for key in keys:
                preferences[key] = self._settings.load_value(key)
            self._settings.end_group()

            self.logger.info("ユーザー設定をエクスポートしました")
            return preferences

        except Exception:
            self.logger.error(f"ユーザー設定のエクスポートに失敗しました: {str()}")
            return {}

    def import_preferences(self, preferences: Dict[str, Any]) -> None:
        """ユーザー設定をインポートする

        Args:
            preferences (Dict[str, Any]): インポートする設定の辞書
        """
        try:
            for key, value in preferences.items():
                self.set_preference(key, value)

            self._settings.sync()
            self.logger.info("ユーザー設定をインポートしました")

        except Exception:
            self.logger.error("ユーザー設定のインポートに失敗しました: {str()}")


class WorkspaceManager:
    """ワークスペース管理クラス

    ワークスペースの状態（開いているファイル、レイアウト等）を管理します。
    """

    def __init__(self, settings_manager: SettingsManager):
        """WorkspaceManagerを初期化する

        Args:
            settings_manager (SettingsManager): 設定管理インスタンス
        """
        self.logger = logging.getLogger(__name__)
        self._settings = settings_manager

    def save_workspace(self, workspace_data: Dict[str, Any]) -> None:
        """ワークスペース状態を保存する

        Args:
            workspace_data (Dict[str, Any]): ワークスペースデータ
        """
        try:
            self._settings.begin_group("workspace")

            # 開いているファイル
            if "open_files" in workspace_data:
                self._settings.save_value("open_files", workspace_data["open_files"])

            # アクティブなファイル
            if "active_file" in workspace_data:
                self._settings.save_value("active_file", workspace_data["active_file"])

            # 最近使用したファイル
            if "recent_files" in workspace_data:
                self._settings.save_value(
                    "recent_files", workspace_data["recent_files"]
                )

            # エディターの状態
            if "editor_state" in workspace_data:
                self._settings.save_value(
                    "editor_state", workspace_data["editor_state"]
                )

            self._settings.end_group()
            self._settings.sync()

            self.logger.info("ワークスペース状態を保存しました")

        except Exception:
            self.logger.error("ワークスペース状態の保存に失敗しました: {str()}")

    def load_workspace(self) -> Dict[str, Any]:
        """ワークスペース状態を読み込む

        Returns:
            Dict[str, Any]: ワークスペースデータ
        """
        workspace_data = {}
        try:
            self._settings.begin_group("workspace")

            # 開いているファイル
            open_files = self._settings.load_value("open_files", [])
            if open_files:
                workspace_data["open_files"] = open_files

            # アクティブなファイル
            active_file = self._settings.load_value("active_file", "")
            if active_file:
                workspace_data["active_file"] = active_file

            # 最近使用したファイル
            recent_files = self._settings.load_value("recent_files", [])
            if recent_files:
                workspace_data["recent_files"] = recent_files

            # エディターの状態
            editor_state = self._settings.load_value("editor_state", {})
            if editor_state:
                workspace_data["editor_state"] = editor_state

            self._settings.end_group()

            self.logger.info("ワークスペース状態を読み込みました")
            return workspace_data

        except Exception:
            self.logger.error(f"ワークスペース状態の読み込みに失敗しました: {str()}")
            return {}

    def clear_workspace(self) -> None:
        """ワークスペース状態をクリアする"""
        try:
            self._settings.begin_group("workspace")
            keys = self._settings.get_all_keys()
            for key in keys:
                self._settings.remove_value(key)
            self._settings.end_group()
            self._settings.sync()

            self.logger.info("ワークスペース状態をクリアしました")

        except Exception:
            self.logger.error("ワークスペース状態のクリアに失敗しました: {str()}")
