#!/usr/bin/env python3
"""
パフォーマンス監視システム設定

このモジュールは、パフォーマンス監視システムの設定を管理します。
"""

import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class ThresholdConfig:
    """回帰検出閾値設定"""
    low: float = 5.0      # 5%以上の性能低下
    medium: float = 15.0  # 15%以上の性能低下
    high: float = 30.0    # 30%以上の性能低下
    critical: float = 50.0 # 50%以上の性能低下


@dataclass
class BenchmarkConfig:
    """ベンチマーク設定"""
    name: str
    test_pattern: str
    timeout: int = 300  # 5分
    min_iterations: int = 3
    max_iterations: int = 10
    warmup_iterations: int = 1
    enabled: bool = True
    custom_thresholds: Optional[ThresholdConfig] = None


@dataclass
class AlertConfig:
    """アラート設定"""
    enabled: bool = True
    email_notifications: bool = False
    slack_webhook: Optional[str] = None
    github_issues: bool = False
    severity_levels: List[str] = None
    
    def __post_init__(self):
        if self.severity_levels is None:
            self.severity_levels = ['MEDIUM', 'HIGH', 'CRITICAL']


@dataclass
class PerformanceConfig:
    """パフォーマンス監視システム全体設定"""
    data_dir: str = "logs/performance"
    retention_days: int = 90
    min_samples: int = 3
    confidence_level: float = 0.95
    
    default_thresholds: ThresholdConfig = None
    benchmarks: List[BenchmarkConfig] = None
    alerts: AlertConfig = None
    
    def __post_init__(self):
        if self.default_thresholds is None:
            self.default_thresholds = ThresholdConfig()
        
        if self.benchmarks is None:
            self.benchmarks = self._get_default_benchmarks()
        
        if self.alerts is None:
            self.alerts = AlertConfig()
    
    def _get_default_benchmarks(self) -> List[BenchmarkConfig]:
        """デフォルトベンチマーク設定を取得"""
        return [
            BenchmarkConfig(
                name="theme_loading",
                test_pattern="test_theme_loading_benchmark",
                timeout=60,
                min_iterations=5
            ),
            BenchmarkConfig(
                name="large_theme_loading", 
                test_pattern="test_large_theme_loading_benchmark",
                timeout=120,
                min_iterations=3
            ),
            BenchmarkConfig(
                name="theme_validation",
                test_pattern="test_theme_validation_benchmark",
                timeout=30,
                min_iterations=5
            ),
            BenchmarkConfig(
                name="css_generation",
                test_pattern="test_css_generation_benchmark",
                timeout=60,
                min_iterations=3
            ),
            BenchmarkConfig(
                name="theme_export",
                test_pattern="test_theme_export_benchmark",
                timeout=60,
                min_iterations=3
            ),
            BenchmarkConfig(
                name="file_operations",
                test_pattern="test_file_*_benchmark",
                timeout=30,
                min_iterations=5
            ),
            BenchmarkConfig(
                name="memory_usage",
                test_pattern="test_*_memory_*_benchmark",
                timeout=120,
                min_iterations=3,
                custom_thresholds=ThresholdConfig(
                    low=10.0,    # メモリ使用量は10%から警告
                    medium=25.0,
                    high=50.0,
                    critical=75.0
                )
            )
        ]


class PerformanceConfigManager:
    """パフォーマンス設定管理クラス"""
    
    def __init__(self, config_path: str = ".kiro/performance/config.json"):
        """
        設定管理を初期化
        
        Args:
            config_path: 設定ファイルパス
        """
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Optional[PerformanceConfig] = None
    
    def load_config(self) -> PerformanceConfig:
        """設定を読み込み"""
        if self._config is not None:
            return self._config
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # JSONからデータクラスに変換
                config_dict = self._convert_from_json(data)
                self._config = PerformanceConfig(**config_dict)
                
                logger.info(f"設定を読み込みました: {self.config_path}")
                return self._config
                
            except Exception as e:
                logger.error(f"設定読み込みに失敗: {e}")
                logger.info("デフォルト設定を使用します")
        
        # デフォルト設定を作成
        self._config = PerformanceConfig()
        self.save_config()
        return self._config
    
    def save_config(self) -> None:
        """設定を保存"""
        if self._config is None:
            return
        
        try:
            # データクラスをJSONに変換
            data = self._convert_to_json(asdict(self._config))
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"設定を保存しました: {self.config_path}")
            
        except Exception as e:
            logger.error(f"設定保存に失敗: {e}")
    
    def get_benchmark_config(self, name: str) -> Optional[BenchmarkConfig]:
        """指定されたベンチマーク設定を取得"""
        config = self.load_config()
        
        for benchmark in config.benchmarks:
            if benchmark.name == name:
                return benchmark
        
        return None
    
    def update_benchmark_config(self, name: str, updates: Dict[str, Any]) -> bool:
        """ベンチマーク設定を更新"""
        config = self.load_config()
        
        for i, benchmark in enumerate(config.benchmarks):
            if benchmark.name == name:
                # 更新を適用
                for key, value in updates.items():
                    if hasattr(benchmark, key):
                        setattr(benchmark, key, value)
                
                self.save_config()
                logger.info(f"ベンチマーク設定を更新: {name}")
                return True
        
        logger.warning(f"ベンチマーク設定が見つかりません: {name}")
        return False
    
    def add_benchmark_config(self, benchmark: BenchmarkConfig) -> None:
        """新しいベンチマーク設定を追加"""
        config = self.load_config()
        
        # 既存の設定をチェック
        existing_names = [b.name for b in config.benchmarks]
        if benchmark.name in existing_names:
            logger.warning(f"ベンチマーク設定が既に存在します: {benchmark.name}")
            return
        
        config.benchmarks.append(benchmark)
        self.save_config()
        logger.info(f"新しいベンチマーク設定を追加: {benchmark.name}")
    
    def remove_benchmark_config(self, name: str) -> bool:
        """ベンチマーク設定を削除"""
        config = self.load_config()
        
        original_count = len(config.benchmarks)
        config.benchmarks = [b for b in config.benchmarks if b.name != name]
        
        if len(config.benchmarks) < original_count:
            self.save_config()
            logger.info(f"ベンチマーク設定を削除: {name}")
            return True
        
        logger.warning(f"削除対象のベンチマーク設定が見つかりません: {name}")
        return False
    
    def get_thresholds_for_benchmark(self, benchmark_name: str) -> ThresholdConfig:
        """指定されたベンチマークの閾値設定を取得"""
        benchmark = self.get_benchmark_config(benchmark_name)
        
        if benchmark and benchmark.custom_thresholds:
            return benchmark.custom_thresholds
        
        config = self.load_config()
        return config.default_thresholds
    
    def validate_config(self) -> List[str]:
        """設定の妥当性を検証"""
        config = self.load_config()
        errors = []
        
        # データディレクトリの検証
        if not config.data_dir:
            errors.append("data_dirが設定されていません")
        
        # 保持期間の検証
        if config.retention_days <= 0:
            errors.append("retention_daysは正の値である必要があります")
        
        # 最小サンプル数の検証
        if config.min_samples <= 0:
            errors.append("min_samplesは正の値である必要があります")
        
        # 信頼度の検証
        if not (0 < config.confidence_level < 1):
            errors.append("confidence_levelは0と1の間の値である必要があります")
        
        # ベンチマーク設定の検証
        benchmark_names = set()
        for benchmark in config.benchmarks:
            if not benchmark.name:
                errors.append("ベンチマーク名が設定されていません")
                continue
            
            if benchmark.name in benchmark_names:
                errors.append(f"重複するベンチマーク名: {benchmark.name}")
            benchmark_names.add(benchmark.name)
            
            if not benchmark.test_pattern:
                errors.append(f"テストパターンが設定されていません: {benchmark.name}")
            
            if benchmark.timeout <= 0:
                errors.append(f"タイムアウトは正の値である必要があります: {benchmark.name}")
            
            if benchmark.min_iterations <= 0:
                errors.append(f"最小反復回数は正の値である必要があります: {benchmark.name}")
        
        # 閾値設定の検証
        def validate_thresholds(thresholds: ThresholdConfig, context: str):
            if thresholds.low < 0:
                errors.append(f"{context}: low閾値は非負の値である必要があります")
            if thresholds.medium <= thresholds.low:
                errors.append(f"{context}: medium閾値はlow閾値より大きい必要があります")
            if thresholds.high <= thresholds.medium:
                errors.append(f"{context}: high閾値はmedium閾値より大きい必要があります")
            if thresholds.critical <= thresholds.high:
                errors.append(f"{context}: critical閾値はhigh閾値より大きい必要があります")
        
        validate_thresholds(config.default_thresholds, "デフォルト閾値")
        
        for benchmark in config.benchmarks:
            if benchmark.custom_thresholds:
                validate_thresholds(
                    benchmark.custom_thresholds, 
                    f"ベンチマーク '{benchmark.name}' のカスタム閾値"
                )
        
        return errors
    
    def _convert_to_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """データクラスをJSON形式に変換"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    result[key] = self._convert_to_json(value)
                elif isinstance(value, list):
                    result[key] = [self._convert_to_json(item) if isinstance(item, dict) else item for item in value]
                else:
                    result[key] = value
            return result
        return data
    
    def _convert_from_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """JSON形式からデータクラス用に変換"""
        result = {}
        
        for key, value in data.items():
            if key == 'default_thresholds' and isinstance(value, dict):
                result[key] = ThresholdConfig(**value)
            elif key == 'benchmarks' and isinstance(value, list):
                benchmarks = []
                for item in value:
                    if isinstance(item, dict):
                        # custom_thresholdsの処理
                        if 'custom_thresholds' in item and item['custom_thresholds']:
                            item['custom_thresholds'] = ThresholdConfig(**item['custom_thresholds'])
                        benchmarks.append(BenchmarkConfig(**item))
                result[key] = benchmarks
            elif key == 'alerts' and isinstance(value, dict):
                result[key] = AlertConfig(**value)
            else:
                result[key] = value
        
        return result


def main():
    """メイン実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="パフォーマンス監視設定管理")
    parser.add_argument(
        '--config-path',
        default='.kiro/performance/config.json',
        help='設定ファイルパス'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='設定の妥当性を検証'
    )
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='現在の設定を表示'
    )
    parser.add_argument(
        '--create-default',
        action='store_true',
        help='デフォルト設定ファイルを作成'
    )
    
    args = parser.parse_args()
    
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = PerformanceConfigManager(args.config_path)
    
    try:
        if args.create_default:
            config = PerformanceConfig()
            manager._config = config
            manager.save_config()
            print(f"✅ デフォルト設定ファイルを作成しました: {args.config_path}")
        
        elif args.validate:
            errors = manager.validate_config()
            if errors:
                print("❌ 設定に問題があります:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("✅ 設定は正常です")
        
        elif args.show_config:
            config = manager.load_config()
            print("📋 現在のパフォーマンス監視設定:")
            print(f"  データディレクトリ: {config.data_dir}")
            print(f"  保持期間: {config.retention_days}日")
            print(f"  最小サンプル数: {config.min_samples}")
            print(f"  信頼度: {config.confidence_level}")
            
            print("\n🎯 デフォルト閾値:")
            print(f"  LOW: {config.default_thresholds.low}%")
            print(f"  MEDIUM: {config.default_thresholds.medium}%")
            print(f"  HIGH: {config.default_thresholds.high}%")
            print(f"  CRITICAL: {config.default_thresholds.critical}%")
            
            print(f"\n🧪 ベンチマーク設定 ({len(config.benchmarks)}件):")
            for benchmark in config.benchmarks:
                status = "有効" if benchmark.enabled else "無効"
                print(f"  - {benchmark.name} ({status})")
                print(f"    パターン: {benchmark.test_pattern}")
                print(f"    タイムアウト: {benchmark.timeout}秒")
                if benchmark.custom_thresholds:
                    print(f"    カスタム閾値: あり")
        
        else:
            # デフォルト: 設定を読み込んで検証
            config = manager.load_config()
            errors = manager.validate_config()
            
            if errors:
                print("⚠️ 設定に問題があります:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("✅ パフォーマンス監視設定が正常に読み込まれました")
                print(f"  ベンチマーク数: {len(config.benchmarks)}")
                enabled_count = sum(1 for b in config.benchmarks if b.enabled)
                print(f"  有効なベンチマーク: {enabled_count}")
    
    except Exception as e:
        logger.error(f"設定管理中にエラーが発生: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())