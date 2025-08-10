"""
ヘルプダイアログモジュール

Qt-Theme-Studioのアプリケーション内ヘルプシステムを提供します。
日本語でのヘルプコンテンツ表示と機能説明を行います。
"""

from typing import Dict, List, Optional
from qt_theme_studio.adapters.qt_adapter import QtAdapter

# Qt モジュールの動的インポート
qt_modules = QtAdapter().get_qt_modules()
QDialog = qt_modules['QtWidgets'].QDialog
QVBoxLayout = qt_modules['QtWidgets'].QVBoxLayout
QHBoxLayout = qt_modules['QtWidgets'].QHBoxLayout
QTextBrowser = qt_modules['QtWidgets'].QTextBrowser
QTreeWidget = qt_modules['QtWidgets'].QTreeWidget
QTreeWidgetItem = qt_modules['QtWidgets'].QTreeWidgetItem
QPushButton = qt_modules['QtWidgets'].QPushButton
QSplitter = qt_modules['QtWidgets'].QSplitter
QLabel = qt_modules['QtWidgets'].QLabel
QFrame = qt_modules['QtWidgets'].QFrame
Qt = qt_modules['QtCore'].Qt
QSize = qt_modules['QtCore'].QSize
pyqtSignal = qt_modules['QtCore'].pyqtSignal if 'pyqtSignal' in qt_modules['QtCore'].__dict__ else qt_modules['QtCore'].Signal


class HelpDialog(QDialog):
    """
    アプリケーション内ヘルプダイアログ
    
    日本語でのヘルプコンテンツを提供し、機能説明とガイドを統合します。
    """
    
    def __init__(self, parent=None):
        """
        ヘルプダイアログを初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.help_content = self._load_help_content()
        self._setup_ui()
        self._setup_connections()
        self._load_initial_content()
    
    def _setup_ui(self) -> None:
        """UIコンポーネントを設定"""
        self.setWindowTitle("Qt-Theme-Studio ヘルプ")
        self.setMinimumSize(QSize(800, 600))
        self.resize(1000, 700)
        
        # メインレイアウト
        main_layout = QVBoxLayout(self)
        
        # ヘッダー
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("Qt-Theme-Studio ヘルプシステム")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        header_layout.addWidget(title_label)
        
        main_layout.addWidget(header_frame)
        
        # スプリッター（左：目次、右：コンテンツ）
        splitter = QSplitter(Qt.Horizontal)
        
        # 左側：目次ツリー
        self.toc_tree = QTreeWidget()
        self.toc_tree.setHeaderLabel("目次")
        self.toc_tree.setMaximumWidth(300)
        self._populate_toc()
        
        # 右側：ヘルプコンテンツ
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(False)
        
        splitter.addWidget(self.toc_tree)
        splitter.addWidget(self.content_browser)
        splitter.setSizes([250, 750])
        
        main_layout.addWidget(splitter)
        
        # ボタンレイアウト
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("閉じる")
        self.close_button.setMinimumWidth(100)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
    
    def _setup_connections(self) -> None:
        """シグナル・スロット接続を設定"""
        self.toc_tree.itemClicked.connect(self._on_toc_item_clicked)
        self.close_button.clicked.connect(self.accept)
    
    def _populate_toc(self) -> None:
        """目次ツリーを構築"""
        # 基本操作
        basic_item = QTreeWidgetItem(self.toc_tree, ["基本操作"])
        QTreeWidgetItem(basic_item, ["アプリケーションの起動"])
        QTreeWidgetItem(basic_item, ["メインウィンドウの概要"])
        QTreeWidgetItem(basic_item, ["新規テーマの作成"])
        QTreeWidgetItem(basic_item, ["テーマの保存と読み込み"])
        
        # テーマエディター
        editor_item = QTreeWidgetItem(self.toc_tree, ["テーマエディター"])
        QTreeWidgetItem(editor_item, ["色の設定"])
        QTreeWidgetItem(editor_item, ["フォントの設定"])
        QTreeWidgetItem(editor_item, ["プロパティの編集"])
        QTreeWidgetItem(editor_item, ["リアルタイムプレビュー"])
        
        # ゼブラパターンエディター
        zebra_item = QTreeWidgetItem(self.toc_tree, ["ゼブラパターンエディター"])
        QTreeWidgetItem(zebra_item, ["WCAG準拠について"])
        QTreeWidgetItem(zebra_item, ["コントラスト比の計算"])
        QTreeWidgetItem(zebra_item, ["色の改善提案"])
        QTreeWidgetItem(zebra_item, ["アクセシビリティレベル"])
        
        # プレビューシステム
        preview_item = QTreeWidgetItem(self.toc_tree, ["プレビューシステム"])
        QTreeWidgetItem(preview_item, ["ライブプレビューの使用"])
        QTreeWidgetItem(preview_item, ["ウィジェット表示"])
        QTreeWidgetItem(preview_item, ["プレビュー画像のエクスポート"])
        QTreeWidgetItem(preview_item, ["レスポンシブテスト"])
        
        # テーマ管理
        management_item = QTreeWidgetItem(self.toc_tree, ["テーマ管理"])
        QTreeWidgetItem(management_item, ["テーマギャラリー"])
        QTreeWidgetItem(management_item, ["インポート・エクスポート"])
        QTreeWidgetItem(management_item, ["テーマテンプレート"])
        QTreeWidgetItem(management_item, ["最近使用したテーマ"])
        
        # 高度な機能
        advanced_item = QTreeWidgetItem(self.toc_tree, ["高度な機能"])
        QTreeWidgetItem(advanced_item, ["Undo/Redo操作"])
        QTreeWidgetItem(advanced_item, ["設定のカスタマイズ"])
        QTreeWidgetItem(advanced_item, ["キーボードショートカット"])
        QTreeWidgetItem(advanced_item, ["トラブルシューティング"])
        
        # すべてのアイテムを展開
        self.toc_tree.expandAll()
    
    def _load_help_content(self) -> Dict[str, str]:
        """ヘルプコンテンツを読み込み"""
        return {
            "welcome": self._get_welcome_content(),
            "アプリケーションの起動": self._get_startup_content(),
            "メインウィンドウの概要": self._get_main_window_content(),
            "新規テーマの作成": self._get_new_theme_content(),
            "テーマの保存と読み込み": self._get_save_load_content(),
            "色の設定": self._get_color_setting_content(),
            "フォントの設定": self._get_font_setting_content(),
            "プロパティの編集": self._get_property_editing_content(),
            "リアルタイムプレビュー": self._get_realtime_preview_content(),
            "WCAG準拠について": self._get_wcag_content(),
            "コントラスト比の計算": self._get_contrast_content(),
            "色の改善提案": self._get_color_improvement_content(),
            "アクセシビリティレベル": self._get_accessibility_level_content(),
            "ライブプレビューの使用": self._get_live_preview_content(),
            "ウィジェット表示": self._get_widget_display_content(),
            "プレビュー画像のエクスポート": self._get_preview_export_content(),
            "レスポンシブテスト": self._get_responsive_test_content(),
            "テーマギャラリー": self._get_theme_gallery_content(),
            "インポート・エクスポート": self._get_import_export_content(),
            "テーマテンプレート": self._get_template_content(),
            "最近使用したテーマ": self._get_recent_themes_content(),
            "Undo/Redo操作": self._get_undo_redo_content(),
            "設定のカスタマイズ": self._get_settings_content(),
            "キーボードショートカット": self._get_shortcuts_content(),
            "トラブルシューティング": self._get_troubleshooting_content(),
        }
    
    def _load_initial_content(self) -> None:
        """初期コンテンツを読み込み"""
        self.content_browser.setHtml(self.help_content["welcome"])
    
    def _on_toc_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        目次アイテムクリック時の処理
        
        Args:
            item: クリックされたアイテム
            column: カラム番号
        """
        item_text = item.text(0)
        if item_text in self.help_content:
            self.content_browser.setHtml(self.help_content[item_text])
    
    def _get_welcome_content(self) -> str:
        """ウェルカムコンテンツを取得"""
        return """
        <h1>Qt-Theme-Studio へようこそ</h1>
        
        <p>Qt-Theme-Studioは、Qtアプリケーション向けの統合テーマエディターです。
        直感的なビジュアルインターフェースを使用して、美しくアクセシブルなテーマを作成できます。</p>
        
        <h2>主な機能</h2>
        <ul>
            <li><strong>統合テーマエディター</strong>: 色、フォント、プロパティの直感的な編集</li>
            <li><strong>ゼブラパターンエディター</strong>: WCAG準拠のアクセシブルなテーマ作成</li>
            <li><strong>ライブプレビュー</strong>: リアルタイムでのテーマ確認</li>
            <li><strong>テーマ管理</strong>: インポート、エクスポート、テンプレート機能</li>
        </ul>
        
        <h2>はじめに</h2>
        <p>左側の目次から興味のあるトピックを選択してください。
        基本操作から始めることをお勧めします。</p>
        
        <p><em>ヒント: このヘルプは「ヘルプ」メニューからいつでもアクセスできます。</em></p>
        """

    def _get_startup_content(self) -> str:
        """アプリケーション起動のヘルプコンテンツ"""
        return """
        <h1>アプリケーションの起動</h1>
        
        <h2>起動方法</h2>
        <p>Qt-Theme-Studioは以下の方法で起動できます：</p>
        
        <h3>1. 統合ランチャーを使用</h3>
        <pre>python launch_theme_studio.py</pre>
        
        <h3>2. モジュールとして実行</h3>
        <pre>python -m qt_theme_studio</pre>
        
        <h2>システム要件</h2>
        <ul>
            <li>Python 3.8以上</li>
            <li>PySide6、PyQt6、またはPyQt5のいずれか</li>
            <li>qt-theme-managerライブラリ</li>
        </ul>
        
        <h2>初回起動時</h2>
        <p>初回起動時には、アプリケーションが自動的に以下を行います：</p>
        <ul>
            <li>利用可能なQtフレームワークの検出</li>
            <li>qt-theme-managerライブラリの初期化</li>
            <li>デフォルト設定の作成</li>
        </ul>
        
        <p><strong>注意:</strong> Qtフレームワークが見つからない場合は、
        エラーメッセージが表示されます。インストール手順に従ってください。</p>
        """
    
    def _get_main_window_content(self) -> str:
        """メインウィンドウのヘルプコンテンツ"""
        return """
        <h1>メインウィンドウの概要</h1>
        
        <h2>ウィンドウ構成</h2>
        <p>メインウィンドウは以下の要素で構成されています：</p>
        
        <h3>メニューバー</h3>
        <ul>
            <li><strong>ファイル</strong>: テーマの新規作成、開く、保存、エクスポート</li>
            <li><strong>編集</strong>: Undo/Redo、設定</li>
            <li><strong>表示</strong>: プレビュー、ツールバーの表示切り替え</li>
            <li><strong>ツール</strong>: ゼブラパターンエディター、テーマギャラリー</li>
            <li><strong>ヘルプ</strong>: このヘルプ、バージョン情報</li>
        </ul>
        
        <h3>ツールバー</h3>
        <p>よく使用する機能へのクイックアクセスを提供します：</p>
        <ul>
            <li>新規テーマ作成</li>
            <li>テーマを開く</li>
            <li>テーマを保存</li>
            <li>Undo/Redo</li>
            <li>プレビュー表示切り替え</li>
        </ul>
        
        <h3>作業エリア</h3>
        <p>中央の作業エリアには、選択したエディターが表示されます：</p>
        <ul>
            <li>テーマエディター（デフォルト）</li>
            <li>ゼブラパターンエディター</li>
            <li>テーマギャラリー</li>
        </ul>
        
        <h3>ステータスバー</h3>
        <p>現在の状態や操作結果を表示します。</p>
        """
    
    def _get_new_theme_content(self) -> str:
        """新規テーマ作成のヘルプコンテンツ"""
        return """
        <h1>新規テーマの作成</h1>
        
        <h2>テーマ作成手順</h2>
        
        <h3>1. 新規テーマの開始</h3>
        <ul>
            <li>「ファイル」→「新規テーマ」を選択</li>
            <li>またはツールバーの「新規」ボタンをクリック</li>
            <li>キーボードショートカット: Ctrl+N</li>
        </ul>
        
        <h3>2. テーマ名の設定</h3>
        <p>テーマ名入力ダイアログが表示されます。
        わかりやすい名前を入力してください。</p>
        
        <h3>3. ベーステンプレートの選択</h3>
        <p>以下のオプションから選択できます：</p>
        <ul>
            <li><strong>空のテーマ</strong>: ゼロから作成</li>
            <li><strong>ライトテーマ</strong>: 明るい色調のベース</li>
            <li><strong>ダークテーマ</strong>: 暗い色調のベース</li>
            <li><strong>ハイコントラスト</strong>: アクセシビリティ重視</li>
        </ul>
        
        <h3>4. 編集開始</h3>
        <p>テーマエディターが開き、編集を開始できます。
        変更は自動的にプレビューに反映されます。</p>
        
        <h2>ヒント</h2>
        <ul>
            <li>テンプレートを使用すると、効率的にテーマを作成できます</li>
            <li>プレビューを確認しながら調整しましょう</li>
            <li>定期的に保存することをお勧めします</li>
        </ul>
        """
    
    def _get_save_load_content(self) -> str:
        """保存・読み込みのヘルプコンテンツ"""
        return """
        <h1>テーマの保存と読み込み</h1>
        
        <h2>テーマの保存</h2>
        
        <h3>基本的な保存</h3>
        <ul>
            <li>「ファイル」→「保存」を選択</li>
            <li>キーボードショートカット: Ctrl+S</li>
            <li>初回保存時はファイル名を指定</li>
        </ul>
        
        <h3>名前を付けて保存</h3>
        <ul>
            <li>「ファイル」→「名前を付けて保存」を選択</li>
            <li>キーボードショートカット: Ctrl+Shift+S</li>
            <li>新しいファイル名で保存</li>
        </ul>
        
        <h3>対応ファイル形式</h3>
        <ul>
            <li><strong>.json</strong>: Qt-Theme-Studio標準形式</li>
            <li><strong>.qss</strong>: Qt Style Sheet形式</li>
            <li><strong>.css</strong>: CSS形式（互換性用）</li>
        </ul>
        
        <h2>テーマの読み込み</h2>
        
        <h3>ファイルから開く</h3>
        <ul>
            <li>「ファイル」→「開く」を選択</li>
            <li>キーボードショートカット: Ctrl+O</li>
            <li>対応形式のファイルを選択</li>
        </ul>
        
        <h3>最近使用したテーマ</h3>
        <ul>
            <li>「ファイル」→「最近使用したテーマ」から選択</li>
            <li>最大10個のテーマが記録されます</li>
        </ul>
        
        <h2>自動保存機能</h2>
        <p>作業内容は定期的に自動保存されます。
        アプリケーションが予期せず終了した場合でも、
        次回起動時に復旧オプションが表示されます。</p>
        """
    
    def _get_color_setting_content(self) -> str:
        """色設定のヘルプコンテンツ"""
        return """
        <h1>色の設定</h1>
        
        <h2>カラーピッカーの使用</h2>
        
        <h3>色の選択方法</h3>
        <ul>
            <li><strong>カラーホイール</strong>: 直感的な色選択</li>
            <li><strong>RGB値入力</strong>: 数値での正確な指定</li>
            <li><strong>16進値入力</strong>: #RRGGBB形式での指定</li>
            <li><strong>HSV値入力</strong>: 色相・彩度・明度での指定</li>
        </ul>
        
        <h3>色の種類</h3>
        <p>以下の色を設定できます：</p>
        <ul>
            <li><strong>プライマリ色</strong>: メインの色調</li>
            <li><strong>セカンダリ色</strong>: アクセント色</li>
            <li><strong>背景色</strong>: ウィンドウの背景</li>
            <li><strong>テキスト色</strong>: 文字の色</li>
            <li><strong>ボーダー色</strong>: 境界線の色</li>
            <li><strong>選択色</strong>: 選択時のハイライト</li>
        </ul>
        
        <h2>色の調和</h2>
        <p>「色の調和」機能を使用すると、
        選択した色に調和する色の組み合わせが自動提案されます。</p>
        
        <h3>調和パターン</h3>
        <ul>
            <li><strong>補色</strong>: 対照的な色の組み合わせ</li>
            <li><strong>類似色</strong>: 近い色相の組み合わせ</li>
            <li><strong>三色配色</strong>: 均等に配置された3色</li>
            <li><strong>分割補色</strong>: 補色の変化形</li>
        </ul>
        
        <h2>アクセシビリティ</h2>
        <p>色を選択する際は、コントラスト比を確認してください。
        WCAG準拠のテーマを作成するには、
        ゼブラパターンエディターの使用をお勧めします。</p>
        """
    
    def _get_font_setting_content(self) -> str:
        """フォント設定のヘルプコンテンツ"""
        return """
        <h1>フォントの設定</h1>
        
        <h2>フォント選択</h2>
        
        <h3>フォントファミリー</h3>
        <p>システムにインストールされているフォントから選択できます：</p>
        <ul>
            <li>システムフォント一覧から選択</li>
            <li>フォント名の直接入力</li>
            <li>フォールバックフォントの指定</li>
        </ul>
        
        <h3>フォントサイズ</h3>
        <ul>
            <li><strong>ポイント単位</strong>: 印刷に適した単位</li>
            <li><strong>ピクセル単位</strong>: 画面表示に適した単位</li>
            <li>スライダーまたは数値入力で調整</li>
        </ul>
        
        <h3>フォントスタイル</h3>
        <ul>
            <li><strong>太字</strong>: 重要な要素の強調</li>
            <li><strong>斜体</strong>: 補足情報の表示</li>
            <li><strong>下線</strong>: リンクやアクティブ要素</li>
            <li><strong>取り消し線</strong>: 削除された内容</li>
        </ul>
        
        <h2>フォントカテゴリ</h2>
        <p>用途別にフォントを設定できます：</p>
        
        <h3>UI要素別設定</h3>
        <ul>
            <li><strong>メニューフォント</strong>: メニューバー、コンテキストメニュー</li>
            <li><strong>ボタンフォント</strong>: プッシュボタン、チェックボックス</li>
            <li><strong>ラベルフォント</strong>: 静的テキスト表示</li>
            <li><strong>入力フォント</strong>: テキストフィールド、テキストエリア</li>
            <li><strong>リストフォント</strong>: リスト、ツリー、テーブル</li>
        </ul>
        
        <h2>フォントプレビュー</h2>
        <p>フォント設定の変更は、リアルタイムでプレビューに反映されます。
        実際のアプリケーションでの見た目を確認しながら調整してください。</p>
        
        <h2>推奨事項</h2>
        <ul>
            <li>読みやすさを重視してフォントサイズを選択</li>
            <li>システム標準フォントの使用を推奨</li>
            <li>異なるプラットフォームでの表示を考慮</li>
        </ul>
        """

    def _get_property_editing_content(self) -> str:
        """プロパティ編集のヘルプコンテンツ"""
        return """
        <h1>プロパティの編集</h1>
        
        <h2>プロパティエディター</h2>
        <p>プロパティエディターでは、テーマの詳細な設定を行えます。</p>
        
        <h3>プロパティの種類</h3>
        <ul>
            <li><strong>色プロパティ</strong>: 背景色、文字色、ボーダー色など</li>
            <li><strong>サイズプロパティ</strong>: 幅、高さ、マージン、パディング</li>
            <li><strong>フォントプロパティ</strong>: フォントファミリー、サイズ、スタイル</li>
            <li><strong>効果プロパティ</strong>: 影、グラデーション、透明度</li>
        </ul>
        
        <h3>編集方法</h3>
        <ul>
            <li><strong>直接入力</strong>: 値を直接入力</li>
            <li><strong>スライダー</strong>: 数値の範囲調整</li>
            <li><strong>チェックボックス</strong>: 有効/無効の切り替え</li>
            <li><strong>ドロップダウン</strong>: 選択肢から選択</li>
        </ul>
        
        <h2>ウィジェット別設定</h2>
        <p>Qtウィジェットごとに個別の設定が可能です：</p>
        
        <h3>ボタン系</h3>
        <ul>
            <li>QPushButton: 通常、ホバー、押下時の状態</li>
            <li>QCheckBox: チェック済み/未チェック状態</li>
            <li>QRadioButton: 選択済み/未選択状態</li>
        </ul>
        
        <h3>入力系</h3>
        <ul>
            <li>QLineEdit: フォーカス時の枠線色</li>
            <li>QTextEdit: 選択テキストの背景色</li>
            <li>QComboBox: ドロップダウンの表示設定</li>
        </ul>
        
        <h3>表示系</h3>
        <ul>
            <li>QListWidget: 項目の選択色、ホバー色</li>
            <li>QTreeWidget: 展開アイコン、インデント</li>
            <li>QTableWidget: ヘッダー、グリッド線</li>
        </ul>
        
        <h2>高度な設定</h2>
        <ul>
            <li><strong>状態別設定</strong>: 通常、ホバー、押下、無効状態</li>
            <li><strong>疑似クラス</strong>: :hover, :pressed, :checked等</li>
            <li><strong>カスタムプロパティ</strong>: 独自プロパティの追加</li>
        </ul>
        """
    
    def _get_realtime_preview_content(self) -> str:
        """リアルタイムプレビューのヘルプコンテンツ"""
        return """
        <h1>リアルタイムプレビュー</h1>
        
        <h2>プレビュー機能</h2>
        <p>テーマの変更は自動的にプレビューに反映されます。
        実際のアプリケーションでの見た目を確認しながら編集できます。</p>
        
        <h3>更新タイミング</h3>
        <ul>
            <li>プロパティ変更時に自動更新</li>
            <li>更新間隔: 500ms以内</li>
            <li>デバウンス処理により効率的な更新</li>
        </ul>
        
        <h2>プレビュー表示</h2>
        
        <h3>表示ウィジェット</h3>
        <p>以下のウィジェットでテーマを確認できます：</p>
        <ul>
            <li>QPushButton（通常、無効状態）</li>
            <li>QLineEdit（通常、フォーカス状態）</li>
            <li>QComboBox（開閉状態）</li>
            <li>QCheckBox、QRadioButton</li>
            <li>QSlider、QProgressBar</li>
            <li>QListWidget、QTreeWidget</li>
            <li>QTabWidget、QGroupBox</li>
        </ul>
        
        <h3>表示モード</h3>
        <ul>
            <li><strong>標準表示</strong>: 基本的なウィジェット配置</li>
            <li><strong>コンパクト表示</strong>: 省スペースでの表示</li>
            <li><strong>詳細表示</strong>: すべての状態を表示</li>
        </ul>
        
        <h2>プレビューコントロール</h2>
        
        <h3>表示設定</h3>
        <ul>
            <li><strong>ズーム</strong>: 表示倍率の調整</li>
            <li><strong>背景色</strong>: プレビュー背景の変更</li>
            <li><strong>レイアウト</strong>: ウィジェット配置の変更</li>
        </ul>
        
        <h3>状態テスト</h3>
        <ul>
            <li><strong>有効/無効</strong>: ウィジェットの状態切り替え</li>
            <li><strong>選択状態</strong>: チェックボックス、ラジオボタン</li>
            <li><strong>フォーカス</strong>: 入力フィールドのフォーカス状態</li>
        </ul>
        
        <h2>パフォーマンス</h2>
        <p>大きなテーマファイルでも快適に動作するよう、
        効率的な更新アルゴリズムを使用しています。</p>
        """
    
    def _get_wcag_content(self) -> str:
        """WCAG準拠のヘルプコンテンツ"""
        return """
        <h1>WCAG準拠について</h1>
        
        <h2>WCAGとは</h2>
        <p>WCAG（Web Content Accessibility Guidelines）は、
        Webコンテンツのアクセシビリティに関する国際的なガイドラインです。
        Qt-Theme-Studioでは、このガイドラインに準拠したテーマ作成を支援します。</p>
        
        <h2>アクセシビリティレベル</h2>
        
        <h3>レベルAA（推奨）</h3>
        <ul>
            <li>コントラスト比: 4.5:1以上（通常テキスト）</li>
            <li>コントラスト比: 3:1以上（大きなテキスト）</li>
            <li>多くのアプリケーションで推奨される標準</li>
        </ul>
        
        <h3>レベルAAA（最高レベル）</h3>
        <ul>
            <li>コントラスト比: 7:1以上（通常テキスト）</li>
            <li>コントラスト比: 4.5:1以上（大きなテキスト）</li>
            <li>最高レベルのアクセシビリティ</li>
        </ul>
        
        <h2>色の選択指針</h2>
        
        <h3>避けるべき組み合わせ</h3>
        <ul>
            <li>赤と緑の組み合わせ（色覚異常への配慮）</li>
            <li>低コントラストの色の組み合わせ</li>
            <li>色のみに依存した情報伝達</li>
        </ul>
        
        <h3>推奨される組み合わせ</h3>
        <ul>
            <li>高コントラストの色の組み合わせ</li>
            <li>明度差の大きい色の組み合わせ</li>
            <li>形状や位置でも情報を伝達</li>
        </ul>
        
        <h2>テスト方法</h2>
        <p>ゼブラパターンエディターを使用して、
        作成したテーマのアクセシビリティを検証できます。</p>
        
        <h3>検証項目</h3>
        <ul>
            <li>コントラスト比の計算</li>
            <li>WCAG適合レベルの判定</li>
            <li>改善提案の表示</li>
            <li>代替色の自動生成</li>
        </ul>
        """
    
    def _get_contrast_content(self) -> str:
        """コントラスト比計算のヘルプコンテンツ"""
        return """
        <h1>コントラスト比の計算</h1>
        
        <h2>コントラスト比とは</h2>
        <p>コントラスト比は、2つの色の明度差を数値で表したものです。
        値が大きいほど、色の区別がしやすくなります。</p>
        
        <h3>計算式</h3>
        <p>コントラスト比 = (明るい色の相対輝度 + 0.05) / (暗い色の相対輝度 + 0.05)</p>
        
        <h3>値の範囲</h3>
        <ul>
            <li><strong>1:1</strong>: 同じ色（区別不可能）</li>
            <li><strong>21:1</strong>: 最大コントラスト（白と黒）</li>
        </ul>
        
        <h2>自動計算機能</h2>
        <p>Qt-Theme-Studioでは、色を選択すると自動的に
        コントラスト比が計算され、表示されます。</p>
        
        <h3>計算対象</h3>
        <ul>
            <li>テキスト色と背景色</li>
            <li>ボーダー色と背景色</li>
            <li>アクティブ色と非アクティブ色</li>
            <li>選択色と通常色</li>
        </ul>
        
        <h2>判定基準</h2>
        
        <h3>色分け表示</h3>
        <ul>
            <li><strong>緑色</strong>: WCAG AAA準拠（7:1以上）</li>
            <li><strong>黄色</strong>: WCAG AA準拠（4.5:1以上）</li>
            <li><strong>赤色</strong>: 基準未満（改善が必要）</li>
        </ul>
        
        <h3>詳細情報</h3>
        <p>各色の組み合わせについて、以下の情報が表示されます：</p>
        <ul>
            <li>正確なコントラスト比（例: 4.52:1）</li>
            <li>WCAG適合レベル（AA、AAA、または未準拠）</li>
            <li>推奨される用途（通常テキスト、大きなテキスト）</li>
        </ul>
        
        <h2>実用的なヒント</h2>
        <ul>
            <li>4.5:1以上を目標にする</li>
            <li>重要な情報は7:1以上を推奨</li>
            <li>装飾的な要素は3:1でも可</li>
            <li>大きなテキスト（18pt以上）は基準が緩和される</li>
        </ul>
        """

    def _get_color_improvement_content(self) -> str:
        """色改善提案のヘルプコンテンツ"""
        return """
        <h1>色の改善提案</h1>
        
        <h2>自動改善機能</h2>
        <p>コントラスト比が不十分な場合、システムが自動的に
        改善案を提案します。</p>
        
        <h3>改善方法</h3>
        <ul>
            <li><strong>明度調整</strong>: 色の明るさを調整</li>
            <li><strong>彩度調整</strong>: 色の鮮やかさを調整</li>
            <li><strong>色相変更</strong>: 近い色相への変更</li>
            <li><strong>代替色提案</strong>: 全く異なる色の提案</li>
        </ul>
        
        <h2>提案の種類</h2>
        
        <h3>最小限の変更</h3>
        <ul>
            <li>元の色に最も近い改善案</li>
            <li>デザインの意図を保持</li>
            <li>WCAG AA基準をクリア</li>
        </ul>
        
        <h3>最適化された変更</h3>
        <ul>
            <li>より高いコントラスト比を実現</li>
            <li>WCAG AAA基準をクリア</li>
            <li>視認性を最大化</li>
        </ul>
        
        <h3>代替色パレット</h3>
        <ul>
            <li>調和する色の組み合わせ</li>
            <li>ブランドカラーとの整合性</li>
            <li>複数の選択肢を提供</li>
        </ul>
        
        <h2>適用方法</h2>
        
        <h3>ワンクリック適用</h3>
        <p>提案された色をクリックするだけで、
        テーマに自動適用されます。</p>
        
        <h3>プレビュー確認</h3>
        <p>適用前に、プレビューで結果を確認できます。
        気に入らない場合は、Undoで元に戻せます。</p>
        
        <h3>カスタム調整</h3>
        <p>提案をベースに、さらに細かい調整も可能です。</p>
        
        <h2>学習機能</h2>
        <p>ユーザーの選択傾向を学習し、
        より適切な提案を行うようになります。</p>
        
        <h3>フィードバック</h3>
        <ul>
            <li>採用された提案を記録</li>
            <li>拒否された提案も学習</li>
            <li>個人の好みを反映</li>
        </ul>
        """
    
    def _get_accessibility_level_content(self) -> str:
        """アクセシビリティレベルのヘルプコンテンツ"""
        return """
        <h1>アクセシビリティレベル</h1>
        
        <h2>レベル選択</h2>
        <p>プロジェクトの要件に応じて、適切なアクセシビリティレベルを選択できます。</p>
        
        <h3>レベルA（基本）</h3>
        <ul>
            <li>最低限のアクセシビリティ要件</li>
            <li>コントラスト比: 3:1以上</li>
            <li>基本的な色覚対応</li>
        </ul>
        
        <h3>レベルAA（標準）</h3>
        <ul>
            <li>一般的なアプリケーションの標準</li>
            <li>コントラスト比: 4.5:1以上（通常テキスト）</li>
            <li>コントラスト比: 3:1以上（大きなテキスト）</li>
            <li>多くの法的要件を満たす</li>
        </ul>
        
        <h3>レベルAAA（最高）</h3>
        <ul>
            <li>最高レベルのアクセシビリティ</li>
            <li>コントラスト比: 7:1以上（通常テキスト）</li>
            <li>コントラスト比: 4.5:1以上（大きなテキスト）</li>
            <li>特別な配慮が必要な環境向け</li>
        </ul>
        
        <h2>プリセット機能</h2>
        <p>選択したレベルに応じて、適切な色の組み合わせが
        自動生成されます。</p>
        
        <h3>プリセットの内容</h3>
        <ul>
            <li><strong>基本色パレット</strong>: メイン、アクセント、背景色</li>
            <li><strong>状態色</strong>: 成功、警告、エラー、情報</li>
            <li><strong>UI色</strong>: ボタン、入力フィールド、リンク</li>
            <li><strong>テキスト色</strong>: 見出し、本文、キャプション</li>
        </ul>
        
        <h3>カスタマイズ</h3>
        <p>プリセットをベースに、さらなるカスタマイズが可能です：</p>
        <ul>
            <li>ブランドカラーの適用</li>
            <li>特定の色相への調整</li>
            <li>明度・彩度の微調整</li>
        </ul>
        
        <h2>検証機能</h2>
        <p>設定したレベルに対して、継続的な検証が行われます。</p>
        
        <h3>リアルタイム検証</h3>
        <ul>
            <li>色変更時の即座な検証</li>
            <li>基準未満の組み合わせを警告</li>
            <li>改善提案の自動表示</li>
        </ul>
        
        <h3>総合レポート</h3>
        <ul>
            <li>テーマ全体のアクセシビリティスコア</li>
            <li>問題箇所の詳細リスト</li>
            <li>改善優先度の表示</li>
        </ul>
        """
    
    def _get_live_preview_content(self) -> str:
        """ライブプレビューのヘルプコンテンツ"""
        return """
        <h1>ライブプレビューの使用</h1>
        
        <h2>プレビューウィンドウ</h2>
        <p>ライブプレビューウィンドウでは、作成中のテーマが
        実際のQtアプリケーションでどのように表示されるかを確認できます。</p>
        
        <h3>表示・非表示</h3>
        <ul>
            <li>「表示」→「プレビュー」で切り替え</li>
            <li>ツールバーのプレビューボタン</li>
            <li>キーボードショートカット: F5</li>
        </ul>
        
        <h2>プレビュー内容</h2>
        
        <h3>基本ウィジェット</h3>
        <p>以下のウィジェットが表示されます：</p>
        <ul>
            <li><strong>ボタン類</strong>: QPushButton、QToolButton</li>
            <li><strong>入力類</strong>: QLineEdit、QTextEdit、QSpinBox</li>
            <li><strong>選択類</strong>: QCheckBox、QRadioButton、QComboBox</li>
            <li><strong>表示類</strong>: QLabel、QProgressBar、QSlider</li>
            <li><strong>コンテナ</strong>: QGroupBox、QTabWidget、QFrame</li>
        </ul>
        
        <h3>リスト・ツリー</h3>
        <ul>
            <li>QListWidget: 項目の選択状態</li>
            <li>QTreeWidget: 階層構造の表示</li>
            <li>QTableWidget: テーブル形式のデータ</li>
        </ul>
        
        <h2>インタラクティブ機能</h2>
        
        <h3>状態変更</h3>
        <p>プレビュー内のウィジェットは実際に操作できます：</p>
        <ul>
            <li>ボタンのクリック</li>
            <li>チェックボックスの切り替え</li>
            <li>テキスト入力</li>
            <li>スライダーの調整</li>
        </ul>
        
        <h3>フォーカス状態</h3>
        <p>Tabキーでフォーカスを移動し、
        フォーカス時のスタイルを確認できます。</p>
        
        <h2>プレビュー設定</h2>
        
        <h3>表示オプション</h3>
        <ul>
            <li><strong>ズームレベル</strong>: 50%〜200%</li>
            <li><strong>背景色</strong>: プレビューの背景色変更</li>
            <li><strong>レイアウト</strong>: ウィジェットの配置変更</li>
        </ul>
        
        <h3>更新設定</h3>
        <ul>
            <li><strong>自動更新</strong>: 変更時の自動反映</li>
            <li><strong>更新間隔</strong>: 反映タイミングの調整</li>
            <li><strong>デバウンス</strong>: 連続変更時の最適化</li>
        </ul>
        """

    def _get_widget_display_content(self) -> str:
        """ウィジェット表示のヘルプコンテンツ"""
        return """
        <h1>ウィジェット表示</h1>
        
        <h2>表示ウィジェット一覧</h2>
        <p>プレビューでは、Qtアプリケーションで使用される
        主要なウィジェットを表示します。</p>
        
        <h3>基本コントロール</h3>
        <ul>
            <li><strong>QPushButton</strong>: 通常、ホバー、押下状態</li>
            <li><strong>QToolButton</strong>: アイコン付きボタン</li>
            <li><strong>QCheckBox</strong>: チェック済み/未チェック</li>
            <li><strong>QRadioButton</strong>: 選択済み/未選択</li>
        </ul>
        
        <h3>入力コントロール</h3>
        <ul>
            <li><strong>QLineEdit</strong>: 単行テキスト入力</li>
            <li><strong>QTextEdit</strong>: 複数行テキスト入力</li>
            <li><strong>QSpinBox</strong>: 数値入力</li>
            <li><strong>QComboBox</strong>: ドロップダウン選択</li>
        </ul>
        
        <h3>表示コントロール</h3>
        <ul>
            <li><strong>QLabel</strong>: 静的テキスト表示</li>
            <li><strong>QProgressBar</strong>: 進捗表示</li>
            <li><strong>QSlider</strong>: 値の調整</li>
            <li><strong>QLCDNumber</strong>: デジタル表示</li>
        </ul>
        
        <h3>コンテナ</h3>
        <ul>
            <li><strong>QGroupBox</strong>: グループ化</li>
            <li><strong>QTabWidget</strong>: タブ表示</li>
            <li><strong>QFrame</strong>: 枠線表示</li>
            <li><strong>QScrollArea</strong>: スクロール領域</li>
        </ul>
        
        <h3>リスト・テーブル</h3>
        <ul>
            <li><strong>QListWidget</strong>: リスト表示</li>
            <li><strong>QTreeWidget</strong>: ツリー表示</li>
            <li><strong>QTableWidget</strong>: テーブル表示</li>
        </ul>
        
        <h2>状態表示</h2>
        
        <h3>基本状態</h3>
        <ul>
            <li><strong>通常状態</strong>: デフォルトの表示</li>
            <li><strong>ホバー状態</strong>: マウスオーバー時</li>
            <li><strong>押下状態</strong>: クリック時</li>
            <li><strong>無効状態</strong>: 操作不可時</li>
        </ul>
        
        <h3>選択状態</h3>
        <ul>
            <li><strong>選択済み</strong>: チェックボックス、ラジオボタン</li>
            <li><strong>フォーカス</strong>: キーボードフォーカス時</li>
            <li><strong>アクティブ</strong>: アクティブウィンドウ時</li>
        </ul>
        
        <h2>カスタマイズ</h2>
        
        <h3>表示ウィジェットの追加</h3>
        <p>プレビューに表示するウィジェットを追加できます：</p>
        <ul>
            <li>「プレビュー設定」から追加</li>
            <li>カスタムウィジェットの登録</li>
            <li>サードパーティウィジェットの対応</li>
        </ul>
        
        <h3>レイアウト調整</h3>
        <ul>
            <li><strong>グリッドレイアウト</strong>: 整列表示</li>
            <li><strong>フローレイアウト</strong>: 自動折り返し</li>
            <li><strong>カスタムレイアウト</strong>: 自由配置</li>
        </ul>
        
        <h2>実用的な使い方</h2>
        <ul>
            <li>各ウィジェットの見た目を個別に確認</li>
            <li>状態変化時の表示をテスト</li>
            <li>全体的な統一感をチェック</li>
            <li>異なるサイズでの表示を確認</li>
        </ul>
        """
    
    def _get_preview_export_content(self) -> str:
        """プレビュー画像エクスポートのヘルプコンテンツ"""
        return """
        <h1>プレビュー画像のエクスポート</h1>
        
        <h2>エクスポート機能</h2>
        <p>作成したテーマのプレビュー画像を画像ファイルとして
        保存できます。</p>
        
        <h3>エクスポート方法</h3>
        <ul>
            <li>プレビューウィンドウの「エクスポート」ボタン</li>
            <li>「ファイル」→「プレビューをエクスポート」</li>
            <li>右クリックメニューから「画像として保存」</li>
        </ul>
        
        <h2>対応形式</h2>
        
        <h3>画像形式</h3>
        <ul>
            <li><strong>PNG</strong>: 高品質、透明度対応（推奨）</li>
            <li><strong>JPEG</strong>: 小サイズ、写真向け</li>
            <li><strong>BMP</strong>: 無圧縮、高品質</li>
            <li><strong>SVG</strong>: ベクター形式、拡大縮小対応</li>
        </ul>
        
        <h3>解像度設定</h3>
        <ul>
            <li><strong>画面解像度</strong>: 実際の表示サイズ</li>
            <li><strong>高解像度</strong>: 2倍、3倍サイズ</li>
            <li><strong>カスタム解像度</strong>: 任意のサイズ指定</li>
        </ul>
        
        <h2>エクスポート設定</h2>
        
        <h3>範囲選択</h3>
        <ul>
            <li><strong>全体</strong>: プレビューウィンドウ全体</li>
            <li><strong>ウィジェット領域のみ</strong>: コントロール部分のみ</li>
            <li><strong>選択範囲</strong>: 指定した範囲のみ</li>
        </ul>
        
        <h3>背景設定</h3>
        <ul>
            <li><strong>透明背景</strong>: PNG形式で透明度保持</li>
            <li><strong>白背景</strong>: 標準的な白背景</li>
            <li><strong>カスタム背景</strong>: 任意の背景色</li>
        </ul>
        
        <h3>品質設定</h3>
        <ul>
            <li><strong>圧縮レベル</strong>: ファイルサイズと品質のバランス</li>
            <li><strong>アンチエイリアス</strong>: 滑らかな表示</li>
            <li><strong>DPI設定</strong>: 印刷品質の調整</li>
        </ul>
        
        <h2>用途別設定</h2>
        
        <h3>ドキュメント用</h3>
        <ul>
            <li>PNG形式、高解像度</li>
            <li>白背景または透明背景</li>
            <li>300dpi以上の設定</li>
        </ul>
        
        <h3>Web用</h3>
        <ul>
            <li>PNG形式、標準解像度</li>
            <li>ファイルサイズ最適化</li>
            <li>72dpiの設定</li>
        </ul>
        
        <h3>プレゼンテーション用</h3>
        <ul>
            <li>PNG形式、高解像度</li>
            <li>透明背景</li>
            <li>大きなサイズ設定</li>
        </ul>
        
        <h2>バッチエクスポート</h2>
        <p>複数の状態や設定でのプレビューを
        一括でエクスポートできます。</p>
        
        <h3>エクスポート対象</h3>
        <ul>
            <li>すべてのウィジェット状態</li>
            <li>異なる解像度での表示</li>
            <li>複数の背景色での表示</li>
        </ul>
        """
    
    def _get_responsive_test_content(self) -> str:
        """レスポンシブテストのヘルプコンテンツ"""
        return """
        <h1>レスポンシブテスト</h1>
        
        <h2>レスポンシブテスト機能</h2>
        <p>異なるウィンドウサイズや解像度でのテーマ表示を
        テストできます。</p>
        
        <h3>テスト項目</h3>
        <ul>
            <li><strong>ウィンドウサイズ</strong>: 小、中、大サイズでの表示</li>
            <li><strong>解像度</strong>: 標準、高解像度での表示</li>
            <li><strong>DPIスケーリング</strong>: 100%、125%、150%、200%</li>
            <li><strong>フォントサイズ</strong>: システムフォントサイズの変更</li>
        </ul>
        
        <h2>プリセットサイズ</h2>
        
        <h3>デスクトップサイズ</h3>
        <ul>
            <li><strong>小型</strong>: 1024x768（古いモニター）</li>
            <li><strong>標準</strong>: 1920x1080（フルHD）</li>
            <li><strong>大型</strong>: 2560x1440（WQHD）</li>
            <li><strong>4K</strong>: 3840x2160（Ultra HD）</li>
        </ul>
        
        <h3>モバイルサイズ</h3>
        <ul>
            <li><strong>タブレット</strong>: 768x1024</li>
            <li><strong>スマートフォン</strong>: 375x667</li>
            <li><strong>小型デバイス</strong>: 320x568</li>
        </ul>
        
        <h2>テスト方法</h2>
        
        <h3>手動テスト</h3>
        <ul>
            <li>プレビューウィンドウのサイズを手動で変更</li>
            <li>リアルタイムでの表示確認</li>
            <li>問題箇所の特定</li>
        </ul>
        
        <h3>自動テスト</h3>
        <ul>
            <li>プリセットサイズでの自動テスト</li>
            <li>問題の自動検出</li>
            <li>レポート生成</li>
        </ul>
        
        <h2>検証項目</h2>
        
        <h3>レイアウト</h3>
        <ul>
            <li><strong>要素の配置</strong>: 重なりや隠れの確認</li>
            <li><strong>スクロールバー</strong>: 必要時の表示</li>
            <li><strong>余白</strong>: 適切なマージン・パディング</li>
        </ul>
        
        <h3>テキスト</h3>
        <ul>
            <li><strong>可読性</strong>: 小さなサイズでの読みやすさ</li>
            <li><strong>折り返し</strong>: 長いテキストの処理</li>
            <li><strong>切り詰め</strong>: 省略記号の表示</li>
        </ul>
        
        <h3>ウィジェット</h3>
        <ul>
            <li><strong>最小サイズ</strong>: 操作可能な最小サイズ</li>
            <li><strong>アスペクト比</strong>: 縦横比の維持</li>
            <li><strong>アイコン</strong>: 解像度に応じた表示</li>
        </ul>
        
        <h2>問題の対処</h2>
        
        <h3>一般的な問題</h3>
        <ul>
            <li><strong>要素の重なり</strong>: マージンの調整</li>
            <li><strong>テキストの切れ</strong>: フォントサイズの調整</li>
            <li><strong>ボタンの小ささ</strong>: 最小サイズの設定</li>
        </ul>
        
        <h3>解決策</h3>
        <ul>
            <li>相対的なサイズ指定の使用</li>
            <li>最小・最大サイズの設定</li>
            <li>フレキシブルレイアウトの採用</li>
        </ul>
        """

    def _get_theme_gallery_content(self) -> str:
        """テーマギャラリーのヘルプコンテンツ"""
        return """
        <h1>テーマギャラリー</h1>
        
        <h2>ギャラリー機能</h2>
        <p>保存されたテーマを一覧表示し、効率的に管理できます。</p>
        
        <h3>表示方法</h3>
        <ul>
            <li>「ツール」→「テーマギャラリー」</li>
            <li>ツールバーのギャラリーボタン</li>
            <li>キーボードショートカット: Ctrl+G</li>
        </ul>
        
        <h2>表示形式</h2>
        
        <h3>サムネイル表示</h3>
        <ul>
            <li><strong>大きなサムネイル</strong>: 詳細な確認</li>
            <li><strong>中サムネイル</strong>: バランスの良い表示</li>
            <li><strong>小さなサムネイル</strong>: 多くのテーマを一覧</li>
        </ul>
        
        <h3>リスト表示</h3>
        <ul>
            <li>テーマ名、作成日、サイズを表示</li>
            <li>ソート機能（名前、日付、サイズ順）</li>
            <li>詳細情報の表示</li>
        </ul>
        
        <h2>検索・フィルタリング</h2>
        
        <h3>検索機能</h3>
        <ul>
            <li><strong>名前検索</strong>: テーマ名での検索</li>
            <li><strong>タグ検索</strong>: 設定されたタグでの検索</li>
            <li><strong>説明検索</strong>: 説明文での検索</li>
        </ul>
        
        <h3>フィルター</h3>
        <ul>
            <li><strong>作成日</strong>: 期間での絞り込み</li>
            <li><strong>カテゴリ</strong>: ライト、ダーク、ハイコントラスト</li>
            <li><strong>アクセシビリティレベル</strong>: AA、AAA準拠</li>
            <li><strong>使用頻度</strong>: よく使用するテーマ</li>
        </ul>
        
        <h2>テーマ操作</h2>
        
        <h3>基本操作</h3>
        <ul>
            <li><strong>開く</strong>: ダブルクリックまたは「開く」ボタン</li>
            <li><strong>プレビュー</strong>: 選択時の自動プレビュー</li>
            <li><strong>削除</strong>: 不要なテーマの削除</li>
            <li><strong>複製</strong>: テーマのコピー作成</li>
        </ul>
        
        <h3>詳細操作</h3>
        <ul>
            <li><strong>名前変更</strong>: テーマ名の変更</li>
            <li><strong>説明編集</strong>: テーマの説明追加・編集</li>
            <li><strong>タグ設定</strong>: 分類用タグの設定</li>
            <li><strong>お気に入り</strong>: よく使用するテーマをマーク</li>
        </ul>
        
        <h2>整理機能</h2>
        
        <h3>フォルダ管理</h3>
        <ul>
            <li>カテゴリ別フォルダの作成</li>
            <li>プロジェクト別の整理</li>
            <li>階層構造での管理</li>
        </ul>
        
        <h3>バックアップ</h3>
        <ul>
            <li>テーマの自動バックアップ</li>
            <li>バージョン履歴の管理</li>
            <li>復元機能</li>
        </ul>
        
        <h2>共有機能</h2>
        
        <h3>エクスポート</h3>
        <ul>
            <li>選択したテーマのエクスポート</li>
            <li>複数テーマの一括エクスポート</li>
            <li>テーマパッケージの作成</li>
        </ul>
        
        <h3>インポート</h3>
        <ul>
            <li>他の環境からのテーマインポート</li>
            <li>テーマパッケージの展開</li>
            <li>重複チェック機能</li>
        </ul>
        """
    
    def _get_import_export_content(self) -> str:
        """インポート・エクスポートのヘルプコンテンツ"""
        return """
        <h1>インポート・エクスポート</h1>
        
        <h2>対応形式</h2>
        <p>Qt-Theme-Studioは複数のテーマ形式に対応しています。</p>
        
        <h3>インポート対応形式</h3>
        <ul>
            <li><strong>JSON</strong>: Qt-Theme-Studio標準形式</li>
            <li><strong>QSS</strong>: Qt Style Sheet形式</li>
            <li><strong>CSS</strong>: Cascading Style Sheets</li>
            <li><strong>INI</strong>: 設定ファイル形式</li>
            <li><strong>XML</strong>: 構造化データ形式</li>
        </ul>
        
        <h3>エクスポート対応形式</h3>
        <ul>
            <li><strong>JSON</strong>: 完全な情報保持</li>
            <li><strong>QSS</strong>: Qt アプリケーション用</li>
            <li><strong>CSS</strong>: Web アプリケーション用</li>
            <li><strong>Python</strong>: プログラムコード形式</li>
            <li><strong>C++</strong>: Qt C++ アプリケーション用</li>
        </ul>
        
        <h2>インポート機能</h2>
        
        <h3>ファイルからインポート</h3>
        <ul>
            <li>「ファイル」→「インポート」を選択</li>
            <li>対応形式のファイルを選択</li>
            <li>自動的に内部形式に変換</li>
        </ul>
        
        <h3>フォルダからインポート</h3>
        <ul>
            <li>複数のテーマファイルを一括インポート</li>
            <li>サブフォルダの再帰的検索</li>
            <li>重複ファイルのスキップ</li>
        </ul>
        
        <h3>インポート設定</h3>
        <ul>
            <li><strong>重複処理</strong>: 上書き、スキップ、名前変更</li>
            <li><strong>検証</strong>: インポート前の形式チェック</li>
            <li><strong>変換オプション</strong>: 色空間、単位の変換</li>
        </ul>
        
        <h2>エクスポート機能</h2>
        
        <h3>単一テーマエクスポート</h3>
        <ul>
            <li>「ファイル」→「エクスポート」を選択</li>
            <li>出力形式を選択</li>
            <li>保存場所を指定</li>
        </ul>
        
        <h3>バッチエクスポート</h3>
        <ul>
            <li>複数テーマの一括エクスポート</li>
            <li>異なる形式での同時出力</li>
            <li>フォルダ構造の保持</li>
        </ul>
        
        <h3>エクスポート設定</h3>
        <ul>
            <li><strong>圧縮</strong>: ファイルサイズの最適化</li>
            <li><strong>コメント</strong>: 説明文の埋め込み</li>
            <li><strong>互換性</strong>: 古いバージョンとの互換性</li>
        </ul>
        
        <h2>ラウンドトリップ変換</h2>
        <p>インポート→編集→エクスポートの過程で、
        データの損失を最小限に抑えます。</p>
        
        <h3>保持される情報</h3>
        <ul>
            <li>色の正確な値</li>
            <li>フォント設定</li>
            <li>カスタムプロパティ</li>
            <li>メタデータ</li>
        </ul>
        
        <h3>変換時の注意</h3>
        <ul>
            <li>形式固有の機能は失われる可能性</li>
            <li>色空間の変換による微細な差異</li>
            <li>コメントや構造の変更</li>
        </ul>
        
        <h2>互換性</h2>
        
        <h3>Qt フレームワーク</h3>
        <ul>
            <li>PySide6/PyQt6/PyQt5での動作確認</li>
            <li>バージョン固有の機能への対応</li>
            <li>互換性レポートの生成</li>
        </ul>
        
        <h3>他のツール</h3>
        <ul>
            <li>Qt Designer との連携</li>
            <li>Qt Creator での使用</li>
            <li>サードパーティツールとの互換性</li>
        </ul>
        """

    def _get_template_content(self) -> str:
        """テーマテンプレートのヘルプコンテンツ"""
        return """
        <h1>テーマテンプレート</h1>
        
        <h2>テンプレート機能</h2>
        <p>事前定義されたテンプレートを使用して、
        効率的にテーマ作成を開始できます。</p>
        
        <h3>利用方法</h3>
        <ul>
            <li>新規テーマ作成時にテンプレート選択</li>
            <li>「ファイル」→「テンプレートから作成」</li>
            <li>テーマギャラリーからテンプレート選択</li>
        </ul>
        
        <h2>標準テンプレート</h2>
        
        <h3>基本テンプレート</h3>
        <ul>
            <li><strong>ライトテーマ</strong>: 明るい色調の標準テーマ</li>
            <li><strong>ダークテーマ</strong>: 暗い色調のモダンテーマ</li>
            <li><strong>クラシック</strong>: 従来のデスクトップスタイル</li>
            <li><strong>ミニマル</strong>: シンプルで洗練されたデザイン</li>
        </ul>
        
        <h3>アクセシビリティテンプレート</h3>
        <ul>
            <li><strong>ハイコントラスト</strong>: WCAG AAA準拠</li>
            <li><strong>大きなフォント</strong>: 視認性重視</li>
            <li><strong>色覚サポート</strong>: 色覚異常に配慮</li>
            <li><strong>シニア向け</strong>: 高齢者に優しいデザイン</li>
        </ul>
        
        <h3>用途別テンプレート</h3>
        <ul>
            <li><strong>ビジネス</strong>: 企業アプリケーション向け</li>
            <li><strong>クリエイティブ</strong>: デザインツール向け</li>
            <li><strong>ゲーミング</strong>: ゲームアプリケーション向け</li>
            <li><strong>教育</strong>: 学習アプリケーション向け</li>
        </ul>
        
        <h2>カスタムテンプレート</h2>
        
        <h3>テンプレートの作成</h3>
        <ul>
            <li>既存テーマからテンプレート作成</li>
            <li>「ファイル」→「テンプレートとして保存」</li>
            <li>テンプレート情報の設定</li>
        </ul>
        
        <h3>テンプレート情報</h3>
        <ul>
            <li><strong>名前</strong>: テンプレートの識別名</li>
            <li><strong>説明</strong>: 用途や特徴の説明</li>
            <li><strong>カテゴリ</strong>: 分類用カテゴリ</li>
            <li><strong>タグ</strong>: 検索用キーワード</li>
            <li><strong>プレビュー画像</strong>: サムネイル画像</li>
        </ul>
        
        <h2>テンプレート管理</h2>
        
        <h3>整理機能</h3>
        <ul>
            <li>カテゴリ別の分類</li>
            <li>お気に入りテンプレート</li>
            <li>使用頻度による並び替え</li>
            <li>カスタムフォルダでの整理</li>
        </ul>
        
        <h3>共有機能</h3>
        <ul>
            <li>テンプレートのエクスポート</li>
            <li>他のユーザーとの共有</li>
            <li>オンラインテンプレートライブラリ</li>
            <li>コミュニティテンプレート</li>
        </ul>
        
        <h2>テンプレートの活用</h2>
        
        <h3>効率的な使い方</h3>
        <ul>
            <li>プロジェクトに適したテンプレート選択</li>
            <li>ベースとしての活用</li>
            <li>一貫性のあるデザイン作成</li>
            <li>時間短縮とクオリティ向上</li>
        </ul>
        
        <h3>カスタマイズ</h3>
        <ul>
            <li>テンプレートをベースに調整</li>
            <li>ブランドカラーの適用</li>
            <li>特定要件への対応</li>
            <li>独自スタイルの追加</li>
        </ul>
        """
    
    def _get_recent_themes_content(self) -> str:
        """最近使用したテーマのヘルプコンテンツ"""
        return """
        <h1>最近使用したテーマ</h1>
        
        <h2>最近使用したテーマ機能</h2>
        <p>最近編集したテーマに素早くアクセスできます。</p>
        
        <h3>アクセス方法</h3>
        <ul>
            <li>「ファイル」→「最近使用したテーマ」</li>
            <li>スタートページの最近使用したテーマ一覧</li>
            <li>ツールバーの履歴ボタン</li>
        </ul>
        
        <h2>表示内容</h2>
        
        <h3>テーマ情報</h3>
        <ul>
            <li><strong>テーマ名</strong>: ファイル名または設定名</li>
            <li><strong>最終更新日時</strong>: 最後に編集した日時</li>
            <li><strong>ファイルパス</strong>: 保存場所</li>
            <li><strong>プレビュー</strong>: 小さなサムネイル画像</li>
        </ul>
        
        <h3>状態表示</h3>
        <ul>
            <li><strong>利用可能</strong>: ファイルが存在し、開ける状態</li>
            <li><strong>移動済み</strong>: ファイルが移動された状態</li>
            <li><strong>削除済み</strong>: ファイルが削除された状態</li>
            <li><strong>アクセス不可</strong>: 権限不足等でアクセスできない状態</li>
        </ul>
        
        <h2>管理機能</h2>
        
        <h3>履歴の管理</h3>
        <ul>
            <li><strong>履歴数</strong>: 最大10個まで記録（設定で変更可能）</li>
            <li><strong>自動更新</strong>: テーマを開くたびに自動更新</li>
            <li><strong>重複除去</strong>: 同じテーマは最新の日時で更新</li>
        </ul>
        
        <h3>履歴の操作</h3>
        <ul>
            <li><strong>開く</strong>: クリックでテーマを開く</li>
            <li><strong>削除</strong>: 履歴から特定項目を削除</li>
            <li><strong>クリア</strong>: 履歴をすべて削除</li>
            <li><strong>固定</strong>: 特定のテーマを履歴に固定</li>
        </ul>
        
        <h2>便利な機能</h2>
        
        <h3>クイックアクセス</h3>
        <ul>
            <li>キーボードショートカット（Ctrl+1〜9）</li>
            <li>番号キーでの直接アクセス</li>
            <li>マウスホバーでのプレビュー表示</li>
        </ul>
        
        <h3>コンテキストメニュー</h3>
        <ul>
            <li><strong>開く</strong>: テーマを開く</li>
            <li><strong>場所を開く</strong>: ファイルの保存場所を開く</li>
            <li><strong>コピー</strong>: ファイルパスをクリップボードにコピー</li>
            <li><strong>履歴から削除</strong>: この項目を履歴から削除</li>
        </ul>
        
        <h2>設定オプション</h2>
        
        <h3>履歴設定</h3>
        <ul>
            <li><strong>履歴数</strong>: 保存する履歴の最大数</li>
            <li><strong>自動クリア</strong>: 一定期間後の自動削除</li>
            <li><strong>プレビュー表示</strong>: サムネイルの表示/非表示</li>
        </ul>
        
        <h3>表示設定</h3>
        <ul>
            <li><strong>並び順</strong>: 日時順、名前順、使用頻度順</li>
            <li><strong>表示形式</strong>: リスト、アイコン、詳細</li>
            <li><strong>グループ化</strong>: 日付やプロジェクトでのグループ化</li>
        </ul>
        
        <h2>トラブルシューティング</h2>
        
        <h3>ファイルが見つからない場合</h3>
        <ul>
            <li>ファイルの場所を確認</li>
            <li>履歴から削除して再度開く</li>
            <li>バックアップからの復元</li>
        </ul>
        
        <h3>履歴が表示されない場合</h3>
        <ul>
            <li>設定の確認</li>
            <li>履歴ファイルの修復</li>
            <li>アプリケーションの再起動</li>
        </ul>
        """
    
    def _get_undo_redo_content(self) -> str:
        """Undo/Redo操作のヘルプコンテンツ"""
        return """
        <h1>Undo/Redo操作</h1>
        
        <h2>操作履歴機能</h2>
        <p>テーマ編集中の操作を記録し、いつでも前の状態に戻したり、
        やり直したりできます。</p>
        
        <h3>基本操作</h3>
        <ul>
            <li><strong>Undo（元に戻す）</strong>: Ctrl+Z</li>
            <li><strong>Redo（やり直し）</strong>: Ctrl+Y または Ctrl+Shift+Z</li>
            <li>「編集」メニューからも実行可能</li>
            <li>ツールバーのUndo/Redoボタン</li>
        </ul>
        
        <h2>記録される操作</h2>
        
        <h3>色の変更</h3>
        <ul>
            <li>カラーピッカーでの色選択</li>
            <li>RGB値の直接入力</li>
            <li>16進値の入力</li>
            <li>色の調和機能での変更</li>
        </ul>
        
        <h3>フォントの変更</h3>
        <ul>
            <li>フォントファミリーの変更</li>
            <li>フォントサイズの調整</li>
            <li>フォントスタイルの変更</li>
        </ul>
        
        <h3>プロパティの変更</h3>
        <ul>
            <li>サイズ値の変更</li>
            <li>マージン・パディングの調整</li>
            <li>ボーダー設定の変更</li>
            <li>効果の追加・削除</li>
        </ul>
        
        <h2>履歴の管理</h2>
        
        <h3>履歴の制限</h3>
        <ul>
            <li><strong>最大履歴数</strong>: 50回（設定で変更可能）</li>
            <li><strong>メモリ使用量</strong>: 自動的に最適化</li>
            <li><strong>セッション単位</strong>: アプリケーション終了時にクリア</li>
        </ul>
        
        <h3>履歴の表示</h3>
        <ul>
            <li>「編集」→「履歴」で履歴一覧を表示</li>
            <li>各操作の詳細情報</li>
            <li>特定の時点への直接ジャンプ</li>
        </ul>
        
        <h2>高度な機能</h2>
        
        <h3>操作のグループ化</h3>
        <ul>
            <li>関連する複数の変更を一つの操作として記録</li>
            <li>一括変更時の効率的なUndo/Redo</li>
            <li>複雑な操作の簡単な取り消し</li>
        </ul>
        
        <h3>選択的Undo</h3>
        <ul>
            <li>特定の種類の変更のみを取り消し</li>
            <li>色変更のみ、フォント変更のみなど</li>
            <li>部分的な変更の取り消し</li>
        </ul>
        
        <h2>プレビューとの連携</h2>
        
        <h3>リアルタイム更新</h3>
        <ul>
            <li>Undo/Redo操作時のプレビュー自動更新</li>
            <li>変更内容の即座な反映</li>
            <li>一貫した表示状態の維持</li>
        </ul>
        
        <h3>履歴プレビュー</h3>
        <ul>
            <li>履歴一覧での各状態のプレビュー</li>
            <li>変更前後の比較表示</li>
            <li>視覚的な変更確認</li>
        </ul>
        
        <h2>パフォーマンス</h2>
        
        <h3>効率的な記録</h3>
        <ul>
            <li>差分のみを記録してメモリ使用量を最小化</li>
            <li>大きなテーマでも高速な操作</li>
            <li>バックグラウンドでの履歴管理</li>
        </ul>
        
        <h3>最適化機能</h3>
        <ul>
            <li>不要な履歴の自動削除</li>
            <li>メモリ使用量の監視</li>
            <li>パフォーマンス低下の防止</li>
        </ul>
        
        <h2>設定オプション</h2>
        
        <h3>履歴設定</h3>
        <ul>
            <li><strong>最大履歴数</strong>: 10〜100回の範囲で設定</li>
            <li><strong>自動保存</strong>: 一定間隔での履歴保存</li>
            <li><strong>グループ化</strong>: 操作のグループ化設定</li>
        </ul>
        
        <h3>表示設定</h3>
        <ul>
            <li><strong>履歴一覧</strong>: 詳細表示の設定</li>
            <li><strong>プレビュー</strong>: 履歴プレビューの有効/無効</li>
            <li><strong>ショートカット</strong>: キーボードショートカットの変更</li>
        </ul>
        """

    def _get_settings_content(self) -> str:
        """設定のカスタマイズのヘルプコンテンツ"""
        return """
        <h1>設定のカスタマイズ</h1>
        
        <h2>設定画面</h2>
        <p>アプリケーションの動作をカスタマイズできます。</p>
        
        <h3>アクセス方法</h3>
        <ul>
            <li>「編集」→「設定」</li>
            <li>キーボードショートカット: Ctrl+,</li>
            <li>ツールバーの設定ボタン</li>
        </ul>
        
        <h2>一般設定</h2>
        
        <h3>アプリケーション</h3>
        <ul>
            <li><strong>起動時の動作</strong>: 最後のテーマを開く、新規テーマ、スタートページ</li>
            <li><strong>自動保存</strong>: 自動保存の間隔設定</li>
            <li><strong>バックアップ</strong>: バックアップファイルの作成設定</li>
            <li><strong>最近使用したファイル</strong>: 履歴の保存数</li>
        </ul>
        
        <h3>インターフェース</h3>
        <ul>
            <li><strong>テーマ</strong>: アプリケーション自体のテーマ</li>
            <li><strong>フォントサイズ</strong>: UI フォントのサイズ</li>
            <li><strong>ツールバー</strong>: ツールバーの表示設定</li>
            <li><strong>ステータスバー</strong>: ステータスバーの表示項目</li>
        </ul>
        
        <h2>エディター設定</h2>
        
        <h3>テーマエディター</h3>
        <ul>
            <li><strong>デフォルト色空間</strong>: RGB、HSV、HSL</li>
            <li><strong>カラーピッカー</strong>: 表示形式の設定</li>
            <li><strong>プロパティ表示</strong>: 表示する項目の選択</li>
            <li><strong>自動補完</strong>: 値入力時の自動補完</li>
        </ul>
        
        <h3>ゼブラエディター</h3>
        <ul>
            <li><strong>デフォルトレベル</strong>: WCAG準拠レベル（AA、AAA）</li>
            <li><strong>コントラスト表示</strong>: 数値表示の精度</li>
            <li><strong>改善提案</strong>: 自動提案の有効/無効</li>
            <li><strong>色覚シミュレーション</strong>: 色覚異常のシミュレーション</li>
        </ul>
        
        <h2>プレビュー設定</h2>
        
        <h3>表示設定</h3>
        <ul>
            <li><strong>更新間隔</strong>: リアルタイム更新の間隔</li>
            <li><strong>デバウンス時間</strong>: 連続変更時の待機時間</li>
            <li><strong>表示ウィジェット</strong>: プレビューに表示するウィジェット</li>
            <li><strong>背景色</strong>: プレビューの背景色</li>
        </ul>
        
        <h3>パフォーマンス</h3>
        <ul>
            <li><strong>ハードウェア加速</strong>: GPU加速の使用</li>
            <li><strong>メモリ使用量</strong>: プレビューのメモリ制限</li>
            <li><strong>品質設定</strong>: 表示品質とパフォーマンスのバランス</li>
        </ul>
        
        <h2>ファイル設定</h2>
        
        <h3>保存設定</h3>
        <ul>
            <li><strong>デフォルト形式</strong>: 保存時のデフォルトファイル形式</li>
            <li><strong>圧縮レベル</strong>: ファイル圧縮の設定</li>
            <li><strong>メタデータ</strong>: 作成者情報等の埋め込み</li>
            <li><strong>バックアップ</strong>: 保存時のバックアップ作成</li>
        </ul>
        
        <h3>エクスポート設定</h3>
        <ul>
            <li><strong>コード生成</strong>: エクスポート時のコード形式</li>
            <li><strong>コメント</strong>: 生成コードへのコメント追加</li>
            <li><strong>インデント</strong>: コードのインデント設定</li>
            <li><strong>互換性</strong>: 古いバージョンとの互換性</li>
        </ul>
        
        <h2>高度な設定</h2>
        
        <h3>パフォーマンス</h3>
        <ul>
            <li><strong>マルチスレッド</strong>: 並列処理の使用</li>
            <li><strong>キャッシュサイズ</strong>: メモリキャッシュの設定</li>
            <li><strong>ガベージコレクション</strong>: メモリ管理の最適化</li>
        </ul>
        
        <h3>デバッグ</h3>
        <ul>
            <li><strong>ログレベル</strong>: 出力するログの詳細度</li>
            <li><strong>ログファイル</strong>: ログファイルの保存場所</li>
            <li><strong>デバッグモード</strong>: 開発者向け機能の有効化</li>
        </ul>
        
        <h2>設定の管理</h2>
        
        <h3>設定ファイル</h3>
        <ul>
            <li><strong>場所</strong>: ユーザーディレクトリ/.qt_theme_studio/</li>
            <li><strong>形式</strong>: JSON形式での保存</li>
            <li><strong>バックアップ</strong>: 設定の自動バックアップ</li>
        </ul>
        
        <h3>設定の共有</h3>
        <ul>
            <li><strong>エクスポート</strong>: 設定ファイルのエクスポート</li>
            <li><strong>インポート</strong>: 他の環境からの設定インポート</li>
            <li><strong>リセット</strong>: デフォルト設定への復元</li>
        </ul>
        """
    
    def _get_shortcuts_content(self) -> str:
        """キーボードショートカットのヘルプコンテンツ"""
        return """
        <h1>キーボードショートカット</h1>
        
        <h2>ファイル操作</h2>
        <ul>
            <li><strong>Ctrl+N</strong>: 新規テーマ作成</li>
            <li><strong>Ctrl+O</strong>: テーマを開く</li>
            <li><strong>Ctrl+S</strong>: テーマを保存</li>
            <li><strong>Ctrl+Shift+S</strong>: 名前を付けて保存</li>
            <li><strong>Ctrl+E</strong>: エクスポート</li>
            <li><strong>Ctrl+I</strong>: インポート</li>
            <li><strong>Ctrl+Q</strong>: アプリケーション終了</li>
        </ul>
        
        <h2>編集操作</h2>
        <ul>
            <li><strong>Ctrl+Z</strong>: 元に戻す（Undo）</li>
            <li><strong>Ctrl+Y</strong>: やり直し（Redo）</li>
            <li><strong>Ctrl+Shift+Z</strong>: やり直し（Redo）</li>
            <li><strong>Ctrl+C</strong>: コピー</li>
            <li><strong>Ctrl+V</strong>: 貼り付け</li>
            <li><strong>Ctrl+X</strong>: 切り取り</li>
            <li><strong>Ctrl+A</strong>: すべて選択</li>
        </ul>
        
        <h2>表示操作</h2>
        <ul>
            <li><strong>F5</strong>: プレビュー表示切り替え</li>
            <li><strong>F11</strong>: フルスクリーン切り替え</li>
            <li><strong>Ctrl+1</strong>: テーマエディター表示</li>
            <li><strong>Ctrl+2</strong>: ゼブラエディター表示</li>
            <li><strong>Ctrl+3</strong>: テーマギャラリー表示</li>
            <li><strong>Ctrl+G</strong>: テーマギャラリーを開く</li>
        </ul>
        
        <h2>ツール操作</h2>
        <ul>
            <li><strong>Ctrl+T</strong>: 色の調和機能</li>
            <li><strong>Ctrl+H</strong>: コントラスト計算</li>
            <li><strong>Ctrl+R</strong>: レスポンシブテスト</li>
            <li><strong>Ctrl+P</strong>: プレビュー画像エクスポート</li>
            <li><strong>Ctrl+,</strong>: 設定を開く</li>
        </ul>
        
        <h2>ナビゲーション</h2>
        <ul>
            <li><strong>Tab</strong>: 次の項目へ移動</li>
            <li><strong>Shift+Tab</strong>: 前の項目へ移動</li>
            <li><strong>Enter</strong>: 選択項目を実行</li>
            <li><strong>Escape</strong>: ダイアログを閉じる</li>
            <li><strong>Space</strong>: チェックボックス切り替え</li>
        </ul>
        
        <h2>最近使用したテーマ</h2>
        <ul>
            <li><strong>Ctrl+1〜9</strong>: 最近使用したテーマを直接開く</li>
            <li><strong>Alt+1〜9</strong>: 最近使用したテーマをプレビュー</li>
        </ul>
        
        <h2>色選択</h2>
        <ul>
            <li><strong>C</strong>: カラーピッカーを開く</li>
            <li><strong>R</strong>: RGB入力モード</li>
            <li><strong>H</strong>: HSV入力モード</li>
            <li><strong>X</strong>: 16進値入力モード</li>
        </ul>
        
        <h2>プレビュー操作</h2>
        <ul>
            <li><strong>+</strong>: ズームイン</li>
            <li><strong>-</strong>: ズームアウト</li>
            <li><strong>0</strong>: ズームリセット</li>
            <li><strong>F</strong>: ウィンドウにフィット</li>
        </ul>
        
        <h2>ヘルプ</h2>
        <ul>
            <li><strong>F1</strong>: ヘルプを開く</li>
            <li><strong>Ctrl+F1</strong>: コンテキストヘルプ</li>
            <li><strong>Shift+F1</strong>: What's This?モード</li>
        </ul>
        
        <h2>カスタマイズ</h2>
        <p>キーボードショートカットは設定画面でカスタマイズできます：</p>
        <ul>
            <li>「編集」→「設定」→「キーボード」</li>
            <li>各機能に対してショートカットキーを設定</li>
            <li>競合するショートカットの自動検出</li>
            <li>デフォルト設定への復元機能</li>
        </ul>
        """
    
    def _get_troubleshooting_content(self) -> str:
        """トラブルシューティングのヘルプコンテンツ"""
        return """
        <h1>トラブルシューティング</h1>
        
        <h2>起動時の問題</h2>
        
        <h3>アプリケーションが起動しない</h3>
        <ul>
            <li><strong>Qtフレームワークの確認</strong>: PySide6、PyQt6、PyQt5のいずれかがインストールされているか確認</li>
            <li><strong>Pythonバージョン</strong>: Python 3.8以上が必要</li>
            <li><strong>依存関係</strong>: qt-theme-managerライブラリがインストールされているか確認</li>
            <li><strong>権限</strong>: アプリケーションの実行権限があるか確認</li>
        </ul>
        
        <h3>エラーメッセージが表示される</h3>
        <ul>
            <li><strong>「Qtフレームワークが見つかりません」</strong>: pip install PySide6 でインストール</li>
            <li><strong>「qt-theme-managerが見つかりません」</strong>: GitHubから直接インストール</li>
            <li><strong>「設定ファイルが読み込めません」</strong>: 設定ファイルを削除して再起動</li>
        </ul>
        
        <h2>テーマ編集の問題</h2>
        
        <h3>色が正しく表示されない</h3>
        <ul>
            <li><strong>色空間の確認</strong>: RGB、HSV設定を確認</li>
            <li><strong>モニター設定</strong>: ディスプレイの色設定を確認</li>
            <li><strong>プレビュー更新</strong>: F5キーでプレビューを更新</li>
        </ul>
        
        <h3>プレビューが更新されない</h3>
        <ul>
            <li><strong>自動更新設定</strong>: 設定で自動更新が有効か確認</li>
            <li><strong>手動更新</strong>: F5キーで手動更新</li>
            <li><strong>メモリ不足</strong>: 他のアプリケーションを終了してメモリを確保</li>
        </ul>
        
        <h2>ファイル操作の問題</h2>
        
        <h3>テーマファイルが開けない</h3>
        <ul>
            <li><strong>ファイル形式</strong>: 対応形式（JSON、QSS、CSS）か確認</li>
            <li><strong>ファイル破損</strong>: バックアップファイルから復元</li>
            <li><strong>権限</strong>: ファイルの読み取り権限があるか確認</li>
            <li><strong>文字エンコーディング</strong>: UTF-8エンコーディングか確認</li>
        </ul>
        
        <h3>保存ができない</h3>
        <ul>
            <li><strong>書き込み権限</strong>: 保存先フォルダの書き込み権限を確認</li>
            <li><strong>ディスク容量</strong>: 十分な空き容量があるか確認</li>
            <li><strong>ファイル名</strong>: 使用できない文字が含まれていないか確認</li>
        </ul>
        
        <h2>パフォーマンスの問題</h2>
        
        <h3>動作が重い</h3>
        <ul>
            <li><strong>メモリ使用量</strong>: タスクマネージャーでメモリ使用量を確認</li>
            <li><strong>プレビュー設定</strong>: プレビューの更新間隔を調整</li>
            <li><strong>ハードウェア加速</strong>: GPU加速を有効にする</li>
            <li><strong>履歴制限</strong>: Undo/Redo履歴の上限を下げる</li>
        </ul>
        
        <h3>メモリ不足エラー</h3>
        <ul>
            <li><strong>他のアプリケーション</strong>: 不要なアプリケーションを終了</li>
            <li><strong>大きなテーマファイル</strong>: テーマファイルのサイズを確認</li>
            <li><strong>設定調整</strong>: キャッシュサイズを小さくする</li>
        </ul>
        
        <h2>表示の問題</h2>
        
        <h3>文字化けが発生する</h3>
        <ul>
            <li><strong>フォント設定</strong>: システムフォントの設定を確認</li>
            <li><strong>文字エンコーディング</strong>: UTF-8エンコーディングを使用</li>
            <li><strong>言語設定</strong>: システムの言語設定を確認</li>
        </ul>
        
        <h3>レイアウトが崩れる</h3>
        <ul>
            <li><strong>DPIスケーリング</strong>: システムのDPI設定を確認</li>
            <li><strong>ウィンドウサイズ</strong>: 最小ウィンドウサイズを確保</li>
            <li><strong>設定リセット</strong>: ウィンドウ設定をリセット</li>
        </ul>
        
        <h2>解決しない場合</h2>
        
        <h3>ログファイルの確認</h3>
        <ul>
            <li><strong>場所</strong>: ~/.qt_theme_studio/logs/</li>
            <li><strong>内容</strong>: エラーメッセージと詳細情報</li>
            <li><strong>レベル</strong>: ログレベルをDEBUGに設定</li>
        </ul>
        
        <h3>設定のリセット</h3>
        <ul>
            <li><strong>設定ファイル削除</strong>: ~/.qt_theme_studio/settings.json を削除</li>
            <li><strong>キャッシュクリア</strong>: ~/.qt_theme_studio/cache/ を削除</li>
            <li><strong>再インストール</strong>: アプリケーションの再インストール</li>
        </ul>
        
        <h3>サポート</h3>
        <ul>
            <li><strong>GitHub Issues</strong>: バグレポートや機能要望</li>
            <li><strong>ドキュメント</strong>: 最新のドキュメントを確認</li>
            <li><strong>コミュニティ</strong>: ユーザーコミュニティでの質問</li>
        </ul>
        """