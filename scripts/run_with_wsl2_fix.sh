#!/bin/bash
# WSL2環境でのQtダイアログのフォーカス問題を解決するための環境変数設定

echo "=== WSL2環境でのQtダイアログフォーカス問題修正スクリプト ==="
echo "環境変数を設定してQt-Theme-Studioを起動します..."

# WSL2環境でのQtアプリケーションの動作を改善する環境変数
export QT_QPA_PLATFORM=xcb
export DISPLAY=:0
export QT_LOGGING_RULES="qt.qpa.*=false"
export QT_ACCESSIBILITY=0

# フォーカス関連の環境変数
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
export QT_WAYLAND_FORCE_DPI=96

# デバッグ情報を表示
echo "設定された環境変数:"
echo "  QT_QPA_PLATFORM: $QT_QPA_PLATFORM"
echo "  DISPLAY: $DISPLAY"
echo "  QT_LOGGING_RULES: $QT_LOGGING_RULES"
echo "  QT_ACCESSIBILITY: $QT_ACCESSIBILITY"
echo "  QT_WAYLAND_DISABLE_WINDOWDECORATION: $QT_WAYLAND_DISABLE_WINDOWDECORATION"
echo "  QT_WAYLAND_FORCE_DPI: $QT_WAYLAND_FORCE_DPI"
echo ""

# アプリケーションを起動
echo "Qt-Theme-Studioを起動中..."
cd "$(dirname "$0")/.."
python qt_theme_studio_main.py
