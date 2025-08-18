#!/usr/bin/env python3
"""
ワークフロー制御エンジン

全ワークフローの統合制御を行うメインエンジン。
YAML設定ファイルによる柔軟な設定管理とエラーハンドリング機能を提供。
"""

import asyncio
import os
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from qt_theme_studio.logger import get_logger


class WorkflowStatus(Enum):
    """ワークフロー実行ステータス"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """ステップ実行ステータス"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    """ステップ実行結果"""

    name: str
    status: StepStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    output: str = ""
    error: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)

    @property
    def execution_time(self) -> float:
        """実行時間を計算"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return self.duration


@dataclass
class WorkflowResult:
    """ワークフロー実行結果"""

    workflow_name: str
    status: WorkflowStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    steps: List[StepResult] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def execution_time(self) -> float:
        """実行時間を計算"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def success_rate(self) -> float:
        """成功率を計算"""
        if not self.steps:
            return 0.0
        successful_steps = sum(
            1 for step in self.steps if step.status == StepStatus.SUCCESS
        )
        return (successful_steps / len(self.steps)) * 100


class WorkflowError(Exception):
    """ワークフロー関連エラーの基底クラス"""


class ConfigurationError(WorkflowError):
    """設定エラー"""


class ExecutionError(WorkflowError):
    """実行エラー"""


class WorkflowEngine:
    """ワークフロー制御エンジン

    全ワークフローの統合制御を行うメインクラス。
    YAML設定ファイルによる柔軟な設定管理とエラーハンドリング機能を提供。
    """

    def __init__(self, config_path: Optional[str] = None):
        """エンジンを初期化

        Args:
            config_path: 設定ファイルのパス(省略時はデフォルト設定を使用)
        """
        self.logger = get_logger(__name__)
        self.project_root = Path(__file__).parent.parent
        self.config_path = (
            config_path or self.project_root / ".kiro" / "workflow" / "config.yml"
        )
        self.config: Dict[str, Any] = {}
        self.plugins: Dict[str, Any] = {}
        self.current_workflow: Optional[str] = None

        # 設定を読み込み
        self._load_configuration()

        self.logger.info("ワークフローエンジンが初期化されました")

    def _load_configuration(self) -> None:
        """設定ファイルを読み込み"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
                self.logger.info(f"設定ファイルを読み込みました: {self.config_path}")
            else:
                # デフォルト設定を使用
                self.config = self._get_default_config()
                self.logger.warning(
                    f"設定ファイルが見つかりません。デフォルト設定を使用します: {self.config_path}"
                )

            # 環境変数による設定オーバーライド
            self._apply_environment_overrides()

        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
            raise ConfigurationError(f"設定ファイルの読み込みエラー: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を取得"""
        return {
            "workflows": {
                "pre_commit": {
                    "enabled": True,
                    "steps": [
                        {
                            "name": "ruff_lint",
                            "command": "ruff check .",
                            "required": True,
                        },
                        {
                            "name": "ruff_format",
                            "command": "ruff format --check .",
                            "required": True,
                        },
                        {
                            "name": "basic_tests",
                            "command": "pytest tests/unit/ -x",
                            "required": False,
                        },
                    ],
                },
                "ci_pipeline": {
                    "enabled": True,
                    "steps": [
                        {
                            "name": "quality_check",
                            "command": "python scripts/quality_check.py",
                            "required": True,
                        },
                        {"name": "full_tests", "command": "pytest", "required": True},
                        {
                            "name": "security_scan",
                            "command": "python scripts/security_scanner.py",
                            "required": False,
                        },
                    ],
                },
                "release": {
                    "enabled": True,
                    "steps": [
                        {"name": "final_tests", "command": "pytest", "required": True},
                        {
                            "name": "build_packages",
                            "command": "python -m build",
                            "required": True,
                        },
                        {
                            "name": "generate_checksums",
                            "command": "python scripts/build_release.py --checksums",
                            "required": True,
                        },
                    ],
                },
            },
            "quality_thresholds": {
                "coverage_minimum": 80,
                "test_success_rate": 95,
                "security_score": 8.0,
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

    def _apply_environment_overrides(self) -> None:
        """環境変数による設定オーバーライドを適用"""
        # 品質閾値のオーバーライド
        if coverage_min := os.getenv("WORKFLOW_COVERAGE_MIN"):
            try:
                self.config.setdefault("quality_thresholds", {})["coverage_minimum"] = (
                    float(coverage_min)
                )
                self.logger.info(f"カバレッジ最小値を環境変数で上書き: {coverage_min}%")
            except ValueError:
                self.logger.warning(f"無効なカバレッジ値: {coverage_min}")

        # ログレベルのオーバーライド
        if log_level := os.getenv("WORKFLOW_LOG_LEVEL"):
            self.config.setdefault("logging", {})["level"] = log_level.upper()
            self.logger.info(f"ログレベルを環境変数で上書き: {log_level}")

    def validate_environment(self) -> bool:
        """環境の妥当性を検証

        Returns:
            環境が有効な場合True
        """
        try:
            self.logger.info("環境の妥当性を検証中...")

            # Python バージョンチェック
            if sys.version_info < (3, 8):
                self.logger.error(
                    f"Python 3.8以上が必要です。現在のバージョン: {sys.version}"
                )
                return False

            # 必要なディレクトリの存在確認
            required_dirs = ["scripts", "qt_theme_studio", "tests"]
            for dir_name in required_dirs:
                dir_path = self.project_root / dir_name
                if not dir_path.exists():
                    self.logger.error(f"必要なディレクトリが見つかりません: {dir_path}")
                    return False

            # 設定の妥当性チェック
            if not self.config.get("workflows"):
                self.logger.error("ワークフロー設定が見つかりません")
                return False

            self.logger.info("環境の検証が完了しました")
            return True

        except Exception as e:
            self.logger.error(f"環境検証中にエラーが発生しました: {e}")
            return False

    async def execute_pipeline(self, pipeline_name: str, **kwargs) -> WorkflowResult:
        """指定されたパイプラインを実行

        Args:
            pipeline_name: 実行するパイプライン名
            **kwargs: パイプライン固有のパラメータ

        Returns:
            実行結果
        """
        self.current_workflow = pipeline_name
        result = WorkflowResult(
            workflow_name=pipeline_name,
            status=WorkflowStatus.PENDING,
            start_time=datetime.now(),
        )

        try:
            self.logger.info(f"パイプライン '{pipeline_name}' の実行を開始します")

            # パイプライン設定を取得
            pipeline_config = self.config.get("workflows", {}).get(pipeline_name)
            if not pipeline_config:
                raise ConfigurationError(
                    f"パイプライン '{pipeline_name}' の設定が見つかりません"
                )

            if not pipeline_config.get("enabled", True):
                self.logger.info(f"パイプライン '{pipeline_name}' は無効化されています")
                result.status = WorkflowStatus.SKIPPED
                return result

            result.status = WorkflowStatus.RUNNING

            # ステップを順次実行
            steps = pipeline_config.get("steps", [])
            for step_config in steps:
                step_result = await self._execute_step(step_config, **kwargs)
                result.steps.append(step_result)

                # 必須ステップが失敗した場合は中断
                if step_result.status == StepStatus.FAILURE and step_config.get(
                    "required", True
                ):
                    self.logger.error(
                        f"必須ステップ '{step_result.name}' が失敗しました。パイプラインを中断します"
                    )
                    result.status = WorkflowStatus.FAILURE
                    break

            # 最終ステータスを決定
            if result.status == WorkflowStatus.RUNNING:
                failed_steps = [
                    s for s in result.steps if s.status == StepStatus.FAILURE
                ]
                if failed_steps:
                    result.status = WorkflowStatus.WARNING
                else:
                    result.status = WorkflowStatus.SUCCESS

            result.end_time = datetime.now()

            self.logger.info(
                f"パイプライン '{pipeline_name}' が完了しました "
                f"(ステータス: {result.status.value}, 実行時間: {result.execution_time:.2f}秒)"
            )

            return result

        except Exception as e:
            result.status = WorkflowStatus.FAILURE
            result.error = str(e)
            result.end_time = datetime.now()

            self.logger.error(
                f"パイプライン '{pipeline_name}' の実行中にエラーが発生しました: {e}"
            )
            self.logger.debug(traceback.format_exc())

            return result

        finally:
            self.current_workflow = None

    async def _execute_step(self, step_config: Dict[str, Any], **kwargs) -> StepResult:
        """個別ステップを実行

        Args:
            step_config: ステップ設定
            **kwargs: 実行パラメータ

        Returns:
            ステップ実行結果
        """
        step_name = step_config.get("name", "unknown")
        result = StepResult(
            name=step_name, status=StepStatus.PENDING, start_time=datetime.now()
        )

        try:
            self.logger.info(f"ステップ '{step_name}' を実行中...")
            result.status = StepStatus.RUNNING

            # コマンド実行
            command = step_config.get("command")
            if command:
                # 環境変数やパラメータでコマンドを置換
                formatted_command = command.format(**kwargs)

                # 非同期でコマンド実行
                process = await asyncio.create_subprocess_shell(
                    formatted_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    cwd=self.project_root,
                )

                stdout, _ = await process.communicate()
                result.output = stdout.decode("utf-8", errors="ignore")

                if process.returncode == 0:
                    result.status = StepStatus.SUCCESS
                    self.logger.info(f"ステップ '{step_name}' が正常に完了しました")
                else:
                    result.status = StepStatus.FAILURE
                    result.error = (
                        f"コマンドが終了コード {process.returncode} で失敗しました"
                    )
                    self.logger.error(
                        f"ステップ '{step_name}' が失敗しました: {result.error}"
                    )
            else:
                # カスタムステップ実行(プラグイン対応)
                plugin_name = step_config.get("plugin")
                if plugin_name and plugin_name in self.plugins:
                    plugin_result = await self.plugins[plugin_name].execute(
                        step_config, **kwargs
                    )
                    result.status = (
                        StepStatus.SUCCESS if plugin_result else StepStatus.FAILURE
                    )
                else:
                    result.status = StepStatus.SKIPPED
                    self.logger.warning(
                        f"ステップ '{step_name}' をスキップしました(コマンドまたはプラグインが指定されていません)"
                    )

        except Exception as e:
            result.status = StepStatus.FAILURE
            result.error = str(e)
            self.logger.error(
                f"ステップ '{step_name}' の実行中にエラーが発生しました: {e}"
            )

        finally:
            result.end_time = datetime.now()
            result.duration = result.execution_time

        return result

    def get_available_workflows(self) -> List[str]:
        """利用可能なワークフロー一覧を取得

        Returns:
            ワークフロー名のリスト
        """
        return list(self.config.get("workflows", {}).keys())

    def get_workflow_config(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """指定されたワークフローの設定を取得

        Args:
            workflow_name: ワークフロー名

        Returns:
            ワークフロー設定(存在しない場合はNone)
        """
        return self.config.get("workflows", {}).get(workflow_name)

    def register_plugin(self, name: str, plugin: Any) -> None:
        """プラグインを登録

        Args:
            name: プラグイン名
            plugin: プラグインオブジェクト
        """
        self.plugins[name] = plugin
        self.logger.info(f"プラグイン '{name}' が登録されました")

    def reload_configuration(self) -> None:
        """設定を再読み込み"""
        try:
            self._load_configuration()
            self.logger.info("設定が再読み込みされました")
        except Exception as e:
            self.logger.error(f"設定の再読み込みに失敗しました: {e}")
            raise


async def main():
    """メイン実行関数(テスト用)"""
    engine = WorkflowEngine()

    # 環境検証
    if not engine.validate_environment():
        print("環境検証に失敗しました")
        return 1

    # 利用可能なワークフロー表示
    workflows = engine.get_available_workflows()
    print(f"利用可能なワークフロー: {', '.join(workflows)}")

    # テスト実行(引数で指定されたワークフローを実行)
    if len(sys.argv) > 1:
        workflow_name = sys.argv[1]
        if workflow_name in workflows:
            result = await engine.execute_pipeline(workflow_name)
            print(f"実行結果: {result.status.value}")
            print(f"実行時間: {result.execution_time:.2f}秒")
            print(f"成功率: {result.success_rate:.1f}%")
            return (
                0
                if result.status in [WorkflowStatus.SUCCESS, WorkflowStatus.WARNING]
                else 1
            )
        print(f"不明なワークフロー: {workflow_name}")
        return 1

    return 0


if __name__ == "__main__":
    import asyncio

    sys.exit(asyncio.run(main()))
