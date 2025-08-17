#!/usr/bin/env python3
"""
Qt-Theme-Studio メインアプリケーション
クリーンなアーキテクチャによる高度なテーマ管理・生成・編集
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """メイン関数"""
    try:
        print("=== Qt-Theme-Studio メインアプリケーション起動 ===")

        # PySide6のインポート
        from PySide6.QtWidgets import QApplication
        print("✓ PySide6インポート成功")

        # アプリケーション作成
        app = QApplication(sys.argv)
        app.setApplicationName("Qt-Theme-Studio")
        app.setApplicationVersion("1.0.0")
        print("✓ QApplication作成完了")

        # メインウィンドウのインポートと作成
        from qt_theme_studio.views.main_window import QtThemeStudioMainWindow

        main_window = QtThemeStudioMainWindow()
        main_window.show()
        print("✓ メインウィンドウ表示完了")

        print("\n🚀 アプリケーション起動完了！")
        print("\n=== 機能説明 ===")
        print("🎨 ワンクリックテーマ生成: 背景色を選ぶだけで完璧なテーマを自動生成")
        print("⚡ プリセットテーマ: 人気のカラーパレットをワンクリックで適用")
        print("🔧 詳細調整: 明度・彩度の微調整で理想のテーマを作成")
        print("💾 テーマ管理: 作成したテーマの保存・エクスポート・共有")
        print("👁️ リアルタイムプレビュー: 変更が即座に反映されるプレビュー機能")

        return app.exec()

    except Exception as e:
        print(f"❌ 致命的なエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
