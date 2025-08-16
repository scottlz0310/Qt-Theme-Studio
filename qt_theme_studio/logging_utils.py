"""
Qt-Theme-Studio ログユーティリティ

このモジュールは、ログシステムの便利な機能とデコレーターを提供します。
"""

import functools
import time
from typing import Any, Callable, Dict, Optional

from .logger import LogCategory, get_logger


def log_function_call(
    category: LogCategory = LogCategory.SYSTEM,
    log_args: bool = False,
    log_result: bool = False,
):
    """
    関数呼び出しをログに記録するデコレーター

    Args:
        category: ログカテゴリ
        log_args: 引数をログに記録するかどうか
        log_result: 戻り値をログに記録するかどうか
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()

            # 関数呼び出し開始ログ
            message = "関数呼び出し開始: {func_name}"
            if log_args and (args or kwargs):
                args_str = ", ".join([str(arg) for arg in args])
                kwargs_str = ", ".join(["{k}={v}" for k, v in kwargs.items()])
                all_args = [args_str, kwargs_str]
                all_args = [arg for arg in all_args if arg]
                if all_args:
                    message += " (引数: {', '.join(all_args)})"

            logger.debug(message, category)

            # パフォーマンス測定開始
            start_time = time.time()

            try:
                # 関数実行
                result = func(*args, **kwargs)

                # 実行時間計算
                time.time() - start_time

                # 成功ログ
                success_message = "関数呼び出し成功: {func_name} ({duration:.3f}秒)"
                if log_result and result is not None:
                    success_message += " (戻り値: {result})"

                logger.debug(success_message, category)

                return result

            except Exception:
                # エラーログ
                time.time() - start_time
                error_message = (
                    "関数呼び出しエラー: {func_name} ({duration:.3f}秒) - {str(e)}"
                )
                logger.error(error_message, category)
                raise

        return wrapper

    return decorator


def log_performance(
    operation_name: Optional[str] = None,
    category: LogCategory = LogCategory.PERFORMANCE,
):
    """
    関数のパフォーマンスを測定してログに記録するデコレーター

    Args:
        operation_name: 操作名（Noneの場合は関数名を使用）
        category: ログカテゴリ
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            op_name = operation_name or f"{func.__module__}.{func.__qualname__}"

            # パフォーマンス測定開始
            logger.start_performance_timer(op_name)

            try:
                result = func(*args, **kwargs)

                # パフォーマンス測定終了
                logger.end_performance_timer(op_name)

                return result

            except Exception as e:
                # エラーが発生した場合もタイマーを終了
                logger.end_performance_timer(op_name, {"error": str(e)})
                raise

        return wrapper

    return decorator


def log_user_action(action_name: Optional[str] = None):
    """
    ユーザー操作をログに記録するデコレーター

    Args:
        action_name: 操作名（Noneの場合は関数名を使用）
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            action = action_name or func.__name__

            # 引数から詳細情報を抽出
            details = {}
            if args:
                details["args_count"] = len(args)
            if kwargs:
                # 機密情報を除外してkwargsを記録
                safe_kwargs = {
                    k: v
                    for k, v in kwargs.items()
                    if not any(
                        sensitive in k.lower()
                        for sensitive in ["password", "token", "key", "secret"]
                    )
                }
                details.update(safe_kwargs)

            try:
                result = func(*args, **kwargs)

                # 成功時のユーザー操作ログ
                details["status"] = "成功"
                logger.log_user_action(action, details)

                return result

            except Exception as e:
                # エラー時のユーザー操作ログ
                details["status"] = "失敗"
                details["error"] = str(e)
                logger.log_user_action(action, details)
                raise

        return wrapper

    return decorator


def log_theme_operation(operation_name: Optional[str] = None):
    """
    テーマ操作をログに記録するデコレーター

    Args:
        operation_name: 操作名（Noneの場合は関数名を使用）
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            operation = operation_name or func.__name__

            # テーマ名を引数から抽出
            theme_name = None
            if args and hasattr(args[0], "name"):
                theme_name = args[0].name
            elif "theme_name" in kwargs:
                theme_name = kwargs["theme_name"]
            elif "theme" in kwargs and hasattr(kwargs["theme"], "name"):
                theme_name = kwargs["theme"].name

            try:
                result = func(*args, **kwargs)

                # 成功時のテーマ操作ログ
                logger.log_theme_operation(operation, theme_name, status="成功")

                return result

            except Exception as e:
                # エラー時のテーマ操作ログ
                logger.log_theme_operation(
                    operation, theme_name, status="失敗", error=str(e)
                )
                raise

        return wrapper

    return decorator


def log_file_operation(operation_name: Optional[str] = None):
    """
    ファイル操作をログに記録するデコレーター

    Args:
        operation_name: 操作名（Noneの場合は関数名を使用）
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            operation = operation_name or func.__name__

            # ファイルパスを引数から抽出
            file_path = None
            if args and isinstance(args[0], (str, type(None))):
                file_path = args[0]
            elif "file_path" in kwargs:
                file_path = kwargs["file_path"]
            elif "path" in kwargs:
                file_path = kwargs["path"]
            elif "filename" in kwargs:
                file_path = kwargs["filename"]

            try:
                result = func(*args, **kwargs)

                # 成功時のファイル操作ログ
                if file_path:
                    logger.log_file_operation(operation, file_path, success=True)

                return result

            except Exception as e:
                # エラー時のファイル操作ログ
                if file_path:
                    logger.log_file_operation(
                        operation, file_path, success=False, error=str(e)
                    )
                raise

        return wrapper

    return decorator


class LogContext:
    """
    ログコンテキストマネージャー

    with文を使用してログのコンテキストを管理します。
    """

    def __init__(
        self, operation: str, category: LogCategory = LogCategory.SYSTEM, **details
    ):
        """
        ログコンテキストを初期化します

        Args:
            operation: 操作名
            category: ログカテゴリ
            **details: 追加詳細情報
        """
        self.operation = operation
        self.category = category
        self.details = details
        self.logger = get_logger()
        self.start_time = None

    def __enter__(self):
        """コンテキスト開始"""
        self.start_time = time.time()
        self.logger.debug("操作開始: {self.operation}", self.category, **self.details)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキスト終了"""
        duration = time.time() - self.start_time if self.start_time else 0

        if exc_type is None:
            # 正常終了
            self.logger.debug(
                "操作完了: {self.operation} ({duration:.3f}秒)",
                self.category,
                duration=duration,
                **self.details,
            )
        else:
            # 例外発生
            self.logger.error(
                "操作エラー: {self.operation} ({duration:.3f}秒) - {str(exc_val)}",
                self.category,
                duration=duration,
                error=str(exc_val),
                **self.details,
            )

    def log(self, message: str, level: str = "info", **kwargs):
        """
        コンテキスト内でログを出力します

        Args:
            message: ログメッセージ
            level: ログレベル
            **kwargs: 追加情報
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        combined_details = {**self.details, **kwargs}
        log_method("{self.operation}: {message}", self.category, **combined_details)


def create_error_context(
    error: Exception, operation: str = "不明な操作"
) -> Dict[str, Any]:
    """
    エラーコンテキスト情報を作成します

    Args:
        error: 例外オブジェクト
        operation: 操作名

    Returns:
        エラーコンテキスト情報
    """
    import sys
    import traceback

    return {
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "python_version": sys.version,
        "timestamp": time.time(),
    }


def log_system_info():
    """システム情報をログに記録します"""
    import platform
    import sys

    logger = get_logger()

    system_info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "machine": platform.machine(),
    }

    logger.info("システム情報", LogCategory.SYSTEM, **system_info)


def log_application_startup():
    """アプリケーション起動ログを記録します"""
    logger = get_logger()
    logger.info("Qt-Theme-Studio アプリケーションを起動しました", LogCategory.SYSTEM)
    log_system_info()


def log_application_shutdown():
    """アプリケーション終了ログを記録します"""
    logger = get_logger()
    logger.info("Qt-Theme-Studio アプリケーションを終了しました", LogCategory.SYSTEM)


def configure_exception_logging():
    """
    未処理例外のログ記録を設定します
    """
    import sys

    def handle_exception(exc_type, exc_value, exc_traceback):
        """未処理例外ハンドラー"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Ctrl+C による中断は通常の終了として扱う
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger = get_logger()
        logger.critical(
            "未処理例外が発生しました: {exc_type.__name__}: {exc_value}",
            LogCategory.ERROR,
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = handle_exception
