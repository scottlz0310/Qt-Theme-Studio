# ダイアログフォーカス問題修正

## 問題の概要

WSL2環境でQt-Theme-Studioを実行した際、ファイルダイアログや色選択ダイアログが開いた時に以下の問題が発生していました：

- ダイアログが開いても操作できない
- 外アプリにフォーカスを移さないと操作できない
- ダイアログが背景に隠れてしまう

## 原因

WSL2環境でのQtアプリケーションでは、以下の要因によりフォーカス問題が発生します：

1. **ウィンドウマネージャーの互換性問題**
2. **ネイティブウィンドウ属性の不足**
3. **フォーカスポリシーの不適切な設定**
4. **ウィンドウモダリティの設定不足**

## 修正内容

### 1. メインウィンドウの設定

```python
# WSL2環境でのフォーカス問題を解決するための設定
self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
self.setWindowModality(Qt.WindowModality.NonModal)
```

### 2. 色選択ダイアログの修正

```python
def choose_color(self, color_type):
    current_color = self.get_current_color(color_type)

    # 色選択ダイアログをインスタンス化して適切な親子関係を設定
    color_dialog = QColorDialog(current_color, self)

    # WSL2環境でのフォーカス問題を解決するための設定
    color_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    color_dialog.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
    color_dialog.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)

    # フォーカス設定を最適化
    color_dialog.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # ダイアログを表示してフォーカスを確実に取得
    if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
        color = color_dialog.currentColor()
        if color.isValid():
            self.set_color_button(color_type, color)
```

### 3. ファイルダイアログの修正

```python
def load_custom_theme_file(self):
    try:
        # ファイルダイアログを設定
        dialog = QFileDialog(self, "テーマファイルを選択")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("JSON Files (*.json)")
        dialog.setViewMode(QFileDialog.ViewMode.List)

        # WSL2環境でのフォーカス問題を解決するための設定
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        dialog.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)

        # フォーカス設定を最適化
        dialog.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # ネイティブダイアログを使用してフォーカス問題を解決
        dialog.setOptions(
            QFileDialog.Option.DontResolveSymlinks |
            QFileDialog.Option.DontConfirmOverwrite |
            QFileDialog.Option.DontUseCustomDirectoryIcons |
            QFileDialog.Option.ReadOnly
        )

        # 同期的にファイルダイアログを表示（フォーカス問題を解決）
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_path = dialog.selectedFiles()[0]
            self._load_theme_from_file(file_path)
```

### 4. プレビューウィンドウの修正

プレビューウィンドウのファイルダイアログにも同様の修正を適用しました。

## 修正のポイント

### 1. WA_NativeWindow属性の設定

```python
dialog.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
```

- ネイティブウィンドウとして扱うことで、WSL2環境での互換性を向上
- ウィンドウマネージャーとの適切な連携を確保

### 2. フォーカスポリシーの最適化

```python
dialog.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
```

- 強力なフォーカスポリシーを設定
- ダイアログが開いた際のフォーカス取得を確実にする

### 3. ウィンドウモダリティの設定

```python
dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
```

- アプリケーションモーダルとして設定
- ダイアログが他のウィンドウの操作をブロック

### 4. フォーカス無効化の防止

```python
dialog.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
```

- ダイアログ表示時のフォーカス無効化を防止
- 確実にフォーカスを取得できるようにする

## テスト方法

修正内容をテストするために、以下のスクリプトを作成しました：

```bash
cd playground
python test_dialog_focus.py
```

このスクリプトでは、以下のダイアログの動作を確認できます：

1. 色選択ダイアログ
2. ファイル選択ダイアログ
3. ファイル保存ダイアログ

## 期待される効果

修正後は以下の改善が期待されます：

- ダイアログが開いた際に即座に操作可能
- 外アプリへのフォーカス移動が不要
- WSL2環境での安定した動作
- ユーザビリティの向上

## 注意事項

- この修正はWSL2環境での動作を最適化しています
- 他の環境（Windows、macOS、Linux）でも動作しますが、主にWSL2環境での問題解決を目的としています
- パフォーマンスへの影響は最小限に抑えられています

## 今後の改善点

- 他のダイアログ（QMessageBox、QInputDialog等）にも同様の修正を適用
- フォーカス管理の一元化
- 環境別の最適化設定の実装
