#!/usr/bin/env python3
"""
print文検出スクリプト

このスクリプトはPythonファイル内のprint文を検出し、
loggerの使用を推奨するメッセージを表示します。
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class PrintStatementVisitor(ast.NodeVisitor):
    """print文を検出するASTビジター"""

    def __init__(self):
        self.print_statements: List[Tuple[int, int, str]] = []

    def visit_Call(self, node: ast.Call) -> None:
        """関数呼び出しノードを訪問"""
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            # print文の位置と内容を記録
            line_no = node.lineno
            col_offset = node.col_offset

            # print文の引数を取得
            args = []
            for arg in node.args:
                if isinstance(arg, ast.Constant):
                    args.append(repr(arg.value))
                elif isinstance(arg, ast.Name):
                    args.append(arg.id)
                else:
                    args.append("...")

            print_content = f"print({', '.join(args)})"
            self.print_statements.append((line_no, col_offset, print_content))

        self.generic_visit(node)


def check_file_for_prints(file_path: Path) -> List[Tuple[int, int, str]]:
    """ファイル内のprint文をチェック"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # ASTを解析
        tree = ast.parse(content, filename=str(file_path))
        visitor = PrintStatementVisitor()
        visitor.visit(tree)

        return visitor.print_statements

    except SyntaxError as e:
        print(f"構文エラー: {file_path}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"ファイル読み込みエラー: {file_path}: {e}", file=sys.stderr)
        return []


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python check_print_statements.py <ファイル1> [ファイル2] ...")
        sys.exit(1)

    total_prints = 0
    files_with_prints = []

    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)

        if not file_path.exists():
            print(f"ファイルが見つかりません: {file_path}", file=sys.stderr)
            continue

        if not file_path.suffix == ".py":
            continue

        # テストファイルやスクリプトファイルは除外
        if (
            file_path.name.startswith("test_")
            or file_path.parent.name == "tests"
            or file_path.parent.name == "scripts"
        ):
            continue

        print_statements = check_file_for_prints(file_path)

        if print_statements:
            files_with_prints.append(file_path)
            total_prints += len(print_statements)

            print(f"\n⚠️  {file_path} でprint文が検出されました:")
            for line_no, col_offset, content in print_statements:
                print(f"  行 {line_no}:{col_offset} - {content}")

    if files_with_prints:
        print(
            f"\n❌ 合計 {total_prints} 個のprint文が {len(files_with_prints)} ファイルで検出されました。"
        )
        print("\n💡 推奨事項:")
        print("   print文の代わりにloggerを使用してください:")
        print("   ")
        print("   ❌ print('メッセージ')")
        print("   ✅ logger.info('メッセージ')")
        print("   ")
        print("   loggerの設定例:")
        print("   from qt_theme_studio.logger import get_logger")
        print("   logger = get_logger(__name__)")
        print("")

        sys.exit(1)
    else:
        print("✅ print文は検出されませんでした。")
        sys.exit(0)


if __name__ == "__main__":
    main()
