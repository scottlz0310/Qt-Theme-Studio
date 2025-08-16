"""
バリデーションサービスのテスト
"""

from unittest.mock import Mock, patch

from qt_theme_studio.services.validation_service import (
    AccessibilityReport,
    ValidationService,
)


class TestValidationService:
    """ValidationServiceのテストクラス"""

    def setup_method(self):
        """テストメソッドの前処理"""
        self.validation_service = ValidationService()

        # テスト用の有効なテーマデータ
        self.valid_theme_data = {
            'name': 'Test Theme',
            'version': '1.0.0',
            'colors': {
                'primary': '#007ACC',
                'secondary': '#005A9E',
                'background': '#FFFFFF',
                'surface': '#F5F5F5',
                'text': '#333333',
                'text_secondary': '#666666'
            },
            'fonts': {
                'default': {
                    'family': 'Arial, sans-seri',
                    'size': 10
                },
                'heading': {
                    'family': 'Arial, sans-seri',
                    'size': 14,
                    'weight': 'bold'
                }
            },
            'sizes': {
                'border_radius': 4,
                'padding': 8,
                'margin': 4
            }
        }

    def test_validate_theme_structure_valid(self):
        """有効なテーマ構造の検証テスト"""
        errors = self.validation_service.validate_theme_structure(self.valid_theme_data)

        assert isinstance(errors, list)
        assert len(errors) == 0

    def test_validate_theme_structure_missing_required_fields(self):
        """必須フィールドが不足している場合のテスト"""
        invalid_data = {
            'name': 'Test Theme'
            # version, colors, fonts が不足
        }

        errors = self.validation_service.validate_theme_structure(invalid_data)

        assert len(errors) >= 3
        assert any('version' in error for error in errors)
        assert any('colors' in error for error in errors)
        assert any('fonts' in error for error in errors)

    def test_validate_theme_structure_invalid_data_types(self):
        """無効なデータ型の場合のテスト"""
        invalid_data = {
            'name': 123,  # 文字列であるべき
            'version': [],  # 文字列であるべき
            'colors': 'not_dict',  # 辞書であるべき
            'fonts': 'not_dict'  # 辞書であるべき
        }

        errors = self.validation_service.validate_theme_structure(invalid_data)

        assert len(errors) >= 4
        assert any('name' in error and '文字列' in error for error in errors)
        assert any('version' in error and '文字列' in error for error in errors)
        assert any('colors' in error and '辞書' in error for error in errors)
        assert any('fonts' in error and '辞書' in error for error in errors)

    def test_validate_colors_structure_valid(self):
        """有効な色構造の検証テスト"""
        colors = {
            'background': '#FFFFFF',
            'text': '#333333',
            'primary': '#007ACC'
        }

        errors = self.validation_service._validate_colors_structure(colors)

        assert len(errors) == 0

    def test_validate_colors_structure_missing_essential(self):
        """必須色が不足している場合のテスト"""
        colors = {
            'primary': '#007ACC'
            # background, text が不足
        }

        errors = self.validation_service._validate_colors_structure(colors)

        assert len(errors) >= 2
        assert any('background' in error for error in errors)
        assert any('text' in error for error in errors)

    def test_validate_colors_structure_invalid_format(self):
        """無効な色形式の場合のテスト"""
        colors = {
            'background': '#FFFFFF',
            'text': '#333333',
            'primary': 'invalid_color'
        }

        errors = self.validation_service._validate_colors_structure(colors)

        assert len(errors) >= 1
        assert any('invalid_color' in error for error in errors)

    def test_validate_fonts_structure_valid(self):
        """有効なフォント構造の検証テスト"""
        fonts = {
            'default': {
                'family': 'Arial, sans-seri',
                'size': 10
            },
            'heading': {
                'family': 'Arial, sans-seri',
                'size': 14
            }
        }

        errors = self.validation_service._validate_fonts_structure(fonts)

        assert len(errors) == 0

    def test_validate_fonts_structure_missing_default(self):
        """デフォルトフォントが不足している場合のテスト"""
        fonts = {
            'heading': {
                'family': 'Arial, sans-seri',
                'size': 14
            }
        }

        errors = self.validation_service._validate_fonts_structure(fonts)

        assert len(errors) >= 1
        assert any('default' in error for error in errors)

    def test_validate_fonts_structure_missing_family(self):
        """フォントファミリーが不足している場合のテスト"""
        fonts = {
            'default': {
                'size': 10
                # family が不足
            }
        }

        errors = self.validation_service._validate_fonts_structure(fonts)

        assert len(errors) >= 1
        assert any('family' in error for error in errors)

    def test_validate_fonts_structure_invalid_size(self):
        """無効なフォントサイズの場合のテスト"""
        fonts = {
            'default': {
                'family': 'Arial, sans-seri',
                'size': -5  # 負の値
            }
        }

        errors = self.validation_service._validate_fonts_structure(fonts)

        assert len(errors) >= 1
        assert any('正の値' in error for error in errors)

    def test_validate_sizes_structure_valid(self):
        """有効なサイズ構造の検証テスト"""
        sizes = {
            'border_radius': 4,
            'padding': 8,
            'margin': 4.5
        }

        errors = self.validation_service._validate_sizes_structure(sizes)

        assert len(errors) == 0

    def test_validate_sizes_structure_invalid_type(self):
        """無効なサイズ型の場合のテスト"""
        sizes = {
            'border_radius': 'not_number',
            'padding': 8
        }

        errors = self.validation_service._validate_sizes_structure(sizes)

        assert len(errors) >= 1
        assert any('数値' in error for error in errors)

    def test_validate_sizes_structure_negative_value(self):
        """負のサイズ値の場合のテスト"""
        sizes = {
            'border_radius': -4,
            'padding': 8
        }

        errors = self.validation_service._validate_sizes_structure(sizes)

        assert len(errors) >= 1
        assert any('非負' in error for error in errors)

    def test_is_valid_color_value_hex(self):
        """16進数色値の検証テスト"""
        # 有効な16進数色値
        assert self.validation_service._is_valid_color_value('#FFF')
        assert self.validation_service._is_valid_color_value('#FFFFFF')
        assert self.validation_service._is_valid_color_value('#FFFFFFFF')
        assert self.validation_service._is_valid_color_value('#123abc')

        # 無効な16進数色値
        assert not self.validation_service._is_valid_color_value('#GGG')
        assert not self.validation_service._is_valid_color_value('#GGGGGG')
        assert not self.validation_service._is_valid_color_value('#FF')
        assert not self.validation_service._is_valid_color_value('#FFFFFFF')

    def test_is_valid_color_value_rgb(self):
        """RGB色値の検証テスト"""
        # 有効なRGB色値
        assert self.validation_service._is_valid_color_value('rgb(255, 255, 255)')
        assert self.validation_service._is_valid_color_value('rgb(0,0,0)')
        assert self.validation_service._is_valid_color_value('rgba(255, 255, 255, 0.5)')
        assert self.validation_service._is_valid_color_value('rgba(0,0,0,1.0)')

    def test_is_valid_color_value_named(self):
        """名前付き色値の検証テスト"""
        # 有効な名前付き色
        assert self.validation_service._is_valid_color_value('red')
        assert self.validation_service._is_valid_color_value('white')
        assert self.validation_service._is_valid_color_value('transparent')
        assert self.validation_service._is_valid_color_value('lightblue')

        # 無効な名前付き色
        assert not self.validation_service._is_valid_color_value('invalidcolor')
        assert not self.validation_service._is_valid_color_value('notacolor')

    def test_is_valid_color_value_invalid_types(self):
        """無効な型の色値テスト"""
        assert not self.validation_service._is_valid_color_value(123)
        assert not self.validation_service._is_valid_color_value([])
        assert not self.validation_service._is_valid_color_value({})
        assert not self.validation_service._is_valid_color_value(None)

    @patch('qt_theme_studio.services.validation_service.ColorAnalyzer')
    def test_validate_wcag_compliance_valid(self, mock_color_analyzer):
        """WCAG準拠検証テスト（有効な場合）"""
        # ColorAnalyzerのモック設定
        mock_analyzer = Mock()
        mock_analyzer.calculate_contrast_ratio.return_value = 7.0  # 高いコントラスト比
        mock_color_analyzer.return_value = mock_analyzer

        # 新しいインスタンスを作成（モックを使用するため）
        validation_service = ValidationService()

        report = validation_service.validate_wcag_compliance(self.valid_theme_data, 'AA')

        assert isinstance(report, AccessibilityReport)
        assert report.wcag_level == 'AA'
        assert report.total_checks > 0

    @patch('qt_theme_studio.services.validation_service.ColorAnalyzer')
    def test_validate_wcag_compliance_insufficient_contrast(self, mock_color_analyzer):
        """WCAG準拠検証テスト（コントラスト不足の場合）"""
        # ColorAnalyzerのモック設定（低いコントラスト比）
        mock_analyzer = Mock()
        mock_analyzer.calculate_contrast_ratio.return_value = 2.0  # 低いコントラスト比
        mock_color_analyzer.return_value = mock_analyzer

        # 新しいインスタンスを作成（モックを使用するため）
        validation_service = ValidationService()

        report = validation_service.validate_wcag_compliance(self.valid_theme_data, 'AA')

        assert isinstance(report, AccessibilityReport)
        assert len(report.violations) > 0
        assert any('コントラスト比が不十分' in v['description'] for v in report.violations)

    def test_validate_wcag_compliance_no_colors(self):
        """色データがない場合のWCAG検証テスト"""
        theme_data = {
            'name': 'Test Theme',
            'version': '1.0.0'
            # colors が不足
        }

        report = self.validation_service.validate_wcag_compliance(theme_data, 'AA')

        assert isinstance(report, AccessibilityReport)
        assert len(report.violations) > 0
        assert any('色データが存在しません' in v['description'] for v in report.violations)

    def test_validate_font_accessibility_valid(self):
        """フォントアクセシビリティ検証テスト（有効な場合）"""
        report = AccessibilityReport()
        fonts = {
            'default': {
                'family': 'Arial, sans-seri',
                'size': 12
            }
        }

        self.validation_service._validate_font_accessibility(fonts, report)

        assert report.total_checks > 0
        assert report.passed_checks > 0

    def test_validate_font_accessibility_small_font(self):
        """小さなフォントサイズの場合のテスト"""
        report = AccessibilityReport()
        fonts = {
            'default': {
                'family': 'Arial, sans-seri',
                'size': 6  # 小さすぎるサイズ
            }
        }

        self.validation_service._validate_font_accessibility(fonts, report)

        assert len(report.violations) > 0
        assert any('小さすぎます' in v['description'] for v in report.violations)

    def test_validate_font_accessibility_difficult_font(self):
        """読みにくいフォントの場合のテスト"""
        report = AccessibilityReport()
        fonts = {
            'default': {
                'family': 'Comic Sans MS',  # 読みにくいフォント
                'size': 12
            }
        }

        self.validation_service._validate_font_accessibility(fonts, report)

        assert len(report.violations) > 0
        assert any('読みにくいフォント' in v['description'] for v in report.violations)


class TestAccessibilityReport:
    """AccessibilityReportのテストクラス"""

    def test_accessibility_report_creation(self):
        """AccessibilityReport作成テスト"""
        report = AccessibilityReport('AA')

        assert report.wcag_level == 'AA'
        assert len(report.contrast_ratios) == 0
        assert len(report.violations) == 0
        assert len(report.suggestions) == 0
        assert report.score == 0.0
        assert report.total_checks == 0
        assert report.passed_checks == 0

    def test_add_contrast_ratio(self):
        """コントラスト比追加テスト"""
        report = AccessibilityReport()
        report.add_contrast_ratio('text/background', 4.5)

        assert 'text/background' in report.contrast_ratios
        assert report.contrast_ratios['text/background'] == 4.5

    def test_add_violation(self):
        """違反追加テスト"""
        report = AccessibilityReport()
        report.add_violation(
            'test_violation',
            'Test violation description',
            'error',
            'Test suggestion'
        )

        assert len(report.violations) == 1
        violation = report.violations[0]
        assert violation['type'] == 'test_violation'
        assert violation['description'] == 'Test violation description'
        assert violation['severity'] == 'error'
        assert violation['suggestion'] == 'Test suggestion'

    def test_add_suggestion(self):
        """改善提案追加テスト"""
        report = AccessibilityReport()
        report.add_suggestion('Test suggestion')

        assert len(report.suggestions) == 1
        assert report.suggestions[0] == 'Test suggestion'

    def test_calculate_score(self):
        """スコア計算テスト"""
        report = AccessibilityReport()
        report.total_checks = 10
        report.passed_checks = 7

        report.calculate_score()

        assert report.score == 70.0

    def test_calculate_score_no_checks(self):
        """チェックがない場合のスコア計算テスト"""
        report = AccessibilityReport()
        report.total_checks = 0
        report.passed_checks = 0

        report.calculate_score()

        assert report.score == 0.0

    def test_is_compliant_no_errors(self):
        """エラーがない場合の準拠判定テスト"""
        report = AccessibilityReport()
        report.add_violation('test', 'Test warning', 'warning')

        assert report.is_compliant()

    def test_is_compliant_with_errors(self):
        """エラーがある場合の準拠判定テスト"""
        report = AccessibilityReport()
        report.add_violation('test', 'Test error', 'error')

        assert not report.is_compliant()

    def test_to_dict(self):
        """辞書変換テスト"""
        report = AccessibilityReport('AAA')
        report.add_contrast_ratio('text/background', 4.5)
        report.add_violation('test', 'Test violation', 'error')
        report.add_suggestion('Test suggestion')
        report.total_checks = 5
        report.passed_checks = 3
        report.calculate_score()

        result = report.to_dict()

        assert isinstance(result, dict)
        assert result['wcag_level'] == 'AAA'
        assert result['contrast_ratios']['text/background'] == 4.5
        assert len(result['violations']) == 1
        assert len(result['suggestions']) == 1
        assert result['score'] == 60.0
        assert result['total_checks'] == 5
        assert result['passed_checks'] == 3
        assert result['is_compliant'] is False

    def test_string_representation(self):
        """文字列表現テスト"""
        report = AccessibilityReport('AA')
        report.add_contrast_ratio('text/background', 4.5)
        report.add_violation('test', 'Test violation', 'error')
        report.add_suggestion('Test suggestion')
        report.total_checks = 5
        report.passed_checks = 3
        report.calculate_score()

        str_repr = str(report)

        assert 'WCAG AA' in str_repr
        assert '60.0%' in str_repr
        assert 'text/background: 4.50' in str_repr
        assert 'Test violation' in str_repr
        assert 'Test suggestion' in str_repr
