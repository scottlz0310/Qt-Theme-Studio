"""
テーマデータフィクスチャ

テストで使用するサンプルテーマデータとヘルパー関数
"""

import json
from pathlib import Path
from typing import Any, 


def create_sample_theme(name: str = "Test Theme") -> dict[str, Any]:
    """サンプルテーマを作成"""
    return {
        "name": name,
        "version": "1.0.0",
        "description": f"{name} - テスト用テーマ",
        "author": "Test User",
        "colors": {
            "primary": "#007acc",
            "secondary": "#6c757d",
            "background": "#ffffff",
            "surface": "#f8f9fa",
            "text": "#212529",
            "text_secondary": "#6c757d",
            "border": "#dee2e6",
            "accent": "#28a745",
            "error": "#dc3545",
            "warning": "#ffc107"
        },
        "fonts": {
            "default": "Arial",
            "monospace": "Consolas",
            "size": {
                "small": 10,
                "normal": 12,
                "large": 14,
                "title": 18
            }
        },
        "spacing": {
            "xs": 4,
            "sm": 8,
            "md": 16,
            "lg": 24,
            "xl": 32
        },
        "border_radius": 4,
        "shadows": {
            "enabled": True,
            "color": "rgba(0, 0, 0, 0.1)"
        }
    }


def create_dark_theme(name: str = "Dark Test Theme") -> dict[str, Any]:
    """ダークテーマのサンプルを作成"""
    theme = create_sample_theme(name)
    theme["colors"].update({
        "background": "#1e1e1e",
        "surface": "#2d2d30",
        "text": "#ffffff",
        "text_secondary": "#cccccc",
        "border": "#3e3e42"
    })
    return theme


def create_minimal_theme(name: str = "Minimal Theme") -> dict[str, Any]:
    """最小限のテーマを作成"""
    return {
        "name": name,
        "version": "1.0.0",
        "colors": {
            "primary": "#000000",
            "background": "#ffffff"
        }
    }


def save_theme_to_file(theme: dict[str, Any], file_path: Path) -> None:
    """テーマをファイルに保存"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(theme, f, indent=2, ensure_ascii=False)


def load_theme_from_file(file_path: Path) -> dict[str, Any]:
    """ファイルからテーマを読み込み"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_test_themes() -> list[dict[str, Any]]:
    """テスト用のテーマリストを取得"""
    themes: list[dict[str, Any]] = [
        create_sample_theme("Light Theme"),
        create_dark_theme("Dark Theme"),
        create_minimal_theme("Minimal Theme")
    ]
    return themes
