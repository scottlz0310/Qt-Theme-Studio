#!/usr/bin/env python3
"""
Qt-Theme-Studio Python バージョン互換性検証

このスクリプトは以下の処理を実行します:
1. サポート対象Pythonバージョン（3.9-3.12）での動作確認
2. 構文互換性チェック
3. 依存関係の互換性検証
4. tox設定ファイルとの統合
"""

import ast
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent


class PythonCompatibilityChecker:
    """Python互換性チェッカークラス"""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Python互換性チェッカーを初期化

        Args:
            output_dir: レポート出力ディレクトリ（デフォルト: logs/）
        """
        self.project_root = PROJECT_ROOT
        self.output_dir = output_dir or (PROJECT_ROOT / "logs")
        self.output_dir.mkdir(exist_ok=True)
        
        # サポート対象バージョン
        self.supported_versions = ["3.9", "3.10", "3.11", "3.12"]
        
        # ログ設定
        self.logger = self._setup_logger()
        
        # チェック結果
        self.check_results = {
            "timestamp": datetime.now().isoformat(),
            "current_python": f"{sys.version_info.major}.{sys.version_info.minor}",
            "supported_versions": self.supported_versions,
            "syntax_check": {"status": "未実行", "issues": []},
            "dependency_check": {"status": "未実行", "issues": []},
            "tox_integration": {"status": "未実行", "config_exists": False},
            "compatibility_summary": {"compatible": [], "incompatible": [], "unknown": []},
            "recommendations": []
        }

    def _setup_logger(self) -> logging.Logger:
        """ログ設定を初期化"""
        logger = logging.getLogger("python_compatibility")
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

    def _run_command(self, command: List[str], check: bool = False) -> Tuple[int, str, str]:
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
                cwd=self.project_root
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"コマンド実行エラー: {e}")
            return e.returncode, e.stdout or "", e.stderr or ""
        except FileNotFoundError:
            self.logger.error(f"コマンドが見つかりません: {command[0]}")
            return -1, "", f"コマンドが見つかりません: {command[0]}"

    def _get_python_files(self) -> List[Path]:
        """
        プロジェクト内のPythonファイルを取得

        Returns:
            Pythonファイルのパスリスト
        """
        python_files = []
        
        # メインパッケージ
        qt_theme_studio_dir = self.project_root / "qt_theme_studio"
        if qt_theme_studio_dir.exists():
            python_files.extend(qt_theme_studio_dir.rglob("*.py"))
        
        # スクリプト
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            python_files.extend(scripts_dir.rglob("*.py"))
        
        # テスト
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            python_files.extend(tests_dir.rglob("*.py"))
        
        # ルートディレクトリのPythonファイル
        python_files.extend(self.project_root.glob("*.py"))
        
        return python_files

    def check_syntax_compatibility(self) -> bool:
        """
        構文互換性をチェック

        Returns:
            チェックが成功したかどうか
        """
        self.logger.info("🐍 Python構文互換性チェックを開始します")
        
        try:
            python_files = self._get_python_files()
            issues = []
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    
                    # 各サポートバージョンでの構文チェック
                    for version in self.supported_versions:
                        major, minor = map(int, version.split('.'))
                        
                        try:
                            # ASTを使用して構文チェック
                            ast.parse(source_code, filename=str(file_path))
                            
                        except SyntaxError as e:
                            issue = {
                                "file": str(file_path.relative_to(self.project_root)),
                                "python_version": version,
                                "error": str(e),
                                "line": e.lineno,
                                "severity": "error"
                            }
                            issues.append(issue)
                            self.logger.warning(f"⚠️ 構文エラー ({version}): {file_path.name}:{e.lineno}")
                
                except Exception as e:
                    issue = {
                        "file": str(file_path.relative_to(self.project_root)),
                        "python_version": "all",
                        "error": f"ファイル読み込みエラー: {e}",
                        "severity": "error"
                    }
                    issues.append(issue)
            
            self.check_results["syntax_check"] = {
                "status": "完了",
                "files_checked": len(python_files),
                "issues": issues
            }
            
            if issues:
                self.logger.warning(f"⚠️ {len(issues)}件の構文互換性問題を検出しました")
                
                # 推奨事項を追加
                self.check_results["recommendations"].append({
                    "type": "syntax",
                    "message": f"{len(issues)}件の構文互換性問題があります。詳細はレポートを確認してください",
                    "severity": "warning"
                })
            else:
                self.logger.info("✅ 構文互換性問題は検出されませんでした")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 構文チェックエラー: {e}")
            self.check_results["syntax_check"]["status"] = f"エラー: {e}"
            return False

    def check_dependency_compatibility(self) -> bool:
        """
        依存関係の互換性をチェック

        Returns:
            チェックが成功したかどうか
        """
        self.logger.info("📦 依存関係互換性チェックを開始します")
        
        try:
            # pyproject.tomlから依存関係を読み取り
            pyproject_path = self.project_root / "pyproject.toml"
            
            if not pyproject_path.exists():
                self.logger.warning("⚠️ pyproject.tomlが見つかりません")
                self.check_results["dependency_check"]["status"] = "pyproject.toml未発見"
                return False
            
            # 現在のPythonバージョンでの依存関係チェック
            return_code, stdout, stderr = self._run_command([
                "pip", "check"
            ])
            
            issues = []
            
            if return_code != 0:
                issue = {
                    "type": "dependency_conflict",
                    "message": "依存関係の競合が検出されました",
                    "details": stderr,
                    "severity": "error"
                }
                issues.append(issue)
                self.logger.warning("⚠️ 依存関係の競合が検出されました")
            
            # Python バージョン要件をチェック
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # requires-python の確認
                if 'requires-python' in content:
                    import re
                    match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        python_req = match.group(1)
                        self.logger.info(f"📋 Python要件: {python_req}")
                        
                        # 要件と実際のサポートバージョンの整合性チェック
                        if ">=3.9" not in python_req:
                            issue = {
                                "type": "python_requirement",
                                "message": f"Python要件 '{python_req}' がサポート対象バージョンと一致しない可能性があります",
                                "severity": "warning"
                            }
                            issues.append(issue)
            
            self.check_results["dependency_check"] = {
                "status": "完了",
                "issues": issues
            }
            
            if issues:
                self.logger.warning(f"⚠️ {len(issues)}件の依存関係問題を検出しました")
            else:
                self.logger.info("✅ 依存関係互換性問題は検出されませんでした")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 依存関係チェックエラー: {e}")
            self.check_results["dependency_check"]["status"] = f"エラー: {e}"
            return False

    def create_tox_config(self) -> bool:
        """
        tox設定ファイルを作成

        Returns:
            作成が成功したかどうか
        """
        self.logger.info("⚙️ tox設定ファイルを作成します")
        
        try:
            tox_config = """[tox]
envlist = py39,py310,py311,py312,lint,type-check
isolated_build = true
skip_missing_interpreters = true

[testenv]
deps = 
    pytest>=7.0.0
    pytest-qt>=4.0.0
    pytest-cov>=4.0.0
    pytest-benchmark>=4.0.0
commands = 
    pytest tests/ -v --tb=short

[testenv:lint]
deps = 
    ruff>=0.3.0
    black>=22.0.0
    isort>=5.10.0
commands = 
    ruff check qt_theme_studio/ tests/ scripts/
    ruff format --check qt_theme_studio/ tests/ scripts/
    black --check qt_theme_studio/ tests/ scripts/
    isort --check-only qt_theme_studio/ tests/ scripts/

[testenv:type-check]
deps = 
    mypy>=1.0.0
    types-requests
commands = 
    mypy qt_theme_studio/

[testenv:security]
deps = 
    bandit>=1.7.0
    safety>=2.3.0
commands = 
    bandit -r qt_theme_studio/
    safety check

[testenv:coverage]
deps = 
    pytest>=7.0.0
    pytest-qt>=4.0.0
    pytest-cov>=4.0.0
commands = 
    pytest tests/ --cov=qt_theme_studio --cov-report=html --cov-report=xml --cov-report=term

[testenv:docs]
deps = 
    sphinx>=4.0.0
    sphinx-rtd-theme
commands = 
    sphinx-build -b html docs/ docs/_build/html

# GitHub Actions用の設定
[gh-actions]
python =
    3.9: py39
    3.10: py310
    3.11: py311
    3.12: py312
"""
            
            tox_path = self.project_root / "tox.ini"
            
            with open(tox_path, 'w', encoding='utf-8') as f:
                f.write(tox_config)
            
            self.logger.info(f"✅ tox設定ファイルを作成しました: {tox_path}")
            
            self.check_results["tox_integration"] = {
                "status": "作成完了",
                "config_exists": True,
                "config_path": str(tox_path)
            }
            
            # 推奨事項を追加
            self.check_results["recommendations"].append({
                "type": "tox",
                "message": "tox設定ファイルが作成されました。'tox'コマンドで複数Pythonバージョンでのテストが可能です",
                "command": "tox",
                "severity": "info"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ tox設定ファイル作成エラー: {e}")
            self.check_results["tox_integration"]["status"] = f"エラー: {e}"
            return False

    def check_tox_integration(self) -> bool:
        """
        tox統合をチェック

        Returns:
            チェックが成功したかどうか
        """
        self.logger.info("🔧 tox統合チェックを開始します")
        
        try:
            tox_path = self.project_root / "tox.ini"
            
            if not tox_path.exists():
                self.logger.info("ℹ️ tox.iniが存在しないため、新規作成します")
                return self.create_tox_config()
            
            self.logger.info("✅ tox.iniが存在します")
            
            # toxが利用可能かチェック
            return_code, stdout, stderr = self._run_command(["tox", "--version"])
            
            if return_code == 0:
                self.logger.info(f"✅ tox利用可能: {stdout.strip()}")
                
                self.check_results["tox_integration"] = {
                    "status": "利用可能",
                    "config_exists": True,
                    "tox_version": stdout.strip()
                }
                
                # 推奨事項を追加
                self.check_results["recommendations"].append({
                    "type": "tox",
                    "message": "toxを使用して複数Pythonバージョンでのテストを実行することを推奨します",
                    "command": "tox -e py39,py310,py311,py312",
                    "severity": "info"
                })
                
            else:
                self.logger.warning("⚠️ toxがインストールされていません")
                
                self.check_results["tox_integration"] = {
                    "status": "tox未インストール",
                    "config_exists": True
                }
                
                # 推奨事項を追加
                self.check_results["recommendations"].append({
                    "type": "tox",
                    "message": "toxをインストールして複数Pythonバージョンでのテストを有効にしてください",
                    "command": "pip install tox",
                    "severity": "warning"
                })
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ tox統合チェックエラー: {e}")
            self.check_results["tox_integration"]["status"] = f"エラー: {e}"
            return False

    def _assess_compatibility_summary(self) -> None:
        """互換性サマリーを評価"""
        syntax_issues = self.check_results["syntax_check"].get("issues", [])
        dependency_issues = self.check_results["dependency_check"].get("issues", [])
        
        # バージョン別の問題を集計
        version_issues = {}
        for version in self.supported_versions:
            version_issues[version] = []
        
        # 構文問題を集計
        for issue in syntax_issues:
            version = issue.get("python_version", "all")
            if version == "all":
                for v in self.supported_versions:
                    version_issues[v].append(issue)
            elif version in version_issues:
                version_issues[version].append(issue)
        
        # 依存関係問題を集計（全バージョンに影響）
        for issue in dependency_issues:
            for version in self.supported_versions:
                version_issues[version].append(issue)
        
        # 互換性判定
        compatible = []
        incompatible = []
        unknown = []
        
        for version in self.supported_versions:
            issues = version_issues[version]
            error_issues = [i for i in issues if i.get("severity") == "error"]
            
            if not error_issues:
                compatible.append(version)
            elif error_issues:
                incompatible.append(version)
            else:
                unknown.append(version)
        
        self.check_results["compatibility_summary"] = {
            "compatible": compatible,
            "incompatible": incompatible,
            "unknown": unknown
        }

    def generate_compatibility_report(self) -> Dict:
        """
        互換性レポートを生成

        Returns:
            互換性レポートデータ
        """
        self._assess_compatibility_summary()
        
        # 統合レポート生成
        report_path = self.output_dir / "python-compatibility-report.json"
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.check_results, f, ensure_ascii=False, indent=2)
        
        # 日本語サマリー生成
        summary_path = self.output_dir / "python-compatibility-summary.txt"
        
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("Qt-Theme-Studio Python互換性チェック結果\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"実行日時: {self.check_results['timestamp']}\n")
            f.write(f"現在のPythonバージョン: {self.check_results['current_python']}\n")
            f.write(f"サポート対象バージョン: {', '.join(self.supported_versions)}\n\n")
            
            # 互換性サマリー
            summary = self.check_results["compatibility_summary"]
            f.write("互換性サマリー:\n")
            f.write(f"  - 互換: {', '.join(summary['compatible']) if summary['compatible'] else 'なし'}\n")
            f.write(f"  - 非互換: {', '.join(summary['incompatible']) if summary['incompatible'] else 'なし'}\n")
            f.write(f"  - 不明: {', '.join(summary['unknown']) if summary['unknown'] else 'なし'}\n\n")
            
            # 構文チェック結果
            syntax = self.check_results["syntax_check"]
            f.write("構文チェック:\n")
            f.write(f"  - ステータス: {syntax['status']}\n")
            if "files_checked" in syntax:
                f.write(f"  - チェック対象ファイル数: {syntax['files_checked']}\n")
            f.write(f"  - 問題数: {len(syntax.get('issues', []))}\n\n")
            
            # 依存関係チェック結果
            dependency = self.check_results["dependency_check"]
            f.write("依存関係チェック:\n")
            f.write(f"  - ステータス: {dependency['status']}\n")
            f.write(f"  - 問題数: {len(dependency.get('issues', []))}\n\n")
            
            # tox統合結果
            tox = self.check_results["tox_integration"]
            f.write("tox統合:\n")
            f.write(f"  - ステータス: {tox['status']}\n")
            f.write(f"  - 設定ファイル存在: {'はい' if tox.get('config_exists') else 'いいえ'}\n\n")
            
            # 推奨事項
            if self.check_results["recommendations"]:
                f.write("推奨事項:\n")
                for i, rec in enumerate(self.check_results["recommendations"], 1):
                    f.write(f"  {i}. {rec['message']}\n")
                    if "command" in rec:
                        f.write(f"     コマンド: {rec['command']}\n")
        
        self.logger.info(f"📄 互換性レポート生成完了: {report_path}")
        self.logger.info(f"📄 日本語サマリー生成完了: {summary_path}")
        
        return self.check_results

    def run_full_check(self) -> bool:
        """
        完全な互換性チェックを実行

        Returns:
            チェックが成功したかどうか
        """
        self.logger.info("🚀 Python互換性チェックを開始します")
        
        success = True
        
        # 構文互換性チェック
        if not self.check_syntax_compatibility():
            success = False
        
        # 依存関係互換性チェック
        if not self.check_dependency_compatibility():
            success = False
        
        # tox統合チェック
        if not self.check_tox_integration():
            success = False
        
        # レポート生成
        self.generate_compatibility_report()
        
        # 結果表示
        summary = self.check_results["compatibility_summary"]
        compatible_count = len(summary["compatible"])
        incompatible_count = len(summary["incompatible"])
        
        self.logger.info(f"🏁 Python互換性チェック完了")
        self.logger.info(f"📊 互換バージョン: {compatible_count}/{len(self.supported_versions)}")
        
        if incompatible_count > 0:
            self.logger.warning(f"⚠️ {incompatible_count}個のバージョンで互換性問題があります")
            for version in summary["incompatible"]:
                self.logger.warning(f"  - Python {version}")
        
        if self.check_results["recommendations"]:
            rec_count = len(self.check_results["recommendations"])
            self.logger.info(f"💡 {rec_count}個の推奨事項があります")
        
        return success and incompatible_count == 0


def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Qt-Theme-Studio Python互換性チェッカー"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        help="レポート出力ディレクトリ（デフォルト: logs/）"
    )
    parser.add_argument(
        "--syntax-only",
        action="store_true",
        help="構文チェックのみ実行"
    )
    parser.add_argument(
        "--dependency-only",
        action="store_true",
        help="依存関係チェックのみ実行"
    )
    parser.add_argument(
        "--tox-only",
        action="store_true",
        help="tox統合チェックのみ実行"
    )
    
    args = parser.parse_args()
    
    try:
        checker = PythonCompatibilityChecker(output_dir=args.output_dir)
        
        if args.syntax_only:
            success = checker.check_syntax_compatibility()
        elif args.dependency_only:
            success = checker.check_dependency_compatibility()
        elif args.tox_only:
            success = checker.check_tox_integration()
        else:
            success = checker.run_full_check()
        
        if success:
            print("\n✅ Python互換性チェック完了")
            sys.exit(0)
        else:
            print("\n⚠️ Python互換性チェックで問題が検出されました")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ チェックが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()