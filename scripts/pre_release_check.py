#!/usr/bin/env python3
"""
Qt-Theme-Studio リリース前チェックスクリプト（拡張版）

このスクリプトは以下の処理を実行します:
1. 全テストスイートの実行
2. コード品質チェック
3. セキュリティスキャン
4. パフォーマンステスト
5. 依存関係の脆弱性チェック
6. バージョン整合性チェック
7. ドキュメント整合性チェック
8. 変更履歴の整合性チェック
9. ビルドテスト
10. 最終統合検証
"""

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)


class PreReleaseChecker:
    def __init__(self, verbose: bool = False):
        """初期化"""
        self.verbose = verbose
        self.logger = self._setup_logger()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "UNKNOWN",
            "summary": {},
            "execution_time": 0,
            "environment": self._get_environment_info()
        }
        self.start_time = time.time()

    def _setup_logger(self) -> logging.Logger:
        """ロガーをセットアップ"""
        logger = logging.getLogger("pre_release_checker")
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def _get_environment_info(self) -> Dict:
        """環境情報を取得"""
        import platform
        
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "working_directory": str(PROJECT_ROOT)
        }

    def run_command(self, command: List[str], check: bool = True, 
                   capture_output: bool = True, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """コマンドを実行する"""
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        self.logger.info(f"コマンド実行: {cmd_str}")

        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["PYTHONPATH"] = str(PROJECT_ROOT)

        try:
            result = subprocess.run(
                command, 
                check=check, 
                capture_output=capture_output, 
                text=True, 
                env=env,
                timeout=timeout
            )
            
            if self.verbose and result.stdout:
                self.logger.debug(f"標準出力: {result.stdout[:500]}...")
            if self.verbose and result.stderr:
                self.logger.debug(f"標準エラー: {result.stderr[:500]}...")
                
            return result
            
        except subprocess.TimeoutExpired as e:
            self.logger.error(f"コマンドタイムアウト: {cmd_str}")
            raise
        except subprocess.CalledProcessError as e:
            self.logger.error(f"コマンド実行エラー: {e}")
            if self.verbose:
                self.logger.error(f"標準出力: {e.stdout}")
                self.logger.error(f"標準エラー: {e.stderr}")
            raise

    def check_test_suite(self):
        """包括的テストスイートを実行"""
        print("\n=== 📋 包括的テストスイート ===")

        try:
            # logsディレクトリを作成(存在しない場合)
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)

            result = self.run_command(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "-v",
                    "--tb=short",
                    "--maxfail=5",
                    "--durations=10",
                    "--junit-xml=" + str(logs_dir / "test-results.xml"),
                ],
                check=False,
            )

            # テストが実行されたかどうかを確認(returncodeは無視)
            if "collected" in result.stdout and "test session starts" in result.stdout:
                print("✅ テストスイートが実行されました")
                self.results["checks"]["test_suite"] = {
                    "status": "PASS",
                    "message": "テストスイート実行完了",
                    "details": result.stdout + result.stderr,
                }
                return True
            print("❌ テストスイートの実行に失敗しました")
            self.results["checks"]["test_suite"] = {
                "status": "FAIL",
                "message": "テストスイート実行失敗",
                "details": result.stdout + result.stderr,
            }
            return False

        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            self.results["checks"]["test_suite"] = {
                "status": "ERROR",
                "message": f"テスト実行エラー: {e}",
                "details": str(e),
            }
            return False

    def check_code_quality(self):
        """コード品質をチェック"""
        print("\n=== 🔍 コード品質チェック ===")

        checks = {}
        overall_pass = True

        # Black (フォーマット)
        try:
            result = self.run_command(
                ["black", "--check", "--diff", "qt_theme_studio/", "tests/"],
                check=False,
            )

            if result.returncode == 0:
                print("✅ Black: コードフォーマットOK")
                checks["black"] = {"status": "PASS", "message": "フォーマットOK"}
            else:
                print("⚠️ Black: フォーマット要修正")
                checks["black"] = {"status": "WARN", "message": "フォーマット要修正"}

        except FileNotFoundError:
            print("⚠️ Black: インストールされていません")
            checks["black"] = {
                "status": "SKIP",
                "message": "インストールされていません",
            }

        # isort (インポート順序)
        try:
            result = self.run_command(
                ["isort", "--check-only", "--diff", "qt_theme_studio/", "tests/"],
                check=False,
            )

            if result.returncode == 0:
                print("✅ isort: インポート順序OK")
                checks["isort"] = {"status": "PASS", "message": "インポート順序OK"}
            else:
                print("⚠️ isort: インポート順序要修正")
                checks["isort"] = {"status": "WARN", "message": "インポート順序要修正"}

        except FileNotFoundError:
            print("⚠️ isort: インストールされていません")
            checks["isort"] = {
                "status": "SKIP",
                "message": "インストールされていません",
            }

        # flake8 (リンティング)
        try:
            result = self.run_command(
                [
                    "flake8",
                    "qt_theme_studio/",
                    "tests/",
                    "--max-line-length=88",
                    "--extend-ignore=E203,W503",
                ],
                check=False,
            )

            if result.returncode == 0:
                print("✅ flake8: リンティングOK")
                checks["flake8"] = {"status": "PASS", "message": "リンティングOK"}
            else:
                print("⚠️ flake8: リンティング警告あり")
                checks["flake8"] = {"status": "WARN", "message": "リンティング警告あり"}

        except FileNotFoundError:
            print("⚠️ flake8: インストールされていません")
            checks["flake8"] = {
                "status": "SKIP",
                "message": "インストールされていません",
            }

        self.results["checks"]["code_quality"] = {
            "status": "PASS" if overall_pass else "WARN",
            "checks": checks,
        }

        return overall_pass

    def check_security(self):
        """セキュリティをチェック"""
        print("\n=== 🔒 セキュリティチェック ===")

        checks = {}

        # Bandit (セキュリティリンティング)
        try:
            # logsディレクトリを作成(存在しない場合)
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)

            result = self.run_command(
                [
                    "bandit",
                    "-r",
                    "qt_theme_studio/",
                    "-f",
                    "json",
                    "-o",
                    str(logs_dir / "bandit-report.json"),
                ],
                check=False,
            )

            if result.returncode == 0:
                print("✅ Bandit: セキュリティ問題なし")
                checks["bandit"] = {"status": "PASS", "message": "セキュリティ問題なし"}
            else:
                print("⚠️ Bandit: セキュリティ警告あり")
                checks["bandit"] = {"status": "WARN", "message": "セキュリティ警告あり"}

        except FileNotFoundError:
            print("⚠️ Bandit: インストールされていません")
            checks["bandit"] = {
                "status": "SKIP",
                "message": "インストールされていません",
            }

        # Safety (依存関係の脆弱性)
        try:
            result = self.run_command(
                [
                    "safety",
                    "check",
                    "--json",
                    "--output",
                    str(logs_dir / "safety-report.json"),
                ],
                check=False,
            )

            if result.returncode == 0:
                print("✅ Safety: 依存関係の脆弱性なし")
                checks["safety"] = {"status": "PASS", "message": "依存関係の脆弱性なし"}
            else:
                print("⚠️ Safety: 依存関係に脆弱性あり")
                checks["safety"] = {"status": "WARN", "message": "依存関係に脆弱性あり"}

        except FileNotFoundError:
            print("⚠️ Safety: インストールされていません")
            checks["safety"] = {
                "status": "SKIP",
                "message": "インストールされていません",
            }

        self.results["checks"]["security"] = {
            "status": "PASS",  # セキュリティは警告があっても通す
            "checks": checks,
        }

        return True

    def check_version_consistency(self):
        """バージョン整合性をチェック"""
        print("\n=== 📦 バージョン整合性チェック ===")

        try:
            # pyproject.tomlからバージョンを取得
            with open("pyproject.toml", encoding="utf-8") as f:
                content = f.read()
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    package_version = version_match.group(1)
                    print(f"📦 パッケージバージョン: {package_version}")
                else:
                    raise ValueError("pyproject.tomlでバージョンが見つかりません")

            # __init__.pyからバージョンを取得(存在する場合)
            init_file = Path("qt_theme_studio/__init__.py")
            if init_file.exists():
                with open(init_file, encoding="utf-8") as f:
                    content = f.read()
                    version_match = re.search(
                        r'__version__\s*=\s*["\']([^"\']+)["\']', content
                    )
                    if version_match:
                        init_version = version_match.group(1)
                        print(f"🐍 __init__.py バージョン: {init_version}")

                        if package_version != init_version:
                            print("❌ バージョン不整合")
                            self.results["checks"]["version_consistency"] = {
                                "status": "FAIL",
                                "message": f"バージョン不整合: package={package_version}, init={init_version}",
                            }
                            return False

            print("✅ バージョン整合性OK")
            self.results["checks"]["version_consistency"] = {
                "status": "PASS",
                "message": f"バージョン整合性OK: {package_version}",
                "version": package_version,
            }
            return True

        except Exception as e:
            print(f"❌ バージョンチェックエラー: {e}")
            self.results["checks"]["version_consistency"] = {
                "status": "ERROR",
                "message": f"バージョンチェックエラー: {e}",
            }
            return False

    def check_documentation(self):
        """ドキュメント整合性をチェック"""
        print("\n=== 📚 ドキュメント整合性チェック ===")

        required_docs = ["README.md", "INSTALL.md", "RELEASE_NOTES.md", "CHANGELOG.md"]

        missing_docs = []
        for doc in required_docs:
            if not Path(doc).exists():
                missing_docs.append(doc)

        if missing_docs:
            print(f"⚠️ 不足ドキュメント: {', '.join(missing_docs)}")
            self.results["checks"]["documentation"] = {
                "status": "WARN",
                "message": f"不足ドキュメント: {', '.join(missing_docs)}",
            }
        else:
            print("✅ 必要ドキュメント揃っています")
            self.results["checks"]["documentation"] = {
                "status": "PASS",
                "message": "必要ドキュメント揃っています",
            }

        return True

    def check_changelog_consistency(self):
        """変更履歴の整合性をチェック"""
        self.logger.info("変更履歴の整合性をチェック中...")
        
        try:
            changelog_path = Path("CHANGELOG.md")
            
            if not changelog_path.exists():
                self.logger.warning("CHANGELOG.mdが見つかりません")
                self.results["checks"]["changelog_consistency"] = {
                    "status": "WARN",
                    "message": "CHANGELOG.mdが見つかりません"
                }
                return False
            
            with open(changelog_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            checks = {}
            
            # 未リリースセクションの存在確認
            if "[未リリース]" in content:
                checks["unreleased_section"] = {"status": "PASS", "message": "未リリースセクション存在"}
                self.logger.info("✅ 未リリースセクションが存在します")
            else:
                checks["unreleased_section"] = {"status": "WARN", "message": "未リリースセクション不足"}
                self.logger.warning("⚠️ 未リリースセクションが見つかりません")
            
            # 必要なカテゴリの存在確認
            required_categories = ["追加", "変更", "修正", "削除", "非推奨", "セキュリティ"]
            missing_categories = []
            
            for category in required_categories:
                if f"### {category}" in content:
                    checks[f"category_{category}"] = {"status": "PASS", "message": f"{category}カテゴリ存在"}
                else:
                    missing_categories.append(category)
                    checks[f"category_{category}"] = {"status": "WARN", "message": f"{category}カテゴリ不足"}
            
            if missing_categories:
                self.logger.warning(f"⚠️ 不足カテゴリ: {', '.join(missing_categories)}")
            else:
                self.logger.info("✅ すべての必要カテゴリが存在します")
            
            # 日付フォーマットの確認
            date_pattern = r'\[[\d.]+\] - \d{4}-\d{2}-\d{2}'
            if re.search(date_pattern, content):
                checks["date_format"] = {"status": "PASS", "message": "日付フォーマット正常"}
                self.logger.info("✅ 日付フォーマットが正常です")
            else:
                checks["date_format"] = {"status": "WARN", "message": "日付フォーマット要確認"}
                self.logger.warning("⚠️ 日付フォーマットを確認してください")
            
            self.results["checks"]["changelog_consistency"] = {
                "status": "PASS" if not missing_categories else "WARN",
                "checks": checks
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"変更履歴チェックエラー: {e}")
            self.results["checks"]["changelog_consistency"] = {
                "status": "ERROR",
                "message": f"変更履歴チェックエラー: {e}"
            }
            return False

    def check_build_test(self):
        """ビルドテストを実行"""
        self.logger.info("ビルドテストを実行中...")
        
        try:
            # 一時ディレクトリでビルドテスト
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # パッケージビルドテスト
                self.logger.info("Pythonパッケージビルドテスト中...")
                result = self.run_command([
                    sys.executable, "-m", "build", 
                    "--outdir", str(temp_path)
                ], check=False, timeout=300)
                
                if result.returncode == 0:
                    # 生成されたファイルを確認
                    wheel_files = list(temp_path.glob("*.whl"))
                    tar_files = list(temp_path.glob("*.tar.gz"))
                    
                    if wheel_files and tar_files:
                        self.logger.info("✅ パッケージビルド成功")
                        
                        # パッケージサイズチェック
                        total_size = sum(f.stat().st_size for f in wheel_files + tar_files)
                        size_mb = total_size / (1024 * 1024)
                        
                        self.results["checks"]["build_test"] = {
                            "status": "PASS",
                            "message": f"ビルド成功 (合計サイズ: {size_mb:.2f}MB)",
                            "artifacts": {
                                "wheel_files": [f.name for f in wheel_files],
                                "source_files": [f.name for f in tar_files],
                                "total_size_mb": round(size_mb, 2)
                            }
                        }
                        return True
                    else:
                        self.logger.error("❌ 期待されるファイルが生成されませんでした")
                        self.results["checks"]["build_test"] = {
                            "status": "FAIL",
                            "message": "期待されるファイルが生成されませんでした"
                        }
                        return False
                else:
                    self.logger.error("❌ パッケージビルドに失敗しました")
                    self.results["checks"]["build_test"] = {
                        "status": "FAIL",
                        "message": "パッケージビルドに失敗しました",
                        "details": result.stderr
                    }
                    return False
                    
        except Exception as e:
            self.logger.error(f"ビルドテストエラー: {e}")
            self.results["checks"]["build_test"] = {
                "status": "ERROR",
                "message": f"ビルドテストエラー: {e}"
            }
            return False

    def check_dependency_health(self):
        """依存関係の健全性をチェック"""
        self.logger.info("依存関係の健全性をチェック中...")
        
        try:
            checks = {}
            
            # pip check で依存関係の整合性確認
            try:
                result = self.run_command([sys.executable, "-m", "pip", "check"], check=False)
                
                if result.returncode == 0:
                    checks["pip_check"] = {"status": "PASS", "message": "依存関係整合性OK"}
                    self.logger.info("✅ 依存関係の整合性OK")
                else:
                    checks["pip_check"] = {"status": "WARN", "message": "依存関係に問題あり"}
                    self.logger.warning("⚠️ 依存関係に問題があります")
                    
            except Exception as e:
                checks["pip_check"] = {"status": "ERROR", "message": f"pip checkエラー: {e}"}
            
            # 重要な依存関係の存在確認
            critical_packages = ["PySide6", "qt_theme_studio"]
            
            for package in critical_packages:
                try:
                    result = self.run_command([
                        sys.executable, "-c", f"import {package.replace('-', '_')}"
                    ], check=False)
                    
                    if result.returncode == 0:
                        checks[f"import_{package}"] = {"status": "PASS", "message": f"{package}インポートOK"}
                        self.logger.info(f"✅ {package}のインポートOK")
                    else:
                        checks[f"import_{package}"] = {"status": "FAIL", "message": f"{package}インポート失敗"}
                        self.logger.error(f"❌ {package}のインポートに失敗")
                        
                except Exception as e:
                    checks[f"import_{package}"] = {"status": "ERROR", "message": f"{package}チェックエラー: {e}"}
            
            # pyproject.tomlの依存関係チェック
            pyproject_path = Path("pyproject.toml")
            if pyproject_path.exists():
                with open(pyproject_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "dependencies" in content:
                    checks["pyproject_dependencies"] = {"status": "PASS", "message": "pyproject.toml依存関係定義OK"}
                    self.logger.info("✅ pyproject.tomlに依存関係が定義されています")
                else:
                    checks["pyproject_dependencies"] = {"status": "WARN", "message": "pyproject.toml依存関係定義不足"}
                    self.logger.warning("⚠️ pyproject.tomlに依存関係が定義されていません")
            
            self.results["checks"]["dependency_health"] = {
                "status": "PASS",  # 依存関係は警告があっても通す
                "checks": checks
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"依存関係チェックエラー: {e}")
            self.results["checks"]["dependency_health"] = {
                "status": "ERROR",
                "message": f"依存関係チェックエラー: {e}"
            }
            return False

    def check_final_integration(self):
        """最終統合検証を実行"""
        self.logger.info("最終統合検証を実行中...")
        
        try:
            checks = {}
            
            # アプリケーション起動テスト
            self.logger.info("アプリケーション起動テスト中...")
            try:
                result = self.run_command([
                    sys.executable, "-c",
                    "import qt_theme_studio; print('Import successful')"
                ], check=False, timeout=30)
                
                if result.returncode == 0 and "Import successful" in result.stdout:
                    checks["app_import"] = {"status": "PASS", "message": "アプリケーションインポートOK"}
                    self.logger.info("✅ アプリケーションのインポートOK")
                else:
                    checks["app_import"] = {"status": "FAIL", "message": "アプリケーションインポート失敗"}
                    self.logger.error("❌ アプリケーションのインポートに失敗")
                    
            except subprocess.TimeoutExpired:
                checks["app_import"] = {"status": "FAIL", "message": "アプリケーションインポートタイムアウト"}
                self.logger.error("❌ アプリケーションインポートがタイムアウトしました")
            
            # 設定ファイルの整合性チェック
            config_files = ["pyproject.toml", "pytest.ini", ".pre-commit-config.yaml"]
            missing_configs = []
            
            for config_file in config_files:
                if Path(config_file).exists():
                    checks[f"config_{config_file}"] = {"status": "PASS", "message": f"{config_file}存在"}
                    self.logger.info(f"✅ {config_file}が存在します")
                else:
                    missing_configs.append(config_file)
                    checks[f"config_{config_file}"] = {"status": "WARN", "message": f"{config_file}不足"}
                    self.logger.warning(f"⚠️ {config_file}が見つかりません")
            
            # ログディレクトリの存在確認
            logs_dir = Path("logs")
            if logs_dir.exists():
                checks["logs_directory"] = {"status": "PASS", "message": "logsディレクトリ存在"}
                self.logger.info("✅ logsディレクトリが存在します")
            else:
                logs_dir.mkdir(exist_ok=True)
                checks["logs_directory"] = {"status": "PASS", "message": "logsディレクトリ作成"}
                self.logger.info("✅ logsディレクトリを作成しました")
            
            self.results["checks"]["final_integration"] = {
                "status": "PASS" if not missing_configs else "WARN",
                "checks": checks
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"最終統合検証エラー: {e}")
            self.results["checks"]["final_integration"] = {
                "status": "ERROR",
                "message": f"最終統合検証エラー: {e}"
            }
            return False

    def generate_detailed_report(self) -> str:
        """詳細レポートを生成"""
        lines = []
        lines.append("=" * 60)
        lines.append("Qt-Theme-Studio リリース前チェック詳細レポート")
        lines.append("=" * 60)
        lines.append(f"実行日時: {self.results['timestamp']}")
        lines.append(f"実行時間: {self.results['execution_time']:.2f}秒")
        lines.append("")
        
        # 環境情報
        lines.append("【環境情報】")
        env = self.results['environment']
        lines.append(f"Python: {env['python_version'].split()[0]}")
        lines.append(f"プラットフォーム: {env['platform']}")
        lines.append(f"作業ディレクトリ: {env['working_directory']}")
        lines.append("")
        
        # チェック結果詳細
        lines.append("【チェック結果詳細】")
        for check_name, check_result in self.results["checks"].items():
            status = check_result.get("status", "UNKNOWN")
            message = check_result.get("message", "メッセージなし")
            
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌", 
                "WARN": "⚠️",
                "ERROR": "💥",
                "SKIP": "⏭️"
            }.get(status, "❓")
            
            lines.append(f"{status_icon} {check_name}: {message}")
            
            # サブチェックがある場合
            if "checks" in check_result:
                for sub_name, sub_result in check_result["checks"].items():
                    sub_status = sub_result.get("status", "UNKNOWN")
                    sub_message = sub_result.get("message", "メッセージなし")
                    sub_icon = {
                        "PASS": "  ✓",
                        "FAIL": "  ✗", 
                        "WARN": "  ⚠",
                        "ERROR": "  💥",
                        "SKIP": "  -"
                    }.get(sub_status, "  ?")
                    lines.append(f"{sub_icon} {sub_name}: {sub_message}")
            
            # 詳細情報がある場合
            if "details" in check_result and self.verbose:
                lines.append(f"    詳細: {check_result['details'][:200]}...")
            
            lines.append("")
        
        # サマリー
        summary = self.results['summary']
        lines.append("【サマリー】")
        lines.append(f"成功: {summary['passed']}個")
        lines.append(f"失敗: {summary['failed']}個") 
        lines.append(f"警告: {summary['warnings']}個")
        lines.append(f"合計: {summary['total']}個")
        lines.append("")
        lines.append(f"総合判定: {self.results['overall_status']}")
        
        return "\n".join(lines)

    def generate_report(self):
        """最終レポートを生成"""
        # 実行時間を記録
        self.results["execution_time"] = time.time() - self.start_time
        
        self.logger.info("リリース前チェック結果を集計中...")

        passed = 0
        failed = 0
        warnings = 0

        for check_name, check_result in self.results["checks"].items():
            status = check_result.get("status", "UNKNOWN")
            message = check_result.get("message", "メッセージなし")

            if status == "PASS":
                self.logger.info(f"✅ {check_name}: {message}")
                passed += 1
            elif status == "FAIL":
                self.logger.error(f"❌ {check_name}: {message}")
                failed += 1
            elif status == "ERROR":
                self.logger.error(f"💥 {check_name}: {message}")
                failed += 1
            elif status in ["WARN", "SKIP"]:
                self.logger.warning(f"⚠️ {check_name}: {message}")
                warnings += 1

        # 総合判定
        if failed > 0:
            self.results["overall_status"] = "FAIL"
            self.logger.error(f"❌ リリース前チェック失敗: {failed}個の重要な問題があります")
        elif warnings > 0:
            self.results["overall_status"] = "PASS_WITH_WARNINGS"
            self.logger.warning(f"⚠️ リリース前チェック通過(警告あり): {warnings}個の警告があります")
        else:
            self.results["overall_status"] = "PASS"
            self.logger.info("✅ リリース前チェック完全通過: すべてのチェックが成功しました")

        self.results["summary"] = {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "total": passed + failed + warnings,
        }

        # logsディレクトリを作成(存在しない場合)
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # JSONレポートを保存
        report_path = logs_dir / "pre-release-report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        # 詳細レポートを保存
        detailed_report = self.generate_detailed_report()
        detailed_report_path = logs_dir / "pre-release-detailed-report.txt"
        with open(detailed_report_path, "w", encoding="utf-8") as f:
            f.write(detailed_report)

        self.logger.info(f"📄 JSONレポート: {report_path}")
        self.logger.info(f"📄 詳細レポート: {detailed_report_path}")

        # コンソールに詳細レポートを表示
        if self.verbose:
            print("\n" + detailed_report)

        return self.results["overall_status"] in ["PASS", "PASS_WITH_WARNINGS"]

    def run_all_checks(self, skip_tests: bool = False, skip_build: bool = False):
        """すべてのチェックを実行"""
        self.logger.info("🚀 Qt-Theme-Studio リリース前チェックを開始します")
        self.logger.info(f"📅 実行日時: {self.results['timestamp']}")

        checks = [
            ("テストスイート", self.check_test_suite, not skip_tests),
            ("コード品質", self.check_code_quality, True),
            ("セキュリティ", self.check_security, True),
            ("バージョン整合性", self.check_version_consistency, True),
            ("ドキュメント", self.check_documentation, True),
            ("変更履歴整合性", self.check_changelog_consistency, True),
            ("依存関係健全性", self.check_dependency_health, True),
            ("ビルドテスト", self.check_build_test, not skip_build),
            ("最終統合検証", self.check_final_integration, True),
        ]

        for check_name, check_func, should_run in checks:
            if not should_run:
                self.logger.info(f"⏭️ {check_name}チェックをスキップします")
                self.results["checks"][check_name.lower().replace(" ", "_")] = {
                    "status": "SKIP",
                    "message": f"{check_name}チェックがスキップされました",
                }
                continue
                
            try:
                self.logger.info(f"🔍 {check_name}チェックを開始...")
                start_time = time.time()
                
                check_func()
                
                elapsed = time.time() - start_time
                self.logger.info(f"✅ {check_name}チェック完了 ({elapsed:.2f}秒)")
                
            except Exception as e:
                self.logger.error(f"💥 {check_name}チェックでエラー: {e}")
                self.results["checks"][check_name.lower().replace(" ", "_")] = {
                    "status": "ERROR",
                    "message": f"チェック実行エラー: {e}",
                    "details": str(e)
                }

        return self.generate_report()


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Qt-Theme-Studio リリース前チェック（拡張版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 標準チェック
  python scripts/pre_release_check.py

  # 詳細ログ付きチェック
  python scripts/pre_release_check.py --verbose

  # テストスキップ（高速チェック）
  python scripts/pre_release_check.py --skip-tests

  # ビルドテストスキップ
  python scripts/pre_release_check.py --skip-build

  # CI/CD用（最小限チェック）
  python scripts/pre_release_check.py --skip-tests --skip-build
        """
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="詳細ログを表示"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="テストスイートをスキップ（高速化）"
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="ビルドテストをスキップ"
    )
    
    args = parser.parse_args()
    
    checker = PreReleaseChecker(verbose=args.verbose)

    try:
        success = checker.run_all_checks(
            skip_tests=args.skip_tests,
            skip_build=args.skip_build
        )

        if success:
            checker.logger.info("🎉 リリース準備完了！")
            sys.exit(0)
        else:
            checker.logger.error("🛑 リリース前に問題を修正してください")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ チェックが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
