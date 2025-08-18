#!/usr/bin/env python3
"""
Qt フレームワーク自動検出スクリプト

このスクリプトはPySide6/PyQt6/PyQt5の利用可能性を検出し、
最適な設定を自動適用します。

機能:
- Qt フレームワークの自動検出
- 検出結果に基づく最適な設定の自動適用
- 不足している場合のインストール案内
- 環境変数の設定提案
"""

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


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


@dataclass
class QtFramework:
    """Qt フレームワーク情報"""

    name: str
    module_name: str
    version: Optional[str] = None
    is_available: bool = False
    import_error: Optional[str] = None
    priority: int = 0  # 優先度（低い数値ほど高優先度）


class QtDetector:
    """Qt フレームワーク検出クラス"""

    def __init__(self):
        self.frameworks = [
            QtFramework("PySide6", "PySide6", priority=1),
            QtFramework("PyQt6", "PyQt6", priority=2),
            QtFramework("PyQt5", "PyQt5", priority=3),
        ]

    def detect_all_frameworks(self) -> List[QtFramework]:
        """すべてのQt フレームワークを検出"""
        logger.info("Qt フレームワークの検出を開始します...")

        for framework in self.frameworks:
            self._detect_framework(framework)

        return self.frameworks

    def _detect_framework(self, framework: QtFramework) -> None:
        """個別のQt フレームワークを検出"""
        logger.debug(f"{framework.name}の検出中...")

        try:
            # モジュールのインポートを試行
            import importlib

            module = importlib.import_module(framework.module_name)

            # バージョン情報を取得
            version = getattr(module, "__version__", "不明")
            framework.version = version
            framework.is_available = True

            logger.info(f"✅ {framework.name} {version} が利用可能です")

        except ImportError as e:
            framework.import_error = str(e)
            framework.is_available = False
            logger.debug(f"❌ {framework.name} は利用できません: {e}")

    def get_available_frameworks(self) -> List[QtFramework]:
        """利用可能なQt フレームワークを取得"""
        return [fw for fw in self.frameworks if fw.is_available]

    def get_recommended_framework(self) -> Optional[QtFramework]:
        """推奨Qt フレームワークを取得（優先度順）"""
        available = self.get_available_frameworks()
        if not available:
            return None

        # 優先度順でソート
        available.sort(key=lambda x: x.priority)
        return available[0]

    def get_installation_candidates(self) -> List[QtFramework]:
        """インストール候補を取得"""
        unavailable = [fw for fw in self.frameworks if not fw.is_available]
        # 優先度順でソート
        unavailable.sort(key=lambda x: x.priority)
        return unavailable


class QtInstaller:
    """Qt フレームワークインストーラー"""

    def __init__(self, python_executable: Optional[str] = None):
        self.python_executable = python_executable or sys.executable

    def install_framework(self, framework: QtFramework) -> bool:
        """Qt フレームワークをインストール"""
        logger.info(f"{framework.name}のインストールを開始します...")

        # インストールコマンドを構築
        package_name = self._get_package_name(framework)
        command = [self.python_executable, "-m", "pip", "install", package_name]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=300,  # 5分のタイムアウト
            )

            logger.info(f"✅ {framework.name}のインストールが完了しました")
            if result.stdout:
                logger.debug(f"出力: {result.stdout}")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ {framework.name}のインストールに失敗しました")
            logger.error(f"エラーコード: {e.returncode}")
            if e.stderr:
                logger.error(f"エラー: {e.stderr}")
            return False

        except subprocess.TimeoutExpired:
            logger.error(f"❌ {framework.name}のインストールがタイムアウトしました")
            return False

    def _get_package_name(self, framework: QtFramework) -> str:
        """パッケージ名を取得"""
        # 特別な要件がある場合はここで処理
        package_names = {
            "PySide6": "PySide6>=6.0.0",
            "PyQt6": "PyQt6>=6.0.0",
            "PyQt5": "PyQt5>=5.15.0",
        }

        return package_names.get(framework.name, framework.module_name)


class QtConfigurationManager:
    """Qt 設定管理クラス"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def generate_environment_config(self, framework: QtFramework) -> Dict[str, str]:
        """環境変数設定を生成"""
        config = {}

        # 基本的なQt設定
        if framework.name in ["PySide6", "PyQt6"]:
            # Qt6系の設定
            config.update(
                {
                    "QT_API": framework.module_name.lower(),
                    "QT_QPA_PLATFORM_PLUGIN_PATH": "",  # 自動検出に任せる
                }
            )
        elif framework.name == "PyQt5":
            # Qt5系の設定
            config.update(
                {
                    "QT_API": "pyqt5",
                }
            )

        # WSL環境の検出と設定
        if self._is_wsl_environment():
            config.update(self._get_wsl_config(framework))

        return config

    def _is_wsl_environment(self) -> bool:
        """WSL環境かどうかを判定"""
        try:
            with open("/proc/version") as f:
                version_info = f.read().lower()
                return "microsoft" in version_info
        except (FileNotFoundError, PermissionError):
            return False

    def _get_wsl_config(self, framework: QtFramework) -> Dict[str, str]:
        """WSL環境用の設定を取得"""
        logger.info("WSL環境が検出されました。WSL用の設定を適用します")

        # WSL環境でのQt設定
        wsl_config = {
            "QT_QPA_PLATFORM": "xcb",
            "DISPLAY": ":0",
            "QT_LOGGING_RULES": "qt.qpa.*=false",
            "QT_ACCESSIBILITY": "0",
        }

        # WSLgの検出
        if os.environ.get("WAYLAND_DISPLAY"):
            logger.info("WSLg環境が検出されました")
            wsl_config.update(
                {
                    "QT_QPA_PLATFORM": "wayland",
                    "WAYLAND_DISPLAY": "wayland-0",
                    "XDG_SESSION_TYPE": "wayland",
                }
            )

        return wsl_config

    def create_qt_config_file(self, framework: QtFramework) -> bool:
        """Qt設定ファイルを作成"""
        config_dir = self.project_root / ".qt_config"
        config_dir.mkdir(exist_ok=True)

        config_file = config_dir / "qt_framework.py"

        config_content = f'''"""
Qt フレームワーク設定ファイル
自動生成されました - 手動編集は推奨されません

検出されたフレームワーク: {framework.name} {framework.version}
"""

# 推奨Qt フレームワーク
PREFERRED_QT_FRAMEWORK = "{framework.name}"
QT_VERSION = "{framework.version}"

# インポート設定
def get_qt_imports():
    """Qt インポートを取得"""
    try:
        if PREFERRED_QT_FRAMEWORK == "PySide6":
            from PySide6.QtCore import QCoreApplication, QSettings
            from PySide6.QtWidgets import QApplication, QWidget
            from PySide6.QtGui import QIcon, QPixmap
            return {{
                "QCoreApplication": QCoreApplication,
                "QApplication": QApplication,
                "QWidget": QWidget,
                "QSettings": QSettings,
                "QIcon": QIcon,
                "QPixmap": QPixmap,
            }}
        elif PREFERRED_QT_FRAMEWORK == "PyQt6":
            from PyQt6.QtCore import QCoreApplication, QSettings
            from PyQt6.QtWidgets import QApplication, QWidget
            from PyQt6.QtGui import QIcon, QPixmap
            return {{
                "QCoreApplication": QCoreApplication,
                "QApplication": QApplication,
                "QWidget": QWidget,
                "QSettings": QSettings,
                "QIcon": QIcon,
                "QPixmap": QPixmap,
            }}
        elif PREFERRED_QT_FRAMEWORK == "PyQt5":
            from PyQt5.QtCore import QCoreApplication, QSettings
            from PyQt5.QtWidgets import QApplication, QWidget
            from PyQt5.QtGui import QIcon, QPixmap
            return {{
                "QCoreApplication": QCoreApplication,
                "QApplication": QApplication,
                "QWidget": QWidget,
                "QSettings": QSettings,
                "QIcon": QIcon,
                "QPixmap": QPixmap,
            }}
    except ImportError as e:
        raise ImportError(f"Qt フレームワーク {{PREFERRED_QT_FRAMEWORK}} のインポートに失敗しました: {{e}}")

# 環境変数設定
ENVIRONMENT_VARIABLES = {self.generate_environment_config(framework)}
'''

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(config_content)

            logger.info(f"✅ Qt設定ファイルを作成しました: {config_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Qt設定ファイルの作成に失敗しました: {e}")
            return False


class QtValidator:
    """Qt フレームワーク検証クラス"""

    def __init__(self, framework: QtFramework):
        self.framework = framework

    def validate_framework(self) -> bool:
        """Qt フレームワークの動作を検証"""
        logger.info(f"{self.framework.name}の動作検証を実行中...")

        # 基本的なインポートテスト
        if not self._test_basic_imports():
            return False

        # GUI機能のテスト（ヘッドレス環境対応）
        if not self._test_gui_functionality():
            logger.warning(
                "GUI機能のテストで問題が発生しましたが、基本機能は利用可能です"
            )

        logger.info(f"✅ {self.framework.name}の検証が完了しました")
        return True

    def _test_basic_imports(self) -> bool:
        """基本的なインポートをテスト"""
        test_script = f"""
import sys
try:
    from {self.framework.module_name}.QtCore import QCoreApplication, QSettings
    from {self.framework.module_name}.QtWidgets import QApplication, QWidget
    from {self.framework.module_name}.QtGui import QIcon, QPixmap
    print("基本的なインポートが成功しました")
    sys.exit(0)
except ImportError as e:
    print(f"インポートエラー: {{e}}")
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                [sys.executable, "-c", test_script],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            logger.debug(f"インポートテスト結果: {result.stdout.strip()}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 基本的なインポートに失敗しました: {e.stderr}")
            return False

    def _test_gui_functionality(self) -> bool:
        """GUI機能をテスト（ヘッドレス環境対応）"""
        test_script = f"""
import sys
import os

# ヘッドレス環境での実行を設定
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

try:
    from {self.framework.module_name}.QtWidgets import QApplication, QWidget

    # QApplicationの作成テスト
    app = QApplication(sys.argv)

    # 基本的なウィジェットの作成テスト
    widget = QWidget()
    widget.setWindowTitle("テストウィジェット")

    print("GUI機能のテストが成功しました")
    app.quit()
    sys.exit(0)

except Exception as e:
    print(f"GUI機能テストエラー: {{e}}")
    sys.exit(1)
"""

        try:
            result = subprocess.run(
                [sys.executable, "-c", test_script],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            logger.debug(f"GUI機能テスト結果: {result.stdout.strip()}")
            return True

        except subprocess.CalledProcessError as e:
            logger.warning(f"GUI機能テストで問題が発生: {e.stderr}")
            return False


def print_detection_report(frameworks: List[QtFramework]) -> None:
    """検出レポートを表示"""
    logger.info("=" * 60)
    logger.info("Qt フレームワーク検出レポート")
    logger.info("=" * 60)

    available = [fw for fw in frameworks if fw.is_available]
    unavailable = [fw for fw in frameworks if not fw.is_available]

    if available:
        logger.info("✅ 利用可能なフレームワーク:")
        for fw in available:
            logger.info(f"  - {fw.name} {fw.version} (優先度: {fw.priority})")
    else:
        logger.warning("⚠️  利用可能なQt フレームワークが見つかりません")

    if unavailable:
        logger.info("❌ 利用できないフレームワーク:")
        for fw in unavailable:
            logger.info(f"  - {fw.name} (エラー: {fw.import_error})")

    logger.info("=" * 60)


def print_installation_guide(frameworks: List[QtFramework]) -> None:
    """インストールガイドを表示"""
    logger.info("📦 Qt フレームワークインストールガイド")
    logger.info("-" * 40)

    logger.info("推奨インストール順序:")
    for i, fw in enumerate(frameworks, 1):
        package_name = QtInstaller()._get_package_name(fw)
        logger.info(f"  {i}. {fw.name}:")
        logger.info(f"     pip install {package_name}")

    logger.info("")
    logger.info("💡 ヒント:")
    logger.info("  - PySide6が最も推奨されます（公式サポート）")
    logger.info("  - PyQt6は商用利用時にライセンス注意")
    logger.info("  - PyQt5は古いプロジェクトとの互換性用")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="Qt フレームワーク自動検出・設定スクリプト"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="不足しているQt フレームワークを自動インストール",
    )
    parser.add_argument(
        "--framework",
        choices=["PySide6", "PyQt6", "PyQt5"],
        help="特定のフレームワークを指定してインストール",
    )
    parser.add_argument(
        "--validate", action="store_true", help="検出されたフレームワークの動作を検証"
    )
    parser.add_argument("--config", action="store_true", help="Qt設定ファイルを生成")
    parser.add_argument("--verbose", action="store_true", help="詳細なログを表示")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(10)  # DEBUG level

    logger.info("🔍 Qt フレームワーク検出スクリプトを開始します")

    # プロジェクトルートの取得
    project_root = Path(__file__).parent.parent

    # Qt フレームワークの検出
    detector = QtDetector()
    frameworks = detector.detect_all_frameworks()

    # 検出レポートの表示
    print_detection_report(frameworks)

    # 利用可能なフレームワークの確認
    available_frameworks = detector.get_available_frameworks()
    recommended_framework = detector.get_recommended_framework()

    if not available_frameworks:
        logger.warning("⚠️  Qt フレームワークが見つかりません")

        if args.install:
            # 自動インストールを実行
            installer = QtInstaller()
            installation_candidates = detector.get_installation_candidates()

            for framework in installation_candidates:
                logger.info(f"📦 {framework.name}のインストールを試行します...")
                if installer.install_framework(framework):
                    # インストール後に再検出
                    detector._detect_framework(framework)
                    if framework.is_available:
                        logger.info(
                            f"✅ {framework.name}のインストールと検出が完了しました"
                        )
                        recommended_framework = framework
                        break
                else:
                    logger.warning(f"⚠️  {framework.name}のインストールに失敗しました")
        else:
            print_installation_guide(detector.get_installation_candidates())
            logger.info("")
            logger.info(
                "自動インストールを実行するには --install オプションを使用してください"
            )
            sys.exit(1)

    elif args.framework:
        # 特定のフレームワークが指定された場合
        target_framework = next(
            (fw for fw in frameworks if fw.name == args.framework), None
        )

        if not target_framework:
            logger.error(
                f"❌ 指定されたフレームワークが見つかりません: {args.framework}"
            )
            sys.exit(1)

        if not target_framework.is_available and args.install:
            installer = QtInstaller()
            if installer.install_framework(target_framework):
                detector._detect_framework(target_framework)

        recommended_framework = (
            target_framework if target_framework.is_available else None
        )

    if recommended_framework:
        logger.info(
            f"🎯 推奨フレームワーク: {recommended_framework.name} {recommended_framework.version}"
        )

        # 動作検証
        if args.validate:
            validator = QtValidator(recommended_framework)
            if not validator.validate_framework():
                logger.error("❌ フレームワークの検証に失敗しました")
                sys.exit(1)

        # 設定ファイルの生成
        if args.config:
            config_manager = QtConfigurationManager(project_root)
            if not config_manager.create_qt_config_file(recommended_framework):
                logger.error("❌ 設定ファイルの生成に失敗しました")
                sys.exit(1)

        # 環境変数の提案
        config_manager = QtConfigurationManager(project_root)
        env_config = config_manager.generate_environment_config(recommended_framework)

        if env_config:
            logger.info("🔧 推奨環境変数設定:")
            for key, value in env_config.items():
                logger.info(f"  export {key}={value}")

        logger.info("✅ Qt フレームワークの検出・設定が完了しました")

    else:
        logger.error("❌ 利用可能なQt フレームワークが見つかりませんでした")
        sys.exit(1)


if __name__ == "__main__":
    main()
