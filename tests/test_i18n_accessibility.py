"""
国際化とアクセシビリティ機能のテスト

このモジュールは、Qt-Theme-Studioの国際化機能と
アクセシビリティ機能のテストを実装します。
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from qt_theme_studio.utilities.i18n_manager import I18nManager
from qt_theme_studio.utilities.japanese_file_handler import JapaneseFileHandler
from qt_theme_studio.utilities.accessibility_manager import AccessibilityManager, AccessibilityReport
from qt_theme_studio.adapters.qt_adapter import QtAdapter


class TestI18nManager(unittest.TestCase):
    """国際化管理のテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.qt_adapter = Mock()
        self.qt_adapter.get_qt_modules.return_value = {
            'QtCore': Mock(),
            'QtWidgets': Mock(),
            'QtGui': Mock()
        }
        
        # QApplicationのモック
        mock_app = Mock()
        self.qt_adapter.get_qt_modules.return_value['QtWidgets'].QApplication.instance.return_value = mock_app
        
        self.i18n_manager = I18nManager(self.qt_adapter)
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.i18n_manager)
        self.assertEqual(self.i18n_manager.current_language, "ja_JP")
        self.assertIsInstance(self.i18n_manager.translations, dict)
    
    def test_translation_fallback(self):
        """フォールバック翻訳テスト"""
        # 既存の翻訳
        translated = self.i18n_manager.tr("File")
        self.assertEqual(translated, "ファイル")
        
        # 存在しない翻訳（元のテキストを返す）
        untranslated = self.i18n_manager.tr("NonExistentText")
        self.assertEqual(untranslated, "NonExistentText")
    
    def test_get_available_languages(self):
        """利用可能言語取得テスト"""
        languages = self.i18n_manager.get_available_languages()
        self.assertIn("ja_JP", languages)
        self.assertIn("en_US", languages)
        self.assertEqual(languages["ja_JP"], "日本語")
    
    def test_create_translation_file(self):
        """翻訳ファイル作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 一時的に翻訳パスを変更
            original_method = self.i18n_manager._get_translation_path
            self.i18n_manager._get_translation_path = lambda: temp_dir
            
            ts_file = self.i18n_manager.create_translation_file()
            
            self.assertTrue(os.path.exists(ts_file))
            self.assertTrue(ts_file.endswith('.ts'))
            
            # ファイル内容の確認
            with open(ts_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('<?xml version="1.0" encoding="utf-8"?>', content)
                self.assertIn('<TS version="2.1" language="ja_JP">', content)
            
            # 元のメソッドを復元
            self.i18n_manager._get_translation_path = original_method
    
    def test_japanese_file_path_handling(self):
        """日本語ファイルパス処理テスト"""
        japanese_path = "/テスト/ディレクトリ/ファイル.txt"
        processed_path = self.i18n_manager.handle_japanese_file_paths(japanese_path)
        
        # パスが正規化されていることを確認
        self.assertIsInstance(processed_path, str)
        self.assertTrue(len(processed_path) > 0)
    
    def test_japanese_text_validation(self):
        """日本語テキスト検証テスト"""
        # 有効な日本語テキスト
        valid_text = "これは有効な日本語テキストです"
        self.assertTrue(self.i18n_manager.validate_japanese_text(valid_text))
        
        # 制御文字を含む無効なテキスト
        invalid_text = "無効な\x00テキスト"
        self.assertFalse(self.i18n_manager.validate_japanese_text(invalid_text))
    
    def test_localized_error_messages(self):
        """ローカライズされたエラーメッセージテスト"""
        error_msg = self.i18n_manager.get_localized_error_message(
            "file_not_found", file_path="/test/file.txt"
        )
        self.assertIn("ファイルが見つかりません", error_msg)
        self.assertIn("/test/file.txt", error_msg)
    
    def test_localized_status_messages(self):
        """ローカライズされたステータスメッセージテスト"""
        status_msg = self.i18n_manager.get_localized_status_message(
            "theme_loaded", theme_name="テストテーマ"
        )
        self.assertIn("テーマを読み込みました", status_msg)
        self.assertIn("テストテーマ", status_msg)


class TestJapaneseFileHandler(unittest.TestCase):
    """日本語ファイル処理のテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.file_handler = JapaneseFileHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """テストクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_path_normalization(self):
        """パス正規化テスト"""
        test_path = "テスト\\ディレクトリ/ファイル.txt"
        normalized = self.file_handler.normalize_path(test_path)
        
        self.assertIsInstance(normalized, str)
        # パス区切り文字が統一されていることを確認
        self.assertNotIn('\\', normalized.replace(os.sep, ''))
    
    def test_path_validation(self):
        """パス検証テスト"""
        # 有効なパス
        valid_path = "テスト/ファイル.txt"
        self.assertTrue(self.file_handler.validate_path(valid_path))
        
        # 無効なパス（空文字）
        self.assertFalse(self.file_handler.validate_path(""))
        
        # 無効なパス（制御文字）
        invalid_path = "テスト\x00ファイル.txt"
        self.assertFalse(self.file_handler.validate_path(invalid_path))
    
    def test_safe_file_operations(self):
        """安全なファイル操作テスト"""
        test_file = os.path.join(self.temp_dir, "テストファイル.txt")
        test_content = "これはテスト用の日本語コンテンツです。\nひらがな、カタカナ、漢字を含みます。"
        
        # ファイル書き込みテスト
        success = self.file_handler.safe_write(test_file, test_content)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(test_file))
        
        # ファイル読み込みテスト
        read_content = self.file_handler.safe_read(test_file)
        self.assertEqual(read_content, test_content)
    
    def test_safe_filename_generation(self):
        """安全なファイル名生成テスト"""
        # 日本語ファイル名
        japanese_name = "テスト<ファイル>名.txt"
        safe_name = self.file_handler.get_safe_filename(japanese_name)
        
        # 無効な文字が置換されていることを確認
        self.assertNotIn('<', safe_name)
        self.assertNotIn('>', safe_name)
        self.assertIn('テスト', safe_name)
    
    def test_encoding_detection(self):
        """エンコーディング検出テスト"""
        test_file = os.path.join(self.temp_dir, "encoding_test.txt")
        
        # UTF-8でファイルを作成
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("日本語テキスト")
        
        encoding_info = self.file_handler.get_encoding_info(test_file)
        
        self.assertIn('detected_encoding', encoding_info)
        self.assertIn('is_utf8', encoding_info)
        self.assertTrue(encoding_info['is_utf8'])
    
    def test_japanese_file_listing(self):
        """日本語ファイル一覧テスト"""
        # 日本語ファイル名のテストファイルを作成
        japanese_files = [
            "日本語ファイル1.txt",
            "テストファイル2.json",
            "english_file.txt"  # 英語ファイル名
        ]
        
        for filename in japanese_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("test content")
        
        # 日本語ファイルのみを取得
        japanese_file_list = self.file_handler.list_japanese_files(self.temp_dir)
        
        # 日本語ファイル名のファイルのみが含まれていることを確認
        japanese_count = sum(1 for f in japanese_file_list 
                           if any(name in f for name in ["日本語ファイル1.txt", "テストファイル2.json"]))
        self.assertEqual(japanese_count, 2)


class TestAccessibilityManager(unittest.TestCase):
    """アクセシビリティ管理のテスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.qt_adapter = Mock()
        self.qt_adapter.get_qt_modules.return_value = {
            'QtCore': Mock(),
            'QtWidgets': Mock(),
            'QtGui': Mock()
        }
        
        self.accessibility_manager = AccessibilityManager(self.qt_adapter)
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertIsNotNone(self.accessibility_manager)
        self.assertEqual(self.accessibility_manager.wcag_aa_ratio, 4.5)
        self.assertEqual(self.accessibility_manager.wcag_aaa_ratio, 7.0)
    
    def test_contrast_ratio_calculation(self):
        """コントラスト比計算テスト"""
        # 黒と白のコントラスト比（最大値）
        contrast = self.accessibility_manager._calculate_contrast_ratio("#000000", "#ffffff")
        self.assertAlmostEqual(contrast, 21.0, places=1)
        
        # 同じ色のコントラスト比（最小値）
        contrast = self.accessibility_manager._calculate_contrast_ratio("#ffffff", "#ffffff")
        self.assertAlmostEqual(contrast, 1.0, places=1)
    
    def test_color_contrast_check(self):
        """色コントラストチェックテスト"""
        # AA準拠のコントラスト比
        result = self.accessibility_manager.check_color_contrast("#000000", "#ffffff")
        
        self.assertIn('contrast_ratio', result)
        self.assertIn('aa_compliant', result)
        self.assertIn('aaa_compliant', result)
        self.assertTrue(result['aa_compliant'])
        self.assertTrue(result['aaa_compliant'])
        
        # 不十分なコントラスト比
        result = self.accessibility_manager.check_color_contrast("#888888", "#999999")
        self.assertFalse(result['aa_compliant'])
    
    def test_accessibility_report_generation(self):
        """アクセシビリティレポート生成テスト"""
        theme_data = {
            'colors': {
                'foreground': '#000000',
                'background': '#ffffff',
                'text': '#333333',
                'button_background': '#f0f0f0'
            },
            'fonts': {
                'default': {'size': 12},
                'small': {'size': 10}  # 小さすぎるフォント
            }
        }
        
        report = self.accessibility_manager.generate_accessibility_report(theme_data)
        
        self.assertIsInstance(report, AccessibilityReport)
        self.assertIn('wcag_level', report.__dict__)
        self.assertIn('contrast_ratios', report.__dict__)
        self.assertIn('violations', report.__dict__)
        self.assertIn('suggestions', report.__dict__)
        
        # 小さいフォントサイズの警告があることを確認
        violations_text = ' '.join(report.violations)
        self.assertIn('small', violations_text)
    
    def test_accessibility_settings(self):
        """アクセシビリティ設定テスト"""
        # 初期設定の取得
        initial_settings = self.accessibility_manager.get_accessibility_settings()
        self.assertIn('high_contrast_mode', initial_settings)
        self.assertIn('large_text_mode', initial_settings)
        
        # 設定の変更
        new_settings = {
            'high_contrast_mode': True,
            'large_text_mode': True,
            'keyboard_navigation_enabled': False
        }
        
        self.accessibility_manager.apply_accessibility_settings(new_settings)
        
        updated_settings = self.accessibility_manager.get_accessibility_settings()
        self.assertTrue(updated_settings['high_contrast_mode'])
        self.assertTrue(updated_settings['large_text_mode'])
        self.assertFalse(updated_settings['keyboard_navigation_enabled'])
    
    def test_high_contrast_mode_toggle(self):
        """高コントラストモード切り替えテスト"""
        initial_state = self.accessibility_manager.high_contrast_mode
        
        self.accessibility_manager.toggle_high_contrast_mode()
        
        self.assertEqual(self.accessibility_manager.high_contrast_mode, not initial_state)
    
    def test_large_text_mode_toggle(self):
        """大きなテキストモード切り替えテスト"""
        initial_state = self.accessibility_manager.large_text_mode
        
        self.accessibility_manager.toggle_large_text_mode()
        
        self.assertEqual(self.accessibility_manager.large_text_mode, not initial_state)


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        """テストセットアップ"""
        self.qt_adapter = Mock()
        self.qt_adapter.get_qt_modules.return_value = {
            'QtCore': Mock(),
            'QtWidgets': Mock(),
            'QtGui': Mock()
        }
        
        self.i18n_manager = I18nManager(self.qt_adapter)
        self.file_handler = JapaneseFileHandler()
        self.accessibility_manager = AccessibilityManager(self.qt_adapter)
    
    def test_japanese_theme_file_processing(self):
        """日本語テーマファイル処理の統合テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 日本語ファイル名でテーマファイルを作成
            theme_file = os.path.join(temp_dir, "日本語テーマ.json")
            theme_data = {
                'name': '日本語テーマ',
                'description': 'これは日本語のテーマです',
                'colors': {
                    'foreground': '#000000',
                    'background': '#ffffff'
                },
                'fonts': {
                    'default': {'size': 12, 'family': 'メイリオ'}
                }
            }
            
            # ファイル保存
            import json
            content = json.dumps(theme_data, ensure_ascii=False, indent=2)
            success = self.file_handler.safe_write(theme_file, content)
            self.assertTrue(success)
            
            # ファイル読み込み
            read_content = self.file_handler.safe_read(theme_file)
            self.assertIsNotNone(read_content)
            
            # JSON解析
            parsed_data = json.loads(read_content)
            self.assertEqual(parsed_data['name'], '日本語テーマ')
            self.assertIn('メイリオ', parsed_data['fonts']['default']['family'])
    
    def test_accessibility_with_japanese_content(self):
        """日本語コンテンツでのアクセシビリティテスト"""
        japanese_theme_data = {
            'name': '日本語アクセシブルテーマ',
            'colors': {
                'foreground': '#000000',
                'background': '#ffffff',
                'text': '#333333',
                'button_background': '#f0f0f0'
            },
            'fonts': {
                'default': {'size': 14, 'family': 'メイリオ'},
                'heading': {'size': 18, 'family': 'メイリオ'}
            }
        }
        
        # アクセシビリティレポート生成
        report = self.accessibility_manager.generate_accessibility_report(japanese_theme_data)
        
        self.assertIsInstance(report, AccessibilityReport)
        self.assertTrue(len(report.contrast_ratios) > 0)
        
        # 日本語フォントが適切に処理されていることを確認
        # （具体的な検証は実装に依存）
        self.assertIsNotNone(report.wcag_level)
    
    def test_error_message_localization(self):
        """エラーメッセージのローカライゼーションテスト"""
        # 存在しないファイルの読み込みを試行
        non_existent_file = "/存在しない/ファイル.txt"
        
        result = self.file_handler.safe_read(non_existent_file)
        self.assertIsNone(result)
        
        # ローカライズされたエラーメッセージを取得
        error_msg = self.i18n_manager.get_localized_error_message(
            "file_not_found", file_path=non_existent_file
        )
        
        self.assertIn("ファイルが見つかりません", error_msg)
        self.assertIn(non_existent_file, error_msg)


if __name__ == '__main__':
    unittest.main()