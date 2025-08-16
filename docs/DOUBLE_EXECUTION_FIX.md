# 2重動作問題の修正

## 問題の概要

テーマファイルを開く時や保存操作で、メソッドが2重実行される問題がありました。これは以下の原因によるものでした：

1. **メソッドの重複定義**: 同じ機能のメソッドが複数箇所で定義されていた
2. **メニューアクションの重複接続**: 同じアクションが複数のメソッドに接続されていた

## 発見された重複

### 1. 新規テーマ作成

**重複していたメソッド**:
- `_on_new_theme()` - 正しいメソッド
- `_new_theme()` - 重複メソッド

**重複していた接続**:
```python
# _connect_menu_actions() で接続
self.actions['new_theme'].triggered.connect(self._on_new_theme)

# _connect_theme_actions() でも接続（重複）
self.actions['new_theme'].triggered.connect(self._new_theme)
```

### 2. テーマファイルを開く

**重複していたメソッド**:
- `_on_open_theme()` - 正しいメソッド
- `_open_theme()` - 重複メソッド

**重複していた接続**:
```python
# _connect_menu_actions() で接続
self.actions['open_theme'].triggered.connect(self._on_open_theme)

# _connect_theme_actions() でも接続（重複）
self.actions['open_theme'].triggered.connect(self._open_theme)
```

### 3. テーマ保存

**重複していたメソッド**:
- `_on_save_theme()` - 正しいメソッド
- `_save_theme()` - 重複メソッド
- `_on_save_as_theme()` - 正しいメソッド
- `_save_theme_as()` - 重複メソッド

**重複していた接続**:
```python
# _connect_menu_actions() で接続
self.actions['save_theme'].triggered.connect(self._on_save_theme)

# _connect_theme_actions() でも接続（重複）
self.actions['save_theme'].triggered.connect(self._save_theme)
```

## 修正内容

### 1. 重複メソッドの削除

**修正ファイル**: `qt_theme_studio/views/main_window.py`

以下の重複メソッドを削除しました：
- `_new_theme()` → `_on_new_theme()` のみ残す
- `_open_theme()` → `_on_open_theme()` のみ残す
- `_save_theme()` → `_on_save_theme()` のみ残す
- `_save_theme_as()` → `_on_save_as_theme()` のみ残す

### 2. 重複したメニューアクション接続の削除

**修正前**:
```python
def _connect_theme_actions(self) -> None:
    # 新規テーマ作成
    if 'new_theme' in self.actions:
        self.actions['new_theme'].triggered.connect(self._new_theme)
    
    # テーマを開く
    if 'open_theme' in self.actions:
        self.actions['open_theme'].triggered.connect(self._open_theme)
    
    # テーマを保存
    if 'save_theme' in self.actions:
        self.actions['save_theme'].triggered.connect(self._save_theme)
```

**修正後**:
```python
def _connect_theme_actions(self) -> None:
    # 新規テーマ作成アクションは_connect_menu_actions()で既に接続済みなのでここでは接続しない
    
    # 開くアクションは_connect_menu_actions()で既に接続済みなのでここでは接続しない
    
    # 保存アクションは_connect_menu_actions()で既に接続済みなのでここでは接続しない
```

### 3. 正しいメニューアクション接続の維持

**`_connect_menu_actions()`** で以下の接続のみを維持：
```python
def _connect_menu_actions(self) -> None:
    # ファイルメニューのアクション接続
    if 'new_theme' in self.actions:
        self.actions['new_theme'].triggered.connect(self._on_new_theme)
    
    if 'open_theme' in self.actions:
        self.actions['open_theme'].triggered.connect(self._on_open_theme)
    
    if 'save_theme' in self.actions:
        self.actions['save_theme'].triggered.connect(self._on_save_theme)
    
    if 'save_as_theme' in self.actions:
        self.actions['save_as_theme'].triggered.connect(self._on_save_as_theme)
```

## 修正結果

### 修正前の問題
1. **新規テーマ作成**: ボタンクリック → `_on_new_theme()` + `_new_theme()` の2回実行
2. **テーマファイルを開く**: ボタンクリック → `_on_open_theme()` + `_open_theme()` の2回実行
3. **テーマ保存**: ボタンクリック → `_on_save_theme()` + `_save_theme()` の2回実行

### 修正後の動作
1. **新規テーマ作成**: ボタンクリック → `_on_new_theme()` の1回実行
2. **テーマファイルを開く**: ボタンクリック → `_on_open_theme()` の1回実行
3. **テーマ保存**: ボタンクリック → `_on_save_theme()` の1回実行

## 検証結果

### メソッド存在確認
```
✅ _on_new_theme のみ存在（重複なし）
✅ _on_open_theme のみ存在（重複なし）
✅ _on_save_theme のみ存在（重複なし）
✅ _on_save_as_theme のみ存在（重複なし）
```

### アクション存在確認
```
✅ アクション 'new_theme' が存在します
✅ アクション 'open_theme' が存在します
✅ アクション 'save_theme' が存在します
✅ アクション 'save_as_theme' が存在します
```

## 影響範囲

### 修正されたファイル
- **qt_theme_studio/views/main_window.py**
  - 重複メソッドの削除
  - 重複アクション接続の削除

### ユーザーへの影響
- **正の影響**: 
  - ボタンクリック時の2重実行が解消
  - 未保存確認ダイアログが2回表示される問題が解消
  - ファイルダイアログが2回開く問題が解消
  - パフォーマンスの向上

- **負の影響**: なし

## 今後の予防策

### 1. コードレビューでのチェック項目
- メソッド名の重複確認
- メニューアクション接続の重複確認
- 同じ機能の実装が複数箇所にないかの確認

### 2. 自動テストの追加
- メニューアクションの実行回数テスト
- メソッド呼び出し回数の監視
- 重複メソッド検出テスト

### 3. 命名規則の統一
- メニューアクション用メソッド: `_on_<action_name>()`
- 内部処理用メソッド: `_<function_name>()`
- 明確な役割分担による重複防止

## まとめ

この修正により、以下の問題が完全に解決されました：

- ✅ メニューアクションの2重実行問題
- ✅ 未保存確認ダイアログの2重表示問題
- ✅ ファイルダイアログの2重表示問題
- ✅ 不要なメソッド重複の削除
- ✅ コードの保守性向上

ユーザーは正常に1回だけの操作でテーマの新規作成、読み込み、保存ができるようになりました。