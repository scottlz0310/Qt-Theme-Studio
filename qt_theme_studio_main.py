#!/usr/bin/env python3
"""
Qt-Theme-Studio メインアプリケーション
クリーンなアーキテクチャによる高度なテーマ管理・生成・編集
"""

import os
import sys
from pathlib import Path

# WSL2環境でのQtダイアログのフォーカス問題を解決するための環境変数設定
def setup_wsl2_environment():
    """WSL2環境でのQtアプリケーションの動作を改善する環境変数を設定"""
    
    # WSLg環境の検出
    wayland_available = os.environ.get('WAYLAND_DISPLAY') and os.path.exists('/dev/wayland-0')
    vcxsrv_configured = os.environ.get('DISPLAY') and ':' in os.environ.get('DISPLAY', '')
    
    if wayland_available and not vcxsrv_configured:
        # WSLg環境: Waylandプラットフォームを使用
        print("=== WSLg環境を検出: Waylandプラットフォームを使用 ===")
        os.environ.setdefault('QT_QPA_PLATFORM', 'wayland')
        os.environ.setdefault('XDG_SESSION_TYPE', 'wayland')
        os.environ.setdefault('WAYLAND_DISPLAY', 'wayland-0')
        
        # Wayland用の最適化設定
        os.environ.setdefault('QT_WAYLAND_DISABLE_WINDOWDECORATION', '0')
        os.environ.setdefault('QT_WAYLAND_FORCE_DPI', '96')
        
        # VcXsrvの設定をクリア
        if 'DISPLAY' in os.environ:
            del os.environ['DISPLAY']
            
    else:
        # VcXsrv環境: X11プラットフォームを使用
        print("=== VcXsrv環境を検出: X11プラットフォームを使用 ===")
        os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')
        os.environ.setdefault('DISPLAY', ':0')
        
        # X11用の最適化設定
        os.environ.setdefault('QT_LOGGING_RULES', 'qt.qpa.*=false')
        os.environ.setdefault('QT_ACCESSIBILITY', '0')
    
    # 共通設定
    print(f"QT_QPA_PLATFORM: {os.environ.get('QT_QPA_PLATFORM')}")
    print(f"XDG_SESSION_TYPE: {os.environ.get('XDG_SESSION_TYPE', 'N/A')}")
    print(f"WAYLAND_DISPLAY: {os.environ.get('WAYLAND_DISPLAY', 'N/A')}")
    print(f"DISPLAY: {os.environ.get('DISPLAY', 'N/A')}")
    print("===================")

# 環境変数を設定
setup_wsl2_environment()

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
