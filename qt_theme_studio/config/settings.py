"""
アプリケーション設定管理

このモジュールは、Qt-Theme-Studioアプリケーションの設定管理機能を提供します。
設定ファイルの読み込み・保存、最近使用したテーマリストの管理、
ウィンドウ状態の永続化などを行います。
"""

import json
from typing import Any, Dict, List, Optional, Union

from ..adapters.qt_adapter import QtAdapter
from .defaults import get_default_settings
from .persistence import SettingsManager, UserPreferences, WorkspaceManager


class ApplicationSettings:
    """アプリケーション設定管理クラス

    アプリケーションの設定ファイルの読み込み・保存、最近使用したテーマリストの管理、
    ユーザー設定のデフォルト値管理を行います。
    """

    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """ApplicationSettingsを初期化する

        Args:
            config_dir (Optional[Union[str, Path]]): 設定ディレクトリのパス
                                                   Noneの場合はデフォルトディレクトリを使用
        """
        self.logger = logging.getLogger(__name__)

        # 設定ディレクトリの決定
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = self._get_default_config_dir()

        # 設定ファイルのパス
        self.settings_file = self.config_dir / "settings.json"

        # 設定ディレクトリの作成
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 設定データ
        self._settings: Dict[str, Any] = {}

        # Qt Adapterの初期化（QSettingsで使用）
        self._qt_adapter = QtAdapter()

        # QSettings統合
        self._settings_manager: Optional[SettingsManager] = None
        self._user_preferences: Optional[UserPreferences] = None
        self._workspace_manager: Optional[WorkspaceManager] = None

        self.logger.info("設定管理を初期化しました: {self.config_dir}")

    def _get_default_config_dir(self) -> Path:
        """デフォルトの設定ディレクトリパスを取得する

        Returns:
            Path: 設定ディレクトリのパス
        """
        # OSに応じた適切な設定ディレクトリを使用
        if os.name == "nt":  # Windows
            config_base = Path(
                os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
            )
        elif os.name == "posix":  # Linux/macOS
            config_base = Path(
                os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
            )
        else:
            config_base = Path.home() / ".config"

        return config_base / "qt-theme-studio"

    def load_settings(self) -> Dict[str, Any]:
        """設定ファイルを読み込む

        設定ファイルが存在しない場合は、デフォルト設定を返します。

        Returns:
            Dict[str, Any]: 読み込まれた設定データ
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)

                # デフォルト設定とマージ
                self._settings = self._merge_settings(
                    get_default_settings(), loaded_settings
                )
                self.logger.info("設定ファイルを読み込みました: {self.settings_file}")
            else:
                # デフォルト設定を使用
                self._settings = get_default_settings()
                self.logger.info(
                    "設定ファイルが存在しないため、デフォルト設定を使用します"
                )

                # デフォルト設定を保存
                self.save_settings(self._settings)

        except (json.JSONDecodeError, IOError) as e:
            self.logger.error("設定ファイルの読み込みに失敗しました: {str(e)}")
            self.logger.info("デフォルト設定を使用します")
            self._settings = get_default_settings()

        return self._settings

    def save_settings(self, settings: Dict[str, Any]) -> None:
        """設定ファイルを保存する

        Args:
            settings (Dict[str, Any]): 保存する設定データ
        """
        try:
            # 設定データを更新
            self._settings = settings

            # JSONファイルとして保存
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            self.logger.info("設定ファイルを保存しました: {self.settings_file}")

        except (IOError, TypeError):
            self.logger.error("設定ファイルの保存に失敗しました: {str(e)}")
            raise

    def get_recent_themes(self) -> List[str]:
        """最近使用したテーマリストを取得する

        Returns:
            List[str]: 最近使用したテーマファイルのパスリスト（最新順）
        """
        if not self._settings:
            self.load_settings()

        recent_themes = self._settings.get("theme", {}).get("recent_themes", [])

        # 存在しないファイルを除外
        valid_themes = []
        for theme_path in recent_themes:
            if os.path.exists(theme_path):
                valid_themes.append(theme_path)
            else:
                self.logger.debug(
                    "存在しないテーマファイルを除外しました: {theme_path}"
                )

        # 有効なテーマリストが変更された場合は設定を更新
        if len(valid_themes) != len(recent_themes):
            self._settings["theme"]["recent_themes"] = valid_themes
            self.save_settings(self._settings)

        return valid_themes

    def add_recent_theme(self, theme_path: str) -> None:
        """最近使用したテーマリストに追加する

        Args:
            theme_path (str): 追加するテーマファイルのパス
        """
        if not self._settings:
            self.load_settings()

        # 絶対パスに変換
        abs_path = os.path.abspath(theme_path)

        # 既存のリストから同じパスを削除
        recent_themes = self._settings.get("theme", {}).get("recent_themes", [])
        if abs_path in recent_themes:
            recent_themes.remove(abs_path)

        # リストの先頭に追加
        recent_themes.insert(0, abs_path)

        # 最大数を超えた場合は古いものを削除
        max_recent = self._settings.get("theme", {}).get("max_recent_themes", 10)
        if len(recent_themes) > max_recent:
            recent_themes = recent_themes[:max_recent]

        # 設定を更新
        if "theme" not in self._settings:
            self._settings["theme"] = {}
        self._settings["theme"]["recent_themes"] = recent_themes

        # 設定を保存
        self.save_settings(self._settings)

        self.logger.info("最近使用したテーマリストに追加しました: {abs_path}")

    def remove_recent_theme(self, theme_path: str) -> None:
        """最近使用したテーマリストから削除する

        Args:
            theme_path (str): 削除するテーマファイルのパス
        """
        if not self._settings:
            self.load_settings()

        abs_path = os.path.abspath(theme_path)
        recent_themes = self._settings.get("theme", {}).get("recent_themes", [])

        if abs_path in recent_themes:
            recent_themes.remove(abs_path)
            self._settings["theme"]["recent_themes"] = recent_themes
            self.save_settings(self._settings)
            self.logger.info("最近使用したテーマリストから削除しました: {abs_path}")

    def clear_recent_themes(self) -> None:
        """最近使用したテーマリストをクリアする"""
        if not self._settings:
            self.load_settings()

        if "theme" not in self._settings:
            self._settings["theme"] = {}

        self._settings["theme"]["recent_themes"] = []
        self.save_settings(self._settings)

        self.logger.info("最近使用したテーマリストをクリアしました")

    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """設定値を取得する

        Args:
            key_path (str): 設定キーのパス（例: 'window.width', 'theme.auto_save'）
            default (Any): デフォルト値

        Returns:
            Any: 設定値
        """
        if not self._settings:
            self.load_settings()

        keys = key_path.split(".")
        value = self._settings

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set_setting(self, key_path: str, value: Any) -> None:
        """設定値を設定する

        Args:
            key_path (str): 設定キーのパス（例: 'window.width', 'theme.auto_save'）
            value (Any): 設定値
        """
        if not self._settings:
            self.load_settings()

        keys = key_path.split(".")
        current = self._settings

        # ネストした辞書を作成
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # 値を設定
        current[keys[-1]] = value

        # 設定を保存
        self.save_settings(self._settings)

        self.logger.debug("設定値を更新しました: {key_path} = {value}")

    def _merge_settings(
        self, default: Dict[str, Any], loaded: Dict[str, Any]
    ) -> Dict[str, Any]:
        """デフォルト設定と読み込み設定をマージする

        Args:
            default (Dict[str, Any]): デフォルト設定
            loaded (Dict[str, Any]): 読み込み設定

        Returns:
            Dict[str, Any]: マージされた設定
        """
        result = default.copy()

        for key, value in loaded.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value

        return result

    def reset_to_defaults(self) -> None:
        """設定をデフォルト値にリセットする"""
        self._settings = get_default_settings()
        self.save_settings(self._settings)
        self.logger.info("設定をデフォルト値にリセットしました")

    def get_config_directory(self) -> Path:
        """設定ディレクトリのパスを取得する

        Returns:
            Path: 設定ディレクトリのパス
        """
        return self.config_dir

    def get_settings_file_path(self) -> Path:
        """設定ファイルのパスを取得する

        Returns:
            Path: 設定ファイルのパス
        """
        return self.settings_file

    @property
    def settings(self) -> Dict[str, Any]:
        """現在の設定データを取得する

        Returns:
            Dict[str, Any]: 設定データ
        """
        if not self._settings:
            self.load_settings()
        return self._settings.copy()

    def get_settings_manager(self) -> SettingsManager:
        """QSettings統合のSettingsManagerを取得する

        Returns:
            SettingsManager: 設定管理インスタンス
        """
        if self._settings_manager is None:
            self._settings_manager = SettingsManager()
        return self._settings_manager

    def get_user_preferences(self) -> UserPreferences:
        """ユーザー設定管理インスタンスを取得する

        Returns:
            UserPreferences: ユーザー設定管理インスタンス
        """
        if self._user_preferences is None:
            self._user_preferences = UserPreferences(self.get_settings_manager())
        return self._user_preferences

    def get_workspace_manager(self) -> WorkspaceManager:
        """ワークスペース管理インスタンスを取得する

        Returns:
            WorkspaceManager: ワークスペース管理インスタンス
        """
        if self._workspace_manager is None:
            self._workspace_manager = WorkspaceManager(self.get_settings_manager())
        return self._workspace_manager

    def save_window_state(self, window) -> None:
        """ウィンドウ状態を保存する（QSettings使用）

        Args:
            window: QMainWindowインスタンス
        """
        settings_manager = self.get_settings_manager()
        settings_manager.save_window_state(window)

    def restore_window_state(self, window) -> bool:
        """ウィンドウ状態を復元する（QSettings使用）

        Args:
            window: QMainWindowインスタンス

        Returns:
            bool: 復元に成功した場合True
        """
        settings_manager = self.get_settings_manager()
        return settings_manager.restore_window_state(window)

    def save_workspace_state(self, workspace_data: Dict[str, Any]) -> None:
        """ワークスペース状態を保存する

        Args:
            workspace_data (Dict[str, Any]): ワークスペースデータ
        """
        workspace_manager = self.get_workspace_manager()
        workspace_manager.save_workspace(workspace_data)

    def load_workspace_state(self) -> Dict[str, Any]:
        """ワークスペース状態を読み込む

        Returns:
            Dict[str, Any]: ワークスペースデータ
        """
        workspace_manager = self.get_workspace_manager()
        return workspace_manager.load_workspace()

    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """ユーザー設定を取得する

        Args:
            key (str): 設定キー
            default (Any): デフォルト値

        Returns:
            Any: 設定値
        """
        user_preferences = self.get_user_preferences()
        return user_preferences.get_preference(key, default)

    def set_user_preference(self, key: str, value: Any) -> None:
        """ユーザー設定を保存する

        Args:
            key (str): 設定キー
            value (Any): 設定値
        """
        user_preferences = self.get_user_preferences()
        user_preferences.set_preference(key, value)
