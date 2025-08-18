#!/usr/bin/env python3
"""
メモリプロファイリング機能

このモジュールは、アプリケーションのメモリ使用量を監視し、
メモリリークを検出し、詳細なプロファイリングレポートを生成します。
"""

import gc
import json
import logging
import os
import psutil
import sys
import threading
import time
import tracemalloc
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
import subprocess

# ログ設定
logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """メモリスナップショットデータクラス"""
    timestamp: datetime
    process_memory_mb: float
    system_memory_percent: float
    tracemalloc_current_mb: float
    tracemalloc_peak_mb: float
    gc_objects_count: int
    thread_count: int
    file_descriptors: int
    context: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class MemoryLeak:
    """メモリリーク検出結果"""
    start_snapshot: MemorySnapshot
    end_snapshot: MemorySnapshot
    leak_rate_mb_per_sec: float
    total_leaked_mb: float
    duration_seconds: float
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    analysis: str
    top_allocations: List[Dict[str, Any]]


@dataclass
class MemoryThresholds:
    """メモリ使用量閾値設定"""
    process_memory_mb: float = 500.0  # プロセスメモリ使用量（MB）
    system_memory_percent: float = 80.0  # システムメモリ使用率（%）
    leak_rate_mb_per_sec: float = 1.0  # リーク率（MB/秒）
    gc_objects_growth_rate: float = 1000.0  # GCオブジェクト増加率（個/秒）


class MemoryProfiler:
    """メモリプロファイリングシステム"""

    def __init__(self, data_dir: str = "logs/performance/memory"):
        """
        メモリプロファイラーを初期化

        Args:
            data_dir: データ保存ディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.snapshots_file = self.data_dir / "memory_snapshots.json"
        self.leaks_file = self.data_dir / "memory_leaks.json"
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # プロセス情報
        self.process = psutil.Process()
        
        # 監視設定
        self.thresholds = MemoryThresholds()
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = 5.0  # 5秒間隔
        
        # スナップショット履歴
        self.snapshots: List[MemorySnapshot] = []
        self.max_snapshots = 1000  # 最大保持スナップショット数
        
        # tracemalloc初期化
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            logger.info("tracemalloc監視を開始しました")
        
        logger.info("メモリプロファイラーを初期化しました")

    def take_snapshot(self, context: str = "") -> MemorySnapshot:
        """
        現在のメモリ状態のスナップショットを取得

        Args:
            context: スナップショットのコンテキスト情報

        Returns:
            メモリスナップショット
        """
        try:
            # プロセスメモリ情報
            memory_info = self.process.memory_info()
            process_memory_mb = memory_info.rss / 1024 / 1024
            
            # システムメモリ情報
            system_memory = psutil.virtual_memory()
            system_memory_percent = system_memory.percent
            
            # tracemalloc情報
            current_size, peak_size = tracemalloc.get_traced_memory()
            tracemalloc_current_mb = current_size / 1024 / 1024
            tracemalloc_peak_mb = peak_size / 1024 / 1024
            
            # GCオブジェクト数
            gc_objects_count = len(gc.get_objects())
            
            # スレッド数
            thread_count = threading.active_count()
            
            # ファイルディスクリプタ数
            try:
                file_descriptors = self.process.num_fds()
            except (AttributeError, psutil.AccessDenied):
                # Windowsまたはアクセス権限がない場合
                file_descriptors = 0
            
            snapshot = MemorySnapshot(
                timestamp=datetime.now(),
                process_memory_mb=process_memory_mb,
                system_memory_percent=system_memory_percent,
                tracemalloc_current_mb=tracemalloc_current_mb,
                tracemalloc_peak_mb=tracemalloc_peak_mb,
                gc_objects_count=gc_objects_count,
                thread_count=thread_count,
                file_descriptors=file_descriptors,
                context=context
            )
            
            # スナップショット履歴に追加
            self.snapshots.append(snapshot)
            
            # 最大数を超えた場合は古いものを削除
            if len(self.snapshots) > self.max_snapshots:
                self.snapshots = self.snapshots[-self.max_snapshots:]
            
            logger.debug(f"メモリスナップショットを取得: {process_memory_mb:.1f}MB ({context})")
            return snapshot
            
        except Exception as e:
            logger.error(f"メモリスナップショット取得に失敗: {e}")
            raise

    def start_monitoring(self, interval: float = 5.0) -> None:
        """
        継続的なメモリ監視を開始

        Args:
            interval: 監視間隔（秒）
        """
        if self.monitoring_active:
            logger.warning("メモリ監視は既に実行中です")
            return
        
        self.monitoring_interval = interval
        self.monitoring_active = True
        
        def monitor_loop():
            logger.info(f"メモリ監視を開始しました（間隔: {interval}秒）")
            
            while self.monitoring_active:
                try:
                    snapshot = self.take_snapshot("監視")
                    
                    # 閾値チェック
                    self._check_thresholds(snapshot)
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"メモリ監視中にエラー: {e}")
                    time.sleep(interval)
            
            logger.info("メモリ監視を停止しました")
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()

    def stop_monitoring(self) -> None:
        """継続的なメモリ監視を停止"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)
        
        logger.info("メモリ監視を停止しました")

    def detect_memory_leaks(self, duration_minutes: int = 5) -> List[MemoryLeak]:
        """
        メモリリークを検出

        Args:
            duration_minutes: 検出期間（分）

        Returns:
            検出されたメモリリークのリスト
        """
        logger.info(f"メモリリーク検出を開始（期間: {duration_minutes}分）")
        
        leaks = []
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        # 指定期間内のスナップショットを取得
        recent_snapshots = [
            s for s in self.snapshots
            if s.timestamp >= cutoff_time
        ]
        
        if len(recent_snapshots) < 2:
            logger.warning("メモリリーク検出に十分なスナップショットがありません")
            return leaks
        
        # 時系列でソート
        recent_snapshots.sort(key=lambda x: x.timestamp)
        
        # リーク検出アルゴリズム
        window_size = min(10, len(recent_snapshots) // 2)  # ウィンドウサイズ
        
        for i in range(len(recent_snapshots) - window_size):
            start_window = recent_snapshots[i:i + window_size]
            end_window = recent_snapshots[i + window_size:]
            
            if len(end_window) < window_size:
                continue
            
            end_window = end_window[:window_size]
            
            # 平均メモリ使用量を計算
            start_avg_memory = sum(s.process_memory_mb for s in start_window) / len(start_window)
            end_avg_memory = sum(s.process_memory_mb for s in end_window) / len(end_window)
            
            # 時間差を計算
            time_diff = (end_window[-1].timestamp - start_window[0].timestamp).total_seconds()
            
            if time_diff <= 0:
                continue
            
            # リーク率を計算
            memory_diff = end_avg_memory - start_avg_memory
            leak_rate = memory_diff / time_diff
            
            # リーク判定
            if leak_rate > self.thresholds.leak_rate_mb_per_sec:
                severity = self._determine_leak_severity(leak_rate, memory_diff)
                
                # トップアロケーション情報を取得
                top_allocations = self._get_top_allocations()
                
                # 分析情報を生成
                analysis = self._analyze_memory_leak(
                    start_window[0], end_window[-1], leak_rate, memory_diff
                )
                
                leak = MemoryLeak(
                    start_snapshot=start_window[0],
                    end_snapshot=end_window[-1],
                    leak_rate_mb_per_sec=leak_rate,
                    total_leaked_mb=memory_diff,
                    duration_seconds=time_diff,
                    severity=severity,
                    analysis=analysis,
                    top_allocations=top_allocations
                )
                
                leaks.append(leak)
                
                logger.warning(
                    f"メモリリークを検出: {leak_rate:.3f}MB/秒 "
                    f"(総量: {memory_diff:.1f}MB, 重要度: {severity})"
                )
        
        # リークを保存
        if leaks:
            self._save_leaks(leaks)
        
        logger.info(f"{len(leaks)}個のメモリリークを検出しました")
        return leaks

    def profile_function(self, func: Callable, *args, **kwargs) -> Tuple[Any, MemorySnapshot, MemorySnapshot]:
        """
        関数実行時のメモリプロファイリング

        Args:
            func: プロファイリング対象の関数
            *args: 関数の引数
            **kwargs: 函数のキーワード引数

        Returns:
            (関数の戻り値, 実行前スナップショット, 実行後スナップショット)
        """
        logger.info(f"関数メモリプロファイリング開始: {func.__name__}")
        
        # 実行前のスナップショット
        gc.collect()  # ガベージコレクション実行
        before_snapshot = self.take_snapshot(f"実行前: {func.__name__}")
        
        try:
            # 関数実行
            result = func(*args, **kwargs)
            
            # 実行後のスナップショット
            after_snapshot = self.take_snapshot(f"実行後: {func.__name__}")
            
            # メモリ使用量の変化をログ出力
            memory_diff = after_snapshot.process_memory_mb - before_snapshot.process_memory_mb
            tracemalloc_diff = after_snapshot.tracemalloc_current_mb - before_snapshot.tracemalloc_current_mb
            
            logger.info(
                f"関数メモリプロファイリング完了: {func.__name__} "
                f"(プロセスメモリ変化: {memory_diff:+.1f}MB, "
                f"tracemalloc変化: {tracemalloc_diff:+.1f}MB)"
            )
            
            return result, before_snapshot, after_snapshot
            
        except Exception as e:
            # エラー時もスナップショットを取得
            error_snapshot = self.take_snapshot(f"エラー時: {func.__name__}")
            logger.error(f"関数実行中にエラー: {func.__name__}: {e}")
            raise

    def generate_memory_report(self, hours: int = 24) -> Dict[str, Any]:
        """
        メモリ使用量レポートを生成

        Args:
            hours: レポート対象期間（時間）

        Returns:
            メモリレポート
        """
        logger.info(f"過去{hours}時間のメモリレポートを生成中")
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 期間内のスナップショットを取得
        recent_snapshots = [
            s for s in self.snapshots
            if s.timestamp >= cutoff_time
        ]
        
        if not recent_snapshots:
            logger.warning("レポート生成に十分なデータがありません")
            return {
                'period_hours': hours,
                'error': 'データが不足しています',
                'snapshots_count': 0
            }
        
        # 統計情報を計算
        memory_values = [s.process_memory_mb for s in recent_snapshots]
        system_memory_values = [s.system_memory_percent for s in recent_snapshots]
        tracemalloc_values = [s.tracemalloc_current_mb for s in recent_snapshots]
        gc_objects_values = [s.gc_objects_count for s in recent_snapshots]
        
        # メモリリークを検出
        leaks = self.detect_memory_leaks(duration_minutes=hours * 60)
        
        # レポート生成
        report = {
            'period_hours': hours,
            'generated_at': datetime.now().isoformat(),
            'snapshots_count': len(recent_snapshots),
            
            'process_memory': {
                'current_mb': memory_values[-1] if memory_values else 0,
                'min_mb': min(memory_values) if memory_values else 0,
                'max_mb': max(memory_values) if memory_values else 0,
                'avg_mb': sum(memory_values) / len(memory_values) if memory_values else 0,
                'trend': self._calculate_trend(memory_values)
            },
            
            'system_memory': {
                'current_percent': system_memory_values[-1] if system_memory_values else 0,
                'min_percent': min(system_memory_values) if system_memory_values else 0,
                'max_percent': max(system_memory_values) if system_memory_values else 0,
                'avg_percent': sum(system_memory_values) / len(system_memory_values) if system_memory_values else 0
            },
            
            'tracemalloc': {
                'current_mb': tracemalloc_values[-1] if tracemalloc_values else 0,
                'min_mb': min(tracemalloc_values) if tracemalloc_values else 0,
                'max_mb': max(tracemalloc_values) if tracemalloc_values else 0,
                'avg_mb': sum(tracemalloc_values) / len(tracemalloc_values) if tracemalloc_values else 0,
                'peak_mb': max(s.tracemalloc_peak_mb for s in recent_snapshots) if recent_snapshots else 0
            },
            
            'gc_objects': {
                'current_count': gc_objects_values[-1] if gc_objects_values else 0,
                'min_count': min(gc_objects_values) if gc_objects_values else 0,
                'max_count': max(gc_objects_values) if gc_objects_values else 0,
                'avg_count': sum(gc_objects_values) / len(gc_objects_values) if gc_objects_values else 0
            },
            
            'memory_leaks': {
                'detected_count': len(leaks),
                'critical_count': len([l for l in leaks if l.severity == 'CRITICAL']),
                'high_count': len([l for l in leaks if l.severity == 'HIGH']),
                'total_leaked_mb': sum(l.total_leaked_mb for l in leaks)
            },
            
            'thresholds_exceeded': self._check_threshold_violations(recent_snapshots),
            
            'recommendations': self._generate_recommendations(recent_snapshots, leaks)
        }
        
        # レポートをファイルに保存
        report_file = self.reports_dir / f"memory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"メモリレポートを生成しました: {report_file}")
        return report

    def _check_thresholds(self, snapshot: MemorySnapshot) -> None:
        """閾値チェック"""
        alerts = []
        
        if snapshot.process_memory_mb > self.thresholds.process_memory_mb:
            alerts.append(
                f"プロセスメモリ使用量が閾値を超過: {snapshot.process_memory_mb:.1f}MB "
                f"(閾値: {self.thresholds.process_memory_mb}MB)"
            )
        
        if snapshot.system_memory_percent > self.thresholds.system_memory_percent:
            alerts.append(
                f"システムメモリ使用率が閾値を超過: {snapshot.system_memory_percent:.1f}% "
                f"(閾値: {self.thresholds.system_memory_percent}%)"
            )
        
        for alert in alerts:
            logger.warning(alert)

    def _determine_leak_severity(self, leak_rate: float, total_leaked: float) -> str:
        """メモリリークの重要度を判定"""
        if leak_rate > 10.0 or total_leaked > 100.0:
            return 'CRITICAL'
        elif leak_rate > 5.0 or total_leaked > 50.0:
            return 'HIGH'
        elif leak_rate > 2.0 or total_leaked > 20.0:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _get_top_allocations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """トップメモリアロケーション情報を取得"""
        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            
            allocations = []
            for stat in top_stats[:limit]:
                allocations.append({
                    'size_mb': stat.size / 1024 / 1024,
                    'count': stat.count,
                    'filename': stat.traceback.format()[0] if stat.traceback.format() else 'unknown',
                })
            
            return allocations
        except Exception as e:
            logger.error(f"トップアロケーション取得に失敗: {e}")
            return []

    def _analyze_memory_leak(self, start: MemorySnapshot, end: MemorySnapshot, 
                           leak_rate: float, total_leaked: float) -> str:
        """メモリリークの分析"""
        analysis_parts = []
        
        # 基本情報
        duration = (end.timestamp - start.timestamp).total_seconds()
        analysis_parts.append(f"{duration:.0f}秒間で{total_leaked:.1f}MBのメモリリーク")
        
        # GCオブジェクト数の変化
        gc_diff = end.gc_objects_count - start.gc_objects_count
        if gc_diff > 0:
            gc_rate = gc_diff / duration
            analysis_parts.append(f"GCオブジェクト数が{gc_diff}個増加（{gc_rate:.1f}個/秒）")
        
        # スレッド数の変化
        thread_diff = end.thread_count - start.thread_count
        if thread_diff > 0:
            analysis_parts.append(f"スレッド数が{thread_diff}個増加")
        
        # ファイルディスクリプタの変化
        fd_diff = end.file_descriptors - start.file_descriptors
        if fd_diff > 0:
            analysis_parts.append(f"ファイルディスクリプタが{fd_diff}個増加")
        
        return "、".join(analysis_parts)

    def _calculate_trend(self, values: List[float]) -> str:
        """トレンドを計算"""
        if len(values) < 2:
            return "不明"
        
        # 線形回帰の傾きを計算
        n = len(values)
        x = list(range(n))
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 == 0:
            return "安定"
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "増加"
        elif slope < -0.1:
            return "減少"
        else:
            return "安定"

    def _check_threshold_violations(self, snapshots: List[MemorySnapshot]) -> Dict[str, int]:
        """閾値違反をチェック"""
        violations = {
            'process_memory': 0,
            'system_memory': 0,
            'total': 0
        }
        
        for snapshot in snapshots:
            if snapshot.process_memory_mb > self.thresholds.process_memory_mb:
                violations['process_memory'] += 1
                violations['total'] += 1
            
            if snapshot.system_memory_percent > self.thresholds.system_memory_percent:
                violations['system_memory'] += 1
                violations['total'] += 1
        
        return violations

    def _generate_recommendations(self, snapshots: List[MemorySnapshot], 
                                leaks: List[MemoryLeak]) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        if not snapshots:
            return recommendations
        
        # 最新のスナップショット
        latest = snapshots[-1]
        
        # メモリ使用量が高い場合
        if latest.process_memory_mb > self.thresholds.process_memory_mb:
            recommendations.append(
                f"プロセスメモリ使用量が高いです（{latest.process_memory_mb:.1f}MB）。"
                "不要なオブジェクトの削除やガベージコレクションの実行を検討してください。"
            )
        
        # メモリリークが検出された場合
        if leaks:
            critical_leaks = [l for l in leaks if l.severity in ['HIGH', 'CRITICAL']]
            if critical_leaks:
                recommendations.append(
                    f"{len(critical_leaks)}個の重要なメモリリークが検出されました。"
                    "コードレビューとメモリ管理の見直しが必要です。"
                )
        
        # GCオブジェクト数が多い場合
        if latest.gc_objects_count > 100000:
            recommendations.append(
                f"GCオブジェクト数が多いです（{latest.gc_objects_count:,}個）。"
                "循環参照や不要なオブジェクト参照の確認を推奨します。"
            )
        
        # システムメモリ使用率が高い場合
        if latest.system_memory_percent > 90:
            recommendations.append(
                f"システムメモリ使用率が高いです（{latest.system_memory_percent:.1f}%）。"
                "他のプロセスの終了やシステムリソースの確認を検討してください。"
            )
        
        return recommendations

    def _save_snapshots(self) -> None:
        """スナップショットを保存"""
        try:
            data = [s.to_dict() for s in self.snapshots]
            
            with open(self.snapshots_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"{len(self.snapshots)}個のスナップショットを保存しました")
            
        except Exception as e:
            logger.error(f"スナップショット保存に失敗: {e}")

    def _load_snapshots(self) -> None:
        """スナップショットを読み込み"""
        if not self.snapshots_file.exists():
            return
        
        try:
            with open(self.snapshots_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.snapshots = []
            for item in data:
                item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                self.snapshots.append(MemorySnapshot(**item))
            
            logger.info(f"{len(self.snapshots)}個のスナップショットを読み込みました")
            
        except Exception as e:
            logger.error(f"スナップショット読み込みに失敗: {e}")

    def _save_leaks(self, leaks: List[MemoryLeak]) -> None:
        """メモリリークを保存"""
        try:
            # 既存のリークを読み込み
            existing_leaks = self._load_leaks()
            existing_leaks.extend(leaks)
            
            # 古いリークを削除（7日以上前）
            cutoff_time = datetime.now() - timedelta(days=7)
            existing_leaks = [
                l for l in existing_leaks
                if l.start_snapshot.timestamp >= cutoff_time
            ]
            
            # JSON形式で保存
            data = []
            for leak in existing_leaks:
                leak_dict = {
                    'start_snapshot': leak.start_snapshot.to_dict(),
                    'end_snapshot': leak.end_snapshot.to_dict(),
                    'leak_rate_mb_per_sec': leak.leak_rate_mb_per_sec,
                    'total_leaked_mb': leak.total_leaked_mb,
                    'duration_seconds': leak.duration_seconds,
                    'severity': leak.severity,
                    'analysis': leak.analysis,
                    'top_allocations': leak.top_allocations
                }
                data.append(leak_dict)
            
            with open(self.leaks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"{len(existing_leaks)}個のメモリリークを保存しました")
            
        except Exception as e:
            logger.error(f"メモリリーク保存に失敗: {e}")

    def _load_leaks(self) -> List[MemoryLeak]:
        """メモリリークを読み込み"""
        if not self.leaks_file.exists():
            return []
        
        try:
            with open(self.leaks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            leaks = []
            for item in data:
                # スナップショットを復元
                start_dict = item['start_snapshot']
                start_dict['timestamp'] = datetime.fromisoformat(start_dict['timestamp'])
                start_snapshot = MemorySnapshot(**start_dict)
                
                end_dict = item['end_snapshot']
                end_dict['timestamp'] = datetime.fromisoformat(end_dict['timestamp'])
                end_snapshot = MemorySnapshot(**end_dict)
                
                leak = MemoryLeak(
                    start_snapshot=start_snapshot,
                    end_snapshot=end_snapshot,
                    leak_rate_mb_per_sec=item['leak_rate_mb_per_sec'],
                    total_leaked_mb=item['total_leaked_mb'],
                    duration_seconds=item['duration_seconds'],
                    severity=item['severity'],
                    analysis=item['analysis'],
                    top_allocations=item['top_allocations']
                )
                leaks.append(leak)
            
            return leaks
            
        except Exception as e:
            logger.error(f"メモリリーク読み込みに失敗: {e}")
            return []

    def cleanup(self) -> None:
        """リソースのクリーンアップ"""
        self.stop_monitoring()
        self._save_snapshots()
        
        if tracemalloc.is_tracing():
            tracemalloc.stop()
            logger.info("tracemalloc監視を停止しました")


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="メモリプロファイリングシステム")
    parser.add_argument(
        '--monitor',
        type=int,
        metavar='SECONDS',
        help='指定秒数間メモリ監視を実行'
    )
    parser.add_argument(
        '--detect-leaks',
        type=int,
        metavar='MINUTES',
        default=5,
        help='指定分数間のメモリリークを検出'
    )
    parser.add_argument(
        '--generate-report',
        type=int,
        metavar='HOURS',
        default=24,
        help='指定時間のメモリレポートを生成'
    )
    parser.add_argument(
        '--snapshot',
        action='store_true',
        help='現在のメモリスナップショットを取得'
    )
    parser.add_argument(
        '--data-dir',
        default='logs/performance/memory',
        help='データ保存ディレクトリ'
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
            logging.FileHandler('logs/memory_profiler.log', encoding='utf-8')
        ]
    )
    
    profiler = MemoryProfiler(args.data_dir)
    
    try:
        if args.snapshot:
            # スナップショット取得
            snapshot = profiler.take_snapshot("手動実行")
            print(f"📸 メモリスナップショット:")
            print(f"  プロセスメモリ: {snapshot.process_memory_mb:.1f}MB")
            print(f"  システムメモリ使用率: {snapshot.system_memory_percent:.1f}%")
            print(f"  tracemalloc: {snapshot.tracemalloc_current_mb:.1f}MB (ピーク: {snapshot.tracemalloc_peak_mb:.1f}MB)")
            print(f"  GCオブジェクト数: {snapshot.gc_objects_count:,}個")
            print(f"  スレッド数: {snapshot.thread_count}")
        
        elif args.monitor:
            # メモリ監視
            print(f"🔍 {args.monitor}秒間メモリ監視を開始...")
            profiler.start_monitoring(interval=1.0)
            time.sleep(args.monitor)
            profiler.stop_monitoring()
            
            # 監視結果の表示
            if profiler.snapshots:
                latest = profiler.snapshots[-1]
                print(f"📊 監視結果:")
                print(f"  最終メモリ使用量: {latest.process_memory_mb:.1f}MB")
                print(f"  スナップショット数: {len(profiler.snapshots)}")
        
        elif args.detect_leaks:
            # メモリリーク検出
            leaks = profiler.detect_memory_leaks(duration_minutes=args.detect_leaks)
            
            if leaks:
                print(f"⚠️  {len(leaks)}個のメモリリークを検出:")
                for leak in leaks:
                    print(f"  - リーク率: {leak.leak_rate_mb_per_sec:.3f}MB/秒")
                    print(f"    総リーク量: {leak.total_leaked_mb:.1f}MB")
                    print(f"    重要度: {leak.severity}")
                    print(f"    分析: {leak.analysis}")
                    print()
            else:
                print("✅ メモリリークは検出されませんでした")
        
        elif args.generate_report:
            # レポート生成
            report = profiler.generate_memory_report(hours=args.generate_report)
            
            print(f"📋 メモリレポート ({report['period_hours']}時間)")
            print(f"スナップショット数: {report['snapshots_count']}")
            
            if 'error' not in report:
                pm = report['process_memory']
                print(f"\n💾 プロセスメモリ:")
                print(f"  現在: {pm['current_mb']:.1f}MB")
                print(f"  最小-最大: {pm['min_mb']:.1f}-{pm['max_mb']:.1f}MB")
                print(f"  平均: {pm['avg_mb']:.1f}MB")
                print(f"  トレンド: {pm['trend']}")
                
                ml = report['memory_leaks']
                print(f"\n🚨 メモリリーク:")
                print(f"  検出数: {ml['detected_count']}")
                print(f"  重要: {ml['critical_count']}")
                print(f"  総リーク量: {ml['total_leaked_mb']:.1f}MB")
                
                if report['recommendations']:
                    print(f"\n💡 推奨事項:")
                    for rec in report['recommendations']:
                        print(f"  - {rec}")
            else:
                print(f"❌ {report['error']}")
        
        else:
            # デフォルト: 基本情報表示
            snapshot = profiler.take_snapshot("基本情報")
            print(f"🖥️  メモリプロファイラー")
            print(f"プロセスメモリ: {snapshot.process_memory_mb:.1f}MB")
            print(f"システムメモリ使用率: {snapshot.system_memory_percent:.1f}%")
            print(f"GCオブジェクト数: {snapshot.gc_objects_count:,}個")
            print(f"\n使用方法:")
            print(f"  --monitor SECONDS     : メモリ監視")
            print(f"  --detect-leaks MINUTES: リーク検出")
            print(f"  --generate-report HOURS: レポート生成")
            print(f"  --snapshot            : スナップショット取得")
    
    except KeyboardInterrupt:
        logger.info("ユーザーによって中断されました")
    except Exception as e:
        logger.error(f"予期しないエラーが発生: {e}")
        return 1
    finally:
        profiler.cleanup()
    
    return 0


if __name__ == "__main__":
    exit(main())