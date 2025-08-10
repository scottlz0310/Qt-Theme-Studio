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


class MainWindow:
    """
    Qt-Theme-Studioメインウィンドウクラス
    
    アプリケーションのメインウィンドウを管理し、メニューバー、ツールバー、
    ステータスバーの基本構造を提供します。日本語UIテキストを使用し、
    ウィンドウ状態の保存・復元機能を統合します。
    """
    
    def __init__(self, qt_adapter: QtAdapter, theme_adapter, settings: ApplicationSettings):
        """
        メインウィンドウを初期化します
        
        Args:
            qt_adapter: Qt フレームワークアダプター
            theme_adapter: テーマアダプター
            settings: アプリケーション設定管理
        """
        self.qt_adapter = qt_adapter
        self.theme_adapter = theme_adapter
        self.settings = settings
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
        
        # メニューアクション
        self.actions: Dict[str, Any] = {}
        
        # メインウィンドウを作成
        self.create_window()
        
        self.logger.info("メインウィンドウを初期化しました", LogCategory.UI)
        self.central_widget: Optional[Any] = None
        
        # メニューアクション
        self.actions: Dict[str, Any] = {}
        
        self.logger.info("メインウィンドウを初期化しました", LogCategory.UI)
    
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
        self.setup_close_event_handler()
        
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
        
        # ゼブラパターンエディター
        zebra_editor_action = self.QtGui.QAction("ゼブラパターンエディター(&Z)", self.main_window)
        zebra_editor_action.setStatusTip("WCAG準拠のゼブラパターンエディターを開きます")
        zebra_editor_action.setCheckable(True)
        theme_menu.addAction(zebra_editor_action)
        self.actions['zebra_editor'] = zebra_editor_action
        
        theme_menu.addSeparator()
        
        # テーマギャラリー
        gallery_action = self.QtGui.QAction("テーマギャラリー(&G)", self.main_window)
        gallery_action.setStatusTip("テーマギャラリーを開きます")
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
        # 実際のコンテンツは後で他のコンポーネントが設定する
        self.central_widget = self.QtWidgets.QWidget()
        self.main_window.setCentralWidget(self.central_widget)
        
        # 基本レイアウトを設定
        layout = self.QtWidgets.QHBoxLayout(self.central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # プレースホルダーラベル
        placeholder_label = self.QtWidgets.QLabel("テーマエディターコンポーネントがここに表示されます")
        placeholder_label.setAlignment(self.QtCore.Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("""
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
        layout.addWidget(placeholder_label)
        
        self.logger.debug("中央ウィジェットを設定しました", LogCategory.UI)
    
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