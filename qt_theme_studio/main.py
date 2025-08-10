"""
Qt-Theme-Studio メインアプリケーション

このモジュールは、Qt-Theme-Studioアプリケーションのメインクラスを提供します。
アプリケーションの初期化、Qtフレームワークとqt-theme-managerの統合、
設定管理などの中核機能を実装します。
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .adapters.qt_adapter import QtAdapter, QtFrameworkNotFoundError
from .adapters.theme_adapter import ThemeAdapter, ThemeManagerError
from .config.settings import ApplicationSettings
from .utilities.i18n_manager import I18nManager
from .utilities.japanese_file_handler import JapaneseFileHandler
from .utilities.accessibility_manager import AccessibilityManager


class ThemeStudioApplication:
    """Qt-Theme-Studio メインアプリケーションクラス
    
    アプリケーションの初期化、Qtフレームワークとqt-theme-managerの統合、
    設定管理、メインウィンドウの管理を行います。
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """ThemeStudioApplicationを初期化する
        
        Args:
            config_dir (Optional[str]): 設定ディレクトリのパス
        """
        # ログ設定
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # アプリケーション状態
        self._is_initialized = False
        self._qt_app = None
        self._main_window = None
        
        # コンポーネント初期化
        self.qt_adapter = QtAdapter()
        self.theme_adapter = ThemeAdapter()
        self.settings = ApplicationSettings(config_dir)
        
        # 国際化とファイル処理
        self.i18n_manager = None
        self.file_handler = JapaneseFileHandler()
        self.accessibility_manager = None
        
        self.logger.info("Qt-Theme-Studio アプリケーションを初期化しています...")
    
    def _setup_logging(self) -> None:
        """ログシステムを設定する"""
        # ログフォーマットを日本語対応で設定
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                # ファイルハンドラーは後で設定ディレクトリが決まってから追加
            ]
        )
        
        # Qt関連のログレベルを調整
        logging.getLogger('qt_theme_studio').setLevel(logging.INFO)
    
    def initialize(self) -> bool:
        """アプリケーションを初期化する
        
        Qtフレームワークの自動検出、qt-theme-managerライブラリの統合、
        設定ファイルの読み込みを行います。
        
        Returns:
            bool: 初期化が成功した場合True
            
        Raises:
            QtFrameworkNotFoundError: Qtフレームワークが見つからない場合
            ThemeManagerError: qt-theme-managerライブラリの初期化に失敗した場合
        """
        if self._is_initialized:
            self.logger.info("アプリケーションは既に初期化されています")
            return True
        
        try:
            # 1. Qtフレームワークの自動検出と初期化
            self.logger.info("Qtフレームワークを検出しています...")
            framework_name = self.qt_adapter.detect_qt_framework()
            self.logger.info(f"Qtフレームワークを検出しました: {framework_name}")
            
            # QApplicationインスタンスの作成
            self._qt_app = self.qt_adapter.create_application("Qt-Theme-Studio")
            self.logger.info("QApplicationインスタンスを作成しました")
            
            # 2. qt-theme-managerライブラリの統合初期化
            self.logger.info("qt-theme-managerライブラリを初期化しています...")
            self.theme_adapter.initialize_theme_manager()
            self.logger.info("qt-theme-managerライブラリの初期化が完了しました")
            
            # 3. 設定ファイルの読み込み
            self.logger.info("設定ファイルを読み込んでいます...")
            self.settings.load_settings()
            self.logger.info("設定ファイルの読み込みが完了しました")
            
            # 4. ログファイルハンドラーの追加（設定ディレクトリが決まった後）
            self._setup_file_logging()
            
            # 5. 国際化システムの初期化
            self.logger.info("国際化システムを初期化しています...")
            self.i18n_manager = I18nManager(self.qt_adapter)
            self.logger.info("国際化システムの初期化が完了しました")
            
            # 6. アクセシビリティシステムの初期化
            self.logger.info("アクセシビリティシステムを初期化しています...")
            self.accessibility_manager = AccessibilityManager(self.qt_adapter)
            self.logger.info("アクセシビリティシステムの初期化が完了しました")
            
            # 7. アプリケーション情報の設定
            self._setup_application_info()
            
            self._is_initialized = True
            self.logger.info("Qt-Theme-Studio アプリケーションの初期化が完了しました")
            return True
            
        except QtFrameworkNotFoundError as e:
            self.logger.error(f"Qtフレームワークの初期化に失敗しました: {str(e)}")
            raise
        except ThemeManagerError as e:
            self.logger.error(f"qt-theme-managerライブラリの初期化に失敗しました: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"アプリケーションの初期化中に予期しないエラーが発生しました: {str(e)}")
            raise
    
    def _setup_file_logging(self) -> None:
        """ファイルログハンドラーを設定する"""
        try:
            log_dir = self.settings.get_config_directory() / "logs"
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / "qt_theme_studio.log"
            
            # ファイルハンドラーを追加
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # ルートロガーにハンドラーを追加
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)
            
            self.logger.info(f"ログファイルを設定しました: {log_file}")
            
        except Exception as e:
            self.logger.warning(f"ログファイルの設定に失敗しました: {str(e)}")
    
    def _setup_application_info(self) -> None:
        """アプリケーション情報を設定する"""
        if self._qt_app:
            self._qt_app.setApplicationName("Qt-Theme-Studio")
            self._qt_app.setApplicationDisplayName("Qt Theme Studio")
            self._qt_app.setApplicationVersion("1.0.0")
            self._qt_app.setOrganizationName("Qt-Theme-Studio")
            self._qt_app.setOrganizationDomain("qt-theme-studio.org")
            
            self.logger.info("アプリケーション情報を設定しました")
    
    def create_main_window(self):
        """メインウィンドウを作成する
        
        Returns:
            MainWindow: メインウィンドウインスタンス
            
        Raises:
            RuntimeError: アプリケーションが初期化されていない場合
        """
        if not self._is_initialized:
            raise RuntimeError("アプリケーションが初期化されていません。initialize()を先に呼び出してください。")
        
        if self._main_window is not None:
            self.logger.info("既存のメインウィンドウを返します")
            return self._main_window
        
        try:
            # メインウィンドウのインポートは初期化後に行う（循環インポート回避）
            from .views.main_window import MainWindow
            
            self._main_window = MainWindow(
                qt_adapter=self.qt_adapter,
                theme_adapter=self.theme_adapter,
                settings=self.settings,
                i18n_manager=self.i18n_manager,
                file_handler=self.file_handler,
                accessibility_manager=self.accessibility_manager
            )
            
            # ウィンドウ状態の復元（実際のQMainWindowインスタンスを渡す）
            if self._main_window.main_window:
                self.settings.restore_window_state(self._main_window.main_window)
            
            self.logger.info("メインウィンドウを作成しました")
            return self._main_window
            
        except ImportError as e:
            self.logger.error(f"メインウィンドウクラスのインポートに失敗しました: {str(e)}")
            raise RuntimeError(f"メインウィンドウの作成に失敗しました: {str(e)}")
        except Exception as e:
            self.logger.error(f"メインウィンドウの作成中にエラーが発生しました: {str(e)}")
            raise
    
    def run(self) -> int:
        """アプリケーションを実行する
        
        Returns:
            int: アプリケーションの終了コード
        """
        if not self._is_initialized:
            self.logger.error("アプリケーションが初期化されていません")
            return 1
        
        if not self._qt_app:
            self.logger.error("QApplicationが作成されていません")
            return 1
        
        try:
            # メインウィンドウの作成と表示
            main_window = self.create_main_window()
            main_window.show()
            
            self.logger.info("Qt-Theme-Studio アプリケーションを開始します")
            
            # アプリケーション終了時の処理を設定
            self._qt_app.aboutToQuit.connect(self._on_application_quit)
            
            # イベントループの開始
            exit_code = self._qt_app.exec()
            
            self.logger.info(f"Qt-Theme-Studio アプリケーションが終了しました (終了コード: {exit_code})")
            return exit_code
            
        except Exception as e:
            self.logger.error(f"アプリケーションの実行中にエラーが発生しました: {str(e)}")
            return 1
    
    def _on_application_quit(self) -> None:
        """アプリケーション終了時の処理"""
        self.logger.info("アプリケーション終了処理を開始します")
        
        try:
            # メインウィンドウの状態を保存
            if self._main_window and self._main_window.main_window:
                self.settings.save_window_state(self._main_window.main_window)
                self.logger.info("ウィンドウ状態を保存しました")
            
            # 設定の最終保存
            # （設定は自動保存されるが、念のため）
            
            self.logger.info("アプリケーション終了処理が完了しました")
            
        except Exception as e:
            self.logger.error(f"アプリケーション終了処理中にエラーが発生しました: {str(e)}")
    
    def get_framework_info(self) -> Dict[str, str]:
        """使用中のQtフレームワーク情報を取得する
        
        Returns:
            Dict[str, str]: フレームワーク情報
        """
        if not self._is_initialized:
            return {'name': 'unknown', 'version': 'unknown'}
        
        return self.qt_adapter.get_framework_info()
    
    def get_application_info(self) -> Dict[str, Any]:
        """アプリケーション情報を取得する
        
        Returns:
            Dict[str, Any]: アプリケーション情報
        """
        framework_info = self.get_framework_info()
        
        return {
            'name': 'Qt-Theme-Studio',
            'version': '1.0.0',
            'qt_framework': framework_info,
            'config_dir': str(self.settings.get_config_directory()),
            'is_initialized': self._is_initialized,
            'theme_manager_available': self.theme_adapter.is_initialized
        }
    
    @property
    def is_initialized(self) -> bool:
        """アプリケーションが初期化されているかどうかを返す
        
        Returns:
            bool: 初期化済みの場合True
        """
        return self._is_initialized
    
    @property
    def qt_application(self):
        """QApplicationインスタンスを返す
        
        Returns:
            QApplication: QApplicationインスタンス（未作成の場合はNone）
        """
        return self._qt_app
    
    @property
    def main_window(self):
        """メインウィンドウインスタンスを返す
        
        Returns:
            MainWindow: メインウィンドウインスタンス（未作成の場合はNone）
        """
        return self._main_window


def create_application(config_dir: Optional[str] = None) -> ThemeStudioApplication:
    """Qt-Theme-Studioアプリケーションインスタンスを作成する
    
    Args:
        config_dir (Optional[str]): 設定ディレクトリのパス
        
    Returns:
        ThemeStudioApplication: アプリケーションインスタンス
    """
    return ThemeStudioApplication(config_dir)


def main(config_dir: Optional[str] = None, initial_theme: Optional[str] = None, 
         debug_mode: bool = False) -> int:
    """メイン関数
    
    Args:
        config_dir (Optional[str]): 設定ディレクトリのパス
        initial_theme (Optional[str]): 起動時に読み込むテーマファイルのパス
        debug_mode (bool): デバッグモードの場合True
        
    Returns:
        int: アプリケーションの終了コード
    """
    try:
        # デバッグモードの場合はログレベルを調整
        if debug_mode:
            logging.getLogger().setLevel(logging.DEBUG)
            logging.getLogger('qt_theme_studio').setLevel(logging.DEBUG)
        
        # アプリケーションインスタンスの作成
        app = create_application(config_dir)
        
        # 初期化
        app.initialize()
        
        # 初期テーマの読み込み（指定されている場合）
        if initial_theme:
            try:
                main_window = app.create_main_window()
                # TODO: メインウィンドウにテーマ読み込み機能を追加後に実装
                app.logger.info(f"初期テーマの読み込み: {initial_theme}")
            except Exception as e:
                app.logger.warning(f"初期テーマの読み込みに失敗しました: {str(e)}")
        
        # 実行
        return app.run()
        
    except QtFrameworkNotFoundError as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        print("PySide6、PyQt6、またはPyQt5をインストールしてください。", file=sys.stderr)
        return 1
    except ThemeManagerError as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        print("qt-theme-managerライブラリをインストールしてください:", file=sys.stderr)
        print("pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"予期しないエラーが発生しました: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())