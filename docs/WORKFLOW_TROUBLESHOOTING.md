# Qt-Theme-Studio ワークフロー統合システム トラブルシューティングガイド

## 概要

このガイドでは、Qt-Theme-Studioワークフロー統合システムで発生する可能性のある問題と、その解決方法について詳しく説明します。

## 目次

1. [一般的な問題](#一般的な問題)
2. [設定関連の問題](#設定関連の問題)
3. [ワークフロー実行の問題](#ワークフロー実行の問題)
4. [ダッシュボードの問題](#ダッシュボードの問題)
5. [パフォーマンスの問題](#パフォーマンスの問題)
6. [セキュリティ関連の問題](#セキュリティ関連の問題)
7. [環境固有の問題](#環境固有の問題)
8. [デバッグ手順](#デバッグ手順)
9. [ログ分析](#ログ分析)
10. [復旧手順](#復旧手順)

## 一般的な問題

### 問題1: モジュールが見つからない

**症状:**
```
ModuleNotFoundError: No module named 'scripts.workflow_engine'
```

**原因:**
- Pythonパスの設定が不正
- 必要なパッケージがインストールされていない
- 仮想環境が有効化されていない

**解決方法:**

1. **仮想環境の確認と有効化**
   ```bash
   # 仮想環境の存在確認
   ls -la venv/
   
   # 仮想環境の有効化
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **パッケージの再インストール**
   ```bash
   pip install -e .[dev]
   ```

3. **Pythonパスの確認**
   ```bash
   python -c "import sys; print('\n'.join(sys.path))"
   ```

4. **プロジェクトルートからの実行**
   ```bash
   cd /path/to/qt-theme-studio
   python scripts/workflow_engine.py
   ```

### 問題2: 権限エラー

**症状:**
```
PermissionError: [Errno 13] Permission denied: '.kiro/workflow/config.yml'
```

**原因:**
- ファイル・ディレクトリの権限が不適切
- 管理者権限が必要な操作
- ファイルが他のプロセスで使用中

**解決方法:**

1. **権限の確認と修正**
   ```bash
   # 権限の確認
   ls -la .kiro/workflow/
   
   # 権限の修正
   chmod 644 .kiro/workflow/config.yml
   chmod 755 .kiro/workflow/
   ```

2. **所有者の確認と修正**
   ```bash
   # 所有者の確認
   ls -la .kiro/
   
   # 所有者の修正（必要に応じて）
   sudo chown -R $USER:$USER .kiro/
   ```

3. **ファイルロックの確認**
   ```bash
   # ファイルを使用しているプロセスの確認
   lsof .kiro/workflow/config.yml
   ```

### 問題3: 依存関係の競合

**症状:**
```
pip._internal.exceptions.DistributionNotFound: The 'package-name>=1.0.0' distribution was not found
```

**原因:**
- パッケージバージョンの競合
- 依存関係の循環参照
- 破損したパッケージ

**解決方法:**

1. **依存関係の確認**
   ```bash
   pip check
   pip list --outdated
   ```

2. **仮想環境の再作成**
   ```bash
   deactivate
   rm -rf venv/
   python -m venv venv
   source venv/bin/activate
   pip install -e .[dev]
   ```

3. **特定パッケージの再インストール**
   ```bash
   pip uninstall package-name
   pip install package-name
   ```

## 設定関連の問題

### 問題4: 設定ファイルが見つからない

**症状:**
```
ConfigurationError: 設定ファイルの読み込みエラー: [Errno 2] No such file or directory: '.kiro/workflow/config.yml'
```

**原因:**
- 設定ファイルが存在しない
- パスが間違っている
- ディレクトリ構造が不正

**解決方法:**

1. **設定ファイルの作成**
   ```bash
   # ディレクトリの作成
   mkdir -p .kiro/workflow
   
   # デフォルト設定の生成
   python scripts/config_manager.py
   ```

2. **設定ファイルの手動作成**
   ```bash
   # テンプレートからコピー
   cp .kiro/workflow/config.yml.example .kiro/workflow/config.yml
   ```

3. **パスの確認**
   ```bash
   # 現在のディレクトリ確認
   pwd
   
   # 設定ファイルの存在確認
   find . -name "config.yml" -type f
   ```

### 問題5: 設定の検証エラー

**症状:**
```
ValidationError: 設定に問題があります: 必須セクション 'workflows' が見つかりません
```

**原因:**
- 設定ファイルの構文エラー
- 必須フィールドの欠如
- 無効な値の設定

**解決方法:**

1. **YAML構文の確認**
   ```bash
   # YAML構文チェック
   python -c "import yaml; yaml.safe_load(open('.kiro/workflow/config.yml'))"
   ```

2. **設定の自動修正**
   ```bash
   python -c "
   from scripts.config_manager import ConfigManager
   cm = ConfigManager()
   result = cm.validate_config()
   if not result.is_valid:
       print('設定を自動修正中...')
       if cm._auto_fix_config():
           cm.save_config()
           print('修正完了')
       else:
           print('自動修正に失敗')
   "
   ```

3. **設定のリセット**
   ```bash
   # バックアップ作成
   cp .kiro/workflow/config.yml .kiro/workflow/config.yml.backup
   
   # デフォルト設定で再初期化
   rm .kiro/workflow/config.yml
   python scripts/config_manager.py
   ```

### 問題6: 環境変数オーバーライドが効かない

**症状:**
環境変数を設定しても設定が変更されない

**原因:**
- 環境変数名が間違っている
- 値の型が不正
- 設定の読み込み順序の問題

**解決方法:**

1. **環境変数の確認**
   ```bash
   # 設定されている環境変数の確認
   env | grep WORKFLOW_
   
   # 特定の環境変数の確認
   echo $WORKFLOW_COVERAGE_MIN
   ```

2. **サポートされている環境変数の確認**
   ```bash
   python -c "
   from scripts.config_manager import ConfigManager
   cm = ConfigManager()
   print('サポートされている環境変数:')
   for env_var, config_path in cm.env_mappings.items():
       print(f'  {env_var} -> {config_path}')
   "
   ```

3. **値の型確認**
   ```bash
   # 数値の場合
   export WORKFLOW_COVERAGE_MIN=85
   
   # ブール値の場合
   export WORKFLOW_DEBUG=true
   
   # 文字列の場合
   export WORKFLOW_LOG_LEVEL=DEBUG
   ```

## ワークフロー実行の問題

### 問題7: ワークフローの実行が失敗する

**症状:**
```
ExecutionError: ワークフロー 'ci_pipeline' の実行中にエラーが発生しました
```

**原因:**
- コマンドの実行エラー
- 依存関係の問題
- タイムアウト
- リソース不足

**解決方法:**

1. **詳細ログの有効化**
   ```bash
   export WORKFLOW_LOG_LEVEL=DEBUG
   python scripts/workflow_engine.py ci_pipeline
   ```

2. **個別ステップの実行**
   ```bash
   # 失敗したコマンドを直接実行
   ruff check .
   pytest tests/
   ```

3. **環境の検証**
   ```bash
   python scripts/workflow_engine.py
   ```

4. **タイムアウトの調整**
   ```yaml
   # .kiro/workflow/config.yml
   workflows:
     ci_pipeline:
       timeout: 1800  # 30分に延長
   ```

### 問題8: Pre-commitフックが動作しない

**症状:**
コミット時にフックが実行されない

**原因:**
- Pre-commitがインストールされていない
- フック設定が不正
- Gitフックが無効化されている

**解決方法:**

1. **Pre-commitの状態確認**
   ```bash
   pre-commit --version
   pre-commit run --all-files
   ```

2. **フックの再インストール**
   ```bash
   pre-commit uninstall
   pre-commit install
   ```

3. **設定ファイルの確認**
   ```bash
   # 設定ファイルの存在確認
   ls -la .pre-commit-config.yaml
   
   # 設定の検証
   pre-commit validate-config
   ```

4. **手動でのフック実行**
   ```bash
   # 全ファイルに対して実行
   pre-commit run --all-files
   
   # 特定のフックのみ実行
   pre-commit run ruff-check
   ```

### 問題9: 非同期実行でのデッドロック

**症状:**
ワークフローが途中で停止し、応答しなくなる

**原因:**
- 非同期処理のデッドロック
- リソースの競合
- 無限ループ

**解決方法:**

1. **プロセスの確認と終了**
   ```bash
   # 実行中のプロセス確認
   ps aux | grep python
   
   # プロセスの強制終了
   pkill -f workflow_engine
   ```

2. **同期実行モードの使用**
   ```yaml
   # .kiro/workflow/config.yml
   workflows:
     ci_pipeline:
       parallel: false  # 並列実行を無効化
   ```

3. **タイムアウトの設定**
   ```yaml
   workflows:
     ci_pipeline:
       timeout: 600  # 10分でタイムアウト
       steps:
         - name: "long_running_step"
           timeout: 300  # 個別ステップのタイムアウト
   ```

## ダッシュボードの問題

### 問題10: ダッシュボードが起動しない

**症状:**
```
ImportError: No module named 'matplotlib'
```

**原因:**
- 必要なパッケージが不足
- 仮想ディスプレイの問題（Linux）
- メモリ不足

**解決方法:**

1. **必要パッケージのインストール**
   ```bash
   pip install matplotlib psutil
   ```

2. **仮想ディスプレイの設定（Linux）**
   ```bash
   # Xvfbのインストール
   sudo apt-get install xvfb
   
   # 仮想ディスプレイで実行
   xvfb-run -a python scripts/quality_dashboard.py --integrated
   ```

3. **ヘッドレスモードの使用**
   ```bash
   export MPLBACKEND=Agg
   python scripts/quality_dashboard.py --integrated
   ```

### 問題11: メトリクス収集でエラー

**症状:**
```
subprocess.CalledProcessError: Command 'pytest' returned non-zero exit status 1
```

**原因:**
- テストの失敗
- 依存関係の問題
- 設定の不備

**解決方法:**

1. **テストの個別実行**
   ```bash
   # テストを直接実行して問題を特定
   pytest -v
   pytest tests/unit/ -x
   ```

2. **依存関係の確認**
   ```bash
   pip check
   pip install -e .[dev]
   ```

3. **モックモードの使用**
   ```python
   # テスト用のダッシュボード実行
   from scripts.quality_dashboard import IntegratedQualityDashboard
   
   dashboard = IntegratedQualityDashboard()
   # 実際のテスト実行をスキップしてモックデータを使用
   dashboard.results = {
       "test_statistics": {"total_tests": 0, "passed": 0, "failed": 0}
   }
   ```

### 問題12: 可視化が生成されない

**症状:**
グラフファイルが作成されない

**原因:**
- matplotlibの設定問題
- ディスプレイの問題
- 権限の問題

**解決方法:**

1. **バックエンドの設定**
   ```python
   import matplotlib
   matplotlib.use('Agg')  # ヘッドレス環境用
   ```

2. **出力ディレクトリの権限確認**
   ```bash
   ls -la .
   chmod 755 .
   ```

3. **手動での可視化テスト**
   ```python
   import matplotlib.pyplot as plt
   plt.figure()
   plt.plot([1, 2, 3], [1, 4, 2])
   plt.savefig('test_plot.png')
   print("テストプロット作成完了")
   ```

## パフォーマンスの問題

### 問題13: ワークフロー実行が遅い

**症状:**
ワークフローの実行に異常に時間がかかる

**原因:**
- リソース不足
- 非効率な設定
- 外部依存関係の遅延

**解決方法:**

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

3. **タイムアウトの最適化**
   ```yaml
   workflows:
     ci_pipeline:
       steps:
         - name: "quick_test"
           timeout: 60  # 短いタイムアウト
   ```

4. **リソース使用量の監視**
   ```bash
   # システムリソースの監視
   top
   htop
   iotop
   ```

### 問題14: メモリ使用量が多い

**症状:**
```
MemoryError: Unable to allocate array
```

**原因:**
- メモリリーク
- 大量データの処理
- 効率的でないアルゴリズム

**解決方法:**

1. **メモリ使用量の監視**
   ```bash
   # メモリプロファイリング
   python scripts/memory_profiler.py
   ```

2. **キャッシュサイズの制限**
   ```yaml
   cache:
     max_size: "500MB"
   ```

3. **バッチ処理の実装**
   ```python
   # 大量データを小さなバッチに分割
   def process_in_batches(data, batch_size=1000):
       for i in range(0, len(data), batch_size):
           yield data[i:i + batch_size]
   ```

### 問題15: ディスク容量不足

**症状:**
```
OSError: [Errno 28] No space left on device
```

**原因:**
- ログファイルの肥大化
- キャッシュの蓄積
- 一時ファイルの残存

**解決方法:**

1. **ディスク使用量の確認**
   ```bash
   df -h
   du -sh logs/
   du -sh .kiro/cache/
   ```

2. **ログローテーションの設定**
   ```yaml
   notifications:
     channels:
       - type: "file"
         max_size: "10MB"
         backup_count: 5
   ```

3. **古いファイルの削除**
   ```bash
   # 古いログファイルの削除
   find logs/ -name "*.log" -mtime +7 -delete
   
   # キャッシュのクリア
   rm -rf .kiro/cache/*
   ```

## セキュリティ関連の問題

### 問題16: セキュリティスキャンが失敗する

**症状:**
```
bandit.core.manager.BanditManager: Unable to find any files to scan
```

**原因:**
- スキャン対象ファイルが見つからない
- 権限の問題
- 設定の不備

**解決方法:**

1. **スキャン対象の確認**
   ```bash
   # 手動でbanditを実行
   bandit -r qt_theme_studio/
   ```

2. **除外パターンの確認**
   ```bash
   # .banditファイルの確認
   cat .bandit
   ```

3. **権限の確認**
   ```bash
   ls -la qt_theme_studio/
   ```

### 問題17: 脆弱性の誤検出

**症状:**
セキュリティスキャンで誤った警告が出る

**原因:**
- ツールの誤検出
- 設定の不備
- コードパターンの問題

**解決方法:**

1. **除外設定の追加**
   ```python
   # コード内でのスキップ
   # nosec B101
   password = "test_password"  # テスト用パスワード
   ```

2. **設定ファイルでの除外**
   ```ini
   # .bandit
   [bandit]
   exclude_dirs = tests,build,dist
   skips = B101,B601
   ```

3. **手動での検証**
   ```bash
   # 特定の問題のみスキャン
   bandit -r qt_theme_studio/ -f json | jq '.results[] | select(.test_id=="B101")'
   ```

## 環境固有の問題

### 問題18: Windows環境での問題

**症状:**
パス区切り文字やコマンドの違いによるエラー

**原因:**
- パス区切り文字の違い（`/` vs `\`）
- コマンドの違い
- 権限モデルの違い

**解決方法:**

1. **パスの正規化**
   ```python
   from pathlib import Path
   
   # クロスプラットフォーム対応
   config_path = Path(".kiro") / "workflow" / "config.yml"
   ```

2. **Windows用スクリプトの使用**
   ```batch
   REM setup_dev_environment.bat
   setup_dev_environment.bat
   ```

3. **PowerShell実行ポリシーの設定**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### 問題19: macOS環境での問題

**症状:**
システム整合性保護（SIP）による制限

**原因:**
- SIPによるファイルアクセス制限
- Homebrewとの競合
- 権限の問題

**解決方法:**

1. **Homebrewの使用**
   ```bash
   # Homebrewでのインストール
   brew install python
   ```

2. **仮想環境の使用**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **権限の確認**
   ```bash
   # ディスクアクセス権限の確認
   ls -la /System/Library/
   ```

### 問題20: Linux環境での問題

**症状:**
ディストリビューション固有の問題

**原因:**
- パッケージマネージャーの違い
- システムライブラリの違い
- 権限設定の違い

**解決方法:**

1. **システムパッケージのインストール**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev python3-venv
   
   # CentOS/RHEL
   sudo yum install python3-devel
   
   # Arch Linux
   sudo pacman -S python python-pip
   ```

2. **仮想ディスプレイの設定**
   ```bash
   sudo apt-get install xvfb
   export DISPLAY=:99
   Xvfb :99 -screen 0 1024x768x24 &
   ```

## デバッグ手順

### 基本的なデバッグ手順

1. **問題の再現**
   ```bash
   # 問題を再現する最小限のコマンド
   python scripts/workflow_engine.py problem_workflow
   ```

2. **ログレベルの上昇**
   ```bash
   export WORKFLOW_LOG_LEVEL=DEBUG
   export WORKFLOW_DEBUG=true
   ```

3. **個別コンポーネントのテスト**
   ```bash
   # 設定マネージャーのテスト
   python scripts/config_manager.py
   
   # ワークフローエンジンのテスト
   python scripts/workflow_engine.py
   
   # ダッシュボードのテスト
   python scripts/quality_dashboard.py
   ```

4. **依存関係の確認**
   ```bash
   pip check
   pip list
   python --version
   ```

### 高度なデバッグ手順

1. **プロファイリング**
   ```bash
   # パフォーマンスプロファイリング
   python -m cProfile -o profile.stats scripts/workflow_engine.py
   
   # メモリプロファイリング
   python scripts/memory_profiler.py
   ```

2. **ネットワーク診断**
   ```bash
   # 外部依存関係の確認
   ping github.com
   curl -I https://pypi.org/
   ```

3. **システムリソースの監視**
   ```bash
   # リアルタイム監視
   top
   iotop
   netstat -tulpn
   ```

## ログ分析

### ログファイルの場所

```
logs/
├── workflow.log              # ワークフロー実行ログ
├── *_errors.log             # エラーログ
├── *_performance.log        # パフォーマンスログ
├── *_structured_*.log       # 構造化ログ
└── metrics_history.json     # メトリクス履歴
```

### ログ分析コマンド

1. **エラーの検索**
   ```bash
   # エラーメッセージの検索
   grep -i error logs/*.log
   
   # 特定の時間範囲のログ
   grep "2024-01-01 12:" logs/workflow.log
   
   # 重要度別のログ
   grep -E "(ERROR|CRITICAL)" logs/*.log
   ```

2. **パフォーマンス分析**
   ```bash
   # 実行時間の分析
   grep "実行時間" logs/*_performance.log
   
   # メモリ使用量の分析
   grep "メモリ" logs/*.log
   ```

3. **構造化ログの分析**
   ```bash
   # JSONログの解析
   jq '.level == "ERROR"' logs/*_structured_*.log
   
   # 特定のワークフローのログ
   jq '.workflow == "ci_pipeline"' logs/*_structured_*.log
   ```

### ログローテーション

```yaml
# .kiro/workflow/config.yml
notifications:
  channels:
    - type: "file"
      path: "logs/workflow.log"
      max_size: "10MB"
      backup_count: 5
      rotation: "daily"
```

## 復旧手順

### 緊急時の復旧手順

1. **システムの停止**
   ```bash
   # 実行中のプロセスを停止
   pkill -f workflow_engine
   pkill -f quality_dashboard
   ```

2. **バックアップからの復旧**
   ```bash
   # 設定ファイルの復旧
   cp .kiro/workflow/config.yml.backup .kiro/workflow/config.yml
   
   # ログファイルのアーカイブ
   tar -czf logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz logs/
   ```

3. **クリーンな状態での再起動**
   ```bash
   # キャッシュのクリア
   rm -rf .kiro/cache/*
   
   # 一時ファイルの削除
   find . -name "*.tmp" -delete
   find . -name "*.pyc" -delete
   
   # システムの再初期化
   python scripts/config_manager.py
   python scripts/workflow_engine.py
   ```

### データの復旧

1. **メトリクス履歴の復旧**
   ```bash
   # バックアップからの復旧
   cp logs/metrics_history.json.backup logs/metrics_history.json
   ```

2. **設定の復旧**
   ```bash
   # Git履歴からの復旧
   git checkout HEAD~1 -- .kiro/workflow/config.yml
   ```

3. **ログファイルの復旧**
   ```bash
   # アーカイブからの展開
   tar -xzf logs_backup_*.tar.gz
   ```

### 予防措置

1. **定期的なバックアップ**
   ```bash
   # 自動バックアップスクリプト
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   tar -czf "backup_${DATE}.tar.gz" .kiro/ logs/
   ```

2. **監視の設定**
   ```yaml
   # .kiro/workflow/config.yml
   monitoring:
     alerts:
       high_failure_rate:
         threshold: 20
         action: "email_admin"
   ```

3. **ヘルスチェック**
   ```bash
   # 定期的なヘルスチェック
   python scripts/workflow_engine.py --health-check
   ```

---

このトラブルシューティングガイドは継続的に更新されます。新しい問題や解決方法が見つかった場合は、このドキュメントに追加してください。