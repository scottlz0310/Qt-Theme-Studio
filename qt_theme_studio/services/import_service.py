"""
テーマインポートサービス実装

このモジュールは、複数フォーマット（JSON、QSS、CSS）からのテーマ読み込みと
内部形式への変換機能を提供します。
"""

import json
import re
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from ..logger import Logger
from ..exceptions import ThemeStudioException


class ImportError(ThemeStudioException):
    """インポートエラー"""
    pass


class ThemeImportService:
    """テーマインポートサービス"""
    
    def __init__(self):
        self.logger = Logger()
        
        # サポートされるファイル形式
        self.supported_formats = {
            '.json': self.import_from_json,
            '.qss': self.import_from_qss,
            '.css': self.import_from_css
        }
        
    def import_theme(self, file_path: str) -> Dict[str, Any]:
        """
        テーマファイルをインポートして内部形式に変換
        
        Args:
            file_path: インポートするファイルのパス
            
        Returns:
            内部形式のテーマデータ
            
        Raises:
            ImportError: インポート処理でエラーが発生した場合
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise ImportError(f"ファイルが見つかりません: {file_path}")
                
            file_extension = file_path.suffix.lower()
            
            if file_extension not in self.supported_formats:
                raise ImportError(
                    f"サポートされていないファイル形式です: {file_extension}\n"
                    f"サポート形式: {', '.join(self.supported_formats.keys())}"
                )
                
            # ファイル形式に応じたインポート処理
            import_func = self.supported_formats[file_extension]
            theme_data = import_func(file_path)
            
            # 共通メタデータの追加
            theme_data = self.add_import_metadata(theme_data, file_path)
            
            self.logger.log_user_action(
                "テーマインポート成功", 
                {"file": str(file_path), "format": file_extension}
            )
            
            return theme_data
            
        except Exception as e:
            error_msg = f"テーマインポートエラー: {str(e)}"
            self.logger.log_error(error_msg, e)
            raise ImportError(error_msg) from e
            
    def import_from_json(self, file_path: Path) -> Dict[str, Any]:
        """
        JSONファイルからテーマをインポート
        
        Args:
            file_path: JSONファイルのパス
            
        Returns:
            テーマデータ
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # JSONデータの検証と正規化
            return self.normalize_json_theme(data)
            
        except json.JSONDecodeError as e:
            raise ImportError(f"JSONファイルの解析エラー: {str(e)}")
        except Exception as e:
            raise ImportError(f"JSONファイル読み込みエラー: {str(e)}")
            
    def import_from_qss(self, file_path: Path) -> Dict[str, Any]:
        """
        QSSファイルからテーマをインポート
        
        Args:
            file_path: QSSファイルのパス
            
        Returns:
            テーマデータ
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                qss_content = f.read()
                
            # QSSからテーマデータを抽出
            return self.parse_qss_content(qss_content, file_path.stem)
            
        except Exception as e:
            raise ImportError(f"QSSファイル読み込みエラー: {str(e)}")
            
    def import_from_css(self, file_path: Path) -> Dict[str, Any]:
        """
        CSSファイルからテーマをインポート
        
        Args:
            file_path: CSSファイルのパス
            
        Returns:
            テーマデータ
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
                
            # CSSからテーマデータを抽出
            return self.parse_css_content(css_content, file_path.stem)
            
        except Exception as e:
            raise ImportError(f"CSSファイル読み込みエラー: {str(e)}")
            
    def normalize_json_theme(self, data: Any) -> Dict[str, Any]:
        """
        JSONテーマデータの正規化
        
        Args:
            data: 元のJSONデータ
            
        Returns:
            正規化されたテーマデータ
        """
        # 配列形式の場合は最初のテーマを使用
        if isinstance(data, list):
            if not data:
                raise ImportError("テーマデータが空です")
            data = data[0]  # 最初のテーマを使用
            self.logger.info("配列形式のJSONファイルを検出し、最初のテーマを使用します")
            
        if not isinstance(data, dict):
            raise ImportError("テーマデータが辞書形式ではありません")
            
        # 基本構造の確保
        normalized = {
            'name': data.get('name', '未命名テーマ'),
            'display_name': data.get('display_name',
                                   data.get('name', '未命名テーマ')),
            'version': data.get('version', '1.0.0'),
            'description': data.get('description', ''),
            'author': data.get('author', ''),
            'qt_theme_name': data.get('qt_theme_name', ''),
            'style_sheet': data.get('style_sheet', ''),
            'colors': {},
            'fonts': {},
            'sizes': {},
            'properties': {},
            'metadata': {}
        }
        
        # color_scheme形式の色情報を正規化
        if 'color_scheme' in data:
            normalized['colors'] = self.normalize_color_scheme(
                data['color_scheme'])
        elif 'colors' in data:
            normalized['colors'] = self.normalize_colors(data['colors'])
        elif 'palette' in data:  # 別名での色情報
            normalized['colors'] = self.normalize_colors(data['palette'])
            
        # フォント情報の正規化
        if 'fonts' in data:
            normalized['fonts'] = self.normalize_fonts(data['fonts'])
            
        # サイズ情報の正規化
        if 'sizes' in data:
            normalized['sizes'] = self.normalize_sizes(data['sizes'])
            
        # アクセシビリティ機能
        if 'accessibility_features' in data:
            normalized['accessibility_features'] = \
                data['accessibility_features']
            
        # パフォーマンス設定
        if 'performance_settings' in data:
            normalized['performance_settings'] = \
                data['performance_settings']
            
        # その他のプロパティ
        if 'properties' in data:
            normalized['properties'] = data['properties']
            
        # カスタムプロパティ
        if 'custom_properties' in data:
            normalized['custom_properties'] = \
                data['custom_properties']
            
        # メタデータ
        if 'metadata' in data:
            normalized['metadata'] = data['metadata']
            
        # 日時情報
        if 'created_date' in data:
            normalized['created_at'] = data['created_date']
        if 'last_modified' in data:
            normalized['updated_at'] = data['last_modified']
            
        return normalized
        
    def normalize_color_scheme(self, color_scheme: Dict[str, Any]) -> \
            Dict[str, str]:
        """
        color_scheme形式の色情報を正規化
        
        Args:
            color_scheme: color_scheme形式の色情報
            
        Returns:
            正規化された色情報
        """
        normalized = {}
        
        # color_schemeの標準的な色名マッピング
        color_mappings = {
            'background': ['background', 'bg', 'base'],
            'foreground': ['foreground', 'fg', 'text'],
            'primary': ['primary', 'main', 'accent'],
            'secondary': ['secondary', 'alternate'],
            'accent': ['accent', 'highlight'],
            'success': ['success', 'ok', 'green'],
            'warning': ['warning', 'caution', 'yellow'],
            'error': ['error', 'danger', 'red'],
            'info': ['info', 'information', 'blue'],
            'border': ['border', 'outline'],
            'hover': ['hover', 'hover_state'],
            'selected': ['selected', 'selection', 'active'],
            'disabled': ['disabled', 'inactive']
        }
        
        # 色の正規化
        for standard_name, possible_names in color_mappings.items():
            for name in possible_names:
                if name in color_scheme:
                    color_value = color_scheme[name]
                    normalized[standard_name] = \
                        self.normalize_color_value(color_value)
                    break
                    
        # その他の色もそのまま追加
        for name, value in color_scheme.items():
            if name not in [n for names in color_mappings.values()
                           for n in names]:
                normalized[name] = self.normalize_color_value(value)
                
        return normalized
        
    def normalize_colors(self, colors: Dict[str, Any]) -> Dict[str, str]:
        """
        色情報の正規化
        
        Args:
            colors: 元の色情報
            
        Returns:
            正規化された色情報
        """
        normalized = {}
        
        # 標準的な色名のマッピング
        color_mappings = {
            'primary': ['primary', 'main', 'accent'],
            'secondary': ['secondary', 'alternate'],
            'background': ['background', 'bg', 'base'],
            'surface': ['surface', 'card', 'panel'],
            'error': ['error', 'danger', 'red'],
            'warning': ['warning', 'caution', 'yellow'],
            'info': ['info', 'information', 'blue'],
            'success': ['success', 'ok', 'green'],
            'text': ['text', 'foreground', 'fg'],
            'text_secondary': ['text_secondary', 'text_muted', 'subtitle']
        }
        
        # 色の正規化
        for standard_name, possible_names in color_mappings.items():
            for name in possible_names:
                if name in colors:
                    color_value = colors[name]
                    normalized[standard_name] = self.normalize_color_value(color_value)
                    break
                    
        # その他の色もそのまま追加
        for name, value in colors.items():
            if name not in [n for names in color_mappings.values() for n in names]:
                normalized[name] = self.normalize_color_value(value)
                
        return normalized
        
    def normalize_color_value(self, color_value: Any) -> str:
        """
        色値の正規化
        
        Args:
            color_value: 元の色値
            
        Returns:
            正規化された色値（16進数形式）
        """
        if isinstance(color_value, str):
            # 16進数形式の確認と正規化
            if color_value.startswith('#'):
                return color_value.lower()
            elif color_value.startswith('0x'):
                return '#' + color_value[2:].lower()
            elif re.match(r'^[0-9a-fA-F]{6}$', color_value):
                return '#' + color_value.lower()
            elif re.match(r'^[0-9a-fA-F]{3}$', color_value):
                # 3桁を6桁に展開
                return '#' + ''.join([c*2 for c in color_value.lower()])
            else:
                # 名前付き色の場合はそのまま返す
                return color_value.lower()
        elif isinstance(color_value, dict):
            # RGB辞書形式の場合
            if all(k in color_value for k in ['r', 'g', 'b']):
                r = int(color_value['r'])
                g = int(color_value['g'])
                b = int(color_value['b'])
                return f'#{r:02x}{g:02x}{b:02x}'
        elif isinstance(color_value, (list, tuple)) and len(color_value) >= 3:
            # RGB配列形式の場合
            r, g, b = int(color_value[0]), int(color_value[1]), int(color_value[2])
            return f'#{r:02x}{g:02x}{b:02x}'
            
        # その他の場合はデフォルト色
        return '#000000'
        
    def normalize_fonts(self, fonts: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        フォント情報の正規化
        
        Args:
            fonts: 元のフォント情報
            
        Returns:
            正規化されたフォント情報
        """
        normalized = {}
        
        for name, font_data in fonts.items():
            if isinstance(font_data, str):
                # フォント名のみの場合
                normalized[name] = {
                    'family': font_data,
                    'size': 12,
                    'weight': 'normal',
                    'style': 'normal'
                }
            elif isinstance(font_data, dict):
                # 詳細フォント情報の場合
                normalized[name] = {
                    'family': font_data.get('family', 'Arial'),
                    'size': font_data.get('size', 12),
                    'weight': font_data.get('weight', 'normal'),
                    'style': font_data.get('style', 'normal')
                }
                
        return normalized
        
    def normalize_sizes(self, sizes: Dict[str, Any]) -> Dict[str, int]:
        """
        サイズ情報の正規化
        
        Args:
            sizes: 元のサイズ情報
            
        Returns:
            正規化されたサイズ情報
        """
        normalized = {}
        
        for name, size_value in sizes.items():
            try:
                # 数値に変換
                if isinstance(size_value, str):
                    # 'px'などの単位を除去
                    size_str = re.sub(r'[^\d.]', '', size_value)
                    normalized[name] = int(float(size_str))
                else:
                    normalized[name] = int(size_value)
            except (ValueError, TypeError):
                # 変換できない場合はデフォルト値
                normalized[name] = 12
                
        return normalized
        
    def parse_qss_content(self, qss_content: str, theme_name: str) -> Dict[str, Any]:
        """
        QSSコンテンツの解析
        
        Args:
            qss_content: QSSファイルの内容
            theme_name: テーマ名
            
        Returns:
            テーマデータ
        """
        theme_data = {
            'name': theme_name,
            'version': '1.0.0',
            'description': f'{theme_name} (QSSからインポート)',
            'colors': {},
            'fonts': {},
            'sizes': {},
            'properties': {'qss_content': qss_content},
            'metadata': {'source_format': 'qss'}
        }
        
        # QSSから色情報を抽出
        colors = self.extract_colors_from_qss(qss_content)
        theme_data['colors'] = colors
        
        # QSSからフォント情報を抽出
        fonts = self.extract_fonts_from_qss(qss_content)
        theme_data['fonts'] = fonts
        
        return theme_data
        
    def extract_colors_from_qss(self, qss_content: str) -> Dict[str, str]:
        """
        QSSから色情報を抽出
        
        Args:
            qss_content: QSSファイルの内容
            
        Returns:
            抽出された色情報
        """
        colors = {}
        
        # 色の正規表現パターン
        color_patterns = [
            r'color\s*:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|\w+)',
            r'background-color\s*:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|\w+)',
            r'border-color\s*:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|\w+)',
            r'selection-background-color\s*:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|\w+)'
        ]
        
        color_index = 0
        for pattern in color_patterns:
            matches = re.findall(pattern, qss_content, re.IGNORECASE)
            for match in matches:
                color_value = self.normalize_color_value(match)
                color_name = f'extracted_color_{color_index}'
                colors[color_name] = color_value
                color_index += 1
                
        # 重複を除去
        unique_colors = {}
        seen_values = set()
        for name, value in colors.items():
            if value not in seen_values:
                unique_colors[name] = value
                seen_values.add(value)
                
        return unique_colors
        
    def extract_fonts_from_qss(self, qss_content: str) -> Dict[str, Dict[str, Any]]:
        """
        QSSからフォント情報を抽出
        
        Args:
            qss_content: QSSファイルの内容
            
        Returns:
            抽出されたフォント情報
        """
        fonts = {}
        
        # フォントの正規表現パターン
        font_patterns = [
            r'font-family\s*:\s*([^;]+)',
            r'font-size\s*:\s*(\d+)px',
            r'font-weight\s*:\s*(\w+)',
            r'font-style\s*:\s*(\w+)'
        ]
        
        font_families = re.findall(font_patterns[0], qss_content, re.IGNORECASE)
        font_sizes = re.findall(font_patterns[1], qss_content, re.IGNORECASE)
        font_weights = re.findall(font_patterns[2], qss_content, re.IGNORECASE)
        font_styles = re.findall(font_patterns[3], qss_content, re.IGNORECASE)
        
        # 抽出されたフォント情報を組み合わせ
        if font_families:
            fonts['primary'] = {
                'family': font_families[0].strip().strip('"\''),
                'size': int(font_sizes[0]) if font_sizes else 12,
                'weight': font_weights[0] if font_weights else 'normal',
                'style': font_styles[0] if font_styles else 'normal'
            }
            
        return fonts
        
    def parse_css_content(self, css_content: str, theme_name: str) -> Dict[str, Any]:
        """
        CSSコンテンツの解析
        
        Args:
            css_content: CSSファイルの内容
            theme_name: テーマ名
            
        Returns:
            テーマデータ
        """
        theme_data = {
            'name': theme_name,
            'version': '1.0.0',
            'description': f'{theme_name} (CSSからインポート)',
            'colors': {},
            'fonts': {},
            'sizes': {},
            'properties': {'css_content': css_content},
            'metadata': {'source_format': 'css'}
        }
        
        # CSSから色情報を抽出（QSSと同様の処理）
        colors = self.extract_colors_from_css(css_content)
        theme_data['colors'] = colors
        
        # CSSからフォント情報を抽出
        fonts = self.extract_fonts_from_css(css_content)
        theme_data['fonts'] = fonts
        
        return theme_data
        
    def extract_colors_from_css(self, css_content: str) -> Dict[str, str]:
        """
        CSSから色情報を抽出
        
        Args:
            css_content: CSSファイルの内容
            
        Returns:
            抽出された色情報
        """
        # CSS変数の抽出
        css_vars = re.findall(r'--[\w-]+\s*:\s*(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|\w+)', css_content)
        
        colors = {}
        for i, color_value in enumerate(css_vars):
            color_name = f'css_var_{i}'
            colors[color_name] = self.normalize_color_value(color_value)
            
        # 通常のCSS色プロパティも抽出
        normal_colors = self.extract_colors_from_qss(css_content)  # QSSと同じ処理
        colors.update(normal_colors)
        
        return colors
        
    def extract_fonts_from_css(self, css_content: str) -> Dict[str, Dict[str, Any]]:
        """
        CSSからフォント情報を抽出
        
        Args:
            css_content: CSSファイルの内容
            
        Returns:
            抽出されたフォント情報
        """
        # QSSと同じ処理
        return self.extract_fonts_from_qss(css_content)
        
    def add_import_metadata(self, theme_data: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """
        インポートメタデータの追加
        
        Args:
            theme_data: テーマデータ
            file_path: インポート元ファイルパス
            
        Returns:
            メタデータが追加されたテーマデータ
        """
        if 'metadata' not in theme_data:
            theme_data['metadata'] = {}
            
        theme_data['metadata'].update({
            'imported_from': str(file_path),
            'imported_at': datetime.now().isoformat(),
            'original_format': file_path.suffix.lower(),
            'file_size': file_path.stat().st_size if file_path.exists() else 0
        })
        
        # 作成日時が設定されていない場合は現在時刻を設定
        if 'created_at' not in theme_data:
            theme_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        return theme_data
        
    def validate_imported_theme(self, theme_data: Dict[str, Any]) -> List[str]:
        """
        インポートされたテーマの検証
        
        Args:
            theme_data: テーマデータ
            
        Returns:
            検証エラーのリスト
        """
        errors = []
        
        # 必須フィールドの確認
        required_fields = ['name', 'version']
        for field in required_fields:
            if field not in theme_data or not theme_data[field]:
                errors.append(f"必須フィールド '{field}' が不足しています")
                
        # 色情報の確認
        if 'colors' in theme_data:
            colors = theme_data['colors']
            if not isinstance(colors, dict):
                errors.append("色情報は辞書形式である必要があります")
            else:
                for color_name, color_value in colors.items():
                    if not self.is_valid_color(color_value):
                        errors.append(f"無効な色値です: {color_name} = {color_value}")
                        
        return errors
        
    def is_valid_color(self, color_value: str) -> bool:
        """
        色値の妥当性確認
        
        Args:
            color_value: 色値
            
        Returns:
            妥当性
        """
        if not isinstance(color_value, str):
            return False
            
        # 16進数形式の確認
        if re.match(r'^#[0-9a-fA-F]{6}$', color_value):
            return True
        if re.match(r'^#[0-9a-fA-F]{3}$', color_value):
            return True
            
        # 名前付き色の確認（基本的な色名）
        named_colors = [
            'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
            'gray', 'grey', 'darkred', 'darkgreen', 'darkblue', 'darkyellow',
            'darkcyan', 'darkmagenta', 'darkgray', 'darkgrey', 'lightgray', 'lightgrey'
        ]
        
        return color_value.lower() in named_colors
        
    def get_supported_formats(self) -> List[str]:
        """
        サポートされるファイル形式の取得
        
        Returns:
            サポートされるファイル拡張子のリスト
        """
        return list(self.supported_formats.keys())
        
    def get_format_description(self, format_ext: str) -> str:
        """
        ファイル形式の説明取得
        
        Args:
            format_ext: ファイル拡張子
            
        Returns:
            形式の説明
        """
        descriptions = {
            '.json': 'JSON形式のテーマファイル（推奨）',
            '.qss': 'Qt Style Sheet形式のファイル',
            '.css': 'Cascading Style Sheet形式のファイル'
        }
        
        return descriptions.get(format_ext, '不明な形式')