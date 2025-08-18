#!/usr/bin/env python3
"""
統合品質チェックスクリプト

このスクリプトはruff、pytest、日本語ログ検証を統合実行し、
pre-commit用に最適化された品質チェックを提供します。
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def get_logger():
    """ロガーを取得（簡易版）"""
    import logging

    # 日本語対応のロガー設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    return logging.getLogger(__name__)


logger = get_logger()


class QualityChecker:
    """統合品質チェッククラス"""

    def __init__(self, project_root: Optional[Path] = None, fast_mode: bool = False):
        self.project_root = project_root or Path(__file__).parent.parent
        self.fast_mode = fast_mode
        self.results: Dict[str, Any] = {
            "timestamp": time.time(),
            "fast_mode": fast_mode,
            "checks": {},
            "summary": {
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "warnings": 0,
            },
        }

        # ログディレクトリの作成
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

    def run_command(
        self, command: List[str], description: str, timeout: int = 300
    ) -> Tuple[bool, str, str]:
        """コマンドを実行"""
        logger.info(f"{description}を実行中...")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )

            success = result.returncode == 0
            stdout = result.stdout or ""
            stderr = result.stderr or ""

            if success:
                logger.info(f"✅ {description}が完了しました")
            else:
                logger.warning(f"⚠️  {description}で問題が検出されました")

            return success, stdout, stderr

        except subprocess.TimeoutExpired:
            logger.error(f"❌ {description}がタイムアウトしました")
            return False, "", "タイムアウト"
        except Exception as e:
            logger.error(f"❌ {description}でエラーが発生しました: {e}")
            return False, "", str(e)

    def check_ruff_lint(self) -> Dict[str, Any]:
        """Ruffリンティングチェック"""
        logger.info("🔍 Ruffリンティングチェックを開始...")

        # リンティングチェック
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "ruff", "check", ".", "--output-format=json"],
            "Ruffリンティング",
        )

        issues = []
        if stdout:
            try:
                issues = json.loads(stdout)
            except json.JSONDecodeError:
                pass

        result = {
            "status": "PASS" if success else "FAIL",
            "issues_count": len(issues),
            "issues": issues[:10] if issues else [],  # 最初の10件のみ
            "stdout": stdout,
            "stderr": stderr,
        }

        if not success and issues:
            logger.warning(f"⚠️  {len(issues)}件のリンティング問題が検出されました")

        return result

    def check_ruff_format(self) -> Dict[str, Any]:
        """Ruffフォーマットチェック"""
        logger.info("🎨 Ruffフォーマットチェックを開始...")

        # フォーマットチェック（--checkオプションで確認のみ）
        success, stdout, stderr = self.run_command(
            [sys.executable, "-m", "ruff", "format", ".", "--check"], "Ruffフォーマット"
        )

        result = {
            "status": "PASS" if success else "FAIL",
            "stdout": stdout,
            "stderr": stderr,
        }

        if not success:
            logger.warning("⚠️  フォーマットの問題が検出されました")

        return result

    def check_basic_tests(self) -> Dict[str, Any]:
        """基本テストの実行"""
        logger.info("🧪 基本テストを開始...")

        # テストコマンドの構築
        test_args = [sys.executable, "-m", "pytest", "-v", "--tb=short"]

        if self.fast_mode:
            # 高速モード: 単体テストのみ、並列実行なし
            test_args.extend(
                [
                    "tests/unit",
                    "-x",  # 最初の失敗で停止
                    "--maxfail=3",
                    "-m",
                    "not slow and not integration",
                    "--durations=5",
                ]
            )
            timeout = 60  # 1分
        else:
            # 通常モード: 全テスト
            test_args.extend(["tests/", "--maxfail=10", "--durations=10"])
            timeout = 300  # 5分

        success, stdout, stderr = self.run_command(
            test_args, "基本テスト実行", timeout=timeout
        )

        # テスト結果の解析
        test_count = 0
        passed_count = 0
        failed_count = 0

        if stdout:
            lines = stdout.split("\n")
            for line in lines:
                if "passed" in line and "failed" in line:
                    # pytest の結果行を解析
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "passed":
                                passed_count = int(parts[i - 1])
                            elif part == "failed":
                                failed_count = int(parts[i - 1])
                        test_count = passed_count + failed_count
                    except (ValueError, IndexError):
                        pass

        result = {
            "status": "PASS" if success else "FAIL",
            "test_count": test_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "success_rate": (passed_count / test_count * 100) if test_count > 0 else 0,
            "stdout": stdout,
            "stderr": stderr,
        }

        if not success:
            logger.warning(f"⚠️  {failed_count}件のテストが失敗しました")

        return result

    def check_print_statements(self) -> Dict[str, Any]:
        """print文チェック"""
        logger.info("🖨️  print文チェックを開始...")

        script_path = self.project_root / "scripts" / "check_print_statements.py"
        if not script_path.exists():
            return {"status": "SKIP", "message": "チェックスクリプトが見つかりません"}

        # Pythonファイルを検索
        python_files = list(self.project_root.glob("qt_theme_studio/**/*.py"))

        if not python_files:
            return {
                "status": "SKIP",
                "message": "チェック対象のPythonファイルが見つかりません",
            }

        success, stdout, stderr = self.run_command(
            [sys.executable, str(script_path)] + [str(f) for f in python_files],
            "print文チェック",
        )

        result = {
            "status": "PASS" if success else "FAIL",
            "stdout": stdout,
            "stderr": stderr,
        }

        return result

    def check_japanese_logs(self) -> Dict[str, Any]:
        """日本語ログメッセージチェック"""
        logger.info("🇯🇵 日本語ログメッセージチェックを開始...")

        script_path = self.project_root / "scripts" / "validate_japanese_logs.py"
        if not script_path.exists():
            return {"status": "SKIP", "message": "チェックスクリプトが見つかりません"}

        # Pythonファイルを検索
        python_files = list(self.project_root.glob("qt_theme_studio/**/*.py"))

        if not python_files:
            return {
                "status": "SKIP",
                "message": "チェック対象のPythonファイルが見つかりません",
            }

        success, stdout, stderr = self.run_command(
            [sys.executable, str(script_path)] + [str(f) for f in python_files],
            "日本語ログメッセージチェック",
        )

        result = {
            "status": "PASS" if success else "FAIL",
            "stdout": stdout,
            "stderr": stderr,
        }

        return result

    def check_security_basic(self) -> Dict[str, Any]:
        """基本セキュリティチェック"""
        if self.fast_mode:
            return {"status": "SKIP", "message": "高速モードのためスキップ"}

        logger.info("🔒 基本セキュリティチェックを開始...")

        # Banditによるセキュリティチェック
        success, stdout, stderr = self.run_command(
            [
                sys.executable,
                "-m",
                "bandit",
                "-r",
                "qt_theme_studio/",
                "-f",
                "json",
                "-o",
                str(self.logs_dir / "bandit-quality-check.json"),
                "-ll",  # Low severity以上
            ],
            "Banditセキュリティチェック",
        )

        issues_count = 0
        if success and (self.logs_dir / "bandit-quality-check.json").exists():
            try:
                with open(self.logs_dir / "bandit-quality-check.json") as f:
                    bandit_result = json.load(f)
                    issues_count = len(bandit_result.get("results", []))
            except Exception:
                pass

        result = {
            "status": "PASS"
            if success and issues_count == 0
            else "WARN"
            if success
            else "FAIL",
            "issues_count": issues_count,
            "stdout": stdout,
            "stderr": stderr,
        }

        if issues_count > 0:
            logger.warning(f"⚠️  {issues_count}件のセキュリティ問題が検出されました")

        return result

    def run_all_checks(self) -> Dict[str, Any]:
        """すべてのチェックを実行"""
        logger.info("🚀 統合品質チェックを開始します")

        start_time = time.time()

        # チェック項目の定義
        checks = [
            ("ruff_lint", "Ruffリンティング", self.check_ruff_lint),
            ("ruff_format", "Ruffフォーマット", self.check_ruff_format),
            ("basic_tests", "基本テスト", self.check_basic_tests),
            ("print_statements", "print文チェック", self.check_print_statements),
            ("japanese_logs", "日本語ログ", self.check_japanese_logs),
            ("security_basic", "基本セキュリティ", self.check_security_basic),
        ]

        # チェック実行
        for check_id, check_name, check_func in checks:
            try:
                self.results["checks"][check_id] = check_func()
                self.results["summary"]["total_checks"] += 1

                status = self.results["checks"][check_id]["status"]
                if status == "PASS":
                    self.results["summary"]["passed_checks"] += 1
                elif status == "FAIL":
                    self.results["summary"]["failed_checks"] += 1
                elif status == "WARN":
                    self.results["summary"]["warnings"] += 1

            except Exception as e:
                logger.error(f"❌ {check_name}でエラーが発生しました: {e}")
                self.results["checks"][check_id] = {"status": "ERROR", "error": str(e)}
                self.results["summary"]["failed_checks"] += 1

        # 実行時間の記録
        end_time = time.time()
        self.results["execution_time"] = end_time - start_time

        # 結果の保存
        self.save_results()

        # サマリーの表示
        self.display_summary()

        return self.results

    def save_results(self):
        """結果をJSONファイルに保存"""
        try:
            output_file = self.logs_dir / "quality_check_results.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 結果を保存しました: {output_file}")
        except Exception as e:
            logger.error(f"❌ 結果の保存に失敗しました: {e}")

    def display_summary(self):
        """結果サマリーを表示"""
        summary = self.results["summary"]
        execution_time = self.results.get("execution_time", 0)

        logger.info("\n" + "=" * 50)
        logger.info("📊 品質チェック結果サマリー")
        logger.info("=" * 50)
        logger.info(f"実行時間: {execution_time:.2f}秒")
        logger.info(f"総チェック数: {summary['total_checks']}")
        logger.info(f"✅ 成功: {summary['passed_checks']}")
        logger.info(f"⚠️  警告: {summary['warnings']}")
        logger.info(f"❌ 失敗: {summary['failed_checks']}")

        # 個別結果の表示
        for check_id, result in self.results["checks"].items():
            status = result["status"]
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARN": "⚠️ ",
                "SKIP": "⏭️ ",
                "ERROR": "💥",
            }.get(status, "❓")

            logger.info(f"{status_icon} {check_id}: {status}")

        # 全体的な成功判定
        overall_success = summary["failed_checks"] == 0

        if overall_success:
            logger.info("\n🎉 すべての品質チェックが完了しました！")
        else:
            logger.info(f"\n⚠️  {summary['failed_checks']}件の問題が検出されました")
            logger.info("詳細は logs/quality_check_results.json を確認してください")

        return overall_success


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="統合品質チェック")
    parser.add_argument(
        "--fast", action="store_true", help="高速モード（基本チェックのみ）"
    )
    parser.add_argument(
        "--project-root", type=Path, help="プロジェクトルートディレクトリ"
    )

    args = parser.parse_args()

    # 品質チェッカーの初期化
    checker = QualityChecker(project_root=args.project_root, fast_mode=args.fast)

    # チェック実行
    results = checker.run_all_checks()

    # 終了コードの決定
    failed_checks = results["summary"]["failed_checks"]
    sys.exit(0 if failed_checks == 0 else 1)


if __name__ == "__main__":
    main()
