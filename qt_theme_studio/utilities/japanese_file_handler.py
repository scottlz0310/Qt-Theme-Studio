"""
日本語ファイル処理モジュール

このモジュールは、日本語ファイル名・パスの適切な処理機能を提供します。
文字化け防止機能と、日本語テキストの妥当性検証を実装します。
"""

import sys
import tempfile
import unicodedata
from typing import Any, Dict, List, Optional
from pathlib import Path
import os

from ..logger import LogCategory, get_logger


class JapaneseFileHandler:
    """
    日本語ファイル処理クラス

    日本語ファイル名・パスの適切な処理機能を提供し、
    文字化け防止とファイル操作の安全性を確保します。
    """

    def __init__(self):
        """日本語ファイル処理を初期化します"""
        self.logger = get_logger()

        # システムエンコーディング情報
        self.system_encoding = sys.getfilesystemencoding()
        self.default_encoding = "utf-8"

        # 一時ディレクトリ
        self.temp_dir = tempfile.gettempdir()

        self.logger.info(
            f"日本語ファイル処理を初期化しました (システムエンコーディング: {self.system_encoding})",
            LogCategory.SYSTEM,
        )

    def normalize_path(self, file_path: str) -> str:
        """
        ファイルパスを正規化します

        Args:
            file_path: 正規化するファイルパス

        Returns:
            str: 正規化されたファイルパス
        """
        try:
            # パスの正規化
            normalized_path = os.path.normpath(file_path)

            # Unicode正規化（NFC形式）
            normalized_path = unicodedata.normalize("NFC", normalized_path)

            # パス区切り文字の統一
            normalized_path = normalized_path.replace("\\", os.sep)

            return normalized_path

        except Exception:
            self.logger.error(
                "パスの正規化に失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            return file_path

    def validate_path(self, file_path: str) -> bool:
        """
        ファイルパスの妥当性を検証します

        Args:
            file_path: 検証するファイルパス

        Returns:
            bool: 妥当な場合True
        """
        try:
            # 空文字チェック
            if not file_path or not file_path.strip():
                return False

            # エンコーディングチェック
            file_path.encode(self.default_encoding)

            # 制御文字チェック
            for char in file_path:
                if unicodedata.category(char).startswith("C") and char not in [
                    "\t",
                    "\n",
                    "\r",
                ]:
                    return False

            # 無効な文字チェック（Windows）
            if sys.platform.startswith("win"):
                invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
                for char in invalid_chars:
                    if char in file_path:
                        return False

            # パスの長さチェック
            if len(file_path) > 260:  # Windows MAX_PATH制限
                return False

            return True

        except UnicodeEncodeError:
            return False
        except Exception:
            self.logger.error("パスの検証に失敗しました: {str(e)}", LogCategory.SYSTEM)
            return False

    def safe_open(
        self, file_path: str, mode: str = "r", encoding: Optional[str] = None
    ) -> Optional[Any]:
        """
        日本語ファイルを安全に開きます

        Args:
            file_path: ファイルパス
            mode: ファイルオープンモード
            encoding: エンコーディング（Noneの場合はUTF-8を使用）

        Returns:
            ファイルオブジェクト（失敗時はNone）
        """
        if encoding is None:
            encoding = self.default_encoding

        try:
            # パスを正規化
            normalized_path = self.normalize_path(file_path)

            # パスの妥当性を検証
            if not self.validate_path(normalized_path):
                self.logger.error(
                    "無効なファイルパスです: {file_path}", LogCategory.SYSTEM
                )
                return None

            # ファイルを開く
            file_obj = open(normalized_path, mode, encoding=encoding, errors="replace")

            self.logger.debug(
                "ファイルを開きました: {normalized_path}", LogCategory.SYSTEM
            )
            return file_obj

        except FileNotFoundError:
            self.logger.error(
                "ファイルが見つかりません: {file_path}", LogCategory.SYSTEM
            )
            return None
        except PermissionError:
            self.logger.error(
                "ファイルへのアクセス権限がありません: {file_path}", LogCategory.SYSTEM
            )
            return None
        except UnicodeDecodeError as e:
            self.logger.error(
                "ファイルのエンコーディングエラー: {str(e)}", LogCategory.SYSTEM
            )
            return None
        except Exception:
            self.logger.error(
                "ファイルのオープンに失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            return None

    def safe_read(
        self, file_path: str, encoding: Optional[str] = None
    ) -> Optional[str]:
        """
        日本語ファイルを安全に読み込みます

        Args:
            file_path: ファイルパス
            encoding: エンコーディング（Noneの場合はUTF-8を使用）

        Returns:
            str: ファイル内容（失敗時はNone）
        """
        file_obj = self.safe_open(file_path, "r", encoding)
        if file_obj is None:
            return None

        try:
            content = file_obj.read()
            file_obj.close()

            # テキストの妥当性を検証
            if self.validate_text(content):
                return content
            else:
                self.logger.warning(
                    "ファイル内容に無効な文字が含まれています: {file_path}",
                    LogCategory.SYSTEM,
                )
                return content  # 警告は出すが内容は返す

        except Exception:
            self.logger.error(
                "ファイルの読み込みに失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            if file_obj:
                file_obj.close()
            return None

    def safe_write(
        self, file_path: str, content: str, encoding: Optional[str] = None
    ) -> bool:
        """
        日本語ファイルを安全に書き込みます

        Args:
            file_path: ファイルパス
            content: 書き込む内容
            encoding: エンコーディング（Noneの場合はUTF-8を使用）

        Returns:
            bool: 成功した場合True
        """
        # ディレクトリが存在しない場合は作成
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception:
                self.logger.error(
                    "ディレクトリの作成に失敗しました: {str(e)}", LogCategory.SYSTEM
                )
                return False

        file_obj = self.safe_open(file_path, "w", encoding)
        if file_obj is None:
            return False

        try:
            file_obj.write(content)
            file_obj.close()

            self.logger.debug(
                "ファイルを書き込みました: {file_path}", LogCategory.SYSTEM
            )
            return True

        except Exception:
            self.logger.error(
                "ファイルの書き込みに失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            if file_obj:
                file_obj.close()
            return False

    def validate_text(self, text: str) -> bool:
        """
        日本語テキストの妥当性を検証します

        Args:
            text: 検証するテキスト

        Returns:
            bool: 妥当な場合True
        """
        try:
            # UTF-8エンコーディングの確認
            text.encode(self.default_encoding)

            # 制御文字のチェック（改行・タブは除く）
            for char in text:
                category = unicodedata.category(char)
                if category.startswith("C") and char not in ["\t", "\n", "\r"]:
                    return False

            return True

        except UnicodeEncodeError:
            return False
        except Exception:
            self.logger.error(
                "テキストの検証に失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            return False

    def get_safe_filename(self, filename: str) -> str:
        """
        安全なファイル名を生成します

        Args:
            filename: 元のファイル名

        Returns:
            str: 安全なファイル名
        """
        try:
            # Unicode正規化
            safe_name = unicodedata.normalize("NFC", filename)

            # 無効な文字を置換（プラットフォーム共通の基本的な文字）
            invalid_chars = ["<", ">", ":", '"', "|", "?", "*"]
            for char in invalid_chars:
                safe_name = safe_name.replace(char, "_")

            # Windows固有の追加文字
            if sys.platform.startswith("win"):
                win_invalid_chars = ["\\", "/"]
                for char in win_invalid_chars:
                    safe_name = safe_name.replace(char, "_")

            # 制御文字を削除
            safe_name = "".join(
                char
                for char in safe_name
                if not unicodedata.category(char).startswith("C")
                or char in ["\t", "\n", "\r"]
            )

            # 長さ制限
            if len(safe_name) > 200:
                name, ext = os.path.splitext(safe_name)
                safe_name = name[: 200 - len(ext)] + ext

            # 空文字の場合はデフォルト名を使用
            if not safe_name.strip():
                safe_name = "untitled"

            return safe_name

        except Exception:
            self.logger.error(
                "安全なファイル名の生成に失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            return "untitled"

    def create_backup_path(self, original_path: str) -> str:
        """
        バックアップファイルのパスを生成します

        Args:
            original_path: 元のファイルパス

        Returns:
            str: バックアップファイルのパス
        """
        try:
            path_obj = Path(original_path)
            backup_name = "{path_obj.stem}_backup{path_obj.suffix}"
            backup_path = path_obj.parent / backup_name

            # 既存のバックアップファイルがある場合は番号を付ける
            counter = 1
            while backup_path.exists():
                backup_name = "{path_obj.stem}_backup_{counter}{path_obj.suffix}"
                backup_path = path_obj.parent / backup_name
                counter += 1

            return str(backup_path)

        except Exception:
            self.logger.error(
                "バックアップパスの生成に失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            # フォールバック: 一時ディレクトリを使用
            import time

            timestamp = int(time.time())
            return os.path.join(self.temp_dir, "backup_{timestamp}.bak")

    def get_encoding_info(self, file_path: str) -> Dict[str, Any]:
        """
        ファイルのエンコーディング情報を取得します

        Args:
            file_path: ファイルパス

        Returns:
            Dict[str, Any]: エンコーディング情報
        """
        info = {
            "detected_encoding": None,
            "confidence": 0.0,
            "is_utf8": False,
            "has_bom": False,
            "errors": [],
        }

        try:
            # ファイルの先頭を読み込んでBOMをチェック
            with open(file_path, "rb") as f:
                raw_data = f.read(1024)

            # BOMチェック
            if raw_data.startswith(b"\xef\xbb\xbf"):
                info["has_bom"] = True
                info["detected_encoding"] = "utf-8-sig"
            elif raw_data.startswith(b"\xff\xfe"):
                info["detected_encoding"] = "utf-16-le"
            elif raw_data.startswith(b"\xfe\xff"):
                info["detected_encoding"] = "utf-16-be"

            # UTF-8チェック
            try:
                raw_data.decode("utf-8")
                info["is_utf8"] = True
                if not info["detected_encoding"]:
                    info["detected_encoding"] = "utf-8"
                    info["confidence"] = 0.9
            except UnicodeDecodeError:
                info["is_utf8"] = False

            # エンコーディング検出ライブラリがある場合は使用
            try:
                import chardet

                detection = chardet.detect(raw_data)
                if detection and detection["encoding"]:
                    info["detected_encoding"] = detection["encoding"]
                    info["confidence"] = detection["confidence"]
            except ImportError:
                pass

        except Exception:
            info["errors"].append(str())
            self.logger.error(
                "エンコーディング情報の取得に失敗しました: {str(e)}",
                LogCategory.SYSTEM,
            )

        return info

    def convert_encoding(self, file_path: str, target_encoding: str = "utf-8") -> bool:
        """
        ファイルのエンコーディングを変換します

        Args:
            file_path: ファイルパス
            target_encoding: 変換先エンコーディング

        Returns:
            bool: 成功した場合True
        """
        try:
            # エンコーディング情報を取得
            encoding_info = self.get_encoding_info(file_path)
            source_encoding = encoding_info.get("detected_encoding", "utf-8")

            if source_encoding == target_encoding:
                self.logger.debug(
                    "エンコーディング変換は不要です: {file_path}", LogCategory.SYSTEM
                )
                return True

            # バックアップを作成
            backup_path = self.create_backup_path(file_path)
            import shutil

            shutil.copy2(file_path, backup_path)

            # ファイルを読み込み
            with open(file_path, "r", encoding=source_encoding, errors="replace") as f:
                content = f.read()

            # 新しいエンコーディングで書き込み
            with open(file_path, "w", encoding=target_encoding, errors="replace") as f:
                f.write(content)

            self.logger.info(
                "エンコーディングを変換しました: {source_encoding} -> {target_encoding}",
                LogCategory.SYSTEM,
            )
            return True

        except Exception:
            self.logger.error(
                "エンコーディング変換に失敗しました: {str(e)}", LogCategory.SYSTEM
            )
            return False

    def list_japanese_files(
        self, directory: str, extensions: Optional[List[str]] = None
    ) -> List[str]:
        """
        ディレクトリ内の日本語ファイルをリストアップします

        Args:
            directory: 検索ディレクトリ
            extensions: 対象拡張子のリスト（Noneの場合は全ファイル）

        Returns:
            List[str]: 日本語ファイルのパスリスト
        """
        japanese_files = []

        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)

                    # 拡張子フィルタ
                    if extensions:
                        name, ext = os.path.splitext(file)
                        if ext.lower() not in extensions:
                            continue

                    # 日本語文字が含まれているかチェック
                    if self._contains_japanese(file_path):
                        japanese_files.append(file_path)

        except Exception:
            self.logger.error(
                "日本語ファイルの検索に失敗しました: {str(e)}", LogCategory.SYSTEM
            )

        return japanese_files

    def _contains_japanese(self, text: str) -> bool:
        """
        テキストに日本語文字が含まれているかチェックします

        Args:
            text: チェックするテキスト

        Returns:
            bool: 日本語文字が含まれている場合True
        """
        for char in text:
            # ひらがな、カタカナ、漢字の範囲をチェック
            if (
                "\u3040" <= char <= "\u309f"  # ひらがな
                or "\u30a0" <= char <= "\u30ff"  # カタカナ
                or "\u4e00" <= char <= "\u9faf"
            ):  # 漢字
                return True
        return False
