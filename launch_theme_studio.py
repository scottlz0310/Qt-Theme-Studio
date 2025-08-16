#!/usr/bin/env python3
"""
Qt-Theme-Studio 統合ランチャー

このスクリプトは、Qt-Theme-Studioアプリケーションのメインエントリーポイントです。
コマンドライン引数処理、エラーハンドリング、日本語メッセージ表示を提供します。

使用方法:
    python launch_theme_studio.py [オプション]
    
オプション:
    --config-dir PATH    設定ディレクトリのパス
    --theme PATH         起動時に読み込むテーマファイル
    --debug             デバッグモードで起動
    --version           バージョン情報を表示
    --help              このヘルプメッセージを表示
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List

# アプリケーションのバージョン情報
__version__ = "1.0.0"
__author__ = "Qt-Theme-Studio Team"


def setup_logging(debug: bool = False) -> None:
    """ログシステムを設定する
    
    Args:
        debug: デバッグモードの場合True
    """
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Qt関連のログレベルを調整
    if not debug:
        logging.getLogger('qt_theme_studio').setLevel(logging.INFO)


def print_version() -> None:
    """バージョン情報を表示する"""
    print(f"Qt-Theme-Studio バージョン {__version__}")
    print(f"作成者: {__author__}")
    print("統合テーマエディターGUIアプリケーション")
    print()
    print("依存関係:")
    
    # Qt フレームワークの検出と表示
    qt_frameworks = ['PySide6', 'PyQt6', 'PyQt5']
    detected_frameworks = []
    
    for framework in qt_frameworks:
        try:
            module = __import__(framework)
            version = getattr(module, '__version__', '不明')
            detected_frameworks.append(f"  {framework}: {version}")
        except ImportError:
            detected_frameworks.append(f"  {framework}: 未インストール")
    
    print("\n".join(detected_frameworks))
    
    # qt-theme-manager の検出
    try:
        import qt_theme_manager
        print(f"  qt-theme-manager: インストール済み")
    except ImportError:
        print(f"  qt-theme-manager: 未インストール")


def print_help() -> None:
    """ヘルプメッセージを表示する"""
    print("Qt-Theme-Studio - 統合テーマエディター")
    print()
    print("使用方法:")
    print("  python launch_theme_studio.py [オプション]")
    print()
    print("オプション:")
    print("  --config-dir PATH    設定ディレクトリのパス")
    print("  --theme PATH         起動時に読み込むテーマファイル")
    print("  --debug             デバッグモードで起動")
    print("  --headless          ヘッドレスモードで起動（GUI表示なし、テスト用）")
    print("  --version           バージョン情報を表示")
    print("  --help              このヘルプメッセージを表示")
    print()
    print("例:")
    print("  python launch_theme_studio.py")
    print("  python launch_theme_studio.py --debug")
    print("  python launch_theme_studio.py --theme my_theme.json")
    print("  python launch_theme_studio.py --config-dir ~/.qt-theme-studio")
    print("  python launch_theme_studio.py --headless --debug  # SSH環境でのテスト用")


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数を解析する
    
    Returns:
        解析された引数
    """
    parser = argparse.ArgumentParser(
        description="Qt-Theme-Studio - 統合テーマエディター",
        add_help=False  # カスタムヘルプを使用
    )
    
    parser.add_argument(
        '--config-dir',
        type=str,
        help='設定ディレクトリのパス'
    )
    
    parser.add_argument(
        '--theme',
        type=str,
        help='起動時に読み込むテーマファイルのパス'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='デバッグモードで起動'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='バージョン情報を表示'
    )
    
    parser.add_argument(
        '--help',
        action='store_true',
        help='このヘルプメッセージを表示'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='ヘッドレスモードで起動（GUI表示なし、テスト用）'
    )
    
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> List[str]:
    """引数の妥当性を検証する
    
    Args:
        args: 解析された引数
        
    Returns:
        エラーメッセージのリスト（エラーがない場合は空リスト）
    """
    errors = []
    
    # 設定ディレクトリの検証
    if args.config_dir:
        config_path = Path(args.config_dir)
        if config_path.exists() and not config_path.is_dir():
            errors.append(f"エラー: 指定された設定ディレクトリはファイルです: {args.config_dir}")
        
        # 親ディレクトリが存在しない場合
        if not config_path.parent.exists():
            errors.append(f"エラー: 設定ディレクトリの親ディレクトリが存在しません: {config_path.parent}")
    
    # テーマファイルの検証
    if args.theme:
        theme_path = Path(args.theme)
        if not theme_path.exists():
            errors.append(f"エラー: 指定されたテーマファイルが見つかりません: {args.theme}")
        elif not theme_path.is_file():
            errors.append(f"エラー: 指定されたテーマパスはファイルではありません: {args.theme}")
        elif theme_path.suffix.lower() not in ['.json', '.qss', '.css']:
            errors.append(f"警告: サポートされていないテーマファイル形式です: {theme_path.suffix}")
    
    return errors


def check_dependencies() -> List[str]:
    """依存関係をチェックする
    
    Returns:
        エラーメッセージのリスト（エラーがない場合は空リスト）
    """
    errors = []
    
    # Qt フレームワークのチェック
    qt_frameworks = ['PySide6', 'PyQt6', 'PyQt5']
    qt_available = False
    
    for framework in qt_frameworks:
        try:
            __import__(framework)
            qt_available = True
            break
        except ImportError:
            continue
    
    if not qt_available:
        errors.append(
            "エラー: 利用可能なQtフレームワークが見つかりません。\n"
            "以下のいずれかをインストールしてください:\n"
            "  pip install PySide6  (推奨)\n"
            "  pip install PyQt6\n"
            "  pip install PyQt5"
        )
    
    # qt-theme-manager のチェック
    try:
        import qt_theme_manager
    except ImportError:
        errors.append(
            "エラー: qt-theme-managerライブラリが見つかりません。\n"
            "以下のコマンドでインストールしてください:\n"
            "  pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git"
        )
    
    return errors


def main() -> int:
    """メイン関数
    
    Returns:
        終了コード（0: 成功、1: エラー）
    """
    try:
        # コマンドライン引数の解析
        args = parse_arguments()
        
        # ヘルプまたはバージョン表示の場合
        if args.help:
            print_help()
            return 0
        
        if args.version:
            print_version()
            return 0
        
        # ログシステムの設定
        setup_logging(args.debug)
        logger = logging.getLogger(__name__)
        
        logger.info("Qt-Theme-Studio を起動しています...")
        
        # 引数の妥当性検証
        validation_errors = validate_arguments(args)
        if validation_errors:
            for error in validation_errors:
                if error.startswith("警告:"):
                    logger.warning(error)
                else:
                    print(error, file=sys.stderr)
                    return 1
        
        # 依存関係のチェック
        dependency_errors = check_dependencies()
        if dependency_errors:
            for error in dependency_errors:
                print(error, file=sys.stderr)
            return 1
        
        # アプリケーションのインポートと起動
        try:
            from qt_theme_studio.main import main as app_main
            
            logger.info("アプリケーションを初期化しています...")
            
            # アプリケーションに引数を渡して実行
            exit_code = app_main(
                config_dir=args.config_dir,
                initial_theme=args.theme,
                debug_mode=args.debug
            )
            
            logger.info(f"Qt-Theme-Studio が終了しました (終了コード: {exit_code})")
            return exit_code
            
        except ImportError as e:
            error_msg = (
                f"エラー: Qt-Theme-Studioアプリケーションの読み込みに失敗しました。\n"
                f"詳細: {str(e)}\n"
                f"アプリケーションが正しくインストールされているか確認してください。"
            )
            print(error_msg, file=sys.stderr)
            logger.error(error_msg)
            return 1
            
        except Exception as e:
            error_msg = f"予期しないエラーが発生しました: {str(e)}"
            print(error_msg, file=sys.stderr)
            logger.error(error_msg, exc_info=True)
            return 1
    
    except KeyboardInterrupt:
        print("\nユーザーによって中断されました。", file=sys.stderr)
        return 1
    
    except Exception as e:
        error_msg = f"起動処理中に予期しないエラーが発生しました: {str(e)}"
        print(error_msg, file=sys.stderr)
        return 1


if __name__ == "__main__":
    # Python バージョンチェック
    if sys.version_info < (3, 8):
        print("エラー: Python 3.8以上が必要です。", file=sys.stderr)
        print(f"現在のバージョン: {sys.version}", file=sys.stderr)
        sys.exit(1)
    
    # メイン処理の実行
    exit_code = main()
    sys.exit(exit_code)