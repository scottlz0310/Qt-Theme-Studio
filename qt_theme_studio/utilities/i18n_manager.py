"""
国際化管理モジュール

このモジュールは、Qt-Theme-Studioの国際化機能を管理します。
QTranslatorを使用した日本語翻訳システムを提供し、
すべてのUIテキスト、メニュー、ダイアログの日本語化を実現します。
"""

from typing import Any, Dict, Optional

from ..logger import LogCategory, get_logger


class I18nManager:
    """
    国際化管理クラス

    QTranslatorを使用した日本語翻訳システムを管理し、
    アプリケーション全体の国際化機能を提供します。
    """

    def __init__(self, qt_adapter):
        """
        国際化管理を初期化します

        Args:
            qt_adapter: Qt フレームワークアダプター
        """
        self.qt_adapter = qt_adapter
        self.logger = get_logger()

        # Qtモジュールを取得
        self.qt_modules = qt_adapter.get_qt_modules()
        self.QtCore = self.qt_modules["QtCore"]
        self.QtWidgets = self.qt_modules["QtWidgets"]

        # 翻訳オブジェクト
        self.translator: Optional[Any] = None
        self.qt_translator: Optional[Any] = None

        # 現在の言語
        self.current_language = "ja_JP"

        # 翻訳辞書（フォールバック用）
        self.translations: Dict[str, str] = {}

        # 翻訳システムを初期化
        self._initialize_translations()

        self.logger.info("国際化管理を初期化しました", LogCategory.SYSTEM)

    def _initialize_translations(self) -> None:
        """翻訳システムを初期化します"""
        try:
            # アプリケーション翻訳を設定
            self._setup_application_translator()

            # Qt標準翻訳を設定
            self._setup_qt_translator()

            # フォールバック翻訳辞書を設定
            self._setup_fallback_translations()

            self.logger.info("翻訳システムを初期化しました", LogCategory.SYSTEM)

        except Exception:
            self.logger.error(
                "翻訳システムの初期化に失敗しました: {str(e)}", LogCategory.SYSTEM
            )

    def _setup_application_translator(self) -> None:
        """アプリケーション翻訳を設定します"""
        self.translator = self.QtCore.QTranslator()

        # 翻訳ファイルのパスを取得
        translation_path = self._get_translation_path()
        translation_file = os.path.join(translation_path, "qt_theme_studio_ja.qm")

        # 翻訳ファイルが存在する場合は読み込み
        if os.path.exists(translation_file):
            if self.translator.load(translation_file):
                app = self.QtWidgets.QApplication.instance()
                if app:
                    app.installTranslator(self.translator)
                    self.logger.info(
                        "翻訳ファイルを読み込みました: {translation_file}",
                        LogCategory.SYSTEM,
                    )
                else:
                    self.logger.warning(
                        "QApplicationインスタンスが見つかりません", LogCategory.SYSTEM
                    )
            else:
                self.logger.warning(
                    "翻訳ファイルの読み込みに失敗しました: {translation_file}",
                    LogCategory.SYSTEM,
                )
        else:
            self.logger.debug(
                "翻訳ファイルが見つかりません: {translation_file}", LogCategory.SYSTEM
            )

    def _setup_qt_translator(self) -> None:
        """Qt標準翻訳を設定します"""
        self.qt_translator = self.QtCore.QTranslator()

        # Qt標準翻訳ファイルを読み込み
        qt_translation_path = self.QtCore.QLibraryInfo.path(
            self.QtCore.QLibraryInfo.LibraryPath.TranslationsPath
        )

        qt_translation_file = "qt_{self.current_language}"

        if self.qt_translator.load(qt_translation_file, qt_translation_path):
            app = self.QtWidgets.QApplication.instance()
            if app:
                app.installTranslator(self.qt_translator)
                self.logger.info(
                    "Qt標準翻訳を読み込みました: {qt_translation_file}",
                    LogCategory.SYSTEM,
                )
        else:
            self.logger.debug(
                "Qt標準翻訳の読み込みに失敗しました: {qt_translation_file}",
                LogCategory.SYSTEM,
            )

    def _setup_fallback_translations(self) -> None:
        """フォールバック翻訳辞書を設定します"""
        self.translations = {
            # アプリケーション基本
            "Qt-Theme-Studio": "Qt-Theme-Studio",
            "Theme Editor": "テーマエディター",
            "Zebra Pattern Editor": "ゼブラパターンエディター",
            "Live Preview": "ライブプレビュー",
            "Theme Gallery": "テーマギャラリー",
            # メニュー項目
            "File": "ファイル",
            "Edit": "編集",
            "Theme": "テーマ",
            "View": "表示",
            "Tools": "ツール",
            "Help": "ヘルプ",
            # ファイルメニュー
            "New Theme": "新規テーマ",
            "Open Theme": "テーマを開く",
            "Save Theme": "テーマを保存",
            "Save As": "名前を付けて保存",
            "Export": "エクスポート",
            "Import": "インポート",
            "Recent Themes": "最近使用したテーマ",
            "Exit": "終了",
            # 編集メニュー
            "Undo": "元に戻す",
            "Redo": "やり直し",
            "Preferences": "設定",
            "Reset Workspace": "ワークスペースリセット",
            # 表示メニュー
            "Toolbar": "ツールバー",
            "Status Bar": "ステータスバー",
            "Full Screen": "フルスクリーン",
            # ツールメニュー
            "Accessibility Check": "アクセシビリティチェック",
            "Contrast Calculator": "色コントラスト計算",
            "Export Preview Image": "プレビュー画像エクスポート",
            # ヘルプメニュー
            "User Manual": "ユーザーマニュアル",
            "About Qt-Theme-Studio": "Qt-Theme-Studioについて",
            "About Qt": "Qtについて",
            # ダイアログ
            "OK": "OK",
            "Cancel": "キャンセル",
            "Yes": "はい",
            "No": "いいえ",
            "Apply": "適用",
            "Close": "閉じる",
            # エラーメッセージ
            "Error": "エラー",
            "Warning": "警告",
            "Information": "情報",
            "File not found": "ファイルが見つかりません",
            "Failed to save file": "ファイルの保存に失敗しました",
            "Failed to load file": "ファイルの読み込みに失敗しました",
            # ステータスメッセージ
            "Ready": "準備完了",
            "Loading": "読み込み中",
            "Saving": "保存中",
            "Theme loaded successfully": "テーマを正常に読み込みました",
            "Theme saved successfully": "テーマを正常に保存しました",
            # テーマエディター
            "Color": "色",
            "Font": "フォント",
            "Size": "サイズ",
            "Background": "背景",
            "Foreground": "前景",
            "Border": "境界線",
            "Margin": "マージン",
            "Padding": "パディング",
            # ゼブラパターンエディター
            "Contrast Ratio": "コントラスト比",
            "WCAG Level": "WCAGレベル",
            "AA Compliant": "AA準拠",
            "AAA Compliant": "AAA準拠",
            "Improve Colors": "色を改善",
            # プレビュー
            "Preview": "プレビュー",
            "Update Preview": "プレビューを更新",
            "Export Image": "画像をエクスポート",
            # ファイル形式
            "JSON Format": "JSON形式",
            "QSS Format": "QSS形式",
            "CSS Format": "CSS形式",
            "PNG Image": "PNG画像",
            # アクセシビリティ
            "Accessibility": "アクセシビリティ",
            "Color Blind Safe": "色覚異常対応",
            "High Contrast": "高コントラスト",
            "Large Text": "大きなテキスト",
        }

        self.logger.debug("フォールバック翻訳辞書を設定しました", LogCategory.SYSTEM)

    def _get_translation_path(self) -> str:
        """翻訳ファイルのパスを取得します"""
        # パッケージのリソースディレクトリを取得
        current_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.dirname(current_dir)
        translation_path = os.path.join(package_dir, "resources", "translations")

        # ディレクトリが存在しない場合は作成
        os.makedirs(translation_path, exist_ok=True)

        return translation_path

    def tr(self, text: str, context: str = "ThemeStudio") -> str:
        """
        テキストを翻訳します

        Args:
            text: 翻訳するテキスト
            context: 翻訳コンテキスト

        Returns:
            str: 翻訳されたテキスト
        """
        # QApplicationの翻訳機能を使用
        app = self.QtWidgets.QApplication.instance()
        if app:
            translated = app.translate(context, text)
            if translated != text:
                return translated

        # フォールバック翻訳辞書を使用
        if text in self.translations:
            return self.translations[text]

        # 翻訳が見つからない場合は元のテキストを返す
        return text

    def get_language(self) -> str:
        """
        現在の言語を取得します

        Returns:
            str: 現在の言語コード
        """
        return self.current_language

    def set_language(self, language: str) -> bool:
        """
        言語を設定します

        Args:
            language: 言語コード（例: "ja_JP", "en_US"）

        Returns:
            bool: 設定に成功した場合True
        """
        if language == self.current_language:
            return True

        try:
            # 現在の翻訳を削除
            self._remove_current_translators()

            # 新しい言語を設定
            self.current_language = language

            # 翻訳システムを再初期化
            self._initialize_translations()

            self.logger.info("言語を変更しました: {language}", LogCategory.SYSTEM)
            return True

        except Exception:
            self.logger.error("言語の変更に失敗しました: {str(e)}", LogCategory.SYSTEM)
            return False

    def _remove_current_translators(self) -> None:
        """現在の翻訳を削除します"""
        app = self.QtWidgets.QApplication.instance()
        if app:
            if self.translator:
                app.removeTranslator(self.translator)
            if self.qt_translator:
                app.removeTranslator(self.qt_translator)

    def get_available_languages(self) -> Dict[str, str]:
        """
        利用可能な言語のリストを取得します

        Returns:
            Dict[str, str]: 言語コードと表示名の辞書
        """
        return {
            "ja_JP": "日本語",
            "en_US": "English",
        }

    def create_translation_file(self) -> str:
        """
        翻訳ファイル（.ts）を作成します

        Returns:
            str: 作成された翻訳ファイルのパス
        """
        translation_path = self._get_translation_path()
        ts_file = os.path.join(translation_path, "qt_theme_studio_ja.ts")

        # 翻訳ファイルの内容を生成
        ts_content = self._generate_ts_content()

        try:
            with open(ts_file, "w", encoding="utf-8") as f:
                f.write(ts_content)

            self.logger.info(
                "翻訳ファイルを作成しました: {ts_file}", LogCategory.SYSTEM
            )
            return ts_file

        except Exception:
            self.logger.error(
                "翻訳ファイルの作成に失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            return ""

    def _generate_ts_content(self) -> str:
        """翻訳ファイル（.ts）の内容を生成します"""
        ts_content = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="ja_JP">
<context>
    <name>ThemeStudio</name>
"""

        # フォールバック翻訳辞書から翻訳エントリを生成
        for source, translation in self.translations.items():
            ts_content += """    <message>
        <source>{source}</source>
        <translation>{translation}</translation>
    </message>
"""

        ts_content += """</context>
</TS>
"""

        return ts_content

    def handle_japanese_file_paths(self, file_path: str) -> str:
        """
        日本語ファイルパスを適切に処理します

        Args:
            file_path: ファイルパス

        Returns:
            str: 処理されたファイルパス
        """
        try:
            # パスの正規化
            normalized_path = os.path.normpath(file_path)

            # UTF-8エンコーディングの確認
            normalized_path.encode("utf-8")

            return normalized_path

        except UnicodeEncodeError:
            self.logger.error(
                "日本語ファイルパスの処理に失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            # フォールバック: ASCII文字のみのパスを生成
            import tempfile

            temp_dir = tempfile.gettempdir()
            fallback_path = os.path.join(temp_dir, "qt_theme_studio_temp")
            self.logger.warning(
                "フォールバックパスを使用します: {fallback_path}", LogCategory.SYSTEM
            )
            return fallback_path

    def validate_japanese_text(self, text: str) -> bool:
        """
        日本語テキストの妥当性を検証します

        Args:
            text: 検証するテキスト

        Returns:
            bool: 妥当な場合True
        """
        try:
            # UTF-8エンコーディングの確認
            text.encode("utf-8")

            # 制御文字のチェック
            import unicodedata

            for char in text:
                if unicodedata.category(char).startswith("C"):
                    return False

            return True

        except UnicodeEncodeError:
            return False

    def get_localized_error_message(self, error_key: str, **kwargs) -> str:
        """
        ローカライズされたエラーメッセージを取得します

        Args:
            error_key: エラーキー
            **kwargs: メッセージのフォーマット引数

        Returns:
            str: ローカライズされたエラーメッセージ
        """
        error_messages = {
            "file_not_found": "ファイルが見つかりません: {file_path}",
            "save_failed": "ファイルの保存に失敗しました: {error}",
            "load_failed": "ファイルの読み込みに失敗しました: {error}",
            "invalid_theme": "無効なテーマファイルです: {file_path}",
            "qt_framework_not_found": "Qtフレームワークが見つかりません",
            "theme_validation_failed": "テーマの検証に失敗しました: {errors}",
            "export_failed": "エクスポートに失敗しました: {error}",
            "import_failed": "インポートに失敗しました: {error}",
            "accessibility_check_failed": "アクセシビリティチェックに失敗しました: {error}",
            "preview_update_failed": "プレビューの更新に失敗しました: {error}",
        }

        message_template = error_messages.get(error_key, "不明なエラーが発生しました")

        try:
            return message_template.format(**kwargs)
        except KeyError:
            self.logger.warning(
                "エラーメッセージのフォーマットに失敗しました: {str(e)}",
                LogCategory.SYSTEM,
            )
            return message_template

    def get_localized_status_message(self, status_key: str, **kwargs) -> str:
        """
        ローカライズされたステータスメッセージを取得します

        Args:
            status_key: ステータスキー
            **kwargs: メッセージのフォーマット引数

        Returns:
            str: ローカライズされたステータスメッセージ
        """
        status_messages = {
            "ready": "準備完了",
            "loading": "読み込み中...",
            "saving": "保存中...",
            "exporting": "エクスポート中...",
            "importing": "インポート中...",
            "theme_loaded": "テーマを読み込みました: {theme_name}",
            "theme_saved": "テーマを保存しました: {theme_name}",
            "preview_updated": "プレビューを更新しました",
            "accessibility_check_complete": "アクセシビリティチェックが完了しました",
            "export_complete": "エクスポートが完了しました: {file_path}",
            "import_complete": "インポートが完了しました: {file_path}",
        }

        message_template = status_messages.get(status_key, "処理中...")

        try:
            return message_template.format(**kwargs)
        except KeyError:
            self.logger.warning(
                "ステータスメッセージのフォーマットに失敗しました: {str(e)}",
                LogCategory.SYSTEM,
            )
            return message_template
