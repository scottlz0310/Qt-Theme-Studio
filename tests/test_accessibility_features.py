"""
アクセシビリティ機能テスト

WCAG準拠検証機能、コントラスト比計算、色改善提案機能のテストを実装します。
"""

import pytest
import math
from unittest.mock import Mock, patch
from typing import List, Dict, Tuple

# テスト対象のインポート（存在しないモジュールはコメントアウト）
try:
    from qt_theme_studio.utilities.color_analyzer import ColorAnalyzer
except ImportError:
    ColorAnalyzer = None

try:
    from qt_theme_studio.utilities.color_improver import ColorImprover
except ImportError:
    ColorImprover = None

try:
    from qt_theme_studio.views.zebra_editor import ZebraEditor
except ImportError:
    ZebraEditor = None

try:
    from qt_theme_studio.controllers.zebra_controller import ZebraController
except ImportError:
    ZebraController = None

try:
    from qt_theme_studio.services.validation_service import ValidationService
except ImportError:
    ValidationService = None


@pytest.mark.skipif(ColorAnalyzer is None, reason="ColorAnalyzerモジュールが利用できません")
class TestColorAnalyzer:
    """ColorAnalyzerクラスのテスト"""
    
    @pytest.fixture
    def color_analyzer(self):
        """ColorAnalyzerインスタンスを作成"""
        return ColorAnalyzer()
    
    def test_hex_to_rgb_conversion(self, color_analyzer):
        """16進数からRGB変換のテスト"""
        # 基本的な色の変換
        assert color_analyzer.hex_to_rgb('#ffffff') == (255, 255, 255)
        assert color_analyzer.hex_to_rgb('#000000') == (0, 0, 0)
        assert color_analyzer.hex_to_rgb('#ff0000') == (255, 0, 0)
        assert color_analyzer.hex_to_rgb('#00ff00') == (0, 255, 0)
        assert color_analyzer.hex_to_rgb('#0000ff') == (0, 0, 255)
        
        # 短縮形式の変換
        assert color_analyzer.hex_to_rgb('#fff') == (255, 255, 255)
        assert color_analyzer.hex_to_rgb('#000') == (0, 0, 0)
        assert color_analyzer.hex_to_rgb('#f00') == (255, 0, 0)
        
        # #なしの形式
        assert color_analyzer.hex_to_rgb('ffffff') == (255, 255, 255)
        assert color_analyzer.hex_to_rgb('000000') == (0, 0, 0)
    
    def test_rgb_to_luminance_conversion(self, color_analyzer):
        """RGBから輝度変換のテスト"""
        # 白の輝度（最大値）
        white_luminance = color_analyzer.calculate_relative_luminance(255, 255, 255)
        assert abs(white_luminance - 1.0) < 0.001
        
        # 黒の輝度（最小値）
        black_luminance = color_analyzer.calculate_relative_luminance(0, 0, 0)
        assert abs(black_luminance - 0.0) < 0.001
        
        # 中間色の輝度
        gray_luminance = color_analyzer.calculate_relative_luminance(128, 128, 128)
        assert 0.0 < gray_luminance < 1.0
        
        # 赤の輝度
        red_luminance = color_analyzer.calculate_relative_luminance(255, 0, 0)
        assert 0.0 < red_luminance < 1.0
    
    def test_contrast_ratio_calculation(self, color_analyzer):
        """コントラスト比計算のテスト"""
        # 白と黒の最大コントラスト比（21:1）
        max_contrast = color_analyzer.calculate_contrast_ratio('#ffffff', '#000000')
        assert abs(max_contrast - 21.0) < 0.1
        
        # 同じ色のコントラスト比（1:1）
        same_contrast = color_analyzer.calculate_contrast_ratio('#ffffff', '#ffffff')
        assert abs(same_contrast - 1.0) < 0.1
        
        # 実際のテストケース
        blue_white_contrast = color_analyzer.calculate_contrast_ratio('#0078d4', '#ffffff')
        assert blue_white_contrast > 1.0
        
        # 順序を変えても同じ結果
        white_blue_contrast = color_analyzer.calculate_contrast_ratio('#ffffff', '#0078d4')
        assert abs(blue_white_contrast - white_blue_contrast) < 0.001
    
    def test_wcag_compliance_check(self, color_analyzer):
        """WCAG準拠チェックのテスト"""
        # AA準拠テスト（4.5:1以上）
        aa_compliant = color_analyzer.is_wcag_compliant('#000000', '#ffffff', 'AA')
        assert aa_compliant is True
        
        aa_non_compliant = color_analyzer.is_wcag_compliant('#cccccc', '#ffffff', 'AA')
        assert aa_non_compliant is False
        
        # AAA準拠テスト（7:1以上）
        aaa_compliant = color_analyzer.is_wcag_compliant('#000000', '#ffffff', 'AAA')
        assert aaa_compliant is True
        
        aaa_non_compliant = color_analyzer.is_wcag_compliant('#666666', '#ffffff', 'AAA')
        assert aaa_non_compliant is False
        
        # 大きなテキスト用のAA準拠（3:1以上）
        large_aa_compliant = color_analyzer.is_wcag_compliant('#767676', '#ffffff', 'AA_LARGE')
        assert large_aa_compliant is True
    
    def test_color_harmony_generation(self, color_analyzer):
        """調和色生成のテスト"""
        base_color = '#0078d4'
        harmony_colors = color_analyzer.get_color_harmony(base_color)
        
        # 調和色が生成されることを確認
        assert isinstance(harmony_colors, list)
        assert len(harmony_colors) > 0
        
        # すべて有効な16進数色であることを確認
        for color in harmony_colors:
            assert color.startswith('#')
            assert len(color) == 7
            # 16進数として解析できることを確認
            int(color[1:], 16)
    
    def test_accessibility_report_generation(self, color_analyzer):
        """アクセシビリティレポート生成のテスト"""
        colors = ['#0078d4', '#ffffff', '#000000', '#cccccc']
        report = color_analyzer.analyze_color_accessibility(colors)
        
        # レポート構造の確認
        assert 'contrast_ratios' in report
        assert 'wcag_violations' in report
        assert 'recommendations' in report
        assert 'overall_score' in report
        
        # コントラスト比が計算されていることを確認
        assert len(report['contrast_ratios']) > 0
        
        # スコアが0-100の範囲内であることを確認
        assert 0 <= report['overall_score'] <= 100


@pytest.mark.skipif(ColorImprover is None, reason="ColorImproverモジュールが利用できません")
class TestColorImprover:
    """ColorImproverクラスのテスト"""
    
    @pytest.fixture
    def color_improver(self):
        """ColorImproverインスタンスを作成"""
        return ColorImprover()
    
    @pytest.fixture
    def color_analyzer(self):
        """ColorAnalyzerインスタンスを作成"""
        return ColorAnalyzer()
    
    def test_contrast_improvement(self, color_improver, color_analyzer):
        """コントラスト改善のテスト"""
        # 不十分なコントラストの色ペア
        color1 = '#cccccc'
        color2 = '#ffffff'
        target_ratio = 4.5  # AA準拠
        
        # 改善前のコントラスト比を確認
        original_ratio = color_analyzer.calculate_contrast_ratio(color1, color2)
        assert original_ratio < target_ratio
        
        # コントラスト改善
        improved_color1, improved_color2 = color_improver.improve_contrast(
            color1, color2, target_ratio
        )
        
        # 改善後のコントラスト比を確認
        improved_ratio = color_analyzer.calculate_contrast_ratio(improved_color1, improved_color2)
        assert improved_ratio >= target_ratio
        
        # 改善された色が有効な16進数色であることを確認
        assert improved_color1.startswith('#')
        assert improved_color2.startswith('#')
        assert len(improved_color1) == 7
        assert len(improved_color2) == 7
    
    def test_accessible_alternatives_suggestion(self, color_improver, color_analyzer):
        """アクセシブル代替色提案のテスト"""
        # アクセシビリティに問題のある色セット
        problematic_colors = ['#cccccc', '#dddddd', '#eeeeee', '#ffffff']
        
        # 代替色の提案
        alternatives = color_improver.suggest_accessible_alternatives(problematic_colors)
        
        # 代替色が提案されることを確認
        assert isinstance(alternatives, list)
        assert len(alternatives) > 0
        
        # 提案された色がより良いコントラストを持つことを確認
        for alt_color in alternatives:
            # 白との組み合わせでAA準拠を確認
            contrast_with_white = color_analyzer.calculate_contrast_ratio(alt_color, '#ffffff')
            contrast_with_black = color_analyzer.calculate_contrast_ratio(alt_color, '#000000')
            
            # 少なくとも一方でAA準拠していることを確認
            assert contrast_with_white >= 4.5 or contrast_with_black >= 4.5
    
    def test_wcag_level_preset_generation(self, color_improver, color_analyzer):
        """WCAGレベルプリセット生成のテスト"""
        base_color = '#0078d4'
        
        # AA準拠プリセット
        aa_preset = color_improver.generate_wcag_preset(base_color, 'AA')
        assert 'primary' in aa_preset
        assert 'background' in aa_preset
        assert 'text' in aa_preset
        
        # AAA準拠プリセット
        aaa_preset = color_improver.generate_wcag_preset(base_color, 'AAA')
        assert 'primary' in aaa_preset
        assert 'background' in aaa_preset
        assert 'text' in aaa_preset
        
        # AA準拠の確認
        aa_contrast = color_analyzer.calculate_contrast_ratio(
            aa_preset['text'], aa_preset['background']
        )
        assert aa_contrast >= 4.5
        
        # AAA準拠の確認
        aaa_contrast = color_analyzer.calculate_contrast_ratio(
            aaa_preset['text'], aaa_preset['background']
        )
        assert aaa_contrast >= 7.0
    
    def test_color_brightness_adjustment(self, color_improver):
        """色の明度調整のテスト"""
        base_color = '#0078d4'
        
        # 明度を上げる
        brighter_color = color_improver.adjust_brightness(base_color, 1.5)
        assert brighter_color != base_color
        assert brighter_color.startswith('#')
        
        # 明度を下げる
        darker_color = color_improver.adjust_brightness(base_color, 0.5)
        assert darker_color != base_color
        assert darker_color.startswith('#')
        
        # 明度調整なし
        same_color = color_improver.adjust_brightness(base_color, 1.0)
        assert same_color == base_color
    
    def test_saturation_adjustment(self, color_improver):
        """彩度調整のテスト"""
        base_color = '#ff6b35'
        
        # 彩度を上げる
        more_saturated = color_improver.adjust_saturation(base_color, 1.5)
        assert more_saturated != base_color
        assert more_saturated.startswith('#')
        
        # 彩度を下げる
        less_saturated = color_improver.adjust_saturation(base_color, 0.5)
        assert less_saturated != base_color
        assert less_saturated.startswith('#')
        
        # 彩度調整なし
        same_color = color_improver.adjust_saturation(base_color, 1.0)
        assert same_color == base_color


@pytest.mark.skipif(ZebraEditor is None, reason="ZebraEditorモジュールが利用できません")
class TestZebraEditor:
    """ZebraEditorクラスのテスト"""
    
    @pytest.fixture
    def mock_qt_adapter(self):
        """モックQtAdapterを作成"""
        mock_adapter = Mock()
        mock_modules = {
            'QtWidgets': Mock(),
            'QtCore': Mock(),
            'QtGui': Mock()
        }
        mock_adapter.get_qt_modules.return_value = mock_modules
        return mock_adapter
    
    @pytest.fixture
    def mock_theme_adapter(self):
        """モックThemeAdapterを作成"""
        return Mock()
    
    def test_zebra_editor_initialization(self, mock_qt_adapter, mock_theme_adapter):
        """ゼブラエディターの初期化テスト"""
        zebra_editor = ZebraEditor(mock_qt_adapter, mock_theme_adapter)
        
        assert zebra_editor.qt_adapter == mock_qt_adapter
        assert zebra_editor.theme_adapter == mock_theme_adapter
        assert zebra_editor.color_analyzer is not None
        assert zebra_editor.color_improver is not None
    
    def test_contrast_calculation_ui(self, mock_qt_adapter, mock_theme_adapter):
        """コントラスト計算UIのテスト"""
        zebra_editor = ZebraEditor(mock_qt_adapter, mock_theme_adapter)
        
        # コントラスト計算
        contrast_ratio = zebra_editor.calculate_contrast_ratio('#000000', '#ffffff')
        assert abs(contrast_ratio - 21.0) < 0.1
        
        # UI更新の確認（モックなので実際の更新は確認困難）
        zebra_editor.update_contrast_display(contrast_ratio)
    
    def test_wcag_level_selection(self, mock_qt_adapter, mock_theme_adapter):
        """WCAGレベル選択のテスト"""
        zebra_editor = ZebraEditor(mock_qt_adapter, mock_theme_adapter)
        
        # AA準拠レベル設定
        zebra_editor.set_wcag_level('AA')
        assert zebra_editor.current_wcag_level == 'AA'
        
        # AAA準拠レベル設定
        zebra_editor.set_wcag_level('AAA')
        assert zebra_editor.current_wcag_level == 'AAA'
    
    def test_color_improvement_suggestions(self, mock_qt_adapter, mock_theme_adapter):
        """色改善提案のテスト"""
        zebra_editor = ZebraEditor(mock_qt_adapter, mock_theme_adapter)
        
        # 不十分なコントラストの色を設定
        zebra_editor.set_primary_color('#cccccc')
        zebra_editor.set_background_color('#ffffff')
        
        # 改善提案を取得
        suggestions = zebra_editor.get_improvement_suggestions()
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        # 提案された色が改善されていることを確認
        for suggestion in suggestions:
            assert 'primary' in suggestion
            assert 'background' in suggestion
            
            # 改善されたコントラスト比を確認
            improved_contrast = zebra_editor.calculate_contrast_ratio(
                suggestion['primary'], suggestion['background']
            )
            assert improved_contrast >= 4.5  # AA準拠


@pytest.mark.skipif(ZebraController is None, reason="ZebraControllerモジュールが利用できません")
class TestZebraController:
    """ZebraControllerクラスのテスト"""
    
    @pytest.fixture
    def mock_qt_adapter(self):
        """モックQtAdapterを作成"""
        return Mock()
    
    @pytest.fixture
    def mock_theme_adapter(self):
        """モックThemeAdapterを作成"""
        return Mock()
    
    def test_zebra_controller_initialization(self, mock_qt_adapter, mock_theme_adapter):
        """ゼブラコントローラーの初期化テスト"""
        zebra_controller = ZebraController(mock_qt_adapter, mock_theme_adapter)
        
        assert zebra_controller.qt_adapter == mock_qt_adapter
        assert zebra_controller.theme_adapter == mock_theme_adapter
        assert zebra_controller.color_analyzer is not None
        assert zebra_controller.color_improver is not None
    
    def test_wcag_compliant_color_generation(self, mock_qt_adapter, mock_theme_adapter):
        """WCAG準拠色生成のテスト"""
        zebra_controller = ZebraController(mock_qt_adapter, mock_theme_adapter)
        
        # AA準拠色生成
        aa_colors = zebra_controller.generate_wcag_compliant_colors('AA')
        assert isinstance(aa_colors, list)
        assert len(aa_colors) > 0
        
        # 生成された色がAA準拠していることを確認
        for i in range(0, len(aa_colors), 2):
            if i + 1 < len(aa_colors):
                contrast = zebra_controller.color_analyzer.calculate_contrast_ratio(
                    aa_colors[i], aa_colors[i + 1]
                )
                assert contrast >= 4.5
        
        # AAA準拠色生成
        aaa_colors = zebra_controller.generate_wcag_compliant_colors('AAA')
        assert isinstance(aaa_colors, list)
        assert len(aaa_colors) > 0
        
        # 生成された色がAAA準拠していることを確認
        for i in range(0, len(aaa_colors), 2):
            if i + 1 < len(aaa_colors):
                contrast = zebra_controller.color_analyzer.calculate_contrast_ratio(
                    aaa_colors[i], aaa_colors[i + 1]
                )
                assert contrast >= 7.0
    
    def test_accessibility_validation(self, mock_qt_adapter, mock_theme_adapter):
        """アクセシビリティ検証のテスト"""
        zebra_controller = ZebraController(mock_qt_adapter, mock_theme_adapter)
        
        # テスト色セット
        test_colors = ['#0078d4', '#ffffff', '#000000', '#cccccc']
        
        # アクセシビリティ検証
        validation_report = zebra_controller.validate_accessibility(test_colors)
        
        # レポート構造の確認
        assert 'wcag_level' in validation_report
        assert 'violations' in validation_report
        assert 'suggestions' in validation_report
        assert 'score' in validation_report
        
        # スコアが適切な範囲内であることを確認
        assert 0 <= validation_report['score'] <= 100
    
    def test_color_palette_optimization(self, mock_qt_adapter, mock_theme_adapter):
        """カラーパレット最適化のテスト"""
        zebra_controller = ZebraController(mock_qt_adapter, mock_theme_adapter)
        
        # 最適化前のパレット
        original_palette = {
            'primary': '#cccccc',
            'secondary': '#dddddd',
            'background': '#ffffff',
            'text': '#eeeeee'
        }
        
        # パレット最適化
        optimized_palette = zebra_controller.optimize_color_palette(original_palette, 'AA')
        
        # 最適化されたパレットの確認
        assert 'primary' in optimized_palette
        assert 'secondary' in optimized_palette
        assert 'background' in optimized_palette
        assert 'text' in optimized_palette
        
        # テキストと背景のコントラストがAA準拠していることを確認
        text_bg_contrast = zebra_controller.color_analyzer.calculate_contrast_ratio(
            optimized_palette['text'], optimized_palette['background']
        )
        assert text_bg_contrast >= 4.5


@pytest.mark.skipif(ValidationService is None, reason="ValidationServiceモジュールが利用できません")
class TestValidationService:
    """ValidationServiceクラスのテスト"""
    
    @pytest.fixture
    def mock_theme_adapter(self):
        """モックThemeAdapterを作成"""
        return Mock()
    
    def test_validation_service_initialization(self, mock_theme_adapter):
        """バリデーションサービスの初期化テスト"""
        validation_service = ValidationService(mock_theme_adapter)
        
        assert validation_service.theme_adapter == mock_theme_adapter
        assert validation_service.color_analyzer is not None
    
    def test_theme_structure_validation(self, mock_theme_adapter):
        """テーマ構造検証のテスト"""
        validation_service = ValidationService(mock_theme_adapter)
        
        # 有効なテーマ構造
        valid_theme = {
            'name': 'テストテーマ',
            'version': '1.0.0',
            'colors': {
                'primary': '#0078d4',
                'background': '#ffffff',
                'text': '#000000'
            },
            'fonts': {
                'default': {
                    'family': 'Arial',
                    'size': 12
                }
            }
        }
        
        validation_result = validation_service.validate_theme_structure(valid_theme)
        assert validation_result['is_valid'] is True
        assert len(validation_result['errors']) == 0
        
        # 無効なテーマ構造
        invalid_theme = {
            'name': 'テストテーマ'
            # 必須フィールドが不足
        }
        
        validation_result = validation_service.validate_theme_structure(invalid_theme)
        assert validation_result['is_valid'] is False
        assert len(validation_result['errors']) > 0
    
    def test_wcag_compliance_validation(self, mock_theme_adapter):
        """WCAG準拠検証のテスト"""
        validation_service = ValidationService(mock_theme_adapter)
        
        # WCAG準拠テーマ
        compliant_theme = {
            'colors': {
                'primary': '#0078d4',
                'background': '#ffffff',
                'text': '#000000',
                'secondary': '#6c757d'
            }
        }
        
        wcag_result = validation_service.validate_wcag_compliance(compliant_theme, 'AA')
        assert wcag_result['is_compliant'] is True
        assert len(wcag_result['violations']) == 0
        
        # WCAG非準拠テーマ
        non_compliant_theme = {
            'colors': {
                'primary': '#cccccc',
                'background': '#ffffff',
                'text': '#dddddd',
                'secondary': '#eeeeee'
            }
        }
        
        wcag_result = validation_service.validate_wcag_compliance(non_compliant_theme, 'AA')
        assert wcag_result['is_compliant'] is False
        assert len(wcag_result['violations']) > 0
    
    def test_comprehensive_theme_validation(self, mock_theme_adapter):
        """包括的テーマ検証のテスト"""
        validation_service = ValidationService(mock_theme_adapter)
        
        # テストテーマ
        test_theme = {
            'name': 'テストテーマ',
            'version': '1.0.0',
            'colors': {
                'primary': '#0078d4',
                'background': '#ffffff',
                'text': '#000000',
                'secondary': '#6c757d'
            },
            'fonts': {
                'default': {
                    'family': 'Arial',
                    'size': 12
                }
            }
        }
        
        # 包括的検証
        comprehensive_result = validation_service.validate_theme_comprehensive(test_theme)
        
        # 結果構造の確認
        assert 'structure_validation' in comprehensive_result
        assert 'wcag_validation' in comprehensive_result
        assert 'overall_score' in comprehensive_result
        assert 'recommendations' in comprehensive_result
        
        # スコアが適切な範囲内であることを確認
        assert 0 <= comprehensive_result['overall_score'] <= 100


@pytest.mark.skipif(any(cls is None for cls in [ZebraEditor, ValidationService]), 
                   reason="必要なモジュールが利用できません")
class TestAccessibilityIntegration:
    """アクセシビリティ統合テスト"""
    
    def test_end_to_end_accessibility_workflow(self):
        """エンドツーエンドアクセシビリティワークフローテスト"""
        # モックアダプターを作成
        mock_qt_adapter = Mock()
        mock_theme_adapter = Mock()
        
        # 1. ゼブラエディターの初期化
        zebra_editor = ZebraEditor(mock_qt_adapter, mock_theme_adapter)
        
        # 2. 初期色の設定（アクセシビリティに問題あり）
        zebra_editor.set_primary_color('#cccccc')
        zebra_editor.set_background_color('#ffffff')
        
        # 3. コントラスト比の計算
        initial_contrast = zebra_editor.calculate_contrast_ratio('#cccccc', '#ffffff')
        assert initial_contrast < 4.5  # AA準拠していない
        
        # 4. 改善提案の取得
        suggestions = zebra_editor.get_improvement_suggestions()
        assert len(suggestions) > 0
        
        # 5. 提案された色の適用
        best_suggestion = suggestions[0]
        zebra_editor.set_primary_color(best_suggestion['primary'])
        zebra_editor.set_background_color(best_suggestion['background'])
        
        # 6. 改善後のコントラスト比確認
        improved_contrast = zebra_editor.calculate_contrast_ratio(
            best_suggestion['primary'], best_suggestion['background']
        )
        assert improved_contrast >= 4.5  # AA準拠
        
        # 7. WCAGレベルの変更とテスト
        zebra_editor.set_wcag_level('AAA')
        aaa_suggestions = zebra_editor.get_improvement_suggestions()
        
        if aaa_suggestions:
            aaa_suggestion = aaa_suggestions[0]
            aaa_contrast = zebra_editor.calculate_contrast_ratio(
                aaa_suggestion['primary'], aaa_suggestion['background']
            )
            assert aaa_contrast >= 7.0  # AAA準拠
    
    def test_accessibility_validation_integration(self):
        """アクセシビリティ検証統合テスト"""
        # モックアダプターを作成
        mock_theme_adapter = Mock()
        
        # バリデーションサービスの初期化
        validation_service = ValidationService(mock_theme_adapter)
        
        # テストテーマ（段階的に改善）
        themes = [
            # 1. 非準拠テーマ
            {
                'name': '非準拠テーマ',
                'colors': {
                    'primary': '#cccccc',
                    'background': '#ffffff',
                    'text': '#dddddd'
                }
            },
            # 2. AA準拠テーマ
            {
                'name': 'AA準拠テーマ',
                'colors': {
                    'primary': '#0078d4',
                    'background': '#ffffff',
                    'text': '#000000'
                }
            },
            # 3. AAA準拠テーマ
            {
                'name': 'AAA準拠テーマ',
                'colors': {
                    'primary': '#003d6b',
                    'background': '#ffffff',
                    'text': '#000000'
                }
            }
        ]
        
        # 各テーマの検証
        for i, theme in enumerate(themes):
            aa_result = validation_service.validate_wcag_compliance(theme, 'AA')
            aaa_result = validation_service.validate_wcag_compliance(theme, 'AAA')
            
            if i == 0:  # 非準拠テーマ
                assert aa_result['is_compliant'] is False
                assert aaa_result['is_compliant'] is False
            elif i == 1:  # AA準拠テーマ
                assert aa_result['is_compliant'] is True
                # AAA準拠は不明（テーマによる）
            elif i == 2:  # AAA準拠テーマ
                assert aa_result['is_compliant'] is True
                assert aaa_result['is_compliant'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])