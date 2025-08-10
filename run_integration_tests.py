#!/usr/bin/env python3
"""
統合テスト実行スクリプト

Qt-Theme-Studioの統合テストとエンドツーエンドテストを実行します。
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import json
import time
from datetime import datetime


def setup_test_environment():
    """テスト環境のセットアップ"""
    print("テスト環境をセットアップ中...")
    
    # 必要なディレクトリの作成
    test_dirs = [
        'tests/fixtures',
        'tests/temp',
        'tests/reports'
    ]
    
    for test_dir in test_dirs:
        Path(test_dir).mkdir(parents=True, exist_ok=True)
    
    # テスト用の設定ファイル作成
    test_config = {
        'test_mode': True,
        'log_level': 'DEBUG',
        'temp_dir': 'tests/temp',
        'fixtures_dir': 'tests/fixtures'
    }
    
    config_file = Path('tests/test_config.json')
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2, ensure_ascii=False)
    
    print("✓ テスト環境のセットアップが完了しました")


def run_pytest_command(test_files, options=None):
    """pytestコマンドの実行"""
    cmd = ['python', '-m', 'pytest']
    
    # テストファイルを追加
    if isinstance(test_files, str):
        cmd.append(test_files)
    else:
        cmd.extend(test_files)
    
    # オプションを追加
    if options:
        cmd.extend(options)
    
    print(f"実行中: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        return result
    except Exception as e:
        print(f"テスト実行エラー: {e}")
        return None


def run_complete_workflow_tests():
    """完全ワークフローテストの実行"""
    print("\n=== 完全ワークフローテスト実行 ===")
    
    test_file = 'tests/test_complete_workflow.py'
    options = [
        '-v',
        '--tb=short',
        '--durations=10',
        f'--junitxml=tests/reports/workflow_tests.xml'
    ]
    
    result = run_pytest_command(test_file, options)
    
    if result and result.returncode == 0:
        print("✓ 完全ワークフローテストが成功しました")
        return True
    else:
        print("✗ 完全ワークフローテストが失敗しました")
        if result:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        return False


def run_accessibility_tests():
    """アクセシビリティ機能テストの実行"""
    print("\n=== アクセシビリティ機能テスト実行 ===")
    
    test_file = 'tests/test_accessibility_features.py'
    options = [
        '-v',
        '--tb=short',
        '--durations=10',
        f'--junitxml=tests/reports/accessibility_tests.xml'
    ]
    
    result = run_pytest_command(test_file, options)
    
    if result and result.returncode == 0:
        print("✓ アクセシビリティ機能テストが成功しました")
        return True
    else:
        print("✗ アクセシビリティ機能テストが失敗しました")
        if result:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        return False


def run_integration_suite():
    """統合テストスイートの実行"""
    print("\n=== 統合テストスイート実行 ===")
    
    test_file = 'tests/test_integration_suite.py'
    options = [
        '-v',
        '--tb=short',
        '--durations=10',
        f'--junitxml=tests/reports/integration_suite.xml'
    ]
    
    result = run_pytest_command(test_file, options)
    
    if result and result.returncode == 0:
        print("✓ 統合テストスイートが成功しました")
        return True
    else:
        print("✗ 統合テストスイートが失敗しました")
        if result:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        return False


def run_all_integration_tests():
    """すべての統合テストの実行"""
    print("\n=== すべての統合テスト実行 ===")
    
    test_files = [
        'tests/test_complete_workflow.py',
        'tests/test_accessibility_features.py',
        'tests/test_config_integration.py',
        'tests/test_preview_integration.py',
        'tests/test_integration_suite.py'
    ]
    
    options = [
        '-v',
        '--tb=short',
        '--durations=20',
        '--cov=qt_theme_studio',
        '--cov-report=html:tests/reports/coverage',
        '--cov-report=xml:tests/reports/coverage.xml',
        f'--junitxml=tests/reports/all_integration_tests.xml'
    ]
    
    result = run_pytest_command(test_files, options)
    
    if result and result.returncode == 0:
        print("✓ すべての統合テストが成功しました")
        return True
    else:
        print("✗ 一部の統合テストが失敗しました")
        if result:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        return False


def run_performance_tests():
    """パフォーマンステストの実行"""
    print("\n=== パフォーマンステスト実行 ===")
    
    # パフォーマンステスト用のマーカーを使用
    options = [
        '-v',
        '-m', 'performance',
        '--tb=short',
        '--durations=10',
        f'--junitxml=tests/reports/performance_tests.xml'
    ]
    
    result = run_pytest_command('tests/', options)
    
    if result and result.returncode == 0:
        print("✓ パフォーマンステストが成功しました")
        return True
    else:
        print("✗ パフォーマンステストが失敗しました")
        if result:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        return False


def generate_test_report(test_results):
    """テストレポートの生成"""
    print("\n=== テストレポート生成 ===")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_results': test_results,
        'summary': {
            'total_tests': len(test_results),
            'passed_tests': sum(1 for result in test_results.values() if result),
            'failed_tests': sum(1 for result in test_results.values() if not result)
        }
    }
    
    # 成功率の計算
    if report['summary']['total_tests'] > 0:
        success_rate = (report['summary']['passed_tests'] / report['summary']['total_tests']) * 100
        report['summary']['success_rate'] = f"{success_rate:.1f}%"
    else:
        report['summary']['success_rate'] = "0.0%"
    
    # レポートファイルの保存
    report_file = Path('tests/reports/integration_test_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # コンソール出力
    print(f"総テスト数: {report['summary']['total_tests']}")
    print(f"成功: {report['summary']['passed_tests']}")
    print(f"失敗: {report['summary']['failed_tests']}")
    print(f"成功率: {report['summary']['success_rate']}")
    
    # 詳細結果
    print("\n詳細結果:")
    for test_name, result in test_results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")
    
    print(f"\n詳細レポート: {report_file}")
    
    return report


def cleanup_test_environment():
    """テスト環境のクリーンアップ"""
    print("\nテスト環境をクリーンアップ中...")
    
    # 一時ファイルの削除
    temp_dir = Path('tests/temp')
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        temp_dir.mkdir(exist_ok=True)
    
    # テスト設定ファイルの削除
    config_file = Path('tests/test_config.json')
    if config_file.exists():
        config_file.unlink()
    
    print("✓ テスト環境のクリーンアップが完了しました")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Qt-Theme-Studio統合テスト実行スクリプト')
    parser.add_argument('--workflow', action='store_true', help='完全ワークフローテストのみ実行')
    parser.add_argument('--accessibility', action='store_true', help='アクセシビリティテストのみ実行')
    parser.add_argument('--suite', action='store_true', help='統合テストスイートのみ実行')
    parser.add_argument('--performance', action='store_true', help='パフォーマンステストのみ実行')
    parser.add_argument('--all', action='store_true', help='すべてのテストを実行（デフォルト）')
    parser.add_argument('--no-cleanup', action='store_true', help='テスト後のクリーンアップをスキップ')
    
    args = parser.parse_args()
    
    # デフォルトはすべてのテストを実行
    if not any([args.workflow, args.accessibility, args.suite, args.performance]):
        args.all = True
    
    print("Qt-Theme-Studio 統合テスト実行スクリプト")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # テスト環境のセットアップ
        setup_test_environment()
        
        # テスト結果を記録
        test_results = {}
        
        # 各テストの実行
        if args.workflow or args.all:
            test_results['complete_workflow'] = run_complete_workflow_tests()
        
        if args.accessibility or args.all:
            test_results['accessibility_features'] = run_accessibility_tests()
        
        if args.suite or args.all:
            test_results['integration_suite'] = run_integration_suite()
        
        if args.performance or args.all:
            test_results['performance_tests'] = run_performance_tests()
        
        if args.all:
            test_results['all_integration'] = run_all_integration_tests()
        
        # テストレポートの生成
        report = generate_test_report(test_results)
        
        # 実行時間の表示
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n総実行時間: {duration:.2f}秒")
        
        # 結果に基づく終了コード
        if all(test_results.values()):
            print("\n🎉 すべてのテストが成功しました！")
            exit_code = 0
        else:
            print("\n❌ 一部のテストが失敗しました")
            exit_code = 1
        
    except KeyboardInterrupt:
        print("\n\nテスト実行が中断されました")
        exit_code = 130
    except Exception as e:
        print(f"\n予期しないエラーが発生しました: {e}")
        exit_code = 1
    finally:
        # クリーンアップ
        if not args.no_cleanup:
            cleanup_test_environment()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()