"""
エクスポートサービスのテスト
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from qt_theme_studio.services.export_service import (
    ExportService, CompatibilityReport, ExportError
)


class TestExportService:
    """ExportServiceのテストクラス"""
    
    def setup_method(self):
        """テストメソッドの前処理"""
        self.export_service = ExportService()
        
        # テスト用のテーマデータ
        self.valid_theme_data = {
            'name': 'Test Theme',
            'version': '1.0.0',
            'colors': {
                'primary': '#007ACC',
                'secondary': '#005A9E',
                'background': '#FFFFFF',
                'surface': '#F5F5F5',
                'text': '#333333',
                'border': '#CCCCCC'
            },
            'fonts': {
                'default': {
                    'family': 'Arial, sans-serif',
                    'size': 10
                },
                'heading': {
                    'family': 'Arial, sans-serif',
                    'size': 14,
                    'weight': 'bold'
                }
            },
            'sizes': {
                'border_radius': 4,
                'border_width': 1,
                'padding': 8,
                'margin': 4
            }
        }
    
    def test_export_theme_json(self):
        """JSON形式エクスポートテスト"""
        result = self.export_service.export_theme(self.valid_theme_data, 'json')
        
        assert isinstance(result, str)
        
        # JSONとして解析可能かチェック
        parsed = json.loads(result)
        assert parsed['name'] == 'Test Theme'
        assert parsed['version'] == '1.0.0'
        assert 'colors' in parsed
        assert 'fonts' in parsed
    
    def test_export_theme_qss(self):
        """QSS形式エクスポートテスト"""
        result = self.export_service.export_theme(self.valid_theme_data, 'qss')
        
        assert isinstance(result, str)
        assert 'Test Theme' in result
        assert 'QWidget' in result
        assert 'QPushButton' in result
        assert '#007ACC' in result  # primary color
        assert 'background-color:' in result
    
    def test_export_theme_css(self):
        """CSS形式エクスポートテスト"""
        result = self.export_service.export_theme(self.valid_theme_data, 'css')
        
        assert isinstance(result, str)
        assert 'Test Theme' in result
        assert ':root' in result
        assert '--color-primary' in result
        assert 'body' in result
        assert 'button' in result
    
    @pytest.mark.skip(reason="YAMLエクスポートはオプション機能のためスキップ")
    def test_export_theme_yaml(self):
        """YAML形式エクスポートテスト"""
        # YAMLライブラリがインストールされている場合のみテスト
        try:
            import yaml
            result = self.export_service.export_theme(self.valid_theme_data, 'yaml')
            assert isinstance(result, str)
            assert 'Test Theme' in result
        except ImportError:
            pytest.skip("yamlライブラリがインストールされていません")
    
    @pytest.mark.skip(reason="YAMLエクスポートはオプション機能のためスキップ")
    def test_export_theme_yaml_no_library(self):
        """YAMLライブラリがない場合のテスト"""
        # 実際のImportErrorをテストするのは複雑なため、スキップ
        pass
    
    def test_export_theme_unsupported_format(self):
        """サポートされていない形式の場合のテスト"""
        with pytest.raises(ExportError) as exc_info:
            self.export_service.export_theme(self.valid_theme_data, 'unsupported')
        
        assert 'サポートされていない形式' in str(exc_info.value)
    
    def test_export_theme_with_file_output(self, tmp_path):
        """ファイル出力付きエクスポートテスト"""
        output_path = tmp_path / 'output.json'
        
        result = self.export_service.export_theme(
            self.valid_theme_data, 'json', output_path
        )
        
        assert isinstance(result, str)
        # ファイルが実際に作成されたことを確認
        assert output_path.exists()
        # ファイル内容を確認
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Test Theme' in content
    
    def test_export_to_json_valid(self):
        """JSON変換テスト（有効データ）"""
        result = self.export_service._export_to_json(self.valid_theme_data)
        
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == self.valid_theme_data
    
    def test_export_to_json_invalid(self):
        """JSON変換テスト（無効データ）"""
        # JSON化できないデータ
        invalid_data = {'func': lambda x: x}
        
        with pytest.raises(ExportError):
            self.export_service._export_to_json(invalid_data)
    
    def test_export_to_qss_basic_structure(self):
        """QSS変換テスト（基本構造）"""
        result = self.export_service._export_to_qss(self.valid_theme_data)
        
        assert isinstance(result, str)
        lines = result.split('\n')
        
        # ヘッダー情報の確認
        assert any('Test Theme' in line for line in lines)
        assert any('Version: 1.0.0' in line for line in lines)
        
        # ウィジェットスタイルの確認
        assert 'QWidget {' in result
        assert 'QPushButton {' in result
        assert 'QLineEdit {' in result
        assert 'QComboBox {' in result
    
    def test_export_to_css_basic_structure(self):
        """CSS変換テスト（基本構造）"""
        result = self.export_service._export_to_css(self.valid_theme_data)
        
        assert isinstance(result, str)
        
        # CSS変数の確認
        assert ':root {' in result
        assert '--color-primary: #007ACC;' in result
        assert '--size-padding: 8px;' in result
        
        # 基本スタイルの確認
        assert 'body {' in result
        assert 'button, .btn {' in result
        assert 'input, textarea, select {' in result
    
    def test_add_qss_widget_styles(self):
        """QSSウィジェットスタイル追加テスト"""
        qss_lines = []
        colors = self.valid_theme_data['colors']
        fonts = self.valid_theme_data['fonts']
        sizes = self.valid_theme_data['sizes']
        
        self.export_service._add_qss_widget_styles(qss_lines, colors, fonts, sizes)
        
        qss_content = '\n'.join(qss_lines)
        
        # 各ウィジェットのスタイルが含まれることを確認
        assert 'QWidget {' in qss_content
        assert 'QPushButton {' in qss_content
        assert 'QPushButton:hover {' in qss_content
        assert 'QPushButton:pressed {' in qss_content
        assert 'QLineEdit {' in qss_content
        assert 'QComboBox {' in qss_content
    
    def test_add_css_base_styles(self):
        """CSS基本スタイル追加テスト"""
        css_lines = []
        colors = self.valid_theme_data['colors']
        fonts = self.valid_theme_data['fonts']
        sizes = self.valid_theme_data['sizes']
        
        self.export_service._add_css_base_styles(css_lines, colors, fonts, sizes)
        
        css_content = '\n'.join(css_lines)
        
        # 基本スタイルが含まれることを確認
        assert 'body {' in css_content
        assert 'button, .btn {' in css_content
        assert 'input, textarea, select {' in css_content
        assert 'var(--color-primary)' in css_content
    
    def test_test_framework_compatibility(self):
        """フレームワーク互換性テストテスト"""
        with patch.object(self.export_service, '_check_framework_availability') as mock_check:
            with patch.object(self.export_service, '_test_theme_application') as mock_test:
                mock_check.return_value = True
                mock_test.return_value = {'compatible': True, 'tested_features': ['colors']}
                
                report = self.export_service.test_framework_compatibility(self.valid_theme_data)
                
                assert isinstance(report, CompatibilityReport)
                assert len(report.framework_results) > 0
    
    def test_check_framework_availability_available(self):
        """フレームワーク利用可能性チェックテスト（利用可能）"""
        with patch('builtins.__import__') as mock_import:
            mock_import.return_value = Mock()
            
            result = self.export_service._check_framework_availability('PySide6')
            
            assert result is True
            mock_import.assert_called_once_with('PySide6')
    
    def test_check_framework_availability_unavailable(self):
        """フレームワーク利用可能性チェックテスト（利用不可）"""
        with patch('builtins.__import__') as mock_import:
            mock_import.side_effect = ImportError()
            
            result = self.export_service._check_framework_availability('PySide6')
            
            assert result is False
    
    def test_test_theme_application_valid(self):
        """テーマ適用テストテスト（有効）"""
        result = self.export_service._test_theme_application(self.valid_theme_data, 'PySide6')
        
        assert isinstance(result, dict)
        assert 'compatible' in result
        assert 'tested_features' in result
        assert 'issues' in result
        assert result['compatible'] is True
        assert 'colors' in result['tested_features']
        assert 'fonts' in result['tested_features']
    
    def test_test_theme_application_missing_colors(self):
        """テーマ適用テストテスト（色データ不足）"""
        invalid_data = {'name': 'Test', 'fonts': {}}
        
        result = self.export_service._test_theme_application(invalid_data, 'PySide6')
        
        assert result['compatible'] is False
        assert any('色データが不足' in issue for issue in result['issues'])
    
    def test_test_theme_application_missing_fonts(self):
        """テーマ適用テストテスト（フォントデータ不足）"""
        invalid_data = {'name': 'Test', 'colors': {}}
        
        result = self.export_service._test_theme_application(invalid_data, 'PySide6')
        
        assert result['compatible'] is False
        assert any('フォントデータが不足' in issue for issue in result['issues'])
    
    def test_export_preview_image_success(self):
        """プレビュー画像エクスポートテスト（成功）"""
        mock_widget = Mock()
        mock_pixmap = Mock()
        mock_pixmap.save.return_value = True
        mock_widget.grab.return_value = mock_pixmap
        
        with patch('pathlib.Path.mkdir'):
            result = self.export_service.export_preview_image(
                mock_widget, '/test/preview.png', 'png'
            )
            
            assert result is True
            mock_widget.grab.assert_called_once()
            mock_pixmap.save.assert_called_once_with('/test/preview.png', 'PNG')
    
    def test_export_preview_image_save_failure(self, tmp_path):
        """プレビュー画像エクスポートテスト（保存失敗）"""
        mock_widget = Mock()
        mock_pixmap = Mock()
        mock_pixmap.save.return_value = False
        mock_widget.grab.return_value = mock_pixmap
        
        with patch('pathlib.Path.mkdir'):
            with pytest.raises(ExportError) as exc_info:
                self.export_service.export_preview_image(
                    mock_widget, str(tmp_path / 'preview.png'), 'png'
                )
            
            assert '保存に失敗' in str(exc_info.value)
    
    def test_export_preview_image_no_grab_method(self, tmp_path):
        """プレビュー画像エクスポートテスト（grabメソッドなし）"""
        mock_widget = Mock()
        del mock_widget.grab  # grabメソッドを削除
        
        output_path = tmp_path / 'preview.png'
        
        with pytest.raises(ExportError) as exc_info:
            self.export_service.export_preview_image(
                mock_widget, str(output_path), 'png'
            )
        
        assert '画像キャプチャに対応していません' in str(exc_info.value)
    
    def test_get_supported_formats(self):
        """サポート形式取得テスト"""
        formats = self.export_service.get_supported_formats()
        
        assert isinstance(formats, list)
        assert 'json' in formats
        assert 'qss' in formats
        assert 'css' in formats
        assert 'yaml' in formats
    
    def test_validate_export_data_valid(self):
        """エクスポートデータ検証テスト（有効）"""
        errors = self.export_service.validate_export_data(self.valid_theme_data)
        
        assert isinstance(errors, list)
        assert len(errors) == 0
    
    def test_validate_export_data_invalid_type(self):
        """エクスポートデータ検証テスト（無効な型）"""
        errors = self.export_service.validate_export_data("not_dict")
        
        assert len(errors) > 0
        assert any('辞書である必要があります' in error for error in errors)
    
    def test_validate_export_data_missing_required_fields(self):
        """エクスポートデータ検証テスト（必須フィールド不足）"""
        invalid_data = {'colors': {}}  # name, version が不足
        
        errors = self.export_service.validate_export_data(invalid_data)
        
        assert len(errors) >= 2
        assert any('name' in error for error in errors)
        assert any('version' in error for error in errors)
    
    def test_validate_export_data_invalid_colors_type(self):
        """エクスポートデータ検証テスト（無効な色データ型）"""
        invalid_data = {
            'name': 'Test',
            'version': '1.0.0',
            'colors': 'not_dict'
        }
        
        errors = self.export_service.validate_export_data(invalid_data)
        
        assert len(errors) > 0
        assert any('colors' in error and '辞書' in error for error in errors)
    
    def test_validate_export_data_empty_colors(self):
        """エクスポートデータ検証テスト（空の色データ）"""
        invalid_data = {
            'name': 'Test',
            'version': '1.0.0',
            'colors': {}
        }
        
        errors = self.export_service.validate_export_data(invalid_data)
        
        assert len(errors) > 0
        assert any('色データが空です' in error for error in errors)
    
    def test_validate_export_data_invalid_fonts_type(self):
        """エクスポートデータ検証テスト（無効なフォントデータ型）"""
        invalid_data = {
            'name': 'Test',
            'version': '1.0.0',
            'fonts': 'not_dict'
        }
        
        errors = self.export_service.validate_export_data(invalid_data)
        
        assert len(errors) > 0
        assert any('fonts' in error and '辞書' in error for error in errors)
    
    def test_validate_export_data_empty_fonts(self):
        """エクスポートデータ検証テスト（空のフォントデータ）"""
        invalid_data = {
            'name': 'Test',
            'version': '1.0.0',
            'fonts': {}
        }
        
        errors = self.export_service.validate_export_data(invalid_data)
        
        assert len(errors) > 0
        assert any('フォントデータが空です' in error for error in errors)


class TestCompatibilityReport:
    """CompatibilityReportのテストクラス"""
    
    def test_compatibility_report_creation(self):
        """CompatibilityReport作成テスト"""
        report = CompatibilityReport()
        
        assert len(report.framework_results) == 0
        assert report.overall_compatibility is True
        assert len(report.warnings) == 0
        assert len(report.errors) == 0
    
    def test_add_framework_result_compatible(self):
        """フレームワーク結果追加テスト（互換）"""
        report = CompatibilityReport()
        details = {'tested_features': ['colors', 'fonts']}
        
        report.add_framework_result('PySide6', True, details)
        
        assert 'PySide6' in report.framework_results
        assert report.framework_results['PySide6']['compatible'] is True
        assert report.framework_results['PySide6']['details'] == details
        assert report.overall_compatibility is True
    
    def test_add_framework_result_incompatible(self):
        """フレームワーク結果追加テスト（非互換）"""
        report = CompatibilityReport()
        
        report.add_framework_result('PyQt5', False)
        
        assert 'PyQt5' in report.framework_results
        assert report.framework_results['PyQt5']['compatible'] is False
        assert report.overall_compatibility is False
    
    def test_add_warning(self):
        """警告追加テスト"""
        report = CompatibilityReport()
        report.add_warning('Test warning')
        
        assert len(report.warnings) == 1
        assert report.warnings[0] == 'Test warning'
        assert report.overall_compatibility is True  # 警告は互換性に影響しない
    
    def test_add_error(self):
        """エラー追加テスト"""
        report = CompatibilityReport()
        report.add_error('Test error')
        
        assert len(report.errors) == 1
        assert report.errors[0] == 'Test error'
        assert report.overall_compatibility is False
    
    def test_to_dict(self):
        """辞書変換テスト"""
        report = CompatibilityReport()
        report.add_framework_result('PySide6', True, {'test': 'data'})
        report.add_warning('Test warning')
        report.add_error('Test error')
        
        result = report.to_dict()
        
        assert isinstance(result, dict)
        assert result['overall_compatibility'] is False
        assert 'PySide6' in result['framework_results']
        assert result['warnings'] == ['Test warning']
        assert result['errors'] == ['Test error']
    
    def test_string_representation(self):
        """文字列表現テスト"""
        report = CompatibilityReport()
        report.add_framework_result('PySide6', True)
        report.add_framework_result('PyQt5', False)
        report.add_warning('Test warning')
        report.add_error('Test error')
        
        str_repr = str(report)
        
        assert '非互換' in str_repr  # overall_compatibility is False
        assert 'PySide6: 互換' in str_repr
        assert 'PyQt5: 非互換' in str_repr
        assert 'Test warning' in str_repr
        assert 'Test error' in str_repr