#!/usr/bin/env python3
"""
Qt-Theme-Studio セキュリティスキャナー

このスクリプトは以下のセキュリティチェックを実行します:
1. Banditによるコードセキュリティスキャン
2. pip-auditによる依存関係脆弱性チェック
3. 脆弱性検出時の日本語アラート機能
4. 統合セキュリティレポート生成
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent


class SecurityScanner:
    """セキュリティスキャナークラス"""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        セキュリティスキャナーを初期化

        Args:
            output_dir: レポート出力ディレクトリ（デフォルト: logs/）
        """
        self.project_root = PROJECT_ROOT
        self.output_dir = output_dir or (PROJECT_ROOT / "logs")
        self.output_dir.mkdir(exist_ok=True)

        # ログ設定
        self.logger = self._setup_logger()

        # スキャン結果
        self.scan_results = {
            "timestamp": datetime.now().isoformat(),
            "bandit": {"status": "未実行", "issues": [], "summary": {}},
            "pip_audit": {"status": "未実行", "vulnerabilities": [], "summary": {}},
            "overall": {
                "status": "未実行",
                "risk_level": "不明",
                "recommendations": [],
            },
        }

    def _setup_logger(self) -> logging.Logger:
        """ログ設定を初期化"""
        logger = logging.getLogger("security_scanner")
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
            self.logger.info(f"コマンド実行: {' '.join(command)}")

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

    def scan_with_bandit(self) -> bool:
        """
        Banditによるコードセキュリティスキャンを実行

        Returns:
            スキャンが成功したかどうか
        """
        self.logger.info("🔒 Banditセキュリティスキャンを開始します")

        # 出力ファイルパス
        json_output = self.output_dir / "bandit-security-report.json"
        txt_output = self.output_dir / "bandit-security-report.txt"

        try:
            # JSONレポート生成
            return_code, stdout, stderr = self._run_command(
                [
                    "bandit",
                    "-r",
                    "qt_theme_studio/",
                    "-f",
                    "json",
                    "-o",
                    str(json_output),
                ]
            )

            # テキストレポート生成
            self._run_command(
                ["bandit", "-r", "qt_theme_studio/", "-f", "txt", "-o", str(txt_output)]
            )

            # 結果解析
            if json_output.exists():
                with open(json_output, encoding="utf-8") as f:
                    bandit_data = json.load(f)

                # 結果を保存
                self.scan_results["bandit"] = {
                    "status": "完了",
                    "issues": bandit_data.get("results", []),
                    "summary": {
                        "total_issues": len(bandit_data.get("results", [])),
                        "high_severity": len(
                            [
                                issue
                                for issue in bandit_data.get("results", [])
                                if issue.get("issue_severity") == "HIGH"
                            ]
                        ),
                        "medium_severity": len(
                            [
                                issue
                                for issue in bandit_data.get("results", [])
                                if issue.get("issue_severity") == "MEDIUM"
                            ]
                        ),
                        "low_severity": len(
                            [
                                issue
                                for issue in bandit_data.get("results", [])
                                if issue.get("issue_severity") == "LOW"
                            ]
                        ),
                    },
                }

                # 結果表示
                total_issues = self.scan_results["bandit"]["summary"]["total_issues"]
                high_issues = self.scan_results["bandit"]["summary"]["high_severity"]

                if total_issues == 0:
                    self.logger.info(
                        "✅ Bandit: セキュリティ問題は検出されませんでした"
                    )
                else:
                    self.logger.warning(
                        f"⚠️ Bandit: {total_issues}件のセキュリティ問題を検出しました"
                    )
                    if high_issues > 0:
                        self.logger.error(
                            f"❌ 高リスクの問題が{high_issues}件あります！"
                        )

                return True

            self.logger.error("❌ Banditレポートファイルが生成されませんでした")
            self.scan_results["bandit"]["status"] = "失敗"
            return False

        except Exception as e:
            self.logger.error(f"❌ Banditスキャンエラー: {e}")
            self.scan_results["bandit"]["status"] = f"エラー: {e}"
            return False

    def scan_with_pip_audit(self) -> bool:
        """
        pip-auditによる依存関係脆弱性チェックを実行

        Returns:
            スキャンが成功したかどうか
        """
        self.logger.info("🛡️ pip-audit依存関係脆弱性チェックを開始します")

        # 出力ファイルパス
        json_output = self.output_dir / "pip-audit-vulnerability-report.json"

        try:
            # pip-auditチェック実行
            return_code, stdout, stderr = self._run_command(
                ["pip-audit", "--format", "json", "--output", str(json_output)]
            )

            if return_code == -1:
                raise FileNotFoundError(stderr or "pip-auditコマンドが見つかりません")
            if return_code not in [0, 1]:
                raise RuntimeError(stderr.strip() or "pip-auditの実行に失敗しました")

            if json_output.exists():
                with open(json_output, encoding="utf-8") as f:
                    audit_data = json.load(f)
            elif stdout.strip():
                audit_data = json.loads(stdout)
            else:
                audit_data = []

            dependencies = []
            if isinstance(audit_data, list):
                dependencies = audit_data
            elif isinstance(audit_data, dict):
                dependencies = audit_data.get("dependencies", [])

            vulnerabilities = []
            for dependency in dependencies:
                if not isinstance(dependency, dict):
                    continue
                package_name = dependency.get("name", "不明")
                installed_version = dependency.get("version", "不明")
                for vuln in dependency.get("vulns", []):
                    if not isinstance(vuln, dict):
                        continue
                    vulnerabilities.append(
                        {
                            "package_name": package_name,
                            "installed_version": installed_version,
                            "vulnerability_id": vuln.get("id", "不明"),
                        }
                    )

            critical_count = len(
                [
                    vuln
                    for vuln in vulnerabilities
                    if isinstance(vuln, dict)
                    and str(vuln.get("vulnerability_id", "")).startswith("CVE")
                ]
            )
            affected_packages = {
                vuln.get("package_name", "不明")
                for vuln in vulnerabilities
                if isinstance(vuln, dict) and vuln.get("package_name")
            }
            package_count = (
                len(affected_packages) if affected_packages else len(vulnerabilities)
            )

            self.scan_results["pip_audit"] = {
                "status": "完了",
                "vulnerabilities": vulnerabilities,
                "summary": {
                    "total_vulnerabilities": len(vulnerabilities),
                    "critical": critical_count,
                    "packages_affected": package_count,
                },
            }

            # 結果表示
            total_vulns = self.scan_results["pip_audit"]["summary"][
                "total_vulnerabilities"
            ]

            if total_vulns == 0:
                self.logger.info("✅ pip-audit: 依存関係に脆弱性は検出されませんでした")
            else:
                affected_package_count = self.scan_results["pip_audit"]["summary"][
                    "packages_affected"
                ]
                self.logger.warning(
                    f"⚠️ pip-audit: {total_vulns}件の脆弱性を検出しました（{affected_package_count}パッケージ）"
                )

                # 詳細表示
                for vuln in vulnerabilities[:5]:  # 最初の5件のみ表示
                    if isinstance(vuln, dict):
                        package = vuln.get("package_name", "不明")
                        version = vuln.get("installed_version", "不明")
                        vuln_id = vuln.get("vulnerability_id", "不明")
                    else:
                        package = "不明"
                        version = "不明"
                        vuln_id = str(vuln)
                    self.logger.warning(f"  - {package} v{version}: {vuln_id}")

            return True

        except Exception as e:
            self.logger.error(f"❌ pip-auditスキャンエラー: {e}")
            self.scan_results["pip_audit"]["status"] = f"エラー: {e}"
            return False

    def _assess_overall_risk(self) -> None:
        """総合リスク評価を実行"""
        bandit_summary = self.scan_results["bandit"]["summary"]
        pip_audit_summary = self.scan_results["pip_audit"]["summary"]

        # リスクレベル計算
        risk_score = 0
        recommendations = []

        # Banditリスク評価
        if bandit_summary:
            high_issues = bandit_summary.get("high_severity", 0)
            medium_issues = bandit_summary.get("medium_severity", 0)

            risk_score += high_issues * 3 + medium_issues * 1

            if high_issues > 0:
                recommendations.append(
                    f"高リスクのセキュリティ問題{high_issues}件を優先的に修正してください"
                )
            if medium_issues > 0:
                recommendations.append(
                    f"中リスクのセキュリティ問題{medium_issues}件の修正を検討してください"
                )

        # pip-auditリスク評価
        if pip_audit_summary:
            total_vulns = pip_audit_summary.get("total_vulnerabilities", 0)
            risk_score += total_vulns * 2

            if total_vulns > 0:
                recommendations.append(
                    f"依存関係の脆弱性{total_vulns}件を修正してください"
                )

        # リスクレベル判定
        if risk_score >= 10:
            risk_level = "高"
            status = "要対応"
        elif risk_score >= 5:
            risk_level = "中"
            status = "注意"
        elif risk_score > 0:
            risk_level = "低"
            status = "監視"
        else:
            risk_level = "なし"
            status = "良好"

        # 結果保存
        self.scan_results["overall"] = {
            "status": status,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommendations": recommendations,
        }

    def generate_alert_report(self) -> Dict:
        """
        アラートレポートを生成

        Returns:
            アラートレポートデータ
        """
        self._assess_overall_risk()

        # 統合レポート生成
        report_path = self.output_dir / "security-alert-report.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.scan_results, f, ensure_ascii=False, indent=2)

        # 日本語サマリー生成
        summary_path = self.output_dir / "security-summary.txt"

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("Qt-Theme-Studio セキュリティスキャン結果\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"実行日時: {self.scan_results['timestamp']}\n")
            f.write(f"総合リスクレベル: {self.scan_results['overall']['risk_level']}\n")
            f.write(f"ステータス: {self.scan_results['overall']['status']}\n\n")

            # Bandit結果
            bandit = self.scan_results["bandit"]
            f.write("コードセキュリティ (Bandit):\n")
            if bandit["summary"]:
                f.write(f"  - 総問題数: {bandit['summary']['total_issues']}\n")
                f.write(f"  - 高リスク: {bandit['summary']['high_severity']}\n")
                f.write(f"  - 中リスク: {bandit['summary']['medium_severity']}\n")
                f.write(f"  - 低リスク: {bandit['summary']['low_severity']}\n")
            else:
                f.write(f"  - ステータス: {bandit['status']}\n")
            f.write("\n")

            # pip-audit結果
            pip_audit = self.scan_results["pip_audit"]
            f.write("依存関係脆弱性 (pip-audit):\n")
            if pip_audit["summary"]:
                f.write(
                    f"  - 総脆弱性数: {pip_audit['summary']['total_vulnerabilities']}\n"
                )
                f.write(
                    f"  - 影響パッケージ数: {pip_audit['summary']['packages_affected']}\n"
                )
            else:
                f.write(f"  - ステータス: {pip_audit['status']}\n")
            f.write("\n")

            # 推奨事項
            if self.scan_results["overall"]["recommendations"]:
                f.write("推奨事項:\n")
                for i, rec in enumerate(
                    self.scan_results["overall"]["recommendations"], 1
                ):
                    f.write(f"  {i}. {rec}\n")

        self.logger.info(f"📄 セキュリティレポート生成完了: {report_path}")
        self.logger.info(f"📄 日本語サマリー生成完了: {summary_path}")

        return self.scan_results

    def run_full_scan(self) -> bool:
        """
        完全なセキュリティスキャンを実行

        Returns:
            スキャンが成功したかどうか
        """
        self.logger.info("🚀 セキュリティスキャンを開始します")

        success = True

        # Banditスキャン
        if not self.scan_with_bandit():
            success = False

        # pip-auditスキャン
        if not self.scan_with_pip_audit():
            success = False

        # レポート生成
        self.generate_alert_report()

        # 結果表示
        overall = self.scan_results["overall"]
        risk_level = overall["risk_level"]
        status = overall["status"]

        self.logger.info("🏁 セキュリティスキャン完了")
        self.logger.info(f"📊 総合リスクレベル: {risk_level}")
        self.logger.info(f"📈 ステータス: {status}")

        if overall["recommendations"]:
            self.logger.warning("⚠️ 推奨事項:")
            for rec in overall["recommendations"]:
                self.logger.warning(f"  - {rec}")

        return success and risk_level in ["なし", "低"]


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Qt-Theme-Studio セキュリティスキャナー"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        help="レポート出力ディレクトリ（デフォルト: logs/）",
    )
    parser.add_argument(
        "--bandit-only", action="store_true", help="Banditスキャンのみ実行"
    )
    parser.add_argument(
        "--pip-audit-only", action="store_true", help="pip-auditスキャンのみ実行"
    )

    args = parser.parse_args()

    try:
        scanner = SecurityScanner(output_dir=args.output_dir)

        if args.bandit_only:
            success = scanner.scan_with_bandit()
        elif args.pip_audit_only:
            success = scanner.scan_with_pip_audit()
        else:
            success = scanner.run_full_scan()

        if success:
            print("\n✅ セキュリティスキャン完了")
            sys.exit(0)
        else:
            print("\n⚠️ セキュリティスキャンで問題が検出されました")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ スキャンが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
