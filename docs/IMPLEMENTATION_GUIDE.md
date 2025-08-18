# Qt-Theme-Studio 実装ガイド

## 概要

Qt-Theme-Studioの将来機能実装時の技術的ガイドラインと設計パターンを記載します。

## アーキテクチャ原則

### 1. MVCパターンの維持
```
qt_theme_studio/
├── views/          # UI層 - ユーザーインターフェース
├── controllers/    # 制御層 - ビジネスロジック
├── services/       # サービス層 - データ処理
└── adapters/       # アダプター層 - 外部ライブラリ統合
```

### 2. 依存性注入の活用
```python
class NewFeatureController:
    def __init__(self, qt_adapter: QtAdapter, theme_adapter: ThemeAdapter):
        self.qt_adapter = qt_adapter
        self.theme_adapter = theme_adapter
```

### 3. イベント駆動設計
```python
class FeatureWidget(QtWidgets.QWidget):
    feature_changed = QtCore.Signal(dict)  # シグナル定義

    def on_change(self):
        self.feature_changed.emit(self.get_data())  # イベント発火
```

## 新機能実装パターン

### 1. ゼブラパターン機能の実装例

#### ステップ1: サービス層の実装
```python
# qt_theme_studio/services/zebra_service.py
class ZebraPatternService:
    """ゼブラパターン生成サービス"""

    def generate_zebra_colors(self, base_color: str, contrast_level: str) -> Dict[str, str]:
        """WCAG準拠のゼブラパターン色を生成"""
        # 色理論に基づく実装
        pass

    def validate_accessibility(self, colors: Dict[str, str]) -> Dict[str, bool]:
        """アクセシビリティ検証"""
        # WCAG 2.1準拠の検証
        pass
```

#### ステップ2: コントローラー層の実装
```python
# qt_theme_studio/controllers/zebra_controller.py
class ZebraPatternController:
    """ゼブラパターン制御"""

    def __init__(self, zebra_service: ZebraPatternService):
        self.zebra_service = zebra_service
        self.current_pattern = {}

    def update_pattern(self, base_color: str, level: str):
        """パターン更新"""
        self.current_pattern = self.zebra_service.generate_zebra_colors(
            base_color, level
        )
        self.pattern_updated.emit(self.current_pattern)
```

#### ステップ3: UI層の実装
```python
# qt_theme_studio/views/zebra_pattern_editor.py
class ZebraPatternEditor(QtWidgets.QWidget):
    """ゼブラパターンエディター"""

    def __init__(self, controller: ZebraPatternController):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """UI構築"""
        # ウィジェット作成とレイアウト
        pass

    def connect_signals(self):
        """シグナル接続"""
        self.controller.pattern_updated.connect(self.update_preview)
```

### 2. プラグインシステムの実装

#### プラグインインターフェース
```python
# qt_theme_studio/plugins/base_plugin.py
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """プラグイン基底クラス"""

    @abstractmethod
    def get_name(self) -> str:
        """プラグイン名を取得"""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """バージョンを取得"""
        pass

    @abstractmethod
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """プラグイン初期化"""
        pass

    @abstractmethod
    def create_widget(self) -> QtWidgets.QWidget:
        """プラグインウィジェットを作成"""
        pass
```

#### プラグインマネージャー
```python
# qt_theme_studio/services/plugin_manager.py
class PluginManager:
    """プラグイン管理"""

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_dir = Path("plugins")

    def load_plugins(self):
        """プラグイン読み込み"""
        for plugin_file in self.plugin_dir.glob("*.py"):
            plugin = self._load_plugin_from_file(plugin_file)
            if plugin:
                self.plugins[plugin.get_name()] = plugin

    def get_plugin_widgets(self) -> List[QtWidgets.QWidget]:
        """プラグインウィジェット取得"""
        return [plugin.create_widget() for plugin in self.plugins.values()]
```

## コーディング規約

### 1. 命名規則
```python
# クラス名: PascalCase
class ThemeGenerator:
    pass

# 関数・変数名: snake_case
def generate_theme_colors():
    theme_data = {}

# 定数: UPPER_SNAKE_CASE
DEFAULT_THEME_PATH = "themes/default.json"

# プライベート: _leading_underscore
def _internal_method():
    pass
```

### 2. 型ヒント必須
```python
from typing import Dict, List, Optional, Union

def process_theme_data(
    theme_data: Dict[str, Any],
    options: Optional[Dict[str, str]] = None
) -> List[str]:
    """テーマデータを処理"""
    return []
```

### 3. ログ出力規則
```python
# print文禁止 - 必ずloggerを使用
from qt_theme_studio.logger import get_logger

logger = get_logger()

def some_function():
    logger.info("処理を開始しました")  # 日本語ログ
    logger.debug(f"データ: {data}")
    logger.error("エラーが発生しました", exc_info=True)
```

### 4. エラーハンドリング
```python
def safe_operation():
    """安全な操作実行"""
    try:
        # 危険な操作
        result = risky_operation()
        return result
    except SpecificException as e:
        logger.error(f"特定エラー: {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"予期しないエラー: {str(e)}", exc_info=True)
        raise
```

## テスト実装パターン

### 1. 単体テスト
```python
# tests/test_zebra_service.py
import pytest
from qt_theme_studio.services.zebra_service import ZebraPatternService

class TestZebraPatternService:

    def setup_method(self):
        self.service = ZebraPatternService()

    def test_generate_zebra_colors_aa_level(self):
        """AA レベルのゼブラパターン生成テスト"""
        result = self.service.generate_zebra_colors("#ffffff", "AA")

        assert "primary" in result
        assert "alternate" in result
        assert self._check_contrast_ratio(result["primary"], result["alternate"]) >= 4.5

    def _check_contrast_ratio(self, color1: str, color2: str) -> float:
        """コントラスト比チェック"""
        # 実装
        return 4.5
```

### 2. 統合テスト
```python
# tests/test_zebra_integration.py
import pytest
from qt_theme_studio.controllers.zebra_controller import ZebraPatternController
from qt_theme_studio.services.zebra_service import ZebraPatternService

class TestZebraIntegration:

    def setup_method(self):
        self.service = ZebraPatternService()
        self.controller = ZebraPatternController(self.service)

    def test_pattern_update_flow(self):
        """パターン更新フローテスト"""
        # シグナル受信をテスト
        received_data = []
        self.controller.pattern_updated.connect(received_data.append)

        # パターン更新実行
        self.controller.update_pattern("#ffffff", "AA")

        # 結果検証
        assert len(received_data) == 1
        assert "primary" in received_data[0]
```

### 3. GUIテスト
```python
# tests/test_zebra_ui.py
import pytest
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from qt_theme_studio.views.zebra_pattern_editor import ZebraPatternEditor

class TestZebraPatternEditor:

    def test_color_selection(self, qtbot):
        """色選択テスト"""
        editor = ZebraPatternEditor(mock_controller)
        qtbot.addWidget(editor)

        # 色選択ボタンクリック
        color_button = editor.findChild(QPushButton, "color_button")
        qtbot.mouseClick(color_button, Qt.LeftButton)

        # 結果検証
        assert editor.selected_color == "#ffffff"
```

## パフォーマンス最適化

### 1. 遅延読み込み
```python
class LazyThemeLoader:
    """遅延テーマ読み込み"""

    def __init__(self):
        self._themes_cache = {}

    def get_theme(self, theme_id: str) -> Dict[str, Any]:
        """テーマ取得（キャッシュ付き）"""
        if theme_id not in self._themes_cache:
            self._themes_cache[theme_id] = self._load_theme(theme_id)
        return self._themes_cache[theme_id]
```

### 2. 非同期処理
```python
from PySide6.QtCore import QThread, QObject, Signal

class ThemeProcessorWorker(QObject):
    """テーマ処理ワーカー"""

    finished = Signal(dict)
    error = Signal(str)

    def process_theme(self, theme_data: Dict[str, Any]):
        """テーマ処理（別スレッド）"""
        try:
            result = heavy_theme_processing(theme_data)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class ThemeProcessor:
    """テーマ処理管理"""

    def __init__(self):
        self.thread = QThread()
        self.worker = ThemeProcessorWorker()
        self.worker.moveToThread(self.thread)

    def start_processing(self, theme_data: Dict[str, Any]):
        """処理開始"""
        self.worker.process_theme(theme_data)
        self.thread.start()
```

## 国際化対応

### 1. 翻訳可能文字列
```python
from PySide6.QtCore import QCoreApplication

def tr(text: str) -> str:
    """翻訳関数"""
    return QCoreApplication.translate("Context", text)

# 使用例
button_text = tr("テーマを生成")
error_message = tr("ファイルの読み込みに失敗しました")
```

### 2. 翻訳ファイル管理
```
resources/translations/
├── qt_theme_studio_ja.ts    # 日本語
├── qt_theme_studio_en.ts    # 英語
├── qt_theme_studio_zh.ts    # 中国語
└── qt_theme_studio_ko.ts    # 韓国語
```

## デプロイメント

### 1. パッケージング
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="qt-theme-studio",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.0.0",
        "qt-theme-manager",
        "pillow",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "qt-theme-studio=qt_theme_studio.main:main"
        ]
    }
)
```

### 2. CI/CD設定
```yaml
# .github/workflows/build.yml
name: Build and Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -e .[dev]
          pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git
      - name: Run tests
        run: pytest --cov=qt_theme_studio
```

## 貢献ガイドライン

### 1. 開発フロー
1. Issueの作成・確認
2. フィーチャーブランチの作成
3. 実装・テスト
4. プルリクエスト作成
5. コードレビュー
6. マージ

### 2. コミットメッセージ
```
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
style: コードスタイル修正
refactor: リファクタリング
test: テスト追加・修正
chore: その他の変更
```

---

このガイドに従って実装することで、一貫性のある高品質なコードベースを維持できます。
