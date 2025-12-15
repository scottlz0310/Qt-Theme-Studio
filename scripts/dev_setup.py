#!/usr/bin/env python3
"""
開発環境自動セットアップスクリプト

このスクリプトは新規開発者向けにQt-Theme-Studioの
開発環境をワンコマンドで構築します。

機能:
- 仮想環境の作成・検出
- 依存関係の自動インストール
- pre-commit設定の自動化
- OS別の設定差異の吸収
- Qt フレームワークの自動検出・設定
"""

import os
import platform
import subprocess
import sys
import venv
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_logger():
    """ロガーを取得（日本語対応）"""
    import logging

    # 日本語対応のロガー設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    return logging.getLogger(__name__)


logger = get_logger()


class EnvironmentDetector:
    """環境検出クラス"""

    @staticmethod
    def get_os_info() -> Dict[str, str]:
        """OS情報を取得"""
        system = platform.system()
        release = platform.release()
        machine = platform.machine()

        return {
            "system": system,
            "release": release,
            "machine": machine,
            "is_windows": system == "Windows",
            "is_linux": system == "Linux",
            "is_macos": system == "Darwin",
            "is_wsl": "microsoft" in release.lower() if system == "Linux" else False,
        }

    @staticmethod
    def detect_virtual_environment() -> Tuple[bool, Optional[str], Optional[str]]:
        """仮想環境の検出"""
        # VIRTUAL_ENV環境変数をチェック
        virtual_env = os.environ.get("VIRTUAL_ENV")
        if virtual_env:
            logger.info(f"仮想環境が検出されました: {virtual_env}")
            return True, virtual_env, "venv"

        # condaの環境をチェック
        conda_env = os.environ.get("CONDA_DEFAULT_ENV")
        if conda_env and conda_env != "base":
            logger.info(f"Conda環境が検出されました: {conda_env}")
            return True, conda_env, "conda"

        # poetryの環境をチェック
        if os.environ.get("POETRY_ACTIVE"):
            logger.info("Poetry環境が検出されました")
            return True, "poetry", "poetry"

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
                        logger.info(
                            f"仮想環境ディレクトリが検出されました: {venv_path}"
                        )
                        return True, str(venv_path), "venv"

        logger.warning("仮想環境が検出されませんでした")
        return False, None, None

    @staticmethod
    def check_python_version() -> bool:
        """Pythonバージョンをチェック"""
        version = sys.version_info
        logger.info(
            f"Pythonバージョン: {version.major}.{version.minor}.{version.micro}"
        )

        if version.major != 3 or version.minor < 9:
            logger.error("❌ Python 3.9以上が必要です")
            logger.info("サポート対象バージョン: Python 3.9, 3.10, 3.11, 3.12")
            return False

        if version.minor > 12:
            logger.warning(f"⚠️  Python {version.major}.{version.minor}は未テストです")
            logger.info("サポート対象バージョン: Python 3.9, 3.10, 3.11, 3.12")

        logger.info("✅ Pythonバージョンは要件を満たしています")
        return True


class CommandRunner:
    """コマンド実行クラス"""

    @staticmethod
    def run_command(
        command: List[str],
        description: str,
        cwd: Optional[Path] = None,
        timeout: int = 300,
    ) -> bool:
        """コマンドを実行"""
        logger.info(f"{description}を実行中...")
        logger.debug(f"コマンド: {' '.join(command)}")
        if cwd:
            logger.debug(f"作業ディレクトリ: {cwd}")

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd,
                timeout=timeout,
            )

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
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {description}がタイムアウトしました（{timeout}秒）")
            return False
        except FileNotFoundError:
            logger.error(f"❌ コマンドが見つかりません: {command[0]}")
            return False


class VirtualEnvironmentManager:
    """仮想環境管理クラス"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.venv_path = project_root / "venv"

    def create_virtual_environment(self) -> bool:
        """仮想環境を作成"""
        if self.venv_path.exists():
            logger.info(f"仮想環境は既に存在します: {self.venv_path}")
            return True

        logger.info(f"仮想環境を作成中: {self.venv_path}")

        try:
            # venvモジュールを使用して仮想環境を作成
            venv.create(
                self.venv_path,
                system_site_packages=False,
                clear=False,
                symlinks=not platform.system() == "Windows",
                with_pip=True,
            )

            logger.info("✅ 仮想環境の作成が完了しました")
            return True

        except Exception as e:
            logger.error(f"❌ 仮想環境の作成に失敗しました: {e}")
            return False

    def get_python_executable(self) -> Optional[Path]:
        """仮想環境のPython実行ファイルパスを取得"""
        if platform.system() == "Windows":
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:
            python_path = self.venv_path / "bin" / "python"

        if python_path.exists():
            return python_path

        logger.error(f"❌ Python実行ファイルが見つかりません: {python_path}")
        return None

    def activate_instructions(self) -> List[str]:
        """仮想環境のアクティベート手順を取得"""
        os_info = EnvironmentDetector.get_os_info()

        if os_info["is_windows"]:
            return [
                f"{self.venv_path}\\Scripts\\activate",
                "# または PowerShell の場合:",
                f"{self.venv_path}\\Scripts\\Activate.ps1",
            ]
        return [f"source {self.venv_path}/bin/activate"]


class DependencyManager:
    """依存関係管理クラス"""

    def __init__(self, python_executable: Path, project_root: Path):
        self.python_executable = python_executable
        self.project_root = project_root

    def upgrade_pip(self) -> bool:
        """pipをアップグレード"""
        command = [
            str(self.python_executable),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        ]
        return CommandRunner.run_command(command, "pipのアップグレード")

    def install_project_dependencies(self) -> bool:
        """プロジェクト依存関係をインストール"""
        # 開発依存関係を含めてインストール
        command = [str(self.python_executable), "-m", "pip", "install", "-e", ".[dev]"]
        return CommandRunner.run_command(
            command,
            "プロジェクト依存関係のインストール",
            cwd=self.project_root,
            timeout=600,  # 10分のタイムアウト
        )

    def install_qt_framework(self) -> bool:
        """Qt フレームワークのインストール確認"""
        # qt_detector.pyを使用してQt フレームワークを検出・インストール
        qt_detector_path = self.project_root / "scripts" / "qt_detector.py"

        if not qt_detector_path.exists():
            logger.warning(
                "qt_detector.pyが見つかりません。Qt フレームワークの自動検出をスキップします"
            )
            return True

        command = [str(self.python_executable), str(qt_detector_path), "--install"]
        return CommandRunner.run_command(
            command, "Qt フレームワークの検出・インストール"
        )


class PreCommitManager:
    """Pre-commit管理クラス"""

    def __init__(self, python_executable: Path, project_root: Path):
        self.python_executable = python_executable
        self.project_root = project_root

    def setup_pre_commit(self) -> bool:
        """pre-commitをセットアップ"""
        # pre_commit_setup.pyを使用
        setup_script = self.project_root / "scripts" / "pre_commit_setup.py"

        if not setup_script.exists():
            logger.error("❌ pre_commit_setup.pyが見つかりません")
            return False

        command = [str(self.python_executable), str(setup_script)]
        return CommandRunner.run_command(
            command, "pre-commitのセットアップ", cwd=self.project_root
        )


class DirectoryManager:
    """ディレクトリ管理クラス"""

    @staticmethod
    def create_required_directories(project_root: Path) -> bool:
        """必要なディレクトリを作成"""
        directories = [
            "logs",
            "themes/exports",
            "themes/import",
            "examples",
        ]

        try:
            for dir_path in directories:
                full_path = project_root / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"ディレクトリを作成: {full_path}")

            logger.info("✅ 必要なディレクトリの作成が完了しました")
            return True

        except Exception as e:
            logger.error(f"❌ ディレクトリの作成に失敗しました: {e}")
            return False


class EnvironmentValidator:
    """環境検証クラス"""

    def __init__(self, python_executable: Path, project_root: Path):
        self.python_executable = python_executable
        self.project_root = project_root

    def validate_installation(self) -> bool:
        """インストールの検証"""
        logger.info("インストールの検証を実行中...")

        # 基本的なインポートテスト
        test_imports = [
            "qt_theme_studio",
            "pytest",
            "ruff",
            "pre_commit",
        ]

        for module in test_imports:
            if not self._test_import(module):
                return False

        # Qt フレームワークのテスト
        if not self._test_qt_framework():
            logger.warning(
                "⚠️  Qt フレームワークの検証で問題が発生しましたが、セットアップは継続します"
            )

        logger.info("✅ インストールの検証が完了しました")
        return True

    def _test_import(self, module_name: str) -> bool:
        """モジュールのインポートテスト"""
        command = [
            str(self.python_executable),
            "-c",
            f"import {module_name}; print(f'{module_name} インポート成功')",
        ]

        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, timeout=30
            )
            logger.debug(f"✅ {module_name}: {result.stdout.strip()}")
            return True

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.error(f"❌ {module_name}のインポートに失敗しました")
            if hasattr(e, "stderr") and e.stderr:
                logger.error(f"エラー: {e.stderr}")
            return False

    def _test_qt_framework(self) -> bool:
        """Qt フレームワークのテスト"""
        qt_test_script = """
import sys
try:
    # PySide6を試行
    from PySide6.QtCore import QCoreApplication
    print("PySide6が利用可能です")
    sys.exit(0)
except ImportError:
    pass

try:
    # PyQt6を試行
    from PyQt6.QtCore import QCoreApplication
    print("PyQt6が利用可能です")
    sys.exit(0)
except ImportError:
    pass

try:
    # PyQt5を試行
    from PyQt5.QtCore import QCoreApplication
    print("PyQt5が利用可能です")
    sys.exit(0)
except ImportError:
    pass

print("Qt フレームワークが見つかりません")
sys.exit(1)
"""

        command = [str(self.python_executable), "-c", qt_test_script]

        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, timeout=30
            )
            logger.info(f"✅ Qt フレームワーク: {result.stdout.strip()}")
            return True

        except subprocess.CalledProcessError:
            logger.error("❌ Qt フレームワークが利用できません")
            return False


def main():
    """メイン処理"""
    logger.info("🚀 Qt-Theme-Studio 開発環境セットアップを開始します")

    # プロジェクトルートの取得
    project_root = Path(__file__).parent.parent
    logger.info(f"プロジェクトルート: {project_root}")

    # OS情報の表示
    os_info = EnvironmentDetector.get_os_info()
    logger.info(f"OS: {os_info['system']} {os_info['release']} ({os_info['machine']})")
    if os_info["is_wsl"]:
        logger.info("WSL環境が検出されました")

    # Pythonバージョンチェック
    if not EnvironmentDetector.check_python_version():
        sys.exit(1)

    # 既存の仮想環境をチェック
    in_venv, venv_path, venv_type = EnvironmentDetector.detect_virtual_environment()

    python_executable = None

    if in_venv:
        logger.info(f"既存の仮想環境を使用します: {venv_path} ({venv_type})")
        if venv_type == "venv":
            # venv環境の場合、Python実行ファイルパスを取得
            venv_manager = VirtualEnvironmentManager(project_root)
            if venv_path == str(venv_manager.venv_path):
                python_executable = venv_manager.get_python_executable()
            else:
                # 別の場所のvenv環境
                if os_info["is_windows"]:
                    python_executable = Path(venv_path) / "Scripts" / "python.exe"
                else:
                    python_executable = Path(venv_path) / "bin" / "python"
        else:
            # conda, poetry等の場合は現在のPython実行ファイルを使用
            python_executable = Path(sys.executable)
    else:
        # 仮想環境を作成
        logger.info("新しい仮想環境を作成します")

        response = input("仮想環境を作成しますか？ (Y/n): ")
        if response.lower() in ["n", "no"]:
            logger.info("仮想環境なしで続行します")
            python_executable = Path(sys.executable)
        else:
            venv_manager = VirtualEnvironmentManager(project_root)
            if not venv_manager.create_virtual_environment():
                logger.error("❌ 仮想環境の作成に失敗しました")
                sys.exit(1)

            python_executable = venv_manager.get_python_executable()
            if not python_executable:
                sys.exit(1)

            logger.info("📋 仮想環境のアクティベート方法:")
            for instruction in venv_manager.activate_instructions():
                logger.info(f"  {instruction}")
            logger.info("")

    if not python_executable or not python_executable.exists():
        logger.error("❌ Python実行ファイルが見つかりません")
        sys.exit(1)

    logger.info(f"使用するPython: {python_executable}")

    # 必要なディレクトリの作成
    if not DirectoryManager.create_required_directories(project_root):
        logger.warning("ディレクトリの作成で問題が発生しましたが、続行します")

    # 依存関係の管理
    dep_manager = DependencyManager(python_executable, project_root)

    # pipのアップグレード
    if not dep_manager.upgrade_pip():
        logger.warning("pipのアップグレードに失敗しましたが、続行します")

    # プロジェクト依存関係のインストール
    if not dep_manager.install_project_dependencies():
        logger.error("❌ プロジェクト依存関係のインストールに失敗しました")
        sys.exit(1)

    # Qt フレームワークの検出・インストール
    if not dep_manager.install_qt_framework():
        logger.warning("Qt フレームワークの検出で問題が発生しましたが、続行します")

    # pre-commitのセットアップ
    precommit_manager = PreCommitManager(python_executable, project_root)
    if not precommit_manager.setup_pre_commit():
        logger.warning("pre-commitのセットアップで問題が発生しましたが、続行します")

    # インストールの検証
    validator = EnvironmentValidator(python_executable, project_root)
    if not validator.validate_installation():
        logger.error("❌ インストールの検証に失敗しました")
        sys.exit(1)

    # 完了メッセージ
    logger.info("🎉 開発環境のセットアップが完了しました！")
    logger.info("")
    logger.info("📋 次のステップ:")

    if not in_venv and python_executable != Path(sys.executable):
        logger.info("  1. 仮想環境をアクティベートしてください:")
        venv_manager = VirtualEnvironmentManager(project_root)
        for instruction in venv_manager.activate_instructions():
            logger.info(f"     {instruction}")

    logger.info("  2. アプリケーションを起動してみてください:")
    logger.info("     python qt_theme_studio_main.py")
    logger.info("     # または")
    logger.info("     python -m qt_theme_studio")
    logger.info("")
    logger.info("  3. テストを実行してみてください:")
    logger.info("     pytest")
    logger.info("")
    logger.info("  4. コード品質チェックを実行してみてください:")
    logger.info("     uv run ruff format .")
    logger.info("     uv run ruff check . --fix")
    logger.info("")
    logger.info("🔧 便利なコマンド:")
    logger.info("  python scripts/quality_check.py     # 品質チェック統合実行")
    logger.info("  python scripts/quality_dashboard.py # 品質ダッシュボード")
    logger.info("  pre-commit run --all-files          # pre-commitフック実行")
    logger.info("")
    logger.info("📚 詳細情報:")
    logger.info("  README.md                           # プロジェクト概要")
    logger.info("  docs/                               # ドキュメント")
    logger.info("  .pre-commit-config.yaml             # pre-commit設定")


if __name__ == "__main__":
    main()
