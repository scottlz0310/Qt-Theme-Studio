# CI/CDガイドライン

## 概要

Qt-Theme-Studioプロジェクトの継続的インテグレーション（CI）と継続的デプロイメント（CD）のガイドラインです。コード品質の維持、自動テスト、リリース自動化を実現します。

## Pre-commitフック

**設定ファイル**: `.pre-commit-config.yaml`

**実行されるチェック**:
- **black**: コード整形（88文字行長）
- **isort**: インポート文の整理
- **autoflake**: 未使用インポートの削除
- **flake8**: コード品質チェック
- **mypy**: 型チェック（オプション）

**セットアップ手順**:
```bash
# Pre-commitのインストール
pip install pre-commit

# フックの有効化
pre-commit install

# 全ファイルに対して実行（初回）
pre-commit run --all-files
```

**動作**:
- `git commit` 実行時に自動実行
- チェック失敗時はコミットが阻止される
- 自動修正可能な問題は自動的に修正される

## GitHubワークフロー

### CI ワークフロー（`.github/workflows/ci.yml`）

**トリガー**:
- プルリクエスト作成・更新時
- mainブランチへのプッシュ時

**実行内容**:
- 複数Pythonバージョンでのテスト（3.8, 3.9, 3.10, 3.11）
- コード品質チェック（black, isort, flake8）
- テストカバレッジ測定
- 型チェック（mypy）

**品質ゲート**:
- すべてのテストが成功
- コードカバレッジ90%以上
- Lintエラーゼロ
- 型チェック成功

### リリースワークフロー（`.github/workflows/release.yml`）

**トリガー**:
- バージョンタグのプッシュ（例: v1.0.0）

**実行内容**:
- アプリケーションのビルド
- GitHub Releasesの自動作成
- 配布用アーティファクトの添付
- 変更履歴の自動生成

### セキュリティワークフロー（`.github/workflows/security.yml`）

**トリガー**:
- 定期実行（週次）
- 依存関係ファイル更新時

**実行内容**:
- 依存関係の脆弱性スキャン
- セキュリティアラートの作成
- 自動修正プルリクエストの作成

## 依存関係管理

**重要な依存関係インストール**:
```bash
# qt-theme-managerは必ずGitHubから直接インストール
pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git

# その他の開発依存関係
pip install -e .[dev]
```

**CI/CDでの依存関係**:
- GitHubワークフローでは必ずGitリポジトリからqt-theme-managerをインストール
- PyPIからのインストールは使用しない
- requirements.txtやpyproject.tomlでGitリポジトリURLを指定

## 開発ワークフロー

### 日常開発

1. **ブランチ作成**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **開発・コミット**:
   ```bash
   # Pre-commitが自動実行される
   git add .
   git commit -m "feat: 新機能を追加"
   ```

3. **プルリクエスト作成**:
   - GitHubでプルリクエスト作成
   - CIワークフローが自動実行
   - レビュー後にマージ

### リリース手順

1. **バージョン更新**:
   ```bash
   # pyproject.tomlのバージョンを更新
   git add pyproject.toml
   git commit -m "bump: version to 1.0.0"
   ```

2. **タグ作成・プッシュ**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **自動リリース**:
   - リリースワークフローが自動実行
   - GitHub Releasesが作成される

## コード品質基準

**必須チェック項目**:
- PEP 8準拠（black + flake8）
- インポート整理（isort）
- 未使用インポート削除（autoflake）
- タイプヒント（mypy）
- テストカバレッジ90%以上

**自動修正対象**:
- コード整形（black）
- インポート順序（isort）
- 未使用インポート（autoflake）
- 行末空白の削除

**手動修正が必要**:
- 論理エラー
- 型エラー
- テストの追加
- docstringの追加

## トラブルシューティング

**Pre-commitが失敗する場合**:
```bash
# 手動でチェック実行
pre-commit run --all-files

# 特定のフックのみ実行
pre-commit run black
pre-commit run flake8
```

**CIが失敗する場合**:
- ローカルでテスト実行: `pytest`
- コード品質チェック: `flake8 .`
- カバレッジ確認: `pytest --cov=qt_theme_studio`

**リリースが失敗する場合**:
- タグの形式確認（v1.0.0形式）
- pyproject.tomlのバージョン確認
- GitHubトークンの権限確認

## Kiro特有の制約

**日本語対応**:
- エラーメッセージは日本語で表示
- ログ出力は日本語
- ドキュメントは日本語で記述

**品質要件**:
- print文は絶対禁止 - loggerを使用
- すべてのコメント・docstringは日本語
- 変数名・関数名は英語（国際標準準拠）
