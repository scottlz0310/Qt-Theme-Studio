# ライブプレビューのテーマ追随強化

## 問題の概要

従来のライブプレビューでは、テーマの適用が不完全で、以下の問題が発生していました：

- 親ウィジェット全体にのみスタイルシートが適用される
- 個別のウィジェット（ボタン、入力フィールド、リスト等）にテーマが反映されない
- 一部のウィジェットがテーマに追随しない
- スタイルシートの適用漏れによる視覚的な不整合

## 解決策

### 1. 個別ウィジェットへのテーマ適用

各ウィジェットタイプ別に専用のスタイルシートを生成し、個別に適用するように改善しました：

```python
def _apply_theme_to_individual_widgets(self, theme_data: dict[str, Any]) -> None:
    """個別のウィジェットにテーマを適用"""
    # 各ウィジェットタイプ別のスタイルシートを生成
    button_stylesheet = self._generate_button_stylesheet(colors)
    input_stylesheet = self._generate_input_stylesheet(colors)
    selection_stylesheet = self._generate_selection_stylesheet(colors)
    display_stylesheet = self._generate_display_stylesheet(colors)
    container_stylesheet = self._generate_container_stylesheet(colors)
    progress_stylesheet = self._generate_progress_stylesheet(colors)

    # 各ウィジェットに個別のスタイルシートを適用
    for widget_name, widget in self.widgets.items():
        if "button" in widget_name.lower():
            widget.setStyleSheet(button_stylesheet)
        elif any(keyword in widget_name.lower() for keyword in ["input", "edit", "line"]):
            widget.setStyleSheet(input_stylesheet)
        # ... 他のウィジェットタイプ
```

### 2. ウィジェットタイプ別スタイルシート生成

#### ボタン用スタイルシート
```python
def _generate_button_stylesheet(self, colors: dict[str, str]) -> str:
    """ボタン用のスタイルシートを生成"""
    primary = colors.get("primary", "#007acc")
    button_bg = colors.get("button_background", primary)
    button_text = colors.get("button_text", "#ffffff")
    button_hover = colors.get("button_hover", colors.get("accent", primary))

    return f"""
    QPushButton {{
        background-color: {button_bg};
        color: {button_text};
        border: 2px solid {button_bg};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: {button_hover};
        border-color: {button_hover};
    }}
    """
```

#### 入力ウィジェット用スタイルシート
```python
def _generate_input_stylesheet(self, colors: dict[str, str]) -> str:
    """入力ウィジェット用のスタイルシートを生成"""
    input_bg = colors.get("input_background", colors.get("background", "#ffffff"))
    input_text = colors.get("input_text", colors.get("text", "#333333"))
    input_border = colors.get("input_border", colors.get("primary", "#007acc"))

    return f"""
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {input_bg};
        color: {input_text};
        border: 2px solid {input_border};
        border-radius: 4px;
        padding: 6px;
    }}
    """
```

### 3. テーマデータの拡張

テーマジェネレータを拡張して、より詳細な色設定をサポート：

```python
"colors": {
    "primary": "#007acc",
    "accent": "#ff6b6b",
    "background": "#ffffff",
    "text": "#333333",
    # ボタン関連の色
    "button_background": "#007acc",
    "button_text": "#ffffff",
    "button_hover": "#005a9e",
    "button_pressed": "#004080",
    # 入力ウィジェット関連の色
    "input_background": "#f8f9fa",
    "input_text": "#333333",
    "input_border": "#007acc",
    "focus_border": "#ff6b6b",
    # スクロールバー関連の色
    "scrollbar_background": "#f8f9fa",
    "scrollbar_handle": "#007acc",
    "scrollbar_handle_hover": "#ff6b6b",
    # プログレス関連の色
    "progress_background": "#f8f9fa",
    "progress_fill": "#007acc",
    # 境界線関連の色
    "border": "#dee2e6",
    # 無効状態の色
    "disabled_background": "#e9ecef",
    "disabled_text": "#6c757d",
    "disabled_border": "#dee2e6"
}
```

### 4. サポートするウィジェットタイプ

以下のウィジェットタイプに対して個別のテーマ適用を実装：

- **ボタン系**: QPushButton
- **入力系**: QLineEdit, QTextEdit, QPlainTextEdit
- **選択系**: QComboBox, QListWidget, QTableWidget
- **表示系**: QLabel, QGroupBox
- **コンテナ系**: QFrame, QWidget, QScrollArea
- **プログレス系**: QProgressBar, QSlider

## 実装の特徴

### 1. 段階的なテーマ適用
1. 親ウィジェット全体にスタイルシートを適用
2. 個別のウィジェットにタイプ別スタイルシートを適用
3. パレットを直接操作してフォールバック
4. 強制再描画で確実に反映

### 2. エラーハンドリング
各ウィジェットへのスタイル適用でエラーが発生しても、他のウィジェットへの適用を継続：

```python
try:
    widget.setStyleSheet(stylesheet)
except Exception as e:
    self.logger.debug(f"ウィジェット {widget_name} へのスタイル適用エラー: {e}")
```

### 3. フォールバック機能
スタイルシートが効かない場合の代替手段として、パレットの直接操作と強制再描画を実装

## テスト方法

### 1. テストスクリプトの実行
```bash
cd playground
python test_theme_preview.py
```

### 2. テスト内容
- ダークテーマ、ライトテーマ、カラフルテーマの切り替え
- 各ウィジェットタイプへのテーマ適用確認
- スタイルシートの適用漏れチェック

### 3. 確認ポイント
- ✅ ボタンの色とホバー効果
- ✅ 入力フィールドの背景色とボーダー
- ✅ コンボボックスのドロップダウン表示
- ✅ スクロールバーの色とスタイル
- ✅ プログレスバーの色とスタイル
- ✅ グループボックスの境界線とタイトル

## 期待される効果

### 1. 視覚的な一貫性
- すべてのウィジェットがテーマに完全に追随
- 色の調和と統一感の向上
- プロフェッショナルな外観の実現

### 2. ユーザビリティの向上
- テーマ切り替え時の即座な反映
- 直感的な操作感の提供
- アクセシビリティの向上

### 3. 保守性の向上
- ウィジェットタイプ別の明確な分離
- テーマデータの構造化
- 拡張性の確保

## 今後の改善点

### 1. カスタムウィジェットのサポート
- ユーザー定義ウィジェットへのテーマ適用
- プラグインアーキテクチャの実装

### 2. アニメーション効果
- テーマ切り替え時のスムーズなトランジション
- ホバー・フォーカス時の動的効果

### 3. テーマプリセットの拡充
- より多くのカラーパレット
- 業界別のテーマテンプレート

## 技術的な注意点

### 1. パフォーマンス
- 大量のウィジェットに対する最適化
- スタイルシートのキャッシュ機能

### 2. 互換性
- 異なるQtバージョンでの動作確認
- プラットフォーム別の最適化

### 3. メモリ管理
- スタイルシートオブジェクトの適切な解放
- 循環参照の防止

この実装により、ライブプレビューのテーマ追随が完全になり、ユーザーはすべてのウィジェットで一貫したテーマ体験を得ることができます。
