"""
Qt-Theme-Studio コマンドラインインターフェース

このモジュールは、CI/CD環境での自動テストと品質検証を
サポートするコマンドラインインターフェースを提供します。
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging
import os

from .services.quality_service import QualityService
from .services.test_api import HeadlessTestRunner
from .services.theme_service import ThemeService


class CLIError(Exception):
    """CLI例外"""


class ThemeStudioCLI:
    """Qt-Theme-Studio コマンドラインインターフェース"""

    def __init__(self):
        """CLIを初期化する"""
        self.quality_service = QualityService()
        self.test_runner = HeadlessTestRunner()
        self.theme_service = ThemeService()

        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def create_parser(self) -> argparse.ArgumentParser:
        """コマンドライン引数パーサーを作成する

        Returns:
            argparse.ArgumentParser: 引数パーサー
        """
        parser = argparse.ArgumentParser(
            prog="qt-theme-studio",
            description="Qt-Theme-Studio コマンドラインツール",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用例:
  # テーマの品質チェック
  qt-theme-studio quality-check theme.json

  # 自動テストスイート実行
  qt-theme-studio test theme.json

  # CI/CD用レポート生成
  qt-theme-studio ci-report theme.json --output report.json

  # テーマ検証のみ
  qt-theme-studio validate theme.json --wcag-level AAA

  # ヘッドレスモードでのテーマエクスポート
  qt-theme-studio export theme.json --format qss --output theme.qss
            """,
        )

        # 共通オプション
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="詳細ログを出力する"
        )

        parser.add_argument(
            "--quiet", "-q", action="store_true", help="エラー以外のログを抑制する"
        )

        # サブコマンド
        subparsers = parser.add_subparsers(
            dest="command", help="利用可能なコマンド", metavar="COMMAND"
        )

        # quality-check コマンド
        quality_parser = subparsers.add_parser(
            "quality-check", help="テーマの品質チェックを実行する"
        )
        quality_parser.add_argument("theme_file", help="テーマファイルパス")
        quality_parser.add_argument("--output", "-o", help="レポート出力ファイルパス")
        quality_parser.add_argument(
            "--threshold",
            type=float,
            default=70.0,
            help="品質スコア閾値（デフォルト: 70.0）",
        )

        # test コマンド
        test_parser = subparsers.add_parser("test", help="自動テストスイートを実行する")
        test_parser.add_argument("theme_file", help="テーマファイルパス")
        test_parser.add_argument("--output", "-o", help="テスト結果出力ファイルパス")
        test_parser.add_argument(
            "--iterations",
            type=int,
            default=5,
            help="パフォーマンステストの反復回数（デフォルト: 5）",
        )

        # ci-report コマンド
        ci_parser = subparsers.add_parser(
            "ci-report", help="CI/CD用統合レポートを生成する"
        )
        ci_parser.add_argument("theme_file", help="テーマファイルパス")
        ci_parser.add_argument(
            "--output", "-o", required=True, help="レポート出力ファイルパス"
        )
        ci_parser.add_argument(
            "--quality-threshold",
            type=float,
            default=70.0,
            help="品質スコア閾値（デフォルト: 70.0）",
        )
        ci_parser.add_argument(
            "--test-threshold",
            type=float,
            default=80.0,
            help="テスト成功率閾値（デフォルト: 80.0）",
        )

        # validate コマンド
        validate_parser = subparsers.add_parser(
            "validate", help="テーマ検証のみを実行する"
        )
        validate_parser.add_argument("theme_file", help="テーマファイルパス")
        validate_parser.add_argument(
            "--wcag-level",
            choices=["AA", "AAA"],
            default="AA",
            help="WCAGレベル（デフォルト: AA）",
        )
        validate_parser.add_argument("--output", "-o", help="検証結果出力ファイルパス")

        # export コマンド
        export_parser = subparsers.add_parser(
            "export", help="ヘッドレスモードでテーマをエクスポートする"
        )
        export_parser.add_argument("theme_file", help="テーマファイルパス")
        export_parser.add_argument(
            "--format",
            choices=["json", "qss", "css"],
            required=True,
            help="エクスポート形式",
        )
        export_parser.add_argument(
            "--output", "-o", required=True, help="出力ファイルパス"
        )

        return parser

    def setup_logging(self, verbose: bool, quiet: bool) -> None:
        """ログレベルを設定する

        Args:
            verbose (bool): 詳細ログを有効にするか
            quiet (bool): 静寂モードを有効にするか
        """
        if quiet:
            logging.getLogger().setLevel(logging.ERROR)
        elif verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)

    def load_theme_file(self, theme_file: str) -> Dict[str, Any]:
        """テーマファイルを読み込む

        Args:
            theme_file (str): テーマファイルパス

        Returns:
            Dict[str, Any]: テーマデータ

        Raises:
            CLIError: ファイル読み込みエラー
        """
        if not os.path.exists(theme_file):
            raise CLIError("テーマファイルが存在しません: {theme_file}")

        try:
            return self.theme_service.load_theme_from_file(theme_file)
        except Exception:
            raise CLIError("テーマファイル読み込みエラー: {str()}")

    def cmd_quality_check(self, args: argparse.Namespace) -> int:
        """品質チェックコマンドを実行する

        Args:
            args (argparse.Namespace): コマンドライン引数

        Returns:
            int: 終了コード
        """
        try:
            print("テーマ品質チェックを開始します...")
            print("テーマファイル: {args.theme_file}")
            print("品質閾値: {args.threshold}")
            print()

            # テーマ読み込み
            theme_data = self.load_theme_file(args.theme_file)
            theme_name = theme_data.get("name", Path(args.theme_file).stem)

            # 品質チェック実行
            report = self.quality_service.run_comprehensive_quality_check(
                theme_data, theme_name
            )

            # 結果表示
            print("=" * 60)
            print("品質チェック結果")
            print("=" * 60)
            print("テーマ名: {report.theme_name}")
            print("総合スコア: {report.overall_score:.1f}/100")
            print(
                "品質判定: {'合格' if report.overall_score >= args.threshold else '不合格'}"
            )
            print()

            # 詳細結果
            if report.quality_checks:
                print("詳細チェック結果:")
                for check_name, check_data in report.quality_checks.items():
                    "✓" if check_data["passed"] else "✗"
                    print("  {status} {check_name}: {check_data['score']:.1f}/100")
                    if check_data["details"]:
                        print("    {check_data['details']}")
                print()

            # 推奨事項
            if report.recommendations:
                print("推奨事項 ({len(report.recommendations)}):")
                for i, recommendation in enumerate(report.recommendations, 1):
                    print("  {i}. {recommendation}")
                print()

            # レポート出力
            if args.output:
                report.save_to_file(args.output)
                print("詳細レポートを {args.output} に出力しました")

            # 終了コード決定
            return 0 if report.overall_score >= args.threshold else 1

        except CLIError:
            print("エラー: {str()}", file=sys.stderr)
            return 1
        except Exception:
            print("予期しないエラーが発生しました: {str()}", file=sys.stderr)
            return 1

    def cmd_test(self, args: argparse.Namespace) -> int:
        """テストコマンドを実行する

        Args:
            args (argparse.Namespace): コマンドライン引数

        Returns:
            int: 終了コード
        """
        try:
            print("自動テストスイートを開始します...")
            print("テーマファイル: {args.theme_file}")
            print("パフォーマンステスト反復回数: {args.iterations}")
            print()

            # 包括的テストスイート実行
            result = self.test_runner.run_comprehensive_test_suite(
                theme_path=args.theme_file
            )

            # 結果表示
            print("=" * 60)
            print("テスト結果サマリー")
            print("=" * 60)
            print("実行テスト数: {result['tests_run']}")
            print("成功テスト数: {result['tests_passed']}")
            print("失敗テスト数: {result['tests_run'] - result['tests_passed']}")
            print("成功率: {result['summary'].get('success_rate', 0.0):.1f}%")
            print("実行時間: {result['total_time']:.3f}秒")
            print()

            # 個別テスト結果
            print("個別テスト結果:")
            for test_result in result["individual_results"]:
                "✓" if test_result["success"] else "✗"
                print("  {status} {test_result['test_name']}")
                if not test_result["success"] and test_result.get("error_message"):
                    print("    エラー: {test_result['error_message']}")
            print()

            # 結果ファイル出力
            output_file = args.output or "test_results_{int(result['start_time'])}.json"
            self.test_runner.export_test_results(output_file)
            print("詳細結果を {output_file} に出力しました")

            # 終了コード決定
            return 0 if result["success"] else 1

        except CLIError:
            print("エラー: {str()}", file=sys.stderr)
            return 1
        except Exception:
            print("予期しないエラーが発生しました: {str()}", file=sys.stderr)
            return 1

    def cmd_ci_report(self, args: argparse.Namespace) -> int:
        """CI/CDレポートコマンドを実行する

        Args:
            args (argparse.Namespace): コマンドライン引数

        Returns:
            int: 終了コード
        """
        try:
            print("CI/CD統合レポートを生成します...")
            print("テーマファイル: {args.theme_file}")
            print("品質閾値: {args.quality_threshold}")
            print("テスト成功率閾値: {args.test_threshold}")
            print()

            # テーマ読み込み
            theme_data = self.load_theme_file(args.theme_file)

            # CI/CDレポート生成
            report_path = self.quality_service.generate_ci_report(
                theme_data, args.output
            )

            # レポート読み込みと結果表示
            with open(report_path, "r", encoding="utf-8") as f:
                ci_report = json.load(f)

            ci_summary = ci_report["ci_summary"]

            print("=" * 60)
            print("CI/CD統合レポート")
            print("=" * 60)
            print("総合判定: {ci_summary['overall_status']}")
            print("品質スコア: {ci_summary['quality_score']:.1f}/100")
            print("テスト成功率: {ci_summary['test_success_rate']:.1f}%")
            print()

            if ci_summary["recommendations"]:
                print("推奨事項 ({len(ci_summary['recommendations'])}):")
                for i, recommendation in enumerate(ci_summary["recommendations"], 1):
                    print("  {i}. {recommendation}")
                print()

            print("詳細レポートを {args.output} に出力しました")

            # 終了コード決定
            return 0 if ci_summary["overall_status"] == "PASS" else 1

        except CLIError:
            print("エラー: {str()}", file=sys.stderr)
            return 1
        except Exception:
            print("予期しないエラーが発生しました: {str()}", file=sys.stderr)
            return 1

    def cmd_validate(self, args: argparse.Namespace) -> int:
        """検証コマンドを実行する

        Args:
            args (argparse.Namespace): コマンドライン引数

        Returns:
            int: 終了コード
        """
        try:
            print("テーマ検証を開始します...")
            print("テーマファイル: {args.theme_file}")
            print("WCAGレベル: {args.wcag_level}")
            print()

            # テーマ読み込み
            theme_data = self.load_theme_file(args.theme_file)

            # 構造検証
            structure_errors = (
                self.quality_service.validation_service.validate_theme_structure(
                    theme_data
                )
            )

            # アクセシビリティ検証
            accessibility_report = (
                self.quality_service.validation_service.validate_wcag_compliance(
                    theme_data, args.wcag_level
                )
            )

            # 結果表示
            print("=" * 60)
            print("検証結果")
            print("=" * 60)

            # 構造検証結果
            if structure_errors:
                print("構造エラー ({len(structure_errors)}):")
                for error in structure_errors:
                    print("  ✗ {error}")
            else:
                print("✓ 構造検証: 正常")
            print()

            # アクセシビリティ検証結果
            print("アクセシビリティ検証 (WCAG {args.wcag_level}):")
            print("  スコア: {accessibility_report.score:.1f}%")
            print(
                "  準拠状況: {'準拠' if accessibility_report.is_compliant() else '非準拠'}"
            )

            if accessibility_report.violations:
                print("  違反 ({len(accessibility_report.violations)}):")
                for violation in accessibility_report.violations:
                    severity_symbol = "✗" if violation["severity"] == "error" else "⚠"
                    print(f"    {severity_symbol} {violation['description']}")
            print()

            # 結果ファイル出力
            if args.output:
                validation_result = {
                    "structure_errors": structure_errors,
                    "accessibility_report": accessibility_report.to_dict(),
                    "overall_valid": len(structure_errors) == 0
                    and accessibility_report.is_compliant(),
                }

                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(validation_result, f, ensure_ascii=False, indent=2)

                print("検証結果を {args.output} に出力しました")

            # 終了コード決定
            is_valid = (
                len(structure_errors) == 0 and accessibility_report.is_compliant()
            )
            return 0 if is_valid else 1

        except CLIError:
            print("エラー: {str()}", file=sys.stderr)
            return 1
        except Exception:
            print("予期しないエラーが発生しました: {str()}", file=sys.stderr)
            return 1

    def cmd_export(self, args: argparse.Namespace) -> int:
        """エクスポートコマンドを実行する

        Args:
            args (argparse.Namespace): コマンドライン引数

        Returns:
            int: 終了コード
        """
        try:
            print("ヘッドレスエクスポートを開始します...")
            print("テーマファイル: {args.theme_file}")
            print("エクスポート形式: {args.format}")
            print("出力ファイル: {args.output}")
            print()

            # テーマ読み込み
            theme_data = self.load_theme_file(args.theme_file)

            # エクスポート実行
            export_result = self.test_runner.run_theme_export_test(
                theme_data, [args.format]
            )

            if export_result["success"]:
                format_result = export_result["export_results"][args.format]
                if format_result["success"]:
                    # エクスポートデータを取得して保存
                    if args.format == "json":
                        exported_data = (
                            self.quality_service.export_service.export_theme(
                                theme_data, "json"
                            )
                        )
                    elif args.format == "qss":
                        exported_data = (
                            self.quality_service.export_service.export_theme(
                                theme_data, "qss"
                            )
                        )
                    elif args.format == "css":
                        exported_data = (
                            self.quality_service.export_service.export_theme(
                                theme_data, "css"
                            )
                        )

                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(exported_data)

                    print("✓ エクスポート成功")
                    print("出力サイズ: {format_result['output_size']} バイト")
                    print("処理時間: {format_result['export_time']:.3f}秒")
                    return 0
                else:
                    print(
                        "✗ エクスポート失敗: {format_result.get('error_message', '不明なエラー')}"
                    )
                    return 1
            else:
                print(
                    "✗ エクスポート失敗: {export_result.get('error_message', '不明なエラー')}"
                )
                return 1

        except CLIError:
            print("エラー: {str()}", file=sys.stderr)
            return 1
        except Exception:
            print("予期しないエラーが発生しました: {str()}", file=sys.stderr)
            return 1

    def run(self, args: Optional[List[str]] = None) -> int:
        """CLIを実行する

        Args:
            args (Optional[List[str]]): コマンドライン引数（Noneの場合はsys.argvを使用）

        Returns:
            int: 終了コード
        """
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        # ログ設定
        self.setup_logging(parsed_args.verbose, parsed_args.quiet)

        # コマンド実行
        if parsed_args.command == "quality-check":
            return self.cmd_quality_check(parsed_args)
        elif parsed_args.command == "test":
            return self.cmd_test(parsed_args)
        elif parsed_args.command == "ci-report":
            return self.cmd_ci_report(parsed_args)
        elif parsed_args.command == "validate":
            return self.cmd_validate(parsed_args)
        elif parsed_args.command == "export":
            return self.cmd_export(parsed_args)
        else:
            parser.print_help()
            return 1


def main():
    """メイン関数"""
    cli = ThemeStudioCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
