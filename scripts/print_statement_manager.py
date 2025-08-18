#!/usr/bin/env python3
"""
print文検出・置換統合システム

既存のreplace_prints.pyとcheck_print_statements.pyを統合し、
pre-commitフックとの統合とlogger使用の自動提案機能を提供します。
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

from qt_theme_studio.logger import LogCategory, LogContext, get_logger

logger = get_logger(__name__)


class PrintStatementAnalyzer(ast.NodeVisitor):
    """print文を詳細に分析するASTビジター"""

    def __init__(self):
        self.print_statements: List[Dict[str, Union[int, str]]] = []
        self.has_logger_import = False
        self.has_logger_instance = False
        self.logger_variable_name = None

    def visit_Import(self, node: ast.Import) -> None:
        """import文を検査してlogger関連のインポートを検出"""
        for alias in node.names:
            if "logger" in alias.name.lower():
                self.has_logger_import = True
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """from import文を検査してlogger関連のインポートを検出"""
        if node.module and "logger" in node.module:
            self.has_logger_import = True
            for alias in node.names:
                if alias.name in ["get_logger", "logger", "Logger"]:
                    self.has_logger_import = True
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """代入文を検査してloggerインスタンスを検出"""
        if isinstance(node.value, ast.Call):
            if (
                isinstance(node.value.func, ast.Name)
                and node.value.func.id == "get_logger"
            ):
                self.has_logger_instance = True
                if node.targets and isinstance(node.targets[0], ast.Name):
                    self.logger_variable_name = node.targets[0].id
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """関数呼び出しノードを訪問してprint文を検出"""
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            # print文の詳細情報を収集
            print_info = {
                "line": node.lineno,
                "column": node.col_offset,
                "args": [],
                "suggested_level": "info",
                "suggested_replacement": "",
            }

            # 引数を解析
            for arg in node.args:
                if isinstance(arg, ast.Constant):
                    arg_value = arg.value
                    print_info["args"].append(repr(arg_value))

                    # メッセージ内容からログレベルを推測
                    if isinstance(arg_value, str):
                        print_info["suggested_level"] = self._suggest_log_level(
                            arg_value
                        )
                elif isinstance(arg, ast.JoinedStr):  # f-string
                    print_info["args"].append("f-string")
                elif isinstance(arg, ast.Name):
                    print_info["args"].append(arg.id)
                else:
                    print_info["args"].append("複雑な式")

            # 置換提案を生成
            print_info["suggested_replacement"] = self._generate_replacement(print_info)
            self.print_statements.append(print_info)

        self.generic_visit(node)

    def _suggest_log_level(self, message: str) -> str:
        """メッセージ内容からログレベルを推測"""
        message_lower = message.lower()

        if any(
            keyword in message_lower for keyword in ["error", "エラー", "❌", "失敗"]
        ):
            return "error"
        if any(
            keyword in message_lower
            for keyword in ["warning", "warn", "警告", "⚠", "注意"]
        ):
            return "warning"
        if any(keyword in message_lower for keyword in ["debug", "デバッグ", "詳細"]):
            return "debug"
        if any(
            keyword in message_lower for keyword in ["success", "完了", "✓", "成功"]
        ):
            return "info"
        return "info"

    def _generate_replacement(self, print_info: Dict) -> str:
        """print文の置換提案を生成"""
        level = print_info["suggested_level"]
        logger_name = self.logger_variable_name or "logger"

        if len(print_info["args"]) == 1:
            arg = print_info["args"][0]
            if arg.startswith("f"):  # f-string
                return f"{logger_name}.{level}({arg})"
            return f"{logger_name}.{level}({arg})"
        args_str = ", ".join(print_info["args"])
        return f"{logger_name}.{level}({args_str})"


class PrintStatementManager:
    """print文管理システム"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.context = LogContext(component="print_statement_manager")

    def analyze_file(self, file_path: Path) -> Optional[PrintStatementAnalyzer]:
        """ファイルを分析してprint文を検出"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            analyzer = PrintStatementAnalyzer()
            analyzer.visit(tree)

            return analyzer

        except SyntaxError as e:
            self.logger.error(
                f"構文エラー: {file_path}: {e}", LogCategory.ERROR, self.context
            )
            return None
        except Exception as e:
            self.logger.error(
                f"ファイル分析エラー: {file_path}: {e}", LogCategory.ERROR, self.context
            )
            return None

    def check_prints_in_file(
        self, file_path: Path
    ) -> Dict[str, Union[int, List, bool]]:
        """ファイル内のprint文をチェック"""
        analyzer = self.analyze_file(file_path)
        if not analyzer:
            return {"error": True, "print_count": 0, "prints": []}

        return {
            "error": False,
            "print_count": len(analyzer.print_statements),
            "prints": analyzer.print_statements,
            "has_logger_import": analyzer.has_logger_import,
            "has_logger_instance": analyzer.has_logger_instance,
            "logger_variable": analyzer.logger_variable_name,
        }

    def replace_prints_in_file(
        self, file_path: Path, auto_fix: bool = False
    ) -> Dict[str, Union[int, bool, List]]:
        """ファイル内のprint文を置換"""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            analyzer = self.analyze_file(file_path)
            if not analyzer or not analyzer.print_statements:
                return {"replaced": 0, "success": True, "changes": []}

            content = original_content
            changes = []

            # loggerのインポートが必要な場合は追加
            if not analyzer.has_logger_import:
                import_line = "from qt_theme_studio.logger import get_logger\n"
                if "import" in content:
                    # 既存のimport文の後に追加
                    lines = content.split("\n")
                    import_index = -1
                    for i, line in enumerate(lines):
                        if line.strip().startswith(
                            "import "
                        ) or line.strip().startswith("from "):
                            import_index = i
                    if import_index >= 0:
                        lines.insert(import_index + 1, import_line.strip())
                        content = "\n".join(lines)
                        changes.append("loggerインポートを追加")
                else:
                    content = import_line + content
                    changes.append("loggerインポートを追加")

            # loggerインスタンスが必要な場合は追加
            if not analyzer.has_logger_instance:
                logger_line = "logger = get_logger(__name__)\n"
                # クラス定義の場合は__init__メソッド内に追加
                if "class " in content:
                    # クラス内のself.loggerとして追加する処理は複雑なので、
                    # ここではモジュールレベルのloggerを追加
                    lines = content.split("\n")
                    # import文の後に追加
                    for i, line in enumerate(lines):
                        if not (
                            line.strip().startswith("import ")
                            or line.strip().startswith("from ")
                            or line.strip().startswith("#")
                            or line.strip() == ""
                        ):
                            lines.insert(i, logger_line.strip())
                            content = "\n".join(lines)
                            changes.append("loggerインスタンスを追加")
                            break
                else:
                    content = content.replace(import_line, import_line + logger_line)
                    changes.append("loggerインスタンスを追加")

            # print文を置換
            replaced_count = 0
            for print_info in analyzer.print_statements:
                level = print_info["suggested_level"]
                logger_name = analyzer.logger_variable_name or "logger"

                # 元のprint文を検索して置換
                lines = content.split("\n")
                if print_info["line"] <= len(lines):
                    original_line = lines[print_info["line"] - 1]

                    # print文を置換
                    if "print(" in original_line:
                        # 簡単な置換パターン
                        new_line = re.sub(
                            r"print\(", f"{logger_name}.{level}(", original_line
                        )
                        lines[print_info["line"] - 1] = new_line
                        replaced_count += 1
                        changes.append(
                            f"行{print_info['line']}: print → {logger_name}.{level}"
                        )

            if replaced_count > 0:
                content = "\n".join(lines)

                if auto_fix:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    self.logger.info(
                        f"print文を置換しました: {file_path} ({replaced_count}箇所)",
                        LogCategory.GENERAL,
                        self.context,
                    )

            return {
                "replaced": replaced_count,
                "success": True,
                "changes": changes,
                "content": content if not auto_fix else None,
            }

        except Exception as e:
            self.logger.error(
                f"print文置換エラー: {file_path}: {e}", LogCategory.ERROR, self.context
            )
            return {"replaced": 0, "success": False, "changes": [], "error": str(e)}

    def scan_project(
        self, project_root: Path, exclude_patterns: Optional[List[str]] = None
    ) -> Dict:
        """プロジェクト全体をスキャン"""
        if exclude_patterns is None:
            exclude_patterns = [
                "venv",
                ".venv",
                "env",
                ".env",
                ".git",
                ".pytest_cache",
                "__pycache__",
                "node_modules",
                "build",
                "dist",
                "tests",
                "test_*",  # テストファイルは除外
            ]

        python_files = []
        for py_file in project_root.rglob("*.py"):
            # 除外パターンをチェック
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue
            python_files.append(py_file)

        results = {
            "total_files": len(python_files),
            "files_with_prints": [],
            "total_prints": 0,
            "files_without_logger": [],
            "summary": {},
        }

        for py_file in python_files:
            file_result = self.check_prints_in_file(py_file)

            if file_result["print_count"] > 0:
                results["files_with_prints"].append(
                    {
                        "file": py_file,
                        "print_count": file_result["print_count"],
                        "prints": file_result["prints"],
                        "has_logger": file_result.get("has_logger_import", False),
                    }
                )
                results["total_prints"] += file_result["print_count"]

            if not file_result.get("has_logger_import", False):
                results["files_without_logger"].append(py_file)

        # サマリー生成
        results["summary"] = {
            "files_scanned": len(python_files),
            "files_with_prints": len(results["files_with_prints"]),
            "total_print_statements": results["total_prints"],
            "files_without_logger": len(results["files_without_logger"]),
        }

        return results

    def generate_report(self, scan_results: Dict) -> str:
        """スキャン結果のレポートを生成"""
        report = []
        report.append("=" * 60)
        report.append("print文検出レポート")
        report.append("=" * 60)

        summary = scan_results["summary"]
        report.append(f"スキャンファイル数: {summary['files_scanned']}")
        report.append(f"print文検出ファイル数: {summary['files_with_prints']}")
        report.append(f"総print文数: {summary['total_print_statements']}")
        report.append(f"loggerなしファイル数: {summary['files_without_logger']}")
        report.append("")

        if scan_results["files_with_prints"]:
            report.append("🔍 print文が検出されたファイル:")
            report.append("-" * 40)

            for file_info in scan_results["files_with_prints"]:
                file_path = file_info["file"]
                print_count = file_info["print_count"]
                has_logger = file_info["has_logger"]

                report.append(f"📁 {file_path}")
                report.append(f"   print文数: {print_count}")
                report.append(f"   logger導入済み: {'✅' if has_logger else '❌'}")

                for print_info in file_info["prints"]:
                    line = print_info["line"]
                    level = print_info["suggested_level"]
                    replacement = print_info["suggested_replacement"]

                    report.append(f"   📍 行{line}: {level}レベル推奨")
                    report.append(f"      提案: {replacement}")

                report.append("")

        if scan_results["files_without_logger"]:
            report.append("⚠️  loggerが導入されていないファイル:")
            report.append("-" * 40)
            for file_path in scan_results["files_without_logger"]:
                report.append(f"   📁 {file_path}")
            report.append("")

        report.append("💡 推奨アクション:")
        report.append("1. print文をlogger呼び出しに置換")
        report.append("2. 必要に応じてloggerをインポート")
        report.append("3. 適切なログレベルを設定")
        report.append("")
        report.append("自動修正を実行するには:")
        report.append("python scripts/print_statement_manager.py --fix")

        return "\n".join(report)


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description="print文検出・置換システム")
    parser.add_argument("--scan", action="store_true", help="プロジェクトをスキャン")
    parser.add_argument("--fix", action="store_true", help="print文を自動修正")
    parser.add_argument("--file", type=str, help="特定ファイルを処理")
    parser.add_argument("--report", action="store_true", help="詳細レポートを生成")
    parser.add_argument("--pre-commit", action="store_true", help="pre-commitモード")

    args = parser.parse_args()

    manager = PrintStatementManager()
    project_root = Path(__file__).parent.parent

    if args.pre_commit:
        # pre-commitフック用の簡易チェック
        scan_results = manager.scan_project(project_root)
        if scan_results["total_prints"] > 0:
            print("❌ print文が検出されました。loggerを使用してください。")
            print(f"検出数: {scan_results['total_prints']}個")
            print("詳細: python scripts/print_statement_manager.py --scan --report")
            sys.exit(1)
        else:
            print("✅ print文は検出されませんでした。")
            sys.exit(0)

    elif args.file:
        # 特定ファイルの処理
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ ファイルが見つかりません: {file_path}")
            sys.exit(1)

        if args.fix:
            result = manager.replace_prints_in_file(file_path, auto_fix=True)
            if result["success"]:
                print(f"✅ 修正完了: {result['replaced']}箇所")
                for change in result["changes"]:
                    print(f"   {change}")
            else:
                print(f"❌ 修正失敗: {result.get('error', '不明なエラー')}")
        else:
            file_result = manager.check_prints_in_file(file_path)
            if file_result["print_count"] > 0:
                print(f"🔍 print文検出: {file_result['print_count']}個")
                for print_info in file_result["prints"]:
                    print(
                        f"   行{print_info['line']}: {print_info['suggested_replacement']}"
                    )
            else:
                print("✅ print文は検出されませんでした。")

    elif args.scan:
        # プロジェクト全体のスキャン
        scan_results = manager.scan_project(project_root)

        if args.report:
            report = manager.generate_report(scan_results)
            print(report)
        else:
            summary = scan_results["summary"]
            print(
                f"スキャン結果: {summary['files_with_prints']}/{summary['files_scanned']} ファイルでprint文検出"
            )
            print(f"総print文数: {summary['total_print_statements']}")

    elif args.fix:
        # プロジェクト全体の自動修正
        scan_results = manager.scan_project(project_root)
        fixed_files = 0
        total_replacements = 0

        for file_info in scan_results["files_with_prints"]:
            file_path = file_info["file"]
            result = manager.replace_prints_in_file(file_path, auto_fix=True)

            if result["success"] and result["replaced"] > 0:
                fixed_files += 1
                total_replacements += result["replaced"]
                print(f"✅ 修正: {file_path} ({result['replaced']}箇所)")

        print(f"\n修正完了: {fixed_files}ファイル, {total_replacements}箇所")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
