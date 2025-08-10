# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# プロジェクトルートディレクトリ
project_root = Path(__file__).parent

# アプリケーション情報
app_name = 'qt-theme-studio'
app_version = '1.0.0'
app_description = 'Qt-Theme-Studio - 統合テーマエディター'

# 隠れたインポートを明示的に指定
hiddenimports = [
    'qt_theme_studio',
    'qt_theme_studio.main',
    'qt_theme_studio.adapters',
    'qt_theme_studio.adapters.qt_adapter',
    'qt_theme_studio.adapters.theme_adapter',
    'qt_theme_studio.config',
    'qt_theme_studio.config.settings',
    'qt_theme_studio.controllers',
    'qt_theme_studio.controllers.theme_controller',
    'qt_theme_studio.services',
    'qt_theme_studio.services.theme_service',
    'qt_theme_studio.services.export_service',
    'qt_theme_studio.services.validation_service',
    'qt_theme_studio.utilities',
    'qt_theme_studio.utilities.color_analyzer',
    'qt_theme_studio.utilities.color_improver',
    'qt_theme_studio.views',
    'qt_theme_studio.views.main_window',
    'qt_theme_studio.views.theme_editor',
    'qt_theme_studio.views.zebra_editor',
    'qt_theme_studio.views.preview',
    'qt_theme_studio.views.theme_gallery',
    'qt_theme_studio.logger',
    'qt_theme_studio.error_handler',
    'qt_theme_studio.exceptions',
    # Qt関連
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    # その他の依存関係
    'json',
    'yaml',
    'configparser',
    'pathlib',
    'typing',
    'dataclasses',
    'logging',
    'datetime',
    'colorsys',
    'math',
    're',
]

# データファイル
datas = [
    (str(project_root / 'qt_theme_studio' / 'resources'), 'qt_theme_studio/resources'),
    (str(project_root / 'examples'), 'examples'),
    (str(project_root / 'README.md'), '.'),
    (str(project_root / 'INSTALL.md'), '.'),
    (str(project_root / 'RELEASE_NOTES.md'), '.'),
]

# バイナリファイル（必要に応じて）
binaries = []

# 除外するモジュール
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'PIL',
    'cv2',
]

# 分析設定
a = Analysis(
    ['launch_theme_studio.py'],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ設定
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 実行ファイル設定
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUIアプリケーションなのでコンソールを非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
    icon='qt_theme_studio/resources/icons/app_icon.ico' if os.path.exists('qt_theme_studio/resources/icons/app_icon.ico') else None,
)

# macOS用のアプリケーションバンドル設定
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name=f'{app_name}.app',
        icon='qt_theme_studio/resources/icons/app_icon.icns' if os.path.exists('qt_theme_studio/resources/icons/app_icon.icns') else None,
        bundle_identifier=f'com.qt-theme-studio.{app_name}',
        version=app_version,
        info_plist={
            'CFBundleName': 'Qt-Theme-Studio',
            'CFBundleDisplayName': 'Qt-Theme-Studio',
            'CFBundleShortVersionString': app_version,
            'CFBundleVersion': app_version,
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': 'QTTS',
            'CFBundleExecutable': app_name,
            'CFBundleIdentifier': f'com.qt-theme-studio.{app_name}',
            'LSMinimumSystemVersion': '10.13.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Qt Theme File',
                    'CFBundleTypeExtensions': ['json', 'qss', 'css'],
                    'CFBundleTypeRole': 'Editor',
                    'CFBundleTypeIconFile': 'theme_icon.icns',
                }
            ],
        },
    )