"""
Qt-Theme-Studio バリデーションサービス

このモジュールは、テーマデータの構造検証、WCAG準拠検証などの
検証機能を提供します。
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from ..exceptions import ThemeStudioException
from ..utilities.color_analyzer import ColorAnalyzer


class ValidationError(ThemeStudioException):
    """バリデーションエラー"""
    pass


class AccessibilityReport:
    """アクセシビリティレポート"""
    
    def __init__(self, wcag_level: str = "AA"):
        """AccessibilityReportを初期化する
        
        Args:
            wcag_level (str): WCAGレベル（AA、AAA）
        """
        self.wcag_level = wcag_level
        self.contrast_ratios: Dict[str, float] = {}
        self.violations: List[Dict[str, Any]] = []
        self.suggestions: List[str] = []
        self.score: float = 0.0
        self.total_checks: int = 0
        self.passed_checks: int = 0
    
    def add_contrast_ratio(self, color_pair: str, ratio: float) -> None:
        """コントラスト比を追加する
        
        Args:
            color_pair (str): 色のペア（例: "text/background"）
            ratio (float): コントラスト比
        """
        self.contrast_ratios[color_pair] = ratio
    
    def add_violation(self, violation_type: str, description: str, 
                     severity: str = "error", suggestion: str = None) -> None:
        """違反を追加する
        
        Args:
            violation_type (str): 違反の種類
            description (str): 違反の説明
            severity (str): 重要度（error、warning、info）
            suggestion (str, optional): 改善提案
        """
        violation = {
            'type': violation_type,
            'description': description,
            'severity': severity
        }
        if suggestion:
            violation['suggestion'] = suggestion
        
        self.violations.append(violation)
    
    def add_suggestion(self, suggestion: str) -> None:
        """改善提案を追加する
        
        Args:
            suggestion (str): 改善提案
        """
        self.suggestions.append(suggestion)
    
    def calculate_score(self) -> None:
        """アクセシビリティスコアを計算する"""
        if self.total_checks == 0:
            self.score = 0.0
        else:
            self.score = (self.passed_checks / self.total_checks) * 100.0
    
    def is_compliant(self) -> bool:
        """WCAG準拠かどうかを判定する
        
        Returns:
            bool: 準拠している場合True
        """
        # エラーレベルの違反がない場合は準拠とみなす
        error_violations = [v for v in self.violations if v['severity'] == 'error']
        return len(error_violations) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換する
        
        Returns:
            Dict[str, Any]: レポートデータ
        """
        return {
            'wcag_level': self.wcag_level,
            'contrast_ratios': self.contrast_ratios,
            'violations': self.violations,
            'suggestions': self.suggestions,
            'score': self.score,
            'total_checks': self.total_checks,
            'passed_checks': self.passed_checks,
            'is_compliant': self.is_compliant()
        }
    
    def __str__(self) -> str:
        """文字列表現を返す"""
        result = f"アクセシビリティレポート (WCAG {self.wcag_level})\n"
        result += f"スコア: {self.score:.1f}% ({self.passed_checks}/{self.total_checks})\n"
        result += f"準拠状況: {'準拠' if self.is_compliant() else '非準拠'}\n\n"
        
        if self.contrast_ratios:
            result += "コントラスト比:\n"
            for pair, ratio in self.contrast_ratios.items():
                result += f"  {pair}: {ratio:.2f}\n"
            result += "\n"
        
        if self.violations:
            result += f"違反 ({len(self.violations)}):\n"
            for violation in self.violations:
                result += f"  [{violation['severity'].upper()}] {violation['description']}\n"
            result += "\n"
        
        if self.suggestions:
            result += f"改善提案 ({len(self.suggestions)}):\n"
            for suggestion in self.suggestions:
                result += f"  - {suggestion}\n"
        
        return result


class ValidationService:
    """バリデーションサービス
    
    テーマデータの構造検証、WCAG準拠検証などの検証機能を提供します。
    """
    
    def __init__(self):
        """ValidationServiceを初期化する"""
        self.logger = logging.getLogger(__name__)
        self.color_analyzer = ColorAnalyzer()
        
        # WCAG準拠の最小コントラスト比
        self.wcag_contrast_ratios = {
            'AA': {
                'normal_text': 4.5,
                'large_text': 3.0,
                'ui_components': 3.0
            },
            'AAA': {
                'normal_text': 7.0,
                'large_text': 4.5,
                'ui_components': 4.5
            }
        }
        
        self.logger.info("バリデーションサービスを初期化しました")
    
    def validate_theme_structure(self, theme_data: Dict[str, Any]) -> List[str]:
        """テーマデータの構造を検証する
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            
        Returns:
            List[str]: エラーメッセージのリスト
        """
        self.logger.debug("テーマ構造の検証を開始します")
        errors = []
        
        try:
            # 必須フィールドの検証
            required_fields = ['name', 'version', 'colors', 'fonts']
            for field in required_fields:
                if field not in theme_data:
                    errors.append(f"必須フィールドが不足しています: {field}")
                elif theme_data[field] is None:
                    errors.append(f"必須フィールドがNullです: {field}")
            
            # データ型の検証
            if 'name' in theme_data and not isinstance(theme_data['name'], str):
                errors.append("nameフィールドは文字列である必要があります")
            
            if 'version' in theme_data and not isinstance(theme_data['version'], str):
                errors.append("versionフィールドは文字列である必要があります")
            
            if 'colors' in theme_data and not isinstance(theme_data['colors'], dict):
                errors.append("colorsフィールドは辞書である必要があります")
            
            if 'fonts' in theme_data and not isinstance(theme_data['fonts'], dict):
                errors.append("fontsフィールドは辞書である必要があります")
            
            # 色データの詳細検証
            if 'colors' in theme_data and isinstance(theme_data['colors'], dict):
                color_errors = self._validate_colors_structure(theme_data['colors'])
                errors.extend(color_errors)
            
            # フォントデータの詳細検証
            if 'fonts' in theme_data and isinstance(theme_data['fonts'], dict):
                font_errors = self._validate_fonts_structure(theme_data['fonts'])
                errors.extend(font_errors)
            
            # サイズデータの検証（存在する場合）
            if 'sizes' in theme_data:
                if not isinstance(theme_data['sizes'], dict):
                    errors.append("sizesフィールドは辞書である必要があります")
                else:
                    size_errors = self._validate_sizes_structure(theme_data['sizes'])
                    errors.extend(size_errors)
            
            self.logger.debug(f"テーマ構造検証完了: {len(errors)}個のエラー")
            return errors
            
        except Exception as e:
            self.logger.error(f"テーマ構造検証中にエラーが発生しました: {str(e)}")
            errors.append(f"構造検証中にエラーが発生しました: {str(e)}")
            return errors
    
    def _validate_colors_structure(self, colors: Dict[str, Any]) -> List[str]:
        """色データの構造を検証する"""
        errors = []
        
        # 基本色の存在確認
        essential_colors = ['background', 'text']
        for color_name in essential_colors:
            if color_name not in colors:
                errors.append(f"必須の色が不足しています: {color_name}")
        
        # 色値の形式検証
        for color_name, color_value in colors.items():
            if not self._is_valid_color_value(color_value):
                errors.append(f"無効な色値です: {color_name} = {color_value}")
        
        return errors
    
    def _validate_fonts_structure(self, fonts: Dict[str, Any]) -> List[str]:
        """フォントデータの構造を検証する"""
        errors = []
        
        # 基本フォントの存在確認
        if 'default' not in fonts:
            errors.append("必須のフォントが不足しています: default")
        
        # フォント設定の検証
        for font_name, font_config in fonts.items():
            if isinstance(font_config, dict):
                if 'family' not in font_config:
                    errors.append(f"フォント設定にfamilyが不足しています: {font_name}")
                elif not isinstance(font_config['family'], str):
                    errors.append(f"フォントfamilyは文字列である必要があります: {font_name}")
                
                if 'size' in font_config:
                    if not isinstance(font_config['size'], (int, float)):
                        errors.append(f"フォントサイズは数値である必要があります: {font_name}")
                    elif font_config['size'] <= 0:
                        errors.append(f"フォントサイズは正の値である必要があります: {font_name}")
            elif isinstance(font_config, str):
                # 文字列の場合はフォントファミリー名として扱う
                pass
            else:
                errors.append(f"フォント設定は辞書または文字列である必要があります: {font_name}")
        
        return errors
    
    def _validate_sizes_structure(self, sizes: Dict[str, Any]) -> List[str]:
        """サイズデータの構造を検証する"""
        errors = []
        
        for size_name, size_value in sizes.items():
            if not isinstance(size_value, (int, float)):
                errors.append(f"サイズ値は数値である必要があります: {size_name}")
            elif size_value < 0:
                errors.append(f"サイズ値は非負の値である必要があります: {size_name}")
        
        return errors
    
    def _is_valid_color_value(self, color_value: Any) -> bool:
        """色値が有効かどうかを検証する"""
        if not isinstance(color_value, str):
            return False
        
        color_value = color_value.strip()
        
        # 16進数形式
        if re.match(r'^#[0-9A-Fa-f]{3}$', color_value):  # #RGB
            return True
        if re.match(r'^#[0-9A-Fa-f]{6}$', color_value):  # #RRGGBB
            return True
        if re.match(r'^#[0-9A-Fa-f]{8}$', color_value):  # #RRGGBBAA
            return True
        
        # RGB/RGBA形式
        if re.match(r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$', color_value):
            return True
        if re.match(r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$', color_value):
            return True
        
        # HSL/HSLA形式
        if re.match(r'^hsl\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)$', color_value):
            return True
        if re.match(r'^hsla\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*,\s*[\d.]+\s*\)$', color_value):
            return True
        
        # 名前付き色
        named_colors = {
            'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
            'gray', 'grey', 'darkgray', 'darkgrey', 'lightgray', 'lightgrey',
            'transparent', 'aliceblue', 'antiquewhite', 'aqua', 'aquamarine',
            'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'brown',
            'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral',
            'cornflowerblue', 'cornsilk', 'crimson', 'darkblue', 'darkcyan',
            'darkgoldenrod', 'darkgreen', 'darkkhaki', 'darkmagenta',
            'darkolivegreen', 'darkorange', 'darkorchid', 'darkred',
            'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray',
            'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
            'dimgray', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen',
            'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod',
            'greenyellow', 'honeydew', 'hotpink', 'indianred', 'indigo',
            'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen',
            'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
            'lightgoldenrodyellow', 'lightgreen', 'lightpink', 'lightsalmon',
            'lightseagreen', 'lightskyblue', 'lightslategray', 'lightsteelblue',
            'lightyellow', 'lime', 'limegreen', 'linen', 'maroon',
            'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple',
            'mediumseagreen', 'mediumslateblue', 'mediumspringgreen',
            'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream',
            'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace',
            'olive', 'olivedrab', 'orange', 'orangered', 'orchid',
            'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred',
            'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue',
            'purple', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon',
            'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver',
            'skyblue', 'slateblue', 'slategray', 'snow', 'springgreen',
            'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise',
            'violet', 'wheat', 'whitesmoke', 'yellowgreen'
        }
        
        return color_value.lower() in named_colors
    
    def validate_wcag_compliance(self, theme_data: Dict[str, Any], 
                               wcag_level: str = "AA") -> AccessibilityReport:
        """WCAG準拠を検証する
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            wcag_level (str): WCAGレベル（AA、AAA）
            
        Returns:
            AccessibilityReport: アクセシビリティレポート
        """
        self.logger.debug(f"WCAG {wcag_level} 準拠検証を開始します")
        
        report = AccessibilityReport(wcag_level)
        
        try:
            colors = theme_data.get('colors', {})
            if not colors:
                report.add_violation(
                    'missing_colors',
                    '色データが存在しません',
                    'error',
                    '色データを追加してください'
                )
                return report
            
            # コントラスト比の検証
            self._validate_contrast_ratios(colors, report)
            
            # 色の区別可能性の検証
            self._validate_color_distinguishability(colors, report)
            
            # フォントサイズの検証
            fonts = theme_data.get('fonts', {})
            self._validate_font_accessibility(fonts, report)
            
            # スコアの計算
            report.calculate_score()
            
            self.logger.debug(f"WCAG検証完了: スコア {report.score:.1f}%")
            return report
            
        except Exception as e:
            self.logger.error(f"WCAG検証中にエラーが発生しました: {str(e)}")
            report.add_violation(
                'validation_error',
                f'検証中にエラーが発生しました: {str(e)}',
                'error'
            )
            return report
    
    def _validate_contrast_ratios(self, colors: Dict[str, str], 
                                report: AccessibilityReport) -> None:
        """コントラスト比を検証する"""
        # 重要な色の組み合わせを定義
        color_combinations = [
            ('text', 'background', 'normal_text'),
            ('text_secondary', 'background', 'normal_text'),
            ('primary', 'background', 'ui_components'),
            ('text', 'primary', 'normal_text'),
            ('text', 'surface', 'normal_text'),
        ]
        
        min_ratios = self.wcag_contrast_ratios[report.wcag_level]
        
        for fg_key, bg_key, text_type in color_combinations:
            if fg_key in colors and bg_key in colors:
                try:
                    ratio = self.color_analyzer.calculate_contrast_ratio(
                        colors[fg_key], colors[bg_key]
                    )
                    
                    pair_name = f"{fg_key}/{bg_key}"
                    report.add_contrast_ratio(pair_name, ratio)
                    report.total_checks += 1
                    
                    min_ratio = min_ratios[text_type]
                    if ratio >= min_ratio:
                        report.passed_checks += 1
                    else:
                        report.add_violation(
                            'insufficient_contrast',
                            f'{pair_name}のコントラスト比が不十分です: {ratio:.2f} (最小: {min_ratio})',
                            'error',
                            f'{pair_name}の色を調整してコントラスト比を{min_ratio}以上にしてください'
                        )
                        
                except Exception as e:
                    self.logger.warning(f"コントラスト比計算エラー ({fg_key}/{bg_key}): {str(e)}")
    
    def _validate_color_distinguishability(self, colors: Dict[str, str], 
                                         report: AccessibilityReport) -> None:
        """色の区別可能性を検証する"""
        # 重要な色が十分に区別できるかチェック
        important_colors = ['primary', 'secondary', 'error', 'warning', 'success', 'info']
        existing_colors = {k: v for k, v in colors.items() if k in important_colors}
        
        if len(existing_colors) < 2:
            return
        
        color_pairs = []
        color_names = list(existing_colors.keys())
        
        for i in range(len(color_names)):
            for j in range(i + 1, len(color_names)):
                color1_name = color_names[i]
                color2_name = color_names[j]
                color_pairs.append((color1_name, color2_name))
        
        for color1_name, color2_name in color_pairs:
            try:
                ratio = self.color_analyzer.calculate_contrast_ratio(
                    existing_colors[color1_name], existing_colors[color2_name]
                )
                
                report.total_checks += 1
                
                # 重要な色同士は最低でも1.5:1の比率が必要
                if ratio >= 1.5:
                    report.passed_checks += 1
                else:
                    report.add_violation(
                        'poor_color_distinction',
                        f'{color1_name}と{color2_name}の色が似すぎています: {ratio:.2f}',
                        'warning',
                        f'{color1_name}と{color2_name}をより区別しやすい色に変更してください'
                    )
                    
            except Exception as e:
                self.logger.warning(f"色区別検証エラー ({color1_name}/{color2_name}): {str(e)}")
    
    def _validate_font_accessibility(self, fonts: Dict[str, Any], 
                                   report: AccessibilityReport) -> None:
        """フォントのアクセシビリティを検証する"""
        if not fonts:
            report.add_violation(
                'missing_fonts',
                'フォント設定が存在しません',
                'warning',
                'フォント設定を追加してください'
            )
            return
        
        # デフォルトフォントのサイズチェック
        if 'default' in fonts:
            font_config = fonts['default']
            if isinstance(font_config, dict) and 'size' in font_config:
                size = font_config['size']
                report.total_checks += 1
                
                # 最小フォントサイズは9pt
                if size >= 9:
                    report.passed_checks += 1
                else:
                    report.add_violation(
                        'small_font_size',
                        f'デフォルトフォントサイズが小さすぎます: {size}pt',
                        'warning',
                        'フォントサイズを9pt以上に設定してください'
                    )
        
        # 読みやすいフォントファミリーの確認
        for font_name, font_config in fonts.items():
            if isinstance(font_config, dict) and 'family' in font_config:
                family = font_config['family'].lower()
                report.total_checks += 1
                
                # 読みにくいフォントファミリーをチェック
                difficult_fonts = ['comic sans', 'papyrus', 'brush script']
                if any(difficult_font in family for difficult_font in difficult_fonts):
                    report.add_violation(
                        'difficult_font',
                        f'読みにくいフォントが使用されています: {font_name}',
                        'warning',
                        'より読みやすいフォントファミリーを選択してください'
                    )
                else:
                    report.passed_checks += 1