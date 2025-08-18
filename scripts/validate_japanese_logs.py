#!/usr/bin/env python3
"""
日本語ログメッセージ検証スクリプト

このスクリプトはPythonファイル内のログメッセージが
適切に日本語で記述されているかを検証します。
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Tuple


class LogMessageVisitor(ast.NodeVisitor):
    """ログメッセージを検出するASTビジター"""

    def __init__(self):
        self.log_calls: List[Tuple[int, str, str]] = []
        self.logger_methods = {
            "debug",
            "info",
            "warning",
            "warn",
            "error",
            "critical",
            "exception",
            "log",
        }

    def visit_Call(self, node: ast.Call) -> None:
        """関数呼び出しノードを訪問"""
        # logger.method() の形式をチェック
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in self.logger_methods
        ):
            line_no = node.lineno
            method_name = node.func.attr

            # 最初の引数（メッセージ）を取得
            if node.args:
                first_arg = node.args[0]
                message = self._extract_string_value(first_arg)
                if message:
                    self.log_calls.append((line_no, method_name, message))

        self.generic_visit(node)

    def _extract_string_value(self, node: ast.AST) -> str:
        """ASTノードから文字列値を抽出"""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Str):  # Python 3.7以前の互換性
            return node.s
        if isinstance(node, ast.JoinedStr):  # f-string
            # f-stringの場合は部分的にチェック
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant):
                    parts.append(str(value.value))
                elif isinstance(value, ast.Str):
                    parts.append(value.s)
            return "".join(parts)
        return ""


def has_japanese_characters(text: str) -> bool:
    """テキストに日本語文字が含まれているかチェック"""
    # ひらがな、カタカナ、漢字の範囲をチェック
    japanese_pattern = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]")
    return bool(japanese_pattern.search(text))


def is_technical_message(text: str) -> bool:
    """技術的なメッセージ（英語でも許可）かどうかチェック"""
    # 以下のパターンは英語でも許可
    technical_patterns = [
        r"^[A-Z_][A-Z0-9_]*$",  # 定数名
        r"^\w+\(\)$",  # 関数名
        r"^\w+\.\w+$",  # モジュール.属性
        r"^https?://",  # URL
        r"^\w+://\w+",  # プロトコル
        r"^\d+(\.\d+)*$",  # バージョン番号
        r"^[a-f0-9]{8,}$",  # ハッシュ値
        r"^\w+\s*=\s*\w+$",  # 変数代入
    ]

    for pattern in technical_patterns:
        if re.match(pattern, text.strip(), re.IGNORECASE):
            return True

    return False


def check_file_for_japanese_logs(file_path: Path) -> List[Tuple[int, str, str, bool]]:
    """ファイル内のログメッセージをチェック"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # ASTを解析
        tree = ast.parse(content, filename=str(file_path))
        visitor = LogMessageVisitor()
        visitor.visit(tree)

        results = []
        for line_no, method, message in visitor.log_calls:
            # 空のメッセージや技術的なメッセージはスキップ
            if not message.strip() or is_technical_message(message):
                continue

            has_japanese = has_japanese_characters(message)
            results.append((line_no, method, message, has_japanese))

        return results

    except SyntaxError as e:
        print(f"構文エラー: {file_path}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"ファイル読み込みエラー: {file_path}: {e}", file=sys.stderr)
        return []


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python validate_japanese_logs.py <ファイル1> [ファイル2] ...")
        sys.exit(1)

    total_non_japanese = 0
    files_with_issues = []

    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)

        if not file_path.exists():
            print(f"ファイルが見つかりません: {file_path}", file=sys.stderr)
            continue

        if not file_path.suffix == ".py":
            continue

        # テストファイルは除外（英語メッセージが多いため）
        if file_path.name.startswith("test_") or file_path.parent.name == "tests":
            continue

        log_messages = check_file_for_japanese_logs(file_path)

        non_japanese_messages = [
            (line_no, method, message)
            for line_no, method, message, has_japanese in log_messages
            if not has_japanese
        ]

        if non_japanese_messages:
            files_with_issues.append(file_path)
            total_non_japanese += len(non_japanese_messages)

            print(f"\n⚠️  {file_path} で日本語以外のログメッセージが検出されました:")
            for line_no, method, message in non_japanese_messages:
                print(f"  行 {line_no}: logger.{method}('{message}')")

    if files_with_issues:
        print(
            f"\n❌ 合計 {total_non_japanese} 個の非日本語ログメッセージが {len(files_with_issues)} ファイルで検出されました。"
        )
        print("\n💡 推奨事項:")
        print("   ログメッセージは日本語で記述してください:")
        print("   ")
        print("   ❌ logger.info('Loading theme')")
        print("   ✅ logger.info('テーマを読み込んでいます')")
        print("   ")
        print("   ❌ logger.error('File not found')")
        print("   ✅ logger.error('ファイルが見つかりません')")
        print("")

        sys.exit(1)
    else:
        print("✅ すべてのログメッセージが適切に日本語で記述されています。")
        sys.exit(0)


if __name__ == "__main__":
    main()
