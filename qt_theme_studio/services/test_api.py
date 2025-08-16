"""
Qt-Theme-Studio プログラマティックテストAPI

このモジュールは、テーマの読み込み、適用、エクスポート機能の
プログラマティックテスト用APIを提供します。
ヘッドレスモードでの動作をサポートし、CI/CD環境での自動テストを可能にします。
"""

import json
import sys
import tempfile
import time
from typing import Any, Dict, List

from ..exceptions import ThemeStudioException
from ..services.export_service import ExportService
from ..services.theme_service import ThemeService
from ..services.validation_service import ValidationService


class TestAPIException(ThemeStudioException):
    """テストAPI例外"""


class HeadlessTestRunner:
    """ヘッドレステストランナー
    
    GUI環境なしでテーマ機能をテストするためのランナーです。
    """
    
    def __init__(self, enable_logging: bool = True):
        """HeadlessTestRunnerを初期化する
        
        Args:
            enable_logging (bool): ログ出力を有効にするか
        """
        self.enable_logging = enable_logging
        if enable_logging:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logging.getLogger('null')
            self.logger.addHandler(logging.NullHandler())
        
        # サービスの初期化
        self.theme_service = ThemeService()
        self.export_service = ExportService()
        self.validation_service = ValidationService()
        
        # テスト結果の保存
        self.test_results: List[Dict[str, Any]] = []
        
        self.logger.info("ヘッドレステストランナーを初期化しました")
    
    def run_theme_loading_test(self, theme_path: str) -> Dict[str, Any]:
        """テーマ読み込みテストを実行する
        
        Args:
            theme_path (str): テーマファイルパス
            
        Returns:
            Dict[str, Any]: テスト結果
        """
        test_name = "theme_loading_test"
        self.logger.info(f"テーマ読み込みテストを開始します: {theme_path}")
        
        result = {
            'test_name': test_name,
            'theme_path': theme_path,
            'start_time': time.time(),
            'success': False,
            'error_message': None,
            'theme_data': None,
            'load_time': 0.0,
            'validation_errors': []
        }
        
        try:
            # テーマファイルの存在確認
            if not os.path.exists(theme_path):
                raise TestAPIException(f"テーマファイルが存在しません: {theme_path}")
            
            # テーマ読み込み
            start_load = time.time()
            theme_data = self.theme_service.load_theme_from_file(theme_path)
            load_time = time.time() - start_load
            
            # 基本検証
            validation_errors = self.validation_service.validate_theme_structure(theme_data)
            
            result.update({
                'success': True,
                'theme_data': theme_data,
                'load_time': load_time,
                'validation_errors': validation_errors
            })
            
            self.logger.info("テーマ読み込み成功: {theme_path} ({load_time:.3f}秒)")
            
        except Exception as e:
            result['error_message'] = str(e)
            self.logger.error("テーマ読み込み失敗: {theme_path} - {str(e)}")
        
        finally:
            result['end_time'] = time.time()
            result['total_time'] = result['end_time'] - result['start_time']
            self.test_results.append(result)
        
        return result
    
    def run_theme_export_test(self, theme_data: Dict[str, Any], 
                            export_formats: List[str] = None) -> Dict[str, Any]:
        """テーマエクスポートテストを実行する
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            export_formats (List[str], optional): エクスポート形式リスト
            
        Returns:
            Dict[str, Any]: テスト結果
        """
        test_name = "theme_export_test"
        export_formats = export_formats or ['json', 'qss', 'css']
        
        self.logger.info(f"テーマエクスポートテストを開始します: {export_formats}")
        
        result = {
            'test_name': test_name,
            'start_time': time.time(),
            'success': False,
            'error_message': None,
            'export_results': {},
            'total_export_time': 0.0
        }
        
        try:
            export_start = time.time()
            
            for format_name in export_formats:
                format_result = {
                    'success': False,
                    'output_size': 0,
                    'export_time': 0.0,
                    'error_message': None
                }
                
                try:
                    format_start = time.time()
                    
                    if format_name.lower() == 'json':
                        exported_data = self.export_service.export_theme(theme_data, 'json')
                    elif format_name.lower() == 'qss':
                        exported_data = self.export_service.export_theme(theme_data, 'qss')
                    elif format_name.lower() == 'css':
                        exported_data = self.export_service.export_theme(theme_data, 'css')
                    else:
                        raise TestAPIException(f"サポートされていないエクスポート形式: {format_name}")
                    
                    format_time = time.time() - format_start
                    
                    format_result.update({
                        'success': True,
                        'output_size': len(exported_data.encode('utf-8')),
                        'export_time': format_time
                    })
                    
                    self.logger.debug("{format_name}エクスポート成功 ({format_time:.3f}秒)")
                    
                except Exception as e:
                    format_result['error_message'] = str(e)
                    self.logger.warning("{format_name}エクスポート失敗: {str(e)}")
                
                result['export_results'][format_name] = format_result
            
            total_export_time = time.time() - export_start
            result['total_export_time'] = total_export_time
            
            # 全体の成功判定
            successful_exports = sum(1 for r in result['export_results'].values() if r['success'])
            result['success'] = successful_exports > 0
            
            if result['success']:
                self.logger.info("エクスポートテスト完了: {successful_exports}/{len(export_formats)} 成功")
            else:
                result['error_message'] = "すべてのエクスポート形式で失敗しました"
                self.logger.error("すべてのエクスポート形式で失敗しました")
            
        except Exception as e:
            result['error_message'] = str(e)
            self.logger.error("エクスポートテスト中にエラーが発生しました: {str(e)}")
        
        finally:
            result['end_time'] = time.time()
            result['total_time'] = result['end_time'] - result['start_time']
            self.test_results.append(result)
        
        return result
    
    def run_theme_validation_test(self, theme_data: Dict[str, Any], 
                                wcag_level: str = "AA") -> Dict[str, Any]:
        """テーマ検証テストを実行する
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            wcag_level (str): WCAGレベル
            
        Returns:
            Dict[str, Any]: テスト結果
        """
        test_name = "theme_validation_test"
        self.logger.info(f"テーマ検証テストを開始します: WCAG {wcag_level}")
        
        result = {
            'test_name': test_name,
            'start_time': time.time(),
            'success': False,
            'error_message': None,
            'structure_validation': {
                'success': False,
                'errors': [],
                'validation_time': 0.0
            },
            'accessibility_validation': {
                'success': False,
                'score': 0.0,
                'violations': [],
                'validation_time': 0.0
            }
        }
        
        try:
            # 構造検証
            structure_start = time.time()
            structure_errors = self.validation_service.validate_theme_structure(theme_data)
            structure_time = time.time() - structure_start
            
            result['structure_validation'].update({
                'success': len(structure_errors) == 0,
                'errors': structure_errors,
                'validation_time': structure_time
            })
            
            # アクセシビリティ検証
            accessibility_start = time.time()
            accessibility_report = self.validation_service.validate_wcag_compliance(theme_data, wcag_level)
            accessibility_time = time.time() - accessibility_start
            
            result['accessibility_validation'].update({
                'success': accessibility_report.is_compliant(),
                'score': accessibility_report.score,
                'violations': [v['description'] for v in accessibility_report.violations],
                'validation_time': accessibility_time
            })
            
            # 全体の成功判定
            result['success'] = (result['structure_validation']['success'] and 
                               result['accessibility_validation']['success'])
            
            if result['success']:
                self.logger.info("テーマ検証テスト成功")
            else:
                error_parts = []
                if not result['structure_validation']['success']:
                    error_parts.append("構造エラー: {len(structure_errors)}個")
                if not result['accessibility_validation']['success']:
                    error_parts.append("アクセシビリティ違反: {len(accessibility_report.violations)}個")
                result['error_message'] = "; ".join(error_parts)
                self.logger.warning("テーマ検証テスト失敗: {result['error_message']}")
            
        except Exception as e:
            result['error_message'] = str(e)
            self.logger.error("検証テスト中にエラーが発生しました: {str(e)}")
        
        finally:
            result['end_time'] = time.time()
            result['total_time'] = result['end_time'] - result['start_time']
            self.test_results.append(result)
        
        return result
    
    def run_roundtrip_test(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """ラウンドトリップテストを実行する
        
        テーマデータをエクスポートして再インポートし、
        データの整合性を確認します。
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            
        Returns:
            Dict[str, Any]: テスト結果
        """
        test_name = "roundtrip_test"
        self.logger.info("ラウンドトリップテストを開始します")
        
        result = {
            'test_name': test_name,
            'start_time': time.time(),
            'success': False,
            'error_message': None,
            'format_results': {}
        }
        
        try:
            formats_to_test = ['json']  # JSONのみラウンドトリップ可能
            
            for format_name in formats_to_test:
                format_result = {
                    'export_success': False,
                    'import_success': False,
                    'data_integrity': False,
                    'differences': []
                }
                
                try:
                    # エクスポート
                    if format_name == 'json':
                        exported_data = self.export_service.export_theme(theme_data, 'json')
                        format_result['export_success'] = True
                        
                        # 一時ファイルに保存
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                            temp_file.write(exported_data)
                            temp_path = temp_file.name
                        
                        try:
                            # インポート
                            imported_data = self.theme_service.load_theme_from_file(temp_path)
                            format_result['import_success'] = True
                            
                            # データ整合性チェック
                            differences = self._compare_theme_data(theme_data, imported_data)
                            format_result['differences'] = differences
                            format_result['data_integrity'] = len(differences) == 0
                            
                        finally:
                            # 一時ファイル削除
                            os.unlink(temp_path)
                    
                except Exception as e:
                    format_result['error_message'] = str(e)
                    self.logger.warning("{format_name}ラウンドトリップ失敗: {str(e)}")
                
                result['format_results'][format_name] = format_result
            
            # 全体の成功判定
            successful_roundtrips = sum(1 for r in result['format_results'].values() 
                                      if r.get('data_integrity', False))
            result['success'] = successful_roundtrips > 0
            
            if result['success']:
                self.logger.info("ラウンドトリップテスト成功: {successful_roundtrips}形式")
            else:
                result['error_message'] = "すべての形式でラウンドトリップに失敗しました"
                self.logger.error("ラウンドトリップテスト失敗")
            
        except Exception as e:
            result['error_message'] = str(e)
            self.logger.error("ラウンドトリップテスト中にエラーが発生しました: {str(e)}")
        
        finally:
            result['end_time'] = time.time()
            result['total_time'] = result['end_time'] - result['start_time']
            self.test_results.append(result)
        
        return result
    
    def _compare_theme_data(self, original: Dict[str, Any], 
                          imported: Dict[str, Any]) -> List[str]:
        """テーマデータを比較して差分を検出する
        
        Args:
            original (Dict[str, Any]): 元のテーマデータ
            imported (Dict[str, Any]): インポートされたテーマデータ
            
        Returns:
            List[str]: 差分のリスト
        """
        differences = []
        
        # 基本フィールドの比較
        basic_fields = ['name', 'version']
        for field in basic_fields:
            if original.get(field) != imported.get(field):
                differences.append(f"{field}: '{original.get(field)}' != '{imported.get(field)}'")
        
        # 色データの比較
        original_colors = original.get('colors', {})
        imported_colors = imported.get('colors', {})
        
        for color_name in set(original_colors.keys()) | set(imported_colors.keys()):
            if color_name not in original_colors:
                differences.append("色が追加されました: {color_name}")
            elif color_name not in imported_colors:
                differences.append("色が削除されました: {color_name}")
            elif original_colors[color_name] != imported_colors[color_name]:
                differences.append(f"色が変更されました: {color_name} '{original_colors[color_name]}' != '{imported_colors[color_name]}'")
        
        # フォントデータの比較
        original_fonts = original.get('fonts', {})
        imported_fonts = imported.get('fonts', {})
        
        for font_name in set(original_fonts.keys()) | set(imported_fonts.keys()):
            if font_name not in original_fonts:
                differences.append("フォントが追加されました: {font_name}")
            elif font_name not in imported_fonts:
                differences.append("フォントが削除されました: {font_name}")
            elif original_fonts[font_name] != imported_fonts[font_name]:
                differences.append("フォントが変更されました: {font_name}")
        
        return differences
    
    def run_performance_test(self, theme_data: Dict[str, Any], 
                           iterations: int = 10) -> Dict[str, Any]:
        """パフォーマンステストを実行する
        
        Args:
            theme_data (Dict[str, Any]): テーマデータ
            iterations (int): 反復回数
            
        Returns:
            Dict[str, Any]: テスト結果
        """
        test_name = "performance_test"
        self.logger.info(f"パフォーマンステストを開始します: {iterations}回反復")
        
        result = {
            'test_name': test_name,
            'start_time': time.time(),
            'success': False,
            'error_message': None,
            'iterations': iterations,
            'validation_times': [],
            'export_times': {
                'json': [],
                'qss': [],
                'css': []
            },
            'statistics': {}
        }
        
        try:
            # 検証パフォーマンステスト
            for i in range(iterations):
                start_time = time.time()
                self.validation_service.validate_theme_structure(theme_data)
                validation_time = time.time() - start_time
                result['validation_times'].append(validation_time)
            
            # エクスポートパフォーマンステスト
            for format_name in ['json', 'qss', 'css']:
                for i in range(iterations):
                    try:
                        start_time = time.time()
                        
                        if format_name == 'json':
                            self.export_service.export_theme(theme_data, 'json')
                        elif format_name == 'qss':
                            self.export_service.export_theme(theme_data, 'qss')
                        elif format_name == 'css':
                            self.export_service.export_theme(theme_data, 'css')
                        
                        export_time = time.time() - start_time
                        result['export_times'][format_name].append(export_time)
                        
                    except Exception as e:
                        self.logger.warning(f"{format_name}エクスポートエラー (反復{i+1}): {str(e)}")
            
            # 統計計算
            result['statistics'] = {
                'validation': self._calculate_statistics(result['validation_times']),
                'export': {
                    format_name: self._calculate_statistics(times)
                    for format_name, times in result['export_times'].items()
                    if times
                }
            }
            
            result['success'] = True
            self.logger.info("パフォーマンステスト完了")
            
        except Exception as e:
            result['error_message'] = str(e)
            self.logger.error("パフォーマンステスト中にエラーが発生しました: {str(e)}")
        
        finally:
            result['end_time'] = time.time()
            result['total_time'] = result['end_time'] - result['start_time']
            self.test_results.append(result)
        
        return result
    
    def _calculate_statistics(self, times: List[float]) -> Dict[str, float]:
        """時間統計を計算する
        
        Args:
            times (List[float]): 時間のリスト
            
        Returns:
            Dict[str, float]: 統計データ
        """
        if not times:
            return {'min': 0.0, 'max': 0.0, 'avg': 0.0, 'median': 0.0}
        
        sorted_times = sorted(times)
        n = len(sorted_times)
        
        return {
            'min': min(sorted_times),
            'max': max(sorted_times),
            'avg': sum(sorted_times) / n,
            'median': sorted_times[n // 2] if n % 2 == 1 else (sorted_times[n // 2 - 1] + sorted_times[n // 2]) / 2
        }
    
    def run_comprehensive_test_suite(self, theme_path: str = None, 
                                   theme_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """包括的テストスイートを実行する
        
        Args:
            theme_path (str, optional): テーマファイルパス
            theme_data (Dict[str, Any], optional): テーマデータ
            
        Returns:
            Dict[str, Any]: 全体のテスト結果
        """
        self.logger.info("包括的テストスイートを開始します")
        
        suite_result = {
            'suite_name': 'comprehensive_test_suite',
            'start_time': time.time(),
            'success': False,
            'tests_run': 0,
            'tests_passed': 0,
            'individual_results': [],
            'summary': {}
        }
        
        try:
            # テーマデータの準備
            if theme_data is None and theme_path is not None:
                load_result = self.run_theme_loading_test(theme_path)
                suite_result['individual_results'].append(load_result)
                suite_result['tests_run'] += 1
                
                if load_result['success']:
                    theme_data = load_result['theme_data']
                    suite_result['tests_passed'] += 1
                else:
                    suite_result['error_message'] = "テーマ読み込みに失敗したため、テストスイートを中断します"
                    return suite_result
            
            if theme_data is None:
                suite_result['error_message'] = "テーマデータまたはテーマパスが必要です"
                return suite_result
            
            # 各テストの実行
            test_methods = [
                (self.run_theme_validation_test, [theme_data]),
                (self.run_theme_export_test, [theme_data]),
                (self.run_roundtrip_test, [theme_data]),
                (self.run_performance_test, [theme_data, 5])  # 5回反復
            ]
            
            for test_method, args in test_methods:
                try:
                    test_result = test_method(*args)
                    suite_result['individual_results'].append(test_result)
                    suite_result['tests_run'] += 1
                    
                    if test_result['success']:
                        suite_result['tests_passed'] += 1
                        
                except Exception as e:
                    self.logger.error(f"テスト実行エラー: {str(e)}")
                    suite_result['individual_results'].append({
                        'test_name': 'unknown',
                        'success': False,
                        'error_message': str(e)
                    })
                    suite_result['tests_run'] += 1
            
            # サマリー作成
            success_rate = (suite_result['tests_passed'] / suite_result['tests_run']) * 100.0 if suite_result['tests_run'] > 0 else 0.0
            suite_result['success'] = success_rate >= 80.0  # 80%以上で成功とみなす
            
            suite_result['summary'] = {
                'success_rate': success_rate,
                'total_tests': suite_result['tests_run'],
                'passed_tests': suite_result['tests_passed'],
                'failed_tests': suite_result['tests_run'] - suite_result['tests_passed']
            }
            
            self.logger.info("テストスイート完了: {suite_result['tests_passed']}/{suite_result['tests_run']} 成功 ({success_rate:.1f}%)")
            
        except Exception as e:
            suite_result['error_message'] = str(e)
            self.logger.error("テストスイート実行中にエラーが発生しました: {str(e)}")
        
        finally:
            suite_result['end_time'] = time.time()
            suite_result['total_time'] = suite_result['end_time'] - suite_result['start_time']
        
        return suite_result
    
    def get_test_summary(self) -> Dict[str, Any]:
        """テスト結果のサマリーを取得する
        
        Returns:
            Dict[str, Any]: テストサマリー
        """
        if not self.test_results:
            return {
                'total_tests': 0,
                'successful_tests': 0,
                'failed_tests': 0,
                'success_rate': 0.0,
                'total_time': 0.0
            }
        
        successful_tests = sum(1 for result in self.test_results if result.get('success', False))
        total_time = sum(result.get('total_time', 0.0) for result in self.test_results)
        
        return {
            'total_tests': len(self.test_results),
            'successful_tests': successful_tests,
            'failed_tests': len(self.test_results) - successful_tests,
            'success_rate': (successful_tests / len(self.test_results)) * 100.0,
            'total_time': total_time
        }
    
    def export_test_results(self, output_path: str) -> None:
        """テスト結果をファイルにエクスポートする
        
        Args:
            output_path (str): 出力ファイルパス
        """
        test_report = {
            'summary': self.get_test_summary(),
            'individual_results': self.test_results,
            'export_time': time.time()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(test_report, f, ensure_ascii=False, indent=2)
        
        self.logger.info("テスト結果をエクスポートしました: {output_path}")


class CommandLineTestRunner:
    """コマンドライン用テストランナー
    
    CI/CD環境でのコマンドライン実行をサポートします。
    """
    
    def __init__(self):
        """CommandLineTestRunnerを初期化する"""
        self.headless_runner = HeadlessTestRunner()
        self.logger = logging.getLogger(__name__)
    
    def run_from_command_line(self, args: List[str]) -> int:
        """コマンドライン引数からテストを実行する
        
        Args:
            args (List[str]): コマンドライン引数
            
        Returns:
            int: 終了コード（0: 成功, 1: 失敗）
        """
        try:
            if len(args) < 2:
                print("使用方法: python -m qt_theme_studio.services.test_api <theme_file> [output_file]")
                return 1
            
            theme_file = args[1]
            output_file = args[2] if len(args) > 2 else "test_results_{int(time.time())}.json"
            
            print("テーマファイル: {theme_file}")
            print("結果出力先: {output_file}")
            print()
            
            # 包括的テストスイート実行
            result = self.headless_runner.run_comprehensive_test_suite(theme_path=theme_file)
            
            # 結果表示
            print("=" * 60)
            print("テスト結果サマリー")
            print("=" * 60)
            print("実行テスト数: {result['tests_run']}")
            print("成功テスト数: {result['tests_passed']}")
            print("失敗テスト数: {result['tests_run'] - result['tests_passed']}")
            print("成功率: {result['summary'].get('success_rate', 0.0):.1f}%")
            print("実行時間: {result['total_time']:.3f}秒")
            print()
            
            # 個別テスト結果
            for test_result in result['individual_results']:
                "✓" if test_result['success'] else "✗"
                print("{status} {test_result['test_name']}")
                if not test_result['success'] and test_result.get('error_message'):
                    print("  エラー: {test_result['error_message']}")
            
            # 結果ファイル出力
            self.headless_runner.export_test_results(output_file)
            print("\n詳細結果を {output_file} に出力しました")
            
            # 終了コード決定
            return 0 if result['success'] else 1
            
        except Exception:
            print("テスト実行中にエラーが発生しました: {str(e)}")
            return 1


if __name__ == "__main__":
    # コマンドライン実行サポート
    runner = CommandLineTestRunner()
    exit_code = runner.run_from_command_line(sys.argv)
    sys.exit(exit_code)