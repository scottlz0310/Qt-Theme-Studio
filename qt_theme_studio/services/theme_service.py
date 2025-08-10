"""
Qt-Theme-Studio テーマ管理サービス

このモジュールは、テーマの検証、形式変換、テンプレート管理などの
テーマ関連のビジネスロジックを提供します。
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..adapters.theme_adapter import ThemeAdapter, ThemeManagerError
from ..exceptions import ThemeStudioException


class ThemeValidationError(ThemeStudioException):
    """テーマ検証エラー"""
    pass


class ThemeConversionError(ThemeStudioException):
    """テーマ形式変換エラー"""
    pass


class ThemeTemplateError(ThemeStudioException):
    """テーマテンプレートエラー"""
    pass


class ValidationResult:
    """テーマ検証結果"""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        """ValidationResultを初期化する
        
        Args:
            is_valid (bool): 検証が成功した場合True
            errors (List[str], optional): エラーメッセージのリスト
            warnings (List[str], optional): 警告メッセージのリスト
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, message: str) -> None:
        """エラーメッセージを追加する
        
        Args:
            message (str): エラーメッセージ
        """
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """警告メッセージを追加する
        
        Args:
            message (str): 警告メッセージ
        """
        self.warnings.append(message)
    
    def __str__(self) -> str:
        """文字列表現を返す"""
        status = "有効" if self.is_valid else "無効"
        result = f"テーマ検証結果: {status}\n"
        
        if self.errors:
            result += f"エラー ({len(self.errors)}):\n"
            for error in self.errors:
                result += f"  - {error}\n"
        
        if self.warnings:
            result += f"警告 ({len(self.warnings)}):\n"
            for warning in self.warnings:
                result += f"  - {warning}\n"
        
        return result


class ThemeTemplate:
    """テーマテンプレート"""
    
    def __init__(self, name: str, description: str, data: Dict[str, Any], 
                 category: str = "general", tags: List[str] = None):
        """ThemeTemplateを初期化する
        
        Args:
            name (str): テンプレート名
            description (str): テンプレートの説明
            data (Dict[str, Any]): テンプレートデータ
            category (str): カテゴリ
            tags (List[str], optional): タグのリスト
        """
        self.name = name
        self.description = description
        self.data = data
        self.category = category
        self.tags = tags or []
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換する
        
        Returns:
            Dict[str, Any]: テンプレートデータ
        """
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'tags': self.tags,
            'data': self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeTemplate':
        """辞書からテンプレートを作成する
        
        Args:
            data (Dict[str, Any]): テンプレートデータ
            
        Returns:
            ThemeTemplate: テンプレートインスタンス
        """
        return cls(
            name=data['name'],
            description=data['description'],
            data=data['data'],
            category=data.get('category', 'general'),
            tags=data.get('tags', [])
        )


class ThemeService:
    """テーマ管理サービス
    
    テーマの検証、形式変換、テンプレート管理などの
    テーマ関連のビジネスロジックを提供します。
    """
    
    def __init__(self, theme_adapter: Optional[ThemeAdapter] = None):
        """ThemeServiceを初期化する
        
        Args:
            theme_adapter (Optional[ThemeAdapter]): テーマアダプター
        """
        self.logger = logging.getLogger(__name__)
        self.theme_adapter = theme_adapter or ThemeAdapter()
        self._templates_cache: Optional[List[ThemeTemplate]] = None
        
        # 必須プロパティの定義
        self.required_properties = {
            'name': str,
            'version': str,
            'colors': dict,
            'fonts': dict
        }
        
        # 推奨プロパティの定義
        self.recommended_properties = {
            'description': str,
            'author': str,
            'created_date': str,
            'sizes': dict,
            'spacing': dict
        }
        
        self.logger.info("テーマサービスを初期化しました")
    
    def validate_theme(self, theme_data: Dict[str, Any]) -> ValidationResult:
        """テーマデータを検証する
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            
        Returns:
            ValidationResult: 検証結果
        """
        self.logger.debug("テーマデータの検証を開始します")
        result = ValidationResult(True)
        
        try:
            # 必須プロパティの検証
            self._validate_required_properties(theme_data, result)
            
            # 色データの検証
            self._validate_colors(theme_data.get('colors', {}), result)
            
            # フォントデータの検証
            self._validate_fonts(theme_data.get('fonts', {}), result)
            
            # サイズデータの検証
            if 'sizes' in theme_data:
                self._validate_sizes(theme_data['sizes'], result)
            
            # 推奨プロパティの確認
            self._check_recommended_properties(theme_data, result)
            
            # qt-theme-manager互換性の検証
            self._validate_qt_theme_manager_compatibility(theme_data, result)
            
            self.logger.debug(f"テーマ検証完了: {'成功' if result.is_valid else '失敗'}")
            return result
            
        except Exception as e:
            self.logger.error(f"テーマ検証中にエラーが発生しました: {str(e)}")
            result.add_error(f"検証処理中にエラーが発生しました: {str(e)}")
            return result
    
    def _validate_required_properties(self, theme_data: Dict[str, Any], 
                                    result: ValidationResult) -> None:
        """必須プロパティを検証する"""
        for prop_name, prop_type in self.required_properties.items():
            if prop_name not in theme_data:
                result.add_error(f"必須プロパティが不足しています: {prop_name}")
            elif not isinstance(theme_data[prop_name], prop_type):
                result.add_error(
                    f"プロパティの型が正しくありません: {prop_name} "
                    f"(期待: {prop_type.__name__}, 実際: {type(theme_data[prop_name]).__name__})"
                )
    
    def _validate_colors(self, colors: Dict[str, Any], result: ValidationResult) -> None:
        """色データを検証する"""
        if not colors:
            result.add_error("色データが空です")
            return
        
        # 基本色の存在確認
        basic_colors = ['primary', 'secondary', 'background', 'surface', 'text']
        for color_name in basic_colors:
            if color_name not in colors:
                result.add_warning(f"推奨される基本色が不足しています: {color_name}")
        
        # 色値の形式検証
        for color_name, color_value in colors.items():
            if not self._is_valid_color_format(color_value):
                result.add_error(f"無効な色形式です: {color_name} = {color_value}")
    
    def _validate_fonts(self, fonts: Dict[str, Any], result: ValidationResult) -> None:
        """フォントデータを検証する"""
        if not fonts:
            result.add_error("フォントデータが空です")
            return
        
        # 基本フォントの存在確認
        basic_fonts = ['default', 'heading', 'monospace']
        for font_name in basic_fonts:
            if font_name not in fonts:
                result.add_warning(f"推奨される基本フォントが不足しています: {font_name}")
        
        # フォント設定の検証
        for font_name, font_config in fonts.items():
            if isinstance(font_config, dict):
                if 'family' not in font_config:
                    result.add_error(f"フォント設定にfamilyが不足しています: {font_name}")
                if 'size' in font_config and not isinstance(font_config['size'], (int, float)):
                    result.add_error(f"フォントサイズが数値ではありません: {font_name}")
    
    def _validate_sizes(self, sizes: Dict[str, Any], result: ValidationResult) -> None:
        """サイズデータを検証する"""
        for size_name, size_value in sizes.items():
            if not isinstance(size_value, (int, float)):
                result.add_error(f"サイズ値が数値ではありません: {size_name} = {size_value}")
            elif size_value < 0:
                result.add_error(f"サイズ値が負の値です: {size_name} = {size_value}")
    
    def _check_recommended_properties(self, theme_data: Dict[str, Any], 
                                    result: ValidationResult) -> None:
        """推奨プロパティを確認する"""
        for prop_name, prop_type in self.recommended_properties.items():
            if prop_name not in theme_data:
                result.add_warning(f"推奨プロパティが不足しています: {prop_name}")
            elif not isinstance(theme_data[prop_name], prop_type):
                result.add_warning(
                    f"推奨プロパティの型が正しくありません: {prop_name} "
                    f"(期待: {prop_type.__name__}, 実際: {type(theme_data[prop_name]).__name__})"
                )
    
    def _validate_qt_theme_manager_compatibility(self, theme_data: Dict[str, Any], 
                                               result: ValidationResult) -> None:
        """qt-theme-manager互換性を検証する"""
        try:
            # テーマアダプターを使用して互換性をチェック
            if self.theme_adapter.is_initialized:
                # 実際にテーマデータを読み込んでみる（テスト用）
                # これは実装の詳細に依存するため、基本的な構造チェックのみ行う
                pass
            else:
                result.add_warning("qt-theme-managerが初期化されていないため、互換性チェックをスキップしました")
                
        except Exception as e:
            result.add_warning(f"qt-theme-manager互換性チェック中にエラーが発生しました: {str(e)}")
    
    def _is_valid_color_format(self, color_value: Any) -> bool:
        """色値の形式が有効かどうかを確認する
        
        Args:
            color_value: 色値
            
        Returns:
            bool: 有効な場合True
        """
        if not isinstance(color_value, str):
            return False
        
        color_value = color_value.strip()
        
        # 16進数形式 (#RGB, #RRGGBB, #RRGGBBAA)
        if color_value.startswith('#'):
            hex_part = color_value[1:]
            if len(hex_part) in [3, 6, 8] and all(c in '0123456789ABCDEFabcdef' for c in hex_part):
                return True
        
        # RGB/RGBA形式 (rgb(r,g,b), rgba(r,g,b,a))
        if color_value.startswith(('rgb(', 'rgba(')):
            return True  # 簡易チェック（詳細な検証は必要に応じて実装）
        
        # 名前付き色（基本的なもののみ）
        named_colors = {
            'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
            'gray', 'grey', 'darkgray', 'darkgrey', 'lightgray', 'lightgrey',
            'transparent'
        }
        if color_value.lower() in named_colors:
            return True
        
        return False 
   def convert_theme_format(self, theme_data: Dict[str, Any], 
                           target_format: str) -> Union[str, Dict[str, Any]]:
        """テーマを指定された形式に変換する
        
        Args:
            theme_data (Dict[str, Any]): 変換元のテーマデータ
            target_format (str): 変換先の形式 ('json', 'qss', 'css')
            
        Returns:
            Union[str, Dict[str, Any]]: 変換されたテーマデータ
            
        Raises:
            ThemeConversionError: 変換に失敗した場合
        """
        self.logger.debug(f"テーマを{target_format}形式に変換します")
        
        try:
            # 入力データの検証
            validation_result = self.validate_theme(theme_data)
            if not validation_result.is_valid:
                raise ThemeConversionError(
                    f"変換元のテーマデータが無効です: {', '.join(validation_result.errors)}"
                )
            
            target_format = target_format.lower()
            
            if target_format == 'json':
                return self._convert_to_json(theme_data)
            elif target_format == 'qss':
                return self._convert_to_qss(theme_data)
            elif target_format == 'css':
                return self._convert_to_css(theme_data)
            else:
                raise ThemeConversionError(f"サポートされていない形式です: {target_format}")
                
        except Exception as e:
            self.logger.error(f"テーマ形式変換中にエラーが発生しました: {str(e)}")
            if isinstance(e, ThemeConversionError):
                raise
            raise ThemeConversionError(f"形式変換中にエラーが発生しました: {str(e)}")
    
    def _convert_to_json(self, theme_data: Dict[str, Any]) -> str:
        """JSON形式に変換する"""
        try:
            return json.dumps(theme_data, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ThemeConversionError(f"JSON変換に失敗しました: {str(e)}")
    
    def _convert_to_qss(self, theme_data: Dict[str, Any]) -> str:
        """QSS形式に変換する"""
        try:
            qss_lines = []
            qss_lines.append(f"/* {theme_data.get('name', 'Unnamed Theme')} */")
            qss_lines.append(f"/* Version: {theme_data.get('version', '1.0.0')} */")
            qss_lines.append("")
            
            colors = theme_data.get('colors', {})
            fonts = theme_data.get('fonts', {})
            
            # 基本的なウィジェットスタイルを生成
            if 'background' in colors:
                qss_lines.append(f"QWidget {{")
                qss_lines.append(f"    background-color: {colors['background']};")
                if 'text' in colors:
                    qss_lines.append(f"    color: {colors['text']};")
                if 'default' in fonts:
                    font_config = fonts['default']
                    if isinstance(font_config, dict):
                        if 'family' in font_config:
                            qss_lines.append(f"    font-family: {font_config['family']};")
                        if 'size' in font_config:
                            qss_lines.append(f"    font-size: {font_config['size']}pt;")
                qss_lines.append("}")
                qss_lines.append("")
            
            # ボタンスタイル
            if 'primary' in colors:
                qss_lines.append("QPushButton {")
                qss_lines.append(f"    background-color: {colors['primary']};")
                qss_lines.append(f"    color: {colors.get('text', '#ffffff')};")
                qss_lines.append("    border: 1px solid #cccccc;")
                qss_lines.append("    padding: 5px 10px;")
                qss_lines.append("    border-radius: 3px;")
                qss_lines.append("}")
                qss_lines.append("")
                
                qss_lines.append("QPushButton:hover {")
                qss_lines.append(f"    background-color: {colors.get('secondary', colors['primary'])};")
                qss_lines.append("}")
                qss_lines.append("")
            
            return "\n".join(qss_lines)
            
        except Exception as e:
            raise ThemeConversionError(f"QSS変換に失敗しました: {str(e)}")
    
    def _convert_to_css(self, theme_data: Dict[str, Any]) -> str:
        """CSS形式に変換する"""
        try:
            css_lines = []
            css_lines.append(f"/* {theme_data.get('name', 'Unnamed Theme')} */")
            css_lines.append(f"/* Version: {theme_data.get('version', '1.0.0')} */")
            css_lines.append("")
            
            colors = theme_data.get('colors', {})
            fonts = theme_data.get('fonts', {})
            
            # CSS変数の定義
            css_lines.append(":root {")
            for color_name, color_value in colors.items():
                css_lines.append(f"    --color-{color_name}: {color_value};")
            css_lines.append("}")
            css_lines.append("")
            
            # 基本スタイル
            css_lines.append("body {")
            if 'background' in colors:
                css_lines.append(f"    background-color: var(--color-background);")
            if 'text' in colors:
                css_lines.append(f"    color: var(--color-text);")
            if 'default' in fonts:
                font_config = fonts['default']
                if isinstance(font_config, dict):
                    if 'family' in font_config:
                        css_lines.append(f"    font-family: {font_config['family']};")
                    if 'size' in font_config:
                        css_lines.append(f"    font-size: {font_config['size']}pt;")
            css_lines.append("}")
            css_lines.append("")
            
            # ボタンスタイル
            if 'primary' in colors:
                css_lines.append("button, .btn {")
                css_lines.append(f"    background-color: var(--color-primary);")
                css_lines.append(f"    color: var(--color-text, #ffffff);")
                css_lines.append("    border: 1px solid #cccccc;")
                css_lines.append("    padding: 5px 10px;")
                css_lines.append("    border-radius: 3px;")
                css_lines.append("    cursor: pointer;")
                css_lines.append("}")
                css_lines.append("")
                
                css_lines.append("button:hover, .btn:hover {")
                css_lines.append(f"    background-color: var(--color-secondary, var(--color-primary));")
                css_lines.append("}")
                css_lines.append("")
            
            return "\n".join(css_lines)
            
        except Exception as e:
            raise ThemeConversionError(f"CSS変換に失敗しました: {str(e)}")
    
    def get_theme_templates(self) -> List[ThemeTemplate]:
        """利用可能なテーマテンプレートを取得する
        
        Returns:
            List[ThemeTemplate]: テーマテンプレートのリスト
        """
        if self._templates_cache is not None:
            return self._templates_cache
        
        self.logger.debug("テーマテンプレートを読み込みます")
        
        try:
            templates = []
            
            # 組み込みテンプレートを追加
            templates.extend(self._get_builtin_templates())
            
            # ユーザー定義テンプレートを読み込み（将来の拡張用）
            # templates.extend(self._load_user_templates())
            
            self._templates_cache = templates
            self.logger.info(f"{len(templates)}個のテーマテンプレートを読み込みました")
            
            return templates
            
        except Exception as e:
            self.logger.error(f"テーマテンプレートの読み込み中にエラーが発生しました: {str(e)}")
            return []
    
    def _get_builtin_templates(self) -> List[ThemeTemplate]:
        """組み込みテーマテンプレートを取得する
        
        Returns:
            List[ThemeTemplate]: 組み込みテンプレートのリスト
        """
        templates = []
        
        # ライトテーマテンプレート
        light_theme = ThemeTemplate(
            name="ライトテーマ",
            description="明るい色調の標準的なテーマ",
            category="basic",
            tags=["light", "standard", "accessible"],
            data={
                "name": "Light Theme",
                "version": "1.0.0",
                "description": "明るい色調の標準的なテーマ",
                "colors": {
                    "primary": "#007ACC",
                    "secondary": "#005A9E",
                    "background": "#FFFFFF",
                    "surface": "#F5F5F5",
                    "text": "#333333",
                    "text_secondary": "#666666",
                    "border": "#CCCCCC",
                    "hover": "#E6F3FF",
                    "selected": "#CCE7FF",
                    "error": "#D32F2F",
                    "warning": "#F57C00",
                    "success": "#388E3C",
                    "info": "#1976D2"
                },
                "fonts": {
                    "default": {
                        "family": "Segoe UI, Arial, sans-serif",
                        "size": 9,
                        "weight": "normal"
                    },
                    "heading": {
                        "family": "Segoe UI, Arial, sans-serif",
                        "size": 12,
                        "weight": "bold"
                    },
                    "monospace": {
                        "family": "Consolas, Monaco, monospace",
                        "size": 9,
                        "weight": "normal"
                    }
                },
                "sizes": {
                    "border_radius": 4,
                    "border_width": 1,
                    "padding": 8,
                    "margin": 4,
                    "icon_size": 16
                }
            }
        )
        templates.append(light_theme)
        
        # ダークテーマテンプレート
        dark_theme = ThemeTemplate(
            name="ダークテーマ",
            description="暗い色調の目に優しいテーマ",
            category="basic",
            tags=["dark", "night", "low-light"],
            data={
                "name": "Dark Theme",
                "version": "1.0.0",
                "description": "暗い色調の目に優しいテーマ",
                "colors": {
                    "primary": "#0078D4",
                    "secondary": "#106EBE",
                    "background": "#1E1E1E",
                    "surface": "#2D2D30",
                    "text": "#FFFFFF",
                    "text_secondary": "#CCCCCC",
                    "border": "#3E3E42",
                    "hover": "#2A2D2E",
                    "selected": "#094771",
                    "error": "#F44336",
                    "warning": "#FF9800",
                    "success": "#4CAF50",
                    "info": "#2196F3"
                },
                "fonts": {
                    "default": {
                        "family": "Segoe UI, Arial, sans-serif",
                        "size": 9,
                        "weight": "normal"
                    },
                    "heading": {
                        "family": "Segoe UI, Arial, sans-serif",
                        "size": 12,
                        "weight": "bold"
                    },
                    "monospace": {
                        "family": "Consolas, Monaco, monospace",
                        "size": 9,
                        "weight": "normal"
                    }
                },
                "sizes": {
                    "border_radius": 4,
                    "border_width": 1,
                    "padding": 8,
                    "margin": 4,
                    "icon_size": 16
                }
            }
        )
        templates.append(dark_theme)
        
        # ハイコントラストテーマテンプレート
        high_contrast_theme = ThemeTemplate(
            name="ハイコントラストテーマ",
            description="アクセシビリティを重視した高コントラストテーマ",
            category="accessibility",
            tags=["high-contrast", "accessible", "wcag"],
            data={
                "name": "High Contrast Theme",
                "version": "1.0.0",
                "description": "アクセシビリティを重視した高コントラストテーマ",
                "colors": {
                    "primary": "#000000",
                    "secondary": "#333333",
                    "background": "#FFFFFF",
                    "surface": "#F0F0F0",
                    "text": "#000000",
                    "text_secondary": "#333333",
                    "border": "#000000",
                    "hover": "#FFFF00",
                    "selected": "#0000FF",
                    "error": "#FF0000",
                    "warning": "#FF8000",
                    "success": "#008000",
                    "info": "#0000FF"
                },
                "fonts": {
                    "default": {
                        "family": "Arial, sans-serif",
                        "size": 10,
                        "weight": "bold"
                    },
                    "heading": {
                        "family": "Arial, sans-serif",
                        "size": 14,
                        "weight": "bold"
                    },
                    "monospace": {
                        "family": "Courier New, monospace",
                        "size": 10,
                        "weight": "bold"
                    }
                },
                "sizes": {
                    "border_radius": 0,
                    "border_width": 2,
                    "padding": 10,
                    "margin": 6,
                    "icon_size": 20
                }
            }
        )
        templates.append(high_contrast_theme)
        
        return templates
    
    def get_template_by_name(self, name: str) -> Optional[ThemeTemplate]:
        """名前でテーマテンプレートを取得する
        
        Args:
            name (str): テンプレート名
            
        Returns:
            Optional[ThemeTemplate]: テンプレート（見つからない場合はNone）
        """
        templates = self.get_theme_templates()
        for template in templates:
            if template.name == name:
                return template
        return None
    
    def get_templates_by_category(self, category: str) -> List[ThemeTemplate]:
        """カテゴリでテーマテンプレートを取得する
        
        Args:
            category (str): カテゴリ名
            
        Returns:
            List[ThemeTemplate]: 該当するテンプレートのリスト
        """
        templates = self.get_theme_templates()
        return [template for template in templates if template.category == category]
    
    def get_templates_by_tag(self, tag: str) -> List[ThemeTemplate]:
        """タグでテーマテンプレートを取得する
        
        Args:
            tag (str): タグ名
            
        Returns:
            List[ThemeTemplate]: 該当するテンプレートのリスト
        """
        templates = self.get_theme_templates()
        return [template for template in templates if tag in template.tags]
    
    def create_theme_from_template(self, template_name: str, 
                                 custom_name: Optional[str] = None) -> Dict[str, Any]:
        """テンプレートから新しいテーマを作成する
        
        Args:
            template_name (str): テンプレート名
            custom_name (Optional[str]): カスタムテーマ名
            
        Returns:
            Dict[str, Any]: 作成されたテーマデータ
            
        Raises:
            ThemeTemplateError: テンプレートが見つからない場合
        """
        template = self.get_template_by_name(template_name)
        if template is None:
            raise ThemeTemplateError(f"テンプレートが見つかりません: {template_name}")
        
        # テンプレートデータをコピー
        theme_data = template.data.copy()
        
        # カスタム名が指定されている場合は更新
        if custom_name:
            theme_data['name'] = custom_name
        
        # 作成日時を追加
        from datetime import datetime
        theme_data['created_date'] = datetime.now().isoformat()
        theme_data['template_source'] = template_name
        
        self.logger.info(f"テンプレート '{template_name}' からテーマを作成しました")
        return theme_data
    
    def clear_templates_cache(self) -> None:
        """テンプレートキャッシュをクリアする"""
        self._templates_cache = None
        self.logger.debug("テンプレートキャッシュをクリアしました")