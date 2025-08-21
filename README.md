# Qt-Theme-Studio

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/your-org/qt-theme-studio/releases)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Qt-Theme-Studioは、Qtアプリケーション（PyQt5/PyQt6/PySide6）向けの統合テーマエディターGUIアプリケーションです。qt-theme-managerライブラリを基盤として、直感的なビジュアルインターフェースでテーマの作成・編集・管理を行います。

## 主要機能

- **統合テーマエディター**: 直感的なビジュアルインターフェースでテーマプロパティを編集
- **CLI モジュール**: テーマ品質チェック機能
- **ライブプレビューシステム**: リアルタイムでテーマの変更を確認
- **スマートテーマ管理**: テーマの保存、読み込み、エクスポート機能
- **アクセシビリティ対応**: WCAG準拠のコントラスト調整機能
- **CI/CD パイプライン**: 自動化されたコード品質チェックとテスト実行

## システム要件

- Python 3.9以上
- Qt フレームワーク（PySide6推奨、PyQt6/PyQt5対応）
- qt-theme-managerライブラリ

## インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-org/qt-theme-studio.git
cd qt-theme-studio
```

### 2. 依存関係のインストール

```bash
# 基本インストール
pip install -e .

# 開発用依存関係も含める場合
pip install -e .[dev]

# 重要: qt-theme-managerは必ずGitHubから直接インストール
pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git
```

### 3. 追加のQtフレームワーク（オプション）

```bash
# PyQt6を使用する場合
pip install -e .[qt6]

# PyQt5を使用する場合
pip install -e .[qt5]
```

## 使用方法

### 基本的な起動

```bash
# メインランチャーを使用
python main.py

# または、モジュールとして実行
python -m qt_theme_studio

# または、インストール後のコマンド
qt-theme-studio
```

## 開発

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
pip install -e .[dev]

# Pre-commitフックの設定
pre-commit install
```

### コード品質チェック

```bash
# Ruffによるリンティングとフォーマット
ruff check qt_theme_studio/
ruff format qt_theme_studio/
```

### テスト実行

```bash
# 基本テスト実行
pytest tests/unit/ -v
```

## プロジェクト構造

```
qt-theme-studio/
├── qt_theme_studio/           # メインアプリケーションパッケージ
│   ├── config/               # 設定管理
│   ├── adapters/             # ライブラリ統合レイヤー
│   ├── views/                # UIコンポーネント（MVCパターン）
│   ├── controllers/          # ビジネスロジック（MVCパターン）
│   ├── services/             # アプリケーションサービス
│   ├── utilities/            # ユーティリティ関数
│   └── resources/            # アセットとテンプレート
├── examples/                 # 使用例とサンプル
├── scripts/                  # ユーティリティスクリプト
├── tests/                    # テストファイル
├── launch_theme_studio.py    # 統合ランチャー
└── pyproject.toml           # プロジェクト設定
```

## ライセンス

MIT License

## 貢献

プルリクエストや課題報告を歓迎します。詳細な貢献ガイドラインについては、CONTRIBUTINGファイルを参照してください。

## サポート

- GitHub Issues: バグ報告や機能要求
- ドキュメント: プロジェクトのdocsディレクトリ
- 例とサンプル: examplesディレクトリ

## 注意事項

- qt-theme-managerライブラリは必ずGitHubリポジトリから直接インストールしてください
- PyPIからのqt-theme-managerインストールは使用しないでください
- 日本語ファイル名・パスに対応していますが、文字化けを避けるためUTF-8エンコーディングを推奨します

## 更新履歴

詳細な変更履歴については [CHANGELOG.md](CHANGELOG.md) を参照してください。
