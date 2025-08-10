# 技術スタック

## コア技術

**Python**: 主要開発言語
- 対象バージョン: Python 3.8+
- コードベース全体でタイプヒント必須
- PEP 8準拠が必須

**Qt フレームワーク**: GUIアプリケーション用フレームワーク
- PySide6（推奨）
- PyQt6（フォールバック）
- PyQt5（レガシーサポート）
- qt-theme-managerライブラリの自動検出機能を活用

**依存ライブラリ**:
- qt-theme-manager: コアテーマ管理機能（GitHubから直接インストール）
- pillow: 画像処理・プレビュー生成
- colorama: コンソール出力の色付け

**重要なインストール注意事項**:
- qt-theme-managerは必ずGitHubリポジトリから直接インストールする
- インストールコマンド: `pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git`
- PyPIからのインストールは使用しない

## ビルドシステム

**パッケージ管理**: 
- `pyproject.toml` GUIアプリケーション設定用
- GitHub Releases経由での配布

**開発依存関係**:
- pytest + pytest-qt GUIテスト用
- black コード整形用
- isort インポート整理用
- flake8 リンティング用
- autoflake 未使用インポート削除用

## コード標準

**整形**:
- 行長: 88文字（GUIツール標準）
- Black フォーマッター設定
- isort インポート整理用
- print文禁止 - 代わりにloggerを使用

**品質要件**:
- テストカバレッジ: 90%（GUIツール目標）
- タイプヒント必須
- docstring カバレッジ必須
- 未使用インポート禁止

## アーキテクチャ要件

**MVCパターン**:
- Model: データ管理とビジネスロジック
- View: UIコンポーネントとユーザーインターフェース
- Controller: ユーザー操作とデータ処理の橋渡し

**アダプターパターン**:
- qt-theme-managerライブラリとの統合
- 異なるQtフレームワーク間の互換性

## 共通コマンド

**開発環境セットアップ**:
```bash
pip install -e .[dev]
pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git
```

**アプリケーション起動**:
```bash
python launch_theme_studio.py
python -m qt_theme_studio
```

**コード整形**:
```bash
black .
isort .
autoflake --remove-all-unused-imports --in-place --recursive .
```

**テスト**:
```bash
pytest
pytest --cov=qt_theme_studio --cov-report=html
```

**リンティング**:
```bash
flake8 .
```

**ビルド・配布**:
```bash
python -m build
# GitHub Releasesでの配布
```

## CI/CDシステム

**Pre-commit フック**:
- `.pre-commit-config.yaml` 設定ファイル必須
- black、isort、autoflake、flake8の自動実行
- コミット前の自動コード品質チェック
- 修正可能な問題の自動修正

**Pre-commit セットアップ**:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # 全ファイルチェック
```

**GitHub ワークフロー**:
- `.github/workflows/` ディレクトリに設定
- プルリクエスト時の自動テスト実行
- 複数Pythonバージョンでのテスト（3.8, 3.9, 3.10, 3.11）
- コード品質チェックの自動実行
- テストカバレッジレポート生成

**自動化要件**:
- プルリクエスト作成時: テスト + 品質チェック実行
- mainブランチマージ時: 全テスト実行
- タグプッシュ時: リリース自動作成
- 定期実行: 依存関係脆弱性チェック

**品質ゲート**:
- すべてのテストが成功
- コードカバレッジ90%以上
- Lintエラーゼロ
- 型チェック（mypy）成功

## Kiro特有の制約

**言語要件**:
- すべての応答は日本語で行う
- ドキュメントは日本語で記述する
- コードコメントは日本語で記述する
- docstringは日本語で記述する
- 変数名・関数名は英語、説明・コメントは日本語

**コード品質**:
- print文は絶対禁止 - 必ずloggerを使用
- すべてのログメッセージは日本語
- エラーメッセージも日本語で記述