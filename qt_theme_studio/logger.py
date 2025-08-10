"""
Qt-Theme-Studio 日本語ログシステム

このモジュールは、Qt-Theme-Studioアプリケーションの日本語ログシステムを実装します。
すべてのログメッセージを日本語で出力し、ユーザー操作ログとパフォーマンスログ機能を提供します。
"""

import logging
import logging.handlers
import os
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from enum import Enum


class LogLevel(Enum):
    """ログレベル定義"""
    DEBUG = "デバッグ"
    INFO = "情報"
    WARNING = "警告"
    ERROR = "エラー"
    CRITICAL = "重大"


class LogCategory(Enum):
    """ログカテゴリ定義"""
    SYSTEM = "システム"
    USER_ACTION = "ユーザー操作"
    PERFORMANCE = "パフォーマンス"
    THEME = "テーマ"
    UI = "ユーザーインターフェース"
    FILE_IO = "ファイル入出力"
    NETWORK = "ネットワーク"
    ERROR = "エラー"


class JapaneseFormatter(logging.Formatter):
    """
    日本語ログフォーマッター
    
    ログメッセージを日本語形式でフォーマットします。
    """
    
    # ログレベルの日本語マッピング
    LEVEL_MAPPING = {
        logging.DEBUG: LogLevel.DEBUG.value,
        logging.INFO: LogLevel.INFO.value,
        logging.WARNING: LogLevel.WARNING.value,
        logging.ERROR: LogLevel.ERROR.value,
        logging.CRITICAL: LogLevel.CRITICAL.value
    }
    
    def __init__(self, include_thread: bool = False):
        """
        フォーマッターを初期化します
        
        Args:
            include_thread: スレッド情報を含めるかどうか
        """
        self.include_thread = include_thread
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        ログレコードを日本語形式でフォーマットします
        
        Args:
            record: ログレコード
            
        Returns:
            フォーマット済みログメッセージ
        """
        # 日本語レベル名を取得
        japanese_level = self.LEVEL_MAPPING.get(record.levelno, "不明")
        
        # 日時を日本語形式でフォーマット
        dt = datetime.datetime.fromtimestamp(record.created)
        timestamp = dt.strftime("%Y年%m月%d日 %H:%M:%S")
        
        # カテゴリ情報を取得
        category = getattr(record, 'category', LogCategory.SYSTEM.value)
        
        # 基本フォーマット
        formatted_message = f"[{timestamp}] [{japanese_level}] [{category}] {record.getMessage()}"
        
        # スレッド情報を含める場合
        if self.include_thread and hasattr(record, 'thread'):
            formatted_message += f" (スレッド: {record.thread})"
        
        # モジュール情報を追加
        if hasattr(record, 'module') and record.module:
            formatted_message += f" ({record.module})"
        
        # 例外情報がある場合は追加
        if record.exc_info and record.exc_info != True:
            formatted_message += f"\n例外詳細:\n{self.formatException(record.exc_info)}"
        
        return formatted_message


class Logger:
    """
    Qt-Theme-Studio 日本語ログシステム
    
    すべてのログメッセージを日本語で出力し、
    ユーザー操作ログとパフォーマンスログ機能を提供します。
    """
    
    def __init__(self, name: str = "qt_theme_studio", log_directory: Optional[str] = None):
        """
        ロガーを初期化します
        
        Args:
            name: ロガー名
            log_directory: ログディレクトリパス（Noneの場合はデフォルト）
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # ログディレクトリの設定
        if log_directory:
            self.log_directory = Path(log_directory)
        else:
            self.log_directory = Path.home() / ".qt_theme_studio" / "logs"
        
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # パフォーマンス測定用
        self.performance_timers: Dict[str, float] = {}
        
        # ユーザー操作履歴
        self.user_actions: list = []
        
        # ログハンドラーの設定
        self.setup_handlers()
    
    def setup_handlers(self) -> None:
        """ログハンドラーを設定します"""
        # 既存のハンドラーをクリア
        self.logger.handlers.clear()
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = JapaneseFormatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # ファイルハンドラー（一般ログ）
        log_file = self.log_directory / "qt_theme_studio.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = JapaneseFormatter(include_thread=True)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # エラーログ専用ハンドラー
        error_log_file = self.log_directory / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # ユーザー操作ログ専用ハンドラー
        user_action_log_file = self.log_directory / "user_actions.log"
        user_action_handler = logging.handlers.RotatingFileHandler(
            user_action_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        user_action_handler.setLevel(logging.INFO)
        user_action_handler.addFilter(self._user_action_filter)
        user_action_handler.setFormatter(file_formatter)
        self.logger.addHandler(user_action_handler)
        
        # パフォーマンスログ専用ハンドラー
        performance_log_file = self.log_directory / "performance.log"
        performance_handler = logging.handlers.RotatingFileHandler(
            performance_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.addFilter(self._performance_filter)
        performance_handler.setFormatter(file_formatter)
        self.logger.addHandler(performance_handler)
    
    def _user_action_filter(self, record: logging.LogRecord) -> bool:
        """ユーザー操作ログフィルター"""
        return getattr(record, 'category', '') == LogCategory.USER_ACTION.value
    
    def _performance_filter(self, record: logging.LogRecord) -> bool:
        """パフォーマンスログフィルター"""
        return getattr(record, 'category', '') == LogCategory.PERFORMANCE.value
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs) -> None:
        """
        デバッグログを出力します
        
        Args:
            message: ログメッセージ
            category: ログカテゴリ
            **kwargs: 追加情報
        """
        self._log(logging.DEBUG, message, category, **kwargs)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs) -> None:
        """
        情報ログを出力します
        
        Args:
            message: ログメッセージ
            category: ログカテゴリ
            **kwargs: 追加情報
        """
        self._log(logging.INFO, message, category, **kwargs)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs) -> None:
        """
        警告ログを出力します
        
        Args:
            message: ログメッセージ
            category: ログカテゴリ
            **kwargs: 追加情報
        """
        self._log(logging.WARNING, message, category, **kwargs)
    
    def error(self, message: str, category: LogCategory = LogCategory.ERROR, **kwargs) -> None:
        """
        エラーログを出力します
        
        Args:
            message: ログメッセージ
            category: ログカテゴリ
            **kwargs: 追加情報
        """
        self._log(logging.ERROR, message, category, **kwargs)
    
    def critical(self, message: str, category: LogCategory = LogCategory.ERROR, **kwargs) -> None:
        """
        重大エラーログを出力します
        
        Args:
            message: ログメッセージ
            category: ログカテゴリ
            **kwargs: 追加情報
        """
        self._log(logging.CRITICAL, message, category, **kwargs)
    
    def log_error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """
        エラーログを記録します（例外情報付き）
        
        Args:
            message: エラーメッセージ
            exception: 例外オブジェクト
            **kwargs: 追加情報
        """
        extra = {
            'category': LogCategory.ERROR.value,
            **kwargs
        }
        
        if exception:
            self.logger.error(message, exc_info=exception, extra=extra)
        else:
            self.logger.error(message, extra=extra)
    
    def log_user_action(self, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        ユーザー操作ログを記録します
        
        Args:
            action: 操作名
            details: 操作詳細
        """
        details = details or {}
        
        # ユーザー操作履歴に追加
        action_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.user_actions.append(action_record)
        
        # 履歴の上限を設定（最新1000件を保持）
        if len(self.user_actions) > 1000:
            self.user_actions = self.user_actions[-1000:]
        
        # ログ出力
        message = f"ユーザー操作: {action}"
        if details:
            details_str = ", ".join([f"{k}={v}" for k, v in details.items()])
            message += f" ({details_str})"
        
        extra = {
            'category': LogCategory.USER_ACTION.value,
            'action': action,
            'details': details
        }
        
        self.logger.info(message, extra=extra)
    
    def start_performance_timer(self, operation: str) -> None:
        """
        パフォーマンス測定を開始します
        
        Args:
            operation: 操作名
        """
        self.performance_timers[operation] = time.time()
        self.debug(f"パフォーマンス測定開始: {operation}", LogCategory.PERFORMANCE)
    
    def end_performance_timer(self, operation: str, details: Optional[Dict[str, Any]] = None) -> float:
        """
        パフォーマンス測定を終了し、結果をログに記録します
        
        Args:
            operation: 操作名
            details: 追加詳細情報
            
        Returns:
            経過時間（秒）
        """
        if operation not in self.performance_timers:
            self.warning(f"パフォーマンス測定が開始されていません: {operation}", LogCategory.PERFORMANCE)
            return 0.0
        
        start_time = self.performance_timers.pop(operation)
        duration = time.time() - start_time
        
        self.log_performance(operation, duration, details)
        
        return duration
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None) -> None:
        """
        パフォーマンスログを記録します
        
        Args:
            operation: 操作名
            duration: 実行時間（秒）
            details: 追加詳細情報
        """
        details = details or {}
        
        # パフォーマンス評価
        if duration < 0.1:
            performance_level = "高速"
        elif duration < 0.5:
            performance_level = "普通"
        elif duration < 2.0:
            performance_level = "やや遅い"
        else:
            performance_level = "遅い"
        
        message = f"パフォーマンス: {operation} - {duration:.3f}秒 ({performance_level})"
        
        if details:
            details_str = ", ".join([f"{k}={v}" for k, v in details.items()])
            message += f" - {details_str}"
        
        extra = {
            'category': LogCategory.PERFORMANCE.value,
            'operation': operation,
            'duration': duration,
            'performance_level': performance_level,
            'details': details
        }
        
        self.logger.info(message, extra=extra)
    
    def log_theme_operation(self, operation: str, theme_name: Optional[str] = None, **kwargs) -> None:
        """
        テーマ操作ログを記録します
        
        Args:
            operation: 操作名
            theme_name: テーマ名
            **kwargs: 追加情報
        """
        message = f"テーマ操作: {operation}"
        if theme_name:
            message += f" (テーマ: {theme_name})"
        
        extra = {
            'operation': operation,
            'theme_name': theme_name,
            **kwargs
        }
        
        self._log(logging.INFO, message, LogCategory.THEME, **extra)
    
    def log_file_operation(self, operation: str, file_path: str, success: bool = True, **kwargs) -> None:
        """
        ファイル操作ログを記録します
        
        Args:
            operation: 操作名
            file_path: ファイルパス
            success: 操作成功フラグ
            **kwargs: 追加情報
        """
        status = "成功" if success else "失敗"
        message = f"ファイル操作: {operation} - {file_path} ({status})"
        
        extra = {
            'operation': operation,
            'file_path': file_path,
            'success': success,
            **kwargs
        }
        
        if success:
            self._log(logging.INFO, message, LogCategory.FILE_IO, **extra)
        else:
            self._log(logging.ERROR, message, LogCategory.FILE_IO, **extra)
    
    def log_ui_event(self, event: str, widget: Optional[str] = None, **kwargs) -> None:
        """
        UI イベントログを記録します
        
        Args:
            event: イベント名
            widget: ウィジェット名
            **kwargs: 追加情報
        """
        message = f"UIイベント: {event}"
        if widget:
            message += f" (ウィジェット: {widget})"
        
        extra = {
            'event': event,
            'widget': widget,
            **kwargs
        }
        
        self._log(logging.DEBUG, message, LogCategory.UI, **extra)
    
    def _log(self, level: int, message: str, category: LogCategory, **kwargs) -> None:
        """
        内部ログ出力メソッド
        
        Args:
            level: ログレベル
            message: メッセージ
            category: カテゴリ
            **kwargs: 追加情報
        """
        extra = {
            'category': category.value,
            **kwargs
        }
        
        self.logger.log(level, message, extra=extra)
    
    def get_user_action_history(self, limit: int = 100) -> list:
        """
        ユーザー操作履歴を取得します
        
        Args:
            limit: 取得件数の上限
            
        Returns:
            ユーザー操作履歴のリスト
        """
        return self.user_actions[-limit:] if limit > 0 else self.user_actions
    
    def export_logs(self, output_file: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> bool:
        """
        ログをファイルにエクスポートします
        
        Args:
            output_file: 出力ファイルパス
            start_date: 開始日時
            end_date: 終了日時
            
        Returns:
            エクスポート成功フラグ
        """
        try:
            export_data = {
                "export_timestamp": datetime.datetime.now().isoformat(),
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "user_actions": self.get_user_action_history(),
                "log_files": {
                    "main_log": str(self.log_directory / "qt_theme_studio.log"),
                    "error_log": str(self.log_directory / "errors.log"),
                    "user_action_log": str(self.log_directory / "user_actions.log"),
                    "performance_log": str(self.log_directory / "performance.log")
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.info(f"ログをエクスポートしました: {output_file}", LogCategory.SYSTEM)
            return True
            
        except Exception as e:
            self.error(f"ログのエクスポートに失敗しました: {str(e)}", LogCategory.SYSTEM)
            return False
    
    def cleanup_old_logs(self, days_to_keep: int = 30) -> None:
        """
        古いログファイルをクリーンアップします
        
        Args:
            days_to_keep: 保持する日数
        """
        try:
            import time
            
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            cleaned_files = []
            
            for log_file in self.log_directory.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    cleaned_files.append(str(log_file))
            
            if cleaned_files:
                self.info(f"古いログファイルを削除しました: {len(cleaned_files)}個", LogCategory.SYSTEM)
            
        except Exception as e:
            self.error(f"ログファイルのクリーンアップに失敗しました: {str(e)}", LogCategory.SYSTEM)


# グローバルロガーインスタンス
_global_logger: Optional[Logger] = None


def get_logger(name: str = "qt_theme_studio") -> Logger:
    """
    グローバルロガーインスタンスを取得します
    
    Args:
        name: ロガー名
        
    Returns:
        ロガーインスタンス
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = Logger(name)
    
    return _global_logger


def setup_logging(log_directory: Optional[str] = None, log_level: str = "INFO") -> Logger:
    """
    ログシステムを初期化します
    
    Args:
        log_directory: ログディレクトリパス
        log_level: ログレベル
        
    Returns:
        初期化されたロガーインスタンス
    """
    global _global_logger
    
    _global_logger = Logger("qt_theme_studio", log_directory)
    
    # ログレベルの設定
    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    if log_level.upper() in level_mapping:
        _global_logger.logger.setLevel(level_mapping[log_level.upper()])
    
    _global_logger.info("ログシステムを初期化しました", LogCategory.SYSTEM)
    
    return _global_logger