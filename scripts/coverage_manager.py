#!/usr/bin/env python3
"""
テストカバレッジ管理スクリプト

pytest-covを使用したカバレッジ測定の自動化と
HTMLとXML形式でのレポート出力、閾値チェック機能を提供します。
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/coverage_manager.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


class CoverageManager:
    """テストカバレッジ管理クラス"""

    def __init__(self, source_dir: str = "qt_theme_studio", min_coverage: float = 80.0):
        self.source_dir = source_dir
        self.min_coverage = min_coverage
        self.project_root = Path(__file__).parent.parent
        self.coverage_dir = self.project_root / "htmlcov"
        self.reports_dir = self.project_root / "logs"

        # ディレクトリ作成
        self.coverage_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    def run_coverage_tests(self, test_paths: Optional[List[str]] = None) -> bool:
        """カバレッジ付きでテストを実行"""
        logger.info("📊 カバレッジ付きテストを開始します...")

        if test_paths is None:
            test_paths = ["tests/"]

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            *test_paths,
            f"--cov={self.source_dir}",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=json:coverage.json",
            f"--cov-fail-under={self.min_coverage}",
            "-v",
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            logger.info(f"テスト実行完了 (終了コード: {result.returncode})")

            if result.stdout:
                logger.info("テスト出力:")
                for line in result.stdout.split("\n"):
                    if line.strip():
                        logger.info(f"  {line}")

            if result.stderr:
                logger.warning("エラー出力:")
                for line in result.stderr.split("\n"):
                    if line.strip():
                        logger.warning(f"  {line}")

            return result.returncode == 0

        except Exception as e:
            logger.error(f"テスト実行中にエラーが発生しました: {e}")
            return False

    def get_coverage_data(self) -> Optional[Dict]:
        """カバレッジデータを取得"""
        coverage_file = self.project_root / "coverage.json"

        if not coverage_file.exists():
            logger.error("カバレッジファイルが見つかりません")
            return None

        try:
            with open(coverage_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"カバレッジデータの読み込みに失敗しました: {e}")
            return None

    def analyze_coverage(self) -> Tuple[float, Dict[str, float]]:
        """カバレッジを分析"""
        coverage_data = self.get_coverage_data()

        if not coverage_data:
            return 0.0, {}

        # 全体のカバレッジ率を計算
        totals = coverage_data.get("totals", {})
        total_coverage = totals.get("percent_covered", 0.0)

        # ファイル別のカバレッジ率を取得
        files_coverage = {}
        files_data = coverage_data.get("files", {})

        for file_path, file_data in files_data.items():
            summary = file_data.get("summary", {})
            coverage_percent = summary.get("percent_covered", 0.0)
            files_coverage[file_path] = coverage_percent

        return total_coverage, files_coverage

    def check_coverage_threshold(self) -> bool:
        """カバレッジ閾値をチェック"""
        total_coverage, files_coverage = self.analyze_coverage()

        logger.info(f"📊 総合カバレッジ: {total_coverage:.2f}%")

        if total_coverage >= self.min_coverage:
            logger.info(
                f"✅ カバレッジが閾値を満たしています: {total_coverage:.2f}% >= {self.min_coverage}%"
            )
            return True
        logger.warning(
            f"⚠️  カバレッジが閾値を下回っています: {total_coverage:.2f}% < {self.min_coverage}%"
        )

        # 低カバレッジファイルを特定
        low_coverage_files = [
            (file_path, coverage)
            for file_path, coverage in files_coverage.items()
            if coverage < self.min_coverage
        ]

        if low_coverage_files:
            logger.warning("低カバレッジファイル:")
            for file_path, coverage in sorted(low_coverage_files, key=lambda x: x[1]):
                logger.warning(f"  {file_path}: {coverage:.2f}%")

        return False

    def generate_coverage_summary(self) -> Dict:
        """カバレッジサマリーを生成"""
        total_coverage, files_coverage = self.analyze_coverage()

        summary = {
            "total_coverage": total_coverage,
            "threshold": self.min_coverage,
            "threshold_met": total_coverage >= self.min_coverage,
            "files_count": len(files_coverage),
            "low_coverage_files": [
                {"file": file_path, "coverage": coverage}
                for file_path, coverage in files_coverage.items()
                if coverage < self.min_coverage
            ],
        }

        # サマリーをファイルに保存
        summary_file = self.reports_dir / "coverage_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"カバレッジサマリーを保存しました: {summary_file}")

        return summary

    def generate_coverage_badge(self) -> str:
        """カバレッジバッジ用のデータを生成"""
        total_coverage, _ = self.analyze_coverage()

        if total_coverage >= 90:
            color = "brightgreen"
        elif total_coverage >= 80:
            color = "green"
        elif total_coverage >= 70:
            color = "yellow"
        elif total_coverage >= 60:
            color = "orange"
        else:
            color = "red"

        badge_data = {
            "schemaVersion": 1,
            "label": "coverage",
            "message": f"{total_coverage:.1f}%",
            "color": color,
        }

        badge_file = self.reports_dir / "coverage_badge.json"
        with open(badge_file, "w", encoding="utf-8") as f:
            json.dump(badge_data, f, indent=2)

        logger.info(f"カバレッジバッジデータを生成しました: {badge_file}")

        return f"https://img.shields.io/badge/coverage-{total_coverage:.1f}%25-{color}"

    def run_full_coverage_check(self, test_paths: Optional[List[str]] = None) -> bool:
        """完全なカバレッジチェックを実行"""
        logger.info("🚀 完全なカバレッジチェックを開始します...")

        # テスト実行
        if not self.run_coverage_tests(test_paths):
            logger.error("❌ テスト実行が失敗しました")
            return False

        # カバレッジ分析
        summary = self.generate_coverage_summary()

        # バッジ生成
        badge_url = self.generate_coverage_badge()
        logger.info(f"カバレッジバッジURL: {badge_url}")

        # 閾値チェック
        threshold_met = self.check_coverage_threshold()

        if threshold_met:
            logger.info("✅ カバレッジチェックが完了しました")
        else:
            logger.warning("⚠️  カバレッジが閾値を下回っています")

        return threshold_met


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="テストカバレッジ管理")
    parser.add_argument(
        "--source-dir",
        default="qt_theme_studio",
        help="ソースディレクトリ (デフォルト: qt_theme_studio)",
    )
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=80.0,
        help="最小カバレッジ閾値 (デフォルト: 80.0)",
    )
    parser.add_argument(
        "--test-paths",
        nargs="*",
        default=["tests/"],
        help="テストパス (デフォルト: tests/)",
    )
    parser.add_argument("--ci-mode", action="store_true", help="CI環境での実行")

    args = parser.parse_args()

    # CI環境での設定調整
    if args.ci_mode:
        logging.getLogger().setLevel(logging.WARNING)

    manager = CoverageManager(
        source_dir=args.source_dir, min_coverage=args.min_coverage
    )

    success = manager.run_full_coverage_check(args.test_paths)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
