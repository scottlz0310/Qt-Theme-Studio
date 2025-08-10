"""
デフォルト設定値定義

このモジュールは、Qt-Theme-Studioアプリケーションのデフォルト設定値を定義します。
"""

from typing import Any, Dict

# アプリケーションのデフォルト設定値
DEFAULT_SETTINGS: Dict[str, Any] = {
    'window': {
        'width': 1200,
        'height': 800,
        'x': 100,
        'y': 100,
        'maximized': False,
        'splitter_state': None,
        'toolbar_visible': True,
        'status_bar_visible': True
    },
    'theme': {
        'recent_themes': [],
        'max_recent_themes': 10,
        'last_opened_theme': None,
        'auto_save': True,
        'auto_save_interval': 300,  # 5分（秒）
        'backup_enabled': True,
        'backup_count': 5
    },
    'editor': {
        'show_preview': True,
        'preview_update_delay': 100,  # ミリ秒
        'show_zebra_editor': True,
        'wcag_level': 'AA',
        'color_picker_type': 'advanced',  # 'basic', 'advanced'
        'show_color_names': True,
        'undo_limit': 50
    },
    'ui': {
        'language': 'ja',
        'theme': 'default',
        'show_tooltips': True,
        'show_status_bar': True,
        'font_family': None,  # システムデフォルトを使用
        'font_size': 9,
        'icon_theme': 'default'
    },
    'export': {
        'default_format': 'json',
        'export_directory': None,  # Noneの場合はホームディレクトリを使用
        'include_metadata': True,
        'compress_output': False,
        'validate_on_export': True
    },
    'preview': {
        'update_delay': 500,  # ミリ秒
        'show_widget_names': True,
        'show_grid': False,
        'background_color': '#f0f0f0',
        'widget_spacing': 10
    },
    'accessibility': {
        'default_wcag_level': 'AA',
        'show_contrast_warnings': True,
        'auto_suggest_improvements': True,
        'highlight_violations': True
    },
    'performance': {
        'enable_caching': True,
        'cache_size_mb': 50,
        'lazy_loading': True,
        'max_undo_memory_mb': 20
    },
    'logging': {
        'level': 'INFO',
        'file_logging': True,
        'console_logging': True,
        'max_log_files': 5,
        'max_log_size_mb': 10
    }
}

# テーマエディターのデフォルト設定
THEME_EDITOR_DEFAULTS: Dict[str, Any] = {
    'color_categories': [
        'primary',
        'secondary', 
        'background',
        'surface',
        'error',
        'warning',
        'info',
        'success'
    ],
    'font_categories': [
        'default',
        'heading',
        'body',
        'caption',
        'button'
    ],
    'size_categories': [
        'small',
        'medium',
        'large',
        'extra_large'
    ]
}

# ゼブラパターンエディターのデフォルト設定
ZEBRA_EDITOR_DEFAULTS: Dict[str, Any] = {
    'wcag_levels': {
        'AA': {
            'normal_text': 4.5,
            'large_text': 3.0
        },
        'AAA': {
            'normal_text': 7.0,
            'large_text': 4.5
        }
    },
    'color_suggestions': {
        'max_suggestions': 5,
        'prefer_darker': True,
        'maintain_hue': True
    }
}

# プレビューウィンドウのデフォルト設定
PREVIEW_DEFAULTS: Dict[str, Any] = {
    'widgets': [
        'QPushButton',
        'QLineEdit',
        'QComboBox',
        'QListWidget',
        'QTreeWidget',
        'QTableWidget',
        'QTabWidget',
        'QGroupBox',
        'QCheckBox',
        'QRadioButton',
        'QSlider',
        'QProgressBar',
        'QSpinBox',
        'QLabel',
        'QTextEdit'
    ],
    'widget_states': [
        'normal',
        'hover',
        'pressed',
        'disabled',
        'focused'
    ]
}

# エクスポート形式のデフォルト設定
EXPORT_FORMAT_DEFAULTS: Dict[str, Any] = {
    'json': {
        'indent': 2,
        'ensure_ascii': False,
        'include_comments': True
    },
    'qss': {
        'minify': False,
        'include_comments': True,
        'sort_selectors': True
    },
    'css': {
        'minify': False,
        'include_comments': True,
        'sort_properties': True
    }
}

# ファイルパスのデフォルト設定
PATH_DEFAULTS: Dict[str, Any] = {
    'theme_extensions': ['.json', '.qss', '.css'],
    'backup_extension': '.bak',
    'temp_extension': '.tmp',
    'default_theme_name': 'untitled_theme',
    'config_file_name': 'settings.json',
    'log_file_name': 'qt_theme_studio.log'
}

# バリデーションのデフォルト設定
VALIDATION_DEFAULTS: Dict[str, Any] = {
    'required_properties': [
        'name',
        'version',
        'colors'
    ],
    'color_format_regex': r'^#[0-9A-Fa-f]{6}$',
    'theme_name_regex': r'^[a-zA-Z0-9_\-\s]+$',
    'max_theme_name_length': 50,
    'max_description_length': 200
}


def get_default_settings() -> Dict[str, Any]:
    """デフォルト設定の完全なコピーを取得する
    
    Returns:
        Dict[str, Any]: デフォルト設定のディープコピー
    """
    import copy
    return copy.deepcopy(DEFAULT_SETTINGS)


def get_theme_editor_defaults() -> Dict[str, Any]:
    """テーマエディターのデフォルト設定を取得する
    
    Returns:
        Dict[str, Any]: テーマエディターのデフォルト設定
    """
    import copy
    return copy.deepcopy(THEME_EDITOR_DEFAULTS)


def get_zebra_editor_defaults() -> Dict[str, Any]:
    """ゼブラパターンエディターのデフォルト設定を取得する
    
    Returns:
        Dict[str, Any]: ゼブラパターンエディターのデフォルト設定
    """
    import copy
    return copy.deepcopy(ZEBRA_EDITOR_DEFAULTS)


def get_preview_defaults() -> Dict[str, Any]:
    """プレビューウィンドウのデフォルト設定を取得する
    
    Returns:
        Dict[str, Any]: プレビューウィンドウのデフォルト設定
    """
    import copy
    return copy.deepcopy(PREVIEW_DEFAULTS)


def get_export_format_defaults() -> Dict[str, Any]:
    """エクスポート形式のデフォルト設定を取得する
    
    Returns:
        Dict[str, Any]: エクスポート形式のデフォルト設定
    """
    import copy
    return copy.deepcopy(EXPORT_FORMAT_DEFAULTS)


def get_path_defaults() -> Dict[str, Any]:
    """ファイルパスのデフォルト設定を取得する
    
    Returns:
        Dict[str, Any]: ファイルパスのデフォルト設定
    """
    import copy
    return copy.deepcopy(PATH_DEFAULTS)


def get_validation_defaults() -> Dict[str, Any]:
    """バリデーションのデフォルト設定を取得する
    
    Returns:
        Dict[str, Any]: バリデーションのデフォルト設定
    """
    import copy
    return copy.deepcopy(VALIDATION_DEFAULTS)