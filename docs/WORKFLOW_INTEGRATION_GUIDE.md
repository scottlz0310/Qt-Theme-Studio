# Qt-Theme-Studio ワークフロー統合システム ユーザーガイド

## 概要

Qt-Theme-Studioワークフロー統合システムは、開発プロセスの自動化と品質管理を統合的に行うシステムです。このガイドでは、システムの使用方法、設定、トラブルシューティングについて詳しく説明します。

## 目次

1. [システム概要](#システム概要)
2. [インストールとセットアップ](#インストールとセットアップ)
3. [基本的な使用方法](#基本的な使用方法)
4. [設定管理](#設定管理)
5. [ワークフロー管理](#ワークフロー管理)
6. [統合ダッシュボード](#統合ダッシュボード)
7. [リアルタイム監視](#リアルタイム監視)
8. [カスタマイズ](#カスタマイズ)
9. [トラブルシューティング](#トラブルシューティング)
10. [FAQ](#faq)

## システム概要

### 主要コンポーネント

ワークフロー統合システムは以下の主要コンポーネントで構成されています：

#### 1. ワークフローエンジン (`scripts/workflow_engine.py`)
- 全ワークフローの統合制御
- 非同期実行とエラーハンドリング
- プラグインシステムのサポート

#### 2. 設定管理システム (`scripts/config_manager.py`)
- YAML設定ファイルの管理
- 環境変数オーバーライド
- 設定の検証と自動修正

#### 3. 統合ダッシュボード (`scripts/quality_dashboard.py`)
- 品質メトリクスの統合表示
- リアルタイム監視機能
- 可視化とレポート生成

#### 4. 統合設定ファイル (`.kiro/workflow/config.yml`)
- 全ワークフローの統一設定
- 品質閾値とアラート設定
- 環境固有の設定

### システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    ワークフロー統合システム                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ワークフロー  │  │   設定管理   │  │統合ダッシュ  │        │
│  │  エンジン    │◄─┤   システム   ├─►│   ボード    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                 │                 │              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Pre-commit   │  │CI/CD        │  │リアルタイム  │        │
│  │フック       │  │パイプライン  │  │監視         │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## インストールとセットアップ

### 前提条件

- Python 3.8以上
- Git
- 必要なPythonパッケージ（requirements.txtを参照）

### 自動セットアップ

最も簡単な方法は、自動セットアップスクリプトを使用することです：

```bash
# Linux/Mac
./setup_dev_environment.sh

# Windows
setup_dev_environment.bat
```

### 手動セットアップ

1. **依存関係のインストール**
   ```bash
   pip install -e .[dev]
   ```

2. **設定ファイルの初期化**
   ```bash
   python scripts/config_manager.py
   ```

3. **Pre-commitフックのセットアップ**
   ```bash
   python scripts/pre_commit_setup.py --auto
   ```

4. **環境の検証**
   ```bash
   python scripts/workflow_engine.py
   ```

### 設定ファイルの確認

セットアップ後、以下のファイルが作成されていることを確認してください：

- `.kiro/workflow/config.yml` - メイン設定ファイル
- `.pre-commit-config.yaml` - Pre-commitフック設定
- `logs/` ディレクトリ - ログファイル保存用

## 基本的な使用方法

### ワークフローの実行

#### 1. 利用可能なワークフローの確認

```bash
python scripts/workflow_engine.py
```

出力例：
```
利用可能なワークフロー: pre_commit, ci_pipeline, release, dev_setup, docs_generation
```

#### 2. 特定のワークフローの実行

```bash
# Pre-commitワークフローの実行
python scripts/workflow_engine.py pre_commit

# CI/CDパイプラインの実行
python scripts/workflow_engine.py ci_pipeline

# リリースワークフローの実行
python scripts/workflow_engine.py release
```

#### 3. 統合ダッシュボードの起動

```bash
# 基本的なダッシュボード
python scripts/quality_dashboard.py

# 統合ダッシュボード
python scripts/quality_dashboard.py --integrated

# リアルタイム監視付き
python scripts/quality_dashboard.py --integrated --monitoring --interval 30
```

### 日常的な開発フロー

1. **コード変更**
   - ファイルを編集
   - 自動的にPre-commitフックが実行される

2. **品質チェック**
   ```bash
   python scripts/quality_check.py
   ```

3. **テスト実行**
   ```bash
   pytest
   ```

4. **統合レポートの確認**
   ```bash
   python scripts/quality_dashboard.py --integrated
   ```

## 設定管理

### 設定ファイルの構造

`.kiro/workflow/config.yml`は以下の主要セクションで構成されています：

```yaml
# ワークフロー定義
workflows:
  pre_commit:
    enabled: true
    steps: [...]
  
# 品質閾値
quality_thresholds:
  coverage_minimum: 80
  test_success_rate: 95
  
# 通知設定
notifications:
  enabled: true
  channels: [...]
  
# エラーハンドリング
error_handling:
  auto_recovery:
    enabled: true
```

### 環境変数による設定オーバーライド

以下の環境変数で設定を上書きできます：

```bash
# カバレッジ最小値
export WORKFLOW_COVERAGE_MIN=85

# ログレベル
export WORKFLOW_LOG_LEVEL=DEBUG

# タイムアウト設定
export WORKFLOW_TIMEOUT=1800

# デバッグモード
export WORKFLOW_DEBUG=true

# 並列実行
export WORKFLOW_PARALLEL=true

# キャッシュ有効化
export WORKFLOW_CACHE_ENABLED=true

# 通知有効化
export WORKFLOW_NOTIFICATIONS=true
```

### 設定の検証と修正

```bash
# 設定の検証
python scripts/config_manager.py

# 設定の自動修正
python -c "
from scripts.config_manager import ConfigManager
cm = ConfigManager()
result = cm.validate_config()
if not result.is_valid:
    print('設定を自動修正中...')
    cm._auto_fix_config()
    cm.save_config()
"
```

## ワークフロー管理

### 利用可能なワークフロー

#### 1. Pre-commitワークフロー (`pre_commit`)
コミット前の自動品質チェック

**ステップ:**
- Ruffリンティング
- Ruffフォーマット
- 基本テスト実行
- 日本語ログメッセージ検証

**実行タイミング:** `git commit`時に自動実行

#### 2. CI/CDパイプライン (`ci_pipeline`)
継続的インテグレーション

**ステップ:**
- 環境セットアップ
- 品質チェック統合実行
- 完全テストスイート
- セキュリティスキャン
- パフォーマンステスト

**実行タイミング:** プッシュ・プルリクエスト時

#### 3. リリース自動化 (`release`)
リリース準備の自動化

**ステップ:**
- リリース前検証
- 最終テスト実行
- パッケージビルド
- チェックサム生成
- アーカイブ作成

**実行タイミング:** リリースタグ作成時

#### 4. 開発環境セットアップ (`dev_setup`)
新規開発者向けの環境構築

**ステップ:**
- 環境検出
- 依存関係インストール
- Pre-commitセットアップ
- インストール検証

**実行タイミング:** 手動実行

#### 5. ドキュメント生成 (`docs_generation`)
ドキュメントの自動生成・検証

**ステップ:**
- APIドキュメント生成
- Markdown検証
- ドキュメント更新チェック

**実行タイミング:** 手動実行またはCI

### カスタムワークフローの作成

新しいワークフローを追加するには、`.kiro/workflow/config.yml`を編集します：

```yaml
workflows:
  my_custom_workflow:
    enabled: true
    description: "カスタムワークフローの説明"
    timeout: 600  # 10分
    steps:
      - name: "custom_step_1"
        description: "カスタムステップ1"
        command: "echo 'カスタム処理1'"
        required: true
        timeout: 60
        
      - name: "custom_step_2"
        description: "カスタムステップ2"
        command: "python scripts/my_custom_script.py"
        required: false
        timeout: 120
        depends_on: ["custom_step_1"]
```

### ワークフローの無効化

特定のワークフローを無効にするには：

```yaml
workflows:
  unwanted_workflow:
    enabled: false  # このワークフローを無効化
```

## 統合ダッシュボード

### 基本的な使用方法

```bash
# 統合ダッシュボードの起動
python scripts/quality_dashboard.py --integrated
```

### 表示される情報

#### 1. ワークフロー統計
- 利用可能なワークフロー数
- 有効なワークフロー数
- ワークフロー成功率
- 最近の実行履歴

#### 2. システムメトリクス
- CPU使用率
- メモリ使用率
- ディスク使用率
- プロセスメモリ使用量

#### 3. セキュリティメトリクス
- 総問題数
- 重要度別問題数
- セキュリティスコア
- 最終スキャン日時

#### 4. パフォーマンスメトリクス
- ベンチマーク数
- 平均実行時間
- 最遅テスト
- パフォーマンス評価

#### 5. 従来の品質メトリクス
- テスト統計
- カバレッジ統計
- ファイル統計
- 品質スコア

### レポートの保存

ダッシュボード実行後、以下のファイルが生成されます：

- `integrated_quality_report.json` - 統合詳細データ
- `logs/metrics_history.json` - メトリクス履歴
- `integrated_quality_dashboard.png` - 統合可視化グラフ

### カスタムレポートの生成

```python
from scripts.quality_dashboard import IntegratedQualityDashboard

# ダッシュボードを初期化
dashboard = IntegratedQualityDashboard()

# 特定のメトリクスのみ収集
workflow_stats = dashboard.collect_workflow_statistics()
system_metrics = dashboard.collect_system_metrics()

# カスタムレポートを生成
custom_report = f"""
カスタムレポート
================
ワークフロー数: {workflow_stats.get('total_workflows', 0)}
CPU使用率: {system_metrics.get('cpu_percent', 0):.1f}%
"""

print(custom_report)
```

## リアルタイム監視

### 監視の開始

```bash
# 60秒間隔での監視
python scripts/quality_dashboard.py --integrated --monitoring --interval 60

# 30秒間隔での監視
python scripts/quality_dashboard.py --integrated --monitoring --interval 30
```

### 監視される項目

- システムリソース使用率
- ワークフロー実行状況
- エラー発生頻度
- パフォーマンス指標

### アラート条件

以下の条件でアラートが発生します：

- CPU使用率 > 80%
- メモリ使用率 > 85%
- ディスク使用率 > 90%
- ワークフロー成功率 < 80%

### プログラムによる監視制御

```python
from scripts.quality_dashboard import IntegratedQualityDashboard

dashboard = IntegratedQualityDashboard()

# 監視開始
dashboard.start_realtime_monitoring(interval=60)

# 監視状況の確認
print(f"監視中: {dashboard.monitoring_active}")

# 監視停止
dashboard.stop_realtime_monitoring()
```

## カスタマイズ

### プラグインの作成

カスタムプラグインを作成してワークフローを拡張できます：

```python
# scripts/plugins/my_plugin.py
class MyCustomPlugin:
    """カスタムプラグインの例"""
    
    async def execute(self, step_config, **kwargs):
        """プラグインの実行ロジック"""
        print(f"カスタムプラグインを実行中: {step_config['name']}")
        
        # カスタム処理をここに実装
        # ...
        
        return True  # 成功時はTrue、失敗時はFalse

# プラグインの登録
from scripts.workflow_engine import WorkflowEngine

engine = WorkflowEngine()
engine.register_plugin("my_plugin", MyCustomPlugin())
```

### カスタムメトリクスの追加

ダッシュボードにカスタムメトリクスを追加：

```python
from scripts.quality_dashboard import IntegratedQualityDashboard

class CustomDashboard(IntegratedQualityDashboard):
    """カスタムダッシュボード"""
    
    def collect_custom_metrics(self):
        """カスタムメトリクスを収集"""
        return {
            "custom_metric_1": 42,
            "custom_metric_2": "カスタム値",
            "timestamp": datetime.now().isoformat()
        }
    
    def run_integrated_dashboard(self, **kwargs):
        """統合ダッシュボードを実行（カスタムメトリクス付き）"""
        # 標準メトリクスを収集
        super().run_integrated_dashboard(**kwargs)
        
        # カスタムメトリクスを追加
        self.results["custom_metrics"] = self.collect_custom_metrics()
```

### 通知システムのカスタマイズ

カスタム通知チャンネルの追加：

```python
class SlackNotifier:
    """Slack通知クラス"""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_notification(self, message, level="INFO"):
        """Slackに通知を送信"""
        import requests
        
        payload = {
            "text": f"[{level}] {message}",
            "username": "Qt-Theme-Studio Bot"
        }
        
        requests.post(self.webhook_url, json=payload)

# 設定ファイルでの使用
# .kiro/workflow/config.yml
notifications:
  channels:
    - type: "custom"
      class: "SlackNotifier"
      config:
        webhook_url: "https://hooks.slack.com/..."
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. 設定ファイルが見つからない

**症状:**
```
ConfigurationError: 設定ファイルの読み込みエラー: [Errno 2] No such file or directory
```

**解決方法:**
```bash
# 設定ファイルを作成
python scripts/config_manager.py

# または手動で作成
mkdir -p .kiro/workflow
cp .kiro/workflow/config.yml.example .kiro/workflow/config.yml
```

#### 2. ワークフローの実行が失敗する

**症状:**
```
ExecutionError: ワークフロー 'ci_pipeline' の実行中にエラーが発生しました
```

**解決方法:**
1. 環境の検証
   ```bash
   python scripts/workflow_engine.py
   ```

2. 詳細ログの確認
   ```bash
   export WORKFLOW_LOG_LEVEL=DEBUG
   python scripts/workflow_engine.py ci_pipeline
   ```

3. 設定の検証
   ```bash
   python scripts/config_manager.py
   ```

#### 3. Pre-commitフックが動作しない

**症状:**
コミット時にフックが実行されない

**解決方法:**
```bash
# Pre-commitの再インストール
python scripts/pre_commit_setup.py --force

# フックの手動実行でテスト
pre-commit run --all-files
```

#### 4. ダッシュボードでエラーが発生する

**症状:**
```
ImportError: No module named 'matplotlib'
```

**解決方法:**
```bash
# 必要なパッケージをインストール
pip install matplotlib psutil

# または開発用依存関係をインストール
pip install -e .[dev]
```

#### 5. 権限エラー

**症状:**
```
PermissionError: [Errno 13] Permission denied
```

**解決方法:**
```bash
# ファイル権限の確認と修正
chmod +x scripts/*.py
chmod +x setup_dev_environment.sh

# ディレクトリ権限の確認
ls -la .kiro/
```

### ログファイルの確認

問題の詳細を確認するには、以下のログファイルをチェックしてください：

```bash
# ワークフローログ
tail -f logs/workflow.log

# エラーログ
tail -f logs/*_errors.log

# パフォーマンスログ
tail -f logs/*_performance.log

# 構造化ログ
tail -f logs/*_structured_*.log
```

### デバッグモードの有効化

詳細なデバッグ情報を取得するには：

```bash
# 環境変数でデバッグモードを有効化
export WORKFLOW_DEBUG=true
export WORKFLOW_LOG_LEVEL=DEBUG

# または設定ファイルで有効化
# .kiro/workflow/config.yml
environments:
  development:
    debug: true
    log_level: "DEBUG"
```

### 設定のリセット

設定に問題がある場合は、リセットできます：

```bash
# 設定ファイルのバックアップ
cp .kiro/workflow/config.yml .kiro/workflow/config.yml.backup

# デフォルト設定で再初期化
rm .kiro/workflow/config.yml
python scripts/config_manager.py
```

## FAQ

### Q1: ワークフローの実行時間を短縮するには？

**A:** 以下の方法で実行時間を短縮できます：

1. **並列実行の有効化**
   ```yaml
   workflows:
     ci_pipeline:
       parallel: true
   ```

2. **キャッシュの有効化**
   ```yaml
   cache:
     enabled: true
     cache_types:
       dependencies: true
       test_results: true
   ```

3. **タイムアウトの調整**
   ```yaml
   workflows:
     ci_pipeline:
       timeout: 900  # 15分に短縮
   ```

### Q2: 特定のファイルをワークフローから除外するには？

**A:** `.gitignore`スタイルのパターンで除外できます：

```yaml
workflows:
  pre_commit:
    exclude_patterns:
      - "*.log"
      - "temp/*"
      - "build/*"
```

### Q3: カスタムコマンドを追加するには？

**A:** 設定ファイルでカスタムステップを定義します：

```yaml
workflows:
  custom_workflow:
    steps:
      - name: "my_custom_command"
        command: "python my_script.py --option value"
        required: true
```

### Q4: 通知を無効にするには？

**A:** 設定ファイルまたは環境変数で無効化できます：

```bash
# 環境変数
export WORKFLOW_NOTIFICATIONS=false

# または設定ファイル
notifications:
  enabled: false
```

### Q5: 異なる環境で異なる設定を使用するには？

**A:** 環境固有の設定を定義します：

```yaml
environments:
  development:
    debug: true
    skip_security_scan: true
    
  production:
    debug: false
    strict_validation: true
```

### Q6: ワークフローの実行履歴を確認するには？

**A:** ログファイルまたはダッシュボードで確認できます：

```bash
# ログファイルで確認
grep "ワークフロー" logs/*.log

# ダッシュボードで確認
python scripts/quality_dashboard.py --integrated
```

### Q7: メモリ使用量を削減するには？

**A:** 以下の設定で最適化できます：

```yaml
cache:
  max_size: "500MB"  # キャッシュサイズを制限

monitoring:
  metrics_storage:
    retention_days: 7  # 履歴保存期間を短縮
```

### Q8: セキュリティスキャンをスキップするには？

**A:** 開発環境でのみスキップできます：

```yaml
environments:
  development:
    skip_security_scan: true
```

または環境変数で：

```bash
export WORKFLOW_SKIP_SECURITY=true
```

## サポート

### 問題の報告

問題が発生した場合は、以下の情報を含めて報告してください：

1. **エラーメッセージ**
2. **実行したコマンド**
3. **環境情報**
   ```bash
   python --version
   pip list | grep -E "(qt|theme|workflow)"
   ```
4. **ログファイル**
   ```bash
   tar -czf logs_$(date +%Y%m%d_%H%M%S).tar.gz logs/
   ```

### 追加リソース

- [プロジェクトREADME](../README.md)
- [API仕様書](FEATURE_SPECIFICATIONS.md)
- [実装ガイド](IMPLEMENTATION_GUIDE.md)
- [リリースノート](RELEASE_NOTES.md)

---

このガイドは継続的に更新されます。最新版は常にプロジェクトリポジトリで確認してください。