"""
テーマサービスのテスト
"""

import pytest

from qt_theme_studio.services.theme_service import (
    ThemeConversionError,
    ThemeService,
    ThemeTemplate,
    ThemeTemplateError,
    ValidationResult,
)


class TestThemeService:
    """ThemeServiceのテストクラス"""

    def setup_method(self):
        """テストメソッドの前処理"""
        self.theme_service = ThemeService()

        # テスト用のテーマデータ
        self.valid_theme_data = {
            'name': 'Test Theme',
            'version': '1.0.0',
            'colors': {
                'primary': '#007ACC',
                'secondary': '#005A9E',
                'background': '#FFFFFF',
                'surface': '#F5F5F5',
                'text': '#333333'
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
            }
        }

    def test_validate_theme_valid_data(self):
        """有効なテーマデータの検証テスト"""
        result = self.theme_service.validate_theme(self.valid_theme_data)

        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_theme_missing_required_fields(self):
        """必須フィールドが不足している場合のテスト"""
        invalid_data = {
            'name': 'Test Theme'
            # version, colors, fonts が不足
        }

        result = self.theme_service.validate_theme(invalid_data)

        assert not result.is_valid
        assert len(result.errors) >= 3  # version, colors, fonts
        assert any('version' in error for error in result.errors)
        assert any('colors' in error for error in result.errors)
        assert any('fonts' in error for error in result.errors)

    def test_validate_theme_invalid_color_format(self):
        """無効な色形式の場合のテスト"""
        invalid_data = self.valid_theme_data.copy()
        invalid_data['colors'] = {
            'primary': 'invalid_color',
            'background': '#FFFFFF'
        }

        result = self.theme_service.validate_theme(invalid_data)

        assert not result.is_valid
        assert any('invalid_color' in error for error in result.errors)

    def test_validate_theme_invalid_font_structure(self):
        """無効なフォント構造の場合のテスト"""
        invalid_data = self.valid_theme_data.copy()
        invalid_data['fonts'] = {
            'default': {
                # family が不足
                'size': 10
            }
        }

        result = self.theme_service.validate_theme(invalid_data)

        assert not result.is_valid
        assert any('family' in error for error in result.errors)

    def test_convert_theme_format_json(self):
        """JSON形式への変換テスト"""
        result = self.theme_service.convert_theme_format(self.valid_theme_data, 'json')

        assert isinstance(result, str)
        assert 'Test Theme' in result
        assert '"colors"' in result

    def test_convert_theme_format_qss(self):
        """QSS形式への変換テスト"""
        result = self.theme_service.convert_theme_format(self.valid_theme_data, 'qss')

        assert isinstance(result, str)
        assert 'Test Theme' in result
        assert 'QWidget' in result
        assert '#007ACC' in result  # primary color

    def test_convert_theme_format_css(self):
        """CSS形式への変換テスト"""
        result = self.theme_service.convert_theme_format(self.valid_theme_data, 'css')

        assert isinstance(result, str)
        assert 'Test Theme' in result
        assert ':root' in result
        assert '--color-primary' in result

    def test_convert_theme_format_unsupported(self):
        """サポートされていない形式の場合のテスト"""
        with pytest.raises(ThemeConversionError):
            self.theme_service.convert_theme_format(self.valid_theme_data, 'unsupported')

    def test_convert_theme_format_invalid_data(self):
        """無効なデータの変換テスト"""
        invalid_data = {'name': 'Test'}  # 必須フィールドが不足

        with pytest.raises(ThemeConversionError):
            self.theme_service.convert_theme_format(invalid_data, 'json')

    def test_get_theme_templates(self):
        """テーマテンプレート取得テスト"""
        templates = self.theme_service.get_theme_templates()

        assert isinstance(templates, list)
        assert len(templates) > 0

        # 組み込みテンプレートの確認
        template_names = [t.name for t in templates]
        assert 'ライトテーマ' in template_names
        assert 'ダークテーマ' in template_names
        assert 'ハイコントラストテーマ' in template_names

    def test_get_template_by_name(self):
        """名前によるテンプレート取得テスト"""
        template = self.theme_service.get_template_by_name('ライトテーマ')

        assert template is not None
        assert isinstance(template, ThemeTemplate)
        assert template.name == 'ライトテーマ'
        assert 'colors' in template.data
        assert 'fonts' in template.data

    def test_get_template_by_name_not_found(self):
        """存在しないテンプレート名の場合のテスト"""
        template = self.theme_service.get_template_by_name('NonExistentTemplate')

        assert template is None

    def test_get_templates_by_category(self):
        """カテゴリによるテンプレート取得テスト"""
        templates = self.theme_service.get_templates_by_category('basic')

        assert isinstance(templates, list)
        assert len(templates) > 0

        # すべてのテンプレートが指定されたカテゴリに属することを確認
        for template in templates:
            assert template.category == 'basic'

    def test_get_templates_by_tag(self):
        """タグによるテンプレート取得テスト"""
        templates = self.theme_service.get_templates_by_tag('accessible')

        assert isinstance(templates, list)
        assert len(templates) > 0

        # すべてのテンプレートが指定されたタグを持つことを確認
        for template in templates:
            assert 'accessible' in template.tags

    def test_create_theme_from_template(self):
        """テンプレートからのテーマ作成テスト"""
        theme_data = self.theme_service.create_theme_from_template('ライトテーマ')

        assert isinstance(theme_data, dict)
        assert 'name' in theme_data
        assert 'colors' in theme_data
        assert 'fonts' in theme_data
        assert 'created_date' in theme_data
        assert 'template_source' in theme_data
        assert theme_data['template_source'] == 'ライトテーマ'

    def test_create_theme_from_template_custom_name(self):
        """カスタム名でのテンプレートからのテーマ作成テスト"""
        custom_name = 'My Custom Theme'
        theme_data = self.theme_service.create_theme_from_template(
            'ライトテーマ', custom_name
        )

        assert theme_data['name'] == custom_name

    def test_create_theme_from_template_not_found(self):
        """存在しないテンプレートからの作成テスト"""
        with pytest.raises(ThemeTemplateError):
            self.theme_service.create_theme_from_template('NonExistentTemplate')

    def test_clear_templates_cache(self):
        """テンプレートキャッシュクリアテスト"""
        # 最初にテンプレートを読み込んでキャッシュを作成
        templates1 = self.theme_service.get_theme_templates()

        # キャッシュをクリア
        self.theme_service.clear_templates_cache()

        # 再度読み込み
        templates2 = self.theme_service.get_theme_templates()

        # 同じ内容が取得できることを確認
        assert len(templates1) == len(templates2)


class TestValidationResult:
    """ValidationResultのテストクラス"""

    def test_validation_result_creation(self):
        """ValidationResult作成テスト"""
        result = ValidationResult(True)

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error(self):
        """エラー追加テスト"""
        result = ValidationResult(True)
        result.add_error('Test error')

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0] == 'Test error'

    def test_add_warning(self):
        """警告追加テスト"""
        result = ValidationResult(True)
        result.add_warning('Test warning')

        assert result.is_valid  # 警告は有効性に影響しない
        assert len(result.warnings) == 1
        assert result.warnings[0] == 'Test warning'

    def test_string_representation(self):
        """文字列表現テスト"""
        result = ValidationResult(False)
        result.add_error('Test error')
        result.add_warning('Test warning')

        str_repr = str(result)
        assert '無効' in str_repr
        assert 'Test error' in str_repr
        assert 'Test warning' in str_repr


class TestThemeTemplate:
    """ThemeTemplateのテストクラス"""

    def test_theme_template_creation(self):
        """ThemeTemplate作成テスト"""
        data = {'colors': {'primary': '#007ACC'}}
        template = ThemeTemplate(
            name='Test Template',
            description='Test description',
            data=data,
            category='test',
            tags=['test', 'sample']
        )

        assert template.name == 'Test Template'
        assert template.description == 'Test description'
        assert template.data == data
        assert template.category == 'test'
        assert template.tags == ['test', 'sample']

    def test_to_dict(self):
        """辞書変換テスト"""
        data = {'colors': {'primary': '#007ACC'}}
        template = ThemeTemplate(
            name='Test Template',
            description='Test description',
            data=data
        )

        result = template.to_dict()

        assert isinstance(result, dict)
        assert result['name'] == 'Test Template'
        assert result['description'] == 'Test description'
        assert result['data'] == data
        assert result['category'] == 'general'  # デフォルト値
        assert result['tags'] == []  # デフォルト値

    def test_from_dict(self):
        """辞書からの作成テスト"""
        data = {
            'name': 'Test Template',
            'description': 'Test description',
            'data': {'colors': {'primary': '#007ACC'}},
            'category': 'test',
            'tags': ['test']
        }

        template = ThemeTemplate.from_dict(data)

        assert template.name == 'Test Template'
        assert template.description == 'Test description'
        assert template.data == data['data']
        assert template.category == 'test'
        assert template.tags == ['test']
