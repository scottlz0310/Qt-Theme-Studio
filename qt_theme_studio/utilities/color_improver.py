"""
色改善ユーティリティ - 自動色改善提案とアクセシビリティ最適化

このモジュールは、WCAG準拠のための自動色改善提案機能を提供します。
コントラスト比の改善、アクセシビリティレベルプリセット、色の最適化を行います。
"""

import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import logging

from .color_analyzer import ColorAnalyzer, AccessibilityReport

logger = logging.getLogger(__name__)


@dataclass
class ColorImprovement:
    """色改善提案データクラス"""
    element_name: str
    original_foreground: str
    original_background: str
    improved_foreground: str
    improved_background: str
    original_contrast: float
    improved_contrast: float
    improvement_type: str
    description: str


@dataclass
class AccessibilityPreset:
    """アクセシビリティプリセットデータクラス"""
    name: str
    level: str  # AA, AAA
    description: str
    color_pairs: Dict[str, Dict[str, str]]
    min_contrast_ratio: float


class ColorImprover:
    """
    色改善ユーティリティクラス
    
    WCAG準拠のための自動色改善提案機能を提供します。
    コントラスト比の改善、色の最適化、プリセット適用を行います。
    """
    
    def __init__(self):
        self.color_analyzer = ColorAnalyzer()
        self.presets = self._initialize_presets()
        logger.info("色改善ユーティリティを初期化しました")
    
    def _initialize_presets(self) -> Dict[str, AccessibilityPreset]:
        """アクセシビリティプリセットを初期化"""
        presets = {}
        
        # WCAG AA準拠プリセット
        aa_preset = AccessibilityPreset(
            name="WCAG AA準拠",
            level="AA",
            description="通常テキスト4.5:1、大きなテキスト3.0:1のコントラスト比を保証",
            color_pairs={
                "通常テキスト": {"foreground": "#000000", "background": "#ffffff"},
                "リンクテキスト": {"foreground": "#0066cc", "background": "#ffffff"},
                "選択テキスト": {"foreground": "#ffffff", "background": "#0066cc"},
                "無効テキスト": {"foreground": "#767676", "background": "#ffffff"},
                "エラーテキスト": {"foreground": "#d13212", "background": "#ffffff"},
                "警告テキスト": {"foreground": "#b7950b", "background": "#ffffff"},
                "成功テキスト": {"foreground": "#0e7c0e", "background": "#ffffff"},
                "情報テキスト": {"foreground": "#1976d2", "background": "#ffffff"},
            },
            min_contrast_ratio=4.5
        )
        presets["AA"] = aa_preset
        
        # WCAG AAA準拠プリセット
        aaa_preset = AccessibilityPreset(
            name="WCAG AAA準拠",
            level="AAA",
            description="通常テキスト7.0:1、大きなテキスト4.5:1のコントラスト比を保証",
            color_pairs={
                "通常テキスト": {"foreground": "#000000", "background": "#ffffff"},
                "リンクテキスト": {"foreground": "#004499", "background": "#ffffff"},
                "選択テキスト": {"foreground": "#ffffff", "background": "#004499"},
                "無効テキスト": {"foreground": "#595959", "background": "#ffffff"},
                "エラーテキスト": {"foreground": "#b30000", "background": "#ffffff"},
                "警告テキスト": {"foreground": "#996600", "background": "#ffffff"},
                "成功テキスト": {"foreground": "#0a5d0a", "background": "#ffffff"},
                "情報テキスト": {"foreground": "#0d47a1", "background": "#ffffff"},
            },
            min_contrast_ratio=7.0
        )
        presets["AAA"] = aaa_preset
        
        # ダークテーマ AA準拠プリセット
        dark_aa_preset = AccessibilityPreset(
            name="ダークテーマ AA準拠",
            level="AA",
            description="ダークテーマでWCAG AA準拠のコントラスト比を保証",
            color_pairs={
                "通常テキスト": {"foreground": "#ffffff", "background": "#121212"},
                "リンクテキスト": {"foreground": "#64b5f6", "background": "#121212"},
                "選択テキスト": {"foreground": "#121212", "background": "#64b5f6"},
                "無効テキスト": {"foreground": "#9e9e9e", "background": "#121212"},
                "エラーテキスト": {"foreground": "#f44336", "background": "#121212"},
                "警告テキスト": {"foreground": "#ff9800", "background": "#121212"},
                "成功テキスト": {"foreground": "#4caf50", "background": "#121212"},
                "情報テキスト": {"foreground": "#2196f3", "background": "#121212"},
            },
            min_contrast_ratio=4.5
        )
        presets["DARK_AA"] = dark_aa_preset
        
        # 高コントラストプリセット
        high_contrast_preset = AccessibilityPreset(
            name="高コントラスト",
            level="AAA",
            description="最大限のコントラストを提供する高アクセシビリティプリセット",
            color_pairs={
                "通常テキスト": {"foreground": "#000000", "background": "#ffffff"},
                "リンクテキスト": {"foreground": "#000080", "background": "#ffffff"},
                "選択テキスト": {"foreground": "#ffffff", "background": "#000000"},
                "無効テキスト": {"foreground": "#404040", "background": "#ffffff"},
                "エラーテキスト": {"foreground": "#800000", "background": "#ffffff"},
                "警告テキスト": {"foreground": "#804000", "background": "#ffffff"},
                "成功テキスト": {"foreground": "#004000", "background": "#ffffff"},
                "情報テキスト": {"foreground": "#000080", "background": "#ffffff"},
            },
            min_contrast_ratio=10.0
        )
        presets["HIGH_CONTRAST"] = high_contrast_preset
        
        return presets
    
    def improve_contrast(self, foreground: str, background: str, target_ratio: float = 4.5) -> Tuple[str, str]:
        """
        コントラスト比を改善
        
        Args:
            foreground: 前景色の16進数カラーコード
            background: 背景色の16進数カラーコード
            target_ratio: 目標コントラスト比
            
        Returns:
            改善された (前景色, 背景色) のタプル
        """
        try:
            current_ratio = self.color_analyzer.calculate_contrast_ratio(foreground, background)
            
            if current_ratio >= target_ratio:
                logger.debug(f"コントラスト比は既に十分です: {current_ratio:.2f}:1")
                return foreground, background
            
            # 前景色の輝度調整を試行
            improved_fg = self._adjust_color_for_contrast(
                foreground, background, target_ratio, adjust_foreground=True
            )
            
            if improved_fg:
                new_ratio = self.color_analyzer.calculate_contrast_ratio(improved_fg, background)
                if new_ratio >= target_ratio:
                    logger.info(f"前景色調整でコントラスト改善: {current_ratio:.2f} -> {new_ratio:.2f}")
                    return improved_fg, background
            
            # 背景色の輝度調整を試行
            improved_bg = self._adjust_color_for_contrast(
                foreground, background, target_ratio, adjust_foreground=False
            )
            
            if improved_bg:
                new_ratio = self.color_analyzer.calculate_contrast_ratio(foreground, improved_bg)
                if new_ratio >= target_ratio:
                    logger.info(f"背景色調整でコントラスト改善: {current_ratio:.2f} -> {new_ratio:.2f}")
                    return foreground, improved_bg
            
            # 両方調整を試行
            if improved_fg and improved_bg:
                new_ratio = self.color_analyzer.calculate_contrast_ratio(improved_fg, improved_bg)
                if new_ratio >= target_ratio:
                    logger.info(f"両色調整でコントラスト改善: {current_ratio:.2f} -> {new_ratio:.2f}")
                    return improved_fg, improved_bg
            
            # 最後の手段：極端な色に変更
            logger.warning(f"標準的な調整では目標コントラスト比に達しませんでした。極端な色を使用します。")
            return self._get_extreme_contrast_colors(target_ratio)
            
        except Exception as e:
            logger.error(f"コントラスト改善エラー: {e}")
            return foreground, background
    
    def _adjust_color_for_contrast(self, foreground: str, background: str, 
                                 target_ratio: float, adjust_foreground: bool = True) -> Optional[str]:
        """色の輝度を調整してコントラスト比を改善"""
        try:
            target_color = foreground if adjust_foreground else background
            reference_color = background if adjust_foreground else foreground
            
            # RGB値とHSL値を取得
            rgb = self.color_analyzer.hex_to_rgb(target_color)
            h, s, l = self.color_analyzer.rgb_to_hsl(*rgb)
            
            # 輝度を段階的に調整
            step = 5
            max_iterations = 20
            
            # 暗くする方向
            for i in range(1, max_iterations + 1):
                new_l = max(0, l - step * i)
                new_color = self._hsl_to_hex(h, s, new_l)
                
                if adjust_foreground:
                    ratio = self.color_analyzer.calculate_contrast_ratio(new_color, reference_color)
                else:
                    ratio = self.color_analyzer.calculate_contrast_ratio(reference_color, new_color)
                
                if ratio >= target_ratio:
                    return new_color
            
            # 明るくする方向
            for i in range(1, max_iterations + 1):
                new_l = min(100, l + step * i)
                new_color = self._hsl_to_hex(h, s, new_l)
                
                if adjust_foreground:
                    ratio = self.color_analyzer.calculate_contrast_ratio(new_color, reference_color)
                else:
                    ratio = self.color_analyzer.calculate_contrast_ratio(reference_color, new_color)
                
                if ratio >= target_ratio:
                    return new_color
            
            return None
            
        except Exception as e:
            logger.error(f"色調整エラー: {e}")
            return None
    
    def _hsl_to_hex(self, h: float, s: float, l: float) -> str:
        """HSL値を16進数カラーコードに変換"""
        return self.color_analyzer._hsl_to_hex(h, s, l)
    
    def _get_extreme_contrast_colors(self, target_ratio: float) -> Tuple[str, str]:
        """極端なコントラストの色の組み合わせを取得"""
        if target_ratio >= 15:
            return "#000000", "#ffffff"  # 最大コントラスト
        elif target_ratio >= 10:
            return "#000000", "#f0f0f0"
        elif target_ratio >= 7:
            return "#1a1a1a", "#ffffff"
        else:
            return "#333333", "#ffffff"
    
    def suggest_accessible_alternatives(self, colors: Dict[str, Dict[str, str]], 
                                      target_level: str = "AA") -> List[ColorImprovement]:
        """
        アクセシブル代替色を提案
        
        Args:
            colors: 色データ辞書
            target_level: 目標WCAGレベル ("AA", "AAA")
            
        Returns:
            ColorImprovement オブジェクトのリスト
        """
        improvements = []
        target_ratio = 7.0 if target_level == "AAA" else 4.5
        
        # アクセシビリティ分析を実行
        report = self.color_analyzer.analyze_color_accessibility(colors)
        
        for violation in report.violations:
            # 改善された色を計算
            improved_fg, improved_bg = self.improve_contrast(
                violation.foreground_color,
                violation.background_color,
                target_ratio
            )
            
            # 改善後のコントラスト比を計算
            improved_ratio = self.color_analyzer.calculate_contrast_ratio(improved_fg, improved_bg)
            
            # 改善タイプを判定
            improvement_type = "both"
            if improved_fg == violation.foreground_color:
                improvement_type = "background_only"
            elif improved_bg == violation.background_color:
                improvement_type = "foreground_only"
            
            # 説明文を生成
            description = self._generate_improvement_description(
                violation.element_name,
                violation.contrast_ratio,
                improved_ratio,
                improvement_type,
                target_level
            )
            
            improvement = ColorImprovement(
                element_name=violation.element_name,
                original_foreground=violation.foreground_color,
                original_background=violation.background_color,
                improved_foreground=improved_fg,
                improved_background=improved_bg,
                original_contrast=violation.contrast_ratio,
                improved_contrast=improved_ratio,
                improvement_type=improvement_type,
                description=description
            )
            
            improvements.append(improvement)
        
        logger.info(f"{len(improvements)}個の色改善提案を生成しました")
        return improvements
    
    def _generate_improvement_description(self, element_name: str, original_ratio: float,
                                        improved_ratio: float, improvement_type: str,
                                        target_level: str) -> str:
        """改善説明文を生成"""
        base_desc = f"{element_name}のコントラスト比を{original_ratio:.1f}:1から{improved_ratio:.1f}:1に改善"
        
        if improvement_type == "foreground_only":
            type_desc = "（前景色のみ調整）"
        elif improvement_type == "background_only":
            type_desc = "（背景色のみ調整）"
        else:
            type_desc = "（前景色・背景色を調整）"
        
        level_desc = f"WCAG {target_level}準拠を達成"
        
        return f"{base_desc}{type_desc}し、{level_desc}しました。"
    
    def get_accessibility_preset(self, preset_name: str) -> Optional[AccessibilityPreset]:
        """アクセシビリティプリセットを取得"""
        return self.presets.get(preset_name)
    
    def list_available_presets(self) -> List[str]:
        """利用可能なプリセット名のリストを取得"""
        return list(self.presets.keys())
    
    def apply_accessibility_preset(self, preset_name: str, 
                                 existing_colors: Optional[Dict[str, Dict[str, str]]] = None) -> Dict[str, Dict[str, str]]:
        """
        アクセシビリティプリセットを適用
        
        Args:
            preset_name: プリセット名
            existing_colors: 既存の色データ（マージする場合）
            
        Returns:
            適用後の色データ辞書
        """
        preset = self.presets.get(preset_name)
        if not preset:
            logger.error(f"プリセット '{preset_name}' が見つかりません")
            return existing_colors or {}
        
        # プリセットの色データをコピー
        result_colors = preset.color_pairs.copy()
        
        # 既存の色データとマージ（既存データを優先）
        if existing_colors:
            for element_name, colors in existing_colors.items():
                if element_name not in result_colors:
                    result_colors[element_name] = colors
        
        logger.info(f"プリセット '{preset.name}' を適用しました")
        return result_colors
    
    def generate_color_variations(self, base_colors: Dict[str, Dict[str, str]], 
                                variation_type: str = "lightness") -> List[Dict[str, Dict[str, str]]]:
        """
        色のバリエーションを生成
        
        Args:
            base_colors: ベースとなる色データ
            variation_type: バリエーションタイプ ("lightness", "saturation", "hue")
            
        Returns:
            色バリエーションのリスト
        """
        variations = []
        
        if variation_type == "lightness":
            # 明度バリエーション
            lightness_adjustments = [-20, -10, 10, 20]
            for adjustment in lightness_adjustments:
                variation = self._adjust_colors_lightness(base_colors, adjustment)
                variations.append(variation)
                
        elif variation_type == "saturation":
            # 彩度バリエーション
            saturation_adjustments = [-30, -15, 15, 30]
            for adjustment in saturation_adjustments:
                variation = self._adjust_colors_saturation(base_colors, adjustment)
                variations.append(variation)
                
        elif variation_type == "hue":
            # 色相バリエーション
            hue_adjustments = [30, 60, 120, 180]
            for adjustment in hue_adjustments:
                variation = self._adjust_colors_hue(base_colors, adjustment)
                variations.append(variation)
        
        # WCAG準拠チェックを行い、適合するもののみ返す
        compliant_variations = []
        for variation in variations:
            report = self.color_analyzer.analyze_color_accessibility(variation)
            if report.score >= 80:  # 80%以上のスコアのもののみ
                compliant_variations.append(variation)
        
        logger.info(f"{len(compliant_variations)}個の適合バリエーションを生成しました")
        return compliant_variations
    
    def _adjust_colors_lightness(self, colors: Dict[str, Dict[str, str]], adjustment: float) -> Dict[str, Dict[str, str]]:
        """色の明度を調整"""
        adjusted_colors = {}
        
        for element_name, color_pair in colors.items():
            adjusted_pair = {}
            
            for color_type, hex_color in color_pair.items():
                try:
                    rgb = self.color_analyzer.hex_to_rgb(hex_color)
                    h, s, l = self.color_analyzer.rgb_to_hsl(*rgb)
                    
                    # 明度を調整（0-100の範囲内に制限）
                    new_l = max(0, min(100, l + adjustment))
                    adjusted_color = self._hsl_to_hex(h, s, new_l)
                    adjusted_pair[color_type] = adjusted_color
                    
                except Exception as e:
                    logger.warning(f"色調整エラー ({element_name}, {color_type}): {e}")
                    adjusted_pair[color_type] = hex_color
            
            adjusted_colors[element_name] = adjusted_pair
        
        return adjusted_colors
    
    def _adjust_colors_saturation(self, colors: Dict[str, Dict[str, str]], adjustment: float) -> Dict[str, Dict[str, str]]:
        """色の彩度を調整"""
        adjusted_colors = {}
        
        for element_name, color_pair in colors.items():
            adjusted_pair = {}
            
            for color_type, hex_color in color_pair.items():
                try:
                    rgb = self.color_analyzer.hex_to_rgb(hex_color)
                    h, s, l = self.color_analyzer.rgb_to_hsl(*rgb)
                    
                    # 彩度を調整（0-100の範囲内に制限）
                    new_s = max(0, min(100, s + adjustment))
                    adjusted_color = self._hsl_to_hex(h, new_s, l)
                    adjusted_pair[color_type] = adjusted_color
                    
                except Exception as e:
                    logger.warning(f"色調整エラー ({element_name}, {color_type}): {e}")
                    adjusted_pair[color_type] = hex_color
            
            adjusted_colors[element_name] = adjusted_pair
        
        return adjusted_colors
    
    def _adjust_colors_hue(self, colors: Dict[str, Dict[str, str]], adjustment: float) -> Dict[str, Dict[str, str]]:
        """色の色相を調整"""
        adjusted_colors = {}
        
        for element_name, color_pair in colors.items():
            adjusted_pair = {}
            
            for color_type, hex_color in color_pair.items():
                try:
                    rgb = self.color_analyzer.hex_to_rgb(hex_color)
                    h, s, l = self.color_analyzer.rgb_to_hsl(*rgb)
                    
                    # 色相を調整（0-360の範囲で循環）
                    new_h = (h + adjustment) % 360
                    adjusted_color = self._hsl_to_hex(new_h, s, l)
                    adjusted_pair[color_type] = adjusted_color
                    
                except Exception as e:
                    logger.warning(f"色調整エラー ({element_name}, {color_type}): {e}")
                    adjusted_pair[color_type] = hex_color
            
            adjusted_colors[element_name] = adjusted_pair
        
        return adjusted_colors
    
    def validate_color_scheme(self, colors: Dict[str, Dict[str, str]], 
                            target_level: str = "AA") -> Tuple[bool, List[str]]:
        """
        色スキームの妥当性を検証
        
        Args:
            colors: 色データ辞書
            target_level: 目標WCAGレベル
            
        Returns:
            (妥当性, 問題点リスト) のタプル
        """
        issues = []
        
        # アクセシビリティ分析
        report = self.color_analyzer.analyze_color_accessibility(colors)
        
        # WCAG準拠チェック
        if report.violations:
            issues.extend([f"{v.element_name}: コントラスト比不足 ({v.contrast_ratio:.1f}:1)" 
                          for v in report.violations])
        
        # 色の多様性チェック
        unique_colors = set()
        for color_pair in colors.values():
            unique_colors.update(color_pair.values())
        
        if len(unique_colors) < 3:
            issues.append("色の種類が少なすぎます（最低3色推奨）")
        
        # 色相の分散チェック
        hues = []
        for color_pair in colors.values():
            for hex_color in color_pair.values():
                try:
                    rgb = self.color_analyzer.hex_to_rgb(hex_color)
                    h, s, l = self.color_analyzer.rgb_to_hsl(*rgb)
                    if s > 10:  # 彩度が低すぎる色は除外
                        hues.append(h)
                except:
                    continue
        
        if len(set(int(h/30) for h in hues)) < 2:  # 30度単位で分類
            issues.append("色相の多様性が不足しています")
        
        is_valid = len(issues) == 0
        
        logger.info(f"色スキーム検証完了: {'妥当' if is_valid else '問題あり'} ({len(issues)}個の問題)")
        
        return is_valid, issues