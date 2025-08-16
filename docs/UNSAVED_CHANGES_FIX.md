# 未保存変更機能の修正

## 問題の概要

テーマファイルを開く時の未保存アラートや保存操作でメソッドが複数回実行される問題がありました。これは以下の原因によるものでした：

1. **メソッドの重複定義**: 保存関連のメソッドが複数箇所で定義されていた
2. **メニューアクションの重複接続**: 同じアクションが複数回接続されていた
3. **未保存状態管理の不備**: テーマ変更時に未保存状態が適切に設定されていなかった

## 修正内容

### 1. 重複したメソッド定義の削除

**修正ファイル**: `qt_theme_studio/views/main_window.py`

- 重複していた `_save_theme()`, `_save_theme_as()`, `_save_theme_to_file()` メソッドを削除
- 正しいメソッド（`_on_save_theme()`, `_on_save_as_theme()`, `_save_theme_to_file()`）のみを残す

### 2. メニューアクション接続の重複修正

**修正前**:
```python
# _connect_theme_actions() で接続
if 'save_theme' in self.actions:
    self.actions['save_theme'].triggered.connect(self._save_theme)

# _connect_menu_actions() でも接続（重複）
if 'save_theme' in self.actions:
    self.actions['save_theme'].triggered.connect(self._on_save_theme)
```

**修正後**:
```python
# _connect_menu_actions() でのみ接続
if 'save_theme' in self.actions:
    self.actions['save_theme'].triggered.connect(self._on_save_theme)
```

### 3. 未保存状態管理の改善

#### 3.1 テーマ変更時の未保存状態設定

**修正ファイル**: `qt_theme_studio/views/main_window.py`

```python
def set_theme_data(self, theme_data: Dict[str, Any]) -> None:
    # ... 既存の処理 ...
    
    # テーマが変更されたので未保存状態に設定
    self._set_theme_saved_state(False)
```

#### 3.2 テーマ読み込み時の保存済み状態設定

```python
def _apply_loaded_theme(self, theme_data: dict, file_path: str) -> None:
    # ... 既存の処理 ...
    
    # テーマを読み込んだので保存済み状態に設定
    self._set_theme_saved_state(True)
```

#### 3.3 保存時の保存済み状態設定

```python
def _save_theme_to_file(self, file_path: str) -> None:
    # ... 保存処理 ...
    
    # テーマを保存したので保存済み状態に設定
    self._set_theme_saved_state(True)
```

#### 3.4 テーマエディターでの変更時の未保存状態設定

**修正ファイル**: `qt_theme_studio/views/theme_editor.py`

```python
def _on_color_changed(self, color: str, style: str) -> None:
    # ... 既存の処理 ...
    
    # テーマが変更されたので未保存状態に設定
    if hasattr(main_window, '_set_theme_saved_state'):
        main_window._set_theme_saved_state(False)
```

### 4. クローズイベントハンドラーの修正

**修正前**:
```python
self._save_theme()  # 存在しないメソッド
```

**修正後**:
```python
self._on_save_theme()  # 正しいメソッド
```

## 実装した機能

### 1. 未保存変更の検出

- テーマデータが変更されると自動的に未保存状態になる
- ウィンドウタイトルに `*` マークが表示される
- 保存ボタンが有効になる

### 2. 未保存変更の確認ダイアログ

以下の操作時に未保存変更がある場合、確認ダイアログが表示される：

- **新規テーマ作成時**
- **テーマファイル読み込み時**
- **アプリケーション終了時**

### 3. 保存状態の管理

- **保存済み状態**: ファイル読み込み時、保存時
- **未保存状態**: テーマ変更時（色変更、プロパティ変更など）

## テスト結果

### 基本機能テスト

**テストファイル**: `test_unsaved_changes.py`

```
=== テスト結果 ===
✅ メインウィンドウを作成しました
✅ テーマ変更時に未保存状態が正しく設定されました
✅ 保存後に未保存状態が正しくクリアされました
✅ 未保存時にウィンドウタイトルに*マークが表示されました
🎉 テストが成功しました！
```

### 動作確認項目

1. **テーマ変更時**:
   - ウィンドウタイトルに `*` が表示される
   - 保存ボタンが有効になる

2. **新規テーマ作成時**:
   - 未保存変更がある場合、確認ダイアログが表示される
   - 「はい」を選択すると新規テーマが作成される
   - 「いいえ」を選択すると操作がキャンセルされる

3. **テーマファイル読み込み時**:
   - 未保存変更がある場合、確認ダイアログが表示される
   - 読み込み後は保存済み状態になる

4. **保存時**:
   - 保存後は保存済み状態になる
   - ウィンドウタイトルから `*` が消える

5. **アプリケーション終了時**:
   - 未保存変更がある場合、確認ダイアログが表示される
   - 「保存」「破棄」「キャンセル」の選択肢が提供される

## 修正されたファイル

1. **qt_theme_studio/views/main_window.py**
   - 重複メソッド定義の削除
   - メニューアクション接続の修正
   - 未保存状態管理の改善

2. **qt_theme_studio/views/theme_editor.py**
   - 色変更時の未保存状態設定

3. **test_unsaved_changes.py** (新規作成)
   - 未保存変更機能のテスト

## 今後の改善点

1. **Undo/Redo機能との統合**: 操作履歴と未保存状態の連携
2. **自動保存機能**: 定期的な自動保存機能の追加
3. **変更内容の詳細表示**: どの部分が変更されたかの詳細表示
4. **保存前のプレビュー**: 保存前に変更内容を確認できる機能

## まとめ

この修正により、以下の問題が解決されました：

- ✅ メソッドの重複実行問題
- ✅ 未保存変更の適切な検出
- ✅ ユーザーフレンドリーな確認ダイアログ
- ✅ 一貫した保存状態管理

ユーザーは安心してテーマ編集作業を行い、未保存の変更を失うリスクなく作業できるようになりました。