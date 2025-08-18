#!/usr/bin/env python3
"""
GUI応答性メトリクス可視化システム

このモジュールは、GUI応答性測定結果の可視化機能を提供します。
"""

import json
import logging
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sys

# 可視化ライブラリのインポート（オプション）
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# GUI応答性監視システムのインポート
try:
    from scripts.gui_responsiveness_monitor import ResponsivenessMonitor
    GUI_MONITOR_AVAILABLE = True
except ImportError:
    GUI_MONITOR_AVAILABLE = False

from qt_theme_studio.logger import get_logger

logger = get_logger(__name__)


class ResponsivenessVisualizer:
    """GUI応答性メトリクス可視化クラス"""
    
    def __init__(self, data_dir: str = "logs/performance/gui"):
        """
        可視化システムを初期化
        
        Args:
            data_dir: データディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.output_dir = self.data_dir / "visualizations"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if GUI_MONITOR_AVAILABLE:
            self.monitor = ResponsivenessMonitor(data_dir)
        else:
            self.monitor = None
        
        # 日本語フォント設定（matplotlib用）
        if MATPLOTLIB_AVAILABLE:
            self._setup_japanese_font()
        
        logger.info("GUI応答性可視化システムを初期化しました")
    
    def _setup_japanese_font(self):
        """日本語フォントを設定"""
        try:
            # 日本語フォントの設定を試行
            plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
            plt.rcParams['axes.unicode_minus'] = False
            logger.info("日本語フォントを設定しました")
        except Exception as e:
            logger.warning(f"日本語フォント設定に失敗: {e}")
    
    def create_response_time_trend_chart(self, days: int = 30) -> Optional[str]:
        """
        応答時間トレンドチャートを作成
        
        Args:
            days: 対象期間（日数）
            
        Returns:
            Optional[str]: 生成されたチャートファイルのパス
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlibが利用できません")
            return None
        
        if not self.monitor:
            logger.error("GUI応答性監視システムが利用できません")
            return None
        
        try:
            # メトリクスデータを読み込み
            metrics_data = self._load_metrics_data(days)
            if not metrics_data:
                logger.warning("メトリクスデータが見つかりません")
                return None
            
            # データを時系列でソート
            sorted_data = sorted(metrics_data, key=lambda x: x.get('timestamp', ''))
            
            # データを抽出
            timestamps = []
            avg_times = []
            p95_times = []
            p99_times = []
            
            for data in sorted_data:
                try:
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    timestamps.append(timestamp)
                    avg_times.append(data.get('average_response_time', 0))
                    p95_times.append(data.get('p95_response_time', 0))
                    p99_times.append(data.get('p99_response_time', 0))
                except (ValueError, KeyError) as e:
                    logger.debug(f"データ解析エラー: {e}")
                    continue
            
            if not timestamps:
                logger.warning("有効なタイムスタンプデータが見つかりません")
                return None
            
            # チャートを作成
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 応答時間の線グラフ
            ax.plot(timestamps, avg_times, label='平均応答時間', linewidth=2, marker='o')
            ax.plot(timestamps, p95_times, label='95パーセンタイル', linewidth=2, marker='s', alpha=0.7)
            ax.plot(timestamps, p99_times, label='99パーセンタイル', linewidth=2, marker='^', alpha=0.7)
            
            # 閾値線を追加
            if self.monitor:
                thresholds = self.monitor.thresholds
                ax.axhline(y=thresholds['excellent'], color='green', linestyle='--', alpha=0.5, label='優秀 (50ms)')
                ax.axhline(y=thresholds['good'], color='blue', linestyle='--', alpha=0.5, label='良好 (100ms)')
                ax.axhline(y=thresholds['acceptable'], color='orange', linestyle='--', alpha=0.5, label='許容範囲 (200ms)')
                ax.axhline(y=thresholds['poor'], color='red', linestyle='--', alpha=0.5, label='改善が必要 (500ms)')
            
            # チャートの設定
            ax.set_xlabel('日時')
            ax.set_ylabel('応答時間 (秒)')
            ax.set_title(f'GUI応答時間トレンド ({days}日間)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # X軸の日付フォーマット
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 10)))
            plt.xticks(rotation=45)
            
            # レイアウト調整
            plt.tight_layout()
            
            # ファイルに保存
            output_file = self.output_dir / f"response_time_trend_{days}days.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"応答時間トレンドチャートを作成: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"応答時間トレンドチャート作成エラー: {e}")
            return None
    
    def create_interaction_type_distribution_chart(self, days: int = 30) -> Optional[str]:
        """
        インタラクションタイプ分布チャートを作成
        
        Args:
            days: 対象期間（日数）
            
        Returns:
            Optional[str]: 生成されたチャートファイルのパス
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlibが利用できません")
            return None
        
        try:
            # メトリクスデータを読み込み
            metrics_data = self._load_metrics_data(days)
            if not metrics_data:
                logger.warning("メトリクスデータが見つかりません")
                return None
            
            # インタラクションタイプ別の集計
            interaction_totals = {}
            for data in metrics_data:
                interactions_by_type = data.get('interactions_by_type', {})
                for interaction_type, count in interactions_by_type.items():
                    interaction_totals[interaction_type] = interaction_totals.get(interaction_type, 0) + count
            
            if not interaction_totals:
                logger.warning("インタラクションデータが見つかりません")
                return None
            
            # 円グラフを作成
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 円グラフ
            labels = list(interaction_totals.keys())
            sizes = list(interaction_totals.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            
            wedges, texts, autotexts = ax1.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            ax1.set_title('インタラクションタイプ分布')
            
            # 棒グラフ
            ax2.bar(labels, sizes, color=colors)
            ax2.set_xlabel('インタラクションタイプ')
            ax2.set_ylabel('実行回数')
            ax2.set_title('インタラクションタイプ別実行回数')
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
            # レイアウト調整
            plt.tight_layout()
            
            # ファイルに保存
            output_file = self.output_dir / f"interaction_distribution_{days}days.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"インタラクション分布チャートを作成: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"インタラクション分布チャート作成エラー: {e}")
            return None
    
    def create_success_rate_chart(self, days: int = 30) -> Optional[str]:
        """
        成功率チャートを作成
        
        Args:
            days: 対象期間（日数）
            
        Returns:
            Optional[str]: 生成されたチャートファイルのパス
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlibが利用できません")
            return None
        
        try:
            # メトリクスデータを読み込み
            metrics_data = self._load_metrics_data(days)
            if not metrics_data:
                logger.warning("メトリクスデータが見つかりません")
                return None
            
            # データを時系列でソート
            sorted_data = sorted(metrics_data, key=lambda x: x.get('timestamp', ''))
            
            # データを抽出
            timestamps = []
            success_rates = []
            total_interactions = []
            
            for data in sorted_data:
                try:
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    total = data.get('total_interactions', 0)
                    successful = data.get('successful_interactions', 0)
                    
                    if total > 0:
                        success_rate = (successful / total) * 100
                        timestamps.append(timestamp)
                        success_rates.append(success_rate)
                        total_interactions.append(total)
                except (ValueError, KeyError) as e:
                    logger.debug(f"データ解析エラー: {e}")
                    continue
            
            if not timestamps:
                logger.warning("有効な成功率データが見つかりません")
                return None
            
            # チャートを作成
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # 成功率の線グラフ
            ax1.plot(timestamps, success_rates, label='成功率', linewidth=2, marker='o', color='green')
            ax1.axhline(y=95, color='orange', linestyle='--', alpha=0.7, label='目標値 (95%)')
            ax1.axhline(y=90, color='red', linestyle='--', alpha=0.7, label='最低値 (90%)')
            ax1.set_ylabel('成功率 (%)')
            ax1.set_title('インタラクション成功率トレンド')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(0, 100)
            
            # 総インタラクション数の棒グラフ
            ax2.bar(timestamps, total_interactions, alpha=0.7, color='blue', label='総インタラクション数')
            ax2.set_xlabel('日時')
            ax2.set_ylabel('インタラクション数')
            ax2.set_title('総インタラクション数')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # X軸の日付フォーマット
            for ax in [ax1, ax2]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 10)))
            
            plt.setp(ax2.get_xticklabels(), rotation=45)
            
            # レイアウト調整
            plt.tight_layout()
            
            # ファイルに保存
            output_file = self.output_dir / f"success_rate_{days}days.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"成功率チャートを作成: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"成功率チャート作成エラー: {e}")
            return None
    
    def create_performance_heatmap(self, days: int = 30) -> Optional[str]:
        """
        パフォーマンスヒートマップを作成
        
        Args:
            days: 対象期間（日数）
            
        Returns:
            Optional[str]: 生成されたチャートファイルのパス
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlibが利用できません")
            return None
        
        try:
            # メトリクスデータを読み込み
            metrics_data = self._load_metrics_data(days)
            if not metrics_data:
                logger.warning("メトリクスデータが見つかりません")
                return None
            
            # インタラクションタイプ別の応答時間データを集計
            interaction_response_times = {}
            
            for data in metrics_data:
                response_times_by_type = data.get('response_times_by_type', {})
                for interaction_type, times in response_times_by_type.items():
                    if interaction_type not in interaction_response_times:
                        interaction_response_times[interaction_type] = []
                    interaction_response_times[interaction_type].extend(times)
            
            if not interaction_response_times:
                logger.warning("応答時間データが見つかりません")
                return None
            
            # 統計値を計算
            interaction_types = list(interaction_response_times.keys())
            metrics_names = ['平均', '中央値', '95%ile', '99%ile', '最大']
            
            heatmap_data = []
            for interaction_type in interaction_types:
                times = interaction_response_times[interaction_type]
                if times:
                    row = [
                        statistics.mean(times),
                        statistics.median(times),
                        np.percentile(times, 95),
                        np.percentile(times, 99),
                        max(times)
                    ]
                else:
                    row = [0, 0, 0, 0, 0]
                heatmap_data.append(row)
            
            # ヒートマップを作成
            fig, ax = plt.subplots(figsize=(10, 6))
            
            im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
            
            # 軸ラベルを設定
            ax.set_xticks(range(len(metrics_names)))
            ax.set_xticklabels(metrics_names)
            ax.set_yticks(range(len(interaction_types)))
            ax.set_yticklabels(interaction_types)
            
            # 値をテキストで表示
            for i in range(len(interaction_types)):
                for j in range(len(metrics_names)):
                    value = heatmap_data[i][j]
                    text = ax.text(j, i, f'{value:.3f}', ha='center', va='center', 
                                 color='white' if value > np.mean(heatmap_data) else 'black')
            
            # カラーバーを追加
            cbar = plt.colorbar(im)
            cbar.set_label('応答時間 (秒)')
            
            ax.set_title('インタラクションタイプ別応答時間ヒートマップ')
            ax.set_xlabel('統計値')
            ax.set_ylabel('インタラクションタイプ')
            
            # レイアウト調整
            plt.tight_layout()
            
            # ファイルに保存
            output_file = self.output_dir / f"performance_heatmap_{days}days.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"パフォーマンスヒートマップを作成: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"パフォーマンスヒートマップ作成エラー: {e}")
            return None
    
    def create_comprehensive_dashboard(self, days: int = 30) -> Optional[str]:
        """
        包括的なダッシュボードを作成
        
        Args:
            days: 対象期間（日数）
            
        Returns:
            Optional[str]: 生成されたダッシュボードファイルのパス
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlibが利用できません")
            return None
        
        try:
            # メトリクスデータを読み込み
            metrics_data = self._load_metrics_data(days)
            if not metrics_data:
                logger.warning("メトリクスデータが見つかりません")
                return None
            
            # 4つのサブプロットを持つダッシュボードを作成
            fig = plt.figure(figsize=(16, 12))
            
            # 1. 応答時間トレンド
            ax1 = plt.subplot(2, 2, 1)
            self._plot_response_time_trend(ax1, metrics_data)
            
            # 2. インタラクション分布
            ax2 = plt.subplot(2, 2, 2)
            self._plot_interaction_distribution(ax2, metrics_data)
            
            # 3. 成功率トレンド
            ax3 = plt.subplot(2, 2, 3)
            self._plot_success_rate_trend(ax3, metrics_data)
            
            # 4. 統計サマリー
            ax4 = plt.subplot(2, 2, 4)
            self._plot_statistics_summary(ax4, metrics_data)
            
            # 全体タイトル
            fig.suptitle(f'GUI応答性ダッシュボード ({days}日間)', fontsize=16, fontweight='bold')
            
            # レイアウト調整
            plt.tight_layout()
            plt.subplots_adjust(top=0.93)
            
            # ファイルに保存
            output_file = self.output_dir / f"dashboard_{days}days.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"包括的ダッシュボードを作成: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"ダッシュボード作成エラー: {e}")
            return None
    
    def _plot_response_time_trend(self, ax, metrics_data: List[Dict[str, Any]]):
        """応答時間トレンドをプロット"""
        sorted_data = sorted(metrics_data, key=lambda x: x.get('timestamp', ''))
        
        timestamps = []
        avg_times = []
        
        for data in sorted_data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'])
                timestamps.append(timestamp)
                avg_times.append(data.get('average_response_time', 0))
            except (ValueError, KeyError):
                continue
        
        if timestamps:
            ax.plot(timestamps, avg_times, linewidth=2, marker='o')
            ax.set_title('応答時間トレンド')
            ax.set_ylabel('応答時間 (秒)')
            ax.grid(True, alpha=0.3)
            
            # X軸の日付フォーマット
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax.get_xticklabels(), rotation=45)
    
    def _plot_interaction_distribution(self, ax, metrics_data: List[Dict[str, Any]]):
        """インタラクション分布をプロット"""
        interaction_totals = {}
        for data in metrics_data:
            interactions_by_type = data.get('interactions_by_type', {})
            for interaction_type, count in interactions_by_type.items():
                interaction_totals[interaction_type] = interaction_totals.get(interaction_type, 0) + count
        
        if interaction_totals:
            labels = list(interaction_totals.keys())
            sizes = list(interaction_totals.values())
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title('インタラクション分布')
    
    def _plot_success_rate_trend(self, ax, metrics_data: List[Dict[str, Any]]):
        """成功率トレンドをプロット"""
        sorted_data = sorted(metrics_data, key=lambda x: x.get('timestamp', ''))
        
        timestamps = []
        success_rates = []
        
        for data in sorted_data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'])
                total = data.get('total_interactions', 0)
                successful = data.get('successful_interactions', 0)
                
                if total > 0:
                    success_rate = (successful / total) * 100
                    timestamps.append(timestamp)
                    success_rates.append(success_rate)
            except (ValueError, KeyError):
                continue
        
        if timestamps:
            ax.plot(timestamps, success_rates, linewidth=2, marker='s', color='green')
            ax.axhline(y=95, color='orange', linestyle='--', alpha=0.7)
            ax.set_title('成功率トレンド')
            ax.set_ylabel('成功率 (%)')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
            
            # X軸の日付フォーマット
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax.get_xticklabels(), rotation=45)
    
    def _plot_statistics_summary(self, ax, metrics_data: List[Dict[str, Any]]):
        """統計サマリーをプロット"""
        # 全期間の統計を計算
        all_avg_times = [d.get('average_response_time', 0) for d in metrics_data if d.get('average_response_time', 0) > 0]
        total_interactions = sum(d.get('total_interactions', 0) for d in metrics_data)
        total_successful = sum(d.get('successful_interactions', 0) for d in metrics_data)
        
        if all_avg_times:
            overall_avg = statistics.mean(all_avg_times)
            overall_success_rate = (total_successful / total_interactions * 100) if total_interactions > 0 else 0
            
            # 統計値を表示
            stats_text = f"""統計サマリー

総インタラクション数: {total_interactions:,}
成功インタラクション数: {total_successful:,}
全体成功率: {overall_success_rate:.1f}%

平均応答時間: {overall_avg:.3f}秒
最速応答時間: {min(all_avg_times):.3f}秒
最遅応答時間: {max(all_avg_times):.3f}秒

セッション数: {len(metrics_data)}"""
            
            ax.text(0.1, 0.9, stats_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', fontfamily='monospace')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
    
    def _load_metrics_data(self, days: int) -> List[Dict[str, Any]]:
        """メトリクスデータを読み込み"""
        if not self.monitor:
            return []
        
        metrics_file = self.monitor.metrics_file
        if not metrics_file.exists():
            return []
        
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            all_metrics = data.get('metrics', [])
            
            # 期間内のデータをフィルタリング
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_metrics = []
            
            for metrics_data in all_metrics:
                try:
                    metrics_time = datetime.fromisoformat(metrics_data['timestamp'])
                    if metrics_time >= cutoff_date:
                        filtered_metrics.append(metrics_data)
                except (ValueError, KeyError):
                    continue
            
            return filtered_metrics
            
        except Exception as e:
            logger.error(f"メトリクスデータ読み込みエラー: {e}")
            return []
    
    def generate_html_report(self, days: int = 30) -> Optional[str]:
        """
        HTML形式のレポートを生成
        
        Args:
            days: 対象期間（日数）
            
        Returns:
            Optional[str]: 生成されたHTMLファイルのパス
        """
        try:
            # 各チャートを生成
            trend_chart = self.create_response_time_trend_chart(days)
            distribution_chart = self.create_interaction_type_distribution_chart(days)
            success_chart = self.create_success_rate_chart(days)
            heatmap_chart = self.create_performance_heatmap(days)
            dashboard_chart = self.create_comprehensive_dashboard(days)
            
            # レポートデータを取得
            if self.monitor:
                report_data = self.monitor.generate_responsiveness_report(days)
            else:
                report_data = self._create_empty_report_data(days)
            
            # HTMLテンプレートを生成
            html_content = self._generate_html_template(
                days, report_data, trend_chart, distribution_chart, 
                success_chart, heatmap_chart, dashboard_chart
            )
            
            # HTMLファイルに保存
            output_file = self.output_dir / f"responsiveness_report_{days}days.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTMLレポートを生成: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"HTMLレポート生成エラー: {e}")
            return None
    
    def _generate_html_template(self, days: int, report_data: Dict[str, Any], 
                              trend_chart: Optional[str], distribution_chart: Optional[str],
                              success_chart: Optional[str], heatmap_chart: Optional[str],
                              dashboard_chart: Optional[str]) -> str:
        """HTMLテンプレートを生成"""
        
        # 相対パスに変換
        def get_relative_path(file_path: Optional[str]) -> str:
            if file_path:
                return Path(file_path).name
            return ""
        
        trend_img = get_relative_path(trend_chart)
        distribution_img = get_relative_path(distribution_chart)
        success_img = get_relative_path(success_chart)
        heatmap_img = get_relative_path(heatmap_chart)
        dashboard_img = get_relative_path(dashboard_chart)
        
        summary = report_data.get('summary', {})
        recommendations = report_data.get('recommendations', [])
        trend_analysis = report_data.get('trend_analysis', {})
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GUI応答性レポート ({days}日間)</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .summary-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}
        .chart-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .recommendations {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .recommendations h3 {{
            color: #856404;
            margin-top: 0;
        }}
        .recommendations ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .recommendations li {{
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        .trend-info {{
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }}
        .grade {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        .grade-a {{ background-color: #27ae60; }}
        .grade-b {{ background-color: #f39c12; }}
        .grade-c {{ background-color: #e67e22; }}
        .grade-d {{ background-color: #e74c3c; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GUI応答性レポート ({days}日間)</h1>
        
        <div class="summary-grid">
            <div class="summary-card">
                <h3>総セッション数</h3>
                <div class="value">{summary.get('total_sessions', 0)}</div>
            </div>
            <div class="summary-card">
                <h3>総インタラクション数</h3>
                <div class="value">{summary.get('total_interactions', 0):,}</div>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="value">{summary.get('success_rate', 0):.1f}%</div>
            </div>
            <div class="summary-card">
                <h3>平均応答時間</h3>
                <div class="value">{summary.get('overall_avg_response_time', 0):.3f}秒</div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            <span class="grade grade-{summary.get('responsiveness_grade', '不明')[0].lower()}">{summary.get('responsiveness_grade', '不明')}</span>
        </div>
        
        <div class="trend-info">
            <strong>トレンド分析:</strong> {trend_analysis.get('trend', '不明')} 
            ({trend_analysis.get('change_rate', 0):+.2f}%)
        </div>
"""
        
        # ダッシュボード画像
        if dashboard_img:
            html_content += f"""
        <h2>📊 総合ダッシュボード</h2>
        <div class="chart-container">
            <img src="{dashboard_img}" alt="総合ダッシュボード">
        </div>
"""
        
        # 個別チャート
        charts = [
            (trend_img, "📈 応答時間トレンド", "応答時間トレンド"),
            (success_img, "✅ 成功率トレンド", "成功率トレンド"),
            (distribution_img, "📊 インタラクション分布", "インタラクション分布"),
            (heatmap_img, "🔥 パフォーマンスヒートマップ", "パフォーマンスヒートマップ")
        ]
        
        for img_path, title, alt_text in charts:
            if img_path:
                html_content += f"""
        <h2>{title}</h2>
        <div class="chart-container">
            <img src="{img_path}" alt="{alt_text}">
        </div>
"""
        
        # 改善提案
        if recommendations:
            html_content += """
        <div class="recommendations">
            <h3>💡 改善提案</h3>
            <ul>
"""
            for recommendation in recommendations:
                html_content += f"                <li>{recommendation}</li>\n"
            
            html_content += """
            </ul>
        </div>
"""
        
        # フッター
        html_content += f"""
        <div class="footer">
            レポート生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}<br>
            Qt-Theme-Studio GUI応答性監視システム
        </div>
    </div>
</body>
</html>
"""
        
        return html_content
    
    def _create_empty_report_data(self, days: int) -> Dict[str, Any]:
        """空のレポートデータを作成"""
        return {
            'period': f"{days}日間",
            'summary': {
                'total_sessions': 0,
                'total_interactions': 0,
                'successful_interactions': 0,
                'failed_interactions': 0,
                'success_rate': 0,
                'overall_avg_response_time': 0,
                'overall_p95_response_time': 0,
                'responsiveness_grade': '不明'
            },
            'interaction_types': {},
            'trend_analysis': {'trend': '不明', 'change_rate': 0},
            'recommendations': ['データが不足しています。応答性テストを実行してください。']
        }


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GUI応答性メトリクス可視化システム")
    parser.add_argument(
        '--create-charts',
        action='store_true',
        help='すべてのチャートを作成'
    )
    parser.add_argument(
        '--create-dashboard',
        action='store_true',
        help='ダッシュボードを作成'
    )
    parser.add_argument(
        '--create-html-report',
        action='store_true',
        help='HTMLレポートを作成'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='対象期間（日数）'
    )
    parser.add_argument(
        '--data-dir',
        default='logs/performance/gui',
        help='データディレクトリ'
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
            logging.FileHandler('logs/gui_responsiveness_visualizer.log', encoding='utf-8')
        ]
    )
    
    if not MATPLOTLIB_AVAILABLE:
        print("❌ matplotlibが利用できません。pip install matplotlibでインストールしてください。")
        return 1
    
    visualizer = ResponsivenessVisualizer(args.data_dir)
    
    try:
        if args.create_charts:
            # すべてのチャートを作成
            print("📊 チャートを作成中...")
            
            trend_chart = visualizer.create_response_time_trend_chart(args.days)
            if trend_chart:
                print(f"✅ 応答時間トレンドチャート: {trend_chart}")
            
            distribution_chart = visualizer.create_interaction_type_distribution_chart(args.days)
            if distribution_chart:
                print(f"✅ インタラクション分布チャート: {distribution_chart}")
            
            success_chart = visualizer.create_success_rate_chart(args.days)
            if success_chart:
                print(f"✅ 成功率チャート: {success_chart}")
            
            heatmap_chart = visualizer.create_performance_heatmap(args.days)
            if heatmap_chart:
                print(f"✅ パフォーマンスヒートマップ: {heatmap_chart}")
        
        elif args.create_dashboard:
            # ダッシュボードを作成
            print("📈 ダッシュボードを作成中...")
            dashboard = visualizer.create_comprehensive_dashboard(args.days)
            if dashboard:
                print(f"✅ ダッシュボード: {dashboard}")
            else:
                print("❌ ダッシュボードの作成に失敗しました")
        
        elif args.create_html_report:
            # HTMLレポートを作成
            print("📄 HTMLレポートを作成中...")
            html_report = visualizer.generate_html_report(args.days)
            if html_report:
                print(f"✅ HTMLレポート: {html_report}")
            else:
                print("❌ HTMLレポートの作成に失敗しました")
        
        else:
            # デフォルト: すべて作成
            print("📊 すべての可視化を作成中...")
            
            # チャート作成
            visualizer.create_response_time_trend_chart(args.days)
            visualizer.create_interaction_type_distribution_chart(args.days)
            visualizer.create_success_rate_chart(args.days)
            visualizer.create_performance_heatmap(args.days)
            
            # ダッシュボード作成
            dashboard = visualizer.create_comprehensive_dashboard(args.days)
            
            # HTMLレポート作成
            html_report = visualizer.generate_html_report(args.days)
            
            if dashboard and html_report:
                print(f"✅ すべての可視化を作成しました")
                print(f"   ダッシュボード: {dashboard}")
                print(f"   HTMLレポート: {html_report}")
            else:
                print("⚠️ 一部の可視化の作成に失敗しました")
    
    except KeyboardInterrupt:
        logger.info("ユーザーによって中断されました")
        return 1
    except Exception as e:
        logger.error(f"予期しないエラーが発生: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())