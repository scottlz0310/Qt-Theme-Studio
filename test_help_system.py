#!/usr/bin/env python3
"""
ヘルプシステムのテストスクリプト

Qt-Theme-Studioのヘルプダイアログとユーザーマニュアルの動作をテストします。
"""

import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qt_theme_studio.adapters.qt_adapter import QtAdapter
from qt_theme_studio.views.dialogs.help_dialog import HelpDialog


def test_help_dialog():
    """ヘルプダイアログのテスト"""
    print("ヘルプダイアログのテストを開始します...")
    
    try:
        # Qt アダプターを初期化
        qt_adapter = QtAdapter()
        qt_modules = qt_adapter.get_qt_modules()
        
        # QApplication を作成
        app = qt_modules['QtWidgets'].QApplication(sys.argv)
        
        # ヘルプダイアログを作成・表示
        help_dialog = HelpDialog()
        help_dialog.show()
        
        print("ヘルプダイアログが正常に表示されました。")
        print("ダイアログを閉じるとテストが終了します。")
        
        # イベントループを開始
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_user_manual():
    """ユーザーマニュアルファイルの存在確認"""
    print("ユーザーマニュアルファイルの確認を開始します...")
    
    manual_path = os.path.join(
        os.path.dirname(__file__),
        'qt_theme_studio', 'resources', 'docs', 'user_manual.html'
    )
    
    if os.path.exists(manual_path):
        print(f"ユーザーマニュアルファイルが見つかりました: {manual_path}")
        
        # ファイルサイズを確認
        file_size = os.path.getsize(manual_path)
        print(f"ファイルサイズ: {file_size:,} bytes")
        
        # HTMLファイルの基本構造を確認
        try:
            with open(manual_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if '<html' in content and '</html>' in content:
                print("HTMLファイルの基本構造が正しいことを確認しました。")
            else:
                print("警告: HTMLファイルの構造に問題がある可能性があります。")
                
            if 'Qt-Theme-Studio' in content:
                print("コンテンツにアプリケーション名が含まれていることを確認しました。")
            else:
                print("警告: コンテンツにアプリケーション名が見つかりません。")
                
        except Exception as e:
            print(f"ファイル読み込みエラー: {str(e)}")
            return False
            
    else:
        print(f"エラー: ユーザーマニュアルファイルが見つかりません: {manual_path}")
        return False
    
    return True


def main():
    """メインテスト関数"""
    print("=== Qt-Theme-Studio ヘルプシステムテスト ===")
    print()
    
    # ユーザーマニュアルファイルのテスト
    manual_test_result = test_user_manual()
    print()
    
    # ヘルプダイアログのテスト
    if manual_test_result:
        print("ユーザーマニュアルテストが成功しました。")
        print("次にヘルプダイアログのテストを実行します。")
        print()
        
        dialog_test_result = test_help_dialog()
        
        if dialog_test_result:
            print("すべてのテストが成功しました！")
        else:
            print("ヘルプダイアログのテストが失敗しました。")
    else:
        print("ユーザーマニュアルテストが失敗しました。")
        print("ヘルプダイアログのテストをスキップします。")


if __name__ == "__main__":
    main()