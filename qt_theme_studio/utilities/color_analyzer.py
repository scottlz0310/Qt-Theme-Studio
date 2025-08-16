"""
色解析ユーティリティ - 科学的色計算とWCAG準拠コントラスト比計算

このモジュールは、WCAG 2.1ガイドラインに基づく科学的な色解析機能を提供します。
コントラスト比計算、色調和分析、アクセシビリティ検証を行います。
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ColorInfo:
    """色情報データクラス"""

    hex_value: str
    rgb: Tuple[int, int, int]
    hsl: Tuple[float, float, float]
    luminance: float

    def __str__(self) -> str:
        return "ColorInfo(hex={self.hex_value}, rgb={self.rgb}, luminance={self.luminance:.3f})"


@dataclass
class AccessibilityViolation:
    """アクセシビリティ違反情報"""

    element_name: str
    foreground_color: str
    background_color: str
    contrast_ratio: float
    required_ratio: float
    wcag_level: str
    violation_type: str
    suggestion: str


@dataclass
class AccessibilityReport:
    """アクセシビリティレポート"""

    wcag_level: str  # AA, AAA
    contrast_ratios: Dict[str, float]
    violations: List[AccessibilityViolation]
    suggestions: List[str]
    score: float

    def is_compliant(self) -> bool:
        """WCAG準拠判定"""
        return len(self.violations) == 0


class ColorAnalyzer:
    """
    色解析ユーティリティクラス

    WCAG 2.1ガイドラインに基づく科学的な色解析機能を提供します。
    相対輝度計算、コントラスト比計算、色調和分析を行います。
    """

    # WCAG 2.1 コントラスト比要件
    WCAG_AA_NORMAL = 4.5
    WCAG_AA_LARGE = 3.0
    WCAG_AAA_NORMAL = 7.0
    WCAG_AAA_LARGE = 4.5

    def __init__(self):
        logger.info("色解析ユーティリティを初期化しました")

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        16進数カラーコードをRGB値に変換

        Args:
            hex_color: 16進数カラーコード (#RRGGBB または #RGB)

        Returns:
            RGB値のタプル (r, g, b)

        Raises:
            ValueError: 無効な16進数カラーコードの場合
        """
        # # を除去し、大文字に変換
        hex_color = hex_color.lstrip("#").upper()

        # 3桁の場合は6桁に展開
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])

        # 有効性チェック
        if len(hex_color) != 6 or not re.match(r"^[0-9A-F]{6}$", hex_color):
            raise ValueError("無効な16進数カラーコード: #{hex_color}")

        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except ValueError as e:
            raise ValueError(
                "16進数カラーコードの変換に失敗しました: #{hex_color}"
            ) from e

    def rgb_to_hsl(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """
        RGB値をHSL値に変換

        Args:
            r, g, b: RGB値 (0-255)

        Returns:
            HSL値のタプル (h: 0-360, s: 0-100, l: 0-100)
        """
        # 0-1の範囲に正規化
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0

        max_val = max(r_norm, g_norm, b_norm)
        min_val = min(r_norm, g_norm, b_norm)
        diff = max_val - min_val

        # 明度 (Lightness)
        lightness = (max_val + min_val) / 2.0

        if diff == 0:
            # グレースケールの場合
            hue = 0
            saturation = 0
        else:
            # 彩度 (Saturation)
            if lightness < 0.5:
                saturation = diff / (max_val + min_val)
            else:
                saturation = diff / (2.0 - max_val - min_val)

            # 色相 (Hue)
            if max_val == r_norm:
                hue = (g_norm - b_norm) / diff
                if g_norm < b_norm:
                    hue += 6
            elif max_val == g_norm:
                hue = (b_norm - r_norm) / diff + 2
            else:  # max_val == b_norm
                hue = (r_norm - g_norm) / diff + 4

            hue *= 60

        return (hue, saturation * 100, lightness * 100)

    def calculate_relative_luminance(self, r: int, g: int, b: int) -> float:
        """
        WCAG 2.1に基づく相対輝度を計算

        Args:
            r, g, b: RGB値 (0-255)

        Returns:
            相対輝度 (0.0-1.0)
        """

        def linearize_rgb_component(component: int) -> float:
            """RGB成分を線形化"""
            c = component / 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return math.pow((c + 0.055) / 1.055, 2.4)

        # 各RGB成分を線形化
        r_linear = linearize_rgb_component(r)
        g_linear = linearize_rgb_component(g)
        b_linear = linearize_rgb_component(b)

        # WCAG 2.1の相対輝度計算式
        luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

        return luminance

    def calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """
        WCAG 2.1に基づくコントラスト比を計算

        Args:
            color1: 前景色の16進数カラーコード
            color2: 背景色の16進数カラーコード

        Returns:
            コントラスト比 (1.0-21.0)

        Raises:
            ValueError: 無効なカラーコードの場合
        """
        try:
            # RGB値に変換
            rgb1 = self.hex_to_rgb(color1)
            rgb2 = self.hex_to_rgb(color2)

            # 相対輝度を計算
            luminance1 = self.calculate_relative_luminance(*rgb1)
            luminance2 = self.calculate_relative_luminance(*rgb2)

            # より明るい色を分子に、暗い色を分母にする
            lighter = max(luminance1, luminance2)
            darker = min(luminance1, luminance2)

            # コントラスト比計算 (WCAG 2.1 式)
            contrast_ratio = (lighter + 0.05) / (darker + 0.05)

            logger.debug(
                "コントラスト比計算: {color1} vs {color2} = {contrast_ratio:.2f}:1"
            )

            return contrast_ratio

        except ValueError:
            logger.error("コントラスト比計算エラー: {e}")
            raise

    def get_wcag_compliance_level(
        self, contrast_ratio: float, is_large_text: bool = False
    ) -> str:
        """
        WCAG適合レベルを判定

        Args:
            contrast_ratio: コントラスト比
            is_large_text: 大きなテキストかどうか (18pt以上または14pt太字以上)

        Returns:
            適合レベル ("AAA", "AA", "FAIL")
        """
        if is_large_text:
            if contrast_ratio >= self.WCAG_AAA_LARGE:
                return "AAA"
            elif contrast_ratio >= self.WCAG_AA_LARGE:
                return "AA"
            else:
                return "FAIL"
        else:
            if contrast_ratio >= self.WCAG_AAA_NORMAL:
                return "AAA"
            elif contrast_ratio >= self.WCAG_AA_NORMAL:
                return "AA"
            else:
                return "FAIL"

    def get_color_info(self, hex_color: str) -> ColorInfo:
        """
        色の詳細情報を取得

        Args:
            hex_color: 16進数カラーコード

        Returns:
            ColorInfo オブジェクト
        """
        rgb = self.hex_to_rgb(hex_color)
        hsl = self.rgb_to_hsl(*rgb)
        luminance = self.calculate_relative_luminance(*rgb)

        return ColorInfo(hex_value=hex_color, rgb=rgb, hsl=hsl, luminance=luminance)

    def get_color_harmony(
        self, base_color: str, harmony_type: str = "complementary"
    ) -> List[str]:
        """
        調和色を生成

        Args:
            base_color: ベースとなる16進数カラーコード
            harmony_type: 調和タイプ ("complementary", "triadic", "analogous", "split_complementary")

        Returns:
            調和色のリスト
        """
        try:
            rgb = self.hex_to_rgb(base_color)
            h, s, lightness = self.rgb_to_hsl(*rgb)

            harmony_colors = []

            if harmony_type == "complementary":
                # 補色 (180度回転)
                comp_h = (h + 180) % 360
                harmony_colors.append(self._hsl_to_hex(comp_h, s, lightness))

            elif harmony_type == "triadic":
                # 三色調和 (120度ずつ)
                for offset in [120, 240]:
                    new_h = (h + offset) % 360
                    harmony_colors.append(self._hsl_to_hex(new_h, s, lightness))

            elif harmony_type == "analogous":
                # 類似色 (±30度)
                for offset in [-30, 30]:
                    new_h = (h + offset) % 360
                    harmony_colors.append(self._hsl_to_hex(new_h, s, lightness))

            elif harmony_type == "split_complementary":
                # 分裂補色 (150度, 210度)
                for offset in [150, 210]:
                    new_h = (h + offset) % 360
                    harmony_colors.append(self._hsl_to_hex(new_h, s, lightness))

            logger.debug("調和色生成: {base_color} -> {harmony_colors}")
            return harmony_colors

        except ValueError:
            logger.error("調和色生成エラー: {e}")
            return []

    def _hsl_to_hex(self, h: float, s: float, l: float) -> str:
        """HSL値を16進数カラーコードに変換"""
        # HSLからRGBに変換
        s_norm = s / 100.0
        l_norm = l / 100.0

        c = (1 - abs(2 * l_norm - 1)) * s_norm
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l_norm - c / 2

        if 0 <= h < 60:
            r_prime, g_prime, b_prime = c, x, 0
        elif 60 <= h < 120:
            r_prime, g_prime, b_prime = x, c, 0
        elif 120 <= h < 180:
            r_prime, g_prime, b_prime = 0, c, x
        elif 180 <= h < 240:
            r_prime, g_prime, b_prime = 0, x, c
        elif 240 <= h < 300:
            r_prime, g_prime, b_prime = x, 0, c
        else:
            r_prime, g_prime, b_prime = c, 0, x

        int((r_prime + m) * 255)
        int((g_prime + m) * 255)
        int((b_prime + m) * 255)

        return "#{r:02x}{g:02x}{b:02x}"

    def analyze_color_accessibility(
        self, colors: Dict[str, Dict[str, str]]
    ) -> AccessibilityReport:
        """
        色アクセシビリティを分析

        Args:
            colors: 色データ辞書 {"element_name": {"foreground": "#hex", "background": "#hex"}}

        Returns:
            AccessibilityReport オブジェクト
        """
        violations = []
        contrast_ratios = {}
        suggestions = []

        for element_name, color_pair in colors.items():
            try:
                fg_color = color_pair["foreground"]
                bg_color = color_pair["background"]

                # コントラスト比計算
                contrast_ratio = self.calculate_contrast_ratio(fg_color, bg_color)
                contrast_ratios[element_name] = contrast_ratio

                # WCAG適合レベル判定
                wcag_level = self.get_wcag_compliance_level(contrast_ratio)

                # 違反チェック
                if wcag_level == "FAIL":
                    violation = AccessibilityViolation(
                        element_name=element_name,
                        foreground_color=fg_color,
                        background_color=bg_color,
                        contrast_ratio=contrast_ratio,
                        required_ratio=self.WCAG_AA_NORMAL,
                        wcag_level="AA",
                        violation_type="insufficient_contrast",
                        suggestion="{element_name}のコントラスト比を{self.WCAG_AA_NORMAL:.1f}:1以上にしてください",
                    )
                    violations.append(violation)

            except ValueError:
                logger.error("色分析エラー ({element_name}): {e}")
                continue

        # 全体的な提案を生成
        if violations:
            suggestions.extend(
                [
                    "コントラスト比が不十分な要素があります",
                    "WCAG AA準拠のため、通常テキストは4.5:1以上のコントラスト比が必要です",
                    "大きなテキスト（18pt以上）は3.0:1以上で十分です",
                ]
            )
        else:
            suggestions.append("すべての色の組み合わせがWCAG基準を満たしています")

        # スコア計算 (0-100)
        total_elements = len(colors)
        compliant_elements = total_elements - len(violations)
        score = (
            (compliant_elements / total_elements * 100) if total_elements > 0 else 100
        )

        # 最高適合レベルを判定
        wcag_level = "AAA"
        for ratio in contrast_ratios.values():
            if ratio < self.WCAG_AAA_NORMAL:
                wcag_level = "AA"
                break
        if violations:
            wcag_level = "FAIL"

        report = AccessibilityReport(
            wcag_level=wcag_level,
            contrast_ratios=contrast_ratios,
            violations=violations,
            suggestions=suggestions,
            score=score,
        )

        logger.info(
            "アクセシビリティ分析完了: スコア {score:.1f}%, レベル {wcag_level}"
        )

        return report

    def get_minimum_contrast_colors(
        self, target_ratio: float = WCAG_AA_NORMAL
    ) -> List[Tuple[str, str]]:
        """
        指定されたコントラスト比を満たす色の組み合わせを生成

        Args:
            target_ratio: 目標コントラスト比

        Returns:
            (前景色, 背景色) のタプルのリスト
        """
        color_combinations = []

        # 基本的な色の組み合わせを生成
        base_colors = [
            "#000000",
            "#333333",
            "#666666",
            "#999999",
            "#cccccc",
            "#fffff",
            "#ff0000",
            "#00ff00",
            "#0000f",
            "#ffff00",
            "#ff00f",
            "#00ffff",
        ]

        for fg in base_colors:
            for bg in base_colors:
                if fg != bg:
                    try:
                        ratio = self.calculate_contrast_ratio(fg, bg)
                        if ratio >= target_ratio:
                            color_combinations.append((fg, bg))
                    except ValueError:
                        continue

        # コントラスト比でソート（降順）
        color_combinations.sort(
            key=lambda x: self.calculate_contrast_ratio(x[0], x[1]), reverse=True
        )

        return color_combinations[:20]  # 上位20組み合わせを返す
