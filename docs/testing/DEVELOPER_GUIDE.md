# Qt-Theme-Studio 開発者テストガイド

## 🚀 クイックスタート

### **前提条件**
- Python 3.11以上
- pip
- Git

### **セットアップ手順**

```bash
# 1. リポジトリのクローン
git clone https://github.com/scottlz0310/Qt-Theme-Studio.git
cd Qt-Theme-Studio

# 2. 仮想環境の作成
python -m venv venv

# 3. 仮想環境の有効化
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. 依存関係のインストール
pip install -e .
pip install -e ".[dev]"

# 5. テストの実行
python -m pytest tests/ -v
```

## 🧪 テスト環境の構成

### **ディレクトリ構造**
```
Qt-Theme-Studio/
├── tests/                    # テストファイル
│   ├── unit/                # 単体テスト
│   ├── integration/         # 統合テスト
│   ├── fixtures/            # テストフィクスチャ
│   └── conftest.py          # pytest設定
├── qt_theme_studio/         # ソースコード
├── docs/testing/            # テストドキュメント
├── .github/workflows/       # CI/CD設定
├── pytest.ini              # pytest設定
└── pyproject.toml           # プロジェクト設定
```

### **設定ファイル**

#### **pytest.ini**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=qt_theme_studio
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    gui: GUI tests
```

#### **pyproject.toml**
```toml
[tool.black]
line-length = 88
target-version = ['py311', 'py312', 'py313']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## 📋 テスト実行コマンド

### **基本的なテスト実行**

```bash
# 全テスト実行
python -m pytest tests/ -v

# 特定のディレクトリ
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# 特定のファイル
python -m pytest tests/unit/test_theme_adapter.py -v

# 特定のテストクラス
python -m pytest tests/unit/test_theme_adapter.py::TestThemeAdapter -v

# 特定のテストメソッド
python -m pytest tests/unit/test_theme_adapter.py::TestThemeAdapter::test_init -v
```

### **マーカーを使用したテスト実行**

```bash
# 単体テストのみ
python -m pytest tests/ -m unit -v

# 統合テストのみ
python -m pytest tests/ -m integration -v

# 遅いテストを除外
python -m pytest tests/ -m "not slow" -v

# GUIテストを除外
python -m pytest tests/ -m "not gui" -v
```

### **カバレッジ測定**

```bash
# 基本カバレッジ
python -m pytest tests/ --cov=qt_theme_studio --cov-report=term-missing

# 特定モジュールのカバレッジ
python -m pytest tests/ --cov=qt_theme_studio.adapters.theme_adapter --cov-report=term-missing

# HTMLレポート生成
python -m pytest tests/ --cov=qt_theme_studio --cov-report=html

# XMLレポート生成（CI/CD用）
python -m pytest tests/ --cov=qt_theme_studio --cov-report=xml
```

### **パフォーマンステスト**

```bash
# ベンチマークテスト
python -m pytest tests/ --benchmark-only

# 特定のパフォーマンステスト
python -m pytest tests/integration/test_comprehensive_integration.py::TestComprehensiveIntegration::test_performance_under_load -v --benchmark-only

# メモリ効率テスト
python -m pytest tests/integration/test_comprehensive_integration.py::TestComprehensiveIntegration::test_memory_efficiency_workflow -v
```

## 🔧 テスト開発ガイド

### **新しいテストの作成**

#### **1. テストファイルの作成**
```python
# tests/unit/test_new_feature.py
import pytest
from unittest.mock import Mock

class TestNewFeature:
    """新機能のテスト"""
    
    def setup_method(self):
        """各テストメソッドの前処理"""
        self.mock_dependency = Mock()
        
    def test_new_feature_basic(self):
        """新機能の基本テスト"""
        # テストの実装
        assert True
        
    def test_new_feature_edge_case(self):
        """新機能のエッジケーステスト"""
        # エッジケースのテスト
        assert True
```

#### **2. テストフィクスチャの作成**
```python
# tests/fixtures/new_feature_data.py
import pytest

@pytest.fixture
def sample_data():
    """サンプルデータのフィクスチャ"""
    return {
        "name": "Test Data",
        "value": 42
    }

@pytest.fixture
def mock_service():
    """モックサービスのフィクスチャ"""
    from unittest.mock import Mock
    service = Mock()
    service.get_data.return_value = {"status": "success"}
    return service
```

#### **3. テストの実行と確認**
```bash
# 新しいテストの実行
python -m pytest tests/unit/test_new_feature.py -v

# カバレッジの確認
python -m pytest tests/unit/test_new_feature.py --cov=qt_theme_studio.new_feature --cov-report=term-missing
```

### **テストのベストプラクティス**

#### **1. テストの命名規則**
```python
# 良い例
def test_user_can_login_with_valid_credentials():
    """有効な認証情報でユーザーがログインできることをテスト"""
    pass

def test_login_fails_with_invalid_credentials():
    """無効な認証情報でログインが失敗することをテスト"""
    pass

# 悪い例
def test_login():
    """ログインテスト"""
    pass
```

#### **2. テストの構造**
```python
def test_feature_behavior():
    """テストの構造例"""
    # Arrange (準備)
    input_data = "test input"
    expected_output = "expected result"
    
    # Act (実行)
    actual_output = process_data(input_data)
    
    # Assert (検証)
    assert actual_output == expected_output
```

#### **3. モックの使用**
```python
from unittest.mock import Mock, patch

def test_with_mock():
    """モックを使用したテスト例"""
    # 依存関係のモック化
    mock_service = Mock()
    mock_service.get_data.return_value = {"result": "success"}
    
    # テスト対象の実行
    result = process_with_service(mock_service)
    
    # モックの呼び出し確認
    mock_service.get_data.assert_called_once()
    assert result == "success"
```

## 🐛 トラブルシューティング

### **よくある問題と解決方法**

#### **1. インポートエラー**
```bash
# 問題: ModuleNotFoundError
# 解決: PYTHONPATHの設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### **2. カバレッジが正しく測定されない**
```bash
# 問題: カバレッジが0%になる
# 解決: ソースディレクトリの指定
python -m pytest tests/ --cov=qt_theme_studio --cov-report=term-missing
```

#### **3. テストが遅い**
```bash
# 問題: テストの実行が遅い
# 解決: 並行実行の使用
python -m pytest tests/ -n auto

# または、遅いテストを除外
python -m pytest tests/ -m "not slow"
```

#### **4. メモリ不足**
```bash
# 問題: メモリ不足でテストが失敗
# 解決: メモリ効率テストの除外
python -m pytest tests/ -m "not memory_intensive"
```

## 📊 テスト結果の分析

### **カバレッジレポートの読み方**

```bash
# HTMLレポートの生成
python -m pytest tests/ --cov=qt_theme_studio --cov-report=html

# ブラウザでレポートを開く
# htmlcov/index.html
```

#### **カバレッジの色分け**
- **緑**: カバーされている行
- **赤**: カバーされていない行
- **オレンジ**: 部分的にカバーされている行

### **テスト実行時間の分析**

```bash
# 実行時間の詳細表示
python -m pytest tests/ --durations=10

# 遅いテストの特定
python -m pytest tests/ --durations=0
```

## 🚀 CI/CDでのテスト実行

### **GitHub Actionsでの自動実行**

#### **プルリクエスト時**
- 全テストの実行
- カバレッジの測定
- コード品質チェック
- セキュリティチェック

#### **メインブランチへのマージ時**
- 品質ゲートの実行
- カバレッジレポートの生成
- パフォーマンステストの実行

### **ローカルでのCI/CDテスト**

```bash
# CI/CDと同じ環境でのテスト実行
python -m pytest tests/ --cov=qt_theme_studio --cov-report=xml --cov-report=html --cov-report=term-missing

# コード品質チェック（ruff推奨）
ruff check qt_theme_studio/ tests/
ruff format --check qt_theme_studio/ tests/

# フォールバック用（必要に応じて）
python -m black --check --diff qt_theme_studio/ tests/
python -m isort --check-only --diff qt_theme_studio/ tests/
python -m flake8 qt_theme_studio/ tests/
python -m mypy qt_theme_studio/
```

## 📚 参考資料

### **公式ドキュメント**
- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov公式ドキュメント](https://pytest-cov.readthedocs.io/)
- [pytest-benchmark公式ドキュメント](https://pytest-benchmark.readthedocs.io/)

### **ベストプラクティス**
- [Python Testing with pytest](https://pragprog.com/book/bopytest/python-testing-with-pytest)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

### **コミュニティ**
- [pytest GitHub](https://github.com/pytest-dev/pytest)
- [Python Testing Discord](https://discord.gg/python-testing)

## 🎯 次のステップ

### **短期目標**
1. テストカバレッジの向上
2. パフォーマンステストの追加
3. エッジケースのテスト追加

### **中期目標**
1. テスト駆動開発の導入
2. 自動化テストの実装
3. 品質メトリクスの可視化

### **長期目標**
1. 継続的品質向上
2. テスト戦略の最適化
3. 開発チーム全体でのテスト文化の浸透
