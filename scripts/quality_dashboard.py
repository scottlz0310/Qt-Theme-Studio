#!/usr/bin/env python3
"""
Qt-Theme-Studio 品質メトリクスダッシュボード

テスト統計、カバレッジ、品質スコアを可視化します
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlibが利用できません。グラフ表示は無効です。")
    print("   インストール: pip install matplotlib")


class QualityDashboard:
    """品質メトリクスダッシュボード"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}

    def collect_test_statistics(self) -> dict[str, Any]:
        """テスト統計を収集"""
        print("📊 テスト統計を収集中...")

        try:
            # テスト数のカウント
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "--collect-only", "-q"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if "collected" in result.stdout:
                test_count = int(result.stdout.split("collected")[1].split()[0])
            else:
                test_count = 0

            # テスト実行
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            # 成功・失敗のカウント
            output_lines = result.stdout.split("\n")
            passed = sum(1 for line in output_lines if line.startswith("."))
            failed = sum(1 for line in output_lines if line.startswith("F"))
            errors = sum(1 for line in output_lines if line.startswith("E"))

            return {
                "total_tests": test_count,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "success_rate": (passed / test_count * 100) if test_count > 0 else 0,
            }

        except Exception as e:
            print(f"❌ テスト統計の収集に失敗: {e}")
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "success_rate": 0,
            }

    def collect_coverage_data(self) -> dict[str, Any]:
        """カバレッジデータを収集"""
        print("📈 カバレッジデータを収集中...")

        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "tests/",
                    "--cov=qt_theme_studio",
                    "--cov-report=term-missing",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            coverage_data = {}
            output_lines = result.stdout.split("\n")

            for line in output_lines:
                if "qt_theme_studio/" in line and "Stmts" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        module_name = parts[0]
                        statements = int(parts[1])
                        missed = int(parts[2])
                        coverage = float(parts[3].rstrip("%"))

                        coverage_data[module_name] = {
                            "statements": statements,
                            "missed": missed,
                            "coverage": coverage,
                        }

            # 全体カバレッジ
            total_line = [line for line in output_lines if "TOTAL" in line]
            if total_line:
                total_parts = total_line[0].split()
                if len(total_parts) >= 4:
                    total_statements = int(total_parts[1])
                    total_missed = int(total_parts[2])
                    total_coverage = float(total_parts[3].rstrip("%"))

                    coverage_data["TOTAL"] = {
                        "statements": total_statements,
                        "missed": total_missed,
                        "coverage": total_coverage,
                    }

            return coverage_data

        except Exception as e:
            print(f"❌ カバレッジデータの収集に失敗: {e}")
            return {}

    def collect_file_statistics(self) -> dict[str, Any]:
        """ファイル統計を収集"""
        print("📁 ファイル統計を収集中...")

        try:
            source_dir = self.project_root / "qt_theme_studio"
            test_dir = self.project_root / "tests"

            # ソースファイルの統計
            source_files = list(source_dir.rglob("*.py"))
            source_lines = sum(len(f.read_text().splitlines()) for f in source_files)

            # テストファイルの統計
            test_files = list(test_dir.rglob("*.py"))
            test_lines = sum(len(f.read_text().splitlines()) for f in test_files)

            return {
                "source_files": len(source_files),
                "source_lines": source_lines,
                "test_files": len(test_files),
                "test_lines": test_lines,
                "test_ratio": test_lines / source_lines if source_lines > 0 else 0,
            }

        except Exception as e:
            print(f"❌ ファイル統計の収集に失敗: {e}")
            return {}

    def calculate_quality_score(
        self, coverage: float, test_count: int, success_rate: float
    ) -> str:
        """品質スコアを計算"""
        # カバレッジの重み: 40%
        coverage_score = min(coverage / 100, 1.0) * 40

        # テスト数の重み: 30%
        test_score = min(test_count / 200, 1.0) * 30

        # 成功率の重み: 30%
        success_score = (success_rate / 100) * 30

        total_score = coverage_score + test_score + success_score

        if total_score >= 85:
            return "A+"
        if total_score >= 75:
            return "A"
        if total_score >= 65:
            return "B+"
        if total_score >= 55:
            return "B"
        if total_score >= 45:
            return "C+"
        if total_score >= 35:
            return "C"
        return "D"

    def generate_text_report(self) -> str:
        """テキストレポートを生成"""
        report = []
        report.append("=" * 60)
        report.append("Qt-Theme-Studio 品質メトリクスレポート")
        report.append("=" * 60)
        report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # テスト統計
        test_stats = self.results.get("test_statistics", {})
        report.append("📊 テスト統計")
        report.append("-" * 30)
        report.append(f"総テスト数: {test_stats.get('total_tests', 0)}")
        report.append(f"成功: {test_stats.get('passed', 0)}")
        report.append(f"失敗: {test_stats.get('failed', 0)}")
        report.append(f"エラー: {test_stats.get('errors', 0)}")
        report.append(f"成功率: {test_stats.get('success_rate', 0):.1f}%")
        report.append("")

        # カバレッジ統計
        coverage_data = self.results.get("coverage_data", {})
        report.append("📈 カバレッジ統計")
        report.append("-" * 30)

        for module, data in coverage_data.items():
            if module != "TOTAL":
                report.append(
                    f"{module}: {data['coverage']:.1f}% ({data['statements']}行)"
                )

        if "TOTAL" in coverage_data:
            total = coverage_data["TOTAL"]
            report.append(f"全体: {total['coverage']:.1f}% ({total['statements']}行)")
        report.append("")

        # ファイル統計
        file_stats = self.results.get("file_statistics", {})
        report.append("📁 ファイル統計")
        report.append("-" * 30)
        report.append(f"ソースファイル: {file_stats.get('source_files', 0)}")
        report.append(f"ソース行数: {file_stats.get('source_lines', 0)}")
        report.append(f"テストファイル: {file_stats.get('test_files', 0)}")
        report.append(f"テスト行数: {file_stats.get('test_lines', 0)}")
        report.append(f"テスト比率: {file_stats.get('test_ratio', 0):.2f}")
        report.append("")

        # 品質スコア
        quality_score = self.results.get("quality_score", "N/A")
        report.append("🎯 品質スコア")
        report.append("-" * 30)
        report.append(f"総合評価: {quality_score}")
        report.append("")

        # 推奨事項
        report.append("💡 推奨事項")
        report.append("-" * 30)

        total_coverage = coverage_data.get("TOTAL", {}).get("coverage", 0)
        if total_coverage < 50:
            report.append(
                "🚨 カバレッジが50%未満です。テストの追加を優先してください。"
            )
        elif total_coverage < 70:
            report.append("⚠️ カバレッジが70%未満です。テストの追加を検討してください。")
        else:
            report.append("✅ カバレッジは良好です。現在のレベルを維持してください。")

        test_count = test_stats.get("total_tests", 0)
        if test_count < 100:
            report.append("📈 テスト数を増やしてカバレッジを向上させてください。")
        else:
            report.append("🎯 テスト数は十分です。")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def generate_visualization(self):
        """可視化を生成"""
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️  matplotlibが利用できないため、可視化をスキップします。")
            return

        print("📊 可視化を生成中...")

        try:
            # カバレッジの棒グラフ
            coverage_data = self.results.get("coverage_data", {})
            if coverage_data:
                modules = [k for k in coverage_data.keys() if k != "TOTAL"]
                coverages = [coverage_data[m]["coverage"] for m in modules]

                plt.figure(figsize=(12, 8))

                # メインのカバレッジグラフ
                plt.subplot(2, 2, 1)
                bars = plt.bar(modules, coverages, color="skyblue", edgecolor="navy")
                plt.title("モジュール別カバレッジ", fontsize=14, fontweight="bold")
                plt.ylabel("カバレッジ (%)")
                plt.xticks(rotation=45, ha="right")
                plt.ylim(0, 100)

                # カバレッジ値の表示
                for bar, coverage in zip(bars, coverages):
                    plt.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 1,
                        f"{coverage:.1f}%",
                        ha="center",
                        va="bottom",
                    )

                # テスト統計の円グラフ
                plt.subplot(2, 2, 2)
                test_stats = self.results.get("test_statistics", {})
                if test_stats:
                    labels = ["成功", "失敗", "エラー"]
                    sizes = [
                        test_stats.get("passed", 0),
                        test_stats.get("failed", 0),
                        test_stats.get("errors", 0),
                    ]
                    colors = ["lightgreen", "lightcoral", "gold"]

                    if sum(sizes) > 0:
                        plt.pie(
                            sizes,
                            labels=labels,
                            colors=colors,
                            autopct="%1.1f%%",
                            startangle=90,
                        )
                        plt.title("テスト結果の分布", fontsize=14, fontweight="bold")

                # ファイル統計の棒グラフ
                plt.subplot(2, 2, 3)
                file_stats = self.results.get("file_statistics", {})
                if file_stats:
                    categories = ["ソース", "テスト"]
                    lines = [
                        file_stats.get("source_lines", 0),
                        file_stats.get("test_lines", 0),
                    ]
                    colors = ["lightblue", "lightgreen"]

                    bars = plt.bar(categories, lines, color=colors, edgecolor="navy")
                    plt.title("コード行数の比較", fontsize=14, fontweight="bold")
                    plt.ylabel("行数")

                    for bar, line_count in zip(bars, lines):
                        plt.text(
                            bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 1,
                            f"{line_count}",
                            ha="center",
                            va="bottom",
                        )

                # 品質スコアの表示
                plt.subplot(2, 2, 4)
                quality_score = self.results.get("quality_score", "N/A")

                # スコアに基づく色の設定
                score_colors = {
                    "A+": "darkgreen",
                    "A": "green",
                    "B+": "lightgreen",
                    "B": "yellow",
                    "C+": "orange",
                    "C": "darkorange",
                    "D": "red",
                }

                color = score_colors.get(quality_score, "gray")

                plt.text(
                    0.5,
                    0.5,
                    f"品質スコア\n{quality_score}",
                    ha="center",
                    va="center",
                    fontsize=24,
                    fontweight="bold",
                    transform=plt.gca().transAxes,
                    color=color,
                )
                plt.title("総合品質評価", fontsize=14, fontweight="bold")
                plt.axis("off")

                plt.tight_layout()

                # 保存
                output_file = self.project_root / "quality_dashboard.png"
                plt.savefig(output_file, dpi=300, bbox_inches="tight")
                print(f"✅ 可視化を保存しました: {output_file}")

                # 表示
                plt.show()

        except Exception as e:
            print(f"❌ 可視化の生成に失敗: {e}")

    def save_json_report(self):
        """JSONレポートを保存"""
        try:
            output_file = self.project_root / "quality_report.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"✅ JSONレポートを保存しました: {output_file}")
        except Exception as e:
            print(f"❌ JSONレポートの保存に失敗: {e}")

    def run(self):
        """ダッシュボードを実行"""
        print("🚀 Qt-Theme-Studio 品質メトリクスダッシュボードを開始します...")
        print("=" * 60)

        # データ収集
        self.results["test_statistics"] = self.collect_test_statistics()
        self.results["coverage_data"] = self.collect_coverage_data()
        self.results["file_statistics"] = self.collect_file_statistics()

        # 品質スコアの計算
        total_coverage = (
            self.results["coverage_data"].get("TOTAL", {}).get("coverage", 0)
        )
        test_count = self.results["test_statistics"].get("total_tests", 0)
        success_rate = self.results["test_statistics"].get("success_rate", 0)

        self.results["quality_score"] = self.calculate_quality_score(
            total_coverage, test_count, success_rate
        )

        # レポート生成
        text_report = self.generate_text_report()
        print(text_report)

        # ファイル保存
        self.save_json_report()

        # 可視化
        self.generate_visualization()

        print("\n🎉 品質メトリクスダッシュボードが完了しました！")
        print("📁 生成されたファイル:")
        print("   - quality_report.json: 詳細データ")
        if MATPLOTLIB_AVAILABLE:
            print("   - quality_dashboard.png: 可視化グラフ")


def main():
    """メイン関数"""
    dashboard = QualityDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
