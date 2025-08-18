#!/usr/bin/env python3
"""
Pre-commitセットアップスクリプト

このスクリプトは新規開発者向けにpre-commitフックを
自動的にインストール・設定します。
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def get_logger():
    """ロガーを取得（簡易版）"""
    import logging

    # 日本語対応のロガー設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    return logging.getLogger(__name__)


logger = get_logger()


def detect_virtual_environment() -> Tuple[bool, Optional[str]]:
    """仮想環境の検出"""
    # VIRTUAL_ENV環境変数をチェック
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if virtual_env:
        logger.info(f"仮想環境が検出されました: {virtual_env}")
        return True, virtual_env

    # condaの環境をチェック
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    if conda_env and conda_env != "base":
        logger.info(f"Conda環境が検出されました: {conda_env}")
        return True, conda_env

    # venvディレクトリの存在をチェック
    project_root = Path(__file__).parent.parent
    venv_dirs = ["venv", ".venv", "env", ".env"]

    for venv_dir in venv_dirs:
        venv_path = project_root / venv_dir
        if venv_path.exists() and venv_path.is_dir():
            # Pythonバイナリの存在をチェック
            python_paths = [
                venv_path / "bin" / "python",  # Unix系
                venv_path / "Scripts" / "python.exe",  # Windows
            ]

            for python_path in python_paths:
                if python_path.exists():
                    logger.info(f"仮想環境ディレクトリが検出されました: {venv_path}")
                    return True, str(venv_path)

    logger.warning("仮想環境が検出されませんでした")
    return False, None


def run_command(command: list, description: str) -> bool:
    """コマンドを実行"""
    logger.info(f"{description}を実行中...")
    logger.debug(f"コマンド: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        if result.stdout:
            logger.debug(f"出力: {result.stdout}")

        logger.info(f"✅ {description}が完了しました")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description}が失敗しました")
        logger.error(f"エラーコード: {e.returncode}")
        if e.stdout:
            logger.error(f"標準出力: {e.stdout}")
        if e.stderr:
            logger.error(f"標準エラー: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error(f"❌ コマンドが見つかりません: {command[0]}")
        return False


def check_python_version() -> bool:
    """Pythonバージョンをチェック"""
    version = sys.version_info
    logger.info(f"Pythonバージョン: {version.major}.{version.minor}.{version.micro}")

    if version.major != 3 or version.minor < 9:
        logger.error("❌ Python 3.9以上が必要です")
        return False

    logger.info("✅ Pythonバージョンは要件を満たしています")
    return True


def install_pre_commit() -> bool:
    """pre-commitをインストール"""
    # pre-commitがすでにインストールされているかチェック
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pre_commit", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info(
            f"✅ pre-commitは既にインストールされています: {result.stdout.strip()}"
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # pre-commitをインストール
    logger.info("pre-commitをインストールしています...")

    install_commands = [
        # pipでインストール
        [sys.executable, "-m", "pip", "install", "pre-commit"],
    ]

    for command in install_commands:
        if run_command(command, "pre-commitのインストール"):
            return True

    logger.error("❌ pre-commitのインストールに失敗しました")
    return False


def setup_pre_commit_hooks() -> bool:
    """pre-commitフックをセットアップ"""
    project_root = Path(__file__).parent.parent
    config_file = project_root / ".pre-commit-config.yaml"

    if not config_file.exists():
        logger.error(f"❌ pre-commit設定ファイルが見つかりません: {config_file}")
        return False

    # pre-commitフックをインストール
    os.chdir(project_root)

    commands = [
        # フックをインストール
        [sys.executable, "-m", "pre_commit", "install"],
        # 設定を更新
        [sys.executable, "-m", "pre_commit", "autoupdate"],
    ]

    for command in commands:
        description = (
            "pre-commitフックのインストール"
            if "install" in command
            else "pre-commit設定の更新"
        )
        if not run_command(command, description):
            return False

    return True


def install_development_dependencies() -> bool:
    """開発依存関係をインストール"""
    project_root = Path(__file__).parent.parent
    pyproject_file = project_root / "pyproject.toml"

    if not pyproject_file.exists():
        logger.warning(
            "pyproject.tomlが見つかりません。依存関係のインストールをスキップします"
        )
        return True

    # 開発依存関係をインストール
    command = [sys.executable, "-m", "pip", "install", "-e", ".[dev]"]

    return run_command(command, "開発依存関係のインストール")


def create_logs_directory() -> bool:
    """ログディレクトリを作成"""
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / "logs"

    try:
        logs_dir.mkdir(exist_ok=True)
        logger.info(f"✅ ログディレクトリを作成しました: {logs_dir}")
        return True
    except Exception as e:
        logger.error(f"❌ ログディレクトリの作成に失敗しました: {e}")
        return False


def verify_setup() -> bool:
    """セットアップの検証"""
    logger.info("セットアップの検証を実行中...")

    # pre-commitの動作確認
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pre_commit", "run", "--all-files", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=30,  # 30秒でタイムアウト
        )

        if result.returncode == 0:
            logger.info("✅ pre-commitフックの検証が完了しました")
            return True
        logger.warning(
            "⚠️  pre-commitフックで問題が検出されましたが、セットアップは完了しています"
        )
        logger.info("実際のコミット時に自動修正されます")
        return True

    except subprocess.TimeoutExpired:
        logger.warning("⚠️  検証がタイムアウトしましたが、セットアップは完了しています")
        return True
    except Exception as e:
        logger.error(f"❌ 検証中にエラーが発生しました: {e}")
        return False


def main():
    """メイン処理"""
    logger.info("🚀 Qt-Theme-Studio Pre-commitセットアップを開始します")

    # Pythonバージョンチェック
    if not check_python_version():
        sys.exit(1)

    # 仮想環境の検出
    in_venv, venv_path = detect_virtual_environment()
    if not in_venv:
        logger.warning("⚠️  仮想環境が検出されませんでした")
        logger.info("仮想環境の使用を強く推奨します:")
        logger.info("  python -m venv venv")
        logger.info("  source venv/bin/activate  # Linux/Mac")
        logger.info("  venv\\Scripts\\activate     # Windows")

        response = input("\n仮想環境なしで続行しますか？ (y/N): ")
        if response.lower() not in ["y", "yes"]:
            logger.info("セットアップを中止しました")
            sys.exit(0)

    # ログディレクトリの作成
    if not create_logs_directory():
        logger.warning("ログディレクトリの作成に失敗しましたが、続行します")

    # 開発依存関係のインストール
    if not install_development_dependencies():
        logger.error("❌ 開発依存関係のインストールに失敗しました")
        sys.exit(1)

    # pre-commitのインストール
    if not install_pre_commit():
        logger.error("❌ pre-commitのインストールに失敗しました")
        sys.exit(1)

    # pre-commitフックのセットアップ
    if not setup_pre_commit_hooks():
        logger.error("❌ pre-commitフックのセットアップに失敗しました")
        sys.exit(1)

    # セットアップの検証
    if not verify_setup():
        logger.error("❌ セットアップの検証に失敗しました")
        sys.exit(1)

    # 完了メッセージ
    logger.info("🎉 Pre-commitセットアップが完了しました！")
    logger.info("")
    logger.info("📋 次のステップ:")
    logger.info("  1. コードを変更してコミットしてみてください")
    logger.info("  2. pre-commitフックが自動的に実行されます")
    logger.info("  3. 品質チェックが通過すればコミットが完了します")
    logger.info("")
    logger.info("🔧 手動実行コマンド:")
    logger.info("  pre-commit run --all-files  # 全ファイルをチェック")
    logger.info("  pre-commit run <フック名>    # 特定のフックを実行")
    logger.info("")
    logger.info("📚 詳細情報:")
    logger.info("  設定ファイル: .pre-commit-config.yaml")
    logger.info("  ログファイル: logs/")


if __name__ == "__main__":
    main()
