# Qt-Theme-Studio インストールガイド

## システム要件

### 必須要件
- Python 3.8 以上
- 利用可能なQtフレームワーク（PySide6、PyQt6、またはPyQt5のいずれか）

### 推奨環境
- Python 3.9 以上
- PySide6 6.0 以上（推奨）
- 4GB以上のRAM
- 100MB以上の空きディスク容量

## インストール手順

### 1. 前提条件の確認

Pythonのバージョンを確認：
```bash
python --version
```

### 2. 仮想環境の作成（推奨）

```bash
# 仮想環境の作成
python -m venv qt-theme-studio-env

# 仮想環境の有効化
# Windows:
qt-theme-studio-env\Scripts\activate
# macOS/Linux:
source qt-theme-studio-env/bin/activate
```

### 3. 依存関係のインストール

#### 基本インストール
```bash
# PyPIからのインストール
pip install qt-theme-studio

# または、GitHubから直接インストール
pip install git+https://github.com/your-org/Qt-Theme-Studio.git
```

#### 開発版インストール
```bash
# リポジトリのクローン
git clone https://github.com/your-org/Qt-Theme-Studio.git
cd Qt-Theme-Studio

# 開発用依存関係を含むインストール
pip install -e .[dev]
```

### 4. qt-theme-managerライブラリのインストール

**重要**: qt-theme-managerは必ずGitHubリポジトリから直接インストールしてください。

```bash
pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git
```

### 5. Qtフレームワークのインストール

#### PySide6（推奨）
```bash
pip install PySide6
```

#### PyQt6（代替）
```bash
pip install PyQt6
```

#### PyQt5（レガシーサポート）
```bash
pip install PyQt5
```

## 起動方法

### 基本起動
```bash
python launch_theme_studio.py
```

### コマンドラインオプション
```bash
# デバッグモードで起動
python launch_theme_studio.py --debug

# 特定のテーマファイルを読み込んで起動
python launch_theme_studio.py --theme my_theme.json

# カスタム設定ディレクトリを指定
python launch_theme_studio.py --config-dir ~/.qt-theme-studio

# バージョン情報を表示
python launch_theme_studio.py --version

# ヘルプを表示
python launch_theme_studio.py --help
```

### モジュールとして起動
```bash
python -m qt_theme_studio
```

## トラブルシューティング

### よくある問題

#### 1. Qtフレームワークが見つからない
```
エラー: 利用可能なQtフレームワークが見つかりません
```

**解決方法**:
```bash
# PySide6をインストール
pip install PySide6
```

#### 2. qt-theme-managerが見つからない
```
エラー: qt-theme-managerライブラリが見つかりません
```

**解決方法**:
```bash
# GitHubから直接インストール
pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git
```

#### 3. 日本語ファイル名の文字化け
- システムのロケール設定を確認してください
- UTF-8エンコーディングが有効になっていることを確認してください

#### 4. メモリ不足エラー
- 他のアプリケーションを終了してメモリを解放してください
- 仮想メモリの設定を確認してください

### ログファイルの確認

問題が発生した場合は、ログファイルを確認してください：

- **Windows**: `%APPDATA%\qt-theme-studio\logs\`
- **macOS**: `~/Library/Application Support/qt-theme-studio/logs/`
- **Linux**: `~/.config/qt-theme-studio/logs/`

### サポート

問題が解決しない場合は、以下の情報を含めてIssueを作成してください：

1. オペレーティングシステムとバージョン
2. Pythonのバージョン
3. インストールされているQtフレームワーク
4. エラーメッセージの全文
5. ログファイルの内容

## アンインストール

### パッケージのアンインストール
```bash
pip uninstall qt-theme-studio
```

### 設定ファイルの削除
```bash
# Windows
rmdir /s "%APPDATA%\qt-theme-studio"

# macOS
rm -rf "~/Library/Application Support/qt-theme-studio"

# Linux
rm -rf ~/.config/qt-theme-studio
```

### 仮想環境の削除
```bash
# 仮想環境の無効化
deactivate

# 仮想環境ディレクトリの削除
rm -rf qt-theme-studio-env
```

## 次のステップ

インストールが完了したら、[ユーザーマニュアル](docs/USER_MANUAL.md)を参照して、Qt-Theme-Studioの使用方法を学習してください。
