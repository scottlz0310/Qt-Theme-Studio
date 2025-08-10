"""
テーマギャラリーのテスト実装

このモジュールは、テーマギャラリーUIの機能をテストします。
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from qt_theme_studio.views.theme_gallery import (
    ThemeGallery, ThemeCard, ThemeLoader
)


class TestThemeCard(unittest.TestCase):
    """テーマカードのテスト"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラス初期化"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
            
    def setUp(self):
        """各テスト前の初期化"""
        self.theme_data = {
            'name': 'テストテーマ',
            'version': '1.0.0',
            'colors': {
                'primary': '#0078d4',
                'secondary': '#106ebe',
                'background': '#ffffff',
                'surface': '#f5f5f5'
            },
            'created_at': '2024-01-01'
        }
        self.theme_path = '/test/path/test_theme.json'
        
    def test_theme_card_creation(self):
        """テーマカード作成テスト"""
        card = ThemeCard(self.theme_path, self.theme_data)
        
        # 基本プロパティの確認
        self.assertEqual(card.theme_path, self.theme_path)
        self.assertEqual(card.theme_data, self.theme_data)
        
        # UI要素の確認
        self.assertIsNotNone(card.thumbnail_label)
        self.assertIsNotNone(card.name_label)
        self.assertIsNotNone(card.select_button)
        self.assertIsNotNone(card.delete_button)
        
        # テキスト内容の確認
        self.assertEqual(card.name_label.text(), 'テストテーマ')
        self.assertIn('1.0.0', card.info_label.text())
        
    def test_theme_card_thumbnail_generation(self):
        """サムネイル生成テスト"""
        card = ThemeCard(self.theme_path, self.theme_data)
        
        # サムネイルが生成されることを確認
        pixmap = card.thumbnail_label.pixmap()
        self.assertIsNotNone(pixmap)
        self.assertFalse(pixmap.isNull())
        
    def test_theme_card_no_colors(self):
        """色情報なしのテーマカードテスト"""
        theme_data_no_colors = {
            'name': 'テストテーマ',
            'version': '1.0.0'
        }
        
        card = ThemeCard(self.theme_path, theme_data_no_colors)
        
        # プレビュー利用不可のテキストが表示されることを確認
        self.assertIn('プレビュー', card.thumbnail_label.text())
        
    def test_select_button_click(self):
        """選択ボタンクリックテスト"""
        card = ThemeCard(self.theme_path, self.theme_data)
        
        # シグナル受信用のモック
        mock_receiver = Mock()
        card.theme_selected.connect(mock_receiver)
        
        # ボタンクリック
        QTest.mouseClick(card.select_button, Qt.LeftButton)
        
        # シグナルが発行されることを確認
        mock_receiver.assert_called_once_with(self.theme_path)
        
    @patch('PySide6.QtWidgets.QMessageBox.question')
    def test_delete_button_click_confirmed(self, mock_question):
        """削除ボタンクリック（確認）テスト"""
        mock_question.return_value = 16384  # QMessageBox.Yes
        
        card = ThemeCard(self.theme_path, self.theme_data)
        
        # シグナル受信用のモック
        mock_receiver = Mock()
        card.theme_deleted.connect(mock_receiver)
        
        # ボタンクリック
        QTest.mouseClick(card.delete_button, Qt.LeftButton)
        
        # 確認ダイアログが表示されることを確認
        mock_question.assert_called_once()
        
        # シグナルが発行されることを確認
        mock_receiver.assert_called_once_with(self.theme_path)
        
    @patch('PySide6.QtWidgets.QMessageBox.question')
    def test_delete_button_click_cancelled(self, mock_question):
        """削除ボタンクリック（キャンセル）テスト"""
        mock_question.return_value = 65536  # QMessageBox.No
        
        card = ThemeCard(self.theme_path, self.theme_data)
        
        # シグナル受信用のモック
        mock_receiver = Mock()
        card.theme_deleted.connect(mock_receiver)
        
        # ボタンクリック
        QTest.mouseClick(card.delete_button, Qt.LeftButton)
        
        # 確認ダイアログが表示されることを確認
        mock_question.assert_called_once()
        
        # シグナルが発行されないことを確認
        mock_receiver.assert_not_called()


class TestThemeLoader(unittest.TestCase):
    """テーマローダーのテスト"""
    
    def setUp(self):
        """各テスト前の初期化"""
        self.temp_dir = tempfile.mkdtemp()
        
        # テストテーマファイル作成
        self.test_theme_data = {
            'name': 'テストテーマ',
            'version': '1.0.0',
            'colors': {'primary': '#0078d4'}
        }
        
        self.theme_file_path = os.path.join(self.temp_dir, 'test_theme.json')
        with open(self.theme_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_theme_data, f, ensure_ascii=False)
            
    def tearDown(self):
        """各テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_theme_loader_success(self):
        """テーマローダー成功テスト"""
        loader = ThemeLoader(self.temp_dir)
        
        # シグナル受信用のモック
        theme_loaded_mock = Mock()
        loading_finished_mock = Mock()
        
        loader.theme_loaded.connect(theme_loaded_mock)
        loader.loading_finished.connect(loading_finished_mock)
        
        # ローダー実行
        loader.run()
        
        # シグナルが発行されることを確認
        theme_loaded_mock.assert_called_once()
        loading_finished_mock.assert_called_once()
        
        # 読み込まれたデータの確認
        args, kwargs = theme_loaded_mock.call_args
        loaded_path, loaded_data = args
        
        self.assertEqual(loaded_path, self.theme_file_path)
        self.assertEqual(loaded_data, self.test_theme_data)
        
    def test_theme_loader_empty_directory(self):
        """空ディレクトリのテーマローダーテスト"""
        empty_dir = tempfile.mkdtemp()
        
        try:
            loader = ThemeLoader(empty_dir)
            
            # シグナル受信用のモック
            theme_loaded_mock = Mock()
            loading_finished_mock = Mock()
            
            loader.theme_loaded.connect(theme_loaded_mock)
            loader.loading_finished.connect(loading_finished_mock)
            
            # ローダー実行
            loader.run()
            
            # テーマが読み込まれないことを確認
            theme_loaded_mock.assert_not_called()
            loading_finished_mock.assert_called_once()
            
        finally:
            import shutil
            shutil.rmtree(empty_dir, ignore_errors=True)
            
    def test_theme_loader_invalid_json(self):
        """無効なJSONファイルのテスト"""
        # 無効なJSONファイル作成
        invalid_file = os.path.join(self.temp_dir, 'invalid.json')
        with open(invalid_file, 'w') as f:
            f.write('invalid json content')
            
        loader = ThemeLoader(self.temp_dir)
        
        # シグナル受信用のモック
        theme_loaded_mock = Mock()
        loading_finished_mock = Mock()
        
        loader.theme_loaded.connect(theme_loaded_mock)
        loader.loading_finished.connect(loading_finished_mock)
        
        # ローダー実行
        loader.run()
        
        # 有効なファイルのみ読み込まれることを確認
        self.assertEqual(theme_loaded_mock.call_count, 1)  # test_theme.jsonのみ
        loading_finished_mock.assert_called_once()


class TestThemeGallery(unittest.TestCase):
    """テーマギャラリーのテスト"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラス初期化"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
            
    def setUp(self):
        """各テスト前の初期化"""
        self.temp_dir = tempfile.mkdtemp()
        self.gallery = ThemeGallery()
        self.gallery.theme_directory = self.temp_dir
        
        # テストテーマファイル作成
        self.create_test_themes()
        
    def tearDown(self):
        """各テスト後のクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def create_test_themes(self):
        """テスト用テーマファイル作成"""
        themes = [
            {
                'name': 'ダークテーマ',
                'version': '1.0.0',
                'colors': {'primary': '#333333'},
                'created_at': '2024-01-01'
            },
            {
                'name': 'ライトテーマ',
                'version': '2.0.0',
                'colors': {'primary': '#ffffff'},
                'created_at': '2024-01-02'
            },
            {
                'name': 'ブルーテーマ',
                'version': '1.5.0',
                'colors': {'primary': '#0078d4'},
                'created_at': '2024-01-03'
            }
        ]
        
        for i, theme_data in enumerate(themes):
            file_path = os.path.join(self.temp_dir, f'theme_{i}.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, ensure_ascii=False)
                
    def test_gallery_initialization(self):
        """ギャラリー初期化テスト"""
        # UI要素の確認
        self.assertIsNotNone(self.gallery.search_edit)
        self.assertIsNotNone(self.gallery.filter_combo)
        self.assertIsNotNone(self.gallery.scroll_area)
        self.assertIsNotNone(self.gallery.import_button)
        self.assertIsNotNone(self.gallery.refresh_button)
        
    def test_search_functionality(self):
        """検索機能テスト"""
        # テーマを手動で追加（テスト用）
        self.gallery.all_themes = [
            ('/path/theme1.json', {'name': 'ダークテーマ'}),
            ('/path/theme2.json', {'name': 'ライトテーマ'}),
            ('/path/theme3.json', {'name': 'ブルーテーマ'})
        ]
        
        # 検索テキスト入力
        self.gallery.search_edit.setText('ダーク')
        self.gallery.apply_filters()
        
        # フィルタ結果の確認
        self.assertEqual(len(self.gallery.filtered_themes), 1)
        self.assertEqual(self.gallery.filtered_themes[0][1]['name'], 'ダークテーマ')
        
    def test_filter_functionality(self):
        """フィルター機能テスト"""
        # テーマを手動で追加（テスト用）
        self.gallery.all_themes = [
            ('/path/theme1.json', {'name': 'Zテーマ', 'version': '1.0.0'}),
            ('/path/theme2.json', {'name': 'Aテーマ', 'version': '2.0.0'}),
            ('/path/theme3.json', {'name': 'Mテーマ', 'version': '1.5.0'})
        ]
        
        # 名前順フィルター適用
        self.gallery.filter_combo.setCurrentText('名前順')
        self.gallery.apply_filters()
        
        # ソート結果の確認
        names = [theme[1]['name'] for theme in self.gallery.filtered_themes]
        self.assertEqual(names, ['Aテーマ', 'Mテーマ', 'Zテーマ'])
        
    def test_version_sort(self):
        """バージョンソートテスト"""
        # テーマを手動で追加（テスト用）
        self.gallery.all_themes = [
            ('/path/theme1.json', {'name': 'テーマ1', 'version': '1.0.0'}),
            ('/path/theme2.json', {'name': 'テーマ2', 'version': '2.0.0'}),
            ('/path/theme3.json', {'name': 'テーマ3', 'version': '1.5.0'})
        ]
        
        # バージョン順フィルター適用
        self.gallery.filter_combo.setCurrentText('バージョン順')
        self.gallery.apply_filters()
        
        # ソート結果の確認（降順）
        versions = [theme[1]['version'] for theme in self.gallery.filtered_themes]
        self.assertEqual(versions, ['2.0.0', '1.5.0', '1.0.0'])
        
    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    @patch('PySide6.QtWidgets.QMessageBox.information')
    def test_import_theme_button(self, mock_info, mock_dialog):
        """テーマインポートボタンテスト"""
        mock_dialog.return_value = ('/test/theme.json', '')
        
        # インポートボタンクリック
        QTest.mouseClick(self.gallery.import_button, Qt.LeftButton)
        
        # ダイアログが表示されることを確認
        mock_dialog.assert_called_once()
        mock_info.assert_called_once()
        
    def test_refresh_button(self):
        """更新ボタンテスト"""
        # 更新ボタンクリック
        QTest.mouseClick(self.gallery.refresh_button, Qt.LeftButton)
        
        # プログレスバーが表示されることを確認
        self.assertTrue(self.gallery.progress_bar.isVisible())
        
    def test_theme_directory_management(self):
        """テーマディレクトリ管理テスト"""
        new_directory = '/new/theme/directory'
        
        # ディレクトリ設定
        self.gallery.set_theme_directory(new_directory)
        
        # 設定が反映されることを確認
        self.assertEqual(self.gallery.get_theme_directory(), new_directory)
        
    @patch('os.remove')
    @patch('PySide6.QtWidgets.QMessageBox.information')
    def test_theme_deletion_success(self, mock_info, mock_remove):
        """テーマ削除成功テスト"""
        # テーマを手動で追加
        test_path = '/test/theme.json'
        self.gallery.all_themes = [(test_path, {'name': 'テストテーマ'})]
        self.gallery.filtered_themes = self.gallery.all_themes.copy()
        
        # 削除処理実行
        self.gallery.on_theme_deleted(test_path)
        
        # ファイル削除が実行されることを確認
        mock_remove.assert_called_once_with(test_path)
        
        # 成功メッセージが表示されることを確認
        mock_info.assert_called_once()
        
        # リストから削除されることを確認
        self.assertEqual(len(self.gallery.all_themes), 0)
        
    @patch('os.remove')
    @patch('PySide6.QtWidgets.QMessageBox.critical')
    def test_theme_deletion_error(self, mock_critical, mock_remove):
        """テーマ削除エラーテスト"""
        mock_remove.side_effect = OSError("削除エラー")
        
        # テーマを手動で追加
        test_path = '/test/theme.json'
        self.gallery.all_themes = [(test_path, {'name': 'テストテーマ'})]
        
        # 削除処理実行
        self.gallery.on_theme_deleted(test_path)
        
        # エラーメッセージが表示されることを確認
        mock_critical.assert_called_once()
        
        # リストから削除されないことを確認
        self.assertEqual(len(self.gallery.all_themes), 1)


if __name__ == '__main__':
    unittest.main()