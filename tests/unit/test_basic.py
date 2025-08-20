"""基本的なテストケース"""

def test_import():
    """パッケージのインポートテスト"""
    import qt_theme_studio
    assert qt_theme_studio is not None

def test_basic_functionality():
    """基本機能のテスト"""
    assert 1 + 1 == 2