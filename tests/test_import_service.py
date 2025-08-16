"""
テーマインポートサービスのテスト実装

このモジュールは、テーマインポートサービスの機能をテストします。
"""

import json
import tempfile
import unittest

from qt_theme_studio.services.import_service import ImportError, ThemeImportService


class TestThemeImportService(unittest.TestCase):
    """テーマインポートサービスのテスト"""

    def setUp(self):
        """各テスト前の初期化"""
        self.import_service = ThemeImportService()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """各テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_supported_formats(self):
        """サポート形式テスト"""
        formats = self.import_service.get_supported_formats()

        expected_formats = ['.json', '.qss', '.css']
        self.assertEqual(set(formats), set(expected_formats))

    def test_format_descriptions(self):
        """形式説明テスト"""
        desc_json = self.import_service.get_format_description('.json')
        desc_qss = self.import_service.get_format_description('.qss')
        desc_css = self.import_service.get_format_description('.css')

        self.assertIn('JSON', desc_json)
        self.assertIn('Qt Style Sheet', desc_qss)
        self.assertIn('Cascading Style Sheet', desc_css)

    def test_import_json_theme(self):
        """JSONテーマインポートテスト"""
        # テストJSONファイル作成
        theme_data = {
            'name': 'テストテーマ',
            'version': '1.0.0',
            'colors': {
                'primary': '#0078d4',
                'secondary': '#106ebe',
                'background': '#ffff'
            },
            'fonts': {
                'default': {
                    'family': 'Arial',
                    'size': 12
                }
            }
        }

        json_file = os.path.join(self.temp_dir, 'test_theme.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, ensure_ascii=False)

        # インポート実行
        imported = self.import_service.import_theme(json_file)

        # 結果確認
        self.assertEqual(imported['name'], 'テストテーマ')
        self.assertEqual(imported['version'], '1.0.0')
        self.assertIn('primary', imported['colors'])
        self.assertEqual(imported['colors']['primary'], '#0078d4')
        self.assertIn('metadata', imported)
        self.assertIn('imported_from', imported['metadata'])

    def test_import_qss_theme(self):
        """QSSテーマインポートテスト"""
        # テストQSSファイル作成
        qss_content = """
        QWidget {
            background-color: #ffffff;
            color: #000000;
            font-family: "Arial";
            font-size: 12px;
        }

        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: 1px solid #106ebe;
        }

        QPushButton:hover {
            background-color: #106ebe;
        }
        """

        qss_file = os.path.join(self.temp_dir, 'test_theme.qss')
        with open(qss_file, 'w', encoding='utf-8') as f:
            f.write(qss_content)

        # インポート実行
        imported = self.import_service.import_theme(qss_file)

        # 結果確認
        self.assertEqual(imported['name'], 'test_theme')
        self.assertIn('colors', imported)
        self.assertIn('fonts', imported)
        self.assertIn('qss_content', imported['properties'])
        self.assertEqual(imported['metadata']['source_format'], 'qss')

    def test_import_css_theme(self):
        """CSSテーマインポートテスト"""
        # テストCSSファイル作成
        css_content = """
        :root {
            --primary-color: #0078d4;
            --secondary-color: #106ebe;
            --background-color: #ffffff;
        }

        body {
            background-color: var(--background-color);
            color: #000000;
            font-family: Arial, sans-serif;
            font-size: 14px;
        }

        .button {
            background-color: var(--primary-color);
            color: white;
        }
        """

        css_file = os.path.join(self.temp_dir, 'test_theme.css')
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_content)

        # インポート実行
        imported = self.import_service.import_theme(css_file)

        # 結果確認
        self.assertEqual(imported['name'], 'test_theme')
        self.assertIn('colors', imported)
        self.assertIn('css_content', imported['properties'])
        self.assertEqual(imported['metadata']['source_format'], 'css')

    def test_import_nonexistent_file(self):
        """存在しないファイルのインポートテスト"""
        nonexistent_file = os.path.join(self.temp_dir, 'nonexistent.json')

        with self.assertRaises(ImportError) as context:
            self.import_service.import_theme(nonexistent_file)

        self.assertIn('ファイルが見つかりません', str(context.exception))

    def test_import_unsupported_format(self):
        """サポートされていない形式のインポートテスト"""
        # テキストファイル作成
        txt_file = os.path.join(self.temp_dir, 'test.txt')
        with open(txt_file, 'w') as f:
            f.write('test content')

        with self.assertRaises(ImportError) as context:
            self.import_service.import_theme(txt_file)

        self.assertIn('サポートされていないファイル形式', str(context.exception))

    def test_import_invalid_json(self):
        """無効なJSONファイルのインポートテスト"""
        # 無効なJSONファイル作成
        json_file = os.path.join(self.temp_dir, 'invalid.json')
        with open(json_file, 'w') as f:
            f.write('invalid json content')

        with self.assertRaises(ImportError) as context:
            self.import_service.import_theme(json_file)

        self.assertIn('JSONファイルの解析エラー', str(context.exception))

    def test_normalize_colors(self):
        """色正規化テスト"""
        colors = {
            'primary': '#0078d4',
            'secondary': '0x106ebe',
            'background': 'ffff',
            'surface': 'f',
            'rgb_dict': {'r': 255, 'g': 0, 'b': 0},
            'rgb_list': [0, 255, 0],
            'named': 'blue'
        }

        normalized = self.import_service.normalize_colors(colors)

        self.assertEqual(normalized['primary'], '#0078d4')
        self.assertEqual(normalized['secondary'], '#106ebe')
        self.assertEqual(normalized['background'], '#ffff')
        self.assertEqual(normalized['surface'], '#ffff')
        self.assertEqual(normalized['rgb_dict'], '#ff0000')
        self.assertEqual(normalized['rgb_list'], '#00ff00')
        self.assertEqual(normalized['named'], 'blue')

    def test_normalize_fonts(self):
        """フォント正規化テスト"""
        fonts = {
            'simple': 'Arial',
            'detailed': {
                'family': 'Helvetica',
                'size': 14,
                'weight': 'bold',
                'style': 'italic'
            }
        }

        normalized = self.import_service.normalize_fonts(fonts)

        # 簡単な形式
        self.assertEqual(normalized['simple']['family'], 'Arial')
        self.assertEqual(normalized['simple']['size'], 12)
        self.assertEqual(normalized['simple']['weight'], 'normal')

        # 詳細な形式
        self.assertEqual(normalized['detailed']['family'], 'Helvetica')
        self.assertEqual(normalized['detailed']['size'], 14)
        self.assertEqual(normalized['detailed']['weight'], 'bold')
        self.assertEqual(normalized['detailed']['style'], 'italic')

    def test_normalize_sizes(self):
        """サイズ正規化テスト"""
        sizes = {
            'int_value': 16,
            'float_value': 14.5,
            'string_value': '12px',
            'string_only_number': '10',
            'invalid': 'invalid'
        }

        normalized = self.import_service.normalize_sizes(sizes)

        self.assertEqual(normalized['int_value'], 16)
        self.assertEqual(normalized['float_value'], 14)
        self.assertEqual(normalized['string_value'], 12)
        self.assertEqual(normalized['string_only_number'], 10)
        self.assertEqual(normalized['invalid'], 12)  # デフォルト値

    def test_extract_colors_from_qss(self):
        """QSSからの色抽出テスト"""
        qss_content = """
        QWidget {
            color: #000000;
            background-color: #ffffff;
            border-color: #cccccc;
        }

        QPushButton {
            background-color: #0078d4;
            selection-background-color: #106ebe;
        }
        """

        colors = self.import_service.extract_colors_from_qss(qss_content)

        # 色が抽出されることを確認
        self.assertGreater(len(colors), 0)

        # 抽出された色値の確認
        color_values = list(colors.values())
        self.assertIn('#000000', color_values)
        self.assertIn('#ffff', color_values)
        self.assertIn('#0078d4', color_values)

    def test_validate_imported_theme(self):
        """インポートテーマ検証テスト"""
        # 有効なテーマ
        valid_theme = {
            'name': 'テストテーマ',
            'version': '1.0.0',
            'colors': {
                'primary': '#0078d4',
                'invalid_color': 'invalid'
            }
        }

        errors = self.import_service.validate_imported_theme(valid_theme)
        self.assertEqual(len(errors), 1)  # 無効な色値のエラーのみ
        self.assertIn('invalid_color', errors[0])

        # 無効なテーマ（必須フィールド不足）
        invalid_theme = {
            'colors': {'primary': '#0078d4'}
        }

        errors = self.import_service.validate_imported_theme(invalid_theme)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('name' in error for error in errors))

    def test_is_valid_color(self):
        """色値妥当性テスト"""
        # 有効な色値
        self.assertTrue(self.import_service.is_valid_color('#ffff'))
        self.assertTrue(self.import_service.is_valid_color('#f'))
        self.assertTrue(self.import_service.is_valid_color('#123ABC'))
        self.assertTrue(self.import_service.is_valid_color('red'))
        self.assertTrue(self.import_service.is_valid_color('blue'))

        # 無効な色値
        self.assertFalse(self.import_service.is_valid_color('#gggggg'))
        self.assertFalse(self.import_service.is_valid_color('invalid'))
        self.assertFalse(self.import_service.is_valid_color(123))
        self.assertFalse(self.import_service.is_valid_color(None))

    def test_add_import_metadata(self):
        """インポートメタデータ追加テスト"""
        theme_data = {
            'name': 'テストテーマ',
            'version': '1.0.0'
        }

        test_file = Path(self.temp_dir) / 'test.json'
        test_file.write_text('{}')

        updated_theme = self.import_service.add_import_metadata(theme_data, test_file)

        # メタデータが追加されることを確認
        self.assertIn('metadata', updated_theme)
        self.assertIn('imported_from', updated_theme['metadata'])
        self.assertIn('imported_at', updated_theme['metadata'])
        self.assertIn('original_format', updated_theme['metadata'])
        self.assertIn('created_at', updated_theme)

        # ファイル情報の確認
        self.assertEqual(updated_theme['metadata']['original_format'], '.json')
        self.assertGreater(updated_theme['metadata']['file_size'], 0)


if __name__ == '__main__':
    unittest.main()
