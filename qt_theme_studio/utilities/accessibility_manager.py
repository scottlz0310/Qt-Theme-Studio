"""
アクセシビリティ管理モジュール

このモジュールは、Qt-Theme-Studioのアクセシビリティ機能を管理します。
WCAG準拠のチェック機能、キーボードナビゲーション、
スクリーンリーダー対応などの機能を提供します。
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from ..logger import get_logger, LogCategory


@dataclass
class AccessibilityReport:
    """アクセシビリティレポート"""
    wcag_level: str  # AA, AAA
    contrast_ratios: Dict[str, float]
    violations: List[str]
    suggestions: List[str]
    score: float
    
    def is_compliant(self) -> bool:
        """WCAG準拠判定"""
        return len(self.violations) == 0


class AccessibilityManager:
    """
    アクセシビリティ管理クラス
    
    WCAG準拠のチェック機能、キーボードナビゲーション、
    スクリーンリーダー対応などのアクセシビリティ機能を提供します。
    """
    
    def __init__(self, qt_adapter):
        """
        アクセシビリティ管理を初期化します
        
        Args:
            qt_adapter: Qt フレームワークアダプター
        """
        self.qt_adapter = qt_adapter
        self.logger = get_logger()
        
        # Qtモジュールを取得
        self.qt_modules = qt_adapter.get_qt_modules()
        self.QtCore = self.qt_modules['QtCore']
        self.QtWidgets = self.qt_modules['QtWidgets']
        self.QtGui = self.qt_modules['QtGui']
        
        # WCAG基準値
        self.wcag_aa_ratio = 4.5
        self.wcag_aaa_ratio = 7.0
        self.wcag_large_text_aa_ratio = 3.0
        self.wcag_large_text_aaa_ratio = 4.5
        
        # アクセシビリティ設定
        self.high_contrast_mode = False
        self.large_text_mode = False
        self.keyboard_navigation_enabled = True
        self.screen_reader_support = True
        
        self.logger.info("アクセシビリティ管理を初期化しました", LogCategory.SYSTEM)
    
    def setup_accessibility_features(self, main_window) -> None:
        """
        メインウィンドウにアクセシビリティ機能を設定します
        
        Args:
            main_window: メインウィンドウインスタンス
        """
        try:
            # キーボードナビゲーションの設定
            self._setup_keyboard_navigation(main_window)
            
            # フォーカス管理の設定
            self._setup_focus_management(main_window)
            
            # アクセシビリティ属性の設定
            self._setup_accessibility_attributes(main_window)
            
            # ショートカットキーの設定
            self._setup_accessibility_shortcuts(main_window)
            
            self.logger.info("アクセシビリティ機能を設定しました", LogCategory.SYSTEM)
            
        except Exception as e:
            self.logger.error(f"アクセシビリティ機能の設定に失敗しました: {str(e)}", LogCategory.SYSTEM)
    
    def _setup_keyboard_navigation(self, main_window) -> None:
        """キーボードナビゲーションを設定します"""
        if not self.keyboard_navigation_enabled:
            return
        
        # タブオーダーの設定
        widgets = self._get_focusable_widgets(main_window)
        for i, widget in enumerate(widgets):
            if hasattr(widget, 'setTabOrder') and i < len(widgets) - 1:
                main_window.setTabOrder(widget, widgets[i + 1])
        
        # キーボードフォーカスの有効化
        for widget in widgets:
            if hasattr(widget, 'setFocusPolicy'):
                widget.setFocusPolicy(self.QtCore.Qt.FocusPolicy.TabFocus)
    
    def _setup_focus_management(self, main_window) -> None:
        """フォーカス管理を設定します"""
        # フォーカス変更時のイベントハンドラー
        def on_focus_changed(old_widget, new_widget):
            if new_widget:
                # フォーカスされたウィジェットをハイライト
                self._highlight_focused_widget(new_widget)
                
                # スクリーンリーダー用の情報を更新
                if self.screen_reader_support:
                    self._update_screen_reader_info(new_widget)
        
        # QApplicationのフォーカス変更イベントに接続
        app = self.QtWidgets.QApplication.instance()
        if app:
            app.focusChanged.connect(on_focus_changed)
    
    def _setup_accessibility_attributes(self, main_window) -> None:
        """アクセシビリティ属性を設定します"""
        # メインウィンドウの属性
        if hasattr(main_window, 'setAccessibleName'):
            main_window.setAccessibleName("Qt-Theme-Studio メインウィンドウ")
        if hasattr(main_window, 'setAccessibleDescription'):
            main_window.setAccessibleDescription("Qtアプリケーション用テーマエディター")
        
        # 子ウィジェットの属性を設定
        self._set_widget_accessibility_attributes(main_window)
    
    def _setup_accessibility_shortcuts(self, main_window) -> None:
        """アクセシビリティ用ショートカットキーを設定します"""
        # 高コントラストモード切り替え
        high_contrast_shortcut = self.QtGui.QShortcut(
            self.QtGui.QKeySequence("Ctrl+Shift+H"), main_window
        )
        high_contrast_shortcut.activated.connect(self.toggle_high_contrast_mode)
        
        # 大きなテキストモード切り替え
        large_text_shortcut = self.QtGui.QShortcut(
            self.QtGui.QKeySequence("Ctrl+Shift+L"), main_window
        )
        large_text_shortcut.activated.connect(self.toggle_large_text_mode)
        
        # フォーカス表示切り替え
        focus_shortcut = self.QtGui.QShortcut(
            self.QtGui.QKeySequence("Ctrl+Shift+F"), main_window
        )
        focus_shortcut.activated.connect(self.toggle_focus_indicators)
    
    def _get_focusable_widgets(self, parent) -> List[Any]:
        """フォーカス可能なウィジェットのリストを取得します"""
        focusable_widgets = []
        
        def collect_widgets(widget):
            if hasattr(widget, 'focusPolicy'):
                policy = widget.focusPolicy()
                if policy in [self.QtCore.Qt.FocusPolicy.TabFocus, 
                             self.QtCore.Qt.FocusPolicy.StrongFocus]:
                    focusable_widgets.append(widget)
            
            # 子ウィジェットを再帰的に処理
            if hasattr(widget, 'children'):
                for child in widget.children():
                    if hasattr(child, 'isWidgetType') and child.isWidgetType():
                        collect_widgets(child)
        
        collect_widgets(parent)
        return focusable_widgets
    
    def _highlight_focused_widget(self, widget) -> None:
        """フォーカスされたウィジェットをハイライトします"""
        if not widget:
            return
        
        # フォーカス枠のスタイルを設定
        focus_style = """
            QWidget:focus {
                border: 2px solid #0078d4;
                border-radius: 2px;
            }
        """
        
        # 既存のスタイルシートに追加
        current_style = widget.styleSheet()
        if focus_style not in current_style:
            widget.setStyleSheet(current_style + focus_style)
    
    def _update_screen_reader_info(self, widget) -> None:
        """スクリーンリーダー用の情報を更新します"""
        if not self.screen_reader_support or not widget:
            return
        
        # ウィジェットの種類に応じて適切な情報を設定
        widget_type = type(widget).__name__
        
        if hasattr(widget, 'setAccessibleName') and not widget.accessibleName():
            # デフォルトのアクセシブル名を設定
            if hasattr(widget, 'text') and widget.text():
                widget.setAccessibleName(widget.text())
            elif hasattr(widget, 'objectName') and widget.objectName():
                widget.setAccessibleName(widget.objectName())
            else:
                widget.setAccessibleName(f"{widget_type}ウィジェット")
    
    def _set_widget_accessibility_attributes(self, parent) -> None:
        """ウィジェットのアクセシビリティ属性を設定します"""
        def set_attributes(widget):
            widget_type = type(widget).__name__
            
            # ボタンの属性
            if widget_type in ['QPushButton', 'QToolButton']:
                if hasattr(widget, 'setAccessibleDescription') and hasattr(widget, 'toolTip'):
                    tooltip = widget.toolTip()
                    if tooltip:
                        widget.setAccessibleDescription(tooltip)
            
            # テキスト入力の属性
            elif widget_type in ['QLineEdit', 'QTextEdit', 'QPlainTextEdit']:
                if hasattr(widget, 'setAccessibleDescription'):
                    widget.setAccessibleDescription("テキスト入力フィールド")
            
            # リストの属性
            elif widget_type in ['QListWidget', 'QTreeWidget', 'QTableWidget']:
                if hasattr(widget, 'setAccessibleDescription'):
                    widget.setAccessibleDescription("選択可能なリスト")
            
            # 子ウィジェットを再帰的に処理
            if hasattr(widget, 'children'):
                for child in widget.children():
                    if hasattr(child, 'isWidgetType') and child.isWidgetType():
                        set_attributes(child)
        
        set_attributes(parent)
    
    def toggle_high_contrast_mode(self) -> None:
        """高コントラストモードを切り替えます"""
        self.high_contrast_mode = not self.high_contrast_mode
        
        if self.high_contrast_mode:
            self._apply_high_contrast_theme()
            self.logger.info("高コントラストモードを有効にしました", LogCategory.SYSTEM)
        else:
            self._remove_high_contrast_theme()
            self.logger.info("高コントラストモードを無効にしました", LogCategory.SYSTEM)
    
    def toggle_large_text_mode(self) -> None:
        """大きなテキストモードを切り替えます"""
        self.large_text_mode = not self.large_text_mode
        
        if self.large_text_mode:
            self._apply_large_text_theme()
            self.logger.info("大きなテキストモードを有効にしました", LogCategory.SYSTEM)
        else:
            self._remove_large_text_theme()
            self.logger.info("大きなテキストモードを無効にしました", LogCategory.SYSTEM)
    
    def toggle_focus_indicators(self) -> None:
        """フォーカス表示を切り替えます"""
        self.keyboard_navigation_enabled = not self.keyboard_navigation_enabled
        
        if self.keyboard_navigation_enabled:
            self.logger.info("フォーカス表示を有効にしました", LogCategory.SYSTEM)
        else:
            self.logger.info("フォーカス表示を無効にしました", LogCategory.SYSTEM)
    
    def _apply_high_contrast_theme(self) -> None:
        """高コントラストテーマを適用します"""
        app = self.QtWidgets.QApplication.instance()
        if not app:
            return
        
        high_contrast_style = """
            QWidget {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #ffffff;
            }
            QPushButton {
                background-color: #000000;
                color: #ffffff;
                border: 2px solid #ffffff;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #808080;
                color: #ffffff;
            }
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: #000000;
                color: #ffffff;
                border: 2px solid #ffffff;
            }
            QMenuBar {
                background-color: #000000;
                color: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #ffffff;
                color: #000000;
            }
            QMenu {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #ffffff;
            }
            QMenu::item:selected {
                background-color: #ffffff;
                color: #000000;
            }
        """
        
        app.setStyleSheet(high_contrast_style)
    
    def _remove_high_contrast_theme(self) -> None:
        """高コントラストテーマを削除します"""
        app = self.QtWidgets.QApplication.instance()
        if app:
            app.setStyleSheet("")
    
    def _apply_large_text_theme(self) -> None:
        """大きなテキストテーマを適用します"""
        app = self.QtWidgets.QApplication.instance()
        if not app:
            return
        
        large_text_style = """
            QWidget {
                font-size: 14pt;
            }
            QPushButton {
                font-size: 14pt;
                padding: 8px;
            }
            QMenuBar {
                font-size: 14pt;
            }
            QMenu {
                font-size: 14pt;
            }
            QLabel {
                font-size: 14pt;
            }
            QLineEdit, QTextEdit, QPlainTextEdit {
                font-size: 14pt;
            }
        """
        
        current_style = app.styleSheet()
        app.setStyleSheet(current_style + large_text_style)
    
    def _remove_large_text_theme(self) -> None:
        """大きなテキストテーマを削除します"""
        app = self.QtWidgets.QApplication.instance()
        if not app:
            return
        
        # 大きなテキスト関連のスタイルを削除
        current_style = app.styleSheet()
        lines = current_style.split('\n')
        filtered_lines = [line for line in lines if 'font-size:' not in line]
        app.setStyleSheet('\n'.join(filtered_lines))
    
    def check_color_contrast(self, foreground: str, background: str, 
                           is_large_text: bool = False) -> Dict[str, Any]:
        """
        色のコントラスト比をチェックします
        
        Args:
            foreground: 前景色（16進数）
            background: 背景色（16進数）
            is_large_text: 大きなテキストの場合True
            
        Returns:
            Dict[str, Any]: コントラスト比チェック結果
        """
        try:
            # コントラスト比を計算
            contrast_ratio = self._calculate_contrast_ratio(foreground, background)
            
            # WCAG基準値を取得
            aa_threshold = self.wcag_large_text_aa_ratio if is_large_text else self.wcag_aa_ratio
            aaa_threshold = self.wcag_large_text_aaa_ratio if is_large_text else self.wcag_aaa_ratio
            
            # 準拠レベルを判定
            aa_compliant = contrast_ratio >= aa_threshold
            aaa_compliant = contrast_ratio >= aaa_threshold
            
            result = {
                'contrast_ratio': contrast_ratio,
                'aa_compliant': aa_compliant,
                'aaa_compliant': aaa_compliant,
                'aa_threshold': aa_threshold,
                'aaa_threshold': aaa_threshold,
                'is_large_text': is_large_text,
                'recommendations': []
            }
            
            # 改善提案を生成
            if not aa_compliant:
                result['recommendations'].append(
                    f"コントラスト比が不十分です。{aa_threshold:.1f}:1以上にしてください。"
                )
            elif not aaa_compliant:
                result['recommendations'].append(
                    f"AAA準拠にするには、コントラスト比を{aaa_threshold:.1f}:1以上にしてください。"
                )
            else:
                result['recommendations'].append("コントラスト比は適切です。")
            
            return result
            
        except Exception as e:
            self.logger.error(f"コントラスト比チェックに失敗しました: {str(e)}", LogCategory.SYSTEM)
            return {
                'contrast_ratio': 0.0,
                'aa_compliant': False,
                'aaa_compliant': False,
                'error': str(e)
            }
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """
        2つの色のコントラスト比を計算します
        
        Args:
            color1: 色1（16進数）
            color2: 色2（16進数）
            
        Returns:
            float: コントラスト比
        """
        # 16進数カラーをRGB値に変換
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # 相対輝度を計算
        def get_relative_luminance(rgb):
            def linearize(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            r, g, b = [linearize(c) for c in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        # RGB値を取得
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # 相対輝度を計算
        lum1 = get_relative_luminance(rgb1)
        lum2 = get_relative_luminance(rgb2)
        
        # コントラスト比を計算
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def generate_accessibility_report(self, theme_data: Dict[str, Any]) -> AccessibilityReport:
        """
        テーマのアクセシビリティレポートを生成します
        
        Args:
            theme_data: テーマデータ
            
        Returns:
            AccessibilityReport: アクセシビリティレポート
        """
        violations = []
        suggestions = []
        contrast_ratios = {}
        
        try:
            # 色の組み合わせをチェック
            colors = theme_data.get('colors', {})
            
            # 主要な色の組み合わせをチェック
            color_combinations = [
                ('foreground', 'background'),
                ('text', 'background'),
                ('button_text', 'button_background'),
                ('link', 'background'),
            ]
            
            for fg_key, bg_key in color_combinations:
                if fg_key in colors and bg_key in colors:
                    fg_color = colors[fg_key]
                    bg_color = colors[bg_key]
                    
                    contrast_result = self.check_color_contrast(fg_color, bg_color)
                    contrast_ratios[f"{fg_key}_{bg_key}"] = contrast_result['contrast_ratio']
                    
                    if not contrast_result['aa_compliant']:
                        violations.append(
                            f"{fg_key}と{bg_key}のコントラスト比が不十分です "
                            f"({contrast_result['contrast_ratio']:.2f}:1)"
                        )
                        suggestions.append(
                            f"{fg_key}と{bg_key}の色を調整してコントラスト比を改善してください"
                        )
            
            # フォントサイズをチェック
            fonts = theme_data.get('fonts', {})
            for font_key, font_data in fonts.items():
                if isinstance(font_data, dict) and 'size' in font_data:
                    font_size = font_data['size']
                    if font_size < 12:
                        violations.append(f"{font_key}のフォントサイズが小さすぎます ({font_size}pt)")
                        suggestions.append(f"{font_key}のフォントサイズを12pt以上にしてください")
            
            # スコアを計算
            total_checks = len(color_combinations) + len(fonts)
            passed_checks = total_checks - len(violations)
            score = (passed_checks / total_checks * 100) if total_checks > 0 else 100
            
            # WCAG レベルを判定
            wcag_level = "AAA" if score >= 90 else "AA" if score >= 70 else "不適合"
            
            return AccessibilityReport(
                wcag_level=wcag_level,
                contrast_ratios=contrast_ratios,
                violations=violations,
                suggestions=suggestions,
                score=score
            )
            
        except Exception as e:
            self.logger.error(f"アクセシビリティレポートの生成に失敗しました: {str(e)}", LogCategory.SYSTEM)
            return AccessibilityReport(
                wcag_level="エラー",
                contrast_ratios={},
                violations=[f"レポート生成エラー: {str(e)}"],
                suggestions=["テーマデータを確認してください"],
                score=0.0
            )
    
    def get_accessibility_settings(self) -> Dict[str, bool]:
        """
        現在のアクセシビリティ設定を取得します
        
        Returns:
            Dict[str, bool]: アクセシビリティ設定
        """
        return {
            'high_contrast_mode': self.high_contrast_mode,
            'large_text_mode': self.large_text_mode,
            'keyboard_navigation_enabled': self.keyboard_navigation_enabled,
            'screen_reader_support': self.screen_reader_support,
        }
    
    def apply_accessibility_settings(self, settings: Dict[str, bool]) -> None:
        """
        アクセシビリティ設定を適用します
        
        Args:
            settings: 適用する設定
        """
        if 'high_contrast_mode' in settings:
            if settings['high_contrast_mode'] != self.high_contrast_mode:
                self.toggle_high_contrast_mode()
        
        if 'large_text_mode' in settings:
            if settings['large_text_mode'] != self.large_text_mode:
                self.toggle_large_text_mode()
        
        if 'keyboard_navigation_enabled' in settings:
            self.keyboard_navigation_enabled = settings['keyboard_navigation_enabled']
        
        if 'screen_reader_support' in settings:
            self.screen_reader_support = settings['screen_reader_support']
        
        self.logger.info("アクセシビリティ設定を適用しました", LogCategory.SYSTEM)