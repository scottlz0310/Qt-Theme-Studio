# Qt-Theme-Studio テスト環境

このディレクトリには、Qt-Theme-Studioアプリケーションのテストスイートが含まれています。

## テスト構成

### ディレクトリ構造

```
tests/
├── __init__.py              # テストパッケージ初期化
├── conftest.py              # pytest共通設定とフィクスチャ
├── README.md                # このファイル
├── run_tests.py             # テスト実行スクリプト
├── unit/                    # 単体テスト
│   ├── __init__.py
│   ├── test_theme_adapter.py
│   └── test_qt_adapter.py
├── integration/             # 統合テスト
│   ├── __init__.py
│   └── test_theme_integration.py
└── fixtures/                # テストフィクスチャ
    ├── __init__.py
    ├── theme_data.py        # テーマデータフィクスチャ
    └── mock_objects.py      # モックオブジェクト
```

### テストの種類

#### 単体テスト (`tests/unit/`)
- 各モジュールの個別機能をテスト
- 依存関係をモック化して単体で動作を確認
- 高速で実行可能

#### 統合テスト (`tests/integration/`)
- 複数モジュール間の連携をテスト
- エンドツーエンドの動作を確認
- 実際のファイルI/Oやデータベース操作を含む

#### フィクスチャ (`tests/fixtures/`)
- テストで使用する共通データ
- モックオブジェクトの作成
- ヘルパー関数

## テストの実行

### 基本的な実行方法

```bash
# すべてのテストを実行
python -m pytest

# 単体テストのみ実行
python -m pytest tests/unit/

# 統合テストのみ実行
python -m pytest tests/integration/

# カバレッジレポート付きで実行
python -m pytest --cov=qt_theme_studio --cov-report=html
```

### テスト実行スクリプトの使用

```bash
# 基本的なテスト実行
python tests/run_tests.py

# 単体テストのみ
python tests/run_tests.py --unit

# 統合テストのみ
python tests/run_tests.py --integration

# カバレッジレポート生成
python tests/run_tests.py --coverage

# 詳細出力
python tests/run_tests.py --verbose

# 高速モード（並列実行）
python tests/run_tests.py --fast
```

## テストの書き方

### 基本的なテストクラス

```python
import pytest
from unittest.mock import Mock

class TestExample:
    """テストクラスの例"""
    
    def setup_method(self) -> None:
        """各テストメソッドの前処理"""
        self.mock_object = Mock()
    
    def test_example_function(self) -> None:
        """テストメソッドの例"""
        # テストの実装
        result = self.example_function()
        assert result == expected_value
```

### フィクスチャの使用

```python
def test_with_fixture(sample_theme_data, mock_qt_app):
    """フィクスチャを使用したテスト"""
    # sample_theme_dataとmock_qt_appが自動的に提供される
    assert sample_theme_data["name"] == "Test Theme"
```

### マーカーの使用

```python
@pytest.mark.slow
def test_slow_operation():
    """実行時間が長いテスト"""
    pass

@pytest.mark.qt
def test_qt_specific():
    """Qt固有のテスト"""
    pass
```

## CI/CD統合

### GitHub Actions

`.github/workflows/test.yml` で以下の処理が自動実行されます：

1. **コード品質チェック**
   - Black（コードフォーマット）
   - isort（インポート順序）
   - flake8（リンター）
   - mypy（型チェック）

2. **セキュリティチェック**
   - bandit（セキュリティ脆弱性）
   - safety（依存関係の脆弱性）

3. **テスト実行**
   - 単体テスト
   - 統合テスト
   - カバレッジレポート生成

4. **パフォーマンステスト**
   - ベンチマークテスト

### ローカルでの事前チェック

```bash
# コードフォーマット
black qt_theme_studio tests

# インポート順序
isort qt_theme_studio tests

# リンター
flake8 qt_theme_studio tests

# 型チェック
mypy qt_theme_studio tests

# セキュリティチェック
bandit -r qt_theme_studio
safety check
```

## カバレッジ

テストカバレッジは以下の方法で確認できます：

1. **HTMLレポート**: `htmlcov/index.html`
2. **ターミナル出力**: `--cov-report=term`
3. **XMLレポート**: `--cov-report=xml` (CI/CD用)

## トラブルシューティング

### よくある問題

1. **インポートエラー**
   - `PYTHONPATH`の設定を確認
   - 仮想環境の有効化を確認

2. **Qt関連のエラー**
   - ディスプレイ環境の設定
   - モックの適切な使用

3. **パフォーマンステストの失敗**
   - システムリソースの確認
   - ベンチマークの閾値調整

### デバッグ

```bash
# 詳細なデバッグ出力
python -m pytest -v -s --tb=long

# 特定のテストのみ実行
python -m pytest tests/unit/test_example.py::TestExample::test_method

# 失敗したテストの詳細
python -m pytest --lf --tb=long
```

## 貢献

新しいテストを追加する際は、以下の点に注意してください：

1. **テストファイル名**: `test_*.py` の形式
2. **テストクラス名**: `Test*` の形式
3. **テストメソッド名**: `test_*` の形式
4. **適切なマーカー**: `@pytest.mark.*` の使用
5. **フィクスチャの活用**: 共通処理の重複を避ける
6. **日本語コメント**: テストの目的を明確に記述
