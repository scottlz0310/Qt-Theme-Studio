---
inclusion: always
---

# デバッグ・テスト用ガイドライン

## 現在のフェーズ
実装確認とデバッグ作業中

## 重要な制約
- **print文禁止** - 必ずloggerを使用
- **日本語ログメッセージ** - すべてのログ出力は日本語
- **エラーハンドリング** - ユーザーフレンドリーな日本語エラーメッセージ

## 技術スタック（最小限）
- **Python 3.8+** with タイプヒント必須
- **Qt フレームワーク**: PySide6/PyQt6/PyQt5 自動検出
- **qt-theme-manager**: GitHubから直接インストール
  ```bash
  pip install git+https://github.com/scottlz0310/Qt-Theme-Manager.git
  ```

## デバッグ用コマンド
```bash
# テスト実行
pytest
python test_theme_loading_reflection.py

# アプリケーション起動
python launch_theme_studio.py
python -m qt_theme_studio

# 依存関係確認
pip list | grep -E "(qt|theme)"
```

## アーキテクチャ（簡潔版）
- **MVC パターン**: views/, controllers/, services/
- **アダプターパターン**: adapters/ でqt-theme-manager統合
- **エントリーポイント**: launch_theme_studio.py

## 言語要件
- **コード**: 変数名・関数名は英語、コメント・docstringは日本語
- **ログ・エラー**: すべて日本語
- **応答**: 日本語で回答
