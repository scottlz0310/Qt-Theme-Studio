"""
メインウィンドウ実装

このモジュールは、Qt-Theme-Studioのメインウィンドウを実装します。
メニューバー、ツールバー、ステータスバーの基本構造を提供し、
日本語UIテキストでユーザーインターフェースを構成します。
"""

import logging
from typing import Optional, Dict, Any

from ..adapters.qt_adapter import QtAdapter
from ..config.settings import ApplicationSettings
from ..logger import get_logger, LogCategory
from .dialogs.help_dialog import HelpDialog
# テーマギャラリーは動的インポートで使用


class MainWindow:
    """
    Qt-Theme-Studioメインウィンドウクラス
    
    アプリケーションのメインウィンドウを管理し、メニューバー、ツールバー、
    ステータスバーの基本構造を提供します。日本語UIテキストを使用し、
    ウィンドウ状態の保存・復元機能を統合します。
    """
    
    def __init__(self, qt_adapter: QtAdapter, theme_adapter, settings: ApplicationSettings, 
                 i18n_manager=None, file_handler=None, accessibility_manager=None):
        """
        メインウィンドウを初期化します
        
        Args:
            qt_adapter: Qt フレームワークアダプター
            theme_adapter: テーマアダプター
            settings: アプリケーション設定管理
            i18n_manager: 国際化管理
            file_handler: 日本語ファイル処理
            accessibility_manager: アクセシビリティ管理
        """
        self.qt_adapter = qt_adapter
        self.theme_adapter = theme_adapter
        self.settings = settings
        self.i18n_manager = i18n_manager
        self.file_handler = file_handler
        self.accessibility_manager = accessibility_manager
        self.logger = get_logger()
        
        # Qtモジュールを取得
        self.qt_modules = qt_adapter.get_qt_modules()
        self.QtWidgets = self.qt_modules['QtWidgets']
        self.QtCore = self.qt_modules['QtCore']
        self.QtGui = self.qt_modules['QtGui']
        
        # メインウィンドウインスタンス
        self.main_window: Optional[Any] = None
        
        # UIコンポーネント
        self.menu_bar: Optional[Any] = None
        self.tool_bar: Optional[Any] = None
        self.status_bar: Optional[Any] = None
        self.central_widget: Optional[Any] = None
        self.placeholder_label: Optional[Any] = None
        
        # 統合コンポーネント
        self.theme_editor: Optional[Any] = None
        self.zebra_editor: Optional[Any] = None
        self.preview_window: Optional[Any] = None
        
        # レイアウト管理
        self.main_splitter: Optional[Any] = None
        self.left_splitter: Optional[Any] = None
        
        # メニューアクション
        self.actions: Dict[str, Any] = {}
        
        # 現在のテーマデータ
        self.current_theme_data: Dict[str, Any] = {}
        
        # テーマファイルパスと保存状態
        self.current_theme_path: Optional[str] = None
        self._theme_saved: bool = True
        
        # 複数テーマファイル対応
        self.current_source_file: Optional[str] = None
        self.current_source_theme_key: Optional[str] = None
        
        # メインウィンドウを作成
        self.create_window()
        
        # デフォルトテーマを作成して保存ボタンを有効化
        self._create_default_theme()
        
        self.logger.info("メインウィンドウを初期化しました", LogCategory.UI)
    
    def tr(self, text: str, context: str = "MainWindow") -> str:
        """
        テキストを翻訳します
        
        Args:
            text: 翻訳するテキスト
            context: 翻訳コンテキスト
            
        Returns:
            str: 翻訳されたテキスト
        """
        if self.i18n_manager:
            return self.i18n_manager.tr(text, context)
        return text
    
    def create_window(self) -> Any:
        """
        メインウィンドウを作成します
        
        Returns:
            QMainWindow: 作成されたメインウィンドウインスタンス
        """
        if self.main_window is not None:
            return self.main_window
        
        # メインウィンドウの作成
        self.main_window = self.QtWidgets.QMainWindow()
        
        # ウィンドウプロパティの設定
        self._setup_window_properties()
        
        # UIコンポーネントの設定
        self._setup_menu_bar()
        self._setup_tool_bar()
        self._setup_status_bar()
        self._setup_central_widget()
        
        # ウィンドウ状態の復元
        self._restore_window_state()
        
        # クローズイベントハンドラーの設定
        self._setup_close_event_handler()
        
        # メニューアクションのシグナル接続
        self._connect_menu_actions()
        
        # アクセシビリティ機能の設定
        if self.accessibility_manager:
            self.accessibility_manager.setup_accessibility_features(self.main_window)
        
        # コンポーネント間の連携を設定
        self._setup_component_connections()
        
        self.logger.info("メインウィンドウを作成しました", LogCategory.UI)
        return self.main_window
    
    def _setup_window_properties(self) -> None:
        """ウィンドウプロパティを設定します"""
        if not self.main_window:
            return
        
        # ウィンドウタイトル
        self.main_window.setWindowTitle("Qt-Theme-Studio - テーマエディター")
        
        # ウィンドウアイコン（将来的に設定）
        # self.main_window.setWindowIcon(self.QtGui.QIcon(":/icons/app_icon.png"))
        
        # デフォルトウィンドウサイズ
        default_width = self.settings.get_setting('window.width', 1200)
        default_height = self.settings.get_setting('window.height', 800)
        self.main_window.resize(default_width, default_height)
        
        # 最小ウィンドウサイズ
        self.main_window.setMinimumSize(800, 600)
        
        # ウィンドウを画面中央に配置
        self._center_window()
        
        self.logger.debug("ウィンドウプロパティを設定しました", LogCategory.UI)
    
    def _center_window(self) -> None:
        """ウィンドウを画面中央に配置します"""
        if not self.main_window:
            return
        
        # 画面の中央にウィンドウを配置
        screen = self.QtWidgets.QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.main_window.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.main_window.move(window_geometry.topLeft())
    
    def _setup_menu_bar(self) -> None:
        """メニューバーを設定します"""
        if not self.main_window:
            return
        
        self.menu_bar = self.main_window.menuBar()
        
        # ファイルメニュー
        self._create_file_menu()
        
        # 編集メニュー
        self._create_edit_menu()
        
        # テーマメニュー
        self._create_theme_menu()
        
        # 表示メニュー
        self._create_view_menu()
        
        # ツールメニュー
        self._create_tools_menu()
        
        # ヘルプメニュー
        self._create_help_menu()
        
        # ヘルプアクションの接続
        self._connect_help_actions()
        
        self.logger.debug("メニューバーを設定しました", LogCategory.UI)
    
    def _create_file_menu(self) -> None:
        """ファイルメニューを作成します"""
        file_menu = self.menu_bar.addMenu("ファイル(&F)")
        
        # 新規テーマ
        new_action = self.QtGui.QAction("新規テーマ(&N)", self.main_window)
        new_action.setShortcut(self.QtGui.QKeySequence.StandardKey.New)
        new_action.setStatusTip("新しいテーマを作成します")
        file_menu.addAction(new_action)
        self.actions['new_theme'] = new_action
        
        # テーマを開く
        open_action = self.QtGui.QAction("テーマを開く(&O)...", self.main_window)
        open_action.setShortcut(self.QtGui.QKeySequence.StandardKey.Open)
        open_action.setStatusTip("既存のテーマファイルを開きます")
        file_menu.addAction(open_action)
        self.actions['open_theme'] = open_action
        
        # 最近使用したテーマ
        recent_menu = file_menu.addMenu("最近使用したテーマ(&R)")
        self._setup_recent_themes_menu(recent_menu)
        
        file_menu.addSeparator()
        
        # テーマを保存
        save_action = self.QtGui.QAction("テーマを保存(&S)", self.main_window)
        save_action.setShortcut(self.QtGui.QKeySequence.StandardKey.Save)
        save_action.setStatusTip("現在のテーマを保存します")
        save_action.setEnabled(False)  # 初期状態では無効
        file_menu.addAction(save_action)
        self.actions['save_theme'] = save_action
        
        # 名前を付けて保存
        save_as_action = self.QtGui.QAction("名前を付けて保存(&A)...", self.main_window)
        save_as_action.setShortcut(self.QtGui.QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("テーマに名前を付けて保存します")
        save_as_action.setEnabled(False)  # 初期状態では無効
        file_menu.addAction(save_as_action)
        self.actions['save_as_theme'] = save_as_action
        
        file_menu.addSeparator()
        
        # エクスポート
        export_menu = file_menu.addMenu("エクスポート(&E)")
        self._create_export_menu(export_menu)
        
        # インポート
        import_menu = file_menu.addMenu("インポート(&I)")
        self._create_import_menu(import_menu)
        
        file_menu.addSeparator()
        
        # 終了
        exit_action = self.QtGui.QAction("終了(&X)", self.main_window)
        exit_action.setShortcut(self.QtGui.QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("アプリケーションを終了します")
        exit_action.triggered.connect(self.main_window.close)
        file_menu.addAction(exit_action)
        self.actions['exit'] = exit_action
    
    def _create_edit_menu(self) -> None:
        """編集メニューを作成します"""
        edit_menu = self.menu_bar.addMenu("編集(&E)")
        
        # 元に戻す
        undo_action = self.QtGui.QAction("元に戻す(&U)", self.main_window)
        undo_action.setShortcut(self.QtGui.QKeySequence.StandardKey.Undo)
        undo_action.setStatusTip("直前の操作を元に戻します")
        undo_action.setEnabled(False)  # 初期状態では無効
        edit_menu.addAction(undo_action)
        self.actions['undo'] = undo_action
        
        # やり直し
        redo_action = self.QtGui.QAction("やり直し(&R)", self.main_window)
        redo_action.setShortcut(self.QtGui.QKeySequence.StandardKey.Redo)
        redo_action.setStatusTip("取り消した操作をやり直します")
        redo_action.setEnabled(False)  # 初期状態では無効
        edit_menu.addAction(redo_action)
        self.actions['redo'] = redo_action
        
        edit_menu.addSeparator()
        
        # 設定
        preferences_action = self.QtGui.QAction("設定(&P)...", self.main_window)
        preferences_action.setStatusTip("アプリケーションの設定を変更します")
        edit_menu.addAction(preferences_action)
        self.actions['preferences'] = preferences_action
        
        edit_menu.addSeparator()
        
        # ワークスペースリセット
        reset_workspace_action = self.QtGui.QAction("ワークスペースリセット(&W)", self.main_window)
        reset_workspace_action.setStatusTip("ワークスペースをデフォルト状態にリセットします")
        reset_workspace_action.triggered.connect(self.reset_workspace)
        edit_menu.addAction(reset_workspace_action)
        self.actions['reset_workspace'] = reset_workspace_action
    
    def _create_theme_menu(self) -> None:
        """テーマメニューを作成します"""
        theme_menu = self.menu_bar.addMenu("テーマ(&T)")
        
        # テーマエディター
        theme_editor_action = self.QtGui.QAction("テーマエディター(&E)", self.main_window)
        theme_editor_action.setStatusTip("テーマエディターを開きます")
        theme_editor_action.setCheckable(True)
        theme_editor_action.setChecked(True)  # デフォルトで表示
        theme_menu.addAction(theme_editor_action)
        self.actions['theme_editor'] = theme_editor_action
        
        # オートテーマジェネレーター
        zebra_editor_action = self.QtGui.QAction("オートテーマジェネレーター(&A)", self.main_window)
        zebra_editor_action.setStatusTip("WCAG準拠のテーマカラーを自動生成します")
        zebra_editor_action.setCheckable(True)
        zebra_editor_action.setChecked(True)  # デフォルトで表示
        theme_menu.addAction(zebra_editor_action)
        self.actions['zebra_editor'] = zebra_editor_action
        
        theme_menu.addSeparator()
        
        # テーマギャラリー
        gallery_action = self.QtGui.QAction("テーマギャラリー(&G)", self.main_window)
        gallery_action.setStatusTip("テーマギャラリーを開きます")
        gallery_action.setShortcut(self.QtGui.QKeySequence("Ctrl+G"))
        theme_menu.addAction(gallery_action)
        self.actions['theme_gallery'] = gallery_action
        
        # テーマテンプレート
        templates_action = self.QtGui.QAction("テーマテンプレート(&T)", self.main_window)
        templates_action.setStatusTip("テーマテンプレートを選択します")
        theme_menu.addAction(templates_action)
        self.actions['theme_templates'] = templates_action
    
    def _create_view_menu(self) -> None:
        """表示メニューを作成します"""
        view_menu = self.menu_bar.addMenu("表示(&V)")
        
        # ライブプレビュー
        preview_action = self.QtGui.QAction("ライブプレビュー(&P)", self.main_window)
        preview_action.setStatusTip("ライブプレビューウィンドウを表示します")
        preview_action.setCheckable(True)
        preview_action.setChecked(True)  # デフォルトで表示
        view_menu.addAction(preview_action)
        self.actions['live_preview'] = preview_action
        
        view_menu.addSeparator()
        
        # ツールバー
        toolbar_action = self.QtGui.QAction("ツールバー(&T)", self.main_window)
        toolbar_action.setStatusTip("ツールバーの表示/非表示を切り替えます")
        toolbar_action.setCheckable(True)
        toolbar_action.setChecked(True)  # デフォルトで表示
        view_menu.addAction(toolbar_action)
        self.actions['toolbar'] = toolbar_action
        
        # ステータスバー
        statusbar_action = self.QtGui.QAction("ステータスバー(&S)", self.main_window)
        statusbar_action.setStatusTip("ステータスバーの表示/非表示を切り替えます")
        statusbar_action.setCheckable(True)
        statusbar_action.setChecked(True)  # デフォルトで表示
        view_menu.addAction(statusbar_action)
        self.actions['statusbar'] = statusbar_action
        
        view_menu.addSeparator()
        
        # フルスクリーン
        fullscreen_action = self.QtGui.QAction("フルスクリーン(&F)", self.main_window)
        fullscreen_action.setShortcut(self.QtGui.QKeySequence.StandardKey.FullScreen)
        fullscreen_action.setStatusTip("フルスクリーン表示に切り替えます")
        fullscreen_action.setCheckable(True)
        view_menu.addAction(fullscreen_action)
        self.actions['fullscreen'] = fullscreen_action
    
    def _create_tools_menu(self) -> None:
        """ツールメニューを作成します"""
        tools_menu = self.menu_bar.addMenu("ツール(&T)")
        
        # アクセシビリティチェック
        accessibility_action = self.QtGui.QAction("アクセシビリティチェック(&A)", self.main_window)
        accessibility_action.setStatusTip("テーマのアクセシビリティをチェックします")
        tools_menu.addAction(accessibility_action)
        self.actions['accessibility_check'] = accessibility_action
        
        # 色コントラスト計算
        contrast_action = self.QtGui.QAction("色コントラスト計算(&C)", self.main_window)
        contrast_action.setStatusTip("色のコントラスト比を計算します")
        tools_menu.addAction(contrast_action)
        self.actions['contrast_calculator'] = contrast_action
        
        tools_menu.addSeparator()
        
        # プレビュー画像エクスポート
        export_preview_action = self.QtGui.QAction("プレビュー画像エクスポート(&P)", self.main_window)
        export_preview_action.setStatusTip("プレビュー画像をPNG形式で保存します")
        tools_menu.addAction(export_preview_action)
        self.actions['export_preview'] = export_preview_action
        
        tools_menu.addSeparator()
        
        # テーマギャラリー
        gallery_action = self.QtGui.QAction("テーマギャラリー(&G)", self.main_window)
        gallery_action.setStatusTip("テーマギャラリーを開きます")
        gallery_action.setShortcut(self.QtGui.QKeySequence("Ctrl+3"))
        tools_menu.addAction(gallery_action)
        self.actions['theme_gallery_tools'] = gallery_action
    
    def _create_help_menu(self) -> None:
        """ヘルプメニューを作成します"""
        help_menu = self.menu_bar.addMenu("ヘルプ(&H)")
        
        # ヘルプ
        help_action = self.QtGui.QAction("ヘルプ(&H)", self.main_window)
        help_action.setShortcut(self.QtGui.QKeySequence.StandardKey.HelpContents)
        help_action.setStatusTip("ヘルプドキュメントを表示します")
        help_menu.addAction(help_action)
        self.actions['help'] = help_action
        
        # ユーザーマニュアル
        manual_action = self.QtGui.QAction("ユーザーマニュアル(&M)", self.main_window)
        manual_action.setStatusTip("ユーザーマニュアルを表示します")
        help_menu.addAction(manual_action)
        self.actions['user_manual'] = manual_action
        
        help_menu.addSeparator()
        
        # Qt-Theme-Studioについて
        about_action = self.QtGui.QAction("Qt-Theme-Studioについて(&A)", self.main_window)
        about_action.setStatusTip("アプリケーションの情報を表示します")
        help_menu.addAction(about_action)
        self.actions['about'] = about_action
        
        # Qtについて
        about_qt_action = self.QtGui.QAction("Qtについて(&Q)", self.main_window)
        about_qt_action.setStatusTip("Qtライブラリの情報を表示します")
        about_qt_action.triggered.connect(self.QtWidgets.QApplication.aboutQt)
        help_menu.addAction(about_qt_action)
        self.actions['about_qt'] = about_qt_action
    
    def _setup_recent_themes_menu(self, recent_menu) -> None:
        """最近使用したテーマメニューを設定します"""
        recent_themes = self.settings.get_recent_themes()
        
        if not recent_themes:
            no_recent_action = self.QtGui.QAction("最近使用したテーマはありません", self.main_window)
            no_recent_action.setEnabled(False)
            recent_menu.addAction(no_recent_action)
        else:
            for i, theme_path in enumerate(recent_themes[:10]):  # 最大10個まで表示
                # ファイル名のみを表示
                import os
                theme_name = os.path.basename(theme_path)
                action_text = f"&{i+1} {theme_name}"
                
                recent_action = self.QtGui.QAction(action_text, self.main_window)
                recent_action.setStatusTip(f"テーマファイルを開きます: {theme_path}")
                recent_action.setData(theme_path)  # パスをデータとして保存
                recent_menu.addAction(recent_action)
    
    def _create_export_menu(self, export_menu) -> None:
        """エクスポートメニューを作成します"""
        # JSON形式でエクスポート
        export_json_action = self.QtGui.QAction("JSON形式(&J)...", self.main_window)
        export_json_action.setStatusTip("テーマをJSON形式でエクスポートします")
        export_menu.addAction(export_json_action)
        self.actions['export_json'] = export_json_action
        
        # QSS形式でエクスポート
        export_qss_action = self.QtGui.QAction("QSS形式(&Q)...", self.main_window)
        export_qss_action.setStatusTip("テーマをQSS形式でエクスポートします")
        export_menu.addAction(export_qss_action)
        self.actions['export_qss'] = export_qss_action
        
        # CSS形式でエクスポート
        export_css_action = self.QtGui.QAction("CSS形式(&C)...", self.main_window)
        export_css_action.setStatusTip("テーマをCSS形式でエクスポートします")
        export_menu.addAction(export_css_action)
        self.actions['export_css'] = export_css_action
    
    def _create_import_menu(self, import_menu) -> None:
        """インポートメニューを作成します"""
        # JSON形式からインポート
        import_json_action = self.QtGui.QAction("JSON形式から(&J)...", self.main_window)
        import_json_action.setStatusTip("JSON形式のテーマファイルをインポートします")
        import_menu.addAction(import_json_action)
        self.actions['import_json'] = import_json_action
        
        # QSS形式からインポート
        import_qss_action = self.QtGui.QAction("QSS形式から(&Q)...", self.main_window)
        import_qss_action.setStatusTip("QSS形式のテーマファイルをインポートします")
        import_menu.addAction(import_qss_action)
        self.actions['import_qss'] = import_qss_action
        
        # CSS形式からインポート
        import_css_action = self.QtGui.QAction("CSS形式から(&C)...", self.main_window)
        import_css_action.setStatusTip("CSS形式のテーマファイルをインポートします")
        import_menu.addAction(import_css_action)
        self.actions['import_css'] = import_css_action
    
    def _setup_tool_bar(self) -> None:
        """ツールバーを設定します"""
        if not self.main_window:
            return
        
        self.tool_bar = self.main_window.addToolBar("メインツールバー")
        self.tool_bar.setObjectName("MainToolBar")
        
        # ツールバーの設定
        self.tool_bar.setToolButtonStyle(self.QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.tool_bar.setMovable(True)
        
        # 新規テーマボタン
        if 'new_theme' in self.actions:
            self.tool_bar.addAction(self.actions['new_theme'])
        
        # テーマを開くボタン
        if 'open_theme' in self.actions:
            self.tool_bar.addAction(self.actions['open_theme'])
        
        # テーマを保存ボタン
        if 'save_theme' in self.actions:
            self.tool_bar.addAction(self.actions['save_theme'])
        
        self.tool_bar.addSeparator()
        
        # 元に戻すボタン
        if 'undo' in self.actions:
            self.tool_bar.addAction(self.actions['undo'])
        
        # やり直しボタン
        if 'redo' in self.actions:
            self.tool_bar.addAction(self.actions['redo'])
        
        self.tool_bar.addSeparator()
        
        # ライブプレビューボタン
        if 'live_preview' in self.actions:
            self.tool_bar.addAction(self.actions['live_preview'])
        
        # アクセシビリティチェックボタン
        if 'accessibility_check' in self.actions:
            self.tool_bar.addAction(self.actions['accessibility_check'])
        
        self.logger.debug("ツールバーを設定しました", LogCategory.UI)
    
    def _setup_status_bar(self) -> None:
        """ステータスバーを設定します"""
        if not self.main_window:
            return
        
        self.status_bar = self.main_window.statusBar()
        
        # 初期メッセージ
        self.status_bar.showMessage("Qt-Theme-Studio へようこそ", 3000)
        
        # 永続的な情報表示用のラベル
        self.status_framework_label = self.QtWidgets.QLabel()
        self.status_theme_label = self.QtWidgets.QLabel()
        
        # フレームワーク情報を表示
        framework_info = self.qt_adapter.get_framework_info()
        framework_text = f"Qt: {framework_info['name']} {framework_info['version']}"
        self.status_framework_label.setText(framework_text)
        
        # テーマ情報を表示（初期状態）
        self.status_theme_label.setText("テーマ: 未選択")
        
        # ステータスバーに追加
        self.status_bar.addPermanentWidget(self.status_theme_label)
        self.status_bar.addPermanentWidget(self.status_framework_label)
        
        self.logger.debug("ステータスバーを設定しました", LogCategory.UI)
    
    def _setup_central_widget(self) -> None:
        """中央ウィジェットを設定します"""
        if not self.main_window:
            return
        
        # 中央ウィジェットとして空のウィジェットを設定
        self.central_widget = self.QtWidgets.QWidget()
        self.main_window.setCentralWidget(self.central_widget)
        
        # メインスプリッターを作成（水平分割）
        self.main_splitter = self.QtWidgets.QSplitter(self.QtCore.Qt.Orientation.Horizontal)
        
        # 左側のスプリッター（垂直分割）
        self.left_splitter = self.QtWidgets.QSplitter(self.QtCore.Qt.Orientation.Vertical)
        
        # 実際のコンポーネントを統合
        self._setup_integrated_components()
        
        # メインレイアウトを設定
        main_layout = self.QtWidgets.QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.main_splitter)
        
        # スプリッターのサイズを設定
        self.main_splitter.setSizes([400, 800])  # 左側400px、右側800px
        self.left_splitter.setSizes([300, 300])  # 上下均等
        
        self.logger.debug("中央ウィジェットを設定しました", LogCategory.UI)
    
    def _setup_integrated_components(self) -> None:
        """統合コンポーネントを設定します"""
        try:
            # テーマエディターを作成
            self._create_theme_editor()
            
            # ゼブラエディターを作成
            self._create_zebra_editor()
            
            # プレビューウィンドウを作成
            self._create_preview_window()
            
            # レイアウトに配置
            self.left_splitter.addWidget(self.zebra_editor)
            self.left_splitter.addWidget(self.theme_editor)
            self.main_splitter.addWidget(self.left_splitter)
            self.main_splitter.addWidget(self.preview_window)
            
            self.logger.info("統合コンポーネントを設定しました", LogCategory.UI)
            
        except Exception as e:
            self.logger.error(f"コンポーネント統合に失敗しました: {str(e)}", LogCategory.UI)
            # フォールバック: プレースホルダーを表示
            self._setup_placeholder()
    
    def _setup_placeholder(self) -> None:
        """プレースホルダーを設定します（フォールバック用）"""
        self.placeholder_label = self.QtWidgets.QLabel("テーマエディターコンポーネントを読み込み中...")
        self.placeholder_label.setAlignment(self.QtCore.Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                font-style: italic;
                padding: 20px;
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
        """)
        self.main_splitter.addWidget(self.placeholder_label)
    
    def _create_theme_editor(self) -> None:
        """テーマエディターを作成します"""
        try:
            from ..views.theme_editor import ThemeEditor
            self.theme_editor_instance = ThemeEditor(self.qt_adapter, self.theme_adapter)
            # MainWindowの参照を渡す
            self.theme_editor_instance.set_main_window_reference(self)
            self.theme_editor = self.theme_editor_instance.create_widget()
            self.logger.debug("テーマエディターを作成しました", LogCategory.UI)
        except Exception as e:
            self.logger.warning(f"テーマエディターの作成に失敗しました: {str(e)}", LogCategory.UI)
            # フォールバック: 簡単なプレースホルダー
            self.theme_editor_instance = None
            self.theme_editor = self._create_component_placeholder("テーマエディター")
    
    def _create_zebra_editor(self) -> None:
        """オートテーマジェネレーターを作成します"""
        try:
            from ..views.zebra_editor import AutoThemeGenerator
            # QtAdapterを渡してAutoThemeGeneratorを作成
            self.zebra_editor_instance = AutoThemeGenerator(self.qt_adapter)
            self.zebra_editor = self.zebra_editor_instance
            self.logger.debug("オートテーマジェネレーターを作成しました", LogCategory.UI)
        except Exception as e:
            self.logger.warning(f"オートテーマジェネレーターの作成に失敗しました: {str(e)}", LogCategory.UI)
            # フォールバック: 簡単なプレースホルダー
            self.zebra_editor_instance = None
            self.zebra_editor = self._create_component_placeholder("オートテーマジェネレーター")
    
    def _create_preview_window(self) -> None:
        """プレビューウィンドウを作成します"""
        try:
            from ..views.preview import PreviewWindow
            self.preview_window_instance = PreviewWindow(self.qt_adapter, self.theme_adapter)
            self.preview_window = self.preview_window_instance.create_widget()
            self.logger.debug("プレビューウィンドウを作成しました", LogCategory.UI)
        except Exception as e:
            self.logger.warning(f"プレビューウィンドウの作成に失敗しました: {str(e)}", LogCategory.UI)
            # フォールバック: 簡単なプレースホルダー
            self.preview_window_instance = None
            self.preview_window = self._create_component_placeholder("プレビューウィンドウ")
    
    def _create_component_placeholder(self, component_name: str) -> Any:
        """コンポーネントプレースホルダーを作成します"""
        placeholder = self.QtWidgets.QWidget()
        layout = self.QtWidgets.QVBoxLayout(placeholder)
        
        label = self.QtWidgets.QLabel(f"{component_name}\n（開発中）")
        label.setAlignment(self.QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                font-style: italic;
                padding: 15px;
                border: 1px solid #dddddd;
                border-radius: 5px;
                background-color: #f5f5f5;
            }
        """)
        
        layout.addWidget(label)
        return placeholder
    
    def _restore_window_state(self) -> None:
        """ウィンドウ状態を復元します"""
        if not self.main_window:
            return
        
        try:
            # QSettingsを使用してウィンドウ状態を復元
            restored = self.settings.restore_window_state(self.main_window)
            
            if restored:
                self.logger.info("ウィンドウ状態を復元しました", LogCategory.UI)
            else:
                self.logger.debug("復元するウィンドウ状態が見つかりませんでした", LogCategory.UI)
                
        except Exception as e:
            self.logger.error(f"ウィンドウ状態の復元に失敗しました: {str(e)}", LogCategory.UI)
    
    def save_window_state(self) -> None:
        """ウィンドウ状態を保存します"""
        if not self.main_window:
            return
        
        try:
            self.settings.save_window_state(self.main_window)
            self.logger.info("ウィンドウ状態を保存しました", LogCategory.UI)
            
        except Exception as e:
            self.logger.error(f"ウィンドウ状態の保存に失敗しました: {str(e)}", LogCategory.UI)
    
    def show(self) -> None:
        """ウィンドウを表示します"""
        if self.main_window:
            self.main_window.show()
            self.logger.info("メインウィンドウを表示しました", LogCategory.UI)
    
    def close(self) -> bool:
        """ウィンドウを閉じます"""
        if not self.main_window:
            return True
        
        # ウィンドウ状態を保存
        self.save_window_state()
        
        # ウィンドウを閉じる
        result = self.main_window.close()
        
        if result:
            self.logger.info("メインウィンドウを閉じました", LogCategory.UI)
        
        return result
    
    def get_action(self, action_name: str) -> Optional[Any]:
        """
        指定された名前のアクションを取得します
        
        Args:
            action_name: アクション名
            
        Returns:
            QAction: アクションオブジェクト（存在しない場合はNone）
        """
        return self.actions.get(action_name)
    
    def set_status_message(self, message: str, timeout: int = 0) -> None:
        """
        ステータスバーにメッセージを表示します
        
        Args:
            message: 表示するメッセージ
            timeout: 表示時間（ミリ秒、0の場合は永続表示）
        """
        if self.status_bar:
            self.status_bar.showMessage(message, timeout)
    
    def update_theme_status(self, theme_name: str) -> None:
        """
        ステータスバーのテーマ情報を更新します
        
        Args:
            theme_name: テーマ名
        """
        if hasattr(self, 'status_theme_label') and self.status_theme_label:
            self.status_theme_label.setText(f"テーマ: {theme_name}")
    
    def set_actions_enabled(self, action_names: list, enabled: bool) -> None:
        """
        指定されたアクションの有効/無効を設定します
        
        Args:
            action_names: アクション名のリスト
            enabled: 有効にする場合True
        """
        for action_name in action_names:
            action = self.get_action(action_name)
            if action:
                action.setEnabled(enabled)
    
    def connect_action(self, action_name: str, slot) -> bool:
        """
        アクションにスロットを接続します
        
        Args:
            action_name: アクション名
            slot: 接続するスロット
            
        Returns:
            bool: 接続に成功した場合True
        """
        action = self.get_action(action_name)
        if action:
            action.triggered.connect(slot)
            return True
        return False
    
    def toggle_toolbar(self, visible: bool) -> None:
        """
        ツールバーの表示/非表示を切り替えます
        
        Args:
            visible: 表示する場合True
        """
        if self.tool_bar:
            self.tool_bar.setVisible(visible)
            if 'toolbar' in self.actions:
                self.actions['toolbar'].setChecked(visible)
    
    def toggle_statusbar(self, visible: bool) -> None:
        """
        ステータスバーの表示/非表示を切り替えます
        
        Args:
            visible: 表示する場合True
        """
        if self.status_bar:
            self.status_bar.setVisible(visible)
            if 'statusbar' in self.actions:
                self.actions['statusbar'].setChecked(visible)
    
    def toggle_fullscreen(self) -> None:
        """フルスクリーン表示を切り替えます"""
        if not self.main_window:
            return
        
        if self.main_window.isFullScreen():
            self.main_window.showNormal()
            if 'fullscreen' in self.actions:
                self.actions['fullscreen'].setChecked(False)
            self.logger.info("フルスクリーン表示を終了しました", LogCategory.UI)
        else:
            self.main_window.showFullScreen()
            if 'fullscreen' in self.actions:
                self.actions['fullscreen'].setChecked(True)
            self.logger.info("フルスクリーン表示に切り替えました", LogCategory.UI)
    
    def get_window(self) -> Optional[Any]:
        """
        メインウィンドウインスタンスを取得します
        
        Returns:
            QMainWindow: メインウィンドウインスタンス
        """
        return self.main_window
    
    def is_created(self) -> bool:
        """
        ウィンドウが作成されているかどうかを確認します
        
        Returns:
            bool: 作成済みの場合True
        """
        return self.main_window is not None
    
    def integrate_components(self, theme_editor, zebra_editor, preview_window) -> None:
        """
        コンポーネントをメインウィンドウに統合します
        
        Args:
            theme_editor: テーマエディターインスタンス
            zebra_editor: ゼブラエディターインスタンス
            preview_window: プレビューウィンドウインスタンス
        """
        if not self.main_window or not self.central_widget:
            self.logger.error("メインウィンドウが初期化されていません", LogCategory.UI)
            return
        
        self.theme_editor = theme_editor
        self.zebra_editor = zebra_editor
        self.preview_window = preview_window
        
        # プレースホルダーを削除
        if self.placeholder_label:
            self.placeholder_label.setParent(None)
            self.placeholder_label = None
        
        # 既存のレイアウトをクリア
        layout = self.central_widget.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
        
        # 新しいレイアウトを作成
        self._setup_integrated_layout()
        
        # コンポーネント間の連携を設定
        self._setup_component_connections()
        
        # メニューアクションを連携
        self._connect_menu_actions()
        
        self.logger.info("コンポーネントを統合しました", LogCategory.UI)
    
    def _setup_integrated_layout(self) -> None:
        """統合レイアウトを設定します"""
        # メインスプリッター（水平分割）
        self.main_splitter = self.QtWidgets.QSplitter(self.QtCore.Qt.Orientation.Horizontal)
        
        # 左側スプリッター（垂直分割：テーマエディター + ゼブラエディター）
        self.left_splitter = self.QtWidgets.QSplitter(self.QtCore.Qt.Orientation.Vertical)
        
        # ゼブラエディターウィジェットを作成・追加
        if self.zebra_editor:
            zebra_editor_widget = self.zebra_editor
            if zebra_editor_widget:
                zebra_editor_dock = self._create_dock_widget("オートテーマジェネレーター", zebra_editor_widget)
                self.left_splitter.addWidget(zebra_editor_dock)
        
        # テーマエディターウィジェットを作成・追加
        if self.theme_editor:
            theme_editor_widget = self.theme_editor.create_widget()
            if theme_editor_widget:
                theme_editor_dock = self._create_dock_widget("テーマエディター", theme_editor_widget)
                self.left_splitter.addWidget(theme_editor_dock)
        
        # プレビューウィンドウウィジェットを作成・追加
        if self.preview_window:
            preview_widget = self.preview_window.create_widget()
            if preview_widget:
                preview_dock = self._create_dock_widget("ライブプレビュー", preview_widget)
                
                # メインスプリッターに追加
                self.main_splitter.addWidget(self.left_splitter)
                self.main_splitter.addWidget(preview_dock)
        
        # スプリッターの初期サイズを設定
        self.main_splitter.setSizes([400, 600])  # 左側40%, 右側60%
        self.left_splitter.setSizes([800, 200])  # テーマエディター60%, ゼブラエディター40%
        
        # 中央ウィジェットのレイアウトに追加
        layout = self.central_widget.layout()
        if not layout:
            layout = self.QtWidgets.QHBoxLayout(self.central_widget)
        layout.addWidget(self.main_splitter)
        
        self.logger.debug("統合レイアウトを設定しました", LogCategory.UI)
    
    def _create_dock_widget(self, title: str, widget: Any) -> Any:
        """ドックウィジェットを作成します
        
        Args:
            title: ドックウィジェットのタイトル
            widget: 内包するウィジェット
            
        Returns:
            QGroupBox: グループボックスとして作成されたドックウィジェット
        """
        dock = self.QtWidgets.QGroupBox(title)
        dock.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = self.QtWidgets.QVBoxLayout(dock)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(widget)
        
        return dock
    
    def _setup_component_connections(self) -> None:
        """コンポーネント間の連携を設定します"""
        # テーマエディターからプレビューウィンドウへの連携
        if self.theme_editor and self.preview_window:
            # テーマ変更時にプレビューを更新
            if hasattr(self.theme_editor, 'set_theme_changed_callback'):
                self.theme_editor.set_theme_changed_callback(self._on_theme_changed)
        
        # オートテーマジェネレーターからの連携
        if self.zebra_editor and self.preview_window:
            # 色変更時にプレビューを更新
            if hasattr(self.zebra_editor, 'colors_changed'):
                self.zebra_editor.colors_changed.connect(self._on_zebra_colors_changed)
            
            # テーマ適用要求の処理
            if hasattr(self.zebra_editor, 'theme_apply_requested'):
                self.zebra_editor.theme_apply_requested.connect(self._on_theme_apply_requested)
        
        # プレビューウィンドウのコールバック設定
        if self.preview_window:
            if hasattr(self.preview_window, 'set_theme_applied_callback'):
                self.preview_window.set_theme_applied_callback(self._on_preview_theme_applied)
        
        self.logger.debug("コンポーネント間の連携を設定しました", LogCategory.UI)
    
    def _on_theme_changed(self, theme_data: Dict[str, Any]) -> None:
        """テーマ変更イベントハンドラ
        
        Args:
            theme_data: 変更されたテーマデータ
        """
        self.current_theme_data = theme_data.copy()
        
        # プレビューウィンドウを更新
        if hasattr(self, 'preview_window_instance') and self.preview_window_instance:
            if hasattr(self.preview_window_instance, 'update_preview'):
                self.preview_window_instance.update_preview(theme_data)
        
        # ステータスバーのテーマ情報を更新
        theme_name = theme_data.get('name', '無題のテーマ')
        self.update_theme_status(theme_name)
        
        # テーマ保存アクションを有効化
        self.set_actions_enabled(['save_theme', 'save_as_theme'], True)
        
        # 未保存状態に設定
        self._set_theme_saved_state(False)
        
        self.logger.debug(f"テーマが変更されました: {theme_name}", LogCategory.UI)
    
    def _on_zebra_colors_changed(self, colors_data: Dict[str, Any]) -> None:
        """ゼブラエディターの色変更イベントハンドラ
        
        Args:
            colors_data: 変更された色データ
        """
        self.logger.debug(f"色変更イベントを受信: {colors_data}", LogCategory.UI)
        self.logger.debug(f"変更前のcurrent_theme_data: {self.current_theme_data}", LogCategory.UI)
        
        # 色データをテーマデータに統合
        if 'colors' not in self.current_theme_data:
            self.current_theme_data['colors'] = {}
        
        # 色調整スライダーからの色データを直接反映
        for color_key, color_value in colors_data.items():
            self.current_theme_data['colors'][color_key] = color_value
        
        self.logger.debug(f"変更後のcurrent_theme_data: {self.current_theme_data}", LogCategory.UI)
        
        # プレビューウィンドウを更新
        if hasattr(self, 'preview_window_instance') and self.preview_window_instance:
            if hasattr(self.preview_window_instance, 'update_preview'):
                self.preview_window_instance.update_preview(self.current_theme_data)
        
        # 未保存状態に設定
        self._set_theme_saved_state(False)
        
        self.logger.debug("オートテーマジェネレーターの色が変更されました", LogCategory.UI)
    
    def _on_theme_apply_requested(self, theme_data: Dict[str, Any]) -> None:
        """オートテーマジェネレーターからのテーマ適用要求ハンドラ
        
        Args:
            theme_data: 適用するテーマデータ
        """
        self.logger.info(f"テーマ適用要求を受信しました: {theme_data.get('name', '無名テーマ')}", LogCategory.UI)
        self.logger.debug(f"適用前のcurrent_theme_data: {self.current_theme_data}", LogCategory.UI)
        
        # 現在のテーマデータを完全に置き換え（updateではなく）
        self.current_theme_data = theme_data.copy()
        
        self.logger.debug(f"適用後のcurrent_theme_data: {self.current_theme_data}", LogCategory.UI)
        
        # テーマエディターに反映
        if hasattr(self, 'theme_editor_instance') and self.theme_editor_instance:
            if hasattr(self.theme_editor_instance, 'load_theme'):
                self.theme_editor_instance.load_theme(theme_data)
        
        # プレビューウィンドウを更新
        if hasattr(self, 'preview_window_instance') and self.preview_window_instance:
            if hasattr(self.preview_window_instance, 'update_theme'):
                self.preview_window_instance.update_theme(theme_data)
        
        # 保存状態をリセット（変更があったことを示す）
        self._set_theme_saved_state(False)
        
        # 保存アクションを有効化
        self.set_actions_enabled(['save_theme', 'save_as_theme'], True)
        
        # ステータスバーに通知
        self.set_status_message("オートテーマジェネレーターからテーマが適用されました", 3000)
        
        self.logger.info(f"オートテーマジェネレーターからテーマを適用しました: {theme_data.get('name', '無名テーマ')}", LogCategory.UI)
    
    def _on_preview_theme_applied(self, theme_data: Dict[str, Any]) -> None:
        """プレビューテーマ適用イベントハンドラ
        
        Args:
            theme_data: 適用されたテーマデータ
        """
        # ステータスメッセージを表示
        self.set_status_message("プレビューを更新しました", 2000)
        
        self.logger.debug("プレビューテーマが適用されました", LogCategory.UI)
    
    def _connect_menu_actions(self) -> None:
        """メニューアクションとコンポーネント機能を連携させます"""
        # テーマエディターの表示/非表示
        if 'theme_editor' in self.actions:
            self.actions['theme_editor'].triggered.connect(self._toggle_theme_editor)
        
        # ゼブラエディターの表示/非表示
        if 'zebra_editor' in self.actions:
            self.actions['zebra_editor'].triggered.connect(self._toggle_zebra_editor)
        
        # ライブプレビューの表示/非表示
        if 'live_preview' in self.actions:
            self.actions['live_preview'].triggered.connect(self._toggle_live_preview)
        
        # プレビュー画像エクスポート
        if 'export_preview' in self.actions and self.preview_window:
            # プレビューウィンドウインスタンスが存在し、メソッドが利用可能な場合のみ接続
            if hasattr(self, 'preview_window_instance') and self.preview_window_instance:
                if hasattr(self.preview_window_instance, 'export_preview_image'):
                    self.actions['export_preview'].triggered.connect(self.preview_window_instance.export_preview_image)
                else:
                    # メソッドが存在しない場合は代替処理
                    self.actions['export_preview'].triggered.connect(self._export_preview_placeholder)
            else:
                # インスタンスが存在しない場合は代替処理
                self.actions['export_preview'].triggered.connect(self._export_preview_placeholder)
        
        # Undo/Redoアクションの連携
        self._connect_undo_redo_actions()
        
        # テーマ操作アクションの連携
        self._connect_theme_actions()
        
        # 表示切り替えアクションの連携
        self._connect_view_actions()
        
        # テーマギャラリーアクションの連携
        self._connect_gallery_actions()
        
        self.logger.debug("メニューアクションを連携しました", LogCategory.UI)
    
    def _connect_gallery_actions(self) -> None:
        """テーマギャラリーアクションを連携します"""
        # テーマメニューのテーマギャラリー
        if 'theme_gallery' in self.actions:
            self.actions['theme_gallery'].triggered.connect(self._show_theme_gallery)
        
        # ツールメニューのテーマギャラリー
        if 'theme_gallery_tools' in self.actions:
            self.actions['theme_gallery_tools'].triggered.connect(self._show_theme_gallery)
        
        self.logger.debug("テーマギャラリーアクションを連携しました", LogCategory.UI)
    
    def _show_theme_gallery(self) -> None:
        """テーマギャラリーを表示します"""
        try:
            # テーマギャラリーのインポート
            from .theme_gallery import ThemeGallery
            
            # ダイアログが既に存在する場合は前面に表示
            if hasattr(self, 'gallery_dialog') and self.gallery_dialog:
                self.gallery_dialog.raise_()
                self.gallery_dialog.activateWindow()
            else:
                # 新しいダイアログを作成
                self.gallery_dialog = ThemeGallery()
                self.gallery_dialog.theme_selected.connect(self._on_gallery_theme_selected)
                self.gallery_dialog.show()
                
            self.logger.debug("テーマギャラリーを表示しました", LogCategory.UI)
            
        except Exception as e:
            self.logger.log_error(f"テーマギャラリーの表示に失敗しました: {str(e)}", e)
            # エラーメッセージを表示
            self.QtWidgets.QMessageBox.critical(
                self.main_window,
                "エラー",
                f"テーマギャラリーの表示に失敗しました:\n{str(e)}"
            )
    
    def _on_gallery_theme_selected(self, theme_path: str) -> None:
        """ギャラリーでテーマが選択された時の処理"""
        try:
            # テーマファイルを読み込み
            if self._load_theme_from_file(theme_path):
                # ギャラリーダイアログを閉じる
                if hasattr(self, 'gallery_dialog') and self.gallery_dialog:
                    self.gallery_dialog.close()
                    self.gallery_dialog = None
                    
                self.logger.debug(f"ギャラリーからテーマを選択しました: {theme_path}", LogCategory.UI)
            else:
                # 読み込みに失敗した場合
                self.QtWidgets.QMessageBox.warning(
                    self.main_window,
                    "テーマ読み込み警告",
                    f"テーマファイルの読み込みに失敗しました:\n{theme_path}"
                )
                
        except Exception as e:
            self.logger.log_error(f"ギャラリーからのテーマ選択処理に失敗しました: {str(e)}", e)
            # エラーメッセージを表示
            self.QtWidgets.QMessageBox.critical(
                self.main_window,
                "エラー",
                f"ギャラリーからのテーマ選択処理に失敗しました:\n{str(e)}"
            )
    
    def _connect_undo_redo_actions(self) -> None:
        """Undo/Redoアクションを連携します"""
        # テーマエディターのUndo/Redoスタックと連携
        if (hasattr(self, 'theme_editor_instance') and self.theme_editor_instance and 
            hasattr(self.theme_editor_instance, 'undo_stack')):
            undo_stack = self.theme_editor_instance.undo_stack
            
            # Undoアクション
            if 'undo' in self.actions:
                self.actions['undo'].triggered.connect(undo_stack.undo)
                undo_stack.canUndoChanged.connect(self.actions['undo'].setEnabled)
                undo_stack.undoTextChanged.connect(
                    lambda text: self.actions['undo'].setText(f"元に戻す: {text}" if text else "元に戻す(&U)")
                )
            
            # Redoアクション
            if 'redo' in self.actions:
                self.actions['redo'].triggered.connect(undo_stack.redo)
                undo_stack.canRedoChanged.connect(self.actions['redo'].setEnabled)
                undo_stack.redoTextChanged.connect(
                    lambda text: self.actions['redo'].setText(f"やり直し: {text}" if text else "やり直し(&R)")
                )
            
            # 初期状態を設定
            if 'undo' in self.actions:
                self.actions['undo'].setEnabled(undo_stack.canUndo())
            if 'redo' in self.actions:
                self.actions['redo'].setEnabled(undo_stack.canRedo())
        else:
            # Undo/Redoスタックが利用できない場合はプレースホルダー処理
            if 'undo' in self.actions:
                self.actions['undo'].triggered.connect(self._undo_placeholder)
                self.actions['undo'].setEnabled(False)  # 初期状態では無効
            if 'redo' in self.actions:
                self.actions['redo'].triggered.connect(self._redo_placeholder)
                self.actions['redo'].setEnabled(False)  # 初期状態では無効
        
        self.logger.debug("Undo/Redoアクションを連携しました", LogCategory.UI)
    
    def _connect_theme_actions(self) -> None:
        """テーマ操作アクションを連携します"""
        # 新規テーマ作成
        if 'new_theme' in self.actions:
            self.actions['new_theme'].triggered.connect(self._new_theme)
        
        # テーマを開く
        if 'open_theme' in self.actions:
            self.actions['open_theme'].triggered.connect(self._open_theme)
        
        # テーマを保存
        if 'save_theme' in self.actions:
            self.actions['save_theme'].triggered.connect(self._save_theme)
        
        # 名前を付けて保存
        if 'save_as_theme' in self.actions:
            self.actions['save_as_theme'].triggered.connect(self._save_theme_as)
        
        # エクスポートアクション
        export_actions = ['export_json', 'export_qss', 'export_css']
        for action_name in export_actions:
            if action_name in self.actions:
                format_type = action_name.replace('export_', '').upper()
                self.actions[action_name].triggered.connect(
                    lambda checked, fmt=format_type: self._export_theme(fmt)
                )
        
        # インポートアクション
        import_actions = ['import_json', 'import_qss', 'import_css']
        for action_name in import_actions:
            if action_name in self.actions:
                format_type = action_name.replace('import_', '').upper()
                self.actions[action_name].triggered.connect(
                    lambda checked, fmt=format_type: self._import_theme(fmt)
                )
        
        # 設定アクション
        if 'preferences' in self.actions:
            self.actions['preferences'].triggered.connect(self._show_preferences_dialog)
        
        self.logger.debug("テーマ操作アクションを連携しました", LogCategory.UI)
    
    def _connect_view_actions(self) -> None:
        """表示切り替えアクションを連携します"""
        # ツールバー表示切り替え
        if 'toolbar' in self.actions:
            self.actions['toolbar'].triggered.connect(self.toggle_toolbar)
        
        # ステータスバー表示切り替え
        if 'statusbar' in self.actions:
            self.actions['statusbar'].triggered.connect(self.toggle_statusbar)
        
        # フルスクリーン切り替え
        if 'fullscreen' in self.actions:
            self.actions['fullscreen'].triggered.connect(self.toggle_fullscreen)
        
        self.logger.debug("表示切り替えアクションを連携しました", LogCategory.UI)
    
    def _new_theme(self) -> None:
        """新規テーマを作成します"""
        self.logger.info("新規テーマ作成が呼び出されました", LogCategory.UI)
        
        # 未保存の変更がある場合は確認
        if self._has_unsaved_changes():
            reply = self.QtWidgets.QMessageBox.question(
                self.main_window,
                "未保存の変更",
                "現在のテーマに未保存の変更があります。新規テーマを作成しますか？",
                self.QtWidgets.QMessageBox.StandardButton.Yes |
                self.QtWidgets.QMessageBox.StandardButton.No,
                self.QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply != self.QtWidgets.QMessageBox.StandardButton.Yes:
                return
        
        # 新規テーマデータを作成
        new_theme_data = {
            'name': '新しいテーマ',
            'version': '1.0.0',
            'colors': {
                'background': '#ffffff',
                'text': '#000000',
                'primary': '#0078d4',
                'secondary': '#6c757d'
            },
            'fonts': {
                'default': {
                    'family': 'Arial',
                    'size': 12,
                    'bold': False,
                    'italic': False
                }
            },
            'properties': {}
        }
        
        # テーマデータを設定
        self.set_theme_data(new_theme_data)
        
        # 保存状態をリセット
        self._set_theme_saved_state(True)
        
        self.set_status_message("新しいテーマを作成しました", 3000)
        self.logger.info("新規テーマを作成しました", LogCategory.UI)
    
    def _create_default_theme(self) -> None:
        """アプリケーション起動時にデフォルトテーマを作成します"""
        self.logger.info("デフォルトテーマを作成しています", LogCategory.UI)
        
        # デフォルトテーマデータを作成
        default_theme_data = {
            'name': 'デフォルトテーマ',
            'version': '1.0.0',
            'colors': {
                'background': '#ffffff',
                'text': '#000000',
                'primary': '#0078d4',
                'secondary': '#6c757d'
            },
            'fonts': {
                'default': {
                    'family': 'Arial',
                    'size': 12,
                    'bold': False,
                    'italic': False
                }
            },
            'properties': {}
        }
        
        # テーマデータを設定
        self.set_theme_data(default_theme_data)
        
        # 保存状態を設定（新規作成なので未保存状態）
        self._set_theme_saved_state(False)
        
        # 保存アクションを有効化
        self.set_actions_enabled(['save_theme', 'save_as_theme'], True)
        
        self.logger.info("デフォルトテーマを作成しました", LogCategory.UI)
    
    def _open_theme(self) -> None:
        """テーマファイルを開きます"""
        self.logger.info("テーマファイルを開くが呼び出されました", LogCategory.UI)
        
        # 未保存の変更がある場合は確認
        if self._has_unsaved_changes():
            reply = self.QtWidgets.QMessageBox.question(
                self.main_window,
                "未保存の変更",
                "現在のテーマに未保存の変更があります。テーマファイルを開きますか？",
                self.QtWidgets.QMessageBox.StandardButton.Yes |
                self.QtWidgets.QMessageBox.StandardButton.No,
                self.QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply != self.QtWidgets.QMessageBox.StandardButton.Yes:
                return
        
        # ファイル選択ダイアログ
        file_path, _ = self.QtWidgets.QFileDialog.getOpenFileName(
            self.main_window,
            "テーマファイルを開く",
            "",
            "テーマファイル (*.json);;すべてのファイル (*)"
        )
        
        if file_path:
            try:
                # テーマファイルを読み込み
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                
                # 複数テーマが含まれているかチェック
                if self._is_multi_theme_file(file_data):
                    # 複数テーマファイルの場合、テーマ選択ダイアログを表示
                    selected_theme = self._show_theme_selection_dialog(file_data, file_path)
                    if selected_theme:
                        self._load_selected_theme(selected_theme, file_path)
                else:
                    # 単一テーマファイルの場合、直接読み込み
                    self.set_theme_data(file_data)
                    self._finalize_theme_loading(file_path)
                
            except Exception as e:
                self.logger.error(f"テーマファイルの読み込みに失敗しました: {str(e)}", LogCategory.UI)
                self.QtWidgets.QMessageBox.critical(
                    self.main_window,
                    "エラー",
                    f"テーマファイルの読み込みに失敗しました:\\n{str(e)}"
                )
    
    def _load_theme_from_file(self, file_path: str) -> bool:
        """指定されたファイルパスからテーマを読み込みます（テスト用）
        
        Args:
            file_path: テーマファイルのパス
            
        Returns:
            bool: 読み込み成功時True
        """
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # テーマデータを設定
            self.set_theme_data(theme_data)
            
            # 最近使用したテーマリストに追加
            self.settings.add_recent_theme(file_path)
            
            # 保存状態を設定
            self._set_theme_saved_state(True)
            
            self.set_status_message(f"テーマファイルを開きました: {file_path}", 3000)
            self.logger.info(f"テーマファイルを開きました: {file_path}", LogCategory.UI)
            
            return True
            
        except Exception as e:
            self.logger.error(f"テーマファイルの読み込みに失敗しました: {str(e)}", LogCategory.UI)
            return False
    
    def _save_theme(self) -> None:
        """現在のテーマを保存します"""
        # 現在のテーマファイルパスがある場合はそのまま保存
        current_path = getattr(self, 'current_theme_path', None)
        if current_path:
            self._save_theme_to_file(current_path)
        else:
            # パスがない場合は名前を付けて保存
            self._save_theme_as()
    
    def _save_theme_as(self) -> None:
        """テーマに名前を付けて保存します"""
        # ファイル保存ダイアログ
        theme_name = self.current_theme_data.get('name', '新しいテーマ')
        default_filename = f"{theme_name}.json"
        
        file_path, _ = self.QtWidgets.QFileDialog.getSaveFileName(
            self.main_window,
            "テーマを保存",
            default_filename,
            "テーマファイル (*.json);;すべてのファイル (*)"
        )
        
        if file_path:
            self._save_theme_to_file(file_path)
    
    def _save_theme_to_file(self, file_path: str) -> None:
        """テーマをファイルに保存します
        
        Args:
            file_path: 保存先ファイルパス
        """
        try:
            self.logger.info(f"テーマ保存処理を開始: {file_path}", LogCategory.UI)
            self.logger.debug(f"保存するテーマデータ: {self.current_theme_data}", LogCategory.UI)
            
            # テーマデータをJSONファイルに保存（プレースホルダー実装）
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_theme_data, f, ensure_ascii=False, indent=2)
            
            # 現在のテーマファイルパスを記録
            self.current_theme_path = file_path
            
            # 最近使用したテーマリストに追加
            self.settings.add_recent_theme(file_path)
            
            # 保存状態を設定
            self._set_theme_saved_state(True)
            
            self.set_status_message(f"テーマを保存しました: {file_path}", 3000)
            self.logger.info(f"テーマを保存しました: {file_path}", LogCategory.UI)
            
        except Exception as e:
            self.logger.error(f"テーマの保存に失敗しました: {str(e)}", LogCategory.UI)
            self.QtWidgets.QMessageBox.critical(
                self.main_window,
                "エラー",
                f"テーマの保存に失敗しました:\\n{str(e)}"
            )
    
    def _export_theme(self, format_type: str) -> None:
        """テーマをエクスポートします
        
        Args:
            format_type: エクスポート形式（JSON, QSS, CSS）
        """
        # ファイル保存ダイアログ
        theme_name = self.current_theme_data.get('name', '新しいテーマ')
        extension = format_type.lower()
        default_filename = f"{theme_name}.{extension}"
        
        file_filter = f"{format_type}ファイル (*.{extension});;すべてのファイル (*)"
        
        file_path, _ = self.QtWidgets.QFileDialog.getSaveFileName(
            self.main_window,
            f"テーマを{format_type}形式でエクスポート",
            default_filename,
            file_filter
        )
        
        if file_path:
            try:
                # エクスポート処理（プレースホルダー実装）
                if self.theme_adapter:
                    exported_content = self.theme_adapter.export_theme(self.current_theme_data, format_type)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(exported_content)
                    
                    self.set_status_message(f"テーマを{format_type}形式でエクスポートしました: {file_path}", 3000)
                    self.logger.info(f"テーマを{format_type}形式でエクスポートしました: {file_path}", LogCategory.UI)
                else:
                    raise Exception("テーマアダプターが利用できません")
                    
            except Exception as e:
                self.logger.error(f"テーマのエクスポートに失敗しました: {str(e)}", LogCategory.UI)
                self.QtWidgets.QMessageBox.critical(
                    self.main_window,
                    "エラー",
                    f"テーマのエクスポートに失敗しました:\\n{str(e)}"
                )
    
    def _import_theme(self, format_type: str) -> None:
        """テーマをインポートします
        
        Args:
            format_type: インポート形式（JSON, QSS, CSS）
        """
        # 未保存の変更がある場合は確認
        if self._has_unsaved_changes():
            reply = self.QtWidgets.QMessageBox.question(
                self.main_window,
                "未保存の変更",
                "現在のテーマに未保存の変更があります。テーマをインポートしますか？",
                self.QtWidgets.QMessageBox.StandardButton.Yes |
                self.QtWidgets.QMessageBox.StandardButton.No,
                self.QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply != self.QtWidgets.QMessageBox.StandardButton.Yes:
                return
        
        # ファイル選択ダイアログ
        extension = format_type.lower()
        file_filter = f"{format_type}ファイル (*.{extension});;すべてのファイル (*)"
        
        file_path, _ = self.QtWidgets.QFileDialog.getOpenFileName(
            self.main_window,
            f"{format_type}形式のテーマファイルをインポート",
            "",
            file_filter
        )
        
        if file_path:
            try:
                # インポート処理（プレースホルダー実装）
                if self.theme_adapter:
                    theme_data = self.theme_adapter.import_theme(file_path, format_type)
                    
                    # テーマデータを設定
                    self.set_theme_data(theme_data)
                    
                    # 保存状態をリセット
                    self._set_theme_saved_state(False)
                    
                    self.set_status_message(f"{format_type}形式のテーマをインポートしました: {file_path}", 3000)
                    self.logger.info(f"{format_type}形式のテーマをインポートしました: {file_path}", LogCategory.UI)
                else:
                    raise Exception("テーマアダプターが利用できません")
                    
            except Exception as e:
                self.logger.error(f"テーマのインポートに失敗しました: {str(e)}", LogCategory.UI)
                self.QtWidgets.QMessageBox.critical(
                    self.main_window,
                    "エラー",
                    f"テーマのインポートに失敗しました:\\n{str(e)}"
                )
    
    def _is_multi_theme_file(self, file_data: dict) -> bool:
        """ファイルが複数テーマを含むかどうかを判定します"""
        # qt_theme_manager形式の複数テーマファイルかチェック
        return ('available_themes' in file_data and 
                isinstance(file_data['available_themes'], dict) and
                len(file_data['available_themes']) > 1)
    
    def _show_theme_selection_dialog(self, file_data: dict, file_path: str) -> dict:
        """テーマ選択ダイアログを表示します"""
        available_themes = file_data.get('available_themes', {})
        
        # ダイアログを作成
        dialog = self.QtWidgets.QDialog(self.main_window)
        dialog.setWindowTitle("テーマを選択")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = self.QtWidgets.QVBoxLayout(dialog)
        
        # 説明ラベル
        info_label = self.QtWidgets.QLabel(f"ファイル: {file_path}\n\n利用可能なテーマから1つを選択してください:")
        layout.addWidget(info_label)
        
        # テーマリスト
        theme_list = self.QtWidgets.QListWidget()
        
        for theme_key, theme_data in available_themes.items():
            display_name = theme_data.get('display_name', theme_key)
            description = theme_data.get('description', '')
            
            item = self.QtWidgets.QListWidgetItem()
            item.setText(f"{display_name}")
            item.setToolTip(f"{display_name}\n{description}")
            item.setData(self.QtCore.Qt.ItemDataRole.UserRole, theme_data)
            
            theme_list.addItem(item)
        
        layout.addWidget(theme_list)
        
        # プレビューエリア
        preview_group = self.QtWidgets.QGroupBox("プレビュー")
        preview_layout = self.QtWidgets.QVBoxLayout(preview_group)
        
        preview_label = self.QtWidgets.QLabel("テーマを選択するとプレビューが表示されます")
        preview_label.setAlignment(self.QtCore.Qt.AlignmentFlag.AlignCenter)
        preview_label.setMinimumHeight(100)
        preview_label.setStyleSheet("border: 1px solid #ccc; padding: 10px;")
        preview_layout.addWidget(preview_label)
        
        layout.addWidget(preview_group)
        
        # ボタン
        button_layout = self.QtWidgets.QHBoxLayout()
        
        ok_button = self.QtWidgets.QPushButton("選択")
        cancel_button = self.QtWidgets.QPushButton("キャンセル")
        
        ok_button.setEnabled(False)  # 初期状態では無効
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # イベント接続
        def on_selection_changed():
            current_item = theme_list.currentItem()
            if current_item:
                ok_button.setEnabled(True)
                theme_data = current_item.data(self.QtCore.Qt.ItemDataRole.UserRole)
                
                # プレビュー更新
                preview_text = f"テーマ名: {theme_data.get('display_name', 'N/A')}\n"
                preview_text += f"説明: {theme_data.get('description', 'N/A')}\n"
                preview_text += f"主要色: {theme_data.get('primaryColor', 'N/A')}\n"
                preview_text += f"背景色: {theme_data.get('backgroundColor', 'N/A')}"
                
                preview_label.setText(preview_text)
                preview_label.setStyleSheet(f"""
                    border: 1px solid #ccc; 
                    padding: 10px;
                    background-color: {theme_data.get('backgroundColor', '#ffffff')};
                    color: {theme_data.get('textColor', '#000000')};
                """)
            else:
                ok_button.setEnabled(False)
        
        theme_list.currentItemChanged.connect(on_selection_changed)
        
        def on_ok():
            dialog.accept()
        
        def on_cancel():
            dialog.reject()
        
        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(on_cancel)
        
        # ダイアログ実行
        if dialog.exec() == self.QtWidgets.QDialog.DialogCode.Accepted:
            current_item = theme_list.currentItem()
            if current_item:
                return current_item.data(self.QtCore.Qt.ItemDataRole.UserRole)
        
        return None
    
    def _load_selected_theme(self, theme_data: dict, file_path: str) -> None:
        """選択されたテーマを読み込みます"""
        # qt_theme_manager形式からQt-Theme-Studio形式に変換
        converted_theme = self._convert_qt_theme_manager_format(theme_data)
        
        # テーマデータを設定
        self.set_theme_data(converted_theme)
        
        # 元ファイル情報を保存（将来の保存機能用）
        self.current_source_file = file_path
        self.current_source_theme_key = theme_data.get('name', 'unknown')
        
        self._finalize_theme_loading(file_path, theme_data.get('display_name', 'テーマ'))
    
    def _convert_qt_theme_manager_format(self, theme_data: dict) -> dict:
        """qt_theme_manager形式をQt-Theme-Studio形式に変換します"""
        converted = {
            'name': theme_data.get('display_name', theme_data.get('name', 'テーマ')),
            'version': '1.0.0',
            'description': theme_data.get('description', ''),
            'colors': {},
            'fonts': {
                'default': {
                    'family': 'Arial',
                    'size': 12,
                    'bold': False,
                    'italic': False
                }
            },
            'properties': {}
        }
        
        # 色の変換
        color_mapping = {
            'background': theme_data.get('backgroundColor', '#ffffff'),
            'text': theme_data.get('textColor', '#000000'),
            'primary': theme_data.get('primaryColor', '#007acc'),
            'accent': theme_data.get('accentColor', '#0078d4'),
        }
        
        # ボタン色
        if 'button' in theme_data:
            button = theme_data['button']
            color_mapping.update({
                'button_background': button.get('background', '#f0f0f0'),
                'button_text': button.get('text', '#000000'),
                'button_hover': button.get('hover', '#e0e0e0'),
                'button_pressed': button.get('pressed', '#d0d0d0'),
                'button_border': button.get('border', '#cccccc'),
            })
        
        # パネル色
        if 'panel' in theme_data:
            panel = theme_data['panel']
            color_mapping.update({
                'panel_background': panel.get('background', '#f8f8f8'),
                'panel_border': panel.get('border', '#ddd'),
            })
            
            if 'zebra' in panel:
                color_mapping['zebra_alternate'] = panel['zebra'].get('alternate', '#e9e9e9')
        
        # テキスト色
        if 'text' in theme_data:
            text = theme_data['text']
            color_mapping.update({
                'text_primary': text.get('primary', '#2d3748'),
                'text_secondary': text.get('secondary', '#4a5568'),
                'text_muted': text.get('muted', '#718096'),
                'text_heading': text.get('heading', '#1a202c'),
                'text_link': text.get('link', '#0078d4'),
                'text_success': text.get('success', '#38a169'),
                'text_warning': text.get('warning', '#d69e2e'),
                'text_error': text.get('error', '#e53e3e'),
            })
        
        converted['colors'] = color_mapping
        return converted
    
    def _finalize_theme_loading(self, file_path: str, theme_name: str = None) -> None:
        """テーマ読み込みの最終処理"""
        # 最近使用したテーマリストに追加
        self.settings.add_recent_theme(file_path)
        
        # 保存状態を設定
        self._set_theme_saved_state(True)
        
        display_name = theme_name or "テーマ"
        self.set_status_message(f"{display_name}を読み込みました: {file_path}", 3000)
        self.logger.info(f"{display_name}を読み込みました: {file_path}", LogCategory.UI)
    
    def _export_preview_placeholder(self) -> None:
        """プレビュー画像エクスポートのプレースホルダー処理"""
        self.logger.info("プレビュー画像エクスポートが呼び出されました（プレースホルダー）", LogCategory.UI)
        self.QtWidgets.QMessageBox.information(
            self.main_window,
            "情報",
            "プレビュー画像エクスポート機能は現在開発中です。"
        )
    
    def _undo_placeholder(self) -> None:
        """元に戻すのプレースホルダー処理"""
        self.logger.info("元に戻すが呼び出されました（プレースホルダー）", LogCategory.UI)
        self.set_status_message("元に戻す機能は現在利用できません", 2000)
    
    def _redo_placeholder(self) -> None:
        """やり直しのプレースホルダー処理"""
        self.logger.info("やり直しが呼び出されました（プレースホルダー）", LogCategory.UI)
        self.set_status_message("やり直し機能は現在利用できません", 2000)
    
    def _show_preferences_dialog(self) -> None:
        """設定ダイアログを表示します"""
        self.logger.info("設定ダイアログが呼び出されました", LogCategory.UI)
        
        # 設定ダイアログを作成
        dialog = self.QtWidgets.QDialog(self.main_window)
        dialog.setWindowTitle("設定")
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        # メインレイアウト
        main_layout = self.QtWidgets.QVBoxLayout(dialog)
        
        # タブウィジェット
        tab_widget = self.QtWidgets.QTabWidget()
        
        # 一般設定タブ
        general_tab = self._create_general_settings_tab()
        tab_widget.addTab(general_tab, "一般")
        
        # テーマ設定タブ
        theme_tab = self._create_theme_settings_tab()
        tab_widget.addTab(theme_tab, "テーマ")
        
        # エディター設定タブ
        editor_tab = self._create_editor_settings_tab()
        tab_widget.addTab(editor_tab, "エディター")
        
        # アクセシビリティ設定タブ
        accessibility_tab = self._create_accessibility_settings_tab()
        tab_widget.addTab(accessibility_tab, "アクセシビリティ")
        
        # ライブプレビュー設定タブ
        live_preview_tab = self._create_live_preview_settings_tab()
        tab_widget.addTab(live_preview_tab, "ライブプレビュー")
        
        main_layout.addWidget(tab_widget)
        
        # ボタン
        button_layout = self.QtWidgets.QHBoxLayout()
        
        # デフォルトに戻すボタン
        reset_button = self.QtWidgets.QPushButton("デフォルトに戻す")
        reset_button.clicked.connect(lambda: self._reset_settings_to_default(dialog))
        
        # OK/キャンセルボタン
        ok_button = self.QtWidgets.QPushButton("OK")
        cancel_button = self.QtWidgets.QPushButton("キャンセル")
        apply_button = self.QtWidgets.QPushButton("適用")
        
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)
        
        main_layout.addLayout(button_layout)
        
        # ボタンイベント
        ok_button.clicked.connect(lambda: self._apply_settings_and_close(dialog))
        cancel_button.clicked.connect(dialog.reject)
        apply_button.clicked.connect(lambda: self._apply_settings(dialog))
        
        # ダイアログ表示
        if dialog.exec() == self.QtWidgets.QDialog.DialogCode.Accepted:
            self.logger.info("設定が適用されました", LogCategory.UI)
        else:
            self.logger.info("設定がキャンセルされました", LogCategory.UI)
    
    def _create_general_settings_tab(self) -> Any:
        """一般設定タブを作成します"""
        widget = self.QtWidgets.QWidget()
        layout = self.QtWidgets.QVBoxLayout(widget)
        
        # 言語設定
        lang_group = self.QtWidgets.QGroupBox("言語設定")
        lang_layout = self.QtWidgets.QFormLayout(lang_group)
        
        lang_combo = self.QtWidgets.QComboBox()
        lang_combo.addItems(["日本語", "English"])
        lang_combo.setCurrentText("日本語")
        lang_layout.addRow("表示言語:", lang_combo)
        
        layout.addWidget(lang_group)
        
        # 起動設定
        startup_group = self.QtWidgets.QGroupBox("起動設定")
        startup_layout = self.QtWidgets.QVBoxLayout(startup_group)
        
        restore_session_cb = self.QtWidgets.QCheckBox("前回のセッションを復元する")
        restore_session_cb.setChecked(True)
        startup_layout.addWidget(restore_session_cb)
        
        show_splash_cb = self.QtWidgets.QCheckBox("起動時にスプラッシュスクリーンを表示する")
        show_splash_cb.setChecked(False)
        startup_layout.addWidget(show_splash_cb)
        
        layout.addWidget(startup_group)
        
        # 自動保存設定
        autosave_group = self.QtWidgets.QGroupBox("自動保存")
        autosave_layout = self.QtWidgets.QFormLayout(autosave_group)
        
        autosave_cb = self.QtWidgets.QCheckBox("自動保存を有効にする")
        autosave_cb.setChecked(True)
        autosave_layout.addRow(autosave_cb)
        
        autosave_interval = self.QtWidgets.QSpinBox()
        autosave_interval.setRange(1, 60)
        autosave_interval.setValue(5)
        autosave_interval.setSuffix(" 分")
        autosave_layout.addRow("自動保存間隔:", autosave_interval)
        
        layout.addWidget(autosave_group)
        
        layout.addStretch()
        return widget
    
    def _create_theme_settings_tab(self) -> Any:
        """テーマ設定タブを作成します"""
        widget = self.QtWidgets.QWidget()
        layout = self.QtWidgets.QVBoxLayout(widget)
        
        # アプリケーションテーマ
        app_theme_group = self.QtWidgets.QGroupBox("アプリケーションテーマ")
        app_theme_layout = self.QtWidgets.QFormLayout(app_theme_group)
        
        app_theme_combo = self.QtWidgets.QComboBox()
        app_theme_combo.addItems(["システム", "ライト", "ダーク"])
        app_theme_combo.setCurrentText("システム")
        app_theme_layout.addRow("テーマ:", app_theme_combo)
        
        layout.addWidget(app_theme_group)
        
        # デフォルトテーマ設定
        default_theme_group = self.QtWidgets.QGroupBox("デフォルトテーマ")
        default_theme_layout = self.QtWidgets.QVBoxLayout(default_theme_group)
        
        default_theme_info = self.QtWidgets.QLabel("新規テーマ作成時のデフォルト設定")
        default_theme_layout.addWidget(default_theme_info)
        
        # デフォルト色設定
        color_layout = self.QtWidgets.QFormLayout()
        
        primary_color_btn = self.QtWidgets.QPushButton("#007acc")
        primary_color_btn.setStyleSheet("background-color: #007acc; color: white;")
        color_layout.addRow("主要色:", primary_color_btn)
        
        bg_color_btn = self.QtWidgets.QPushButton("#ffffff")
        bg_color_btn.setStyleSheet("background-color: #ffffff; color: black; border: 1px solid #ccc;")
        color_layout.addRow("背景色:", bg_color_btn)
        
        default_theme_layout.addLayout(color_layout)
        layout.addWidget(default_theme_group)
        
        layout.addStretch()
        return widget
    
    def _create_editor_settings_tab(self) -> Any:
        """エディター設定タブを作成します"""
        widget = self.QtWidgets.QWidget()
        layout = self.QtWidgets.QVBoxLayout(widget)
        
        # グリッド設定
        grid_group = self.QtWidgets.QGroupBox("グリッド設定")
        grid_layout = self.QtWidgets.QVBoxLayout(grid_group)
        
        show_grid_cb = self.QtWidgets.QCheckBox("グリッドを表示する")
        show_grid_cb.setChecked(False)
        grid_layout.addWidget(show_grid_cb)
        
        snap_to_grid_cb = self.QtWidgets.QCheckBox("グリッドにスナップする")
        snap_to_grid_cb.setChecked(False)
        grid_layout.addWidget(snap_to_grid_cb)
        
        layout.addWidget(grid_group)
        
        # 色選択設定
        color_group = self.QtWidgets.QGroupBox("色選択設定")
        color_layout = self.QtWidgets.QFormLayout(color_group)
        
        color_format_combo = self.QtWidgets.QComboBox()
        color_format_combo.addItems(["HEX", "RGB", "HSL", "HSV"])
        color_format_combo.setCurrentText("HEX")
        color_layout.addRow("デフォルト色形式:", color_format_combo)
        
        show_color_names_cb = self.QtWidgets.QCheckBox("色名を表示する")
        show_color_names_cb.setChecked(True)
        color_layout.addRow(show_color_names_cb)
        
        layout.addWidget(color_group)
        
        layout.addStretch()
        return widget
    
    def _create_accessibility_settings_tab(self) -> Any:
        """アクセシビリティ設定タブを作成します"""
        widget = self.QtWidgets.QWidget()
        layout = self.QtWidgets.QVBoxLayout(widget)
        
        # WCAG設定
        wcag_group = self.QtWidgets.QGroupBox("WCAG準拠設定")
        wcag_layout = self.QtWidgets.QFormLayout(wcag_group)
        
        wcag_level_combo = self.QtWidgets.QComboBox()
        wcag_level_combo.addItems(["AA", "AAA"])
        wcag_level_combo.setCurrentText("AA")
        wcag_layout.addRow("WCAG準拠レベル:", wcag_level_combo)
        
        auto_check_cb = self.QtWidgets.QCheckBox("自動アクセシビリティチェックを有効にする")
        auto_check_cb.setChecked(True)
        wcag_layout.addRow(auto_check_cb)
        
        layout.addWidget(wcag_group)
        
        # コントラスト設定
        contrast_group = self.QtWidgets.QGroupBox("コントラスト設定")
        contrast_layout = self.QtWidgets.QVBoxLayout(contrast_group)
        
        show_contrast_cb = self.QtWidgets.QCheckBox("コントラスト比を常に表示する")
        show_contrast_cb.setChecked(True)
        contrast_layout.addWidget(show_contrast_cb)
        
        warn_low_contrast_cb = self.QtWidgets.QCheckBox("低コントラストの場合に警告する")
        warn_low_contrast_cb.setChecked(True)
        contrast_layout.addWidget(warn_low_contrast_cb)
        
        layout.addWidget(contrast_group)
        
        # フォント設定
        font_group = self.QtWidgets.QGroupBox("フォント設定")
        font_layout = self.QtWidgets.QFormLayout(font_group)
        
        ui_font_btn = self.QtWidgets.QPushButton("フォントを選択...")
        font_layout.addRow("UIフォント:", ui_font_btn)
        
        font_size_spin = self.QtWidgets.QSpinBox()
        font_size_spin.setRange(8, 24)
        font_size_spin.setValue(12)
        font_layout.addRow("フォントサイズ:", font_size_spin)
        
        layout.addWidget(font_group)
        
        layout.addStretch()
        return widget
    
    def _create_live_preview_settings_tab(self) -> Any:
        """ライブプレビュー設定タブを作成します"""
        widget = self.QtWidgets.QWidget()
        layout = self.QtWidgets.QVBoxLayout(widget)
        
        # ライブプレビュー設定
        live_preview_group = self.QtWidgets.QGroupBox("ライブプレビュー設定")
        live_preview_layout = self.QtWidgets.QVBoxLayout(live_preview_group)
        
        live_preview_cb = self.QtWidgets.QCheckBox("リアルタイムプレビューを有効にする")
        live_preview_cb.setChecked(True)
        live_preview_layout.addWidget(live_preview_cb)
        
        preview_delay_layout = self.QtWidgets.QFormLayout()
        preview_delay = self.QtWidgets.QSpinBox()
        preview_delay.setRange(0, 2000)
        preview_delay.setValue(300)
        preview_delay.setSuffix(" ms")
        preview_delay_layout.addRow("プレビュー更新遅延:", preview_delay)
        live_preview_layout.addLayout(preview_delay_layout)
        
        layout.addWidget(live_preview_group)
        
        layout.addStretch()
        return widget
    
    def _apply_settings_and_close(self, dialog) -> None:
        """設定を適用してダイアログを閉じます"""
        self._apply_settings(dialog)
        dialog.accept()
    
    def _apply_settings(self, dialog) -> None:
        """設定を適用します"""
        self.logger.info("設定を適用しています", LogCategory.UI)
        # TODO: 実際の設定適用処理を実装
        self.set_status_message("設定を適用しました", 2000)
    
    def _reset_settings_to_default(self, dialog) -> None:
        """設定をデフォルトに戻します"""
        reply = self.QtWidgets.QMessageBox.question(
            dialog,
            "設定をリセット",
            "すべての設定をデフォルト値に戻しますか？",
            self.QtWidgets.QMessageBox.StandardButton.Yes |
            self.QtWidgets.QMessageBox.StandardButton.No,
            self.QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == self.QtWidgets.QMessageBox.StandardButton.Yes:
            self.logger.info("設定をデフォルトにリセットしました", LogCategory.UI)
            # TODO: 実際のリセット処理を実装
            self.set_status_message("設定をデフォルトにリセットしました", 2000)
    
    def _has_unsaved_changes(self) -> bool:
        """未保存の変更があるかどうかを確認します
        
        Returns:
            bool: 未保存の変更がある場合True
        """
        return getattr(self, '_theme_saved', True) == False
    
    def _set_theme_saved_state(self, saved: bool) -> None:
        """テーマの保存状態を設定します
        
        Args:
            saved: 保存済みの場合True
        """
        self._theme_saved = saved
        
        # ウィンドウタイトルを更新
        if self.main_window:
            theme_name = self.current_theme_data.get('name', '無題のテーマ')
            title = f"Qt-Theme-Studio - {theme_name}"
            if not saved:
                title += " *"  # 未保存マーク
            self.main_window.setWindowTitle(title)
        
        # 保存アクションの有効/無効を設定
        self.set_actions_enabled(['save_theme'], not saved)
    
    def update_undo_redo_state(self) -> None:
        """Undo/Redoアクションの状態を更新します"""
        if self.theme_editor and hasattr(self.theme_editor, 'undo_stack'):
            undo_stack = self.theme_editor.undo_stack
            
            if 'undo' in self.actions:
                self.actions['undo'].setEnabled(undo_stack.canUndo())
            
            if 'redo' in self.actions:
                self.actions['redo'].setEnabled(undo_stack.canRedo())
        
        self.logger.debug("Undo/Redoアクションの状態を更新しました", LogCategory.UI)
    
    def _toggle_theme_editor(self, visible: bool) -> None:
        """テーマエディターの表示/非表示を切り替えます
        
        Args:
            visible: 表示する場合True
        """
        if self.left_splitter and self.left_splitter.count() > 0:
            theme_editor_dock = self.left_splitter.widget(0)
            if theme_editor_dock:
                theme_editor_dock.setVisible(visible)
                self.logger.debug(f"テーマエディターの表示を{'有効' if visible else '無効'}にしました", LogCategory.UI)
    
    def _toggle_zebra_editor(self, visible: bool) -> None:
        """オートテーマジェネレーターの表示/非表示を切り替えます
        
        Args:
            visible: 表示する場合True
        """
        if self.left_splitter and self.left_splitter.count() > 1:
            zebra_editor_dock = self.left_splitter.widget(1)
            if zebra_editor_dock:
                zebra_editor_dock.setVisible(visible)
                self.logger.debug(f"オートテーマジェネレーターの表示を{'有効' if visible else '無効'}にしました", LogCategory.UI)
    
    def _toggle_live_preview(self, visible: bool) -> None:
        """ライブプレビューの表示/非表示を切り替えます
        
        Args:
            visible: 表示する場合True
        """
        if self.main_splitter and self.main_splitter.count() > 1:
            preview_dock = self.main_splitter.widget(1)
            if preview_dock:
                preview_dock.setVisible(visible)
                self.logger.debug(f"ライブプレビューの表示を{'有効' if visible else '無効'}にしました", LogCategory.UI)
    
    def get_current_theme_data(self) -> Dict[str, Any]:
        """現在のテーマデータを取得します
        
        Returns:
            Dict[str, Any]: 現在のテーマデータ
        """
        return self.current_theme_data.copy()
    
    def set_theme_data(self, theme_data: Dict[str, Any]) -> None:
        """テーマデータを設定します
        
        Args:
            theme_data: 設定するテーマデータ
        """
        self.current_theme_data = theme_data.copy()
        
        # 各コンポーネントにテーマデータを反映
        if hasattr(self, 'theme_editor_instance') and self.theme_editor_instance:
            if hasattr(self.theme_editor_instance, 'set_theme_data'):
                self.theme_editor_instance.set_theme_data(theme_data)
            elif hasattr(self.theme_editor_instance, 'load_theme'):
                self.theme_editor_instance.load_theme(theme_data)
        
        if hasattr(self, 'zebra_editor_instance') and self.zebra_editor_instance and hasattr(self.zebra_editor_instance, 'set_color_data'):
            # テーマジェネレーター用の色データを抽出
            zebra_colors = {}
            for key, value in theme_data.get('colors', {}).items():
                if key.startswith('zebra_'):
                    # zebra_通常テキスト_fg -> 通常テキスト
                    parts = key.replace('zebra_', '').split('_')
                    if len(parts) >= 2:
                        label = ' '.join(parts[:-1]).title()
                        color_type = parts[-1]
                        
                        if label not in zebra_colors:
                            zebra_colors[label] = {}
                        
                        if color_type == 'fg':
                            zebra_colors[label]['foreground'] = value
                        elif color_type == 'bg':
                            zebra_colors[label]['background'] = value
            
            if zebra_colors:
                self.zebra_editor_instance.set_color_data(zebra_colors)
        
        if hasattr(self, 'preview_window_instance') and self.preview_window_instance:
            if hasattr(self.preview_window_instance, 'update_preview'):
                self.preview_window_instance.update_preview(theme_data)
        
        # ステータスバーを更新
        theme_name = theme_data.get('name', '無題のテーマ')
        self.update_theme_status(theme_name)
        
        self.logger.info(f"テーマデータを設定しました: {theme_name}", LogCategory.UI)
    
    def _setup_close_event_handler(self) -> None:
        """クローズイベントハンドラーを設定します"""
        if not self.main_window:
            return
        
        # 元のcloseEventをオーバーライド
        original_close_event = self.main_window.closeEvent
        
        def close_event_handler(event):
            """クローズイベントハンドラー"""
            # 未保存の変更がある場合は確認
            if self._has_unsaved_changes():
                reply = self.QtWidgets.QMessageBox.question(
                    self.main_window,
                    "未保存の変更",
                    "テーマに未保存の変更があります。保存しますか？",
                    self.QtWidgets.QMessageBox.StandardButton.Save |
                    self.QtWidgets.QMessageBox.StandardButton.Discard |
                    self.QtWidgets.QMessageBox.StandardButton.Cancel,
                    self.QtWidgets.QMessageBox.StandardButton.Save
                )
                
                if reply == self.QtWidgets.QMessageBox.StandardButton.Save:
                    # 保存してから終了
                    self._save_theme()
                    if self._has_unsaved_changes():  # 保存がキャンセルされた場合
                        event.ignore()
                        return
                elif reply == self.QtWidgets.QMessageBox.StandardButton.Cancel:
                    # 終了をキャンセル
                    event.ignore()
                    return
                # Discardの場合はそのまま終了
            
            # ウィンドウ状態を保存
            self.save_window_state()
            
            # 元のcloseEventを呼び出し
            if original_close_event:
                original_close_event(event)
            else:
                event.accept()
        
        # closeEventを置き換え
        self.main_window.closeEvent = close_event_handler
        
        self.logger.debug("クローズイベントハンドラーを設定しました", LogCategory.UI)
    
    def reset_workspace(self) -> None:
        """
        ワークスペースをデフォルト状態にリセットします
        
        ウィンドウサイズ、位置、レイアウトをデフォルト値に戻し、
        ユーザーに確認ダイアログを表示します。
        """
        if not self.main_window:
            return
        
        # 確認ダイアログを表示
        reply = self.QtWidgets.QMessageBox.question(
            self.main_window,
            "ワークスペースリセット",
            "ワークスペースをデフォルト状態にリセットしますか？\n"
            "現在のウィンドウレイアウトと設定が失われます。",
            self.QtWidgets.QMessageBox.StandardButton.Yes | 
            self.QtWidgets.QMessageBox.StandardButton.No,
            self.QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == self.QtWidgets.QMessageBox.StandardButton.Yes:
            self._perform_workspace_reset()
    
    def _perform_workspace_reset(self) -> None:
        """ワークスペースリセットを実行します"""
        try:
            # 現在の設定をクリア
            settings_manager = self.settings.get_settings_manager()
            
            # ウィンドウ関連の設定をクリア
            settings_manager.remove_value("window/geometry")
            settings_manager.remove_value("window/windowState")
            settings_manager.remove_value("window/maximized")
            
            # スプリッター状態をクリア
            settings_manager.begin_group("splitters")
            keys = settings_manager.get_all_keys()
            for key in keys:
                settings_manager.remove_value(key)
            settings_manager.end_group()
            
            # ドック状態をクリア
            settings_manager.begin_group("docks")
            keys = settings_manager.get_all_keys()
            for key in keys:
                settings_manager.remove_value(key)
            settings_manager.end_group()
            
            # ワークスペース状態をクリア
            workspace_manager = self.settings.get_workspace_manager()
            workspace_manager.clear_workspace()
            
            # 設定を同期
            settings_manager.sync()
            
            # ウィンドウをデフォルト状態に戻す
            self._reset_window_to_defaults()
            
            # ツールバーとステータスバーを表示状態に戻す
            self.toggle_toolbar(True)
            self.toggle_statusbar(True)
            
            # フルスクリーンを解除
            if self.main_window.isFullScreen():
                self.main_window.showNormal()
                if 'fullscreen' in self.actions:
                    self.actions['fullscreen'].setChecked(False)
            
            # 成功メッセージを表示
            self.set_status_message("ワークスペースをリセットしました", 3000)
            
            self.logger.info("ワークスペースをリセットしました", LogCategory.UI)
            
        except Exception as e:
            self.logger.error(f"ワークスペースリセットに失敗しました: {str(e)}", LogCategory.UI)
            
            # エラーメッセージを表示
            self.QtWidgets.QMessageBox.critical(
                self.main_window,
                "エラー",
                f"ワークスペースのリセットに失敗しました:\n{str(e)}"
            )
    
    def _reset_window_to_defaults(self) -> None:
        """ウィンドウをデフォルト状態に戻します"""
        if not self.main_window:
            return
        
        # デフォルトサイズに戻す
        default_width = self.settings.get_setting('window.width', 1200)
        default_height = self.settings.get_setting('window.height', 800)
        self.main_window.resize(default_width, default_height)
        
        # ウィンドウを画面中央に配置
        self._center_window()
        
        # 最大化を解除
        if self.main_window.isMaximized():
            self.main_window.showNormal()
    
    def save_layout_state(self) -> Dict[str, Any]:
        """
        現在のレイアウト状態を保存します
        
        Returns:
            Dict[str, Any]: レイアウト状態データ
        """
        if not self.main_window:
            return {}
        
        layout_state = {}
        
        try:
            # ウィンドウの基本情報
            layout_state['window'] = {
                'geometry': self.main_window.saveGeometry(),
                'state': self.main_window.saveState(),
                'maximized': self.main_window.isMaximized(),
                'fullscreen': self.main_window.isFullScreen()
            }
            
            # ツールバーの状態
            layout_state['toolbar'] = {
                'visible': self.tool_bar.isVisible() if self.tool_bar else True,
                'area': self.main_window.toolBarArea(self.tool_bar) if self.tool_bar else None
            }
            
            # ステータスバーの状態
            layout_state['statusbar'] = {
                'visible': self.status_bar.isVisible() if self.status_bar else True
            }
            
            # メニューアクションの状態
            layout_state['actions'] = {}
            for action_name, action in self.actions.items():
                if action.isCheckable():
                    layout_state['actions'][action_name] = action.isChecked()
            
            self.logger.debug("レイアウト状態を保存しました", LogCategory.UI)
            return layout_state
            
        except Exception as e:
            self.logger.error(f"レイアウト状態の保存に失敗しました: {str(e)}", LogCategory.UI)
            return {}
    
    def restore_layout_state(self, layout_state: Dict[str, Any]) -> bool:
        """
        レイアウト状態を復元します
        
        Args:
            layout_state: レイアウト状態データ
            
        Returns:
            bool: 復元に成功した場合True
        """
        if not self.main_window or not layout_state:
            return False
        
        try:
            # ウィンドウ状態の復元
            if 'window' in layout_state:
                window_data = layout_state['window']
                
                if 'geometry' in window_data:
                    self.main_window.restoreGeometry(window_data['geometry'])
                
                if 'state' in window_data:
                    self.main_window.restoreState(window_data['state'])
                
                if 'maximized' in window_data and window_data['maximized']:
                    self.main_window.showMaximized()
                
                if 'fullscreen' in window_data and window_data['fullscreen']:
                    self.main_window.showFullScreen()
            
            # ツールバー状態の復元
            if 'toolbar' in layout_state and self.tool_bar:
                toolbar_data = layout_state['toolbar']
                
                if 'visible' in toolbar_data:
                    self.toggle_toolbar(toolbar_data['visible'])
            
            # ステータスバー状態の復元
            if 'statusbar' in layout_state and self.status_bar:
                statusbar_data = layout_state['statusbar']
                
                if 'visible' in statusbar_data:
                    self.toggle_statusbar(statusbar_data['visible'])
            
            # アクション状態の復元
            if 'actions' in layout_state:
                actions_data = layout_state['actions']
                
                for action_name, checked in actions_data.items():
                    if action_name in self.actions:
                        action = self.actions[action_name]
                        if action.isCheckable():
                            action.setChecked(checked)
            
            self.logger.info("レイアウト状態を復元しました", LogCategory.UI)
            return True
            
        except Exception as e:
            self.logger.error(f"レイアウト状態の復元に失敗しました: {str(e)}", LogCategory.UI)
            return False
    
    def save_window_geometry(self) -> None:
        """ウィンドウのジオメトリ情報を保存します"""
        if not self.main_window:
            return
        
        try:
            # 現在のウィンドウ情報を設定に保存
            self.settings.set_setting('window.width', self.main_window.width())
            self.settings.set_setting('window.height', self.main_window.height())
            self.settings.set_setting('window.x', self.main_window.x())
            self.settings.set_setting('window.y', self.main_window.y())
            self.settings.set_setting('window.maximized', self.main_window.isMaximized())
            
            self.logger.debug("ウィンドウジオメトリを保存しました", LogCategory.UI)
            
        except Exception as e:
            self.logger.error(f"ウィンドウジオメトリの保存に失敗しました: {str(e)}", LogCategory.UI)
    
    def restore_window_geometry(self) -> None:
        """ウィンドウのジオメトリ情報を復元します"""
        if not self.main_window:
            return
        
        try:
            # 設定からウィンドウ情報を復元
            width = self.settings.get_setting('window.width', 1200)
            height = self.settings.get_setting('window.height', 800)
            x = self.settings.get_setting('window.x', None)
            y = self.settings.get_setting('window.y', None)
            maximized = self.settings.get_setting('window.maximized', False)
            
            # サイズを設定
            self.main_window.resize(width, height)
            
            # 位置を設定（保存されている場合）
            if x is not None and y is not None:
                self.main_window.move(x, y)
            else:
                # 保存されていない場合は中央に配置
                self._center_window()
            
            # 最大化状態を復元
            if maximized:
                self.main_window.showMaximized()
            
            self.logger.debug("ウィンドウジオメトリを復元しました", LogCategory.UI)
            
        except Exception as e:
            self.logger.error(f"ウィンドウジオメトリの復元に失敗しました: {str(e)}", LogCategory.UI)
    
    def get_current_workspace_state(self) -> Dict[str, Any]:
        """
        現在のワークスペース状態を取得します
        
        Returns:
            Dict[str, Any]: ワークスペース状態データ
        """
        workspace_state = {}
        
        try:
            # レイアウト状態
            workspace_state['layout'] = self.save_layout_state()
            
            # 現在開いているテーマ情報（将来的に実装）
            workspace_state['current_theme'] = None
            
            # エディターの状態（将来的に実装）
            workspace_state['editor_state'] = {}
            
            # プレビューの状態（将来的に実装）
            workspace_state['preview_state'] = {}
            
            self.logger.debug("ワークスペース状態を取得しました", LogCategory.UI)
            return workspace_state
            
        except Exception as e:
            self.logger.error(f"ワークスペース状態の取得に失敗しました: {str(e)}", LogCategory.UI)
            return {}
    
    def apply_workspace_state(self, workspace_state: Dict[str, Any]) -> bool:
        """
        ワークスペース状態を適用します
        
        Args:
            workspace_state: ワークスペース状態データ
            
        Returns:
            bool: 適用に成功した場合True
        """
        if not workspace_state:
            return False
        
        try:
            # レイアウト状態の適用
            if 'layout' in workspace_state:
                self.restore_layout_state(workspace_state['layout'])
            
            # その他の状態は将来的に実装
            
            self.logger.info("ワークスペース状態を適用しました", LogCategory.UI)
            return True
            
        except Exception as e:
            self.logger.error(f"ワークスペース状態の適用に失敗しました: {str(e)}", LogCategory.UI)
            return False
    
    def setup_close_event_handler(self) -> None:
        """ウィンドウクローズイベントハンドラーを設定します"""
        if not self.main_window:
            return
        
        # 元のcloseEventを保存
        original_close_event = self.main_window.closeEvent
        
        def close_event_handler(event):
            """ウィンドウクローズイベントハンドラー"""
            try:
                # ウィンドウ状態を保存
                self.save_window_state()
                self.save_window_geometry()
                
                # ワークスペース状態を保存
                workspace_state = self.get_current_workspace_state()
                self.settings.save_workspace_state(workspace_state)
                
                self.logger.info("アプリケーション終了時の状態保存が完了しました", LogCategory.UI)
                
                # 元のcloseEventを呼び出し
                if original_close_event:
                    original_close_event(event)
                else:
                    event.accept()
                    
            except Exception as e:
                self.logger.error(f"終了時の状態保存に失敗しました: {str(e)}", LogCategory.UI)
                event.accept()  # エラーが発生してもアプリケーションは終了させる
        
        # closeEventハンドラーを設定
        self.main_window.closeEvent = close_event_handler    

    def show_help_dialog(self) -> None:
        """ヘルプダイアログを表示します"""
        try:
            help_dialog = HelpDialog(self.main_window)
            help_dialog.exec()
            self.logger.info("ヘルプダイアログを表示しました", LogCategory.UI)
        except Exception as e:
            self.logger.error(f"ヘルプダイアログの表示に失敗しました: {str(e)}", LogCategory.UI)
            self.QtWidgets.QMessageBox.critical(
                self.main_window,
                "エラー",
                f"ヘルプダイアログの表示に失敗しました:\\n{str(e)}"
            )
    
    def show_user_manual(self) -> None:
        """ユーザーマニュアルを表示します"""
        # ユーザーマニュアルファイルのパスを取得
        import os
        manual_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'docs', 'user_manual.html')
        
        if os.path.exists(manual_path):
            try:
                # デフォルトブラウザでマニュアルを開く
                import webbrowser
                webbrowser.open(f'file://{os.path.abspath(manual_path)}')
                self.logger.info("ユーザーマニュアルを開きました", LogCategory.UI)
            except Exception as e:
                self.logger.error(f"ユーザーマニュアルの表示に失敗しました: {str(e)}", LogCategory.UI)
                self.QtWidgets.QMessageBox.critical(
                    self.main_window,
                    "エラー",
                    f"ユーザーマニュアルの表示に失敗しました:\\n{str(e)}"
                )
        else:
            # マニュアルファイルが存在しない場合はヘルプダイアログを表示
            self.show_help_dialog()
    
    def show_about_dialog(self) -> None:
        """アプリケーション情報ダイアログを表示します"""
        about_text = """
        <h2>Qt-Theme-Studio</h2>
        <p>バージョン: 1.0.0</p>
        <p>Qtアプリケーション向けの統合テーマエディター</p>
        
        <h3>主な機能</h3>
        <ul>
            <li>直感的なビジュアルテーマエディター</li>
            <li>WCAG準拠のアクセシビリティ機能</li>
            <li>リアルタイムプレビューシステム</li>
            <li>多形式インポート・エクスポート</li>
        </ul>
        
        <h3>対応フレームワーク</h3>
        <ul>
            <li>PySide6</li>
            <li>PyQt6</li>
            <li>PyQt5</li>
        </ul>
        
        <p><small>© 2024 Qt-Theme-Studio Project</small></p>
        """
        
        self.QtWidgets.QMessageBox.about(
            self.main_window,
            "Qt-Theme-Studioについて",
            about_text
        )
        self.logger.info("アプリケーション情報ダイアログを表示しました", LogCategory.UI)    

    def _connect_help_actions(self) -> None:
        """ヘルプアクションを接続します"""
        # ヘルプダイアログ
        if 'help' in self.actions:
            self.actions['help'].triggered.connect(self.show_help_dialog)
        
        # ユーザーマニュアル
        if 'user_manual' in self.actions:
            self.actions['user_manual'].triggered.connect(self.show_user_manual)
        
        # アプリケーション情報
        if 'about' in self.actions:
            self.actions['about'].triggered.connect(self.show_about_dialog)
        
        self.logger.debug("ヘルプアクションを接続しました", LogCategory.UI)