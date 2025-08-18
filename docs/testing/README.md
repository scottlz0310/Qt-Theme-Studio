# テスト環境

## 📁 ディレクトリ構成

```
tests/
├── unit/                    # 単体テスト
│   ├── test_theme_adapter.py
│   └── test_qt_adapter.py
├── integration/             # 統合テスト
│   └── test_theme_integration.py
├── fixtures/                # テスト用データ・モック
│   ├── theme_data.py
│   ├── mock_objects.py
│   └── test_theme.json
├── conftest.py             # pytest設定・フィクスチャ
└── run_tests.py            # テスト実行スクリプト
```

## 🚀 テストの実行

### 基本的な実行
```bash
# 全テスト実行
python -m pytest tests/

# 単体テストのみ
python -m pytest tests/unit/

# 統合テストのみ
python -m pytest tests/integration/
```

### カバレッジ付き実行
```bash
# カバレッジレポート付き
python -m pytest tests/ --cov=qt_theme_studio --cov-report=term-missing

# HTMLレポート生成
python -m pytest tests/ --cov=qt_theme_studio --cov-report=html:htmlcov
```

### 便利な実行スクリプト
```bash
# 単体テストのみ
python tests/run_tests.py --unit

# 統合テストのみ
python tests/run_tests.py --integration

# カバレッジ付き
python tests/run_tests.py --coverage

# 詳細出力
python tests/run_tests.py --verbose
```

## 🧪 テストの種類

### 1. 単体テスト (Unit Tests)
- 個々のクラス・メソッドのテスト
- 外部依存をモック化
- 高速で安定

### 2. 統合テスト (Integration Tests)
- 複数コンポーネント間の連携テスト
- 実際の依存関係を使用
- より現実的なテスト

### 3. GUIテスト (GUI Tests)
- Qtウィジェットのテスト
- ユーザーインタラクションのテスト
- 不安定になりがち

### 4. パフォーマンステスト (Performance Tests)
- 実行時間・メモリ使用量の測定
- ベンチマーク比較
- リグレッション検出

## 📊 カバレッジ

### 現在の状況
- **全体**: 21%
- **アダプター層**: 42-62%
- **ビュー層**: 0%

### 改善計画
詳細は [coverage_improvement_strategy.md](./coverage_improvement_strategy.md) を参照

## 🛠️ テストツール

### 主要ツール
- **pytest**: テストフレームワーク
- **pytest-cov**: カバレッジ測定
- **pytest-qt**: Qtテストサポート
- **pytest-benchmark**: パフォーマンステスト

### コード品質ツール
- **Black**: コードフォーマッター
- **isort**: インポートソーター
- **flake8**: リンター
- **mypy**: 静的型チェッカー

## 🔧 設定ファイル

### pytest.ini
- テスト設定
- マーカー定義
- カバレッジ設定

### pyproject.toml
- 開発依存関係
- ツール設定
- プロジェクト情報

## 📝 テスト作成ガイドライン

### 1. テストファイル命名
- `test_*.py` 形式
- テスト対象モジュールに対応

### 2. テストクラス命名
- `Test*` 形式
- テスト対象クラスに対応

### 3. テストメソッド命名
- `test_*` 形式
- テスト内容を明確に記述

### 4. フィクスチャの使用
- `conftest.py` で共通フィクスチャを定義
- テストデータは `fixtures/` に配置

### 5. モック化
- 外部依存は適切にモック化
- テストの安定性を確保

## 🚨 よくある問題と解決方法

### 1. インポートエラー
- PYTHONPATHの設定
- 相対インポートの確認
- モジュール構造の確認

### 2. Qt関連のエラー
- ヘッドレスモードでの実行
- 適切なモック化
- テスト環境の分離

### 3. カバレッジが低い
- 未テストコードの特定
- エラーハンドリングパスのテスト
- 境界値テストの追加

## 📚 参考資料

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov公式ドキュメント](https://pytest-cov.readthedocs.io/)
- [Qt for Python Testing](https://doc.qt.io/qtforpython/overviews/qt-testing.html)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
