"""
qt-theme-manager ライブラリ統合アダプター

このモジュールは、qt-theme-managerライブラリとの統合機能を提供し、
テーマファイルの読み込み・保存・エクスポート機能を実装します。
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# カスタム例外クラス
class ThemeManagerError(Exception):
    """テーママネージャー関連のエラー"""


class ThemeLoadError(ThemeManagerError):
    """テーマ読み込みエラー"""


class ThemeSaveError(ThemeManagerError):
    """テーマ保存エラー"""


class ThemeExportError(ThemeManagerError):
    """テーマエクスポートエラー"""


class ThemeValidationError(ThemeManagerError):
    """テーマ検証エラー"""


class ThemeAdapter:
    """qt-theme-manager ライブラリ統合アダプター

    qt-theme-managerライブラリとの統合を提供し、テーマの読み込み、保存、
    エクスポート機能を実装します。
    """

    def __init__(self):
        """Theme Adapterを初期化する"""
        self.logger = logging.getLogger(__name__)
        self._theme_manager = None
        self._is_initialized = False

    def initialize_theme_manager(self) -> bool:
        """テーママネージャーを初期化する

        qt-theme-managerライブラリを初期化し、テーマ管理機能を利用可能にします。

        Returns:
            bool: 初期化が成功した場合True

        Raises:
            ThemeManagerError: qt-theme-managerライブラリが利用できない場合
        """
        try:
            # qt-theme-managerライブラリのインポートを試行
            import qt_theme_manager

            self._theme_manager = qt_theme_manager
            self._is_initialized = True

            self.logger.info("qt-theme-managerライブラリを正常に初期化しました")
            return True

        except ImportError:
            error_msg = (
                "qt-theme-managerライブラリが見つかりません。"
                "以下のコマンドでインストールしてください:\n"
                "pip install git+https://github.com/scottlz0310/"
                "Qt-Theme-Manager.git"
            )
            self.logger.error("{error_msg}\n詳細: {str(e)}")
            raise ThemeManagerError(error_msg)
        except Exception as e:
            error_msg = "qt-theme-managerライブラリの初期化に失敗しました: " "{str(e)}"
            self.logger.error(error_msg)
            raise ThemeManagerError(error_msg)

    def load_theme(self, theme_path: Union[str, Path]) -> Dict[str, Any]:
        """テーマファイルを読み込む

        指定されたパスからテーマファイルを読み込み、内部形式に変換します。
        JSON、QSS、CSS形式のテーマファイルをサポートします。

        Args:
            theme_path (Union[str, Path]): テーマファイルのパス

        Returns:
            Dict[str, Any]: 読み込まれたテーマデータ

        Raises:
            ThemeLoadError: テーマファイルの読み込みに失敗した場合
        """
        if not self._is_initialized:
            self.initialize_theme_manager()

        theme_path = Path(theme_path)

        if not theme_path.exists():
            error_msg = "テーマファイルが見つかりません: {theme_path}"
            self.logger.error(error_msg)
            raise ThemeLoadError(error_msg)

        try:
            file_extension = theme_path.suffix.lower()

            if file_extension == ".json":
                return self._load_json_theme(theme_path)
            elif file_extension == ".qss":
                return self._load_qss_theme(theme_path)
            elif file_extension == ".css":
                return self._load_css_theme(theme_path)
            else:
                error_msg = "サポートされていないテーマファイル形式: {file_extension}"
                self.logger.error(error_msg)
                raise ThemeLoadError(error_msg)

        except Exception as e:
            if isinstance(e, ThemeLoadError):
                raise
            error_msg = f"テーマファイルの読み込みに失敗しました: {str(e)}"
            self.logger.error(error_msg)
            raise ThemeLoadError(error_msg)

    def save_theme(self, theme_data: Dict[str, Any], path: Union[str, Path]) -> bool:
        """テーマファイルを保存する

        テーマデータをqt-theme-manager互換形式でファイルに保存します。

        Args:
            theme_data (Dict[str, Any]): 保存するテーマデータ
            path (Union[str, Path]): 保存先のパス

        Returns:
            bool: 保存が成功した場合True

        Raises:
            ThemeSaveError: テーマファイルの保存に失敗した場合
        """
        if not self._is_initialized:
            self.initialize_theme_manager()

        save_path = Path(path)

        try:
            # テーマデータの検証
            self._validate_theme_data(theme_data)

            # ディレクトリが存在しない場合は作成
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # JSON形式で保存（qt-theme-manager標準形式）
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(theme_data, f, ensure_ascii=False, indent=2)

            self.logger.info("テーマファイルを保存しました: {save_path}")
            return True

        except Exception as e:
            if isinstance(e, (ThemeSaveError, ThemeValidationError)):
                raise
            error_msg = "テーマファイルの保存に失敗しました: {str(e)}"
            self.logger.error(error_msg)
            raise ThemeSaveError(error_msg)

    def export_theme(self, theme_data: Dict[str, Any], format_type: str) -> str:
        """テーマを指定された形式でエクスポートする

        Args:
            theme_data: エクスポートするテーマデータ
            format_type: エクスポート形式（'json', 'qss', 'css'）

        Returns:
            str: エクスポートされたコンテンツ

        Raises:
            ThemeExportError: エクスポートに失敗した場合
        """
        try:
            format_type = format_type.lower()

            if format_type == "json":
                return json.dumps(theme_data, ensure_ascii=False, indent=2)
            elif format_type == "qss":
                return self._generate_qss_from_theme(theme_data)
            elif format_type == "css":
                return self._generate_css_from_theme(theme_data)
            else:
                raise ThemeExportError(
                    "サポートされていないエクスポート形式: {format_type}"
                )

        except Exception as e:
            error_msg = "テーマのエクスポートに失敗しました: {str(e)}"
            self.logger.error(error_msg)
            raise ThemeExportError(error_msg)

    def import_theme(self, file_path: str, format_type: str = None) -> Dict[str, Any]:
        """テーマファイルをインポートする

        Args:
            file_path: インポートするファイルのパス
            format_type: ファイル形式（自動検出の場合はNone）

        Returns:
            Dict[str, Any]: インポートされたテーマデータ

        Raises:
            ThemeLoadError: インポートに失敗した場合
        """
        try:
            # ImportServiceを使用してインポート
            from ..services.import_service import ThemeImportService

            import_service = ThemeImportService()
            theme_data = import_service.import_theme(file_path)

            self.logger.info("テーマファイルをインポートしました: {file_path}")
            return theme_data

        except Exception as e:
            error_msg = "テーマのインポートに失敗しました: {str(e)}"
            self.logger.error(error_msg)
            raise ThemeLoadError(error_msg)

    def get_supported_formats(self) -> List[str]:
        """サポートされているテーマ形式のリストを返す

        Returns:
            List[str]: サポートされている形式のリスト
        """
        return ["json", "qss", "css"]

    def validate_theme(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """テーマデータを検証する

        Args:
            theme_data (Dict[str, Any]): 検証するテーマデータ

        Returns:
            Dict[str, Any]: 検証結果
                - 'is_valid': bool - 検証が成功したかどうか
                - 'errors': List[str] - エラーメッセージのリスト
                - 'warnings': List[str] - 警告メッセージのリスト
        """
        result = {"is_valid": True, "errors": [], "warnings": []}

        try:
            self._validate_theme_data(theme_data)
        except ThemeValidationError as e:
            result["is_valid"] = False
            result["errors"].append(str())

        # 追加の検証ロジック
        self._validate_theme_structure(theme_data, result)
        self._validate_theme_colors(theme_data, result)

        return result

    def _load_json_theme(self, theme_path: Path) -> Dict[str, Any]:
        """JSON形式のテーマファイルを読み込む"""
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                theme_data = json.load(f)

            self.logger.info("JSONテーマファイルを読み込みました: {theme_path}")
            return theme_data

        except json.JSONDecodeError as e:
            error_msg = "JSONファイルの解析に失敗しました: {e}"
            self.logger.error(error_msg)
            raise ThemeLoadError(error_msg)
        except Exception as e:
            error_msg = "JSONファイルの読み込みに失敗しました: {e}"
            self.logger.error(error_msg)
            raise ThemeLoadError(error_msg)

    def _load_qss_theme(self, theme_path: Path) -> Dict[str, Any]:
        """QSS形式のテーマファイルを読み込む"""
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                qss_content = f.read()

            # QSSをテーマデータに変換（基本的な実装）
            theme_data = {
                "name": theme_path.stem,
                "version": "1.0.0",
                "type": "qss",
                "content": qss_content,
                "colors": self._extract_colors_from_qss(qss_content),
                "metadata": {"source_file": str(theme_path), "format": "qss"},
            }

            self.logger.info("QSSテーマファイルを読み込みました: {theme_path}")
            return theme_data

        except Exception as e:
            error_msg = "QSSファイルの読み込みに失敗しました: {e}"
            self.logger.error(error_msg)
            raise ThemeLoadError(error_msg)

    def _load_css_theme(self, theme_path: Path) -> Dict[str, Any]:
        """CSS形式のテーマファイルを読み込む"""
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                css_content = f.read()

            # CSSをテーマデータに変換（基本的な実装）
            theme_data = {
                "name": theme_path.stem,
                "version": "1.0.0",
                "type": "css",
                "content": css_content,
                "colors": self._extract_colors_from_css(css_content),
                "metadata": {"source_file": str(theme_path), "format": "css"},
            }

            self.logger.info("CSSテーマファイルを読み込みました: {theme_path}")
            return theme_data

        except Exception as e:
            error_msg = "CSSファイルの読み込みに失敗しました: {e}"
            self.logger.error(error_msg)
            raise ThemeLoadError(error_msg)

    def _export_to_json(self, theme_data: Dict[str, Any]) -> str:
        """テーマデータをJSON形式でエクスポートする"""
        try:
            return json.dumps(theme_data, ensure_ascii=False, indent=2)
        except Exception as e:
            error_msg = "JSON形式でのエクスポートに失敗しました: {str(e)}"
            self.logger.error(error_msg)
            raise ThemeExportError(error_msg)

    def _export_to_qss(self, theme_data: Dict[str, Any]) -> str:
        """テーマデータをQSS形式でエクスポートする"""
        try:
            # 既にQSS形式の場合はそのまま返す
            if theme_data.get("type") == "qss" and "content" in theme_data:
                return theme_data["content"]

            # テーマデータからQSSを生成
            qss_content = self._generate_qss_from_theme(theme_data)
            return qss_content

        except Exception as e:
            error_msg = "QSS形式でのエクスポートに失敗しました: {str(e)}"
            self.logger.error(error_msg)
            raise ThemeExportError(error_msg)

    def _export_to_css(self, theme_data: Dict[str, Any]) -> str:
        """テーマデータをCSS形式でエクスポートする"""
        try:
            # 既にCSS形式の場合はそのまま返す
            if theme_data.get("type") == "css" and "content" in theme_data:
                return theme_data["content"]

            # テーマデータからCSSを生成
            css_content = self._generate_css_from_theme(theme_data)
            return css_content

        except Exception as e:
            error_msg = "CSS形式でのエクスポートに失敗しました: {str(e)}"
            self.logger.error(error_msg)
            raise ThemeExportError(error_msg)

    def _validate_theme_data(self, theme_data: Dict[str, Any]) -> None:
        """テーマデータの基本的な検証を行う"""
        if not isinstance(theme_data, dict):
            raise ThemeValidationError("テーマデータは辞書形式である必要があります")

        # 必須フィールドの確認
        required_fields = ["name"]
        for field in required_fields:
            if field not in theme_data:
                raise ThemeValidationError("必須フィールドが不足しています: {field}")

        # 名前の検証
        if not isinstance(theme_data["name"], str) or not theme_data["name"].strip():
            raise ThemeValidationError("テーマ名は空でない文字列である必要があります")

    def _validate_theme_structure(
        self, theme_data: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """テーマデータの構造を検証する"""
        # バージョン情報の確認
        if "version" not in theme_data:
            result["warnings"].append("バージョン情報が設定されていません")

        # メタデータの確認
        if "metadata" not in theme_data:
            result["warnings"].append("メタデータが設定されていません")

    def _validate_theme_colors(
        self, theme_data: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """テーマの色設定を検証する"""
        if "colors" in theme_data:
            colors = theme_data["colors"]
            if isinstance(colors, dict):
                for color_name, color_value in colors.items():
                    if not self._is_valid_color(color_value):
                        result["warnings"].append(
                            "無効な色値が検出されました: {color_name} = {color_value}"
                        )

    def _is_valid_color(self, color_value: str) -> bool:
        """色値が有効かどうかを確認する"""
        if not isinstance(color_value, str):
            return False

        color_value = color_value.strip()

        # 16進数カラーコードの確認
        if color_value.startswith("#"):
            hex_part = color_value[1:]
            if len(hex_part) in [3, 6, 8]:  # #RGB, #RRGGBB, #RRGGBBAA
                try:
                    int(hex_part, 16)
                    return True
                except ValueError:
                    pass

        # RGB/RGBA形式の確認（簡易版）
        if color_value.startswith(("rgb(", "rgba(")):
            return True

        # 名前付き色の確認（基本的な色名）
        named_colors = {
            "black",
            "white",
            "red",
            "green",
            "blue",
            "yellow",
            "cyan",
            "magenta",
            "gray",
            "grey",
            "darkgray",
            "darkgrey",
            "lightgray",
            "lightgrey",
            "transparent",
        }
        if color_value.lower() in named_colors:
            return True

        return False

    def _extract_colors_from_qss(self, qss_content: str) -> Dict[str, str]:
        """QSSコンテンツから色情報を抽出する（基本的な実装）"""
        import re

        colors = {}

        # 16進数カラーコードを抽出
        hex_pattern = r"#[0-9a-fA-F]{3,8}"
        hex_matches = re.findall(hex_pattern, qss_content)

        for i, color in enumerate(set(hex_matches)):
            colors["color_{i+1}"] = color

        return colors

    def _extract_colors_from_css(self, css_content: str) -> Dict[str, str]:
        """CSSコンテンツから色情報を抽出する（基本的な実装）"""
        # QSSと同様の処理
        return self._extract_colors_from_qss(css_content)

    def _generate_qss_from_theme(self, theme_data: Dict[str, Any]) -> str:
        """テーマデータからQSSを生成する（基本的な実装）"""
        qss_lines = []

        # テーマ名をコメントとして追加
        qss_lines.append("/* Theme: {theme_data.get('name', 'Unnamed')} */")
        qss_lines.append("")

        # 色設定がある場合は基本的なスタイルを生成
        if "colors" in theme_data and isinstance(theme_data["colors"], dict):
            colors = theme_data["colors"]

            # 基本的なウィジェットスタイル
            if "background" in colors:
                qss_lines.append(
                    "QWidget {{ background-color: {colors['background']}; }}"
                )

            if "text" in colors:
                qss_lines.append("QWidget {{ color: {colors['text']}; }}")

            if "primary" in colors:
                qss_lines.append(
                    "QPushButton {{ background-color: {colors['primary']}; }}"
                )

        return "\n".join(qss_lines)

    def _generate_css_from_theme(self, theme_data: Dict[str, Any]) -> str:
        """テーマデータからCSSを生成する（基本的な実装）"""
        css_lines = []

        # テーマ名をコメントとして追加
        css_lines.append("/* Theme: {theme_data.get('name', 'Unnamed')} */")
        css_lines.append("")

        # 色設定がある場合は基本的なスタイルを生成
        if "colors" in theme_data and isinstance(theme_data["colors"], dict):
            colors = theme_data["colors"]

            # CSS変数として色を定義
            css_lines.append(":root {")
            for color_name, color_value in colors.items():
                css_lines.append("  --{color_name}: {color_value};")
            css_lines.append("}")
            css_lines.append("")

            # 基本的なスタイル
            if "background" in colors:
                css_lines.append("body {{ background-color: var(--background); }}")

            if "text" in colors:
                css_lines.append("body {{ color: var(--text); }}")

        return "\n".join(css_lines)

    @property
    def is_initialized(self) -> bool:
        """Theme Adapterが初期化されているかどうかを返す

        Returns:
            bool: 初期化済みの場合True
        """
        return self._is_initialized

    @property
    def theme_manager(self) -> Optional[Any]:
        """qt-theme-managerライブラリのインスタンスを返す

        Returns:
            Optional[Any]: qt-theme-managerライブラリ（未初期化の場合はNone）
        """
        return self._theme_manager
