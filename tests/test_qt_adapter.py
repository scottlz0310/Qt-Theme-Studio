"""
Qt Adapter単体テスト

Qt Adapterの各機能をテストし、各フレームワークでの動作を検証します。
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from qt_theme_studio.adapters.qt_adapter import QtAdapter, QtFrameworkNotFoundError


class TestQtAdapter:
    """Qt Adapterのテストクラス"""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理"""
        self.adapter = QtAdapter()

    def test_init(self):
        """Qt Adapterの初期化テスト"""
        adapter = QtAdapter()
        assert adapter._detected_framework is None
        assert adapter._qt_modules is None
        assert adapter._application is None
        assert not adapter.is_initialized

    @patch('builtins.__import__')
    def test_detect_qt_framework_pyside6(self, mock_import):
        """PySide6が検出される場合のテスト"""
        # PySide6のインポートは成功、他は失敗
        def side_effect(name, *args, **kwargs):
            if name == 'PySide6':
                return MagicMock()
            raise ImportError("No module named '{name}'")

        mock_import.side_effect = side_effect

        framework = self.adapter.detect_qt_framework()
        assert framework == 'PySide6'
        assert self.adapter._detected_framework == 'PySide6'

    @patch('builtins.__import__')
    def test_detect_qt_framework_pyqt6(self, mock_import):
        """PyQt6が検出される場合のテスト（PySide6が利用不可）"""
        # PySide6は失敗、PyQt6は成功
        def side_effect(name, *args, **kwargs):
            if name == 'PySide6':
                raise ImportError("No module named '{name}'")
            elif name == 'PyQt6':
                return MagicMock()
            raise ImportError("No module named '{name}'")

        mock_import.side_effect = side_effect

        framework = self.adapter.detect_qt_framework()
        assert framework == 'PyQt6'
        assert self.adapter._detected_framework == 'PyQt6'

    @patch('builtins.__import__')
    def test_detect_qt_framework_pyqt5(self, mock_import):
        """PyQt5が検出される場合のテスト（PySide6、PyQt6が利用不可）"""
        # PySide6、PyQt6は失敗、PyQt5は成功
        def side_effect(name, *args, **kwargs):
            if name in ['PySide6', 'PyQt6']:
                raise ImportError("No module named '{name}'")
            elif name == 'PyQt5':
                return MagicMock()
            raise ImportError("No module named '{name}'")

        mock_import.side_effect = side_effect

        framework = self.adapter.detect_qt_framework()
        assert framework == 'PyQt5'
        assert self.adapter._detected_framework == 'PyQt5'

    @patch('builtins.__import__')
    def test_detect_qt_framework_not_found(self, mock_import):
        """フレームワークが見つからない場合のテスト"""
        # すべてのフレームワークのインポートが失敗
        def side_effect(name, *args, **kwargs):
            raise ImportError("No module found")

        mock_import.side_effect = side_effect

        with pytest.raises(QtFrameworkNotFoundError) as exc_info:
            self.adapter.detect_qt_framework()

        assert "利用可能なQtフレームワークが見つかりません" in str(exc_info.value)

    def test_detect_qt_framework_cached(self):
        """フレームワーク検出結果のキャッシュテスト"""
        with patch('builtins.__import__') as mock_import:
            mock_import.return_value = MagicMock()

            # 最初の呼び出し
            framework1 = self.adapter.detect_qt_framework()
            initial_call_count = mock_import.call_count

            # 2回目の呼び出し（キャッシュされた結果を使用）
            framework2 = self.adapter.detect_qt_framework()

            assert framework1 == framework2
            # 2回目の呼び出しでは__import__は実行されない（キャッシュを使用）
            assert mock_import.call_count == initial_call_count

    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.detect_qt_framework')
    def test_get_qt_modules_pyside6(self, mock_detect):
        """PySide6モジュール取得テスト"""
        mock_detect.return_value = 'PySide6'

        # PySide6モジュールをモック
        mock_qtwidgets = MagicMock()
        mock_qtcore = MagicMock()
        mock_qtgui = MagicMock()

        with patch.dict('sys.modules', {
            'PySide6': MagicMock(),
            'PySide6.QtWidgets': mock_qtwidgets,
            'PySide6.QtCore': mock_qtcore,
            'PySide6.QtGui': mock_qtgui,
        }):
            modules = self.adapter.get_qt_modules()

            assert modules['framework'] == 'PySide6'
            assert 'QtWidgets' in modules
            assert 'QtCore' in modules
            assert 'QtGui' in modules

    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.detect_qt_framework')
    def test_get_qt_modules_pyqt6(self, mock_detect):
        """PyQt6モジュール取得テスト"""
        mock_detect.return_value = 'PyQt6'

        # PyQt6モジュールをモック
        mock_qtwidgets = MagicMock()
        mock_qtcore = MagicMock()
        mock_qtgui = MagicMock()

        with patch.dict('sys.modules', {
            'PyQt6': MagicMock(),
            'PyQt6.QtWidgets': mock_qtwidgets,
            'PyQt6.QtCore': mock_qtcore,
            'PyQt6.QtGui': mock_qtgui,
        }):
            modules = self.adapter.get_qt_modules()

            assert modules['framework'] == 'PyQt6'
            assert 'QtWidgets' in modules
            assert 'QtCore' in modules
            assert 'QtGui' in modules

    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.detect_qt_framework')
    def test_get_qt_modules_pyqt5(self, mock_detect):
        """PyQt5モジュール取得テスト"""
        mock_detect.return_value = 'PyQt5'

        # PyQt5モジュールをモック
        mock_qtwidgets = MagicMock()
        mock_qtcore = MagicMock()
        mock_qtgui = MagicMock()

        with patch.dict('sys.modules', {
            'PyQt5': MagicMock(),
            'PyQt5.QtWidgets': mock_qtwidgets,
            'PyQt5.QtCore': mock_qtcore,
            'PyQt5.QtGui': mock_qtgui,
        }):
            modules = self.adapter.get_qt_modules()

            assert modules['framework'] == 'PyQt5'
            assert 'QtWidgets' in modules
            assert 'QtCore' in modules
            assert 'QtGui' in modules

    def test_get_qt_modules_cached(self):
        """モジュール取得結果のキャッシュテスト"""
        with patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.detect_qt_framework') as mock_detect:
            mock_detect.return_value = 'PySide6'

            with patch.dict('sys.modules', {
                'PySide6': MagicMock(),
                'PySide6.QtWidgets': MagicMock(),
                'PySide6.QtCore': MagicMock(),
                'PySide6.QtGui': MagicMock(),
            }):
                # 最初の呼び出し
                modules1 = self.adapter.get_qt_modules()
                # 2回目の呼び出し（キャッシュされた結果を使用）
                modules2 = self.adapter.get_qt_modules()

                assert modules1 is modules2

    def test_get_qt_modules_import_error(self):
        """モジュールインポートエラーのテスト"""
        # フレームワークが検出されていない状態でget_qt_modulesを呼び出す
        with patch('builtins.__import__') as mock_import:
            def side_effect(name, *args, **kwargs):
                raise ImportError("No module named '{name}'")

            mock_import.side_effect = side_effect

            with pytest.raises(QtFrameworkNotFoundError) as exc_info:
                self.adapter.get_qt_modules()

            assert "利用可能なQtフレームワークが見つかりません" in str(exc_info.value)

    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.get_qt_modules')
    def test_create_application_new(self, mock_get_modules):
        """新しいQApplication作成テスト"""
        # QtWidgetsモジュールをモック
        mock_qtwidgets = MagicMock()
        mock_qapp_class = MagicMock()
        mock_qapp_instance = MagicMock()

        # QApplication.instance()がNoneを返す（既存のアプリケーションなし）
        mock_qapp_class.instance.return_value = None
        mock_qapp_class.return_value = mock_qapp_instance
        mock_qtwidgets.QApplication = mock_qapp_class

        mock_get_modules.return_value = {'QtWidgets': mock_qtwidgets}

        app = self.adapter.create_application("Test-App")

        assert app is mock_qapp_instance
        assert self.adapter._application is mock_qapp_instance

        # QApplicationが正しい引数で作成されたことを確認
        mock_qapp_class.assert_called_once_with(sys.argv)
        mock_qapp_instance.setApplicationName.assert_called_once_with("Test-App")
        mock_qapp_instance.setApplicationDisplayName.assert_called_once_with("Test-App")
        mock_qapp_instance.setApplicationVersion.assert_called_once_with("1.0.0")

    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.get_qt_modules')
    def test_create_application_existing(self, mock_get_modules):
        """既存のQApplication使用テスト"""
        # QtWidgetsモジュールをモック
        mock_qtwidgets = MagicMock()
        mock_qapp_class = MagicMock()
        mock_existing_app = MagicMock()

        # QApplication.instance()が既存のアプリケーションを返す
        mock_qapp_class.instance.return_value = mock_existing_app
        mock_qtwidgets.QApplication = mock_qapp_class

        mock_get_modules.return_value = {'QtWidgets': mock_qtwidgets}

        app = self.adapter.create_application("Test-App")

        assert app is mock_existing_app
        assert self.adapter._application is mock_existing_app

        # 新しいQApplicationは作成されない
        mock_qapp_class.assert_not_called()

    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.get_qt_modules')
    def test_create_application_error(self, mock_get_modules):
        """QApplication作成エラーテスト"""
        # QtWidgetsモジュールをモック
        mock_qtwidgets = MagicMock()
        mock_qapp_class = MagicMock()

        # QApplication作成時にエラーが発生
        mock_qapp_class.instance.return_value = None
        mock_qapp_class.side_effect = Exception("QApplication creation failed")
        mock_qtwidgets.QApplication = mock_qapp_class

        mock_get_modules.return_value = {'QtWidgets': mock_qtwidgets}

        with pytest.raises(QtFrameworkNotFoundError) as exc_info:
            self.adapter.create_application("Test-App")

        assert "QApplicationの作成に失敗しました" in str(exc_info.value)

    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.detect_qt_framework')
    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.get_qt_modules')
    def test_get_framework_info(self, mock_get_modules, mock_detect):
        """フレームワーク情報取得テスト"""
        mock_detect.return_value = 'PySide6'

        # QtCoreモジュールをモック
        mock_qtcore = MagicMock()
        mock_qtcore.qVersion.return_value = '6.5.0'
        mock_get_modules.return_value = {'QtCore': mock_qtcore}

        info = self.adapter.get_framework_info()

        assert info['name'] == 'PySide6'
        assert info['version'] == '6.5.0'

    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.detect_qt_framework')
    @patch('qt_theme_studio.adapters.qt_adapter.QtAdapter.get_qt_modules')
    def test_get_framework_info_no_version(self, mock_get_modules, mock_detect):
        """バージョン情報が取得できない場合のテスト"""
        mock_detect.return_value = 'PyQt6'

        # QtCoreモジュールにバージョン情報がない
        mock_qtcore = MagicMock()
        del mock_qtcore.qVersion
        del mock_qtcore.__version__
        mock_get_modules.return_value = {'QtCore': mock_qtcore}

        info = self.adapter.get_framework_info()

        assert info['name'] == 'PyQt6'
        assert info['version'] == 'unknown'

    def test_is_initialized_false(self):
        """初期化状態テスト（未初期化）"""
        adapter = QtAdapter()
        assert not adapter.is_initialized

    def test_is_initialized_true(self):
        """初期化状態テスト（初期化済み）"""
        adapter = QtAdapter()
        adapter._detected_framework = 'PySide6'
        adapter._qt_modules = {'QtWidgets': MagicMock()}

        assert adapter.is_initialized

    def test_application_property(self):
        """applicationプロパティテスト"""
        adapter = QtAdapter()
        assert adapter.application is None

        mock_app = MagicMock()
        adapter._application = mock_app
        assert adapter.application is mock_app


class TestQtAdapterIntegration:
    """Qt Adapterの統合テスト（実際のQtフレームワークが必要）"""

    def test_real_framework_detection(self):
        """実際のフレームワーク検出テスト

        注意: このテストは実際のQtフレームワークがインストールされている場合のみ実行されます。
        """
        adapter = QtAdapter()

        try:
            framework = adapter.detect_qt_framework()
            assert framework in ['PySide6', 'PyQt6', 'PyQt5']

            modules = adapter.get_qt_modules()
            assert 'QtWidgets' in modules
            assert 'QtCore' in modules
            assert 'QtGui' in modules
            assert modules['framework'] == framework

            info = adapter.get_framework_info()
            assert info['name'] == framework
            assert 'version' in info

            assert adapter.is_initialized

        except QtFrameworkNotFoundError:
            # Qtフレームワークがインストールされていない場合はスキップ
            pytest.skip("Qtフレームワークがインストールされていません")


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
