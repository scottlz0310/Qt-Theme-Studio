# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-08-21 - MVP Release

### Added
- **統合テーマエディター**: 直感的なビジュアルインターフェースでテーマプロパティを編集
- **ライブプレビューシステム**: リアルタイムでテーマの変更を確認
- **スマートテーマ管理**: テーマの保存、読み込み、エクスポート機能
- **CLI モジュール**: テーマ品質チェック機能
- **包括的テストスイート**: 高いコードカバレッジを実現
- **CI/CD パイプライン**: 自動化されたコード品質チェックとテスト実行
- **アクセシビリティ対応**: WCAG準拠のコントラスト調整機能

### Fixed
- ライブプレビュー機能の安定性向上
- テーマエラー可視化と検証機能の追加
- X11/WSLg環境での検出ロジック改善
- EGL ライブラリ依存関係の解決
- MyPy 型チェックエラーの完全解決
- Ruff コード品質問題の修正
- 例外処理の改善とエラー抑制の排除

### Changed
- メインエントリーポイントを `qt_theme_studio_main.py` から `main.py` に変更
- アーキテクチャの完全刷新（MVCパターン採用）
- qt-theme-manager ライブラリとの統合強化
- ファイルダイアログのパフォーマンス改善
- UI応答性の向上

### Technical Improvements
- Python 3.8-3.12 サポート
- PySide6/PyQt6/PyQt5 対応
- Pre-commit フック設定
- GitHub Actions ワークフロー統合
- コード品質ツール統合（Black, isort, Flake8, MyPy）
- テストカバレッジ向上

### Development
- 開発ルールの確立（エラー回避ソリューションの禁止）
- 統合CI/CDシステムの構築
- コード品質チェックの自動化
- テスト環境の整備

## [Unreleased]

### Planned
- ゼブラパターンエディターの実装
- 追加のテーマテンプレート
- 国際化対応の拡張
- プラグインシステムの検討

---

**Note**: このプロジェクトは qt-theme-manager ライブラリに依存しており、GitHubから直接インストールする必要があります。
