"""
Qt-Theme-Studio 高機能ロガー

構造化ログ、パフォーマンス測定、エラートラッキング機能を提供します。
自動ローテーション、サイズ制限、アーカイブ機能を含む統合ログ管理システム。
"""

import gzip
import json
import logging
import logging.handlers
import shutil
import time
import traceback
from contextlib import contextmanager, suppress
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional, TextIO, Union


class LogLevel(Enum):
    """ログレベルの定義"""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class LogCategory(Enum):
    """ログカテゴリの定義"""

    GENERAL = auto()
    UI = auto()
    THEME = auto()
    PERFORMANCE = auto()
    ERROR = auto()
    SECURITY = auto()


class LogContext:
    """ログコンテキスト情報"""

    def __init__(self, **kwargs: Any) -> None:
        self.context = kwargs
        self.timestamp = datetime.now()
        self.session_id = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """セッションIDを生成"""
        return f"session_{int(time.time())}"

    def add_context(self, **kwargs: Any) -> None:
        """コンテキスト情報を追加"""
        self.context.update(kwargs)

    def to_dict(self) -> dict[str, Any]:
        """辞書形式でコンテキスト情報を取得"""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            **self.context,
        }


class StructuredFormatter(logging.Formatter):
    """構造化ログフォーマッター"""

    def format(self, record: logging.LogRecord) -> str:
        """ログレコードを構造化形式でフォーマット"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # カスタム属性を追加
        if hasattr(record, "category"):
            log_entry["category"] = (
                record.category.value
                if hasattr(record.category, "value")
                else str(record.category)
            )

        if hasattr(record, "context"):
            log_entry["context"] = (
                record.context.to_dict()
                if hasattr(record.context, "to_dict")
                else record.context
            )

        if hasattr(record, "performance_data"):
            log_entry["performance"] = record.performance_data

        return json.dumps(log_entry, ensure_ascii=False, indent=2)


class LogRotationConfig:
    """ログローテーション設定クラス"""

    def __init__(
        self,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        compress_backups: bool = True,
        archive_after_days: int = 30,
        cleanup_after_days: int = 90,
    ):
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.compress_backups = compress_backups
        self.archive_after_days = archive_after_days
        self.cleanup_after_days = cleanup_after_days


class AdvancedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """拡張ローテーションファイルハンドラー(圧縮・アーカイブ機能付き)"""

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: Optional[str] = None,
        delay: bool = False,
        compress_backups: bool = True,
    ) -> None:
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.compress_backups = compress_backups
        # streamの型を明示的に指定
        self.stream: Optional[TextIO] = None

    def doRollover(self) -> None:
        """ローテーション実行時の処理をオーバーライド"""
        if self.stream:
            self.stream.close()
            self.stream = None

        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename(f"{self.baseFilename}.{i}")
                dfn = self.rotation_filename(f"{self.baseFilename}.{i + 1}")

                if Path(sfn).exists():
                    if Path(dfn).exists():
                        Path(dfn).unlink()
                    Path(sfn).rename(dfn)

            dfn = self.rotation_filename(f"{self.baseFilename}.1")
            if Path(dfn).exists():
                Path(dfn).unlink()

            # 現在のログファイルをバックアップ
            if Path(self.baseFilename).exists():
                Path(self.baseFilename).rename(dfn)

                # 圧縮オプションが有効な場合
                if self.compress_backups:
                    self._compress_backup(dfn)

        if not self.delay:
            self.stream = self._open()

    def _compress_backup(self, backup_file: str) -> None:
        """バックアップファイルを圧縮"""
        try:
            compressed_file = f"{backup_file}.gz"
            with (
                Path(backup_file).open("rb") as f_in,
                gzip.open(compressed_file, "wb") as f_out,
            ):
                shutil.copyfileobj(f_in, f_out)

            # 元のファイルを削除
            Path(backup_file).unlink()
        except Exception:
            # 圧縮に失敗しても処理を続行
            pass


class LogArchiveManager:
    """ログアーカイブ管理クラス"""

    def __init__(self, log_dir: Path, config: LogRotationConfig):
        self.log_dir = log_dir
        self.config = config
        self.archive_dir = log_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)

    def archive_old_logs(self) -> None:
        """古いログファイルをアーカイブ"""
        cutoff_date = datetime.now() - timedelta(days=self.config.archive_after_days)

        for log_file in self.log_dir.glob("*.log*"):
            if (
                log_file.is_file()
                and log_file.stat().st_mtime < cutoff_date.timestamp()
            ):
                try:
                    archive_path = self.archive_dir / log_file.name

                    # 既に圧縮されている場合はそのまま移動
                    if log_file.suffix == ".gz":
                        shutil.move(str(log_file), str(archive_path))
                    else:
                        # 圧縮してアーカイブ
                        with (
                            Path(log_file).open("rb") as f_in,
                            gzip.open(f"{archive_path}.gz", "wb") as f_out,
                        ):
                            shutil.copyfileobj(f_in, f_out)
                        log_file.unlink()

                except Exception:
                    # アーカイブに失敗しても処理を続行
                    pass

    def cleanup_old_archives(self) -> None:
        """古いアーカイブファイルを削除"""
        cutoff_date = datetime.now() - timedelta(days=self.config.cleanup_after_days)

        for archive_file in self.archive_dir.glob("*"):
            if (
                archive_file.is_file()
                and archive_file.stat().st_mtime < cutoff_date.timestamp()
            ):
                with suppress(Exception):
                    archive_file.unlink()

    def get_archive_stats(self) -> dict[str, Any]:
        """アーカイブ統計情報を取得"""
        stats: dict[str, Any] = {
            "total_files": 0,
            "total_size_mb": 0.0,
            "oldest_file": "",
            "newest_file": "",
        }

        archive_files = list(self.archive_dir.glob("*"))
        stats["total_files"] = len(archive_files)

        if archive_files:
            total_size = sum(f.stat().st_size for f in archive_files if f.is_file())
            stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)

            file_times = [f.stat().st_mtime for f in archive_files if f.is_file()]
            if file_times:
                stats["oldest_file"] = datetime.fromtimestamp(
                    min(file_times)
                ).isoformat()
                stats["newest_file"] = datetime.fromtimestamp(
                    max(file_times)
                ).isoformat()

        return stats


class QtThemeStudioLogger:
    """Qt-Theme-Studio専用ロガー(拡張版)"""

    def __init__(
        self,
        name: str = "qt_theme_studio",
        rotation_config: Optional[LogRotationConfig] = None,
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # ローテーション設定
        self.rotation_config = rotation_config or LogRotationConfig()

        # ログディレクトリの設定
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # アーカイブマネージャー
        self.archive_manager = LogArchiveManager(self.log_dir, self.rotation_config)

        # ハンドラーの設定
        self._setup_handlers()

        # パフォーマンス測定用
        self._performance_timers: dict[str, float] = {}

        # 定期メンテナンス用のカウンター
        self._maintenance_counter = 0
        self._maintenance_interval = 100  # 100回のログ出力ごとにメンテナンス実行

    def _setup_handlers(self) -> None:
        """ログハンドラーを設定(拡張版)"""
        # 既存のハンドラーをクリア
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # コンソールは INFO 以上
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)

        # メインログファイルハンドラー(ローテーション付き)
        main_log_file = self.log_dir / f"{self.name}.log"
        main_handler = AdvancedRotatingFileHandler(
            filename=str(main_log_file),
            maxBytes=self.rotation_config.max_bytes,
            backupCount=self.rotation_config.backup_count,
            encoding="utf-8",
            compress_backups=self.rotation_config.compress_backups,
        )
        main_handler.setLevel(logging.DEBUG)
        main_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        main_handler.setFormatter(main_formatter)

        # 構造化ログファイルハンドラー(日別)
        structured_log_file = (
            self.log_dir
            / f"{self.name}_structured_{datetime.now().strftime('%Y%m%d')}.log"
        )
        structured_handler = AdvancedRotatingFileHandler(
            filename=str(structured_log_file),
            maxBytes=self.rotation_config.max_bytes,
            backupCount=self.rotation_config.backup_count,
            encoding="utf-8",
            compress_backups=self.rotation_config.compress_backups,
        )
        structured_handler.setLevel(logging.DEBUG)
        structured_formatter = StructuredFormatter()
        structured_handler.setFormatter(structured_formatter)

        # エラー専用ログファイルハンドラー
        error_log_file = self.log_dir / f"{self.name}_errors.log"
        error_handler = AdvancedRotatingFileHandler(
            filename=str(error_log_file),
            maxBytes=self.rotation_config.max_bytes // 2,  # エラーログは小さめ
            backupCount=self.rotation_config.backup_count,
            encoding="utf-8",
            compress_backups=self.rotation_config.compress_backups,
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s\n%(exc_info)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        error_handler.setFormatter(error_formatter)

        # パフォーマンス専用ログファイルハンドラー
        perf_log_file = self.log_dir / f"{self.name}_performance.log"
        perf_handler = AdvancedRotatingFileHandler(
            filename=str(perf_log_file),
            maxBytes=self.rotation_config.max_bytes // 4,  # パフォーマンスログは小さめ
            backupCount=self.rotation_config.backup_count,
            encoding="utf-8",
            compress_backups=self.rotation_config.compress_backups,
        )
        perf_handler.setLevel(logging.DEBUG)
        perf_handler.addFilter(self._performance_filter)
        perf_formatter = logging.Formatter(
            "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        perf_handler.setFormatter(perf_formatter)

        # ハンドラーを追加
        self.logger.addHandler(console_handler)
        self.logger.addHandler(main_handler)
        self.logger.addHandler(structured_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(perf_handler)

    def _performance_filter(self, record: logging.LogRecord) -> bool:
        """パフォーマンスログ用フィルター"""
        return (
            hasattr(record, "category") and record.category == LogCategory.PERFORMANCE
        )

    def _log_with_category(
        self,
        level: int,
        message: str,
        category: LogCategory,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """カテゴリ付きでログを出力"""
        extra: dict[str, Any] = {"category": category}
        if context:
            extra["context"] = context

        # パフォーマンスデータがある場合
        if "performance_data" in kwargs:
            extra["performance_data"] = kwargs["performance_data"]

        self.logger.log(level, message, extra=extra)

        # 定期メンテナンスの実行
        self._maintenance_counter += 1
        if self._maintenance_counter >= self._maintenance_interval:
            self._perform_maintenance()
            self._maintenance_counter = 0

    def debug(
        self,
        message: str,
        category: LogCategory = LogCategory.GENERAL,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """デバッグログ"""
        self._log_with_category(logging.DEBUG, message, category, context, **kwargs)

    def info(
        self,
        message: str,
        category: LogCategory = LogCategory.GENERAL,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """情報ログ"""
        self._log_with_category(logging.INFO, message, category, context, **kwargs)

    def warning(
        self,
        message: str,
        category: LogCategory = LogCategory.GENERAL,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """警告ログ"""
        self._log_with_category(logging.WARNING, message, category, context, **kwargs)

    def error(
        self,
        message: str,
        category: LogCategory = LogCategory.ERROR,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """エラーログ"""
        self._log_with_category(logging.ERROR, message, category, context, **kwargs)

    def critical(
        self,
        message: str,
        category: LogCategory = LogCategory.ERROR,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """重大エラーログ"""
        self._log_with_category(logging.CRITICAL, message, category, context, **kwargs)

    def log_theme_operation(
        self,
        operation: str,
        theme_name: str,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """テーマ操作のログ"""
        message = f"テーマ操作: {operation} - {theme_name}"
        self.info(message, LogCategory.THEME, context, **kwargs)

    def log_ui_operation(
        self,
        operation: str,
        widget_name: str,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """UI操作のログ"""
        message = f"UI操作: {operation} - {widget_name}"
        self.info(message, LogCategory.UI, context, **kwargs)

    def log_performance(
        self,
        operation: str,
        duration: float,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """パフォーマンスログ"""
        message = f"パフォーマンス: {operation} - {duration:.3f}秒"
        self.info(
            message,
            LogCategory.PERFORMANCE,
            context,
            performance_data={"operation": operation, "duration": duration},
            **kwargs,
        )

    @contextmanager
    def performance_timer(
        self, operation: str, context: Optional[LogContext] = None
    ) -> Any:
        """パフォーマンス測定用コンテキストマネージャー"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.log_performance(operation, duration, context)

    def log_exception(
        self,
        message: str,
        exception: Exception,
        context: Optional[LogContext] = None,
        **kwargs: Any,
    ) -> None:
        """例外ログ"""
        error_details = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc(),
        }

        self.error(
            f"{message}: {exception!s}",
            LogCategory.ERROR,
            context,
            performance_data=error_details,
            **kwargs,
        )

    def _perform_maintenance(self) -> None:
        """定期メンテナンス処理"""
        try:
            # アーカイブ処理
            self.archive_manager.archive_old_logs()

            # 古いアーカイブの削除
            self.archive_manager.cleanup_old_archives()

            # ログディスク使用量のチェック
            self._check_disk_usage()

        except Exception:
            # メンテナンス処理でエラーが発生しても本来の処理は継続
            pass

    def _check_disk_usage(self) -> None:
        """ログディスクの使用量をチェック"""
        try:
            total_size = sum(
                f.stat().st_size for f in self.log_dir.rglob("*") if f.is_file()
            )

            # 100MB を超えた場合は警告
            if total_size > 100 * 1024 * 1024:
                self.warning(
                    f"ログディスク使用量が大きくなっています: {total_size / (1024 * 1024):.1f}MB",
                    LogCategory.GENERAL,
                )

        except Exception:
            pass

    def get_log_statistics(self) -> dict[str, Any]:
        """ログ統計情報を取得"""
        stats: dict[str, Any] = {
            "log_directory": str(self.log_dir),
            "rotation_config": {
                "max_bytes_mb": self.rotation_config.max_bytes / (1024 * 1024),
                "backup_count": self.rotation_config.backup_count,
                "compress_backups": self.rotation_config.compress_backups,
                "archive_after_days": self.rotation_config.archive_after_days,
                "cleanup_after_days": self.rotation_config.cleanup_after_days,
            },
            "current_logs": [],
            "total_size_mb": 0.0,
            "archive_stats": self.archive_manager.get_archive_stats(),
        }

        # 現在のログファイル情報
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
                stats["total_size_mb"] += float(file_stats.st_size) / (1024 * 1024)

        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        return stats

    def cleanup_logs(self, older_than_days: int = 30) -> list[str]:
        """指定日数より古いログファイルを削除"""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        deleted_files = []

        for log_file in self.log_dir.glob("*.log*"):
            if log_file.is_file():
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    try:
                        log_file.unlink()
                        deleted_files.append(str(log_file))
                    except Exception as e:
                        self.warning(
                            f"ログファイル削除に失敗: {log_file} - {e}",
                            LogCategory.GENERAL,
                        )

        if deleted_files:
            self.info(
                f"古いログファイルを削除しました: {len(deleted_files)}ファイル",
                LogCategory.GENERAL,
            )

        return deleted_files

    def set_log_level(self, level: LogLevel) -> None:
        """ログレベルを動的に変更"""
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }

        self.logger.setLevel(level_map[level])
        self.info(f"ログレベルを {level.name} に変更しました", LogCategory.GENERAL)

    def rotate_logs_now(self) -> list[str]:
        """手動でログローテーションを実行"""
        rotated_handlers = []

        for handler in self.logger.handlers:
            if isinstance(handler, AdvancedRotatingFileHandler):
                try:
                    handler.doRollover()
                    rotated_handlers.append(handler.baseFilename)
                except Exception as e:
                    self.warning(
                        f"ログローテーションに失敗: {handler.baseFilename} - {e}",
                        LogCategory.GENERAL,
                    )

        if rotated_handlers:
            self.info(
                f"ログローテーションを実行しました: {len(rotated_handlers)}ファイル",
                LogCategory.GENERAL,
            )

        return rotated_handlers

    def export_logs(
        self,
        output_file: Union[str, Path],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        log_levels: Optional[list[LogLevel]] = None,
    ) -> bool:
        """ログをエクスポート"""
        try:
            output_path = Path(output_file)
            exported_entries = []

            # フィルター条件の設定
            level_names = [level.name for level in log_levels] if log_levels else None

            # ログファイルを読み込んでフィルタリング
            for log_file in self.log_dir.glob("*.log"):
                if log_file.is_file():
                    try:
                        with log_file.open(encoding="utf-8") as f:
                            for line in f:
                                # 簡単な日付・レベルフィルタリング
                                if start_date or end_date or level_names:
                                    # より詳細なフィルタリングロジックを実装可能
                                    pass
                                exported_entries.append(line.strip())
                    except Exception:
                        continue

            # エクスポートファイルに書き込み
            with output_path.open("w", encoding="utf-8") as f:
                f.write("# Qt-Theme-Studio ログエクスポート\n")
                f.write(f"# エクスポート日時: {datetime.now().isoformat()}\n")
                f.write(f"# 総エントリ数: {len(exported_entries)}\n\n")

                for entry in exported_entries:
                    f.write(f"{entry}\n")

            self.info(
                f"ログをエクスポートしました: {output_path} ({len(exported_entries)}エントリ)",
                LogCategory.GENERAL,
            )
            return True

        except Exception as e:
            self.error(f"ログエクスポートに失敗: {e}", LogCategory.ERROR)
            return False


# グローバルロガーインスタンス
_global_logger = None


def get_logger(name: str = "qt_theme_studio") -> QtThemeStudioLogger:
    """ロガーインスタンスを取得"""
    global _global_logger
    if _global_logger is None:
        _global_logger = QtThemeStudioLogger(name)
    return _global_logger


def setup_logging(
    log_level: LogLevel = LogLevel.INFO,
    log_file: Optional[Union[str, Path]] = None,
    rotation_config: Optional[LogRotationConfig] = None,
) -> None:
    """ログ設定を初期化(拡張版)"""
    global _global_logger

    # 新しい設定でロガーを再作成
    _global_logger = QtThemeStudioLogger(
        "qt_theme_studio", rotation_config or LogRotationConfig()
    )

    # ログレベルの設定
    _global_logger.set_log_level(log_level)

    # カスタムログファイルの設定
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        custom_handler = AdvancedRotatingFileHandler(
            filename=str(file_path),
            maxBytes=rotation_config.max_bytes if rotation_config else 10 * 1024 * 1024,
            backupCount=rotation_config.backup_count if rotation_config else 5,
            encoding="utf-8",
            compress_backups=rotation_config.compress_backups
            if rotation_config
            else True,
        )
        custom_handler.setLevel(logging.DEBUG)
        structured_formatter = StructuredFormatter()
        custom_handler.setFormatter(structured_formatter)

        _global_logger.logger.addHandler(custom_handler)


# 便利な関数
def log_function_call(func_name: str, **kwargs: Any) -> None:
    """関数呼び出しのログ"""
    logger = get_logger()
    context = LogContext(function=func_name, **kwargs)
    logger.debug(f"関数呼び出し: {func_name}", LogCategory.GENERAL, context)


def log_user_action(action: str, user_id: Optional[str] = None, **kwargs: Any) -> None:
    """ユーザーアクションのログ"""
    logger = get_logger()
    context = LogContext(action=action, user_id=user_id, **kwargs)
    logger.info(f"ユーザーアクション: {action}", LogCategory.UI, context)


def log_file_operation(operation: str, file_path: str, **kwargs: Any) -> None:
    """ファイル操作のログ"""
    logger = get_logger()
    context = LogContext(operation=operation, file_path=file_path, **kwargs)
    logger.info(
        f"ファイル操作: {operation} - {file_path}", LogCategory.GENERAL, context
    )


def log_application_startup() -> None:
    """アプリケーション起動のログ"""
    logger = get_logger()
    context = LogContext(event="application_startup")
    logger.info("アプリケーション起動", LogCategory.GENERAL, context)


def log_application_shutdown() -> None:
    """アプリケーション終了のログ"""
    logger = get_logger()
    context = LogContext(event="application_shutdown")
    logger.info("アプリケーション終了", LogCategory.GENERAL, context)
