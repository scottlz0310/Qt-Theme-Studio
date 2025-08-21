#!/usr/bin/env python3
"""
Qt-Theme-Studio メインアプリケーション
クリーンなアーキテクチャによる高度なテーマ管理・生成・編集
"""

import os
import sys


# WSL2環境でのQtダイアログのフォーカス問題を解決するための環境変数設定
def detect_display_environment():
    """ディスプレイ環境を正確に検出して適切な設定を適用"""
    
    # WSL環境の検出
    is_wsl = os.path.exists("/proc/version") and "microsoft" in open("/proc/version").read().lower()
    
    # 環境変数の確認
    wayland_display = os.environ.get("WAYLAND_DISPLAY")
    x11_display = os.environ.get("DISPLAY")
    
    # ファイルシステムの確認
    wayland_socket = os.path.exists("/run/user/1000/wayland-0") or os.path.exists("/tmp/.X11-unix/X0")
    x11_socket = os.path.exists("/tmp/.X11-unix/X0")
    
    print(f"=== 環境検出 ===")
    print(f"WSL環境: {is_wsl}")
    print(f"WAYLAND_DISPLAY: {wayland_display}")
    print(f"DISPLAY: {x11_display}")
    print(f"Waylandソケット: {wayland_socket}")
    print(f"X11ソケット: {x11_socket}")
    
    # WSLg (Wayland) の優先判定
    if is_wsl and wayland_display and wayland_socket:
        print("=== WSLg (Wayland) 環境を選択 ===")
        os.environ["QT_QPA_PLATFORM"] = "wayland"
        os.environ["XDG_SESSION_TYPE"] = "wayland"
        os.environ["WAYLAND_DISPLAY"] = wayland_display
        
        # Wayland最適化
        os.environ["QT_WAYLAND_DISABLE_WINDOWDECORATION"] = "0"
        os.environ["QT_WAYLAND_FORCE_DPI"] = "96"
        
        return "wslg"
    
    # VcXsrv (X11) の判定
    elif is_wsl and x11_display and x11_socket:
        print("=== VcXsrv (X11) 環境を選択 ===")
        os.environ["QT_QPA_PLATFORM"] = "xcb"
        os.environ["DISPLAY"] = x11_display
        
        # X11最適化
        os.environ["QT_LOGGING_RULES"] = "qt.qpa.*=false"
        os.environ["QT_ACCESSIBILITY"] = "0"
        
        return "vcxsrv"
    
    # ネイティブLinux環境
    elif not is_wsl:
        print("=== ネイティブLinux環境を検出 ===")
        # デフォルトのプラットフォームを使用
        return "native"
    
    # フォールバック: X11を使用
    else:
        print("=== フォールバック: X11を使用 ===")
        os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
        os.environ.setdefault("DISPLAY", ":0")
        
        return "fallback"


# 環境検出と設定
env_type = detect_display_environment()
print(f"検出された環境: {env_type}")
print(f"QT_QPA_PLATFORM: {os.environ.get('QT_QPA_PLATFORM', '未設定')}")
print(f"DISPLAY: {os.environ.get('DISPLAY', '未設定')}")
print("===================")

# PySide6のインポートを試行
try:
    from PySide6.QtWidgets import QApplication

    print("✓ PySide6インポート成功")
except ImportError as e:
    print(f"❌ PySide6インポート失敗: {e}")
    print("PySide6をインストールしてください: pip install PySide6")
    sys.exit(1)

# アプリケーション作成
try:
    app = QApplication(sys.argv)
    print("✓ QApplication作成完了")
except Exception as e:
    print(f"❌ QApplication作成失敗: {e}")
    sys.exit(1)

# メインウィンドウのインポートと作成
try:
    from qt_theme_studio.views.main_window import QtThemeStudioMainWindow

    # メインウィンドウを作成
    main_window = QtThemeStudioMainWindow()
    main_window.show()
    print("✓ メインウィンドウ表示完了")

    print("\n🚀 アプリケーション起動完了!")
    print("\n=== 機能説明 ===")
    print("🎨 ワンクリックテーマ生成: 背景色を選ぶだけで完璧なテーマを自動生成")
    print("⚡ プリセットテーマ: 人気のカラーパレットをワンクリックで適用")
    print("🔧 詳細調整: 明度・彩度の微調整で理想のテーマを作成")
    print("💾 テーマ管理: 作成したテーマの保存・エクスポート・共有")
    print("👁️ リアルタイムプレビュー: 変更が即座に反映されるプレビュー機能")

    # アプリケーションを実行
    sys.exit(app.exec())

except Exception as e:
    print(f"❌ メインウィンドウ作成失敗: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
