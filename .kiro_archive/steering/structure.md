# プロジェクト構造

## Qt-Theme-Studio（このリポジトリ）

```
qt-theme-studio/
├── qt_theme_studio/           # メインGUIアプリケーションパッケージ
│   ├── __init__.py           # パッケージ初期化
│   ├── main.py               # アプリケーションエントリーポイント
│   ├── config/               # アプリケーション設定管理
│   │   ├── __init__.py
│   │   ├── settings.py       # 設定クラス
│   │   └── defaults.py       # デフォルト設定
│   ├── adapters/             # qt-theme-managerライブラリ統合レイヤー
│   │   ├── __init__.py
│   │   ├── theme_adapter.py  # テーマライブラリアダプター
│   │   └── qt_adapter.py     # Qt フレームワークアダプター
│   ├── views/                # UIコンポーネント（MVCパターン）
│   │   ├── __init__.py
│   │   ├── main_window.py    # メインウィンドウ
│   │   ├── theme_editor.py   # テーマエディター
│   │   ├── zebra_editor.py   # ゼブラパターンエディター
│   │   ├── preview.py        # プレビューウィンドウ
│   │   └── dialogs/          # ダイアログコンポーネント
│   ├── controllers/          # ビジネスロジック（MVCパターン）
│   │   ├── __init__.py
│   │   ├── theme_controller.py    # テーマ管理コントローラー
│   │   ├── zebra_controller.py    # ゼブラパターンコントローラー
│   │   └── preview_controller.py  # プレビューコントローラー
│   ├── services/             # アプリケーションサービス
│   │   ├── __init__.py
│   │   ├── theme_service.py  # テーマ管理サービス
│   │   ├── export_service.py # エクスポートサービス
│   │   └── validation_service.py # 検証サービス
│   ├── utilities/            # GUI専用ユーティリティ
│   │   ├── __init__.py
│   │   ├── color_analyzer.py # 色解析ユーティリティ
│   │   ├── color_improver.py # 色改善ユーティリティ
│   │   └── ui_helpers.py     # UI ヘルパー関数
│   └── resources/            # アセットとテンプレート
│       ├── icons/            # アイコンファイル
│       ├── templates/        # テーマテンプレート
│       └── styles/           # スタイルシート
├── examples/                 # 使用例とサンプル
├── scripts/                  # ユーティリティスクリプト
├── docs/                     # GUIツールドキュメント
├── tests/                    # テストファイル
├── .github/                  # GitHub設定
│   └── workflows/            # GitHubワークフロー
│       ├── ci.yml           # 継続的インテグレーション
│       ├── release.yml      # リリース自動化
│       └── security.yml     # セキュリティチェック
├── .pre-commit-config.yaml   # Pre-commitフック設定
├── launch_theme_studio.py    # 統合ランチャー（メインエントリーポイント）
├── pyproject.toml           # プロジェクト設定
├── README.md                # プロジェクトドキュメント
└── CHANGELOG.md             # 変更履歴
```

## アーキテクチャパターン

**MVCアーキテクチャ**:
- **Model**: `services/` - データ管理とビジネスロジック
- **View**: `views/` - UIコンポーネントとユーザーインターフェース  
- **Controller**: `controllers/` - ユーザー操作とデータ処理の橋渡し

**アダプターパターン**:
- `adapters/` - qt-theme-managerライブラリとの統合
- 異なるQtフレームワーク間の互換性保証

**サービスレイヤー**:
- `services/` - 複雑なビジネスロジックの分離
- 再利用可能なアプリケーション機能

## ファイル整理ルール

**パッケージ構造**:
- すべてのコードは `qt_theme_studio/` パッケージ内に配置
- 適切なサブパッケージに機能を分離
- `__init__.py` ファイルで適切なインポートを提供

**スクリプト整理**:
- メインランチャーのみルートに配置（`launch_theme_studio.py`）
- その他のスクリプトは `scripts/` ディレクトリに配置
- 実行可能スクリプトには適切なシバン行を追加

**リソース管理**:
- 静的リソースは `resources/` ディレクトリに整理
- アイコン、テンプレート、スタイルを分離
- リソースファイルの相対パス参照を使用

## 開発ガイドライン

**依存関係管理**:
- qt-theme-managerライブラリへの依存
- Qt フレームワークの自動検出機能を活用
- 最小限の外部依存関係を維持

**テスト戦略**:
- 各コンポーネントに対応する単体テスト
- pytest-qtを使用したGUIテスト
- 統合テストでワークフロー検証

**CI/CD構造**:
- `.github/workflows/` - GitHubアクション設定
- `.pre-commit-config.yaml` - コミット前フック設定
- 自動テスト実行とコード品質チェック
- リリース自動化とセキュリティ監視

**ログ管理**:
- print文禁止 - 必ずloggerを使用
- 適切なログレベルの設定
- デバッグ情報の構造化

## 命名規則

**パッケージ**: snake_case (qt_theme_studio)
**モジュール**: snake_case (color_analyzer.py)
**クラス**: PascalCase (ThemeController)
**関数/変数**: snake_case (get_theme_data)
**定数**: UPPER_SNAKE_CASE (DEFAULT_THEME_PATH)
**プライベート**: _leading_underscore (_internal_method)

## Kiro特有の制約

**言語要件**:
- すべての応答は日本語で行う
- ドキュメント（README、API仕様書等）は日本語で記述
- コードコメントは日本語で記述
- docstringは日本語で記述
- ログメッセージは日本語で記述
- エラーメッセージは日本語で記述

**コード記述ルール**:
- 変数名・関数名・クラス名は英語（国際標準に準拠）
- コメント・docstring・説明文は日本語
- print文は絶対禁止 - 必ずloggerを使用
- すべてのログ出力は日本語で記述

**ドキュメント要件**:
- README.mdは日本語で記述
- API仕様書は日本語で記述
- 設計ドキュメントは日本語で記述
- ユーザーマニュアルは日本語で記述