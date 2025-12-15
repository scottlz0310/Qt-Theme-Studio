# Qt-Theme-Studio インストールガイド

## システム要件

- Python 3.8 以上
- Qt フレームワーク (PySide6, PyQt6, または PyQt5)
- 対応OS: Windows, macOS, Linux

## インストール方法

### 1. PyPI からのインストール（推奨）

```bash
uv add qt-theme-studio
```

### 2. GitHubからの開発版インストール

```bash
uv tool install git+https://github.com/your-username/Qt-Theme-Studio.git
```

### 3. ソースからのインストール

```bash
git clone https://github.com/your-username/Qt-Theme-Studio.git
cd Qt-Theme-Studio
uv add -e .
```

## 依存関係のインストール

### qt-theme-manager（必須）

```bash
uv add git+https://github.com/scottlz0310/Qt-Theme-Manager.git
```

### 開発用依存関係（開発者向け）

```bash
uv sync --dev
```

## 動作確認

インストール後、以下のコマンドで動作確認できます：

```bash
# バージョン確認
uv run qt_theme_studio --version

# ヘルプ表示
uv run qt_theme_studio --help

# GUI起動
uv run qt_theme_studio
```

## トラブルシューティング

### Qt フレームワークが見つからない場合

```bash
# PySide6をインストール
uv add PySide6

# または PyQt6
uv add PyQt6
# または PyQt5
uv add PyQt5
```

### 権限エラーが発生する場合

```bash
# ユーザーディレクトリにインストール
uv add --user qt-theme-studio
```

### 仮想環境での使用（推奨）

```bash
# 仮想環境作成
uv venv

# 仮想環境有効化
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# インストール
uv add qt-theme-studio
```

## アンインストール

```bash
pip uninstall qt-theme-studio
```

## サポート

問題が発生した場合は、[GitHub Issues](https://github.com/your-username/Qt-Theme-Studio/issues) でお知らせください。
