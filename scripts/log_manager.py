#!/usr/bin/env python3
"""
ログ管理システム CLI ツール

Qt-Theme-Studio のログファイルの管理、統計表示、メンテナンス機能を提供します。
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from qt_theme_studio.logger import (
    LogLevel,
    LogRotationConfig,
    QtThemeStudioLogger,
    get_logger,
    setup_logging,
)

logger = get_logger(__name__)


class LogManager:
    """ログ管理システム"""

    def __init__(self):
        self.logger = get_logger("log_manager")
        self.log_dir = Path("logs")

    def show_statistics(self) -> Dict:
        """ログ統計情報を表示"""
        qt_logger = get_logger()
        if isinstance(qt_logger, QtThemeStudioLogger):
            stats = qt_logger.get_log_statistics()
        else:
            # フォールバック統計
            stats = self._get_basic_statistics()

        print("=" * 60)
        print("Qt-Theme-Studio ログ統計")
        print("=" * 60)
        print(f"ログディレクトリ: {stats['log_directory']}")
        print(f"現在のログファイル数: {len(stats['current_logs'])}")
        print(f"総サイズ: {stats['total_size_mb']:.2f} MB")
        print()

        if stats["current_logs"]:
            print("📁 現在のログファイル:")
            print("-" * 40)
            for log_info in stats["current_logs"]:
                print(f"  {log_info['name']}: {log_info['size_mb']:.2f} MB")
                print(f"    最終更新: {log_info['modified']}")
            print()

        if "rotation_config" in stats:
            config = stats["rotation_config"]
            print("⚙️  ローテーション設定:")
            print("-" * 40)
            print(f"  最大ファイルサイズ: {config['max_bytes_mb']:.1f} MB")
            print(f"  バックアップ数: {config['backup_count']}")
            print(
                f"  バックアップ圧縮: {'有効' if config['compress_backups'] else '無効'}"
            )
            print(f"  アーカイブ期間: {config['archive_after_days']} 日")
            print(f"  削除期間: {config['cleanup_after_days']} 日")
            print()

        if "archive_stats" in stats:
            archive = stats["archive_stats"]
            print("📦 アーカイブ統計:")
            print("-" * 40)
            print(f"  アーカイブファイル数: {archive['total_files']}")
            print(f"  アーカイブサイズ: {archive['total_size_mb']} MB")
            if archive["oldest_file"]:
                print(f"  最古ファイル: {archive['oldest_file']}")
            if archive["newest_file"]:
                print(f"  最新ファイル: {archive['newest_file']}")

        return stats

    def _get_basic_statistics(self) -> Dict:
        """基本的な統計情報を取得（フォールバック）"""
        stats = {
            "log_directory": str(self.log_dir),
            "current_logs": [],
            "total_size_mb": 0,
        }

        if self.log_dir.exists():
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.is_file():
                    file_stats = log_file.stat()
                    stats["current_logs"].append(
                        {
                            "name": log_file.name,
                            "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                            "modified": datetime.fromtimestamp(
                                file_stats.st_mtime
                            ).isoformat(),
                        }
                    )
                    stats["total_size_mb"] += file_stats.st_size / (1024 * 1024)

        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        return stats

    def cleanup_logs(self, days: int = 30, dry_run: bool = False) -> List[str]:
        """古いログファイルをクリーンアップ"""
        cutoff_date = datetime.now() - timedelta(days=days)
        files_to_delete = []

        print(f"🧹 {days}日より古いログファイルをクリーンアップします...")
        if dry_run:
            print("（ドライランモード - 実際の削除は行いません）")
        print()

        for log_file in self.log_dir.rglob("*.log*"):
            if log_file.is_file():
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    files_to_delete.append(str(log_file))
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    print(
                        f"  🗑️  {log_file.name} ({size_mb:.2f} MB) - {file_time.strftime('%Y-%m-%d')}"
                    )

        if not files_to_delete:
            print("✅ 削除対象のファイルはありません。")
            return []

        print(f"\n削除対象: {len(files_to_delete)} ファイル")

        if not dry_run:
            deleted_count = 0
            for file_path in files_to_delete:
                try:
                    Path(file_path).unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ 削除失敗: {file_path} - {e}")

            print(f"✅ {deleted_count} ファイルを削除しました。")

        return files_to_delete

    def rotate_logs(self) -> List[str]:
        """手動でログローテーションを実行"""
        print("🔄 ログローテーションを実行します...")

        qt_logger = get_logger()
        if isinstance(qt_logger, QtThemeStudioLogger):
            rotated_files = qt_logger.rotate_logs_now()
            if rotated_files:
                print("✅ ローテーション完了:")
                for file_path in rotated_files:
                    print(f"  📁 {Path(file_path).name}")
            else:
                print("ℹ️  ローテーション対象のファイルはありませんでした。")
        else:
            print("❌ 拡張ロガーが利用できません。")
            rotated_files = []

        return rotated_files

    def export_logs(
        self,
        output_file: str,
        days: Optional[int] = None,
        levels: Optional[List[str]] = None,
    ) -> bool:
        """ログをエクスポート"""
        print(f"📤 ログをエクスポートします: {output_file}")

        # 日付フィルター
        start_date = None
        if days:
            start_date = datetime.now() - timedelta(days=days)
            print(f"   期間: 過去{days}日間")

        # レベルフィルター
        log_levels = None
        if levels:
            try:
                log_levels = [LogLevel[level.upper()] for level in levels]
                print(f"   レベル: {', '.join(levels)}")
            except KeyError as e:
                print(f"❌ 無効なログレベル: {e}")
                return False

        qt_logger = get_logger()
        if isinstance(qt_logger, QtThemeStudioLogger):
            success = qt_logger.export_logs(
                output_file, start_date=start_date, log_levels=log_levels
            )
            if success:
                print("✅ エクスポート完了")
            else:
                print("❌ エクスポート失敗")
            return success
        print("❌ 拡張ロガーが利用できません。")
        return False

    def set_log_level(self, level: str) -> bool:
        """ログレベルを変更"""
        try:
            log_level = LogLevel[level.upper()]
            qt_logger = get_logger()

            if isinstance(qt_logger, QtThemeStudioLogger):
                qt_logger.set_log_level(log_level)
                print(f"✅ ログレベルを {level.upper()} に変更しました。")
                return True
            print("❌ 拡張ロガーが利用できません。")
            return False

        except KeyError:
            print(f"❌ 無効なログレベル: {level}")
            print("有効なレベル: DEBUG, INFO, WARNING, ERROR, CRITICAL")
            return False

    def configure_rotation(
        self,
        max_size_mb: Optional[int] = None,
        backup_count: Optional[int] = None,
        compress: Optional[bool] = None,
        archive_days: Optional[int] = None,
        cleanup_days: Optional[int] = None,
    ) -> bool:
        """ローテーション設定を変更"""
        print("⚙️  ローテーション設定を更新します...")

        # 現在の設定を取得
        current_config = LogRotationConfig()

        # 新しい設定を作成
        new_config = LogRotationConfig(
            max_bytes=(max_size_mb * 1024 * 1024)
            if max_size_mb
            else current_config.max_bytes,
            backup_count=backup_count
            if backup_count is not None
            else current_config.backup_count,
            compress_backups=compress
            if compress is not None
            else current_config.compress_backups,
            archive_after_days=archive_days
            if archive_days is not None
            else current_config.archive_after_days,
            cleanup_after_days=cleanup_days
            if cleanup_days is not None
            else current_config.cleanup_after_days,
        )

        # ロガーを再設定
        setup_logging(LogLevel.INFO, rotation_config=new_config)

        print("✅ 設定を更新しました:")
        print(f"   最大ファイルサイズ: {new_config.max_bytes / (1024 * 1024):.1f} MB")
        print(f"   バックアップ数: {new_config.backup_count}")
        print(f"   圧縮: {'有効' if new_config.compress_backups else '無効'}")
        print(f"   アーカイブ期間: {new_config.archive_after_days} 日")
        print(f"   削除期間: {new_config.cleanup_after_days} 日")

        return True

    def monitor_logs(self, interval: int = 60):
        """ログファイルを監視"""
        print(f"👁️  ログファイルを監視します（{interval}秒間隔）")
        print("Ctrl+C で停止")

        try:
            import time

            while True:
                stats = self._get_basic_statistics()
                print(
                    f"\r現在のログサイズ: {stats['total_size_mb']:.2f} MB",
                    end="",
                    flush=True,
                )
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n監視を停止しました。")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="Qt-Theme-Studio ログ管理システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 統計情報を表示
  python scripts/log_manager.py --stats

  # 30日より古いログを削除（ドライラン）
  python scripts/log_manager.py --cleanup 30 --dry-run

  # ログローテーションを実行
  python scripts/log_manager.py --rotate

  # ログレベルをDEBUGに変更
  python scripts/log_manager.py --set-level DEBUG

  # 過去7日間のERRORログをエクスポート
  python scripts/log_manager.py --export error_logs.txt --days 7 --levels ERROR

  # ローテーション設定を変更（最大5MB、バックアップ3個）
  python scripts/log_manager.py --configure --max-size 5 --backup-count 3
        """,
    )

    # 基本操作
    parser.add_argument("--stats", action="store_true", help="ログ統計情報を表示")
    parser.add_argument(
        "--cleanup", type=int, metavar="DAYS", help="指定日数より古いログを削除"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="削除のドライラン（実際には削除しない）"
    )
    parser.add_argument(
        "--rotate", action="store_true", help="手動でログローテーションを実行"
    )
    parser.add_argument(
        "--monitor", type=int, metavar="SECONDS", help="ログファイルを監視（秒間隔）"
    )

    # エクスポート
    parser.add_argument(
        "--export", type=str, metavar="FILE", help="ログをファイルにエクスポート"
    )
    parser.add_argument("--days", type=int, help="エクスポート期間（日数）")
    parser.add_argument("--levels", nargs="+", help="エクスポートするログレベル")

    # 設定
    parser.add_argument(
        "--set-level", type=str, metavar="LEVEL", help="ログレベルを変更"
    )
    parser.add_argument(
        "--configure", action="store_true", help="ローテーション設定を変更"
    )
    parser.add_argument(
        "--max-size", type=int, metavar="MB", help="最大ファイルサイズ（MB）"
    )
    parser.add_argument("--backup-count", type=int, help="バックアップファイル数")
    parser.add_argument(
        "--compress", action="store_true", help="バックアップ圧縮を有効化"
    )
    parser.add_argument(
        "--no-compress", action="store_true", help="バックアップ圧縮を無効化"
    )
    parser.add_argument("--archive-days", type=int, help="アーカイブ期間（日数）")
    parser.add_argument("--cleanup-days", type=int, help="削除期間（日数）")

    args = parser.parse_args()

    # 引数が指定されていない場合はヘルプを表示
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # ログマネージャーを初期化
    manager = LogManager()

    try:
        if args.stats:
            manager.show_statistics()

        elif args.cleanup is not None:
            manager.cleanup_logs(args.cleanup, args.dry_run)

        elif args.rotate:
            manager.rotate_logs()

        elif args.export:
            manager.export_logs(args.export, args.days, args.levels)

        elif args.set_level:
            manager.set_log_level(args.set_level)

        elif args.configure:
            compress = None
            if args.compress:
                compress = True
            elif args.no_compress:
                compress = False

            manager.configure_rotation(
                max_size_mb=args.max_size,
                backup_count=args.backup_count,
                compress=compress,
                archive_days=args.archive_days,
                cleanup_days=args.cleanup_days,
            )

        elif args.monitor:
            manager.monitor_logs(args.monitor)

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n操作が中断されました。")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
