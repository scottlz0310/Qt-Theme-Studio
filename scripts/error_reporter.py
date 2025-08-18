#!/usr/bin/env python3
"""
構造化エラーレポートシステム

例外発生時の詳細コンテキスト収集、スタックトレースの日本語化、
デバッグ情報の自動収集機能を提供します。
"""

import inspect
import json
import os
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from qt_theme_studio.logger import LogCategory, LogContext, get_logger

logger = get_logger(__name__)


class SystemInfo:
    """システム情報収集クラス"""

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """システム情報を収集"""
        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
            },
            "python": {
                "version": sys.version,
                "version_info": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro,
                },
                "executable": sys.executable,
                "path": sys.path[:5],  # 最初の5つのパスのみ
            },
            "environment": {
                "cwd": os.getcwd(),
                "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
                "home": os.environ.get(
                    "HOME", os.environ.get("USERPROFILE", "unknown")
                ),
                "path_env": os.environ.get("PATH", "")[:500],  # 最初の500文字のみ
            },
        }

    @staticmethod
    def get_qt_info() -> Dict[str, Any]:
        """Qt関連情報を収集"""
        qt_info = {"available_frameworks": [], "active_framework": None}

        # PySide6チェック
        try:
            import PySide6

            qt_info["available_frameworks"].append(
                {
                    "name": "PySide6",
                    "version": PySide6.__version__,
                    "qt_version": PySide6.QtCore.qVersion()
                    if hasattr(PySide6, "QtCore")
                    else "unknown",
                }
            )
            if qt_info["active_framework"] is None:
                qt_info["active_framework"] = "PySide6"
        except ImportError:
            pass

        # PyQt6チェック
        try:
            import PyQt6

            qt_info["available_frameworks"].append(
                {
                    "name": "PyQt6",
                    "version": getattr(PyQt6, "__version__", "unknown"),
                    "qt_version": PyQt6.QtCore.qVersion()
                    if hasattr(PyQt6, "QtCore")
                    else "unknown",
                }
            )
            if qt_info["active_framework"] is None:
                qt_info["active_framework"] = "PyQt6"
        except ImportError:
            pass

        # PyQt5チェック
        try:
            import PyQt5

            qt_info["available_frameworks"].append(
                {
                    "name": "PyQt5",
                    "version": getattr(PyQt5, "__version__", "unknown"),
                    "qt_version": PyQt5.QtCore.qVersion()
                    if hasattr(PyQt5, "QtCore")
                    else "unknown",
                }
            )
            if qt_info["active_framework"] is None:
                qt_info["active_framework"] = "PyQt5"
        except ImportError:
            pass

        return qt_info

    @staticmethod
    def get_dependencies_info() -> Dict[str, Any]:
        """依存関係情報を収集"""
        dependencies = {}

        # 主要な依存関係をチェック
        important_packages = ["qt-theme-manager", "pytest", "ruff", "bandit", "safety"]

        for package in important_packages:
            try:
                import importlib.metadata

                version = importlib.metadata.version(package)
                dependencies[package] = version
            except importlib.metadata.PackageNotFoundError:
                dependencies[package] = "not_installed"
            except Exception:
                dependencies[package] = "unknown"

        return dependencies


class StackTraceTranslator:
    """スタックトレース日本語化クラス"""

    # 英語→日本語の翻訳マップ
    TRANSLATIONS = {
        "Traceback (most recent call last)": "トレースバック（最新の呼び出し順）:",
        "File": "ファイル",
        "line": "行",
        "in": "関数内",
        "NameError": "名前エラー",
        "TypeError": "型エラー",
        "ValueError": "値エラー",
        "AttributeError": "属性エラー",
        "KeyError": "キーエラー",
        "IndexError": "インデックスエラー",
        "FileNotFoundError": "ファイル未発見エラー",
        "PermissionError": "権限エラー",
        "ImportError": "インポートエラー",
        "ModuleNotFoundError": "モジュール未発見エラー",
        "RuntimeError": "実行時エラー",
        "OSError": "OS エラー",
        "IOError": "入出力エラー",
        "ZeroDivisionError": "ゼロ除算エラー",
        "is not defined": "が定義されていません",
        "object has no attribute": "オブジェクトに属性がありません",
        "No such file or directory": "ファイルまたはディレクトリが存在しません",
        "Permission denied": "アクセスが拒否されました",
        "No module named": "モジュールが見つかりません",
    }

    @classmethod
    def translate_traceback(cls, tb_str: str) -> str:
        """スタックトレースを日本語化"""
        translated = tb_str

        for english, japanese in cls.TRANSLATIONS.items():
            translated = translated.replace(english, japanese)

        return translated

    @classmethod
    def get_exception_explanation(cls, exception: Exception) -> str:
        """例外の日本語説明を生成"""
        exc_type = type(exception).__name__
        exc_message = str(exception)

        explanations = {
            "NameError": f"変数または関数 '{exc_message.split("'")[1] if "'" in exc_message else 'unknown'}' が定義されていません。スペルミスや未定義の変数を確認してください。",
            "TypeError": f"型に関するエラーが発生しました: {exc_message}。引数の型や数を確認してください。",
            "ValueError": f"値に関するエラーが発生しました: {exc_message}。引数の値が適切な範囲内にあるか確認してください。",
            "AttributeError": f"属性エラーが発生しました: {exc_message}。オブジェクトに指定された属性が存在するか確認してください。",
            "KeyError": f"キーエラーが発生しました: {exc_message}。辞書に指定されたキーが存在するか確認してください。",
            "IndexError": f"インデックスエラーが発生しました: {exc_message}。リストやタプルのインデックスが範囲内にあるか確認してください。",
            "FileNotFoundError": f"ファイルが見つかりません: {exc_message}。ファイルパスが正しいか確認してください。",
            "ImportError": f"インポートエラーが発生しました: {exc_message}。モジュールが正しくインストールされているか確認してください。",
            "ModuleNotFoundError": f"モジュールが見つかりません: {exc_message}。必要なパッケージがインストールされているか確認してください。",
        }

        return explanations.get(exc_type, f"{exc_type}: {exc_message}")


class ErrorContext:
    """エラーコンテキスト情報クラス"""

    def __init__(self, exception: Exception, frame: Optional[inspect.FrameInfo] = None):
        self.exception = exception
        self.frame = frame
        self.timestamp = datetime.now()
        self.context_data = {}

    def collect_local_variables(self) -> Dict[str, Any]:
        """ローカル変数を収集（安全に）"""
        if not self.frame:
            return {}

        local_vars = {}
        try:
            for name, value in self.frame.frame.f_locals.items():
                # プライベート変数やシステム変数は除外
                if name.startswith("_"):
                    continue

                # 値を安全に文字列化
                try:
                    if isinstance(value, (str, int, float, bool, type(None))):
                        local_vars[name] = value
                    elif isinstance(value, (list, tuple, dict)):
                        # 大きなコレクションは制限
                        if len(str(value)) > 200:
                            local_vars[name] = (
                                f"{type(value).__name__}(size={len(value)})"
                            )
                        else:
                            local_vars[name] = value
                    else:
                        local_vars[name] = f"{type(value).__name__} object"
                except Exception:
                    local_vars[name] = "収集不可"

        except Exception as e:
            local_vars["_collection_error"] = str(e)

        return local_vars

    def collect_function_info(self) -> Dict[str, Any]:
        """関数情報を収集"""
        if not self.frame:
            return {}

        return {
            "function_name": self.frame.function,
            "filename": self.frame.filename,
            "line_number": self.frame.lineno,
            "code_context": self.frame.code_context,
        }

    def add_context(self, key: str, value: Any):
        """追加のコンテキスト情報を設定"""
        self.context_data[key] = value


class ErrorReporter:
    """構造化エラーレポートシステム"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.reports_dir = Path("logs/error_reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def capture_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """例外を捕捉して詳細レポートを生成"""

        # スタックトレース情報を取得
        tb = traceback.extract_tb(exception.__traceback__)

        # 最後のフレーム（エラー発生箇所）を取得
        last_frame = None
        if tb:
            last_tb = tb[-1]
            try:
                # フレーム情報を構築
                last_frame = inspect.FrameInfo(
                    frame=None,  # 実際のフレームオブジェクトは取得困難
                    filename=last_tb.filename,
                    lineno=last_tb.lineno,
                    function=last_tb.name,
                    code_context=[last_tb.line] if last_tb.line else None,
                    index=0,
                )
            except Exception:
                pass

        # エラーコンテキストを作成
        error_context = ErrorContext(exception, last_frame)
        if context:
            for key, value in context.items():
                error_context.add_context(key, value)

        # 詳細レポートを生成
        report = self._generate_detailed_report(exception, error_context, user_message)

        # レポートを保存
        report_file = self._save_report(report)

        # ログに記録
        self._log_error_report(report, report_file)

        return report

    def _generate_detailed_report(
        self,
        exception: Exception,
        error_context: ErrorContext,
        user_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """詳細エラーレポートを生成"""

        # 基本的な例外情報
        exception_info = {
            "type": type(exception).__name__,
            "message": str(exception),
            "japanese_explanation": StackTraceTranslator.get_exception_explanation(
                exception
            ),
        }

        # スタックトレース（日本語化）
        tb_str = traceback.format_exc()
        japanese_traceback = StackTraceTranslator.translate_traceback(tb_str)

        # システム情報
        system_info = SystemInfo.get_system_info()
        qt_info = SystemInfo.get_qt_info()
        dependencies_info = SystemInfo.get_dependencies_info()

        # 関数情報とローカル変数
        function_info = error_context.collect_function_info()
        local_variables = error_context.collect_local_variables()

        # 完全なレポート
        report = {
            "metadata": {
                "report_id": f"error_{int(error_context.timestamp.timestamp())}",
                "timestamp": error_context.timestamp.isoformat(),
                "reporter_version": "1.0.0",
            },
            "user_info": {
                "message": user_message,
                "context": error_context.context_data,
            },
            "exception": exception_info,
            "traceback": {
                "original": tb_str,
                "japanese": japanese_traceback,
            },
            "execution_context": {
                "function": function_info,
                "local_variables": local_variables,
            },
            "system_environment": {
                "system": system_info,
                "qt_framework": qt_info,
                "dependencies": dependencies_info,
            },
            "suggestions": self._generate_suggestions(exception, function_info),
        }

        return report

    def _generate_suggestions(
        self, exception: Exception, function_info: Dict[str, Any]
    ) -> List[str]:
        """エラーに基づく修正提案を生成"""
        suggestions = []
        exc_type = type(exception).__name__
        exc_message = str(exception)

        if exc_type == "ModuleNotFoundError":
            module_name = exc_message.split("'")[1] if "'" in exc_message else "unknown"
            suggestions.extend(
                [
                    f"モジュール '{module_name}' をインストールしてください: pip install {module_name}",
                    "仮想環境が正しく有効化されているか確認してください",
                    "requirements.txtに必要な依存関係が記載されているか確認してください",
                ]
            )

        elif exc_type == "FileNotFoundError":
            suggestions.extend(
                [
                    "ファイルパスが正しいか確認してください",
                    "ファイルが存在するか確認してください",
                    "相対パスではなく絶対パスを使用することを検討してください",
                    "ファイルの権限を確認してください",
                ]
            )

        elif exc_type == "AttributeError":
            suggestions.extend(
                [
                    "オブジェクトの型が期待されるものか確認してください",
                    "属性名のスペルミスがないか確認してください",
                    "オブジェクトが正しく初期化されているか確認してください",
                ]
            )

        elif exc_type in ["TypeError", "ValueError"]:
            suggestions.extend(
                [
                    "関数の引数の型と数を確認してください",
                    "変数の値が期待される範囲内にあるか確認してください",
                    "型変換が必要な場合は適切に行ってください",
                ]
            )

        # Qt関連のエラー
        if "Qt" in exc_message or "PySide" in exc_message or "PyQt" in exc_message:
            suggestions.extend(
                [
                    "Qtアプリケーションが正しく初期化されているか確認してください",
                    "UIスレッドから操作を実行しているか確認してください",
                    "Qtオブジェクトのライフサイクルを確認してください",
                ]
            )

        # 一般的な提案
        suggestions.extend(
            [
                "ログファイルで詳細な情報を確認してください",
                "デバッガーを使用してステップ実行を行ってください",
                "単体テストを作成して問題を再現してください",
            ]
        )

        return suggestions

    def _save_report(self, report: Dict[str, Any]) -> Path:
        """レポートをファイルに保存"""
        report_id = report["metadata"]["report_id"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_id}_{timestamp}.json"

        report_file = self.reports_dir / filename

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(
                f"エラーレポートの保存に失敗しました: {e}", LogCategory.ERROR
            )
            # フォールバック: 一時ファイルに保存
            fallback_file = Path(f"/tmp/{filename}")
            try:
                with open(fallback_file, "w", encoding="utf-8") as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                return fallback_file
            except Exception:
                pass

        return report_file

    def _log_error_report(self, report: Dict[str, Any], report_file: Path):
        """エラーレポートをログに記録"""
        exception_info = report["exception"]
        metadata = report["metadata"]

        log_context = LogContext(
            report_id=metadata["report_id"],
            report_file=str(report_file),
            exception_type=exception_info["type"],
        )

        self.logger.error(
            f"構造化エラーレポートを生成しました: {exception_info['type']} - {exception_info['message']}",
            LogCategory.ERROR,
            log_context,
        )

        # 日本語の説明もログに記録
        self.logger.info(
            f"エラー説明: {exception_info['japanese_explanation']}",
            LogCategory.ERROR,
            log_context,
        )

    def generate_summary_report(self, days: int = 7) -> Dict[str, Any]:
        """過去N日間のエラーサマリーレポートを生成"""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        error_files = []

        # エラーレポートファイルを収集
        for report_file in self.reports_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                if file_time >= cutoff_date:
                    error_files.append(report_file)
            except Exception:
                continue

        # 統計情報を収集
        error_types = {}
        total_errors = len(error_files)

        for report_file in error_files:
            try:
                with open(report_file, encoding="utf-8") as f:
                    report = json.load(f)
                    exc_type = report["exception"]["type"]
                    error_types[exc_type] = error_types.get(exc_type, 0) + 1
            except Exception:
                continue

        summary = {
            "period": f"過去{days}日間",
            "total_errors": total_errors,
            "error_types": error_types,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])
            if error_types
            else None,
            "report_files": [str(f) for f in error_files],
            "generated_at": datetime.now().isoformat(),
        }

        return summary


# 便利な関数とデコレータ
def capture_and_report_exceptions(
    user_message: Optional[str] = None, context: Optional[Dict[str, Any]] = None
):
    """例外を自動的に捕捉してレポートするデコレータ"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                reporter = ErrorReporter()
                reporter.capture_exception(e, context, user_message)
                raise  # 例外を再発生させる

        return wrapper

    return decorator


def report_exception(
    exception: Exception, user_message: Optional[str] = None, **context
) -> Dict[str, Any]:
    """例外を手動でレポート"""
    reporter = ErrorReporter()
    return reporter.capture_exception(exception, context, user_message)


def main():
    """メイン処理（テスト用）"""
    import argparse

    parser = argparse.ArgumentParser(description="エラーレポートシステム")
    parser.add_argument("--test", action="store_true", help="テスト例外を生成")
    parser.add_argument(
        "--summary", type=int, default=7, help="サマリーレポート生成（日数）"
    )

    args = parser.parse_args()

    reporter = ErrorReporter()

    if args.test:
        # テスト例外を生成
        try:
            # 意図的にエラーを発生させる
            undefined_variable = some_undefined_variable  # NameError
        except Exception as e:
            report = reporter.capture_exception(
                e,
                context={"test_mode": True, "user_action": "テスト実行"},
                user_message="これはテスト用の例外です",
            )
            print(f"テストレポートを生成しました: {report['metadata']['report_id']}")

    elif args.summary:
        summary = reporter.generate_summary_report(args.summary)
        print("=" * 50)
        print(f"エラーサマリーレポート ({summary['period']})")
        print("=" * 50)
        print(f"総エラー数: {summary['total_errors']}")
        print("エラータイプ別統計:")
        for error_type, count in summary["error_types"].items():
            print(f"  {error_type}: {count}回")

        if summary["most_common_error"]:
            error_type, count = summary["most_common_error"]
            print(f"最も多いエラー: {error_type} ({count}回)")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
