#!/bin/bash
# WSLg環境でQt-Theme-Studioを起動するスクリプト

echo "=== WSLg環境でのQt-Theme-Studio起動 ==="
echo "VcXsrvの設定を無効化してWSLgに切り替えます..."

# VcXsrvの設定をクリア
unset DISPLAY

# WSLg環境変数を設定
export WAYLAND_DISPLAY=wayland-0
export XDG_SESSION_TYPE=wayland

# Qtの設定をWSLg用に最適化
export QT_QPA_PLATFORM=wayland
export QT_WAYLAND_DISABLE_WINDOWDECORATION=0
export QT_WAYLAND_FORCE_DPI=96

# デバッグ情報を表示
echo "設定された環境変数:"
echo "  WAYLAND_DISPLAY: $WAYLAND_DISPLAY"
echo "  XDG_SESSION_TYPE: $XDG_SESSION_TYPE"
echo "  QT_QPA_PLATFORM: $QT_QPA_PLATFORM"
echo "  DISPLAY: $DISPLAY (VcXsrv無効化)"
echo ""

# アプリケーションを起動
echo "Qt-Theme-StudioをWSLg環境で起動中..."
cd "$(dirname "$0")/.."
python qt_theme_studio_main.py
