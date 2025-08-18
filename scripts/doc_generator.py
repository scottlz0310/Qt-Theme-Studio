#!/usr/bin/env python3
"""
APIドキュメント自動生成システム

docstringからAPIドキュメントを自動生成し、品質チェック機能を提供します。
日本語docstringの適切な処理とSphinx/mkdocsでのドキュメント生成を自動化します。
"""

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from qt_theme_studio.logger import LogCategory, LogContext, get_logger


class DocstringQualityChecker:
    """docstring品質チェッカー"""

    def __init__(self):
        """品質チェッカーを初期化"""
        self.logger = get_logger()
        self.issues: List[Dict[str, Any]] = []

    def check_docstring_quality(
        self, docstring: str, function_name: str, file_path: str, line_number: int
    ) -> Dict[str, Any]:
        """docstringの品質をチェック

        Args:
            docstring: チェック対象のdocstring
            function_name: 関数名
            file_path: ファイルパス
            line_number: 行番号

        Returns:
            品質チェック結果
        """
        issues = []

        # 基本的な存在チェック
        if not docstring or not docstring.strip():
            issues.append(
                {
                    "type": "missing_docstring",
                    "message": "docstringが存在しません",
                    "severity": "error",
                }
            )
            return {
                "function_name": function_name,
                "file_path": file_path,
                "line_number": line_number,
                "issues": issues,
                "score": 0,
            }

        # 長さチェック
        if len(docstring.strip()) < 10:
            issues.append(
                {
                    "type": "too_short",
                    "message": "docstringが短すぎます（10文字未満）",
                    "severity": "warning",
                }
            )

        # 日本語文字の存在チェック
        japanese_pattern = re.compile(r"[ひらがなカタカナ漢字]")
        if not japanese_pattern.search(docstring):
            issues.append(
                {
                    "type": "no_japanese",
                    "message": "日本語の説明が含まれていません",
                    "severity": "warning",
                }
            )

        # Args/Returns セクションのチェック
        if "Args:" not in docstring and "引数:" not in docstring:
            if "(" in function_name or "def " in function_name:
                issues.append(
                    {
                        "type": "missing_args_section",
                        "message": "引数の説明セクションが不足しています",
                        "severity": "info",
                    }
                )

        if (
            "Returns:" not in docstring
            and "戻り値:" not in docstring
            and "return" in docstring.lower()
        ):
            issues.append(
                {
                    "type": "missing_returns_section",
                    "message": "戻り値の説明セクションが不足しています",
                    "severity": "info",
                }
            )

        # スコア計算
        score = 100
        for issue in issues:
            if issue["severity"] == "error":
                score -= 30
            elif issue["severity"] == "warning":
                score -= 15
            elif issue["severity"] == "info":
                score -= 5

        return {
            "function_name": function_name,
            "file_path": file_path,
            "line_number": line_number,
            "issues": issues,
            "score": max(0, score),
        }


class PythonDocstringExtractor:
    """Pythonファイルからdocstringを抽出"""

    def __init__(self):
        """docstring抽出器を初期化"""
        self.logger = get_logger()

    def extract_docstrings(self, file_path: Path) -> List[Dict[str, Any]]:
        """Pythonファイルからdocstringを抽出

        Args:
            file_path: 解析対象のPythonファイルパス

        Returns:
            抽出されたdocstring情報のリスト
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            docstrings = []

            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)
                ):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        docstrings.append(
                            {
                                "name": node.name,
                                "type": type(node).__name__,
                                "docstring": docstring,
                                "line_number": node.lineno,
                                "file_path": str(file_path),
                            }
                        )

            # モジュールレベルのdocstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                docstrings.append(
                    {
                        "name": "__module__",
                        "type": "Module",
                        "docstring": module_docstring,
                        "line_number": 1,
                        "file_path": str(file_path),
                    }
                )

            return docstrings

        except Exception as e:
            self.logger.error(
                f"docstring抽出エラー: {file_path}",
                LogCategory.ERROR,
                LogContext(file_path=str(file_path), error=str(e)),
            )
            return []


class SphinxDocGenerator:
    """Sphinx用ドキュメント生成器"""

    def __init__(self, project_root: Path):
        """Sphinx生成器を初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root
        self.docs_dir = project_root / "docs" / "api"
        self.logger = get_logger()

    def setup_sphinx_project(self) -> bool:
        """Sphinxプロジェクトをセットアップ

        Returns:
            セットアップ成功可否
        """
        try:
            # docs/apiディレクトリを作成
            self.docs_dir.mkdir(parents=True, exist_ok=True)

            # conf.pyを生成
            conf_content = self._generate_sphinx_config()
            (self.docs_dir / "conf.py").write_text(conf_content, encoding="utf-8")

            # index.rstを生成
            index_content = self._generate_index_rst()
            (self.docs_dir / "index.rst").write_text(index_content, encoding="utf-8")

            self.logger.info(
                "Sphinxプロジェクトセットアップ完了",
                LogCategory.GENERAL,
                LogContext(docs_dir=str(self.docs_dir)),
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Sphinxセットアップエラー: {e}",
                LogCategory.ERROR,
                LogContext(error=str(e)),
            )
            return False

    def _generate_sphinx_config(self) -> str:
        """Sphinx設定ファイルを生成

        Returns:
            conf.pyの内容
        """
        return '''# -*- coding: utf-8 -*-
"""
Qt-Theme-Studio API ドキュメント設定
"""

import os
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath('../../'))

# プロジェクト情報
project = 'Qt-Theme-Studio'
copyright = '2024, Qt-Theme-Studio Team'
author = 'Qt-Theme-Studio Team'
version = '0.1.0'
release = '0.1.0'

# 拡張機能
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
]

# 日本語対応
language = 'ja'

# HTMLテーマ
html_theme = 'sphinx_rtd_theme'

# 自動ドキュメント生成設定
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Napoleon設定（Google/NumPy形式のdocstring対応）
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False

# TODO拡張設定
todo_include_todos = True

# Intersphinx設定
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'pyside6': ('https://doc.qt.io/qtforpython/', None),
}
'''

    def _generate_index_rst(self) -> str:
        """メインインデックスファイルを生成

        Returns:
            index.rstの内容
        """
        return """Qt-Theme-Studio API ドキュメント
=====================================

Qt-Theme-Studio の API ドキュメントへようこそ。

.. toctree::
   :maxdepth: 2
   :caption: コンテンツ:

   modules

モジュール一覧
==============

.. automodule:: qt_theme_studio
   :members:

アダプター
----------

.. automodule:: qt_theme_studio.adapters.qt_adapter
   :members:

.. automodule:: qt_theme_studio.adapters.theme_adapter
   :members:

ジェネレーター
--------------

.. automodule:: qt_theme_studio.generators.theme_generator
   :members:

ビュー
------

.. automodule:: qt_theme_studio.views.main_window
   :members:

.. automodule:: qt_theme_studio.views.preview
   :members:

ログシステム
------------

.. automodule:: qt_theme_studio.logger
   :members:

インデックスと表
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

    def generate_module_docs(self) -> bool:
        """モジュール別ドキュメントを生成

        Returns:
            生成成功可否
        """
        try:
            # apidocを使用してモジュールドキュメントを自動生成
            cmd = [
                sys.executable,
                "-m",
                "sphinx.ext.apidoc",
                "-f",
                "-o",
                str(self.docs_dir),
                str(self.project_root / "qt_theme_studio"),
                "--separate",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                self.logger.info(
                    "モジュールドキュメント生成完了",
                    LogCategory.GENERAL,
                    LogContext(command=" ".join(cmd)),
                )
                return True
            self.logger.error(
                f"apidoc実行エラー: {result.stderr}",
                LogCategory.ERROR,
                LogContext(command=" ".join(cmd), stderr=result.stderr),
            )
            return False

        except Exception as e:
            self.logger.error(
                f"モジュールドキュメント生成エラー: {e}",
                LogCategory.ERROR,
                LogContext(error=str(e)),
            )
            return False

    def build_html_docs(self) -> bool:
        """HTMLドキュメントをビルド

        Returns:
            ビルド成功可否
        """
        try:
            build_dir = self.docs_dir / "_build" / "html"

            cmd = [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "html",
                str(self.docs_dir),
                str(build_dir),
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                self.logger.info(
                    f"HTMLドキュメントビルド完了: {build_dir}",
                    LogCategory.GENERAL,
                    LogContext(build_dir=str(build_dir)),
                )
                return True
            self.logger.error(
                f"Sphinxビルドエラー: {result.stderr}",
                LogCategory.ERROR,
                LogContext(command=" ".join(cmd), stderr=result.stderr),
            )
            return False

        except Exception as e:
            self.logger.error(
                f"HTMLドキュメントビルドエラー: {e}",
                LogCategory.ERROR,
                LogContext(error=str(e)),
            )
            return False


class MkDocsGenerator:
    """MkDocs用ドキュメント生成器"""

    def __init__(self, project_root: Path):
        """MkDocs生成器を初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.logger = get_logger()

    def setup_mkdocs_project(self) -> bool:
        """MkDocsプロジェクトをセットアップ

        Returns:
            セットアップ成功可否
        """
        try:
            # mkdocs.ymlを生成
            config_content = self._generate_mkdocs_config()
            (self.project_root / "mkdocs.yml").write_text(
                config_content, encoding="utf-8"
            )

            # docsディレクトリを作成
            self.docs_dir.mkdir(exist_ok=True)

            # index.mdを生成
            index_content = self._generate_index_md()
            (self.docs_dir / "index.md").write_text(index_content, encoding="utf-8")

            self.logger.info(
                "MkDocsプロジェクトセットアップ完了",
                LogCategory.GENERAL,
                LogContext(docs_dir=str(self.docs_dir)),
            )
            return True

        except Exception as e:
            self.logger.error(
                f"MkDocsセットアップエラー: {e}",
                LogCategory.ERROR,
                LogContext(error=str(e)),
            )
            return False

    def _generate_mkdocs_config(self) -> str:
        """MkDocs設定ファイルを生成

        Returns:
            mkdocs.ymlの内容
        """
        return """site_name: Qt-Theme-Studio API ドキュメント
site_description: Qt-Theme-Studio の API ドキュメント
site_author: Qt-Theme-Studio Team

theme:
  name: material
  language: ja
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.highlight
    - search.share
  palette:
    - scheme: default
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-7
        name: ダークモードに切り替え
    - scheme: slate
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-4
        name: ライトモードに切り替え

plugins:
  - search:
      lang: ja
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true
            show_root_heading: true

nav:
  - ホーム: index.md
  - API リファレンス:
    - qt_theme_studio: api/qt_theme_studio.md
    - アダプター:
      - qt_adapter: api/adapters/qt_adapter.md
      - theme_adapter: api/adapters/theme_adapter.md
    - ジェネレーター:
      - theme_generator: api/generators/theme_generator.md
    - ビュー:
      - main_window: api/views/main_window.md
      - preview: api/views/preview.md
    - ログシステム: api/logger.md

markdown_extensions:
  - admonition
  - codehilite
  - pymdownx.superfences
  - pymdownx.tabbed
  - toc:
      permalink: true
"""

    def _generate_index_md(self) -> str:
        """メインインデックスファイルを生成

        Returns:
            index.mdの内容
        """
        return """# Qt-Theme-Studio API ドキュメント

Qt-Theme-Studio の API ドキュメントへようこそ。

## 概要

Qt-Theme-Studio は、Qtアプリケーション向けの統合テーマエディターです。
直感的なビジュアルインターフェースでテーマの作成・編集・管理を行えます。

## 主要コンポーネント

### アダプター
- **QtAdapter**: Qt フレームワークとの統合
- **ThemeAdapter**: qt-theme-manager ライブラリとの統合

### ジェネレーター
- **ThemeGenerator**: テーマファイルの生成

### ビュー
- **MainWindow**: メインウィンドウ
- **PreviewWindow**: テーマプレビュー

### ログシステム
- **QtThemeStudioLogger**: 構造化ログシステム

## 使用方法

```python
from qt_theme_studio import QtThemeStudioMainWindow
from qt_theme_studio.logger import setup_logging

# ログ設定
setup_logging()

# メインウィンドウを起動
app = QApplication(sys.argv)
window = QtThemeStudioMainWindow()
window.show()
app.exec()
```

## API リファレンス

詳細なAPI情報については、左側のナビゲーションメニューから各モジュールのドキュメントをご覧ください。
"""

    def generate_api_docs(self) -> bool:
        """API ドキュメントページを生成

        Returns:
            生成成功可否
        """
        try:
            api_dir = self.docs_dir / "api"
            api_dir.mkdir(exist_ok=True)

            # メインモジュール
            self._generate_module_doc("qt_theme_studio", api_dir / "qt_theme_studio.md")

            # アダプター
            adapters_dir = api_dir / "adapters"
            adapters_dir.mkdir(exist_ok=True)
            self._generate_module_doc(
                "qt_theme_studio.adapters.qt_adapter", adapters_dir / "qt_adapter.md"
            )
            self._generate_module_doc(
                "qt_theme_studio.adapters.theme_adapter",
                adapters_dir / "theme_adapter.md",
            )

            # ジェネレーター
            generators_dir = api_dir / "generators"
            generators_dir.mkdir(exist_ok=True)
            self._generate_module_doc(
                "qt_theme_studio.generators.theme_generator",
                generators_dir / "theme_generator.md",
            )

            # ビュー
            views_dir = api_dir / "views"
            views_dir.mkdir(exist_ok=True)
            self._generate_module_doc(
                "qt_theme_studio.views.main_window", views_dir / "main_window.md"
            )
            self._generate_module_doc(
                "qt_theme_studio.views.preview", views_dir / "preview.md"
            )

            # ログシステム
            self._generate_module_doc("qt_theme_studio.logger", api_dir / "logger.md")

            self.logger.info(
                "API ドキュメント生成完了",
                LogCategory.GENERAL,
                LogContext(api_dir=str(api_dir)),
            )
            return True

        except Exception as e:
            self.logger.error(
                f"API ドキュメント生成エラー: {e}",
                LogCategory.ERROR,
                LogContext(error=str(e)),
            )
            return False

    def _generate_module_doc(self, module_name: str, output_path: Path):
        """モジュール用ドキュメントページを生成

        Args:
            module_name: モジュール名
            output_path: 出力ファイルパス
        """
        content = f"""# {module_name}

::: {module_name}
"""
        output_path.write_text(content, encoding="utf-8")

    def build_site(self) -> bool:
        """MkDocsサイトをビルド

        Returns:
            ビルド成功可否
        """
        try:
            cmd = [sys.executable, "-m", "mkdocs", "build"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                self.logger.info(
                    "MkDocsサイトビルド完了",
                    LogCategory.GENERAL,
                    LogContext(command=" ".join(cmd)),
                )
                return True
            self.logger.error(
                f"MkDocsビルドエラー: {result.stderr}",
                LogCategory.ERROR,
                LogContext(command=" ".join(cmd), stderr=result.stderr),
            )
            return False

        except Exception as e:
            self.logger.error(
                f"MkDocsサイトビルドエラー: {e}",
                LogCategory.ERROR,
                LogContext(error=str(e)),
            )
            return False


class DocumentationGenerator:
    """統合ドキュメント生成システム"""

    def __init__(self, project_root: Optional[Path] = None):
        """ドキュメント生成器を初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root or Path.cwd()
        self.logger = get_logger()
        self.quality_checker = DocstringQualityChecker()
        self.docstring_extractor = PythonDocstringExtractor()

    def analyze_project_docstrings(self) -> Dict[str, Any]:
        """プロジェクト全体のdocstringを分析

        Returns:
            分析結果
        """
        self.logger.info(
            "プロジェクトdocstring分析開始",
            LogCategory.GENERAL,
            LogContext(project_root=str(self.project_root)),
        )

        python_files = list(self.project_root.rglob("*.py"))
        all_docstrings = []
        quality_results = []

        for py_file in python_files:
            # テストファイルやキャッシュファイルをスキップ
            if any(
                skip in str(py_file)
                for skip in ["__pycache__", ".pytest_cache", "test_", "_test.py"]
            ):
                continue

            docstrings = self.docstring_extractor.extract_docstrings(py_file)
            all_docstrings.extend(docstrings)

            # 品質チェック
            for doc_info in docstrings:
                quality_result = self.quality_checker.check_docstring_quality(
                    doc_info["docstring"],
                    doc_info["name"],
                    doc_info["file_path"],
                    doc_info["line_number"],
                )
                quality_results.append(quality_result)

        # 統計情報を計算
        total_functions = len(
            [
                d
                for d in all_docstrings
                if d["type"] in ["FunctionDef", "AsyncFunctionDef"]
            ]
        )
        total_classes = len([d for d in all_docstrings if d["type"] == "ClassDef"])
        total_modules = len([d for d in all_docstrings if d["type"] == "Module"])

        average_score = (
            sum(r["score"] for r in quality_results) / len(quality_results)
            if quality_results
            else 0
        )

        analysis_result = {
            "total_docstrings": len(all_docstrings),
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_modules": total_modules,
            "average_quality_score": average_score,
            "quality_results": quality_results,
            "docstrings": all_docstrings,
        }

        self.logger.info(
            f"docstring分析完了: {len(all_docstrings)}個のdocstring、平均品質スコア: {average_score:.1f}",
            LogCategory.GENERAL,
            LogContext(
                total_docstrings=len(all_docstrings), average_score=average_score
            ),
        )

        return analysis_result

    def generate_quality_report(self, analysis_result: Dict[str, Any]) -> str:
        """品質レポートを生成

        Args:
            analysis_result: 分析結果

        Returns:
            品質レポート（Markdown形式）
        """
        report_lines = [
            "# Docstring 品質レポート",
            "",
            f"生成日時: {Path().cwd()}",
            "",
            "## 概要",
            "",
            f"- 総docstring数: {analysis_result['total_docstrings']}",
            f"- 関数: {analysis_result['total_functions']}",
            f"- クラス: {analysis_result['total_classes']}",
            f"- モジュール: {analysis_result['total_modules']}",
            f"- 平均品質スコア: {analysis_result['average_quality_score']:.1f}/100",
            "",
            "## 品質問題",
            "",
        ]

        # 問題のある項目をリストアップ
        problematic_items = [
            r for r in analysis_result["quality_results"] if r["issues"]
        ]

        if problematic_items:
            for item in problematic_items:
                report_lines.append(
                    f"### {item['function_name']} ({item['file_path']}:{item['line_number']})"
                )
                report_lines.append(f"スコア: {item['score']}/100")
                report_lines.append("")

                for issue in item["issues"]:
                    severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(
                        issue["severity"], "•"
                    )
                    report_lines.append(f"- {severity_icon} {issue['message']}")

                report_lines.append("")
        else:
            report_lines.append("品質問題は検出されませんでした。")

        return "\n".join(report_lines)

    def generate_documentation(self, doc_type: str = "sphinx") -> bool:
        """ドキュメントを生成

        Args:
            doc_type: ドキュメント生成タイプ ("sphinx" または "mkdocs")

        Returns:
            生成成功可否
        """
        self.logger.info(
            f"{doc_type}ドキュメント生成開始",
            LogCategory.GENERAL,
            LogContext(doc_type=doc_type, project_root=str(self.project_root)),
        )

        try:
            if doc_type.lower() == "sphinx":
                generator = SphinxDocGenerator(self.project_root)
                success = (
                    generator.setup_sphinx_project()
                    and generator.generate_module_docs()
                    and generator.build_html_docs()
                )
            elif doc_type.lower() == "mkdocs":
                generator = MkDocsGenerator(self.project_root)
                success = (
                    generator.setup_mkdocs_project()
                    and generator.generate_api_docs()
                    and generator.build_site()
                )
            else:
                self.logger.error(
                    f"サポートされていないドキュメントタイプ: {doc_type}",
                    LogCategory.ERROR,
                    LogContext(doc_type=doc_type),
                )
                return False

            if success:
                self.logger.info(
                    f"{doc_type}ドキュメント生成完了",
                    LogCategory.GENERAL,
                    LogContext(doc_type=doc_type),
                )
            else:
                self.logger.error(
                    f"{doc_type}ドキュメント生成失敗",
                    LogCategory.ERROR,
                    LogContext(doc_type=doc_type),
                )

            return success

        except Exception as e:
            self.logger.error(
                f"ドキュメント生成エラー: {e}",
                LogCategory.ERROR,
                LogContext(doc_type=doc_type, error=str(e)),
            )
            return False


def main():
    """メイン実行関数"""
    import argparse

    parser = argparse.ArgumentParser(description="APIドキュメント自動生成システム")
    parser.add_argument(
        "--type",
        choices=["sphinx", "mkdocs"],
        default="sphinx",
        help="ドキュメント生成タイプ",
    )
    parser.add_argument(
        "--analyze-only", action="store_true", help="docstring分析のみ実行"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="プロジェクトルートディレクトリ",
    )

    args = parser.parse_args()

    # ロガー設定
    logger = get_logger()

    try:
        generator = DocumentationGenerator(args.project_root)

        # docstring分析
        analysis_result = generator.analyze_project_docstrings()

        # 品質レポート生成
        quality_report = generator.generate_quality_report(analysis_result)
        report_path = args.project_root / "docs" / "docstring_quality_report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(quality_report, encoding="utf-8")

        logger.info(
            f"品質レポート生成完了: {report_path}",
            LogCategory.GENERAL,
            LogContext(report_path=str(report_path)),
        )

        # 分析のみの場合はここで終了
        if args.analyze_only:
            return

        # ドキュメント生成
        success = generator.generate_documentation(args.type)

        if success:
            logger.info(
                "ドキュメント生成処理完了",
                LogCategory.GENERAL,
                LogContext(doc_type=args.type),
            )
        else:
            logger.error(
                "ドキュメント生成処理失敗",
                LogCategory.ERROR,
                LogContext(doc_type=args.type),
            )
            sys.exit(1)

    except Exception as e:
        logger.error(
            f"ドキュメント生成システムエラー: {e}",
            LogCategory.ERROR,
            LogContext(error=str(e)),
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
