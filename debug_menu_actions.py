#!/usr/bin/env python3
"""
メニューアクション接続デバッグ

このスクリプトは、メニューアクションが正しく接続されているかをデバッグします。
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_menu_actions():
    """メニューアクション接続をデバッグ"""
    try:
        print("メニューアクション接続デバッグを開始します...")
        
        # メインアプリケーションをインポート
        from qt_theme_studio.main import ThemeStudioApplication
        
        # アプリケーションインスタンスを作成（ログを抑制）
        import logging
        logging.getLogger().setLevel(logging.ERROR)
        
        app = ThemeStudioApplication()
        app.initialize()
        main_window = app.create_main_window()
        
        print("✓ アプリケーションの初期化完了")
        
        # アクションの存在確認
        print("\n=== アクション存在確認 ===")
        expected_actions = ['new_theme', 'open_theme', 'save_theme', 'save_as_theme']
        
        for action_name in expected_actions:
            if action_name in main_window.actions:
                action = main_window.actions[action_name]
                print(f"✓ {action_name}: 存在 - テキスト: '{action.text()}'")
                
                # シグナル接続確認
                receivers = action.receivers(action.triggered)
                print(f"  - 接続されたレシーバー数: {receivers}")
                
                if receivers > 0:
                    print(f"  - ✓ シグナルが接続されています")
                else:
                    print(f"  - ✗ シグナルが接続されていません")
            else:
                print(f"✗ {action_name}: 存在しません")
        
        # メニューバーの確認
        print("\n=== メニューバー確認 ===")
        if hasattr(main_window, 'menu_bar') and main_window.menu_bar:
            print("✓ メニューバーが存在します")
            
            # ファイルメニューの確認
            menus = main_window.menu_bar.findChildren(main_window.QtWidgets.QMenu)
            print(f"✓ メニュー数: {len(menus)}")
            
            for menu in menus:
                print(f"  - メニュー: '{menu.title()}'")
                actions = menu.actions()
                print(f"    アクション数: {len(actions)}")
                for action in actions:
                    if not action.isSeparator():
                        print(f"    - '{action.text()}'")
        else:
            print("✗ メニューバーが存在しません")
        
        # 手動でアクションをトリガーしてテスト
        print("\n=== 手動アクショントリガーテスト ===")
        if 'new_theme' in main_window.actions:
            print("新規テーマアクションを手動でトリガーします...")
            main_window.actions['new_theme'].trigger()
            print("✓ 新規テーマアクションのトリガーが完了しました")
            
            # テーマデータを確認
            theme_data = main_window.get_current_theme_data()
            print(f"✓ 現在のテーマ: {theme_data.get('name', 'Unknown')}")
        
        print("\n✓ メニューアクション接続デバッグが完了しました")
        
        return True
        
    except Exception as e:
        print(f"✗ メニューアクション接続デバッグに失敗しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_menu_actions()
    sys.exit(0 if success else 1)