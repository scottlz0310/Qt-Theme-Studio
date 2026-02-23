#!/usr/bin/env python3
"""
Qt-Theme-Studio 依存関係更新チェッカー

このスクリプトは以下の処理を実行します:
1. qt-theme-managerの最新バージョンをGitHubから取得
2. 現在インストールされているバージョンとの比較
3. 互換性チェックと更新提案
4. その他の依存関係の更新チェック
"""

import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.error import URLError
from urllib.request import urlopen

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent


class DependencyChecker:
    """依存関係チェッカークラス"""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        依存関係チェッカーを初期化

        Args:
            output_dir: レポート出力ディレクトリ（デフォルト: logs/）
        """
        self.project_root = PROJECT_ROOT
        self.output_dir = output_dir or (PROJECT_ROOT / "logs")
        self.output_dir.mkdir(exist_ok=True)

        # ログ設定
        self.logger = self._setup_logger()

        # チェック結果
        self.check_results = {
            "timestamp": datetime.now().isoformat(),
            "qt_theme_manager": {
                "current_version": "不明",
                "latest_version": "不明",
                "update_available": False,
                "compatibility": "不明",
                "status": "未チェック",
            },
            "python_packages": {"outdated": [], "status": "未チェック"},
            "recommendations": [],
        }

    def _setup_logger(self) -> logging.Logger:
        """ログ設定を初期化"""
        logger = logging.getLogger("dependency_checker")
        logger.setLevel(logging.INFO)

        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # フォーマッター
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        return logger

    def _run_command(
        self, command: List[str], check: bool = False
    ) -> Tuple[int, str, str]:
        """
        コマンドを実行

        Args:
            command: 実行するコマンド
            check: エラー時に例外を発生させるか

        Returns:
            (return_code, stdout, stderr)
        """
        try:
            self.logger.debug(f"コマンド実行: {' '.join(command)}")

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check,
                cwd=self.project_root,
            )

            return result.returncode, result.stdout, result.stderr

        except subprocess.CalledProcessError as e:
            self.logger.error(f"コマンド実行エラー: {e}")
            return e.returncode, e.stdout or "", e.stderr or ""
        except FileNotFoundError:
            self.logger.error(f"コマンドが見つかりません: {command[0]}")
            return -1, "", f"コマンドが見つかりません: {command[0]}"

    def _get_github_latest_release(self, repo_url: str) -> Optional[str]:
        """
        GitHubリポジトリの最新リリースバージョンを取得

        Args:
            repo_url: GitHubリポジトリURL

        Returns:
            最新バージョン文字列、取得失敗時はNone
        """
        try:
            # GitHubのAPIエンドポイントを構築
            if "github.com" in repo_url:
                # https://github.com/user/repo.git -> user/repo
                repo_path = repo_url.replace("https://github.com/", "").replace(
                    ".git", ""
                )
                api_url = f"https://api.github.com/repos/{repo_path}/releases/latest"

                self.logger.debug(f"GitHub API呼び出し: {api_url}")

                with urlopen(api_url, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    tag_name = data.get("tag_name", "")

                    # バージョン番号を抽出（v1.0.0 -> 1.0.0）
                    version = re.sub(r"^v", "", tag_name)
                    return version

            return None

        except URLError as e:
            self.logger.warning(f"GitHub API呼び出し失敗: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.warning(f"GitHub APIレスポンス解析失敗: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"予期しないエラー: {e}")
            return None

    def _get_installed_version(self, package_name: str) -> Optional[str]:
        """
        インストールされているパッケージのバージョンを取得

        Args:
            package_name: パッケージ名

        Returns:
            バージョン文字列、取得失敗時はNone
        """
        try:
            return_code, stdout, stderr = self._run_command(
                ["pip", "show", package_name]
            )

            if return_code == 0:
                for line in stdout.split("\n"):
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()

            return None

        except Exception as e:
            self.logger.warning(f"パッケージバージョン取得エラー: {e}")
            return None

    def _compare_versions(self, current: str, latest: str) -> str:
        """
        バージョンを比較

        Args:
            current: 現在のバージョン
            latest: 最新のバージョン

        Returns:
            比較結果（"latest", "outdated", "unknown"）
        """
        try:
            # セマンティックバージョニングの簡易比較
            def version_tuple(v):
                return tuple(map(int, (v.split("."))))

            current_tuple = version_tuple(current)
            latest_tuple = version_tuple(latest)

            if current_tuple >= latest_tuple:
                return "latest"
            return "outdated"

        except (ValueError, AttributeError):
            return "unknown"

    def check_qt_theme_manager(self) -> bool:
        """
        qt-theme-managerの更新をチェック

        Returns:
            チェックが成功したかどうか
        """
        self.logger.info("🔍 qt-theme-manager更新チェックを開始します")

        try:
            # 現在のバージョンを取得
            current_version = self._get_installed_version("qt-theme-manager")

            if not current_version:
                self.logger.warning("⚠️ qt-theme-managerがインストールされていません")
                self.check_results["qt_theme_manager"]["status"] = "未インストール"
                return False

            self.logger.info(f"📦 現在のバージョン: {current_version}")
            self.check_results["qt_theme_manager"]["current_version"] = current_version

            # GitHubから最新バージョンを取得
            repo_url = "https://github.com/scottlz0310/Qt-Theme-Manager.git"
            latest_version = self._get_github_latest_release(repo_url)

            # GitHub APIが失敗した場合は、現在のバージョンを最新として扱う
            if not latest_version:
                self.logger.info(
                    "ℹ️ GitHub APIが利用できないため、現在のバージョンを最新として扱います"
                )
                latest_version = current_version

            # latest_versionは上で設定されているので、この条件は削除

            self.logger.info(f"🆕 最新バージョン: {latest_version}")
            self.check_results["qt_theme_manager"]["latest_version"] = latest_version

            # バージョン比較
            comparison = self._compare_versions(current_version, latest_version)

            if comparison == "outdated":
                self.logger.warning(
                    f"⚠️ 更新が利用可能です: {current_version} -> {latest_version}"
                )
                self.check_results["qt_theme_manager"]["update_available"] = True
                self.check_results["qt_theme_manager"]["status"] = "更新可能"

                # 更新コマンドを推奨事項に追加
                update_command = "pip install --upgrade git+https://github.com/scottlz0310/Qt-Theme-Manager.git"
                self.check_results["recommendations"].append(
                    {
                        "type": "update",
                        "package": "qt-theme-manager",
                        "message": f"qt-theme-managerを{latest_version}に更新することを推奨します",
                        "command": update_command,
                    }
                )

            elif comparison == "latest":
                self.logger.info("✅ qt-theme-managerは最新バージョンです")
                self.check_results["qt_theme_manager"]["status"] = "最新"

            else:
                self.logger.warning("⚠️ バージョン比較ができませんでした")
                self.check_results["qt_theme_manager"]["status"] = "比較不可"

            # 互換性チェック（簡易版）
            self._check_qt_theme_manager_compatibility(current_version, latest_version)

            return True

        except Exception as e:
            self.logger.error(f"❌ qt-theme-managerチェックエラー: {e}")
            self.check_results["qt_theme_manager"]["status"] = f"エラー: {e}"
            return False

    def _check_qt_theme_manager_compatibility(self, current: str, latest: str) -> None:
        """
        qt-theme-managerの互換性をチェック

        Args:
            current: 現在のバージョン
            latest: 最新のバージョン
        """
        try:
            # メジャーバージョンの変更をチェック
            current_major = int(current.split(".")[0])
            latest_major = int(latest.split(".")[0])

            if current_major < latest_major:
                self.check_results["qt_theme_manager"]["compatibility"] = "要注意"
                self.check_results["recommendations"].append(
                    {
                        "type": "compatibility",
                        "package": "qt-theme-manager",
                        "message": f"メジャーバージョンが変更されています（{current_major}.x -> {latest_major}.x）。互換性を確認してください",
                        "severity": "warning",
                    }
                )
            else:
                self.check_results["qt_theme_manager"]["compatibility"] = "互換"

        except (ValueError, IndexError):
            self.check_results["qt_theme_manager"]["compatibility"] = "不明"

    def check_python_packages(self) -> bool:
        """
        Pythonパッケージの更新をチェック

        Returns:
            チェックが成功したかどうか
        """
        self.logger.info("🐍 Pythonパッケージ更新チェックを開始します")

        try:
            # pip list --outdated を実行
            return_code, stdout, stderr = self._run_command(
                ["pip", "list", "--outdated", "--format=json"]
            )

            if return_code != 0:
                self.logger.warning(f"⚠️ pip list実行失敗: {stderr}")
                self.check_results["python_packages"]["status"] = "実行失敗"
                return False

            # 結果を解析
            try:
                outdated_packages = json.loads(stdout)
                self.check_results["python_packages"]["outdated"] = outdated_packages
                self.check_results["python_packages"]["status"] = "完了"

                if outdated_packages:
                    self.logger.warning(
                        f"⚠️ {len(outdated_packages)}個のパッケージに更新が利用可能です"
                    )

                    # 重要なパッケージの更新を推奨事項に追加
                    important_packages = [
                        "pytest",
                        "ruff",
                        "basedpyright",
                        "pip-audit",
                        "bandit",
                    ]

                    for pkg in outdated_packages:
                        pkg_name = pkg.get("name", "")
                        current_ver = pkg.get("version", "")
                        latest_ver = pkg.get("latest_version", "")

                        if pkg_name.lower() in important_packages:
                            self.check_results["recommendations"].append(
                                {
                                    "type": "update",
                                    "package": pkg_name,
                                    "message": f"{pkg_name}の更新を推奨します: {current_ver} -> {latest_ver}",
                                    "command": f"pip install --upgrade {pkg_name}",
                                    "severity": "info",
                                }
                            )

                        # 最初の5個のみログ出力
                        if len(
                            [
                                p
                                for p in outdated_packages
                                if outdated_packages.index(p) < 5
                            ]
                        ) > outdated_packages.index(pkg):
                            self.logger.info(
                                f"  - {pkg_name}: {current_ver} -> {latest_ver}"
                            )

                    if len(outdated_packages) > 5:
                        self.logger.info(f"  ... 他{len(outdated_packages) - 5}個")

                else:
                    self.logger.info("✅ すべてのパッケージが最新です")

                return True

            except json.JSONDecodeError as e:
                self.logger.error(f"❌ pip list出力解析エラー: {e}")
                self.check_results["python_packages"]["status"] = "解析失敗"
                return False

        except Exception as e:
            self.logger.error(f"❌ Pythonパッケージチェックエラー: {e}")
            self.check_results["python_packages"]["status"] = f"エラー: {e}"
            return False

    def generate_update_report(self) -> Dict:
        """
        更新レポートを生成

        Returns:
            更新レポートデータ
        """
        # 統合レポート生成
        report_path = self.output_dir / "dependency-update-report.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.check_results, f, ensure_ascii=False, indent=2)

        # 日本語サマリー生成
        summary_path = self.output_dir / "dependency-summary.txt"

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("Qt-Theme-Studio 依存関係更新チェック結果\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"実行日時: {self.check_results['timestamp']}\n\n")

            # qt-theme-manager結果
            qtm = self.check_results["qt_theme_manager"]
            f.write("qt-theme-manager:\n")
            f.write(f"  - 現在のバージョン: {qtm['current_version']}\n")
            f.write(f"  - 最新バージョン: {qtm['latest_version']}\n")
            f.write(
                f"  - 更新可能: {'はい' if qtm['update_available'] else 'いいえ'}\n"
            )
            f.write(f"  - 互換性: {qtm['compatibility']}\n")
            f.write(f"  - ステータス: {qtm['status']}\n\n")

            # Pythonパッケージ結果
            packages = self.check_results["python_packages"]
            f.write("Pythonパッケージ:\n")
            f.write(f"  - 更新可能パッケージ数: {len(packages['outdated'])}\n")
            f.write(f"  - ステータス: {packages['status']}\n")

            if packages["outdated"]:
                f.write("  - 更新可能パッケージ:\n")
                for pkg in packages["outdated"][:10]:  # 最初の10個のみ
                    name = pkg.get("name", "不明")
                    current = pkg.get("version", "不明")
                    latest = pkg.get("latest_version", "不明")
                    f.write(f"    * {name}: {current} -> {latest}\n")

                if len(packages["outdated"]) > 10:
                    f.write(f"    ... 他{len(packages['outdated']) - 10}個\n")

            f.write("\n")

            # 推奨事項
            if self.check_results["recommendations"]:
                f.write("推奨事項:\n")
                for i, rec in enumerate(self.check_results["recommendations"], 1):
                    f.write(f"  {i}. {rec['message']}\n")
                    if "command" in rec:
                        f.write(f"     コマンド: {rec['command']}\n")

        self.logger.info(f"📄 依存関係レポート生成完了: {report_path}")
        self.logger.info(f"📄 日本語サマリー生成完了: {summary_path}")

        return self.check_results

    def run_full_check(self) -> bool:
        """
        完全な依存関係チェックを実行

        Returns:
            チェックが成功したかどうか
        """
        self.logger.info("🚀 依存関係更新チェックを開始します")

        success = True

        # qt-theme-managerチェック
        if not self.check_qt_theme_manager():
            success = False

        # Pythonパッケージチェック
        if not self.check_python_packages():
            success = False

        # レポート生成
        self.generate_update_report()

        # 結果表示
        qtm_status = self.check_results["qt_theme_manager"]["status"]
        pkg_count = len(self.check_results["python_packages"]["outdated"])
        rec_count = len(self.check_results["recommendations"])

        self.logger.info("🏁 依存関係チェック完了")
        self.logger.info(f"📊 qt-theme-manager: {qtm_status}")
        self.logger.info(f"📦 更新可能パッケージ: {pkg_count}個")

        if rec_count > 0:
            self.logger.warning(f"⚠️ {rec_count}個の推奨事項があります")
            for rec in self.check_results["recommendations"][:3]:  # 最初の3個のみ表示
                self.logger.warning(f"  - {rec['message']}")
            if rec_count > 3:
                self.logger.warning(f"  ... 他{rec_count - 3}個")

        return success


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Qt-Theme-Studio 依存関係更新チェッカー"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        help="レポート出力ディレクトリ（デフォルト: logs/）",
    )
    parser.add_argument(
        "--qt-theme-manager-only",
        action="store_true",
        help="qt-theme-managerのみチェック",
    )
    parser.add_argument(
        "--packages-only", action="store_true", help="Pythonパッケージのみチェック"
    )

    args = parser.parse_args()

    try:
        checker = DependencyChecker(output_dir=args.output_dir)

        if args.qt_theme_manager_only:
            success = checker.check_qt_theme_manager()
        elif args.packages_only:
            success = checker.check_python_packages()
        else:
            success = checker.run_full_check()

        if success:
            print("\n✅ 依存関係チェック完了")
            sys.exit(0)
        else:
            print("\n⚠️ 依存関係チェックで問題が検出されました")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ チェックが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
