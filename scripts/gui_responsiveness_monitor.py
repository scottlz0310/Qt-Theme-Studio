#!/usr/bin/env python3
"""
GUI応答性測定システム

このモジュールは、Qt アプリケーションの応答時間測定機能、
ユーザーインタラクションのシミュレーション、応答性メトリクスの可視化を提供します。
"""

import json
import logging
import statistics
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
import threading
import queue
import sys
import subprocess

# Qt関連のインポート（動的インポート）
try:
    from PySide6.QtCore import QTimer, QEventLoop, QCoreApplication, QThread, pyqtSignal
    from PySide6.QtWidgets import QApplication, QWidget
    from PySide6.QtTest import QTest
    from PySide6.QtCore import Qt
    QT_AVAILABLE = True
except ImportError:
    try:
        from PyQt6.QtCore import QTimer, QEventLoop, QCoreApplication, QThread, pyqtSignal
        from PyQt6.QtWidgets import QApplication, QWidget
        from PyQt6.QtTest import QTest
        from PyQt6.QtCore import Qt
        QT_AVAILABLE = True
    except ImportError:
        try:
            from PyQt5.QtCore import QTimer, QEventLoop, QCoreApplication, QThread, pyqtSignal
            from PyQt5.QtWidgets import QApplication, QWidget
            from PyQt5.QtTest import QTest
            from PyQt5.QtCore import Qt
            QT_AVAILABLE = True
        except ImportError:
            QT_AVAILABLE = False

# ログ設定
logger = logging.getLogger(__name__)


@dataclass
class InteractionEvent:
    """ユーザーインタラクションイベント"""
    event_type: str  # 'click', 'key_press', 'mouse_move', 'scroll', etc.
    target_widget: str
    timestamp: datetime
    parameters: Dict[str, Any]
    expected_response_time: float = 0.1  # 期待される応答時間（秒）


@dataclass
class ResponseMeasurement:
    """応答性測定結果"""
    event: InteractionEvent
    start_time: datetime
    end_time: datetime
    response_time: float  # 実際の応答時間（秒）
    success: bool
    error_message: Optional[str] = None
    ui_state_before: Optional[Dict[str, Any]] = None
    ui_state_after: Optional[Dict[str, Any]] = None


@dataclass
class ResponsivenessMetrics:
    """応答性メトリクス"""
    measurement_session: str
    timestamp: datetime
    total_interactions: int
    successful_interactions: int
    failed_interactions: int
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    slowest_interaction: Optional[ResponseMeasurement]
    fastest_interaction: Optional[ResponseMeasurement]
    interactions_by_type: Dict[str, int]
    response_times_by_type: Dict[str, List[float]]


class UIStateCapture:
    """UI状態キャプチャクラス"""
    
    def __init__(self):
        self.logger = get_logger()
    
    def capture_widget_state(self, widget) -> Dict[str, Any]:
        """ウィジェットの状態をキャプチャ"""
        if not QT_AVAILABLE or not widget:
            return {}
        
        try:
            state = {
                'class_name': widget.__class__.__name__,
                'object_name': widget.objectName(),
                'enabled': widget.isEnabled(),
                'visible': widget.isVisible(),
                'geometry': {
                    'x': widget.x(),
                    'y': widget.y(),
                    'width': widget.width(),
                    'height': widget.height()
                },
                'focus': widget.hasFocus(),
                'timestamp': datetime.now().isoformat()
            }
            
            # ウィジェット固有の状態を追加
            if hasattr(widget, 'text'):
                state['text'] = widget.text()
            if hasattr(widget, 'isChecked'):
                state['checked'] = widget.isChecked()
            if hasattr(widget, 'currentText'):
                state['current_text'] = widget.currentText()
            if hasattr(widget, 'value'):
                state['value'] = widget.value()
            
            return state
            
        except Exception as e:
            self.logger.error(f"ウィジェット状態キャプチャエラー: {e}")
            return {}
    
    def capture_application_state(self) -> Dict[str, Any]:
        """アプリケーション全体の状態をキャプチャ"""
        if not QT_AVAILABLE:
            return {}
        
        try:
            app = QApplication.instance()
            if not app:
                return {}
            
            state = {
                'active_window': None,
                'all_widgets': [],
                'focus_widget': None,
                'timestamp': datetime.now().isoformat()
            }
            
            # アクティブウィンドウ
            active_window = app.activeWindow()
            if active_window:
                state['active_window'] = self.capture_widget_state(active_window)
            
            # フォーカスウィジェット
            focus_widget = app.focusWidget()
            if focus_widget:
                state['focus_widget'] = self.capture_widget_state(focus_widget)
            
            # 全ウィジェット（トップレベルのみ）
            for widget in app.allWidgets():
                if widget.isWindow():
                    state['all_widgets'].append(self.capture_widget_state(widget))
            
            return state
            
        except Exception as e:
            self.logger.error(f"アプリケーション状態キャプチャエラー: {e}")
            return {}


class InteractionSimulator:
    """ユーザーインタラクションシミュレータ"""
    
    def __init__(self):
        self.logger = get_logger()
        self.state_capture = UIStateCapture()
    
    def simulate_click(self, widget, button=None) -> ResponseMeasurement:
        """クリックイベントをシミュレート"""
        if not QT_AVAILABLE or not widget:
            return self._create_failed_measurement("Qt not available or widget is None")
        
        event = InteractionEvent(
            event_type="click",
            target_widget=widget.objectName() or widget.__class__.__name__,
            timestamp=datetime.now(),
            parameters={"button": button or "left"}
        )
        
        try:
            # UI状態をキャプチャ（前）
            ui_state_before = self.state_capture.capture_widget_state(widget)
            
            # 応答時間測定開始
            start_time = datetime.now()
            start_perf = time.perf_counter()
            
            # クリックイベントを送信
            if button == "right":
                QTest.mouseClick(widget, Qt.MouseButton.RightButton)
            else:
                QTest.mouseClick(widget, Qt.MouseButton.LeftButton)
            
            # イベント処理を待機
            QCoreApplication.processEvents()
            
            # 応答時間測定終了
            end_perf = time.perf_counter()
            end_time = datetime.now()
            response_time = end_perf - start_perf
            
            # UI状態をキャプチャ（後）
            ui_state_after = self.state_capture.capture_widget_state(widget)
            
            return ResponseMeasurement(
                event=event,
                start_time=start_time,
                end_time=end_time,
                response_time=response_time,
                success=True,
                ui_state_before=ui_state_before,
                ui_state_after=ui_state_after
            )
            
        except Exception as e:
            return self._create_failed_measurement(f"クリックシミュレーションエラー: {e}", event)
    
    def simulate_key_press(self, widget, key, modifiers=None) -> ResponseMeasurement:
        """キー押下イベントをシミュレート"""
        if not QT_AVAILABLE or not widget:
            return self._create_failed_measurement("Qt not available or widget is None")
        
        event = InteractionEvent(
            event_type="key_press",
            target_widget=widget.objectName() or widget.__class__.__name__,
            timestamp=datetime.now(),
            parameters={"key": str(key), "modifiers": str(modifiers) if modifiers else None}
        )
        
        try:
            # UI状態をキャプチャ（前）
            ui_state_before = self.state_capture.capture_widget_state(widget)
            
            # 応答時間測定開始
            start_time = datetime.now()
            start_perf = time.perf_counter()
            
            # キー押下イベントを送信
            if modifiers:
                QTest.keyClick(widget, key, modifiers)
            else:
                QTest.keyClick(widget, key)
            
            # イベント処理を待機
            QCoreApplication.processEvents()
            
            # 応答時間測定終了
            end_perf = time.perf_counter()
            end_time = datetime.now()
            response_time = end_perf - start_perf
            
            # UI状態をキャプチャ（後）
            ui_state_after = self.state_capture.capture_widget_state(widget)
            
            return ResponseMeasurement(
                event=event,
                start_time=start_time,
                end_time=end_time,
                response_time=response_time,
                success=True,
                ui_state_before=ui_state_before,
                ui_state_after=ui_state_after
            )
            
        except Exception as e:
            return self._create_failed_measurement(f"キー押下シミュレーションエラー: {e}", event)
    
    def simulate_text_input(self, widget, text: str) -> ResponseMeasurement:
        """テキスト入力をシミュレート"""
        if not QT_AVAILABLE or not widget:
            return self._create_failed_measurement("Qt not available or widget is None")
        
        event = InteractionEvent(
            event_type="text_input",
            target_widget=widget.objectName() or widget.__class__.__name__,
            timestamp=datetime.now(),
            parameters={"text": text}
        )
        
        try:
            # UI状態をキャプチャ（前）
            ui_state_before = self.state_capture.capture_widget_state(widget)
            
            # 応答時間測定開始
            start_time = datetime.now()
            start_perf = time.perf_counter()
            
            # テキスト入力をシミュレート
            widget.setFocus()
            QTest.keyClicks(widget, text)
            
            # イベント処理を待機
            QCoreApplication.processEvents()
            
            # 応答時間測定終了
            end_perf = time.perf_counter()
            end_time = datetime.now()
            response_time = end_perf - start_perf
            
            # UI状態をキャプチャ（後）
            ui_state_after = self.state_capture.capture_widget_state(widget)
            
            return ResponseMeasurement(
                event=event,
                start_time=start_time,
                end_time=end_time,
                response_time=response_time,
                success=True,
                ui_state_before=ui_state_before,
                ui_state_after=ui_state_after
            )
            
        except Exception as e:
            return self._create_failed_measurement(f"テキスト入力シミュレーションエラー: {e}", event)
    
    def simulate_window_resize(self, widget, width: int, height: int) -> ResponseMeasurement:
        """ウィンドウリサイズをシミュレート"""
        if not QT_AVAILABLE or not widget:
            return self._create_failed_measurement("Qt not available or widget is None")
        
        event = InteractionEvent(
            event_type="window_resize",
            target_widget=widget.objectName() or widget.__class__.__name__,
            timestamp=datetime.now(),
            parameters={"width": width, "height": height}
        )
        
        try:
            # UI状態をキャプチャ（前）
            ui_state_before = self.state_capture.capture_widget_state(widget)
            
            # 応答時間測定開始
            start_time = datetime.now()
            start_perf = time.perf_counter()
            
            # ウィンドウリサイズを実行
            widget.resize(width, height)
            
            # イベント処理を待機
            QCoreApplication.processEvents()
            
            # 応答時間測定終了
            end_perf = time.perf_counter()
            end_time = datetime.now()
            response_time = end_perf - start_perf
            
            # UI状態をキャプチャ（後）
            ui_state_after = self.state_capture.capture_widget_state(widget)
            
            return ResponseMeasurement(
                event=event,
                start_time=start_time,
                end_time=end_time,
                response_time=response_time,
                success=True,
                ui_state_before=ui_state_before,
                ui_state_after=ui_state_after
            )
            
        except Exception as e:
            return self._create_failed_measurement(f"ウィンドウリサイズシミュレーションエラー: {e}", event)
    
    def _create_failed_measurement(self, error_message: str, event: Optional[InteractionEvent] = None) -> ResponseMeasurement:
        """失敗した測定結果を作成"""
        if event is None:
            event = InteractionEvent(
                event_type="unknown",
                target_widget="unknown",
                timestamp=datetime.now(),
                parameters={}
            )
        
        return ResponseMeasurement(
            event=event,
            start_time=datetime.now(),
            end_time=datetime.now(),
            response_time=0.0,
            success=False,
            error_message=error_message
        )


class ResponsivenessMonitor:
    """GUI応答性監視システム"""
    
    def __init__(self, data_dir: str = "logs/performance/gui"):
        """
        GUI応答性監視システムを初期化
        
        Args:
            data_dir: データ保存ディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.measurements_file = self.data_dir / "responsiveness_measurements.json"
        self.metrics_file = self.data_dir / "responsiveness_metrics.json"
        
        self.simulator = InteractionSimulator()
        self.state_capture = UIStateCapture()
        
        # 応答性閾値設定
        self.thresholds = {
            'excellent': 0.05,   # 50ms以下
            'good': 0.1,         # 100ms以下
            'acceptable': 0.2,   # 200ms以下
            'poor': 0.5,         # 500ms以下
            'unacceptable': 1.0  # 1秒以上
        }
        
        self.logger = get_logger()
        self.logger.info("GUI応答性監視システムを初期化しました")
    
    def run_responsiveness_test(self, widget, test_scenarios: List[Dict[str, Any]]) -> ResponsivenessMetrics:
        """
        応答性テストを実行
        
        Args:
            widget: テスト対象のウィジェット
            test_scenarios: テストシナリオのリスト
            
        Returns:
            ResponsivenessMetrics: 応答性メトリクス
        """
        if not QT_AVAILABLE:
            self.logger.error("Qtが利用できません")
            return self._create_empty_metrics("Qt not available")
        
        session_id = f"test_{int(time.time())}"
        self.logger.info(f"応答性テストを開始: {session_id}")
        
        measurements = []
        
        for i, scenario in enumerate(test_scenarios):
            self.logger.info(f"シナリオ {i+1}/{len(test_scenarios)} を実行中: {scenario.get('name', 'unnamed')}")
            
            try:
                measurement = self._execute_scenario(widget, scenario)
                measurements.append(measurement)
                
                # シナリオ間の待機時間
                wait_time = scenario.get('wait_after', 0.1)
                if wait_time > 0:
                    time.sleep(wait_time)
                
            except Exception as e:
                self.logger.error(f"シナリオ実行エラー: {e}")
                # エラーの場合も測定結果として記録
                error_measurement = ResponseMeasurement(
                    event=InteractionEvent(
                        event_type=scenario.get('type', 'unknown'),
                        target_widget=widget.objectName() if widget else 'unknown',
                        timestamp=datetime.now(),
                        parameters=scenario
                    ),
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    response_time=0.0,
                    success=False,
                    error_message=str(e)
                )
                measurements.append(error_measurement)
        
        # メトリクスを計算
        metrics = self._calculate_metrics(session_id, measurements)
        
        # 結果を保存
        self._save_measurements(measurements)
        self._save_metrics(metrics)
        
        self.logger.info(f"応答性テスト完了: {len(measurements)}個の測定を実行")
        return metrics
    
    def _execute_scenario(self, widget, scenario: Dict[str, Any]) -> ResponseMeasurement:
        """個別のテストシナリオを実行"""
        scenario_type = scenario.get('type', 'click')
        
        if scenario_type == 'click':
            button = scenario.get('button', 'left')
            return self.simulator.simulate_click(widget, button)
        
        elif scenario_type == 'key_press':
            key = scenario.get('key', Qt.Key.Key_Space)
            modifiers = scenario.get('modifiers')
            return self.simulator.simulate_key_press(widget, key, modifiers)
        
        elif scenario_type == 'text_input':
            text = scenario.get('text', 'test')
            return self.simulator.simulate_text_input(widget, text)
        
        elif scenario_type == 'window_resize':
            width = scenario.get('width', 800)
            height = scenario.get('height', 600)
            return self.simulator.simulate_window_resize(widget, width, height)
        
        else:
            raise ValueError(f"未対応のシナリオタイプ: {scenario_type}")
    
    def _calculate_metrics(self, session_id: str, measurements: List[ResponseMeasurement]) -> ResponsivenessMetrics:
        """応答性メトリクスを計算"""
        if not measurements:
            return self._create_empty_metrics(session_id)
        
        # 成功した測定のみを対象
        successful_measurements = [m for m in measurements if m.success]
        failed_measurements = [m for m in measurements if not m.success]
        
        if not successful_measurements:
            return ResponsivenessMetrics(
                measurement_session=session_id,
                timestamp=datetime.now(),
                total_interactions=len(measurements),
                successful_interactions=0,
                failed_interactions=len(failed_measurements),
                average_response_time=0.0,
                median_response_time=0.0,
                p95_response_time=0.0,
                p99_response_time=0.0,
                slowest_interaction=None,
                fastest_interaction=None,
                interactions_by_type={},
                response_times_by_type={}
            )
        
        # 応答時間の統計を計算
        response_times = [m.response_time for m in successful_measurements]
        
        average_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        
        # パーセンタイル計算
        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        
        p95_response_time = sorted_times[min(p95_index, len(sorted_times) - 1)]
        p99_response_time = sorted_times[min(p99_index, len(sorted_times) - 1)]
        
        # 最速・最遅のインタラクション
        slowest_measurement = max(successful_measurements, key=lambda m: m.response_time)
        fastest_measurement = min(successful_measurements, key=lambda m: m.response_time)
        
        # インタラクションタイプ別の統計
        interactions_by_type = {}
        response_times_by_type = {}
        
        for measurement in measurements:
            event_type = measurement.event.event_type
            interactions_by_type[event_type] = interactions_by_type.get(event_type, 0) + 1
            
            if measurement.success:
                if event_type not in response_times_by_type:
                    response_times_by_type[event_type] = []
                response_times_by_type[event_type].append(measurement.response_time)
        
        return ResponsivenessMetrics(
            measurement_session=session_id,
            timestamp=datetime.now(),
            total_interactions=len(measurements),
            successful_interactions=len(successful_measurements),
            failed_interactions=len(failed_measurements),
            average_response_time=average_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            slowest_interaction=slowest_measurement,
            fastest_interaction=fastest_measurement,
            interactions_by_type=interactions_by_type,
            response_times_by_type=response_times_by_type
        )
    
    def _create_empty_metrics(self, session_id: str) -> ResponsivenessMetrics:
        """空のメトリクスを作成"""
        return ResponsivenessMetrics(
            measurement_session=session_id,
            timestamp=datetime.now(),
            total_interactions=0,
            successful_interactions=0,
            failed_interactions=0,
            average_response_time=0.0,
            median_response_time=0.0,
            p95_response_time=0.0,
            p99_response_time=0.0,
            slowest_interaction=None,
            fastest_interaction=None,
            interactions_by_type={},
            response_times_by_type={}
        )
    
    def _save_measurements(self, measurements: List[ResponseMeasurement]) -> None:
        """測定結果を保存"""
        try:
            # 既存の測定結果を読み込み
            existing_measurements = []
            if self.measurements_file.exists():
                with open(self.measurements_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing_measurements = data.get('measurements', [])
            
            # 新しい測定結果を追加
            for measurement in measurements:
                measurement_dict = asdict(measurement)
                # datetimeオブジェクトをISO形式の文字列に変換
                measurement_dict['start_time'] = measurement.start_time.isoformat()
                measurement_dict['end_time'] = measurement.end_time.isoformat()
                measurement_dict['event']['timestamp'] = measurement.event.timestamp.isoformat()
                existing_measurements.append(measurement_dict)
            
            # 古い測定結果を削除（30日以上前）
            cutoff_date = datetime.now() - timedelta(days=30)
            filtered_measurements = []
            for m in existing_measurements:
                try:
                    measurement_time = datetime.fromisoformat(m['start_time'])
                    if measurement_time >= cutoff_date:
                        filtered_measurements.append(m)
                except (ValueError, KeyError):
                    # 無効なデータはスキップ
                    continue
            
            # ファイルに保存
            with open(self.measurements_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'measurements': filtered_measurements,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"測定結果を保存しました: {len(measurements)}件")
            
        except Exception as e:
            self.logger.error(f"測定結果保存エラー: {e}")
    
    def _save_metrics(self, metrics: ResponsivenessMetrics) -> None:
        """メトリクスを保存"""
        try:
            # 既存のメトリクスを読み込み
            existing_metrics = []
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing_metrics = data.get('metrics', [])
            
            # 新しいメトリクスを追加
            metrics_dict = asdict(metrics)
            metrics_dict['timestamp'] = metrics.timestamp.isoformat()
            
            # slowest_interaction と fastest_interaction の処理
            if metrics.slowest_interaction:
                slowest_dict = asdict(metrics.slowest_interaction)
                slowest_dict['start_time'] = metrics.slowest_interaction.start_time.isoformat()
                slowest_dict['end_time'] = metrics.slowest_interaction.end_time.isoformat()
                slowest_dict['event']['timestamp'] = metrics.slowest_interaction.event.timestamp.isoformat()
                metrics_dict['slowest_interaction'] = slowest_dict
            
            if metrics.fastest_interaction:
                fastest_dict = asdict(metrics.fastest_interaction)
                fastest_dict['start_time'] = metrics.fastest_interaction.start_time.isoformat()
                fastest_dict['end_time'] = metrics.fastest_interaction.end_time.isoformat()
                fastest_dict['event']['timestamp'] = metrics.fastest_interaction.event.timestamp.isoformat()
                metrics_dict['fastest_interaction'] = fastest_dict
            
            existing_metrics.append(metrics_dict)
            
            # 古いメトリクスを削除（30日以上前）
            cutoff_date = datetime.now() - timedelta(days=30)
            filtered_metrics = []
            for m in existing_metrics:
                try:
                    metrics_time = datetime.fromisoformat(m['timestamp'])
                    if metrics_time >= cutoff_date:
                        filtered_metrics.append(m)
                except (ValueError, KeyError):
                    # 無効なデータはスキップ
                    continue
            
            # ファイルに保存
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'metrics': filtered_metrics,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info("応答性メトリクスを保存しました")
            
        except Exception as e:
            self.logger.error(f"メトリクス保存エラー: {e}")
    
    def generate_responsiveness_report(self, days: int = 7) -> Dict[str, Any]:
        """
        応答性レポートを生成
        
        Args:
            days: レポート対象期間（日数）
            
        Returns:
            Dict[str, Any]: 応答性レポート
        """
        self.logger.info(f"過去{days}日間の応答性レポートを生成中")
        
        try:
            # メトリクスデータを読み込み
            if not self.metrics_file.exists():
                return self._create_empty_report(days)
            
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_metrics = data.get('metrics', [])
            
            # 期間内のメトリクスをフィルタリング
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_metrics = []
            
            for metrics_data in all_metrics:
                try:
                    metrics_time = datetime.fromisoformat(metrics_data['timestamp'])
                    if metrics_time >= cutoff_date:
                        recent_metrics.append(metrics_data)
                except (ValueError, KeyError):
                    continue
            
            if not recent_metrics:
                return self._create_empty_report(days)
            
            # レポートを生成
            report = self._analyze_metrics_data(recent_metrics, days)
            
            self.logger.info("応答性レポートを生成しました")
            return report
            
        except Exception as e:
            self.logger.error(f"応答性レポート生成エラー: {e}")
            return self._create_empty_report(days)
    
    def _analyze_metrics_data(self, metrics_data: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
        """メトリクスデータを分析してレポートを生成"""
        total_sessions = len(metrics_data)
        total_interactions = sum(m.get('total_interactions', 0) for m in metrics_data)
        total_successful = sum(m.get('successful_interactions', 0) for m in metrics_data)
        total_failed = sum(m.get('failed_interactions', 0) for m in metrics_data)
        
        # 応答時間の統計
        all_avg_times = [m.get('average_response_time', 0) for m in metrics_data if m.get('average_response_time', 0) > 0]
        all_p95_times = [m.get('p95_response_time', 0) for m in metrics_data if m.get('p95_response_time', 0) > 0]
        
        overall_avg_response_time = statistics.mean(all_avg_times) if all_avg_times else 0
        overall_p95_response_time = statistics.mean(all_p95_times) if all_p95_times else 0
        
        # 成功率
        success_rate = (total_successful / total_interactions * 100) if total_interactions > 0 else 0
        
        # インタラクションタイプ別の統計
        interaction_types = {}
        for metrics in metrics_data:
            for interaction_type, count in metrics.get('interactions_by_type', {}).items():
                interaction_types[interaction_type] = interaction_types.get(interaction_type, 0) + count
        
        # 応答性評価
        responsiveness_grade = self._calculate_responsiveness_grade(overall_avg_response_time)
        
        # トレンド分析
        trend_analysis = self._analyze_trends(metrics_data)
        
        return {
            'period': f"{days}日間",
            'summary': {
                'total_sessions': total_sessions,
                'total_interactions': total_interactions,
                'successful_interactions': total_successful,
                'failed_interactions': total_failed,
                'success_rate': round(success_rate, 2),
                'overall_avg_response_time': round(overall_avg_response_time, 4),
                'overall_p95_response_time': round(overall_p95_response_time, 4),
                'responsiveness_grade': responsiveness_grade
            },
            'interaction_types': interaction_types,
            'trend_analysis': trend_analysis,
            'recommendations': self._generate_recommendations(overall_avg_response_time, success_rate, interaction_types)
        }
    
    def _calculate_responsiveness_grade(self, avg_response_time: float) -> str:
        """応答性の評価グレードを計算"""
        if avg_response_time <= self.thresholds['excellent']:
            return 'A+ (優秀)'
        elif avg_response_time <= self.thresholds['good']:
            return 'A (良好)'
        elif avg_response_time <= self.thresholds['acceptable']:
            return 'B (許容範囲)'
        elif avg_response_time <= self.thresholds['poor']:
            return 'C (改善が必要)'
        else:
            return 'D (大幅な改善が必要)'
    
    def _analyze_trends(self, metrics_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """トレンド分析を実行"""
        if len(metrics_data) < 2:
            return {'trend': '不明', 'change_rate': 0}
        
        # 時系列でソート
        sorted_metrics = sorted(metrics_data, key=lambda x: x.get('timestamp', ''))
        
        # 応答時間のトレンド
        response_times = [m.get('average_response_time', 0) for m in sorted_metrics]
        
        if len(response_times) >= 2:
            # 線形回帰の傾きを計算
            n = len(response_times)
            x = list(range(n))
            
            sum_x = sum(x)
            sum_y = sum(response_times)
            sum_xy = sum(x[i] * response_times[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            if n * sum_x2 - sum_x ** 2 != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
                
                if slope > 0.001:
                    trend = '悪化'
                elif slope < -0.001:
                    trend = '改善'
                else:
                    trend = '安定'
                
                # 変化率を計算
                first_value = response_times[0]
                last_value = response_times[-1]
                change_rate = ((last_value - first_value) / first_value * 100) if first_value > 0 else 0
                
                return {
                    'trend': trend,
                    'change_rate': round(change_rate, 2),
                    'slope': round(slope, 6)
                }
        
        return {'trend': '不明', 'change_rate': 0}
    
    def _generate_recommendations(self, avg_response_time: float, success_rate: float, interaction_types: Dict[str, int]) -> List[str]:
        """改善提案を生成"""
        recommendations = []
        
        # 応答時間に基づく提案
        if avg_response_time > self.thresholds['poor']:
            recommendations.append("応答時間が非常に遅いです。UIスレッドでの重い処理を別スレッドに移動することを検討してください。")
        elif avg_response_time > self.thresholds['acceptable']:
            recommendations.append("応答時間が許容範囲を超えています。処理の最適化を検討してください。")
        
        # 成功率に基づく提案
        if success_rate < 90:
            recommendations.append("インタラクションの成功率が低いです。エラーハンドリングの改善を検討してください。")
        elif success_rate < 95:
            recommendations.append("インタラクションの成功率を向上させる余地があります。")
        
        # インタラクションタイプに基づく提案
        if interaction_types.get('window_resize', 0) > 0:
            recommendations.append("ウィンドウリサイズの応答性を改善するため、レイアウトの最適化を検討してください。")
        
        if interaction_types.get('text_input', 0) > 0:
            recommendations.append("テキスト入力の応答性向上のため、入力検証の最適化を検討してください。")
        
        if not recommendations:
            recommendations.append("現在の応答性は良好です。この状態を維持してください。")
        
        return recommendations
    
    def _create_empty_report(self, days: int) -> Dict[str, Any]:
        """空のレポートを作成"""
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


def get_logger():
    """ロガーを取得"""
    return logging.getLogger(__name__)


def create_default_test_scenarios() -> List[Dict[str, Any]]:
    """デフォルトのテストシナリオを作成"""
    if not QT_AVAILABLE:
        return []
    
    return [
        {
            'name': 'ボタンクリック',
            'type': 'click',
            'button': 'left',
            'wait_after': 0.1
        },
        {
            'name': '右クリック',
            'type': 'click',
            'button': 'right',
            'wait_after': 0.1
        },
        {
            'name': 'スペースキー押下',
            'type': 'key_press',
            'key': Qt.Key.Key_Space,
            'wait_after': 0.1
        },
        {
            'name': 'Enterキー押下',
            'type': 'key_press',
            'key': Qt.Key.Key_Return,
            'wait_after': 0.1
        },
        {
            'name': 'テキスト入力',
            'type': 'text_input',
            'text': 'テスト入力',
            'wait_after': 0.2
        },
        {
            'name': 'ウィンドウリサイズ（大）',
            'type': 'window_resize',
            'width': 1200,
            'height': 800,
            'wait_after': 0.3
        },
        {
            'name': 'ウィンドウリサイズ（小）',
            'type': 'window_resize',
            'width': 600,
            'height': 400,
            'wait_after': 0.3
        }
    ]


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GUI応答性測定システム")
    parser.add_argument(
        '--test-app',
        action='store_true',
        help='テストアプリケーションで応答性テストを実行'
    )
    parser.add_argument(
        '--generate-report',
        type=int,
        metavar='DAYS',
        help='指定日数の応答性レポートを生成'
    )
    parser.add_argument(
        '--data-dir',
        default='logs/performance/gui',
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
            logging.FileHandler('logs/gui_responsiveness_monitor.log', encoding='utf-8')
        ]
    )
    
    monitor = ResponsivenessMonitor(args.data_dir)
    
    try:
        if args.test_app:
            if not QT_AVAILABLE:
                print("❌ Qtが利用できません。PySide6、PyQt6、またはPyQt5をインストールしてください。")
                return 1
            
            # テストアプリケーションを作成
            app = QApplication.instance() or QApplication(sys.argv)
            
            # シンプルなテストウィジェットを作成
            test_widget = QWidget()
            test_widget.setWindowTitle("GUI応答性テスト")
            test_widget.resize(800, 600)
            test_widget.show()
            
            # テストシナリオを実行
            scenarios = create_default_test_scenarios()
            metrics = monitor.run_responsiveness_test(test_widget, scenarios)
            
            # 結果を表示
            print(f"\n📊 GUI応答性テスト結果:")
            print(f"総インタラクション数: {metrics.total_interactions}")
            print(f"成功: {metrics.successful_interactions}")
            print(f"失敗: {metrics.failed_interactions}")
            print(f"平均応答時間: {metrics.average_response_time:.4f}秒")
            print(f"95パーセンタイル: {metrics.p95_response_time:.4f}秒")
            
            if metrics.slowest_interaction:
                print(f"最遅インタラクション: {metrics.slowest_interaction.event.event_type} ({metrics.slowest_interaction.response_time:.4f}秒)")
            
            if metrics.fastest_interaction:
                print(f"最速インタラクション: {metrics.fastest_interaction.event.event_type} ({metrics.fastest_interaction.response_time:.4f}秒)")
            
            test_widget.close()
        
        elif args.generate_report is not None:
            # レポート生成
            report = monitor.generate_responsiveness_report(args.generate_report)
            
            print(f"\n📈 GUI応答性レポート ({report['period']})")
            summary = report['summary']
            print(f"セッション数: {summary['total_sessions']}")
            print(f"総インタラクション数: {summary['total_interactions']}")
            print(f"成功率: {summary['success_rate']}%")
            print(f"平均応答時間: {summary['overall_avg_response_time']:.4f}秒")
            print(f"応答性評価: {summary['responsiveness_grade']}")
            
            trend = report['trend_analysis']
            print(f"トレンド: {trend['trend']} ({trend['change_rate']:+.2f}%)")
            
            print("\n💡 改善提案:")
            for i, recommendation in enumerate(report['recommendations'], 1):
                print(f"  {i}. {recommendation}")
        
        else:
            print("使用方法:")
            print("  --test-app: テストアプリケーションで応答性テストを実行")
            print("  --generate-report DAYS: 指定日数の応答性レポートを生成")
            print("  --verbose: 詳細ログを出力")
    
    except KeyboardInterrupt:
        logger.info("ユーザーによって中断されました")
        return 1
    except Exception as e:
        logger.error(f"予期しないエラーが発生: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())