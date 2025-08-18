#!/usr/bin/env python3
"""
パフォーマンス回帰検出システム

このモジュールは、アプリケーションのパフォーマンス回帰を自動検出し、
アラートを生成する機能を提供します。
"""

import json
import logging
import statistics
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import subprocess
import sys

# ログ設定
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """ベンチマーク結果データクラス"""
    name: str
    timestamp: datetime
    mean_time: float
    std_dev: float
    min_time: float
    max_time: float
    iterations: int
    commit_hash: Optional[str] = None
    branch: Optional[str] = None


@dataclass
class RegressionAlert:
    """回帰アラートデータクラス"""
    benchmark_name: str
    current_result: BenchmarkResult
    baseline_result: BenchmarkResult
    regression_percentage: float
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    timestamp: datetime
    analysis: str


class PerformanceMonitor:
    """パフォーマンス監視・回帰検出システム"""

    def __init__(self, data_dir: str = "logs/performance"):
        """
        パフォーマンス監視システムを初期化

        Args:
            data_dir: パフォーマンスデータ保存ディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_file = self.data_dir / "benchmark_results.json"
        self.alerts_file = self.data_dir / "regression_alerts.json"
        
        # 回帰検出の閾値設定
        self.thresholds = {
            'LOW': 5.0,      # 5%以上の性能低下
            'MEDIUM': 15.0,  # 15%以上の性能低下
            'HIGH': 30.0,    # 30%以上の性能低下
            'CRITICAL': 50.0 # 50%以上の性能低下
        }
        
        # 統計的有意性の設定
        self.min_samples = 3  # 最小サンプル数
        self.confidence_level = 0.95  # 信頼度
        
        logger.info("パフォーマンス監視システムを初期化しました")

    def run_benchmarks(self, test_pattern: str = "test_*benchmark*") -> List[BenchmarkResult]:
        """
        ベンチマークテストを実行し、結果を収集

        Args:
            test_pattern: 実行するテストパターン

        Returns:
            ベンチマーク結果のリスト
        """
        logger.info(f"ベンチマークテストを実行中: {test_pattern}")
        
        try:
            # pytest-benchmarkでベンチマークを実行
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/test_performance_benchmarks.py",
                "-k", test_pattern,
                "--benchmark-json=benchmark_results.json",
                "--benchmark-only",
                "-v"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分でタイムアウト
            )
            
            if result.returncode != 0:
                logger.error(f"ベンチマーク実行に失敗: {result.stderr}")
                return []
            
            # 結果ファイルを読み込み
            benchmark_file = Path("benchmark_results.json")
            if not benchmark_file.exists():
                logger.warning("ベンチマーク結果ファイルが見つかりません")
                return []
            
            with open(benchmark_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 結果を解析してBenchmarkResultオブジェクトに変換
            results = []
            commit_hash = self._get_current_commit_hash()
            branch = self._get_current_branch()
            
            for benchmark in data.get('benchmarks', []):
                result = BenchmarkResult(
                    name=benchmark['name'],
                    timestamp=datetime.now(),
                    mean_time=benchmark['stats']['mean'],
                    std_dev=benchmark['stats']['stddev'],
                    min_time=benchmark['stats']['min'],
                    max_time=benchmark['stats']['max'],
                    iterations=benchmark['stats']['rounds'],
                    commit_hash=commit_hash,
                    branch=branch
                )
                results.append(result)
            
            # 結果を保存
            self._save_results(results)
            
            # 一時ファイルを削除
            benchmark_file.unlink(missing_ok=True)
            
            logger.info(f"{len(results)}個のベンチマーク結果を収集しました")
            return results
            
        except subprocess.TimeoutExpired:
            logger.error("ベンチマーク実行がタイムアウトしました")
            return []
        except Exception as e:
            logger.error(f"ベンチマーク実行中にエラーが発生: {e}")
            return []

    def run_gui_responsiveness_test(self, widget=None, scenarios=None) -> Dict[str, Any]:
        """
        GUI応答性テストを実行

        Args:
            widget: テスト対象のウィジェット
            scenarios: テストシナリオのリスト

        Returns:
            GUI応答性テスト結果
        """
        logger.info("GUI応答性テストを実行中")
        
        try:
            from scripts.gui_responsiveness_monitor import ResponsivenessMonitor, create_default_test_scenarios
            
            # GUI応答性監視システムを初期化
            gui_monitor = ResponsivenessMonitor(str(self.data_dir / "gui"))
            
            # デフォルトシナリオを使用（ウィジェットが指定されていない場合）
            if scenarios is None:
                scenarios = create_default_test_scenarios()
            
            if not scenarios:
                logger.warning("GUI応答性テストシナリオが利用できません")
                return {
                    'success': False,
                    'error': 'テストシナリオが利用できません',
                    'metrics': None
                }
            
            # 応答性テストを実行
            metrics = gui_monitor.run_responsiveness_test(widget, scenarios)
            
            # 結果をログに記録
            logger.info(f"GUI応答性テスト完了:")
            logger.info(f"  総インタラクション数: {metrics.total_interactions}")
            logger.info(f"  成功インタラクション数: {metrics.successful_interactions}")
            logger.info(f"  平均応答時間: {metrics.average_response_time:.4f}秒")
            logger.info(f"  95パーセンタイル: {metrics.p95_response_time:.4f}秒")
            
            return {
                'success': True,
                'metrics': metrics,
                'summary': {
                    'total_interactions': metrics.total_interactions,
                    'successful_interactions': metrics.successful_interactions,
                    'failed_interactions': metrics.failed_interactions,
                    'average_response_time': metrics.average_response_time,
                    'p95_response_time': metrics.p95_response_time,
                    'success_rate': (metrics.successful_interactions / metrics.total_interactions * 100) if metrics.total_interactions > 0 else 0
                }
            }
            
        except ImportError as e:
            logger.error(f"GUI応答性監視システムが利用できません: {e}")
            return {
                'success': False,
                'error': f'GUI応答性監視システムが利用できません: {e}',
                'metrics': None
            }
        except Exception as e:
            logger.error(f"GUI応答性テスト実行中にエラーが発生: {e}")
            return {
                'success': False,
                'error': str(e),
                'metrics': None
            }

    def run_memory_profiling_test(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """
        メモリプロファイリングテストを実行

        Args:
            duration_minutes: プロファイリング期間（分）

        Returns:
            メモリプロファイリング結果
        """
        logger.info(f"メモリプロファイリングテストを実行中（期間: {duration_minutes}分）")
        
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from scripts.memory_profiler import MemoryProfiler
            
            # メモリプロファイラーを初期化
            memory_profiler = MemoryProfiler(str(self.data_dir / "memory"))
            
            # 初期スナップショット
            initial_snapshot = memory_profiler.take_snapshot("プロファイリングテスト開始")
            
            # 短時間の監視を実行
            memory_profiler.start_monitoring(interval=1.0)
            
            # 指定時間待機
            import time
            time.sleep(duration_minutes * 60)
            
            # 監視停止
            memory_profiler.stop_monitoring()
            
            # 最終スナップショット
            final_snapshot = memory_profiler.take_snapshot("プロファイリングテスト終了")
            
            # メモリリーク検出
            leaks = memory_profiler.detect_memory_leaks(duration_minutes=duration_minutes)
            
            # レポート生成
            report = memory_profiler.generate_memory_report(hours=1)
            
            # 結果をログに記録
            memory_diff = final_snapshot.process_memory_mb - initial_snapshot.process_memory_mb
            logger.info(f"メモリプロファイリングテスト完了:")
            logger.info(f"  メモリ使用量変化: {memory_diff:+.1f}MB")
            logger.info(f"  検出されたリーク数: {len(leaks)}")
            logger.info(f"  スナップショット数: {len(memory_profiler.snapshots)}")
            
            # クリーンアップ
            memory_profiler.cleanup()
            
            return {
                'success': True,
                'initial_memory_mb': initial_snapshot.process_memory_mb,
                'final_memory_mb': final_snapshot.process_memory_mb,
                'memory_change_mb': memory_diff,
                'leaks_detected': len(leaks),
                'critical_leaks': len([l for l in leaks if l.severity == 'CRITICAL']),
                'snapshots_count': len(memory_profiler.snapshots),
                'report': report,
                'summary': {
                    'duration_minutes': duration_minutes,
                    'memory_stable': abs(memory_diff) < 10.0,  # 10MB以下の変化は安定とみなす
                    'no_critical_leaks': len([l for l in leaks if l.severity == 'CRITICAL']) == 0,
                    'monitoring_successful': len(memory_profiler.snapshots) > 0
                }
            }
            
        except ImportError as e:
            logger.error(f"メモリプロファイラーが利用できません: {e}")
            return {
                'success': False,
                'error': f'メモリプロファイラーが利用できません: {e}',
                'summary': None
            }
        except Exception as e:
            logger.error(f"メモリプロファイリングテスト実行中にエラーが発生: {e}")
            return {
                'success': False,
                'error': str(e),
                'summary': None
            }

    def detect_regressions(self, current_results: List[BenchmarkResult]) -> List[RegressionAlert]:
        """
        パフォーマンス回帰を検出

        Args:
            current_results: 現在のベンチマーク結果

        Returns:
            検出された回帰アラートのリスト
        """
        logger.info("パフォーマンス回帰の検出を開始")
        
        alerts = []
        historical_results = self._load_historical_results()
        
        for current in current_results:
            baseline = self._get_baseline_result(current.name, historical_results)
            
            if baseline is None:
                logger.info(f"ベースライン結果が見つかりません: {current.name}")
                continue
            
            # 回帰を検出
            regression_percentage = self._calculate_regression_percentage(
                baseline.mean_time, current.mean_time
            )
            
            if regression_percentage >= self.thresholds['LOW']:
                severity = self._determine_severity(regression_percentage)
                
                # 'NONE'の場合はアラートを生成しない
                if severity != 'NONE':
                    analysis = self._analyze_regression(current, baseline)
                    
                    alert = RegressionAlert(
                        benchmark_name=current.name,
                        current_result=current,
                        baseline_result=baseline,
                        regression_percentage=regression_percentage,
                        severity=severity,
                        timestamp=datetime.now(),
                        analysis=analysis
                    )
                    
                    alerts.append(alert)
                    logger.warning(
                        f"パフォーマンス回帰を検出: {current.name} "
                        f"({regression_percentage:.1f}% 低下, {severity})"
                    )
        
        if alerts:
            self._save_alerts(alerts)
        
        logger.info(f"{len(alerts)}個の回帰アラートを生成しました")
        return alerts

    def generate_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """
        パフォーマンスレポートを生成

        Args:
            days: レポート対象期間（日数）

        Returns:
            パフォーマンスレポート
        """
        logger.info(f"過去{days}日間のパフォーマンスレポートを生成中")
        
        cutoff_date = datetime.now() - timedelta(days=days)
        historical_results = self._load_historical_results()
        
        # 期間内の結果をフィルタリング
        recent_results = [
            r for r in historical_results
            if r.timestamp >= cutoff_date
        ]
        
        # ベンチマーク別の統計を計算
        benchmark_stats = {}
        for result in recent_results:
            if result.name not in benchmark_stats:
                benchmark_stats[result.name] = []
            benchmark_stats[result.name].append(result.mean_time)
        
        # 統計情報を計算
        report = {
            'period': f"{days}日間",
            'total_benchmarks': len(recent_results),
            'unique_benchmarks': len(benchmark_stats),
            'benchmarks': {}
        }
        
        for name, times in benchmark_stats.items():
            if len(times) >= 2:
                trend = self._calculate_trend(times)
                report['benchmarks'][name] = {
                    'samples': len(times),
                    'mean_time': statistics.mean(times),
                    'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
                    'min_time': min(times),
                    'max_time': max(times),
                    'trend': trend
                }
        
        # 最近のアラートを含める
        recent_alerts = self._load_recent_alerts(days)
        report['alerts'] = len(recent_alerts)
        report['critical_alerts'] = len([a for a in recent_alerts if a.severity == 'CRITICAL'])
        
        logger.info("パフォーマンスレポートを生成しました")
        return report

    def _save_results(self, results: List[BenchmarkResult]) -> None:
        """ベンチマーク結果を保存"""
        historical_results = self._load_historical_results()
        historical_results.extend(results)
        
        # 古い結果を削除（90日以上前）
        cutoff_date = datetime.now() - timedelta(days=90)
        historical_results = [
            r for r in historical_results
            if r.timestamp >= cutoff_date
        ]
        
        # JSON形式で保存
        data = [asdict(r) for r in historical_results]
        for item in data:
            item['timestamp'] = item['timestamp'].isoformat()
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_historical_results(self) -> List[BenchmarkResult]:
        """過去のベンチマーク結果を読み込み"""
        if not self.results_file.exists():
            return []
        
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            results = []
            for item in data:
                item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                results.append(BenchmarkResult(**item))
            
            return results
        except Exception as e:
            logger.error(f"過去の結果読み込みに失敗: {e}")
            return []

    def _get_baseline_result(self, benchmark_name: str, 
                           historical_results: List[BenchmarkResult]) -> Optional[BenchmarkResult]:
        """ベースライン結果を取得"""
        # 同じベンチマークの過去の結果を取得
        same_benchmark = [
            r for r in historical_results
            if r.name == benchmark_name
        ]
        
        if len(same_benchmark) < self.min_samples:
            return None
        
        # 最新の安定した結果を使用（過去7日間の平均）
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_results = [
            r for r in same_benchmark
            if r.timestamp >= cutoff_date
        ]
        
        if len(recent_results) < self.min_samples:
            # 過去7日間にデータが不足している場合は、最新の結果を使用
            sorted_results = sorted(same_benchmark, key=lambda x: x.timestamp, reverse=True)
            recent_results = sorted_results[:self.min_samples]
        
        if len(recent_results) < self.min_samples:
            return None
        
        # 平均値を計算してベースラインとする
        mean_time = statistics.mean([r.mean_time for r in recent_results])
        std_dev = statistics.stdev([r.mean_time for r in recent_results]) if len(recent_results) > 1 else 0
        
        # 代表的な結果を作成
        latest = recent_results[0]  # 最新の結果
        return BenchmarkResult(
            name=benchmark_name,
            timestamp=latest.timestamp,
            mean_time=mean_time,
            std_dev=std_dev,
            min_time=min([r.min_time for r in recent_results]),
            max_time=max([r.max_time for r in recent_results]),
            iterations=latest.iterations,
            commit_hash=latest.commit_hash,
            branch=latest.branch
        )

    def _calculate_regression_percentage(self, baseline: float, current: float) -> float:
        """回帰率を計算"""
        if baseline == 0:
            return 0.0
        return ((current - baseline) / baseline) * 100

    def _determine_severity(self, regression_percentage: float) -> str:
        """回帰の重要度を判定"""
        if regression_percentage >= self.thresholds['CRITICAL']:
            return 'CRITICAL'
        elif regression_percentage >= self.thresholds['HIGH']:
            return 'HIGH'
        elif regression_percentage >= self.thresholds['MEDIUM']:
            return 'MEDIUM'
        elif regression_percentage >= self.thresholds['LOW']:
            return 'LOW'
        else:
            # 閾値未満の場合は回帰として扱わない
            return 'NONE'

    def _analyze_regression(self, current: BenchmarkResult, baseline: BenchmarkResult) -> str:
        """回帰の原因分析"""
        analysis_parts = []
        
        # 実行時間の変化
        time_change = current.mean_time - baseline.mean_time
        analysis_parts.append(f"実行時間が{time_change:.3f}秒増加")
        
        # 標準偏差の変化
        if current.std_dev > baseline.std_dev * 1.5:
            analysis_parts.append("実行時間のばらつきが大幅に増加")
        
        # 最大実行時間の変化
        if current.max_time > baseline.max_time * 1.3:
            analysis_parts.append("最大実行時間が大幅に増加")
        
        # コミット情報
        if current.commit_hash and baseline.commit_hash:
            if current.commit_hash != baseline.commit_hash:
                analysis_parts.append(f"コミット変更: {baseline.commit_hash[:8]} → {current.commit_hash[:8]}")
        
        return "、".join(analysis_parts)

    def _calculate_trend(self, times: List[float]) -> str:
        """パフォーマンストレンドを計算"""
        if len(times) < 2:
            return "不明"
        
        # 線形回帰の傾きを計算
        n = len(times)
        x = list(range(n))
        
        sum_x = sum(x)
        sum_y = sum(times)
        sum_xy = sum(x[i] * times[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.001:
            return "悪化"
        elif slope < -0.001:
            return "改善"
        else:
            return "安定"

    def _save_alerts(self, alerts: List[RegressionAlert]) -> None:
        """アラートを保存"""
        historical_alerts = self._load_all_alerts()
        historical_alerts.extend(alerts)
        
        # 古いアラートを削除（30日以上前）
        cutoff_date = datetime.now() - timedelta(days=30)
        historical_alerts = [
            a for a in historical_alerts
            if a.timestamp >= cutoff_date
        ]
        
        # JSON形式で保存
        data = []
        for alert in historical_alerts:
            alert_dict = asdict(alert)
            alert_dict['timestamp'] = alert_dict['timestamp'].isoformat()
            alert_dict['current_result']['timestamp'] = alert_dict['current_result']['timestamp'].isoformat()
            alert_dict['baseline_result']['timestamp'] = alert_dict['baseline_result']['timestamp'].isoformat()
            data.append(alert_dict)
        
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_all_alerts(self) -> List[RegressionAlert]:
        """すべてのアラートを読み込み"""
        if not self.alerts_file.exists():
            return []
        
        try:
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            alerts = []
            for item in data:
                item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                item['current_result']['timestamp'] = datetime.fromisoformat(item['current_result']['timestamp'])
                item['baseline_result']['timestamp'] = datetime.fromisoformat(item['baseline_result']['timestamp'])
                
                current_result = BenchmarkResult(**item['current_result'])
                baseline_result = BenchmarkResult(**item['baseline_result'])
                
                alert = RegressionAlert(
                    benchmark_name=item['benchmark_name'],
                    current_result=current_result,
                    baseline_result=baseline_result,
                    regression_percentage=item['regression_percentage'],
                    severity=item['severity'],
                    timestamp=item['timestamp'],
                    analysis=item['analysis']
                )
                alerts.append(alert)
            
            return alerts
        except Exception as e:
            logger.error(f"アラート読み込みに失敗: {e}")
            return []

    def _load_recent_alerts(self, days: int) -> List[RegressionAlert]:
        """最近のアラートを読み込み"""
        all_alerts = self._load_all_alerts()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return [
            alert for alert in all_alerts
            if alert.timestamp >= cutoff_date
        ]

    def _get_current_commit_hash(self) -> Optional[str]:
        """現在のコミットハッシュを取得"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _get_current_branch(self) -> Optional[str]:
        """現在のブランチ名を取得"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="パフォーマンス回帰検出システム")
    parser.add_argument(
        '--run-benchmarks',
        action='store_true',
        help='ベンチマークテストを実行'
    )
    parser.add_argument(
        '--detect-regressions',
        action='store_true',
        help='回帰検出のみ実行'
    )
    parser.add_argument(
        '--generate-report',
        type=int,
        metavar='DAYS',
        help='指定日数のパフォーマンスレポートを生成'
    )
    parser.add_argument(
        '--test-pattern',
        default='test_*benchmark*',
        help='実行するテストパターン'
    )
    parser.add_argument(
        '--data-dir',
        default='logs/performance',
        help='データ保存ディレクトリ'
    )
    parser.add_argument(
        '--memory-profile',
        type=int,
        metavar='MINUTES',
        help='指定分数間メモリプロファイリングを実行'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='詳細ログを出力'
    )
    
    args = parser.parse_args()
    
    # ログ設定
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/performance_monitor.log', encoding='utf-8')
        ]
    )
    
    monitor = PerformanceMonitor(args.data_dir)
    
    try:
        if args.run_benchmarks:
            # ベンチマーク実行と回帰検出
            results = monitor.run_benchmarks(args.test_pattern)
            if results:
                alerts = monitor.detect_regressions(results)
                
                if alerts:
                    print(f"\n⚠️  {len(alerts)}個のパフォーマンス回帰を検出しました:")
                    for alert in alerts:
                        print(f"  - {alert.benchmark_name}: {alert.regression_percentage:.1f}% 低下 ({alert.severity})")
                        print(f"    分析: {alert.analysis}")
                else:
                    print("✅ パフォーマンス回帰は検出されませんでした")
            else:
                print("❌ ベンチマーク結果を取得できませんでした")
        
        elif args.detect_regressions:
            # 既存結果から回帰検出のみ
            historical_results = monitor._load_historical_results()
            if historical_results:
                # 最新の結果を使用
                latest_results = {}
                for result in historical_results:
                    if result.name not in latest_results or result.timestamp > latest_results[result.name].timestamp:
                        latest_results[result.name] = result
                
                alerts = monitor.detect_regressions(list(latest_results.values()))
                
                if alerts:
                    print(f"\n⚠️  {len(alerts)}個のパフォーマンス回帰を検出しました:")
                    for alert in alerts:
                        print(f"  - {alert.benchmark_name}: {alert.regression_percentage:.1f}% 低下 ({alert.severity})")
                else:
                    print("✅ パフォーマンス回帰は検出されませんでした")
            else:
                print("❌ 過去のベンチマーク結果が見つかりません")
        
        elif args.memory_profile:
            # メモリプロファイリング実行
            memory_result = monitor.run_memory_profiling_test(duration_minutes=args.memory_profile)
            
            if memory_result['success']:
                print(f"\n🧠 メモリプロファイリング結果 ({args.memory_profile}分間)")
                print(f"初期メモリ使用量: {memory_result['initial_memory_mb']:.1f}MB")
                print(f"最終メモリ使用量: {memory_result['final_memory_mb']:.1f}MB")
                print(f"メモリ変化: {memory_result['memory_change_mb']:+.1f}MB")
                print(f"検出されたリーク数: {memory_result['leaks_detected']}")
                print(f"スナップショット数: {memory_result['snapshots_count']}")
                
                if memory_result['critical_leaks'] > 0:
                    print(f"\n⚠️ 重要なメモリリーク: {memory_result['critical_leaks']}個")
                    sys.exit(1)
                
                summary = memory_result['summary']
                if summary['memory_stable'] and summary['no_critical_leaks']:
                    print("\n✅ メモリ使用量は安定しています")
                else:
                    print("\n⚠️ メモリ使用量に問題が検出されました")
                    if not summary['memory_stable']:
                        print(f"  - メモリ使用量が不安定: {memory_result['memory_change_mb']:+.1f}MB")
                    if not summary['no_critical_leaks']:
                        print(f"  - 重要なメモリリークが検出: {memory_result['critical_leaks']}個")
            else:
                print(f"❌ メモリプロファイリングに失敗: {memory_result['error']}")
                sys.exit(1)
        
        elif args.generate_report is not None:
            # レポート生成
            report = monitor.generate_performance_report(args.generate_report)
            
            print(f"\n📊 パフォーマンスレポート ({report['period']})")
            print(f"総ベンチマーク数: {report['total_benchmarks']}")
            print(f"ユニークベンチマーク数: {report['unique_benchmarks']}")
            print(f"アラート数: {report['alerts']} (重要: {report['critical_alerts']})")
            
            if report['benchmarks']:
                print("\nベンチマーク詳細:")
                for name, stats in report['benchmarks'].items():
                    trend_emoji = {"改善": "📈", "悪化": "📉", "安定": "➡️", "不明": "❓"}
                    print(f"  {name}:")
                    print(f"    平均実行時間: {stats['mean_time']:.3f}秒")
                    print(f"    トレンド: {trend_emoji.get(stats['trend'], '❓')} {stats['trend']}")
                    print(f"    サンプル数: {stats['samples']}")
            
            # GUI応答性レポートも生成
            try:
                gui_result = monitor.run_gui_responsiveness_test()
                if gui_result['success']:
                    print(f"\n🖱️ GUI応答性テスト結果:")
                    summary = gui_result['summary']
                    print(f"総インタラクション数: {summary['total_interactions']}")
                    print(f"成功率: {summary['success_rate']:.1f}%")
                    print(f"平均応答時間: {summary['average_response_time']:.4f}秒")
                    print(f"95パーセンタイル: {summary['p95_response_time']:.4f}秒")
                else:
                    print(f"\n⚠️ GUI応答性テストをスキップ: {gui_result['error']}")
            except Exception as e:
                print(f"\n⚠️ GUI応答性テストでエラー: {e}")
            
            # メモリプロファイリングレポートも生成
            try:
                memory_result = monitor.run_memory_profiling_test(duration_minutes=1)
                if memory_result['success']:
                    print(f"\n🧠 メモリプロファイリング結果:")
                    print(f"初期メモリ使用量: {memory_result['initial_memory_mb']:.1f}MB")
                    print(f"最終メモリ使用量: {memory_result['final_memory_mb']:.1f}MB")
                    print(f"メモリ変化: {memory_result['memory_change_mb']:+.1f}MB")
                    print(f"検出されたリーク数: {memory_result['leaks_detected']}")
                    if memory_result['critical_leaks'] > 0:
                        print(f"⚠️ 重要なリーク: {memory_result['critical_leaks']}個")
                    
                    summary = memory_result['summary']
                    if summary['memory_stable'] and summary['no_critical_leaks']:
                        print("✅ メモリ使用量は安定しています")
                    else:
                        print("⚠️ メモリ使用量に問題が検出されました")
                else:
                    print(f"\n⚠️ メモリプロファイリングをスキップ: {memory_result['error']}")
            except Exception as e:
                print(f"\n⚠️ メモリプロファイリングでエラー: {e}")
        
        else:
            # デフォルト: ベンチマーク実行
            results = monitor.run_benchmarks(args.test_pattern)
            if results:
                alerts = monitor.detect_regressions(results)
                
                if alerts:
                    print(f"\n⚠️  {len(alerts)}個のパフォーマンス回帰を検出しました:")
                    for alert in alerts:
                        print(f"  - {alert.benchmark_name}: {alert.regression_percentage:.1f}% 低下 ({alert.severity})")
                        print(f"    分析: {alert.analysis}")
                    
                    # 重要なアラートがある場合は終了コード1で終了
                    critical_alerts = [a for a in alerts if a.severity in ['HIGH', 'CRITICAL']]
                    if critical_alerts:
                        sys.exit(1)
                else:
                    print("✅ パフォーマンス回帰は検出されませんでした")
            else:
                print("❌ ベンチマーク結果を取得できませんでした")
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラーが発生: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()