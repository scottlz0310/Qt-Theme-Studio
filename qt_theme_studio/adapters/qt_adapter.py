"""
Qt フレームワーク自動検出・統合アダプター

このモジュールは、PySide6、PyQt6、PyQt5の順でQtフレームワークを自動検出し、
利用可能なフレームワークを使用してQApplicationインスタンスを作成する機能を提供します。
"""

import logging
import sys
from typing import Any, Optional


# カスタム例外クラス
class QtFrameworkNotFoundError(Exception):
    """Qtフレームワークが検出されない場合の例外"""


class QtAdapter:
    """Qt フレームワーク自動検出・統合アダプター

    PySide6 → PyQt6 → PyQt5 の順でフレームワークを自動検出し、
    検出されたフレームワークのモジュールとQApplicationインスタンスを提供します。
    """

    def __init__(self):
        """Qt Adapterを初期化する"""
        self.logger = logging.getLogger(__name__)
        self._detected_framework: Optional[str] = None
        self._qt_modules: Optional[dict[str, Any]] = None
        self._application: Optional[Any] = None

    def detect_qt_framework(self) -> str:
        """Qt フレームワークを自動検出する

        PySide6 → PyQt6 → PyQt5 の順で検出を試行し、
        最初に見つかったフレームワークを返します。

        Returns:
            str: 検出されたフレームワーク名 ('PySide6', 'PyQt6', 'PyQt5')

        Raises:
            QtFrameworkNotFoundError: 利用可能なQtフレームワークが見つからない場合
        """
        if self._detected_framework:
            return self._detected_framework

        frameworks = ["PySide6", "PyQt6", "PyQt5"]

        for framework in frameworks:
            try:
                __import__(framework)
                self._detected_framework = framework
                self.logger.info(f"Qtフレームワークを検出しました: {framework}")
                return framework
            except ImportError:
                self.logger.debug("フレームワーク {framework} は利用できません")
                continue

        error_msg = (
            "利用可能なQtフレームワークが見つかりません。"
            "PySide6、PyQt6、またはPyQt5をインストールしてください。"
        )
        self.logger.error(error_msg)
        raise QtFrameworkNotFoundError(error_msg)

    def get_qt_modules(self) -> dict[str, Any]:
        """検出されたQtモジュールを返す

        検出されたフレームワークの主要なQtモジュール(QtWidgets、QtCore、QtGui等)を
        辞書形式で返します。

        Returns: dict[str, Any]: Qtモジュールの辞書
                - 'QtWidgets': QtWidgetsモジュール
                - 'QtCore': QtCoreモジュール
                - 'QtGui': QtGuiモジュール
                - 'framework': 検出されたフレームワーク名

        Raises:
            QtFrameworkNotFoundError: Qtフレームワークが検出されていない場合
        """
        if self._qt_modules:
            return self._qt_modules

        framework = self.detect_qt_framework()

        try:
            if framework == "PySide6":
                from PySide6 import QtCore, QtGui, QtWidgets
            elif framework == "PyQt6":
                from PyQt6 import QtCore, QtGui, QtWidgets
            elif framework == "PyQt5":
                from PyQt5 import QtCore, QtGui, QtWidgets
            else:
                raise QtFrameworkNotFoundError(
                    f"サポートされていないフレームワーク: {framework}"
                )

            self._qt_modules = {
                "QtWidgets": QtWidgets,
                "QtCore": QtCore,
                "QtGui": QtGui,
                "framework": framework,
            }

            self.logger.info(f"{framework}のモジュールを正常に読み込みました")
            return self._qt_modules

        except ImportError as e:
            error_msg = f"{framework}のモジュール読み込みに失敗しました: {e}"
            self.logger.error(error_msg)
            raise QtFrameworkNotFoundError(error_msg) from e

    def create_application(self, app_name: str = "Qt-Theme-Studio") -> Any:
        """QApplicationインスタンスを作成する

        検出されたQtフレームワークを使用してQApplicationインスタンスを作成します。
        既にQApplicationが存在する場合は、既存のインスタンスを返します。

        Args:
            app_name (str): アプリケーション名(デフォルト: "Qt-Theme-Studio")

        Returns:
            QApplication: QApplicationインスタンス

        Raises:
            QtFrameworkNotFoundError: Qtフレームワークが検出されていない場合
        """
        qt_modules = self.get_qt_modules()
        QtWidgets = qt_modules["QtWidgets"]

        # 既存のQApplicationインスタンスをチェック
        existing_app = QtWidgets.QApplication.instance()
        if existing_app:
            self.logger.info("既存のQApplicationインスタンスを使用します")
            self._application = existing_app
            return existing_app

        # 新しいQApplicationインスタンスを作成
        try:
            app = QtWidgets.QApplication(sys.argv)
            app.setApplicationName(app_name)
            app.setApplicationDisplayName(app_name)
            app.setApplicationVersion("1.0.0")

            self._application = app
            self.logger.info(f"QApplicationインスタンスを作成しました: {app_name}")
            return app

        except Exception as e:
            error_msg = f"QApplicationの作成に失敗しました: {e}"
            self.logger.error(error_msg)
            raise QtFrameworkNotFoundError(error_msg) from e

    def get_framework_info(self) -> dict[str, str]:
        """検出されたフレームワークの詳細情報を返す

        Returns: dict[str, str]: フレームワーク情報
                - 'name': フレームワーク名
                - 'version': フレームワークのバージョン(取得可能な場合)
        """
        framework = self.detect_qt_framework()
        qt_modules = self.get_qt_modules()
        QtCore = qt_modules["QtCore"]

        info = {"name": framework, "version": "unknown"}

        try:
            # フレームワークのバージョン情報を取得
            if hasattr(QtCore, "qVersion"):
                info["version"] = QtCore.qVersion()
            elif hasattr(QtCore, "__version__"):
                info["version"] = QtCore.__version__
        except Exception:
            self.logger.debug("バージョン情報の取得に失敗しました: {e}")

        return info

    @property
    def is_initialized(self) -> bool:
        """Qt Adapterが初期化されているかどうかを返す

        Returns:
            bool: 初期化済みの場合True
        """
        return self._detected_framework is not None and self._qt_modules is not None

    @property
    def application(self) -> Optional[Any]:
        """現在のQApplicationインスタンスを返す

        Returns:
            Optional[QApplication]: QApplicationインスタンス(未作成の場合はNone)
        """
        return self._application
