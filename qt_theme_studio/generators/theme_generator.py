#!/usr/bin/env python3
"""
テーマジェネレータモジュール
背景色から自動的に調和の取れたテーマを生成
"""

from typing import Dict, Any
from PySide6.QtGui import QColor


class ThemeGenerator:
    """テーマジェネレータクラス"""
    
    def __init__(self):
        """初期化"""
        self.preset_themes = {
            "dark": {
                "name": "ダークモード",
                "background": "#1a1a1a",
                "description": "暗い背景の低負荷テーマ"
            },
            "light": {
                "name": "ライトモード", 
                "background": "#ffffff",
                "description": "明るい背景の標準テーマ"
            },
            "blue": {
                "name": "ブルーモード",
                "background": "#1e3a5f", 
                "description": "プロフェッショナルなブルーベーステーマ"
            },
            "green": {
                "name": "グリーンモード",
                "background": "#1a2e1a",
                "description": "自然なグリーンベーステーマ"
            },
            "purple": {
                "name": "パープルモード",
                "background": "#2d1b45",
                "description": "エレガントなパープルベーステーマ"
            },
            "orange": {
                "name": "オレンジモード",
                "background": "#4a1c1c",
                "description": "温かみのあるオレンジベーステーマ"
            }
        }
    
    def generate_theme_from_background(self, bg_color: QColor) -> Dict[str, Any]:
        """背景色から自動的にテーマを生成"""
        # 背景色の明度を取得
        bg_lightness = bg_color.lightness()
        is_dark_bg = bg_lightness < 128
        
        # 背景色から調和の取れた色を生成
        if is_dark_bg:
            # 暗い背景の場合
            primary_color = self._generate_contrasting_color(bg_color, 0.7)
            accent_color = self._generate_contrasting_color(bg_color, 0.8)
            text_color = QColor("#ffffff")  # 白いテキスト
            surface_color = self._adjust_color(bg_color, 20, 0)
        else:
            # 明るい背景の場合
            primary_color = self._generate_contrasting_color(bg_color, 0.3)
            accent_color = self._generate_contrasting_color(bg_color, 0.4)
            text_color = QColor("#000000")  # 黒いテキスト
            surface_color = self._adjust_color(bg_color, -20, 0)
        
        # ボタン色を生成
        button_bg = primary_color
        button_text = text_color
        button_hover = self._adjust_color(primary_color, 20, 10)
        button_pressed = self._adjust_color(primary_color, -20, -10)
        button_border = self._adjust_color(primary_color, -10, 0)
        
        # パネル色を生成
        panel_bg = surface_color
        panel_border = self._adjust_color(surface_color, -30, 0)
        header_bg = self._adjust_color(surface_color, -10, 0)
        header_text = text_color
        header_border = panel_border
        zebra_alternate = self._adjust_color(surface_color, 5, 0)
        
        return {
            "name": "auto_generated",
            "display_name": "自動生成テーマ",
            "description": "背景色から自動生成された調和の取れたテーマ",
            "colors": {
                "primary": primary_color.name(),
                "accent": accent_color.name(),
                "background": bg_color.name(),
                "text": text_color.name(),
                "surface": surface_color.name()
            },
            "primaryColor": primary_color.name(),
            "accentColor": accent_color.name(),
            "backgroundColor": bg_color.name(),
            "textColor": text_color.name(),
            "button": {
                "background": button_bg.name(),
                "text": button_text.name(),
                "hover": button_hover.name(),
                "pressed": button_pressed.name(),
                "border": button_border.name()
            },
            "panel": {
                "background": panel_bg.name(),
                "border": panel_border.name(),
                "header": {
                    "background": header_bg.name(),
                    "text": header_text.name(),
                    "border": header_border.name()
                },
                "zebra": {
                    "alternate": zebra_alternate.name()
                }
            }
        }
    
    def _generate_contrasting_color(self, base_color: QColor, contrast_ratio: float) -> QColor:
        """基準色から指定されたコントラスト比の色を生成"""
        h, s, l, a = base_color.getHsl()
        
        # コントラスト比に基づいて明度を調整
        if contrast_ratio > 0.5:
            # 高いコントラスト（明るい色）
            new_l = min(255, l + (255 - l) * contrast_ratio)
        else:
            # 低いコントラスト（暗い色）
            new_l = max(0, l * contrast_ratio)
        
        # 彩度も少し調整
        new_s = min(255, s * 1.2)
        
        # 新しい色を作成
        contrasting_color = QColor()
        contrasting_color.setHsl(int(h), int(new_s), int(new_l), int(a))
        return contrasting_color
    
    def _adjust_color(self, color: QColor, brightness: int, saturation: int) -> QColor:
        """色の明度・彩度を調整"""
        h, s, lightness, a = color.getHsl()
        
        # 明度調整（-50 to 50）
        lightness = max(0, min(255, 
                               lightness + brightness * 2.55))
        
        # 彩度調整（-50 to 50）
        s = max(0, min(255, s + saturation * 2.55))
        
        adjusted_color = QColor()
        adjusted_color.setHsl(int(h), int(s), int(lightness), int(a))
        return adjusted_color
    
    def get_preset_themes(self) -> Dict[str, Dict[str, str]]:
        """プリセットテーマを取得"""
        return self.preset_themes
    
    def is_dark_color(self, hex_color: str) -> bool:
        """色が暗いかどうかを判定"""
        color = QColor(hex_color)
        return color.lightness() < 128
