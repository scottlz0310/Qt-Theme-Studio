#!/usr/bin/env python3
"""
Qt-Theme-Studio 統合品質メトリクスダッシュボード

テスト統計、カバレッジ、品質スコア、ワークフロー統計を統合表示します。
リアルタイム監視機能と日本語での統合レポート生成をサポート。
"""

import json
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from qt_theme_studio.logger import get_logger

# ワークフローエンジンをインポート
try:
    from scripts.config_manager import ConfigManager
    from scripts.workflow_engine import WorkflowEngine, WorkflowStatus

    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False
    print("⚠️  ワークフローエンジンが利用できません。")

try:
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlibが利用できません。グラフ表示は無効です。")
    print("   インストール: pip install matplotlib")


class IntegratedQualityDashboard:
    """統合品質メトリクスダッシュボード

    品質メトリクス、ワークフロー統計、リアルタイム監視を統合したダッシュボード。
    """

    def __init__(self, config_path: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.workflow_history = []
        self.monitoring_active = False
        self.monitoring_thread = None

        # ワークフローエンジンとコンフィグマネージャーを初期化
        if WORKFLOW_AVAILABLE:
            try:
                self.workflow_engine = WorkflowEngine(config_path)
                self.config_manager = ConfigManager(config_path)
                self.logger.info("ワークフローエンジンが初期化されました")
            except Exception as e:
                self.logger.warning(f"ワークフローエンジンの初期化に失敗: {e}")
                self.workflow_engine = None
                self.config_manager = None
        else:
            self.workflow_engine = None
            self.config_manager = None

        # メトリクス履歴保存用
        self.metrics_history_file = self.project_root / "logs" / "metrics_history.json"
        self.metrics_history = self._load_metrics_history()

        self.logger.info("統合品質ダッシュボードが初期化されました")

    def _load_metrics_history(self) -> List[Dict[str, Any]]:
        """メトリクス履歴を読み込み"""
        try:
            if self.metrics_history_file.exists():
                with open(self.metrics_history_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"メトリクス履歴の読み込みに失敗: {e}")
        return []

    def _save_metrics_history(self) -> None:
        """メトリクス履歴を保存"""
        try:
            # ディレクトリを作成
            self.metrics_history_file.parent.mkdir(parents=True, exist_ok=True)

            # 履歴を保存（最新100件まで）
            history_to_save = self.metrics_history[-100:]
            with open(self.metrics_history_file, "w", encoding="utf-8") as f:
                json.dump(history_to_save, f, indent=2, ensure_ascii=False, default=str)

            self.logger.debug("メトリクス履歴を保存しました")
        except Exception as e:
            self.logger.error(f"メトリクス履歴の保存に失敗: {e}")

    def collect_workflow_statistics(self) -> Dict[str, Any]:
        """ワークフロー統計を収集"""
        if not self.workflow_engine:
            return {}

        self.logger.info("ワークフロー統計を収集中...")

        try:
            # 利用可能なワークフロー一覧
            available_workflows = self.workflow_engine.get_available_workflows()

            # ワークフロー設定情報
            workflow_configs = {}
            for workflow_name in available_workflows:
                config = self.workflow_engine.get_workflow_config(workflow_name)
                if config:
                    workflow_configs[workflow_name] = {
                        "enabled": config.get("enabled", True),
                        "step_count": len(config.get("steps", [])),
                        "description": config.get("description", ""),
                    }

            # 最近のワークフロー実行履歴（ログファイルから取得）
            recent_executions = self._get_recent_workflow_executions()

            # 成功率の計算
            success_rates = {}
            for workflow_name in available_workflows:
                executions = [
                    e for e in recent_executions if e.get("workflow") == workflow_name
                ]
                if executions:
                    successful = sum(
                        1 for e in executions if e.get("status") == "success"
                    )
                    success_rates[workflow_name] = (successful / len(executions)) * 100
                else:
                    success_rates[workflow_name] = 0

            return {
                "available_workflows": available_workflows,
                "workflow_configs": workflow_configs,
                "recent_executions": recent_executions,
                "success_rates": success_rates,
                "total_workflows": len(available_workflows),
                "enabled_workflows": sum(
                    1 for config in workflow_configs.values() if config["enabled"]
                ),
            }

        except Exception as e:
            self.logger.error(f"ワークフロー統計の収集に失敗: {e}")
            return {}

    def _get_recent_workflow_executions(self) -> List[Dict[str, Any]]:
        """最近のワークフロー実行履歴を取得"""
        try:
            # ログファイルから実行履歴を抽出（簡易実装）
            log_files = list((self.project_root / "logs").glob("*.log"))
            executions = []

            for log_file in log_files:
                try:
                    with open(log_file, encoding="utf-8") as f:
                        for line in f:
                            if "ワークフロー" in line and (
                                "開始" in line or "完了" in line
                            ):
                                # ログ行からワークフロー情報を抽出
                                # 実際の実装では、より構造化されたログ形式を使用
                                execution_info = self._parse_workflow_log_line(line)
                                if execution_info:
                                    executions.append(execution_info)
                except Exception:
                    continue

            # 最新20件を返す
            return sorted(
                executions, key=lambda x: x.get("timestamp", ""), reverse=True
            )[:20]

        except Exception as e:
            self.logger.warning(f"ワークフロー実行履歴の取得に失敗: {e}")
            return []

    def _parse_workflow_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """ログ行からワークフロー情報を解析"""
        try:
            # 簡易的なログ解析（実際の実装では正規表現等を使用）
            if "完了" in line:
                parts = line.split()
                timestamp = f"{parts[0]} {parts[1]}"

                # ワークフロー名を抽出
                workflow_name = "unknown"
                if "'" in line:
                    start = line.find("'") + 1
                    end = line.find("'", start)
                    if end > start:
                        workflow_name = line[start:end]

                # ステータスを判定
                status = "success" if "正常" in line or "完了" in line else "failure"

                return {
                    "timestamp": timestamp,
                    "workflow": workflow_name,
                    "status": status,
                    "message": line.strip(),
                }
        except Exception:
            pass

        return None

    def collect_system_metrics(self) -> Dict[str, Any]:
        """システムメトリクスを収集"""
        self.logger.info("システムメトリクスを収集中...")

        try:
            import psutil

            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # メモリ使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # ディスク使用率
            disk = psutil.disk_usage(str(self.project_root))
            disk_percent = (disk.used / disk.total) * 100

            # プロセス情報
            current_process = psutil.Process()
            process_memory = current_process.memory_info().rss / 1024 / 1024  # MB

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "process_memory_mb": process_memory,
                "timestamp": datetime.now().isoformat(),
            }

        except ImportError:
            self.logger.warning(
                "psutilが利用できません。システムメトリクスをスキップします"
            )
            return {}
        except Exception as e:
            self.logger.error(f"システムメトリクスの収集に失敗: {e}")
            return {}

    def collect_security_metrics(self) -> Dict[str, Any]:
        """セキュリティメトリクスを収集"""
        self.logger.info("セキュリティメトリクスを収集中...")

        try:
            # セキュリティスキャン結果を取得
            security_report_file = (
                self.project_root / "logs" / "bandit-security-report.json"
            )

            if security_report_file.exists():
                with open(security_report_file, encoding="utf-8") as f:
                    security_data = json.load(f)

                # メトリクスを抽出
                metrics = security_data.get("metrics", {})
                results = security_data.get("results", [])

                # 重要度別の問題数
                severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
                for result in results:
                    severity = result.get("issue_severity", "LOW")
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1

                return {
                    "total_issues": len(results),
                    "severity_counts": severity_counts,
                    "files_scanned": metrics.get("_totals", {}).get("loc", 0),
                    "security_score": self._calculate_security_score(severity_counts),
                    "last_scan": datetime.now().isoformat(),
                }
            return {"error": "セキュリティレポートが見つかりません"}

        except Exception as e:
            self.logger.error(f"セキュリティメトリクスの収集に失敗: {e}")
            return {}

    def _calculate_security_score(self, severity_counts: Dict[str, int]) -> float:
        """セキュリティスコアを計算（1-10）"""
        # 重要度に応じた重み付け
        high_weight = 3
        medium_weight = 2
        low_weight = 1

        total_weighted_issues = (
            severity_counts.get("HIGH", 0) * high_weight
            + severity_counts.get("MEDIUM", 0) * medium_weight
            + severity_counts.get("LOW", 0) * low_weight
        )

        # スコア計算（問題が少ないほど高スコア）
        if total_weighted_issues == 0:
            return 10.0
        if total_weighted_issues <= 5:
            return 9.0
        if total_weighted_issues <= 10:
            return 8.0
        if total_weighted_issues <= 20:
            return 7.0
        if total_weighted_issues <= 30:
            return 6.0
        return max(1.0, 6.0 - (total_weighted_issues - 30) * 0.1)

    def collect_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンスメトリクスを収集"""
        self.logger.info("パフォーマンスメトリクスを収集中...")

        try:
            # ベンチマーク結果を取得
            benchmark_file = self.project_root / "benchmark.json"

            if benchmark_file.exists():
                with open(benchmark_file, encoding="utf-8") as f:
                    benchmark_data = json.load(f)

                # ベンチマーク統計を抽出
                benchmarks = benchmark_data.get("benchmarks", [])

                if benchmarks:
                    # 平均実行時間
                    avg_times = [b.get("stats", {}).get("mean", 0) for b in benchmarks]
                    overall_avg = sum(avg_times) / len(avg_times) if avg_times else 0

                    # 最も遅いテスト
                    slowest_test = max(
                        benchmarks, key=lambda x: x.get("stats", {}).get("mean", 0)
                    )

                    return {
                        "total_benchmarks": len(benchmarks),
                        "average_execution_time": overall_avg,
                        "slowest_test": {
                            "name": slowest_test.get("name", "unknown"),
                            "time": slowest_test.get("stats", {}).get("mean", 0),
                        },
                        "performance_score": self._calculate_performance_score(
                            overall_avg
                        ),
                    }

            return {"error": "ベンチマーク結果が見つかりません"}

        except Exception as e:
            self.logger.error(f"パフォーマンスメトリクスの収集に失敗: {e}")
            return {}

    def _calculate_performance_score(self, avg_time: float) -> str:
        """パフォーマンススコアを計算"""
        if avg_time < 0.1:
            return "優秀"
        if avg_time < 0.5:
            return "良好"
        if avg_time < 1.0:
            return "普通"
        if avg_time < 2.0:
            return "改善要"
        return "要最適化"

    def collect_test_statistics(self) -> Dict[str, Any]:
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

    def start_realtime_monitoring(self, interval: int = 60) -> None:
        """リアルタイム監視を開始

        Args:
            interval: 監視間隔（秒）
        """
        if self.monitoring_active:
            self.logger.warning("リアルタイム監視は既に実行中です")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, args=(interval,), daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info(f"リアルタイム監視を開始しました（間隔: {interval}秒）")

    def stop_realtime_monitoring(self) -> None:
        """リアルタイム監視を停止"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("リアルタイム監視を停止しました")

    def _monitoring_loop(self, interval: int) -> None:
        """監視ループ"""
        while self.monitoring_active:
            try:
                # メトリクスを収集
                current_metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "system_metrics": self.collect_system_metrics(),
                    "workflow_statistics": self.collect_workflow_statistics(),
                }

                # 履歴に追加
                self.metrics_history.append(current_metrics)

                # アラートチェック
                self._check_alerts(current_metrics)

                # 履歴を保存
                self._save_metrics_history()

                # 指定間隔で待機
                time.sleep(interval)

            except Exception as e:
                self.logger.error(f"監視ループでエラーが発生: {e}")
                time.sleep(interval)

    def _check_alerts(self, metrics: Dict[str, Any]) -> None:
        """アラート条件をチェック"""
        try:
            system_metrics = metrics.get("system_metrics", {})

            # CPU使用率アラート
            cpu_percent = system_metrics.get("cpu_percent", 0)
            if cpu_percent > 80:
                self.logger.warning(f"🚨 CPU使用率が高いです: {cpu_percent:.1f}%")

            # メモリ使用率アラート
            memory_percent = system_metrics.get("memory_percent", 0)
            if memory_percent > 85:
                self.logger.warning(f"🚨 メモリ使用率が高いです: {memory_percent:.1f}%")

            # ディスク使用率アラート
            disk_percent = system_metrics.get("disk_percent", 0)
            if disk_percent > 90:
                self.logger.warning(f"🚨 ディスク使用率が高いです: {disk_percent:.1f}%")

            # ワークフロー失敗率アラート
            workflow_stats = metrics.get("workflow_statistics", {})
            success_rates = workflow_stats.get("success_rates", {})

            for workflow_name, success_rate in success_rates.items():
                if success_rate < 80:
                    self.logger.warning(
                        f"🚨 ワークフロー '{workflow_name}' の成功率が低いです: {success_rate:.1f}%"
                    )

        except Exception as e:
            self.logger.error(f"アラートチェック中にエラーが発生: {e}")

    def generate_integrated_report(self) -> str:
        """統合レポートを生成（日本語）"""
        report = []
        report.append("=" * 80)
        report.append("Qt-Theme-Studio 統合品質メトリクスレポート")
        report.append("=" * 80)
        report.append(
            f"生成日時: {datetime.now().strftime('%Y年%m月%d日 %H時%M分%S秒')}"
        )
        report.append("")

        # ワークフロー統計
        workflow_stats = self.results.get("workflow_statistics", {})
        if workflow_stats:
            report.append("🔄 ワークフロー統計")
            report.append("-" * 40)
            report.append(
                f"利用可能なワークフロー数: {workflow_stats.get('total_workflows', 0)}"
            )
            report.append(
                f"有効なワークフロー数: {workflow_stats.get('enabled_workflows', 0)}"
            )

            success_rates = workflow_stats.get("success_rates", {})
            if success_rates:
                report.append("\nワークフロー成功率:")
                for workflow_name, success_rate in success_rates.items():
                    status_icon = (
                        "✅"
                        if success_rate >= 90
                        else "⚠️"
                        if success_rate >= 70
                        else "❌"
                    )
                    report.append(
                        f"  {status_icon} {workflow_name}: {success_rate:.1f}%"
                    )
            report.append("")

        # システムメトリクス
        system_metrics = self.results.get("system_metrics", {})
        if system_metrics:
            report.append("💻 システムメトリクス")
            report.append("-" * 40)
            report.append(f"CPU使用率: {system_metrics.get('cpu_percent', 0):.1f}%")
            report.append(
                f"メモリ使用率: {system_metrics.get('memory_percent', 0):.1f}%"
            )
            report.append(
                f"ディスク使用率: {system_metrics.get('disk_percent', 0):.1f}%"
            )
            report.append(
                f"プロセスメモリ: {system_metrics.get('process_memory_mb', 0):.1f}MB"
            )
            report.append("")

        # セキュリティメトリクス
        security_metrics = self.results.get("security_metrics", {})
        if security_metrics and "error" not in security_metrics:
            report.append("🔒 セキュリティメトリクス")
            report.append("-" * 40)
            report.append(f"総問題数: {security_metrics.get('total_issues', 0)}")

            severity_counts = security_metrics.get("severity_counts", {})
            report.append(f"高重要度: {severity_counts.get('HIGH', 0)}")
            report.append(f"中重要度: {severity_counts.get('MEDIUM', 0)}")
            report.append(f"低重要度: {severity_counts.get('LOW', 0)}")
            report.append(
                f"セキュリティスコア: {security_metrics.get('security_score', 0):.1f}/10"
            )
            report.append("")

        # パフォーマンスメトリクス
        performance_metrics = self.results.get("performance_metrics", {})
        if performance_metrics and "error" not in performance_metrics:
            report.append("⚡ パフォーマンスメトリクス")
            report.append("-" * 40)
            report.append(
                f"ベンチマーク数: {performance_metrics.get('total_benchmarks', 0)}"
            )
            report.append(
                f"平均実行時間: {performance_metrics.get('average_execution_time', 0):.3f}秒"
            )

            slowest_test = performance_metrics.get("slowest_test", {})
            if slowest_test:
                report.append(
                    f"最遅テスト: {slowest_test.get('name', 'N/A')} ({slowest_test.get('time', 0):.3f}秒)"
                )

            report.append(
                f"パフォーマンス評価: {performance_metrics.get('performance_score', 'N/A')}"
            )
            report.append("")

        # 従来のテスト統計
        test_stats = self.results.get("test_statistics", {})
        if test_stats:
            report.append("📊 テスト統計")
            report.append("-" * 40)
            report.append(f"総テスト数: {test_stats.get('total_tests', 0)}")
            report.append(f"成功: {test_stats.get('passed', 0)}")
            report.append(f"失敗: {test_stats.get('failed', 0)}")
            report.append(f"エラー: {test_stats.get('errors', 0)}")
            report.append(f"成功率: {test_stats.get('success_rate', 0):.1f}%")
            report.append("")

        # カバレッジ統計
        coverage_data = self.results.get("coverage_data", {})
        if coverage_data:
            report.append("📈 カバレッジ統計")
            report.append("-" * 40)

            for module, data in coverage_data.items():
                if module != "TOTAL":
                    coverage_icon = (
                        "✅"
                        if data["coverage"] >= 80
                        else "⚠️"
                        if data["coverage"] >= 60
                        else "❌"
                    )
                    report.append(
                        f"  {coverage_icon} {module}: {data['coverage']:.1f}% ({data['statements']}行)"
                    )

            if "TOTAL" in coverage_data:
                total = coverage_data["TOTAL"]
                total_icon = (
                    "✅"
                    if total["coverage"] >= 80
                    else "⚠️"
                    if total["coverage"] >= 60
                    else "❌"
                )
                report.append(
                    f"  {total_icon} 全体: {total['coverage']:.1f}% ({total['statements']}行)"
                )
            report.append("")

        # 総合評価と推奨事項
        report.append("🎯 総合評価と推奨事項")
        report.append("-" * 40)

        # 品質スコア
        quality_score = self.results.get("quality_score", "N/A")
        report.append(f"品質スコア: {quality_score}")

        # 推奨事項
        recommendations = self._generate_recommendations()
        if recommendations:
            report.append("\n推奨事項:")
            for recommendation in recommendations:
                report.append(f"  • {recommendation}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def _generate_recommendations(self) -> List[str]:
        """推奨事項を生成"""
        recommendations = []

        # カバレッジに基づく推奨事項
        coverage_data = self.results.get("coverage_data", {})
        total_coverage = coverage_data.get("TOTAL", {}).get("coverage", 0)

        if total_coverage < 50:
            recommendations.append(
                "🚨 カバレッジが50%未満です。テストの追加を最優先で実施してください"
            )
        elif total_coverage < 70:
            recommendations.append(
                "⚠️ カバレッジが70%未満です。テストの追加を検討してください"
            )
        elif total_coverage >= 90:
            recommendations.append(
                "✅ カバレッジは優秀です。現在のレベルを維持してください"
            )

        # ワークフロー成功率に基づく推奨事項
        workflow_stats = self.results.get("workflow_statistics", {})
        success_rates = workflow_stats.get("success_rates", {})

        for workflow_name, success_rate in success_rates.items():
            if success_rate < 70:
                recommendations.append(
                    f"🔧 ワークフロー '{workflow_name}' の成功率が低いです。設定を見直してください"
                )

        # セキュリティに基づく推奨事項
        security_metrics = self.results.get("security_metrics", {})
        if security_metrics and "error" not in security_metrics:
            total_issues = security_metrics.get("total_issues", 0)
            severity_counts = security_metrics.get("severity_counts", {})

            if severity_counts.get("HIGH", 0) > 0:
                recommendations.append(
                    "🚨 高重要度のセキュリティ問題があります。即座に対応してください"
                )
            elif total_issues > 10:
                recommendations.append(
                    "⚠️ セキュリティ問題が多数検出されています。定期的な対応を検討してください"
                )

        # パフォーマンスに基づく推奨事項
        performance_metrics = self.results.get("performance_metrics", {})
        if performance_metrics and "error" not in performance_metrics:
            avg_time = performance_metrics.get("average_execution_time", 0)
            if avg_time > 2.0:
                recommendations.append(
                    "⚡ テストの実行時間が長いです。パフォーマンス最適化を検討してください"
                )

        # システムリソースに基づく推奨事項
        system_metrics = self.results.get("system_metrics", {})
        if system_metrics:
            memory_percent = system_metrics.get("memory_percent", 0)
            if memory_percent > 80:
                recommendations.append(
                    "💾 メモリ使用率が高いです。リソース使用量の最適化を検討してください"
                )

        return recommendations

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

    def generate_integrated_visualization(self):
        """統合可視化を生成"""
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("matplotlibが利用できないため、可視化をスキップします")
            return

        self.logger.info("統合可視化を生成中...")

        try:
            # 大きなフィギュアを作成（3x3のサブプロット）
            fig = plt.figure(figsize=(18, 15))
            fig.suptitle(
                "Qt-Theme-Studio 統合品質メトリクス", fontsize=16, fontweight="bold"
            )

            # 1. カバレッジの棒グラフ
            ax1 = plt.subplot(3, 3, 1)
            coverage_data = self.results.get("coverage_data", {})
            if coverage_data:
                modules = [k for k in coverage_data.keys() if k != "TOTAL"]
                coverages = [coverage_data[m]["coverage"] for m in modules]

                bars = ax1.bar(modules, coverages, color="skyblue", edgecolor="navy")
                ax1.set_title("モジュール別カバレッジ", fontweight="bold")
                ax1.set_ylabel("カバレッジ (%)")
                ax1.tick_params(axis="x", rotation=45)
                ax1.set_ylim(0, 100)

                # カバレッジ値の表示
                for bar, coverage in zip(bars, coverages):
                    ax1.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 1,
                        f"{coverage:.1f}%",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                    )

            # 2. ワークフロー成功率
            ax2 = plt.subplot(3, 3, 2)
            workflow_stats = self.results.get("workflow_statistics", {})
            success_rates = workflow_stats.get("success_rates", {})

            if success_rates:
                workflows = list(success_rates.keys())
                rates = list(success_rates.values())

                colors = [
                    "green" if r >= 90 else "orange" if r >= 70 else "red"
                    for r in rates
                ]
                bars = ax2.bar(workflows, rates, color=colors, alpha=0.7)
                ax2.set_title("ワークフロー成功率", fontweight="bold")
                ax2.set_ylabel("成功率 (%)")
                ax2.tick_params(axis="x", rotation=45)
                ax2.set_ylim(0, 100)

                for bar, rate in zip(bars, rates):
                    ax2.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 1,
                        f"{rate:.1f}%",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                    )

            # 3. テスト結果の円グラフ
            ax3 = plt.subplot(3, 3, 3)
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
                    ax3.pie(
                        sizes,
                        labels=labels,
                        colors=colors,
                        autopct="%1.1f%%",
                        startangle=90,
                    )
                    ax3.set_title("テスト結果の分布", fontweight="bold")

            # 4. システムリソース使用率
            ax4 = plt.subplot(3, 3, 4)
            system_metrics = self.results.get("system_metrics", {})
            if system_metrics:
                resources = ["CPU", "メモリ", "ディスク"]
                usage = [
                    system_metrics.get("cpu_percent", 0),
                    system_metrics.get("memory_percent", 0),
                    system_metrics.get("disk_percent", 0),
                ]

                colors = [
                    "red" if u > 80 else "orange" if u > 60 else "green" for u in usage
                ]
                bars = ax4.bar(resources, usage, color=colors, alpha=0.7)
                ax4.set_title("システムリソース使用率", fontweight="bold")
                ax4.set_ylabel("使用率 (%)")
                ax4.set_ylim(0, 100)

                for bar, use in zip(bars, usage):
                    ax4.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 1,
                        f"{use:.1f}%",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                    )

            # 5. セキュリティ問題の分布
            ax5 = plt.subplot(3, 3, 5)
            security_metrics = self.results.get("security_metrics", {})
            if security_metrics and "error" not in security_metrics:
                severity_counts = security_metrics.get("severity_counts", {})
                severities = list(severity_counts.keys())
                counts = list(severity_counts.values())

                if sum(counts) > 0:
                    colors = {"HIGH": "red", "MEDIUM": "orange", "LOW": "yellow"}
                    bar_colors = [colors.get(s, "gray") for s in severities]

                    bars = ax5.bar(severities, counts, color=bar_colors, alpha=0.7)
                    ax5.set_title("セキュリティ問題の分布", fontweight="bold")
                    ax5.set_ylabel("問題数")

                    for bar, count in zip(bars, counts):
                        ax5.text(
                            bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 0.1,
                            str(count),
                            ha="center",
                            va="bottom",
                            fontsize=8,
                        )

            # 6. パフォーマンス履歴（時系列）
            ax6 = plt.subplot(3, 3, 6)
            if len(self.metrics_history) > 1:
                timestamps = []
                cpu_usage = []
                memory_usage = []

                for entry in self.metrics_history[-20:]:  # 最新20件
                    try:
                        timestamp = datetime.fromisoformat(entry["timestamp"])
                        timestamps.append(timestamp)

                        sys_metrics = entry.get("system_metrics", {})
                        cpu_usage.append(sys_metrics.get("cpu_percent", 0))
                        memory_usage.append(sys_metrics.get("memory_percent", 0))
                    except Exception:
                        continue

                if timestamps:
                    ax6.plot(
                        timestamps,
                        cpu_usage,
                        label="CPU",
                        color="blue",
                        marker="o",
                        markersize=3,
                    )
                    ax6.plot(
                        timestamps,
                        memory_usage,
                        label="メモリ",
                        color="red",
                        marker="s",
                        markersize=3,
                    )
                    ax6.set_title("リソース使用率の推移", fontweight="bold")
                    ax6.set_ylabel("使用率 (%)")
                    ax6.legend()
                    ax6.tick_params(axis="x", rotation=45)

                    # 時間軸のフォーマット
                    ax6.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

            # 7. 品質スコア表示
            ax7 = plt.subplot(3, 3, 7)
            quality_score = self.results.get("quality_score", "N/A")

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

            ax7.text(
                0.5,
                0.5,
                f"品質スコア\n{quality_score}",
                ha="center",
                va="center",
                fontsize=20,
                fontweight="bold",
                transform=ax7.transAxes,
                color=color,
            )
            ax7.set_title("総合品質評価", fontweight="bold")
            ax7.axis("off")

            # 8. ファイル統計
            ax8 = plt.subplot(3, 3, 8)
            file_stats = self.results.get("file_statistics", {})
            if file_stats:
                categories = ["ソース", "テスト"]
                lines = [
                    file_stats.get("source_lines", 0),
                    file_stats.get("test_lines", 0),
                ]
                colors = ["lightblue", "lightgreen"]

                bars = ax8.bar(categories, lines, color=colors, edgecolor="navy")
                ax8.set_title("コード行数の比較", fontweight="bold")
                ax8.set_ylabel("行数")

                for bar, line_count in zip(bars, lines):
                    ax8.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(lines) * 0.01,
                        f"{line_count:,}",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                    )

            # 9. 統合メトリクス概要
            ax9 = plt.subplot(3, 3, 9)

            # 主要メトリクスのサマリー
            summary_text = []

            # カバレッジ
            total_coverage = coverage_data.get("TOTAL", {}).get("coverage", 0)
            summary_text.append(f"カバレッジ: {total_coverage:.1f}%")

            # テスト成功率
            test_success_rate = test_stats.get("success_rate", 0)
            summary_text.append(f"テスト成功率: {test_success_rate:.1f}%")

            # セキュリティスコア
            security_score = (
                security_metrics.get("security_score", 0) if security_metrics else 0
            )
            summary_text.append(f"セキュリティ: {security_score:.1f}/10")

            # ワークフロー数
            total_workflows = workflow_stats.get("total_workflows", 0)
            enabled_workflows = workflow_stats.get("enabled_workflows", 0)
            summary_text.append(f"ワークフロー: {enabled_workflows}/{total_workflows}")

            ax9.text(
                0.1,
                0.9,
                "\n".join(summary_text),
                transform=ax9.transAxes,
                fontsize=12,
                verticalalignment="top",
                fontfamily="monospace",
            )
            ax9.set_title("メトリクス概要", fontweight="bold")
            ax9.axis("off")

            plt.tight_layout()

            # 保存
            output_file = self.project_root / "integrated_quality_dashboard.png"
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            self.logger.info(f"統合可視化を保存しました: {output_file}")

            # 表示
            plt.show()

        except Exception as e:
            self.logger.error(f"統合可視化の生成に失敗: {e}")

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

    def run_integrated_dashboard(
        self, enable_monitoring: bool = False, monitoring_interval: int = 60
    ):
        """統合ダッシュボードを実行

        Args:
            enable_monitoring: リアルタイム監視を有効にするか
            monitoring_interval: 監視間隔（秒）
        """
        self.logger.info(
            "Qt-Theme-Studio 統合品質メトリクスダッシュボードを開始します..."
        )
        print("🚀 Qt-Theme-Studio 統合品質メトリクスダッシュボードを開始します...")
        print("=" * 80)

        try:
            # 全メトリクスを収集
            self.logger.info("全メトリクスを収集中...")

            self.results["test_statistics"] = self.collect_test_statistics()
            self.results["coverage_data"] = self.collect_coverage_data()
            self.results["file_statistics"] = self.collect_file_statistics()
            self.results["workflow_statistics"] = self.collect_workflow_statistics()
            self.results["system_metrics"] = self.collect_system_metrics()
            self.results["security_metrics"] = self.collect_security_metrics()
            self.results["performance_metrics"] = self.collect_performance_metrics()

            # 品質スコアの計算
            total_coverage = (
                self.results["coverage_data"].get("TOTAL", {}).get("coverage", 0)
            )
            test_count = self.results["test_statistics"].get("total_tests", 0)
            success_rate = self.results["test_statistics"].get("success_rate", 0)

            self.results["quality_score"] = self.calculate_quality_score(
                total_coverage, test_count, success_rate
            )

            # 統合レポート生成
            integrated_report = self.generate_integrated_report()
            print(integrated_report)

            # ファイル保存
            self.save_integrated_json_report()

            # 統合可視化
            self.generate_integrated_visualization()

            # メトリクス履歴に追加
            current_metrics = {
                "timestamp": datetime.now().isoformat(),
                "results": self.results,
            }
            self.metrics_history.append(current_metrics)
            self._save_metrics_history()

            # リアルタイム監視を開始（オプション）
            if enable_monitoring:
                self.start_realtime_monitoring(monitoring_interval)
                print(
                    f"\n📊 リアルタイム監視を開始しました（間隔: {monitoring_interval}秒）"
                )
                print("監視を停止するには Ctrl+C を押してください")

                try:
                    while self.monitoring_active:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n監視を停止中...")
                    self.stop_realtime_monitoring()

            print("\n🎉 統合品質メトリクスダッシュボードが完了しました！")
            print("📁 生成されたファイル:")
            print("   - integrated_quality_report.json: 統合詳細データ")
            print("   - logs/metrics_history.json: メトリクス履歴")
            if MATPLOTLIB_AVAILABLE:
                print("   - integrated_quality_dashboard.png: 統合可視化グラフ")

        except Exception as e:
            self.logger.error(f"統合ダッシュボードの実行中にエラーが発生: {e}")
            print(f"❌ エラーが発生しました: {e}")
            raise

    def save_integrated_json_report(self):
        """統合JSONレポートを保存"""
        try:
            output_file = self.project_root / "integrated_quality_report.json"

            # タイムスタンプと追加情報を含む完全なレポート
            full_report = {
                "generated_at": datetime.now().isoformat(),
                "dashboard_version": "2.0.0",
                "project_root": str(self.project_root),
                "workflow_engine_available": WORKFLOW_AVAILABLE,
                "matplotlib_available": MATPLOTLIB_AVAILABLE,
                "results": self.results,
                "metrics_history_count": len(self.metrics_history),
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(full_report, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(f"統合JSONレポートを保存しました: {output_file}")

        except Exception as e:
            self.logger.error(f"統合JSONレポートの保存に失敗: {e}")

    def run(self):
        """従来の品質ダッシュボードを実行（後方互換性のため）"""
        self.logger.info("従来の品質メトリクスダッシュボードを実行中...")
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
    import argparse

    parser = argparse.ArgumentParser(
        description="Qt-Theme-Studio 統合品質メトリクスダッシュボード"
    )
    parser.add_argument(
        "--integrated", action="store_true", help="統合ダッシュボードを実行"
    )
    parser.add_argument(
        "--monitoring", action="store_true", help="リアルタイム監視を有効化"
    )
    parser.add_argument("--interval", type=int, default=60, help="監視間隔（秒）")
    parser.add_argument("--config", type=str, help="設定ファイルのパス")

    args = parser.parse_args()

    try:
        dashboard = IntegratedQualityDashboard(config_path=args.config)

        if args.integrated:
            dashboard.run_integrated_dashboard(
                enable_monitoring=args.monitoring, monitoring_interval=args.interval
            )
        else:
            dashboard.run()

    except KeyboardInterrupt:
        print("\n👋 ダッシュボードを終了します")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1

    return 0


# 後方互換性のためのエイリアス
QualityDashboard = IntegratedQualityDashboard


if __name__ == "__main__":
    main()
