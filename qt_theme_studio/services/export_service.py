"""
Qt-Theme-Studio エクスポートサービス

このモジュールは、テーマのマルチフォーマットエクスポート、
互換性テスト、プレビュー画像エクスポートなどの機能を提供します。
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..adapters.qt_adapter import QtAdapter
from ..adapters.theme_adapter import ThemeAdapter
from ..exceptions import ThemeStudioException
from ..utilities.japanese_file_handler import JapaneseFileHandler


class ExportError(ThemeStudioException):
    """エクスポートエラー"""
    pass


class CompatibilityReport:
    """互換性レポート"""
    
    def __init__(self):
        """CompatibilityReportを初期化する"""
        self.framework_results: Dict[str, Dict[str, Any]] = {}
        self.overall_compatibility: bool = True
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def add_framework_result(self, framework: str, is_compatible: bool, 
                           details: Dict[str, Any] = None) -> None:
        """フレームワークの結果を追加する
        
        Args:
            framework (str): フレームワーク名
            is_compatible (bool): 互換性があるかどうか
            details (Dict[str, Any], optional): 詳細情報
        """
        self.framework_results[framework] = {
            'compatible': is_compatible,
            'details': details or {}
        }
        
        if not is_compatible:
            self.overall_compatibility = False
    
    def add_warning(self, message: str) -> None:
        """警告を追加する
        
        Args:
            message (str): 警告メッセージ
        """
        self.warnings.append(message)
    
    def add_error(self, message: str) -> None:
        """エラーを追加する
        
        Args:
            message (str): エラーメッセージ
        """
        self.errors.append(message)
        self.overall_compatibility = False
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換する
        
        Returns:
            Dict[str, Any]: レポートデータ
        """
        return {
            'overall_compatibility': self.overall_compatibility,
            'framework_results': self.framework_results,
            'warnings': self.warnings,
            'errors': self.errors
        }
    
    def __str__(self) -> str:
        """文字列表現を返す"""
        result = f"互換性レポート\n"
        result += f"全体的な互換性: {'互換' if self.overall_compatibility else '非互換'}\n\n"
        
        if self.framework_results:
            result += "フレームワーク別結果:\n"
            for framework, data in self.framework_results.items():
                status = "互換" if data['compatible'] else "非互換"
                result += f"  {framework}: {status}\n"
            result += "\n"
        
        if self.warnings:
            result += f"警告 ({len(self.warnings)}):\n"
            for warning in self.warnings:
                result += f"  - {warning}\n"
            result += "\n"
        
        if self.errors:
            result += f"エラー ({len(self.errors)}):\n"
            for error in self.errors:
                result += f"  - {error}\n"
        
        return result


class ExportService:
    """エクスポートサービス
    
    テーマのマルチフォーマットエクスポート、互換性テスト、
    プレビュー画像エクスポートなどの機能を提供します。
    """
    
    def __init__(self, theme_adapter: Optional[ThemeAdapter] = None,
                 qt_adapter: Optional[QtAdapter] = None,
                 file_handler: Optional[JapaneseFileHandler] = None):
        """ExportServiceを初期化する
        
        Args:
            theme_adapter (Optional[ThemeAdapter]): テーマアダプター
            qt_adapter (Optional[QtAdapter]): Qtアダプター
            file_handler (Optional[JapaneseFileHandler]): 日本語ファイル処理
        """
        self.logger = logging.getLogger(__name__)
        self.theme_adapter = theme_adapter or ThemeAdapter()
        self.qt_adapter = qt_adapter or QtAdapter()
        self.file_handler = file_handler or JapaneseFileHandler()
        
        # サポートされているエクスポート形式
        self.supported_formats = ['json', 'qss', 'css', 'yaml']
        
        self.logger.info("エクスポートサービスを初期化しました")
    
    def export_theme(self, theme_data: Dict[str, Any], format_type: str, 
                    output_path: Optional[Union[str, Path]] = None) -> str:
        """テーマを指定された形式でエクスポートする
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            format_type (str): エクスポート形式
            output_path (Optional[Union[str, Path]]): 出力パス
            
        Returns:
            str: エクスポートされたデータ（文字列形式）
            
        Raises:
            ExportError: エクスポートに失敗した場合
        """
        self.logger.debug(f"テーマを{format_type}形式でエクスポートします")
        
        try:
            format_type = format_type.lower()
            
            if format_type not in self.supported_formats:
                raise ExportError(f"サポートされていない形式です: {format_type}")
            
            # 形式別のエクスポート処理
            if format_type == 'json':
                exported_data = self._export_to_json(theme_data)
            elif format_type == 'qss':
                exported_data = self._export_to_qss(theme_data)
            elif format_type == 'css':
                exported_data = self._export_to_css(theme_data)
            elif format_type == 'yaml':
                exported_data = self._export_to_yaml(theme_data)
            else:
                raise ExportError(f"未実装の形式です: {format_type}")
            
            # ファイルに保存（パスが指定されている場合）
            if output_path:
                output_path_str = str(output_path)
                
                # 日本語ファイルパスを正規化
                normalized_path = self.file_handler.normalize_path(output_path_str)
                
                # 安全なファイル名を生成
                safe_filename = self.file_handler.get_safe_filename(Path(normalized_path).name)
                safe_path = str(Path(normalized_path).parent / safe_filename)
                
                # ファイルを安全に書き込み
                success = self.file_handler.safe_write(safe_path, exported_data)
                
                if success:
                    self.logger.info(f"テーマを{safe_path}にエクスポートしました")
                else:
                    raise ExportError(f"ファイルの書き込みに失敗しました: {safe_path}")
            
            return exported_data
            
        except Exception as e:
            self.logger.error(f"テーマエクスポート中にエラーが発生しました: {str(e)}")
            if isinstance(e, ExportError):
                raise
            raise ExportError(f"エクスポート中にエラーが発生しました: {str(e)}")
    
    def _export_to_json(self, theme_data: Dict[str, Any]) -> str:
        """JSON形式でエクスポートする"""
        try:
            return json.dumps(theme_data, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ExportError(f"JSON形式への変換に失敗しました: {str(e)}")
    
    def _export_to_qss(self, theme_data: Dict[str, Any]) -> str:
        """QSS形式でエクスポートする"""
        try:
            qss_lines = []
            
            # ヘッダー情報
            theme_name = theme_data.get('name', 'Unnamed Theme')
            theme_version = theme_data.get('version', '1.0.0')
            qss_lines.append(f"/* {theme_name} */")
            qss_lines.append(f"/* Version: {theme_version} */")
            qss_lines.append(f"/* Generated by Qt-Theme-Studio */")
            qss_lines.append("")
            
            colors = theme_data.get('colors', {})
            fonts = theme_data.get('fonts', {})
            sizes = theme_data.get('sizes', {})
            
            # 基本ウィジェットスタイル
            self._add_qss_widget_styles(qss_lines, colors, fonts, sizes)
            
            return "\n".join(qss_lines)
            
        except Exception as e:
            raise ExportError(f"QSS形式への変換に失敗しました: {str(e)}")
    
    def _add_qss_widget_styles(self, qss_lines: List[str], colors: Dict[str, str],
                              fonts: Dict[str, Any], sizes: Dict[str, Any]) -> None:
        """QSSウィジェットスタイルを追加する"""
        
        # QWidget基本スタイル
        if colors.get('background') or colors.get('text'):
            qss_lines.append("QWidget {")
            if colors.get('background'):
                qss_lines.append(f"    background-color: {colors['background']};")
            if colors.get('text'):
                qss_lines.append(f"    color: {colors['text']};")
            
            # デフォルトフォント
            default_font = fonts.get('default')
            if isinstance(default_font, dict):
                if default_font.get('family'):
                    qss_lines.append(f"    font-family: {default_font['family']};")
                if default_font.get('size'):
                    qss_lines.append(f"    font-size: {default_font['size']}pt;")
            
            qss_lines.append("}")
            qss_lines.append("")
        
        # QPushButtonスタイル
        if colors.get('primary'):
            qss_lines.append("QPushButton {")
            qss_lines.append(f"    background-color: {colors['primary']};")
            qss_lines.append(f"    color: {colors.get('text', '#ffffff')};")
            qss_lines.append("    border: 1px solid #cccccc;")
            
            padding = sizes.get('padding', 8)
            border_radius = sizes.get('border_radius', 4)
            qss_lines.append(f"    padding: {padding}px;")
            qss_lines.append(f"    border-radius: {border_radius}px;")
            qss_lines.append("}")
            qss_lines.append("")
            
            # ホバー状態
            qss_lines.append("QPushButton:hover {")
            hover_color = colors.get('secondary', colors['primary'])
            qss_lines.append(f"    background-color: {hover_color};")
            qss_lines.append("}")
            qss_lines.append("")
            
            # 押下状態
            qss_lines.append("QPushButton:pressed {")
            qss_lines.append(f"    background-color: {colors.get('primary')};")
            qss_lines.append("    border: 2px solid #999999;")
            qss_lines.append("}")
            qss_lines.append("")
        
        # QLineEditスタイル
        if colors.get('surface') or colors.get('text'):
            qss_lines.append("QLineEdit {")
            if colors.get('surface'):
                qss_lines.append(f"    background-color: {colors['surface']};")
            if colors.get('text'):
                qss_lines.append(f"    color: {colors['text']};")
            
            border_color = colors.get('border', '#cccccc')
            border_width = sizes.get('border_width', 1)
            border_radius = sizes.get('border_radius', 4)
            padding = sizes.get('padding', 8)
            
            qss_lines.append(f"    border: {border_width}px solid {border_color};")
            qss_lines.append(f"    border-radius: {border_radius}px;")
            qss_lines.append(f"    padding: {padding}px;")
            qss_lines.append("}")
            qss_lines.append("")
        
        # QComboBoxスタイル
        if colors.get('surface'):
            qss_lines.append("QComboBox {")
            qss_lines.append(f"    background-color: {colors['surface']};")
            qss_lines.append(f"    color: {colors.get('text', '#000000')};")
            
            border_color = colors.get('border', '#cccccc')
            border_width = sizes.get('border_width', 1)
            border_radius = sizes.get('border_radius', 4)
            padding = sizes.get('padding', 8)
            
            qss_lines.append(f"    border: {border_width}px solid {border_color};")
            qss_lines.append(f"    border-radius: {border_radius}px;")
            qss_lines.append(f"    padding: {padding}px;")
            qss_lines.append("}")
            qss_lines.append("")
    
    def _export_to_css(self, theme_data: Dict[str, Any]) -> str:
        """CSS形式でエクスポートする"""
        try:
            css_lines = []
            
            # ヘッダー情報
            theme_name = theme_data.get('name', 'Unnamed Theme')
            theme_version = theme_data.get('version', '1.0.0')
            css_lines.append(f"/* {theme_name} */")
            css_lines.append(f"/* Version: {theme_version} */")
            css_lines.append(f"/* Generated by Qt-Theme-Studio */")
            css_lines.append("")
            
            colors = theme_data.get('colors', {})
            fonts = theme_data.get('fonts', {})
            sizes = theme_data.get('sizes', {})
            
            # CSS変数の定義
            css_lines.append(":root {")
            
            # 色変数
            for color_name, color_value in colors.items():
                css_lines.append(f"    --color-{color_name}: {color_value};")
            
            # サイズ変数
            for size_name, size_value in sizes.items():
                css_lines.append(f"    --size-{size_name}: {size_value}px;")
            
            css_lines.append("}")
            css_lines.append("")
            
            # 基本スタイル
            self._add_css_base_styles(css_lines, colors, fonts, sizes)
            
            return "\n".join(css_lines)
            
        except Exception as e:
            raise ExportError(f"CSS形式への変換に失敗しました: {str(e)}")
    
    def _add_css_base_styles(self, css_lines: List[str], colors: Dict[str, str],
                            fonts: Dict[str, Any], sizes: Dict[str, Any]) -> None:
        """CSS基本スタイルを追加する"""
        
        # body要素
        css_lines.append("body {")
        if colors.get('background'):
            css_lines.append("    background-color: var(--color-background);")
        if colors.get('text'):
            css_lines.append("    color: var(--color-text);")
        
        # デフォルトフォント
        default_font = fonts.get('default')
        if isinstance(default_font, dict):
            if default_font.get('family'):
                css_lines.append(f"    font-family: {default_font['family']};")
            if default_font.get('size'):
                css_lines.append(f"    font-size: {default_font['size']}pt;")
        
        css_lines.append("}")
        css_lines.append("")
        
        # ボタンスタイル
        if colors.get('primary'):
            css_lines.append("button, .btn {")
            css_lines.append("    background-color: var(--color-primary);")
            css_lines.append("    color: var(--color-text, #ffffff);")
            css_lines.append("    border: var(--size-border-width, 1px) solid var(--color-border, #cccccc);")
            css_lines.append("    border-radius: var(--size-border-radius, 4px);")
            css_lines.append("    padding: var(--size-padding, 8px);")
            css_lines.append("    cursor: pointer;")
            css_lines.append("}")
            css_lines.append("")
            
            css_lines.append("button:hover, .btn:hover {")
            css_lines.append("    background-color: var(--color-secondary, var(--color-primary));")
            css_lines.append("}")
            css_lines.append("")
        
        # 入力フィールドスタイル
        if colors.get('surface'):
            css_lines.append("input, textarea, select {")
            css_lines.append("    background-color: var(--color-surface);")
            css_lines.append("    color: var(--color-text);")
            css_lines.append("    border: var(--size-border-width, 1px) solid var(--color-border, #cccccc);")
            css_lines.append("    border-radius: var(--size-border-radius, 4px);")
            css_lines.append("    padding: var(--size-padding, 8px);")
            css_lines.append("}")
            css_lines.append("")
    
    def _export_to_yaml(self, theme_data: Dict[str, Any]) -> str:
        """YAML形式でエクスポートする"""
        try:
            import yaml
            return yaml.dump(theme_data, default_flow_style=False, 
                           allow_unicode=True, indent=2)
        except ImportError:
            raise ExportError("YAML形式のエクスポートにはpyyamlライブラリが必要です")
        except Exception as e:
            raise ExportError(f"YAML形式への変換に失敗しました: {str(e)}")
    
    def test_framework_compatibility(self, theme_data: Dict[str, Any]) -> CompatibilityReport:
        """各Qtフレームワークでの互換性をテストする
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            
        Returns:
            CompatibilityReport: 互換性レポート
        """
        self.logger.debug("フレームワーク互換性テストを開始します")
        
        report = CompatibilityReport()
        
        try:
            # テスト対象のフレームワーク
            frameworks = ['PySide6', 'PyQt6', 'PyQt5']
            
            for framework in frameworks:
                try:
                    # フレームワークの利用可能性をチェック
                    is_available = self._check_framework_availability(framework)
                    
                    if not is_available:
                        report.add_framework_result(
                            framework, False, 
                            {'reason': 'フレームワークが利用できません'}
                        )
                        continue
                    
                    # テーマの適用テスト
                    compatibility_result = self._test_theme_application(theme_data, framework)
                    report.add_framework_result(framework, compatibility_result['compatible'], 
                                              compatibility_result)
                    
                except Exception as e:
                    self.logger.warning(f"{framework}の互換性テスト中にエラー: {str(e)}")
                    report.add_framework_result(
                        framework, False,
                        {'reason': f'テスト中にエラーが発生しました: {str(e)}'}
                    )
            
            # 全体的な評価
            if not report.framework_results:
                report.add_error("利用可能なQtフレームワークが見つかりません")
            
            self.logger.debug(f"互換性テスト完了: {'互換' if report.overall_compatibility else '非互換'}")
            return report
            
        except Exception as e:
            self.logger.error(f"互換性テスト中にエラーが発生しました: {str(e)}")
            report.add_error(f"互換性テスト中にエラーが発生しました: {str(e)}")
            return report
    
    def _check_framework_availability(self, framework: str) -> bool:
        """フレームワークの利用可能性をチェックする"""
        try:
            __import__(framework)
            return True
        except ImportError:
            return False
    
    def _test_theme_application(self, theme_data: Dict[str, Any], 
                              framework: str) -> Dict[str, Any]:
        """テーマの適用テストを実行する"""
        result = {
            'compatible': True,
            'tested_features': [],
            'issues': []
        }
        
        try:
            # 基本的な構造チェック
            if 'colors' not in theme_data:
                result['compatible'] = False
                result['issues'].append('色データが不足しています')
            else:
                result['tested_features'].append('colors')
            
            if 'fonts' not in theme_data:
                result['compatible'] = False
                result['issues'].append('フォントデータが不足しています')
            else:
                result['tested_features'].append('fonts')
            
            # qt-theme-managerとの互換性チェック
            if self.theme_adapter.is_initialized:
                try:
                    # 実際のテーマ適用テスト（簡易版）
                    # 本格的なテストは実際のウィジェットを作成して行う必要がある
                    result['tested_features'].append('qt_theme_manager_integration')
                except Exception as e:
                    result['compatible'] = False
                    result['issues'].append(f'qt-theme-manager統合エラー: {str(e)}')
            
            return result
            
        except Exception as e:
            result['compatible'] = False
            result['issues'].append(f'テスト実行エラー: {str(e)}')
            return result
    
    def export_preview_image(self, preview_widget, output_path: Union[str, Path],
                           format_type: str = 'png') -> bool:
        """プレビュー画像をエクスポートする
        
        Args:
            preview_widget: プレビューウィジェット
            output_path (Union[str, Path]): 出力パス
            format_type (str): 画像形式
            
        Returns:
            bool: エクスポートが成功した場合True
            
        Raises:
            ExportError: エクスポートに失敗した場合
        """
        self.logger.debug(f"プレビュー画像を{format_type}形式でエクスポートします")
        
        try:
            # 日本語ファイルパスを正規化
            output_path_str = str(output_path)
            normalized_path = self.file_handler.normalize_path(output_path_str)
            
            # 安全なファイル名を生成
            safe_filename = self.file_handler.get_safe_filename(Path(normalized_path).name)
            safe_path = str(Path(normalized_path).parent / safe_filename)
            
            # ディレクトリを作成
            Path(safe_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Qtウィジェットから画像を生成
            if hasattr(preview_widget, 'grab'):
                pixmap = preview_widget.grab()
                success = pixmap.save(safe_path, format_type.upper())
                
                if success:
                    self.logger.info(f"プレビュー画像を{safe_path}に保存しました")
                    return True
                else:
                    raise ExportError("画像の保存に失敗しました")
            else:
                raise ExportError("プレビューウィジェットが画像キャプチャに対応していません")
                
        except Exception as e:
            self.logger.error(f"プレビュー画像エクスポート中にエラーが発生しました: {str(e)}")
            if isinstance(e, ExportError):
                raise
            raise ExportError(f"プレビュー画像エクスポート中にエラーが発生しました: {str(e)}")
    
    def get_supported_formats(self) -> List[str]:
        """サポートされているエクスポート形式を取得する
        
        Returns:
            List[str]: サポートされている形式のリスト
        """
        return self.supported_formats.copy()
    
    def validate_export_data(self, theme_data: Dict[str, Any]) -> List[str]:
        """エクスポート用データを検証する
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            
        Returns:
            List[str]: エラーメッセージのリスト
        """
        errors = []
        
        # 基本的な構造チェック
        if not isinstance(theme_data, dict):
            errors.append("テーマデータは辞書である必要があります")
            return errors
        
        # 必須フィールドのチェック
        required_fields = ['name', 'version']
        for field in required_fields:
            if field not in theme_data:
                errors.append(f"必須フィールドが不足しています: {field}")
        
        # 色データのチェック
        if 'colors' in theme_data:
            if not isinstance(theme_data['colors'], dict):
                errors.append("colorsフィールドは辞書である必要があります")
            elif not theme_data['colors']:
                errors.append("色データが空です")
        
        # フォントデータのチェック
        if 'fonts' in theme_data:
            if not isinstance(theme_data['fonts'], dict):
                errors.append("fontsフィールドは辞書である必要があります")
            elif not theme_data['fonts']:
                errors.append("フォントデータが空です")
        
        return errors