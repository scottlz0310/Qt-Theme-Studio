#!/usr/bin/env python3
"""
統合設定管理システム

ワークフロー設定の読み込み、検証、自動修正機能を提供。
環境変数オーバーライドと設定の動的更新をサポート。
"""

import copy
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from qt_theme_studio.logger import get_logger


@dataclass
class ValidationResult:
    """設定検証結果"""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ConfigChange:
    """設定変更記録"""

    timestamp: datetime
    path: str
    old_value: Any
    new_value: Any
    source: str  # 'file', 'environment', 'api'
    reason: str


class ConfigurationError(Exception):
    """設定エラー"""


class ConfigManager:
    """統合設定管理クラス

    ワークフロー設定の読み込み、検証、自動修正機能を提供。
    環境変数オーバーライドと設定の動的更新をサポート。
    """

    def __init__(self, config_path: Optional[str] = None):
        """設定マネージャーを初期化

        Args:
            config_path: 設定ファイルのパス（省略時はデフォルト）
        """
        self.logger = get_logger(__name__)
        self.project_root = Path(__file__).parent.parent
        self.config_path = (
            Path(config_path)
            if config_path
            else self.project_root / ".kiro" / "workflow" / "config.yml"
        )

        # 設定データ
        self.config: Dict[str, Any] = {}
        self.original_config: Dict[str, Any] = {}
        self.change_history: List[ConfigChange] = []

        # 環境変数マッピング
        self.env_mappings = {
            "WORKFLOW_LOG_LEVEL": "notifications.channels.0.level",
            "WORKFLOW_COVERAGE_MIN": "quality_thresholds.coverage_minimum",
            "WORKFLOW_TIMEOUT": "workflows.ci_pipeline.timeout",
            "WORKFLOW_DEBUG": "environments.development.debug",
            "WORKFLOW_PARALLEL": "workflows.ci_pipeline.parallel",
            "WORKFLOW_CACHE_ENABLED": "cache.enabled",
            "WORKFLOW_NOTIFICATIONS": "notifications.enabled",
        }

        # 設定スキーマ（検証用）
        self.schema = self._get_config_schema()

        # 設定を読み込み
        self.load_config()

        self.logger.info("設定マネージャーが初期化されました")

    def load_config(self) -> None:
        """設定ファイルを読み込み"""
        try:
            if self.config_path.exists():
                with open(self.config_path, encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
                self.original_config = copy.deepcopy(self.config)
                self.logger.info(f"設定ファイルを読み込みました: {self.config_path}")
            else:
                # デフォルト設定を作成
                self.config = self._get_default_config()
                self.original_config = copy.deepcopy(self.config)
                self._create_default_config_file()
                self.logger.info(
                    f"デフォルト設定ファイルを作成しました: {self.config_path}"
                )

            # 環境変数オーバーライドを適用
            self._apply_environment_overrides()

            # 設定を検証
            validation_result = self.validate_config()
            if not validation_result.is_valid:
                self.logger.warning("設定に問題があります:")
                for error in validation_result.errors:
                    self.logger.error(f"  エラー: {error}")
                for warning in validation_result.warnings:
                    self.logger.warning(f"  警告: {warning}")

                # 自動修正を試行
                if self._auto_fix_config():
                    self.logger.info("設定の自動修正が完了しました")
                else:
                    raise ConfigurationError("設定の自動修正に失敗しました")

        except Exception as e:
            self.logger.error(f"設定の読み込みに失敗しました: {e}")
            raise ConfigurationError(f"設定読み込みエラー: {e}")

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
                    ],
                }
            },
            "quality_thresholds": {"coverage_minimum": 80, "test_success_rate": 95},
            "notifications": {
                "enabled": True,
                "channels": [{"type": "console", "level": "INFO"}],
            },
        }

    def _create_default_config_file(self) -> None:
        """デフォルト設定ファイルを作成"""
        try:
            # ディレクトリを作成
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # 設定ファイルを作成
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            self.logger.info(
                f"デフォルト設定ファイルを作成しました: {self.config_path}"
            )

        except Exception as e:
            self.logger.error(f"設定ファイルの作成に失敗しました: {e}")
            raise

    def _apply_environment_overrides(self) -> None:
        """環境変数による設定オーバーライドを適用"""
        for env_var, config_path in self.env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    # 値の型変換
                    converted_value = self._convert_env_value(env_value)

                    # 設定パスに値を設定
                    old_value = self._get_config_value(config_path)
                    self._set_config_value(config_path, converted_value)

                    # 変更を記録
                    self._record_change(
                        config_path,
                        old_value,
                        converted_value,
                        "environment",
                        f"環境変数 {env_var}",
                    )

                    self.logger.info(
                        f"環境変数 {env_var} で設定を上書き: {config_path} = {converted_value}"
                    )

                except Exception as e:
                    self.logger.warning(f"環境変数 {env_var} の処理に失敗しました: {e}")

    def _convert_env_value(self, value: str) -> Any:
        """環境変数の値を適切な型に変換"""
        # ブール値
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False

        # 数値
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # JSON形式
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

        # 文字列
        return value

    def _get_config_value(self, path: str) -> Any:
        """設定パスから値を取得"""
        keys = path.split(".")
        current = self.config

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None

        return current

    def _set_config_value(self, path: str, value: Any) -> None:
        """設定パスに値を設定"""
        keys = path.split(".")
        current = self.config

        # 最後のキー以外を辿る
        for key in keys[:-1]:
            if key.isdigit():
                index = int(key)
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    raise ValueError(f"無効なリストインデックス: {key}")
            else:
                if not isinstance(current, dict):
                    raise ValueError(f"辞書でない要素にキーアクセス: {key}")
                if key not in current:
                    current[key] = {}
                current = current[key]

        # 最後のキーに値を設定
        last_key = keys[-1]
        if last_key.isdigit():
            index = int(last_key)
            if isinstance(current, list) and 0 <= index < len(current):
                current[index] = value
            else:
                raise ValueError(f"無効なリストインデックス: {last_key}")
        else:
            if not isinstance(current, dict):
                raise ValueError(f"辞書でない要素にキーアクセス: {last_key}")
            current[last_key] = value

    def _record_change(
        self, path: str, old_value: Any, new_value: Any, source: str, reason: str
    ) -> None:
        """設定変更を記録"""
        change = ConfigChange(
            timestamp=datetime.now(),
            path=path,
            old_value=old_value,
            new_value=new_value,
            source=source,
            reason=reason,
        )
        self.change_history.append(change)

    def validate_config(self) -> ValidationResult:
        """設定を検証

        Returns:
            検証結果
        """
        result = ValidationResult(is_valid=True)

        try:
            # 必須セクションの確認
            required_sections = ["workflows", "quality_thresholds", "notifications"]
            for section in required_sections:
                if section not in self.config:
                    result.errors.append(f"必須セクション '{section}' が見つかりません")
                    result.is_valid = False

            # ワークフロー設定の検証
            if "workflows" in self.config:
                self._validate_workflows(self.config["workflows"], result)

            # 品質閾値の検証
            if "quality_thresholds" in self.config:
                self._validate_quality_thresholds(
                    self.config["quality_thresholds"], result
                )

            # 通知設定の検証
            if "notifications" in self.config:
                self._validate_notifications(self.config["notifications"], result)

            # 環境設定の検証
            if "environments" in self.config:
                self._validate_environments(self.config["environments"], result)

        except Exception as e:
            result.errors.append(f"設定検証中にエラーが発生しました: {e}")
            result.is_valid = False

        return result

    def _validate_workflows(
        self, workflows: Dict[str, Any], result: ValidationResult
    ) -> None:
        """ワークフロー設定を検証"""
        for workflow_name, workflow_config in workflows.items():
            if not isinstance(workflow_config, dict):
                result.errors.append(
                    f"ワークフロー '{workflow_name}' の設定が辞書ではありません"
                )
                continue

            # 必須フィールドの確認
            if "steps" not in workflow_config:
                result.errors.append(
                    f"ワークフロー '{workflow_name}' にstepsが定義されていません"
                )
                continue

            # ステップの検証
            steps = workflow_config["steps"]
            if not isinstance(steps, list):
                result.errors.append(
                    f"ワークフロー '{workflow_name}' のstepsがリストではありません"
                )
                continue

            for i, step in enumerate(steps):
                if not isinstance(step, dict):
                    result.errors.append(
                        f"ワークフロー '{workflow_name}' のステップ {i} が辞書ではありません"
                    )
                    continue

                if "name" not in step:
                    result.errors.append(
                        f"ワークフロー '{workflow_name}' のステップ {i} にnameが定義されていません"
                    )

                if "command" not in step and "plugin" not in step:
                    result.warnings.append(
                        f"ワークフロー '{workflow_name}' のステップ '{step.get('name', i)}' にcommandまたはpluginが定義されていません"
                    )

    def _validate_quality_thresholds(
        self, thresholds: Dict[str, Any], result: ValidationResult
    ) -> None:
        """品質閾値設定を検証"""
        # カバレッジ閾値
        if "coverage_minimum" in thresholds:
            coverage = thresholds["coverage_minimum"]
            if not isinstance(coverage, (int, float)) or not 0 <= coverage <= 100:
                result.errors.append(
                    "coverage_minimumは0-100の数値である必要があります"
                )

        # テスト成功率
        if "test_success_rate" in thresholds:
            success_rate = thresholds["test_success_rate"]
            if (
                not isinstance(success_rate, (int, float))
                or not 0 <= success_rate <= 100
            ):
                result.errors.append(
                    "test_success_rateは0-100の数値である必要があります"
                )

        # セキュリティスコア
        if "security_score" in thresholds:
            security_score = thresholds["security_score"]
            if (
                not isinstance(security_score, (int, float))
                or not 0 <= security_score <= 10
            ):
                result.errors.append("security_scoreは0-10の数値である必要があります")

    def _validate_notifications(
        self, notifications: Dict[str, Any], result: ValidationResult
    ) -> None:
        """通知設定を検証"""
        if "channels" in notifications:
            channels = notifications["channels"]
            if not isinstance(channels, list):
                result.errors.append(
                    "notification channelsはリストである必要があります"
                )
                return

            for i, channel in enumerate(channels):
                if not isinstance(channel, dict):
                    result.errors.append(f"通知チャンネル {i} が辞書ではありません")
                    continue

                if "type" not in channel:
                    result.errors.append(
                        f"通知チャンネル {i} にtypeが定義されていません"
                    )

                channel_type = channel.get("type")
                if channel_type not in ["console", "file", "email"]:
                    result.warnings.append(
                        f"未知の通知チャンネルタイプ: {channel_type}"
                    )

    def _validate_environments(
        self, environments: Dict[str, Any], result: ValidationResult
    ) -> None:
        """環境設定を検証"""
        valid_environments = ["development", "testing", "production", "ci"]

        for env_name, env_config in environments.items():
            if env_name not in valid_environments:
                result.warnings.append(f"未知の環境名: {env_name}")

            if not isinstance(env_config, dict):
                result.errors.append(f"環境 '{env_name}' の設定が辞書ではありません")

    def _auto_fix_config(self) -> bool:
        """設定の自動修正を試行

        Returns:
            修正が成功した場合True
        """
        try:
            fixed = False

            # 必須セクションの追加
            if "workflows" not in self.config:
                self.config["workflows"] = {}
                fixed = True
                self.logger.info("必須セクション 'workflows' を追加しました")

            if "quality_thresholds" not in self.config:
                self.config["quality_thresholds"] = {
                    "coverage_minimum": 80,
                    "test_success_rate": 95,
                }
                fixed = True
                self.logger.info("必須セクション 'quality_thresholds' を追加しました")

            if "notifications" not in self.config:
                self.config["notifications"] = {
                    "enabled": True,
                    "channels": [{"type": "console", "level": "INFO"}],
                }
                fixed = True
                self.logger.info("必須セクション 'notifications' を追加しました")

            # 無効な値の修正
            thresholds = self.config.get("quality_thresholds", {})

            # カバレッジ閾値の修正
            coverage = thresholds.get("coverage_minimum")
            if coverage is not None and (
                not isinstance(coverage, (int, float)) or not 0 <= coverage <= 100
            ):
                thresholds["coverage_minimum"] = 80
                fixed = True
                self.logger.info("無効なcoverage_minimumを80に修正しました")

            # テスト成功率の修正
            success_rate = thresholds.get("test_success_rate")
            if success_rate is not None and (
                not isinstance(success_rate, (int, float))
                or not 0 <= success_rate <= 100
            ):
                thresholds["test_success_rate"] = 95
                fixed = True
                self.logger.info("無効なtest_success_rateを95に修正しました")

            return fixed

        except Exception as e:
            self.logger.error(f"設定の自動修正中にエラーが発生しました: {e}")
            return False

    def get_config(self, path: Optional[str] = None) -> Any:
        """設定値を取得

        Args:
            path: 設定パス（省略時は全設定を返す）

        Returns:
            設定値
        """
        if path is None:
            return copy.deepcopy(self.config)

        return self._get_config_value(path)

    def set_config(self, path: str, value: Any, source: str = "api") -> None:
        """設定値を更新

        Args:
            path: 設定パス
            value: 新しい値
            source: 変更元
        """
        old_value = self._get_config_value(path)
        self._set_config_value(path, value)
        self._record_change(path, old_value, value, source, "API経由での設定変更")

        self.logger.info(f"設定を更新しました: {path} = {value}")

    def save_config(self) -> None:
        """設定をファイルに保存"""
        try:
            # バックアップを作成
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix(".yml.backup")
                backup_path.write_text(
                    self.config_path.read_text(encoding="utf-8"), encoding="utf-8"
                )

            # 設定を保存
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            self.logger.info(f"設定をファイルに保存しました: {self.config_path}")

        except Exception as e:
            self.logger.error(f"設定の保存に失敗しました: {e}")
            raise

    def reload_config(self) -> None:
        """設定を再読み込み"""
        self.logger.info("設定を再読み込み中...")
        self.load_config()

    def get_change_history(self) -> List[ConfigChange]:
        """設定変更履歴を取得

        Returns:
            変更履歴のリスト
        """
        return copy.deepcopy(self.change_history)

    def _get_config_schema(self) -> Dict[str, Any]:
        """設定スキーマを取得（検証用）"""
        return {
            "type": "object",
            "required": ["workflows", "quality_thresholds", "notifications"],
            "properties": {
                "workflows": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "object",
                            "required": ["steps"],
                            "properties": {
                                "enabled": {"type": "boolean"},
                                "steps": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["name"],
                                        "properties": {
                                            "name": {"type": "string"},
                                            "command": {"type": "string"},
                                            "required": {"type": "boolean"},
                                        },
                                    },
                                },
                            },
                        }
                    },
                },
                "quality_thresholds": {
                    "type": "object",
                    "properties": {
                        "coverage_minimum": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "test_success_rate": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                        },
                    },
                },
            },
        }


def main():
    """メイン実行関数（テスト用）"""
    try:
        # 設定マネージャーを初期化
        config_manager = ConfigManager()

        # 設定を表示
        print("現在の設定:")
        print(
            yaml.dump(
                config_manager.get_config(),
                default_flow_style=False,
                allow_unicode=True,
            )
        )

        # 設定検証
        validation_result = config_manager.validate_config()
        print(f"\n設定検証結果: {'有効' if validation_result.is_valid else '無効'}")

        if validation_result.errors:
            print("エラー:")
            for error in validation_result.errors:
                print(f"  - {error}")

        if validation_result.warnings:
            print("警告:")
            for warning in validation_result.warnings:
                print(f"  - {warning}")

        return 0

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
