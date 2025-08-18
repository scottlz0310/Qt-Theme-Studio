#!/usr/bin/env python3
"""
ドキュメント更新チェッカー

新機能追加時の対応ドキュメント存在チェック、コード変更とドキュメント更新の関連性分析、
不足ドキュメントの自動検出と案内を提供します。
"""

import ast
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from qt_theme_studio.logger import LogCategory, LogContext, get_logger


class CodeAnalyzer:
    """コード分析器"""

    def __init__(self):
        """コード分析器を初期化"""
        self.logger = get_logger()

    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Pythonファイルを分析

        Args:
            file_path: 分析対象ファイル

        Returns:
            分析結果
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # 関数とクラスを抽出
            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "is_public": not node.name.startswith("_"),
                            "has_docstring": ast.get_docstring(node) is not None,
                            "decorators": [
                                d.id if hasattr(d, "id") else str(d)
                                for d in node.decorator_list
                            ],
                        }
                    )
                elif isinstance(node, ast.ClassDef):
                    classes.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "is_public": not node.name.startswith("_"),
                            "has_docstring": ast.get_docstring(node) is not None,
                            "methods": [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef)
                            ],
                        }
                    )

            return {
                "file_path": str(file_path),
                "functions": functions,
                "classes": classes,
                "public_functions": [f for f in functions if f["is_public"]],
                "public_classes": [c for c in classes if c["is_public"]],
            }

        except Exception as e:
            self.logger.error(
                f"Pythonファイル分析エラー: {file_path} - {e}",
                LogCategory.ERROR,
                LogContext(file_path=str(file_path), error=str(e)),
            )
            return {"file_path": str(file_path), "error": str(e)}


class GitChangeAnalyzer:
    """Git変更分析器"""

    def __init__(self, project_root: Path):
        """Git変更分析器を初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root
        self.logger = get_logger()

    def get_recent_changes(self, days: int = 7) -> Dict[str, Any]:
        """最近の変更を取得

        Args:
            days: 取得する日数

        Returns:
            変更情報
        """
        try:
            # 指定日数前からの変更を取得
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            cmd = [
                "git",
                "log",
                f"--since={since_date}",
                "--name-status",
                "--pretty=format:%H|%an|%ad|%s",
                "--date=iso",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode != 0:
                self.logger.error(
                    f"Git log取得エラー: {result.stderr}",
                    LogCategory.ERROR,
                    LogContext(command=" ".join(cmd), stderr=result.stderr),
                )
                return {"error": result.stderr}

            # 出力を解析
            changes = self._parse_git_log(result.stdout)

            return {
                "since_date": since_date,
                "total_commits": len(changes),
                "changes": changes,
            }

        except Exception as e:
            self.logger.error(
                f"Git変更分析エラー: {e}", LogCategory.ERROR, LogContext(error=str(e))
            )
            return {"error": str(e)}

    def _parse_git_log(self, git_output: str) -> List[Dict[str, Any]]:
        """Git logの出力を解析

        Args:
            git_output: Git logの出力

        Returns:
            解析された変更情報
        """
        changes = []
        current_commit = None

        for line in git_output.split("\n"):
            if "|" in line and not line.startswith(("A\t", "M\t", "D\t")):
                # コミット情報行
                parts = line.split("|")
                if len(parts) >= 4:
                    current_commit = {
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3],
                        "files": [],
                    }
                    changes.append(current_commit)
            elif current_commit and line.startswith(("A\t", "M\t", "D\t")):
                # ファイル変更行
                status, file_path = line.split("\t", 1)
                current_commit["files"].append({"status": status, "path": file_path})

        return changes


class DocumentationMapper:
    """ドキュメントマッピング管理"""

    def __init__(self, project_root: Path):
        """ドキュメントマッパーを初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root
        self.logger = get_logger()
        self.doc_patterns = self._load_documentation_patterns()

    def _load_documentation_patterns(self) -> Dict[str, List[str]]:
        """ドキュメントパターンを読み込み

        Returns:
            ドキュメントパターン辞書
        """
        return {
            "api_docs": ["docs/api/*.md", "docs/reference/*.md", "README.md"],
            "user_guides": [
                "docs/user_guide/*.md",
                "docs/tutorial/*.md",
                "docs/getting_started.md",
            ],
            "developer_docs": [
                "docs/development/*.md",
                "docs/contributing.md",
                "CONTRIBUTING.md",
            ],
            "changelog": ["CHANGELOG.md", "RELEASE_NOTES.md", "docs/changelog.md"],
        }

    def find_related_documentation(self, code_file: Path) -> List[Path]:
        """コードファイルに関連するドキュメントを検索

        Args:
            code_file: コードファイルパス

        Returns:
            関連ドキュメントファイルのリスト
        """
        related_docs = []

        # ファイル名ベースの関連付け
        file_stem = code_file.stem
        module_path = str(code_file.relative_to(self.project_root)).replace("/", ".")

        # 直接的な関連ドキュメント
        potential_docs = [
            self.project_root / "docs" / "api" / f"{file_stem}.md",
            self.project_root / "docs" / "reference" / f"{file_stem}.md",
            self.project_root / "docs" / f"{file_stem}.md",
        ]

        for doc_path in potential_docs:
            if doc_path.exists():
                related_docs.append(doc_path)

        # パターンベースの検索
        for doc_type, patterns in self.doc_patterns.items():
            for pattern in patterns:
                pattern_path = self.project_root / pattern.replace("*", file_stem)
                if pattern_path.exists():
                    related_docs.append(pattern_path)

        return related_docs

    def check_documentation_mentions(self, code_file: Path) -> Dict[str, Any]:
        """ドキュメント内でのコードファイル言及をチェック

        Args:
            code_file: コードファイルパス

        Returns:
            言及チェック結果
        """
        mentions = []
        file_name = code_file.name
        module_name = code_file.stem

        # 全ドキュメントファイルを検索
        doc_files = list(self.project_root.rglob("*.md"))

        for doc_file in doc_files:
            try:
                with open(doc_file, encoding="utf-8") as f:
                    content = f.read()

                # ファイル名やモジュール名の言及をチェック
                if file_name in content or module_name in content:
                    mentions.append(
                        {
                            "doc_file": str(doc_file),
                            "mentions_file_name": file_name in content,
                            "mentions_module_name": module_name in content,
                        }
                    )

            except Exception as e:
                self.logger.warning(
                    f"ドキュメントファイル読み込みエラー: {doc_file} - {e}",
                    LogCategory.ERROR,
                    LogContext(doc_file=str(doc_file), error=str(e)),
                )

        return {
            "code_file": str(code_file),
            "total_mentions": len(mentions),
            "mentions": mentions,
        }


class DocumentationGapAnalyzer:
    """ドキュメントギャップ分析器"""

    def __init__(self, project_root: Path):
        """ギャップ分析器を初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root
        self.logger = get_logger()
        self.code_analyzer = CodeAnalyzer()
        self.doc_mapper = DocumentationMapper(project_root)

    def analyze_documentation_gaps(self) -> Dict[str, Any]:
        """ドキュメントギャップを分析

        Returns:
            ギャップ分析結果
        """
        self.logger.info(
            "ドキュメントギャップ分析開始",
            LogCategory.GENERAL,
            LogContext(project_root=str(self.project_root)),
        )

        gaps = []

        # Pythonファイルを検索
        python_files = list(self.project_root.rglob("*.py"))

        # 除外パターン
        exclude_patterns = [
            "__pycache__",
            ".pytest_cache",
            "test_",
            "_test.py",
            "conftest.py",
        ]

        filtered_files = []
        for py_file in python_files:
            if not any(pattern in str(py_file) for pattern in exclude_patterns):
                filtered_files.append(py_file)

        for py_file in filtered_files:
            # コード分析
            code_analysis = self.code_analyzer.analyze_python_file(py_file)

            if "error" in code_analysis:
                continue

            # 関連ドキュメント検索
            related_docs = self.doc_mapper.find_related_documentation(py_file)

            # ドキュメント言及チェック
            mention_check = self.doc_mapper.check_documentation_mentions(py_file)

            # ギャップ判定
            file_gaps = self._identify_gaps(code_analysis, related_docs, mention_check)

            if file_gaps:
                gaps.append(
                    {
                        "file": str(py_file),
                        "code_analysis": code_analysis,
                        "related_docs": [str(d) for d in related_docs],
                        "mention_check": mention_check,
                        "gaps": file_gaps,
                    }
                )

        return {
            "project_root": str(self.project_root),
            "total_files_analyzed": len(filtered_files),
            "files_with_gaps": len(gaps),
            "gaps": gaps,
        }

    def _identify_gaps(
        self,
        code_analysis: Dict[str, Any],
        related_docs: List[Path],
        mention_check: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """ドキュメントギャップを特定

        Args:
            code_analysis: コード分析結果
            related_docs: 関連ドキュメント
            mention_check: 言及チェック結果

        Returns:
            特定されたギャップ
        """
        gaps = []

        # パブリック関数/クラスのドキュメント不足
        public_functions = code_analysis.get("public_functions", [])
        public_classes = code_analysis.get("public_classes", [])

        if public_functions or public_classes:
            if not related_docs:
                gaps.append(
                    {
                        "type": "missing_api_documentation",
                        "message": f"パブリックAPI（関数{len(public_functions)}個、クラス{len(public_classes)}個）のドキュメントが不足しています",
                        "severity": "warning",
                        "public_functions": len(public_functions),
                        "public_classes": len(public_classes),
                    }
                )

        # docstringの不足
        functions_without_docstring = [
            f for f in public_functions if not f["has_docstring"]
        ]
        classes_without_docstring = [
            c for c in public_classes if not c["has_docstring"]
        ]

        if functions_without_docstring:
            gaps.append(
                {
                    "type": "missing_function_docstrings",
                    "message": f"{len(functions_without_docstring)}個のパブリック関数にdocstringがありません",
                    "severity": "info",
                    "functions": [f["name"] for f in functions_without_docstring],
                }
            )

        if classes_without_docstring:
            gaps.append(
                {
                    "type": "missing_class_docstrings",
                    "message": f"{len(classes_without_docstring)}個のパブリッククラスにdocstringがありません",
                    "severity": "info",
                    "classes": [c["name"] for c in classes_without_docstring],
                }
            )

        # ドキュメント内での言及不足
        if mention_check["total_mentions"] == 0 and (
            public_functions or public_classes
        ):
            gaps.append(
                {
                    "type": "no_documentation_mentions",
                    "message": "このファイルはドキュメント内で言及されていません",
                    "severity": "info",
                }
            )

        return gaps


class DocumentationUpdateChecker:
    """統合ドキュメント更新チェッカー"""

    def __init__(self, project_root: Optional[Path] = None):
        """ドキュメント更新チェッカーを初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root or Path.cwd()
        self.logger = get_logger()
        self.git_analyzer = GitChangeAnalyzer(self.project_root)
        self.gap_analyzer = DocumentationGapAnalyzer(self.project_root)

    def check_recent_changes(self, days: int = 7) -> Dict[str, Any]:
        """最近の変更に対するドキュメント更新をチェック

        Args:
            days: チェック対象日数

        Returns:
            チェック結果
        """
        self.logger.info(
            f"最近{days}日間の変更に対するドキュメント更新チェック開始",
            LogCategory.GENERAL,
            LogContext(days=days, project_root=str(self.project_root)),
        )

        # 最近の変更を取得
        recent_changes = self.git_analyzer.get_recent_changes(days)

        if "error" in recent_changes:
            return recent_changes

        # 変更されたPythonファイルを抽出
        changed_python_files = set()
        changed_doc_files = set()

        for commit in recent_changes["changes"]:
            for file_info in commit["files"]:
                file_path = file_info["path"]
                if file_path.endswith(".py"):
                    changed_python_files.add(file_path)
                elif file_path.endswith(".md"):
                    changed_doc_files.add(file_path)

        # 変更されたPythonファイルに対応するドキュメント更新をチェック
        update_recommendations = []

        for py_file_path in changed_python_files:
            py_file = self.project_root / py_file_path
            if py_file.exists():
                # 関連ドキュメントを検索
                related_docs = self.gap_analyzer.doc_mapper.find_related_documentation(
                    py_file
                )

                # 関連ドキュメントが更新されているかチェック
                updated_related_docs = []
                for doc in related_docs:
                    doc_relative = str(doc.relative_to(self.project_root))
                    if doc_relative in changed_doc_files:
                        updated_related_docs.append(doc_relative)

                if related_docs and not updated_related_docs:
                    update_recommendations.append(
                        {
                            "python_file": py_file_path,
                            "related_docs": [
                                str(d.relative_to(self.project_root))
                                for d in related_docs
                            ],
                            "recommendation": "関連ドキュメントの更新を検討してください",
                            "severity": "info",
                        }
                    )
                elif not related_docs:
                    update_recommendations.append(
                        {
                            "python_file": py_file_path,
                            "related_docs": [],
                            "recommendation": "このファイル用のドキュメント作成を検討してください",
                            "severity": "warning",
                        }
                    )

        return {
            "check_period_days": days,
            "total_commits": recent_changes["total_commits"],
            "changed_python_files": len(changed_python_files),
            "changed_doc_files": len(changed_doc_files),
            "update_recommendations": update_recommendations,
            "recent_changes": recent_changes,
        }

    def generate_update_suggestions(self) -> Dict[str, Any]:
        """ドキュメント更新提案を生成

        Returns:
            更新提案
        """
        self.logger.info(
            "ドキュメント更新提案生成開始",
            LogCategory.GENERAL,
            LogContext(project_root=str(self.project_root)),
        )

        # ギャップ分析
        gap_analysis = self.gap_analyzer.analyze_documentation_gaps()

        # 提案を生成
        suggestions = []

        for gap_info in gap_analysis["gaps"]:
            file_path = gap_info["file"]
            gaps = gap_info["gaps"]

            for gap in gaps:
                if gap["type"] == "missing_api_documentation":
                    suggestions.append(
                        {
                            "type": "create_api_doc",
                            "file": file_path,
                            "priority": "high",
                            "description": f"{file_path}のAPIドキュメントを作成",
                            "suggested_path": f"docs/api/{Path(file_path).stem}.md",
                            "details": gap,
                        }
                    )
                elif gap["type"] == "missing_function_docstrings":
                    suggestions.append(
                        {
                            "type": "add_docstrings",
                            "file": file_path,
                            "priority": "medium",
                            "description": f"{file_path}の関数にdocstringを追加",
                            "functions": gap["functions"],
                            "details": gap,
                        }
                    )
                elif gap["type"] == "missing_class_docstrings":
                    suggestions.append(
                        {
                            "type": "add_docstrings",
                            "file": file_path,
                            "priority": "medium",
                            "description": f"{file_path}のクラスにdocstringを追加",
                            "classes": gap["classes"],
                            "details": gap,
                        }
                    )

        return {
            "total_suggestions": len(suggestions),
            "high_priority": len([s for s in suggestions if s["priority"] == "high"]),
            "medium_priority": len(
                [s for s in suggestions if s["priority"] == "medium"]
            ),
            "low_priority": len([s for s in suggestions if s["priority"] == "low"]),
            "suggestions": suggestions,
            "gap_analysis": gap_analysis,
        }

    def generate_update_report(
        self, check_result: Dict[str, Any], suggestions: Dict[str, Any]
    ) -> str:
        """ドキュメント更新レポートを生成

        Args:
            check_result: チェック結果
            suggestions: 更新提案

        Returns:
            更新レポート（Markdown形式）
        """
        report_lines = [
            "# ドキュメント更新チェックレポート",
            "",
            f"プロジェクト: {self.project_root}",
            f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 最近の変更概要",
            "",
            f"- チェック期間: 過去{check_result['check_period_days']}日間",
            f"- 総コミット数: {check_result['total_commits']}",
            f"- 変更されたPythonファイル: {check_result['changed_python_files']}個",
            f"- 変更されたドキュメントファイル: {check_result['changed_doc_files']}個",
            "",
            "## ドキュメント更新推奨事項",
            "",
        ]

        if check_result["update_recommendations"]:
            for rec in check_result["update_recommendations"]:
                severity_icon = {"warning": "⚠️", "info": "ℹ️"}.get(rec["severity"], "•")
                report_lines.append(f"### {severity_icon} {rec['python_file']}")
                report_lines.append(f"**推奨事項**: {rec['recommendation']}")

                if rec["related_docs"]:
                    report_lines.append("**関連ドキュメント**:")
                    for doc in rec["related_docs"]:
                        report_lines.append(f"- {doc}")

                report_lines.append("")
        else:
            report_lines.append("現在、ドキュメント更新の推奨事項はありません。")

        report_lines.extend(
            [
                "",
                "## 全体的な改善提案",
                "",
                f"- 高優先度: {suggestions['high_priority']}項目",
                f"- 中優先度: {suggestions['medium_priority']}項目",
                f"- 低優先度: {suggestions['low_priority']}項目",
                "",
            ]
        )

        # 高優先度の提案を詳細表示
        high_priority_suggestions = [
            s for s in suggestions["suggestions"] if s["priority"] == "high"
        ]
        if high_priority_suggestions:
            report_lines.append("### 高優先度の改善提案")
            report_lines.append("")

            for suggestion in high_priority_suggestions:
                report_lines.append(f"#### {suggestion['description']}")
                report_lines.append(f"**ファイル**: {suggestion['file']}")
                if "suggested_path" in suggestion:
                    report_lines.append(
                        f"**推奨作成先**: {suggestion['suggested_path']}"
                    )
                report_lines.append("")

        return "\n".join(report_lines)


def main():
    """メイン実行関数"""
    import argparse

    parser = argparse.ArgumentParser(description="ドキュメント更新チェッカー")
    parser.add_argument("--days", type=int, default=7, help="チェック対象日数")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="プロジェクトルートディレクトリ",
    )
    parser.add_argument("--output", type=Path, help="レポート出力ファイル")
    parser.add_argument(
        "--suggestions-only",
        action="store_true",
        help="提案のみ生成（Git変更チェックをスキップ）",
    )

    args = parser.parse_args()

    # ロガー設定
    logger = get_logger()

    try:
        checker = DocumentationUpdateChecker(args.project_root)

        if not args.suggestions_only:
            # 最近の変更チェック
            check_result = checker.check_recent_changes(args.days)

            if "error" in check_result:
                logger.error(f"変更チェックエラー: {check_result['error']}")
                return 1
        else:
            check_result = {
                "check_period_days": args.days,
                "total_commits": 0,
                "changed_python_files": 0,
                "changed_doc_files": 0,
                "update_recommendations": [],
            }

        # 更新提案生成
        suggestions = checker.generate_update_suggestions()

        # レポート生成
        report = checker.generate_update_report(check_result, suggestions)

        # 出力
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(report, encoding="utf-8")
            logger.info(f"ドキュメント更新レポート出力: {args.output}")
        else:
            # デフォルトの出力先
            report_path = args.project_root / "docs" / "doc_update_report.md"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report, encoding="utf-8")
            logger.info(f"ドキュメント更新レポート出力: {report_path}")

        # サマリー表示
        logger.info(
            f"ドキュメント更新チェック完了: "
            f"推奨事項{len(check_result.get('update_recommendations', []))}件、"
            f"改善提案{suggestions['total_suggestions']}件"
        )

    except Exception as e:
        logger.error(f"ドキュメント更新チェッカーエラー: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
