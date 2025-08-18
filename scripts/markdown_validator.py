#!/usr/bin/env python3
"""
Markdown検証システム

Markdown構文と内部リンクの自動検証、壊れたリンクの検出、
日本語文書の文字エンコーディング検証を提供します。
"""

import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError

from qt_theme_studio.logger import LogCategory, LogContext, get_logger


class MarkdownSyntaxValidator:
    """Markdown構文検証器"""

    def __init__(self):
        """構文検証器を初期化"""
        self.logger = get_logger()

    def validate_syntax(self, content: str, file_path: str) -> Dict[str, Any]:
        """Markdown構文を検証

        Args:
            content: Markdownコンテンツ
            file_path: ファイルパス

        Returns:
            検証結果
        """
        issues = []
        lines = content.split('\n')

        # ヘッダー構文チェック
        header_issues = self._check_headers(lines)
        issues.extend(header_issues)

        # リスト構文チェック
        list_issues = self._check_lists(lines)
        issues.extend(list_issues)

        # コードブロック構文チェック
        code_block_issues = self._check_code_blocks(lines)
        issues.extend(code_block_issues)

        # テーブル構文チェック
        table_issues = self._check_tables(lines)
        issues.extend(table_issues)

        # リンク構文チェック
        link_issues = self._check_link_syntax(lines)
        issues.extend(link_issues)

        return {
            "file_path": file_path,
            "total_issues": len(issues),
            "issues": issues,
            "is_valid": len(issues) == 0
        }

    def _check_headers(self, lines: List[str]) -> List[Dict[str, Any]]:
        """ヘッダー構文をチェック

        Args:
            lines: 行のリスト

        Returns:
            ヘッダー関連の問題リスト
        """
        issues = []
        header_levels = []

        for line_num, line in enumerate(lines, 1):
            # ATXスタイルヘッダー（# ## ###）
            atx_match = re.match(r'^(#{1,6})\s*(.+)', line)
            if atx_match:
                level = len(atx_match.group(1))
                header_levels.append(level)
                
                # ヘッダー後にスペースがない
                if not re.match(r'^#{1,6}\s+.+', line):
                    issues.append({
                        "line": line_num,
                        "type": "header_no_space",
                        "message": "ヘッダーマーク（#）の後にスペースが必要です",
                        "severity": "warning"
                    })

                # ヘッダーレベルの飛び越し
                if len(header_levels) > 1:
                    prev_level = header_levels[-2]
                    if level > prev_level + 1:
                        issues.append({
                            "line": line_num,
                            "type": "header_level_skip",
                            "message": f"ヘッダーレベルが飛び越されています（{prev_level} → {level}）",
                            "severity": "info"
                        })

            # Setextスタイルヘッダー（下線）
            elif line_num > 1 and re.match(r'^[=-]+$', line):
                prev_line = lines[line_num - 2]
                if not prev_line.strip():
                    issues.append({
                        "line": line_num,
                        "type": "setext_header_empty_line",
                        "message": "Setextスタイルヘッダーの上の行が空です",
                        "severity": "warning"
                    })

        return issues

    def _check_lists(self, lines: List[str]) -> List[Dict[str, Any]]:
        """リスト構文をチェック

        Args:
            lines: 行のリスト

        Returns:
            リスト関連の問題リスト
        """
        issues = []

        for line_num, line in enumerate(lines, 1):
            # 順序なしリスト
            unordered_match = re.match(r'^(\s*)[-*+]\s*(.+)', line)
            if unordered_match:
                indent = unordered_match.group(1)
                content = unordered_match.group(2)

                # インデントが4の倍数でない
                if len(indent) % 2 != 0:
                    issues.append({
                        "line": line_num,
                        "type": "list_indent_inconsistent",
                        "message": "リストのインデントが不正です（2の倍数である必要があります）",
                        "severity": "warning"
                    })

                # リストマーカー後にスペースがない
                if not re.match(r'^(\s*)[-*+]\s+.+', line):
                    issues.append({
                        "line": line_num,
                        "type": "list_no_space",
                        "message": "リストマーカーの後にスペースが必要です",
                        "severity": "warning"
                    })

            # 順序ありリスト
            ordered_match = re.match(r'^(\s*)(\d+)\.\s*(.+)', line)
            if ordered_match:
                indent = ordered_match.group(1)
                number = int(ordered_match.group(2))
                content = ordered_match.group(3)

                # リストマーカー後にスペースがない
                if not re.match(r'^(\s*)\d+\.\s+.+', line):
                    issues.append({
                        "line": line_num,
                        "type": "ordered_list_no_space",
                        "message": "順序ありリストマーカーの後にスペースが必要です",
                        "severity": "warning"
                    })

        return issues

    def _check_code_blocks(self, lines: List[str]) -> List[Dict[str, Any]]:
        """コードブロック構文をチェック

        Args:
            lines: 行のリスト

        Returns:
            コードブロック関連の問題リスト
        """
        issues = []
        in_fenced_block = False
        fenced_start_line = 0

        for line_num, line in enumerate(lines, 1):
            # フェンスコードブロック
            if re.match(r'^```', line):
                if not in_fenced_block:
                    in_fenced_block = True
                    fenced_start_line = line_num
                else:
                    in_fenced_block = False

            # インラインコード
            inline_code_matches = re.findall(r'`([^`]+)`', line)
            for match in inline_code_matches:
                if '`' in match:
                    issues.append({
                        "line": line_num,
                        "type": "inline_code_backtick",
                        "message": "インラインコード内にバッククォートが含まれています",
                        "severity": "error"
                    })

        # 閉じられていないフェンスコードブロック
        if in_fenced_block:
            issues.append({
                "line": fenced_start_line,
                "type": "unclosed_fenced_block",
                "message": "フェンスコードブロックが閉じられていません",
                "severity": "error"
            })

        return issues

    def _check_tables(self, lines: List[str]) -> List[Dict[str, Any]]:
        """テーブル構文をチェック

        Args:
            lines: 行のリスト

        Returns:
            テーブル関連の問題リスト
        """
        issues = []

        for line_num, line in enumerate(lines, 1):
            # テーブル行の検出
            if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                # セパレーター行のチェック
                if re.match(r'^\|[\s\-:|]+\|$', line):
                    # セパレーター行の形式チェック
                    separators = line.strip('|').split('|')
                    for sep in separators:
                        if not re.match(r'^[\s\-:]+$', sep.strip()):
                            issues.append({
                                "line": line_num,
                                "type": "table_separator_invalid",
                                "message": "テーブルセパレーターの形式が不正です",
                                "severity": "error"
                            })
                            break

                # 前後の行もテーブル行かチェック
                if line_num > 1:
                    prev_line = lines[line_num - 2]
                    if '|' in prev_line:
                        # カラム数の一致チェック
                        current_cols = len(line.split('|')) - 2  # 先頭と末尾の|を除く
                        prev_cols = len(prev_line.split('|')) - 2
                        if current_cols != prev_cols:
                            issues.append({
                                "line": line_num,
                                "type": "table_column_mismatch",
                                "message": f"テーブルのカラム数が一致しません（{prev_cols} vs {current_cols}）",
                                "severity": "warning"
                            })

        return issues

    def _check_link_syntax(self, lines: List[str]) -> List[Dict[str, Any]]:
        """リンク構文をチェック

        Args:
            lines: 行のリスト

        Returns:
            リンク構文関連の問題リスト
        """
        issues = []

        for line_num, line in enumerate(lines, 1):
            # インラインリンク [text](url)
            inline_links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', line)
            for text, url in inline_links:
                if not text.strip():
                    issues.append({
                        "line": line_num,
                        "type": "link_empty_text",
                        "message": "リンクテキストが空です",
                        "severity": "warning"
                    })

                if not url.strip():
                    issues.append({
                        "line": line_num,
                        "type": "link_empty_url",
                        "message": "リンクURLが空です",
                        "severity": "error"
                    })

            # 参照リンク [text][ref]
            ref_links = re.findall(r'\[([^\]]*)\]\[([^\]]*)\]', line)
            for text, ref in ref_links:
                if not text.strip():
                    issues.append({
                        "line": line_num,
                        "type": "ref_link_empty_text",
                        "message": "参照リンクテキストが空です",
                        "severity": "warning"
                    })

            # 画像リンク ![alt](url)
            image_links = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            for alt, url in image_links:
                if not alt.strip():
                    issues.append({
                        "line": line_num,
                        "type": "image_empty_alt",
                        "message": "画像のalt属性が空です",
                        "severity": "info"
                    })

        return issues


class LinkValidator:
    """リンク検証器"""

    def __init__(self, project_root: Path):
        """リンク検証器を初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root
        self.logger = get_logger()

    def validate_links(self, content: str, file_path: str) -> Dict[str, Any]:
        """リンクを検証

        Args:
            content: Markdownコンテンツ
            file_path: ファイルパス

        Returns:
            リンク検証結果
        """
        issues = []
        
        # 内部リンクの検証
        internal_issues = self._validate_internal_links(content, file_path)
        issues.extend(internal_issues)

        # 外部リンクの検証（オプション）
        external_issues = self._validate_external_links(content, file_path)
        issues.extend(external_issues)

        return {
            "file_path": file_path,
            "total_issues": len(issues),
            "issues": issues,
            "is_valid": len(issues) == 0
        }

    def _validate_internal_links(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """内部リンクを検証

        Args:
            content: Markdownコンテンツ
            file_path: ファイルパス

        Returns:
            内部リンク関連の問題リスト
        """
        issues = []
        lines = content.split('\n')
        current_file = Path(file_path)

        for line_num, line in enumerate(lines, 1):
            # 相対パスリンクを抽出
            links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', line)
            
            for text, url in links:
                # 外部URLをスキップ
                if url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                    continue

                # アンカーリンクをスキップ
                if url.startswith('#'):
                    continue

                # 相対パスの解決
                if url.startswith('./') or not url.startswith('/'):
                    target_path = current_file.parent / url
                else:
                    target_path = self.project_root / url.lstrip('/')

                # ファイルの存在チェック
                try:
                    resolved_path = target_path.resolve()
                    if not resolved_path.exists():
                        issues.append({
                            "line": line_num,
                            "type": "broken_internal_link",
                            "message": f"リンク先ファイルが存在しません: {url}",
                            "severity": "error",
                            "url": url,
                            "resolved_path": str(resolved_path)
                        })
                except Exception as e:
                    issues.append({
                        "line": line_num,
                        "type": "invalid_path",
                        "message": f"無効なパス: {url} ({e})",
                        "severity": "error",
                        "url": url
                    })

        return issues

    def _validate_external_links(self, content: str, file_path: str, check_external: bool = False) -> List[Dict[str, Any]]:
        """外部リンクを検証

        Args:
            content: Markdownコンテンツ
            file_path: ファイルパス
            check_external: 外部リンクをチェックするかどうか

        Returns:
            外部リンク関連の問題リスト
        """
        if not check_external:
            return []

        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # 外部URLを抽出
            links = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', line)
            
            for text, url in links:
                if url.startswith(('http://', 'https://')):
                    try:
                        # HTTPリクエストでリンクをチェック
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=10) as response:
                            if response.status >= 400:
                                issues.append({
                                    "line": line_num,
                                    "type": "broken_external_link",
                                    "message": f"外部リンクエラー: {url} (HTTP {response.status})",
                                    "severity": "warning",
                                    "url": url,
                                    "status_code": response.status
                                })
                    except (HTTPError, URLError) as e:
                        issues.append({
                            "line": line_num,
                            "type": "broken_external_link",
                            "message": f"外部リンクアクセスエラー: {url} ({e})",
                            "severity": "warning",
                            "url": url,
                            "error": str(e)
                        })
                    except Exception as e:
                        # タイムアウトなどの一般的なエラーは情報レベル
                        issues.append({
                            "line": line_num,
                            "type": "external_link_check_failed",
                            "message": f"外部リンクチェック失敗: {url} ({e})",
                            "severity": "info",
                            "url": url,
                            "error": str(e)
                        })

        return issues


class EncodingValidator:
    """文字エンコーディング検証器"""

    def __init__(self):
        """エンコーディング検証器を初期化"""
        self.logger = get_logger()

    def validate_encoding(self, file_path: Path) -> Dict[str, Any]:
        """ファイルの文字エンコーディングを検証

        Args:
            file_path: 検証対象ファイル

        Returns:
            エンコーディング検証結果
        """
        issues = []

        try:
            # UTF-8として読み込み試行
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # BOMの存在チェック
            if content.startswith('\ufeff'):
                issues.append({
                    "type": "utf8_bom_detected",
                    "message": "UTF-8 BOMが検出されました（推奨されません）",
                    "severity": "warning"
                })

            # 日本語文字の検証
            japanese_issues = self._validate_japanese_characters(content)
            issues.extend(japanese_issues)

            # 制御文字のチェック
            control_char_issues = self._check_control_characters(content)
            issues.extend(control_char_issues)

        except UnicodeDecodeError as e:
            issues.append({
                "type": "encoding_error",
                "message": f"UTF-8デコードエラー: {e}",
                "severity": "error"
            })

        return {
            "file_path": str(file_path),
            "encoding": "utf-8",
            "total_issues": len(issues),
            "issues": issues,
            "is_valid": len(issues) == 0
        }

    def _validate_japanese_characters(self, content: str) -> List[Dict[str, Any]]:
        """日本語文字を検証

        Args:
            content: ファイル内容

        Returns:
            日本語文字関連の問題リスト
        """
        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # 全角スペースのチェック
            if '　' in line:  # 全角スペース
                issues.append({
                    "line": line_num,
                    "type": "fullwidth_space",
                    "message": "全角スペースが含まれています",
                    "severity": "info"
                })

            # 半角カタカナのチェック
            halfwidth_katakana = re.search(r'[ｦ-ﾟ]', line)
            if halfwidth_katakana:
                issues.append({
                    "line": line_num,
                    "type": "halfwidth_katakana",
                    "message": "半角カタカナが含まれています（全角推奨）",
                    "severity": "info"
                })

            # 機種依存文字のチェック
            platform_dependent = re.search(r'[①-⑳㍉㌔㌢㍍㌘㌧㌃㌶㍑㍗㌍㌦㌣㌫㍊㌻㎜㎝㎞㎎㎏㏄㎡]', line)
            if platform_dependent:
                issues.append({
                    "line": line_num,
                    "type": "platform_dependent_char",
                    "message": "機種依存文字が含まれています",
                    "severity": "warning"
                })

        return issues

    def _check_control_characters(self, content: str) -> List[Dict[str, Any]]:
        """制御文字をチェック

        Args:
            content: ファイル内容

        Returns:
            制御文字関連の問題リスト
        """
        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # タブ文字のチェック
            if '\t' in line:
                issues.append({
                    "line": line_num,
                    "type": "tab_character",
                    "message": "タブ文字が含まれています（スペース推奨）",
                    "severity": "info"
                })

            # 行末の空白文字
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    "line": line_num,
                    "type": "trailing_whitespace",
                    "message": "行末に空白文字があります",
                    "severity": "info"
                })

            # 制御文字（印刷不可能文字）
            control_chars = re.findall(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', line)
            if control_chars:
                issues.append({
                    "line": line_num,
                    "type": "control_character",
                    "message": f"制御文字が含まれています: {[hex(ord(c)) for c in control_chars]}",
                    "severity": "warning"
                })

        return issues


class MarkdownValidator:
    """統合Markdown検証システム"""

    def __init__(self, project_root: Optional[Path] = None):
        """Markdown検証器を初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = project_root or Path.cwd()
        self.logger = get_logger()
        self.syntax_validator = MarkdownSyntaxValidator()
        self.link_validator = LinkValidator(self.project_root)
        self.encoding_validator = EncodingValidator()

    def validate_file(self, file_path: Path, check_external_links: bool = False) -> Dict[str, Any]:
        """Markdownファイルを検証

        Args:
            file_path: 検証対象ファイル
            check_external_links: 外部リンクをチェックするかどうか

        Returns:
            検証結果
        """
        self.logger.info(
            f"Markdownファイル検証開始: {file_path}",
            LogCategory.GENERAL,
            LogContext(file_path=str(file_path))
        )

        try:
            # ファイル存在チェック
            if not file_path.exists():
                return {
                    "file_path": str(file_path),
                    "error": "ファイルが存在しません",
                    "is_valid": False
                }

            # エンコーディング検証
            encoding_result = self.encoding_validator.validate_encoding(file_path)
            
            if not encoding_result["is_valid"]:
                return {
                    "file_path": str(file_path),
                    "encoding_result": encoding_result,
                    "error": "エンコーディングエラー",
                    "is_valid": False
                }

            # ファイル内容読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 構文検証
            syntax_result = self.syntax_validator.validate_syntax(content, str(file_path))

            # リンク検証
            link_result = self.link_validator.validate_links(content, str(file_path))

            # 結果統合
            all_issues = []
            all_issues.extend(encoding_result["issues"])
            all_issues.extend(syntax_result["issues"])
            all_issues.extend(link_result["issues"])

            result = {
                "file_path": str(file_path),
                "encoding_result": encoding_result,
                "syntax_result": syntax_result,
                "link_result": link_result,
                "total_issues": len(all_issues),
                "all_issues": all_issues,
                "is_valid": len(all_issues) == 0
            }

            self.logger.info(
                f"Markdownファイル検証完了: {file_path} ({len(all_issues)}個の問題)",
                LogCategory.GENERAL,
                LogContext(
                    file_path=str(file_path),
                    total_issues=len(all_issues),
                    is_valid=result["is_valid"]
                )
            )

            return result

        except Exception as e:
            self.logger.error(
                f"Markdownファイル検証エラー: {file_path} - {e}",
                LogCategory.ERROR,
                LogContext(file_path=str(file_path), error=str(e))
            )
            return {
                "file_path": str(file_path),
                "error": str(e),
                "is_valid": False
            }

    def validate_project(self, check_external_links: bool = False) -> Dict[str, Any]:
        """プロジェクト全体のMarkdownファイルを検証

        Args:
            check_external_links: 外部リンクをチェックするかどうか

        Returns:
            プロジェクト検証結果
        """
        self.logger.info(
            "プロジェクトMarkdown検証開始",
            LogCategory.GENERAL,
            LogContext(project_root=str(self.project_root))
        )

        # Markdownファイルを検索
        markdown_files = list(self.project_root.rglob("*.md"))
        
        # 除外パターン
        exclude_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            "_build",
            "site"
        ]

        filtered_files = []
        for md_file in markdown_files:
            if not any(pattern in str(md_file) for pattern in exclude_patterns):
                filtered_files.append(md_file)

        # 各ファイルを検証
        file_results = []
        total_issues = 0

        for md_file in filtered_files:
            result = self.validate_file(md_file, check_external_links)
            file_results.append(result)
            total_issues += result.get("total_issues", 0)

        # 統計情報
        valid_files = sum(1 for r in file_results if r.get("is_valid", False))
        invalid_files = len(file_results) - valid_files

        project_result = {
            "project_root": str(self.project_root),
            "total_files": len(file_results),
            "valid_files": valid_files,
            "invalid_files": invalid_files,
            "total_issues": total_issues,
            "file_results": file_results,
            "is_valid": invalid_files == 0
        }

        self.logger.info(
            f"プロジェクトMarkdown検証完了: {len(file_results)}ファイル、{total_issues}個の問題",
            LogCategory.GENERAL,
            LogContext(
                total_files=len(file_results),
                valid_files=valid_files,
                invalid_files=invalid_files,
                total_issues=total_issues
            )
        )

        return project_result

    def generate_validation_report(self, validation_result: Dict[str, Any]) -> str:
        """検証レポートを生成

        Args:
            validation_result: 検証結果

        Returns:
            検証レポート（Markdown形式）
        """
        report_lines = [
            "# Markdown検証レポート",
            "",
            f"プロジェクト: {validation_result['project_root']}",
            f"検証日時: {Path().cwd()}",
            "",
            "## 概要",
            "",
            f"- 総ファイル数: {validation_result['total_files']}",
            f"- 有効ファイル数: {validation_result['valid_files']}",
            f"- 問題のあるファイル数: {validation_result['invalid_files']}",
            f"- 総問題数: {validation_result['total_issues']}",
            "",
            "## ファイル別結果",
            ""
        ]

        for file_result in validation_result['file_results']:
            file_path = file_result['file_path']
            is_valid = file_result.get('is_valid', False)
            total_issues = file_result.get('total_issues', 0)

            status_icon = "✅" if is_valid else "❌"
            report_lines.append(f"### {status_icon} {file_path}")
            
            if total_issues > 0:
                report_lines.append(f"問題数: {total_issues}")
                report_lines.append("")

                # 各カテゴリの問題を表示
                for category in ['encoding_result', 'syntax_result', 'link_result']:
                    if category in file_result and file_result[category]['issues']:
                        category_name = {
                            'encoding_result': 'エンコーディング',
                            'syntax_result': '構文',
                            'link_result': 'リンク'
                        }[category]
                        
                        report_lines.append(f"#### {category_name}問題")
                        
                        for issue in file_result[category]['issues']:
                            severity_icon = {
                                "error": "❌",
                                "warning": "⚠️", 
                                "info": "ℹ️"
                            }.get(issue.get('severity', 'info'), "•")
                            
                            line_info = f" (行 {issue['line']})" if 'line' in issue else ""
                            report_lines.append(f"- {severity_icon} {issue['message']}{line_info}")
                        
                        report_lines.append("")
            else:
                report_lines.append("問題なし")
                report_lines.append("")

        return "\n".join(report_lines)


def main():
    """メイン実行関数"""
    import argparse

    parser = argparse.ArgumentParser(description="Markdown検証システム")
    parser.add_argument(
        "files",
        nargs="*",
        help="検証対象ファイル（指定しない場合はプロジェクト全体）"
    )
    parser.add_argument(
        "--check-external-links",
        action="store_true",
        help="外部リンクもチェックする"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="プロジェクトルートディレクトリ"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="レポート出力ファイル"
    )

    args = parser.parse_args()

    # ロガー設定
    logger = get_logger()
    
    try:
        validator = MarkdownValidator(args.project_root)

        if args.files:
            # 指定ファイルの検証
            for file_path in args.files:
                file_path = Path(file_path)
                result = validator.validate_file(file_path, args.check_external_links)
                
                if result["is_valid"]:
                    logger.info(f"✅ {file_path}: 問題なし")
                else:
                    logger.warning(f"❌ {file_path}: {result.get('total_issues', 0)}個の問題")
        else:
            # プロジェクト全体の検証
            result = validator.validate_project(args.check_external_links)
            
            # レポート生成
            report = validator.generate_validation_report(result)
            
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(report, encoding='utf-8')
                logger.info(f"検証レポート出力: {args.output}")
            else:
                # デフォルトの出力先
                report_path = args.project_root / "docs" / "markdown_validation_report.md"
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(report, encoding='utf-8')
                logger.info(f"検証レポート出力: {report_path}")

            # サマリー表示
            if result["is_valid"]:
                logger.info("✅ すべてのMarkdownファイルが有効です")
            else:
                logger.warning(
                    f"❌ {result['invalid_files']}個のファイルに問題があります "
                    f"（総問題数: {result['total_issues']}）"
                )

    except Exception as e:
        logger.error(f"Markdown検証システムエラー: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())