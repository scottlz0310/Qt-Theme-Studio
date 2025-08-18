# メモリプロファイリング機能

Qt-Theme-Studioのメモリプロファイリング機能は、アプリケーションのメモリ使用量を監視し、メモリリークを検出し、詳細なプロファイリングレポートを生成します。

## 概要

メモリプロファイリング機能は以下の機能を提供します：

- **リアルタイムメモリ監視**: アプリケーションのメモリ使用量を継続的に監視
- **メモリリーク検出**: 自動的にメモリリークを検出し、重要度を判定
- **詳細レポート生成**: メモリ使用パターンの分析と推奨事項の提供
- **関数レベルプロファイリング**: 特定の関数実行時のメモリ使用量を測定
- **CI/CD統合**: 自動テストでのメモリ使用量チェック

## 基本的な使用方法

### コマンドライン実行

```bash
# 基本的なメモリスナップショット取得
python scripts/memory_profiler.py --snapshot

# 5分間のメモリ監視
python scripts/memory_profiler.py --monitor 300

# メモリリーク検出（過去10分間）
python scripts/memory_profiler.py --detect-leaks 10

# 24時間のメモリレポート生成
python scripts/memory_profiler.py --generate-report 24
```

### プログラムからの使用

```python
from scripts.memory_profiler import MemoryProfiler

# プロファイラーを初期化
profiler = MemoryProfiler(data_dir="logs/memory")

# スナップショット取得
snapshot = profiler.take_snapshot("アプリケーション開始")
print(f"メモリ使用量: {snapshot.process_memory_mb:.1f}MB")

# 関数のメモリプロファイリング
def memory_intensive_function():
    # メモリを使用する処理
    data = [i for i in range(100000)]
    return len(data)

result, before, after = profiler.profile_function(memory_intensive_function)
memory_diff = after.process_memory_mb - before.process_memory_mb
print(f"メモリ使用量変化: {memory_diff:+.1f}MB")

# 継続的な監視開始
profiler.start_monitoring(interval=5.0)  # 5秒間隔

# 処理実行...

# 監視停止
profiler.stop_monitoring()

# メモリリーク検出
leaks = profiler.detect_memory_leaks(duration_minutes=5)
if leaks:
    for leak in leaks:
        print(f"リーク検出: {leak.leak_rate_mb_per_sec:.3f}MB/秒 ({leak.severity})")

# レポート生成
report = profiler.generate_memory_report(hours=1)
print(f"平均メモリ使用量: {report['process_memory']['avg_mb']:.1f}MB")

# クリーンアップ
profiler.cleanup()
```

## メモリスナップショット

メモリスナップショットは、特定の時点でのメモリ状態を記録します。

### スナップショットに含まれる情報

- **プロセスメモリ使用量**: アプリケーションが使用している物理メモリ
- **システムメモリ使用率**: システム全体のメモリ使用率
- **tracemalloc情報**: Pythonオブジェクトのメモリ使用量
- **GCオブジェクト数**: ガベージコレクション対象のオブジェクト数
- **スレッド数**: アクティブなスレッド数
- **ファイルディスクリプタ数**: 開いているファイルディスクリプタ数

### スナップショット例

```python
snapshot = profiler.take_snapshot("テスト実行")
print(f"タイムスタンプ: {snapshot.timestamp}")
print(f"プロセスメモリ: {snapshot.process_memory_mb:.1f}MB")
print(f"システムメモリ使用率: {snapshot.system_memory_percent:.1f}%")
print(f"GCオブジェクト数: {snapshot.gc_objects_count:,}個")
```

## メモリリーク検出

メモリリーク検出機能は、時系列のメモリ使用量データを分析してリークを特定します。

### 検出アルゴリズム

1. **時系列分析**: 指定期間内のメモリ使用量の変化を分析
2. **リーク率計算**: メモリ増加率（MB/秒）を計算
3. **重要度判定**: リーク率と総リーク量に基づいて重要度を決定
4. **原因分析**: GCオブジェクト数、スレッド数などの変化を分析

### 重要度レベル

- **LOW**: 軽微なメモリリーク（1-2MB/秒）
- **MEDIUM**: 中程度のメモリリーク（2-5MB/秒）
- **HIGH**: 重要なメモリリーク（5-10MB/秒）
- **CRITICAL**: 深刻なメモリリーク（10MB/秒以上）

### リーク検出例

```python
# 5分間のメモリリーク検出
leaks = profiler.detect_memory_leaks(duration_minutes=5)

for leak in leaks:
    print(f"ベンチマーク: {leak.start_snapshot.context}")
    print(f"リーク率: {leak.leak_rate_mb_per_sec:.3f}MB/秒")
    print(f"総リーク量: {leak.total_leaked_mb:.1f}MB")
    print(f"重要度: {leak.severity}")
    print(f"分析: {leak.analysis}")
    print(f"期間: {leak.duration_seconds:.0f}秒")
    print("---")
```

## メモリレポート

メモリレポート機能は、指定期間のメモリ使用パターンを分析し、詳細なレポートを生成します。

### レポートに含まれる情報

- **プロセスメモリ統計**: 現在値、最小値、最大値、平均値、トレンド
- **システムメモリ統計**: システム全体のメモリ使用状況
- **tracemalloc統計**: Pythonオブジェクトのメモリ使用状況
- **GCオブジェクト統計**: ガベージコレクション対象オブジェクトの統計
- **メモリリーク情報**: 検出されたリークの概要
- **閾値違反**: 設定された閾値を超えた回数
- **推奨事項**: メモリ使用量改善のための提案

### レポート例

```python
report = profiler.generate_memory_report(hours=24)

print(f"期間: {report['period_hours']}時間")
print(f"スナップショット数: {report['snapshots_count']}")

# プロセスメモリ情報
pm = report['process_memory']
print(f"現在のメモリ使用量: {pm['current_mb']:.1f}MB")
print(f"平均メモリ使用量: {pm['avg_mb']:.1f}MB")
print(f"最大メモリ使用量: {pm['max_mb']:.1f}MB")
print(f"メモリ使用量トレンド: {pm['trend']}")

# メモリリーク情報
ml = report['memory_leaks']
print(f"検出されたリーク数: {ml['detected_count']}")
print(f"重要なリーク数: {ml['critical_count']}")
print(f"総リーク量: {ml['total_leaked_mb']:.1f}MB")

# 推奨事項
if report['recommendations']:
    print("推奨事項:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
```

## 設定とカスタマイズ

### メモリ閾値の設定

```python
from scripts.memory_profiler import MemoryThresholds

# カスタム閾値を設定
thresholds = MemoryThresholds(
    process_memory_mb=1000.0,      # プロセスメモリ閾値（MB）
    system_memory_percent=85.0,    # システムメモリ使用率閾値（%）
    leak_rate_mb_per_sec=2.0,      # リーク率閾値（MB/秒）
    gc_objects_growth_rate=2000.0  # GCオブジェクト増加率閾値（個/秒）
)

profiler = MemoryProfiler()
profiler.thresholds = thresholds
```

### 監視間隔の調整

```python
# 高頻度監視（1秒間隔）
profiler.start_monitoring(interval=1.0)

# 低頻度監視（30秒間隔）
profiler.start_monitoring(interval=30.0)
```

### データ保存期間の設定

```python
# スナップショット保持数を変更
profiler.max_snapshots = 2000  # デフォルト: 1000

# 古いデータの自動削除期間は内部で管理
# - スナップショット: 90日
# - メモリリーク: 7日
```

## パフォーマンス監視システムとの統合

メモリプロファイリング機能は、パフォーマンス監視システムと統合されています。

### 統合実行

```python
from scripts.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()

# メモリプロファイリングテストを実行
result = monitor.run_memory_profiling_test(duration_minutes=5)

if result['success']:
    print(f"メモリ変化: {result['memory_change_mb']:+.1f}MB")
    print(f"検出されたリーク数: {result['leaks_detected']}")
    
    if result['summary']['memory_stable']:
        print("✅ メモリ使用量は安定しています")
    else:
        print("⚠️ メモリ使用量に問題があります")
```

### CI/CDでの使用

```bash
# パフォーマンス監視システム経由でメモリプロファイリング実行
python scripts/performance_monitor.py --memory-profile 2

# 直接実行
python scripts/memory_profiler.py --monitor 120 --detect-leaks 2
```

## ベストプラクティス

### 1. 適切な監視間隔の選択

- **開発時**: 1-5秒間隔で詳細な監視
- **テスト時**: 5-10秒間隔でバランスの取れた監視
- **本番環境**: 30-60秒間隔で軽量な監視

### 2. メモリリーク検出のタイミング

- **短期テスト**: 1-5分間の監視でクイックチェック
- **長期テスト**: 30分-1時間の監視で詳細分析
- **継続監視**: 24時間以上の監視で傾向分析

### 3. 閾値の適切な設定

```python
# 開発環境用（緩い閾値）
dev_thresholds = MemoryThresholds(
    process_memory_mb=2000.0,
    system_memory_percent=90.0,
    leak_rate_mb_per_sec=5.0
)

# 本番環境用（厳しい閾値）
prod_thresholds = MemoryThresholds(
    process_memory_mb=500.0,
    system_memory_percent=80.0,
    leak_rate_mb_per_sec=1.0
)
```

### 4. レポートの定期生成

```python
# 日次レポート
daily_report = profiler.generate_memory_report(hours=24)

# 週次レポート
weekly_report = profiler.generate_memory_report(hours=168)

# 月次レポート
monthly_report = profiler.generate_memory_report(hours=720)
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. tracemalloc が利用できない

```python
import tracemalloc

if not tracemalloc.is_tracing():
    tracemalloc.start()
    print("tracemalloc監視を開始しました")
```

#### 2. ファイルディスクリプタ数が取得できない

Windows環境では`num_fds()`が利用できない場合があります。この場合、値は0として記録されます。

#### 3. メモリ使用量が異常に高い

```python
# ガベージコレクションを強制実行
import gc
gc.collect()

# スナップショット取得
snapshot = profiler.take_snapshot("GC後")
```

#### 4. 監視が停止しない

```python
# 強制停止
profiler.monitoring_active = False
if profiler.monitoring_thread:
    profiler.monitoring_thread.join(timeout=5)
```

## API リファレンス

### MemoryProfiler クラス

#### 初期化

```python
MemoryProfiler(data_dir: str = "logs/performance/memory")
```

#### 主要メソッド

- `take_snapshot(context: str = "") -> MemorySnapshot`
- `start_monitoring(interval: float = 5.0) -> None`
- `stop_monitoring() -> None`
- `detect_memory_leaks(duration_minutes: int = 5) -> List[MemoryLeak]`
- `profile_function(func: Callable, *args, **kwargs) -> Tuple[Any, MemorySnapshot, MemorySnapshot]`
- `generate_memory_report(hours: int = 24) -> Dict[str, Any]`
- `cleanup() -> None`

### MemorySnapshot クラス

#### 属性

- `timestamp: datetime` - スナップショット取得時刻
- `process_memory_mb: float` - プロセスメモリ使用量（MB）
- `system_memory_percent: float` - システムメモリ使用率（%）
- `tracemalloc_current_mb: float` - tracemalloc現在値（MB）
- `tracemalloc_peak_mb: float` - tracemalloc最大値（MB）
- `gc_objects_count: int` - GCオブジェクト数
- `thread_count: int` - スレッド数
- `file_descriptors: int` - ファイルディスクリプタ数
- `context: str` - コンテキスト情報

### MemoryLeak クラス

#### 属性

- `start_snapshot: MemorySnapshot` - 開始時のスナップショット
- `end_snapshot: MemorySnapshot` - 終了時のスナップショット
- `leak_rate_mb_per_sec: float` - リーク率（MB/秒）
- `total_leaked_mb: float` - 総リーク量（MB）
- `duration_seconds: float` - 検出期間（秒）
- `severity: str` - 重要度（LOW/MEDIUM/HIGH/CRITICAL）
- `analysis: str` - 分析結果
- `top_allocations: List[Dict[str, Any]]` - トップアロケーション情報

## 関連ドキュメント

- [パフォーマンス監視システム](performance_monitoring.md)
- [GUI応答性監視](gui_responsiveness.md)
- [CI/CD統合](ci_cd_integration.md)
- [トラブルシューティング](troubleshooting.md)