# Qt-Theme-Studio テストケース完全ガイド

## 📊 テスト概要

### **テスト統計**
- **総テスト数**: 153個
- **成功率**: 100%
- **カバレッジ**: 36%
- **テストタイプ**: 単体テスト、統合テスト、パフォーマンステスト

### **テスト構成**
```
tests/
├── unit/                    # 単体テスト (98個)
│   ├── test_theme_adapter.py      # 38個 - テーマアダプター
│   ├── test_qt_adapter.py         # 7個 - Qtアダプター
│   ├── test_theme_generator.py    # 25個 - テーマジェネレーター
│   ├── test_main_window.py        # 25個 - メインウィンドウ
│   └── test_preview.py            # 15個 - プレビュー機能
├── integration/            # 統合テスト (16個)
│   ├── test_theme_integration.py          # 6個 - 基本統合
│   └── test_comprehensive_integration.py  # 10個 - 包括的統合
└── fixtures/              # テストフィクスチャ
    ├── theme_data.py      # テーマデータ
    └── mock_objects.py    # モックオブジェクト
```

## 🧪 単体テスト詳細

### **1. テーマアダプター (38個)**

#### **基本機能テスト**
- `test_init`: 初期化テスト
- `test_initialize_theme_manager_success`: テーママネージャー初期化成功
- `test_is_initialized`: 初期化状態確認

#### **テーマ読み込みテスト**
- `test_load_theme_success`: テーマ読み込み成功
- `test_load_theme_failure`: テーマ読み込み失敗
- `test_load_qss_theme_success`: QSSテーマ読み込み
- `test_load_css_theme_success`: CSSテーマ読み込み
- `test_load_unsupported_format`: 未対応形式
- `test_json_decode_error`: JSONデコードエラー

#### **テーマ保存・エクスポートテスト**
- `test_save_theme_success`: テーマ保存成功
- `test_export_theme`: テーマエクスポート
- `test_export_qss_format`: QSS形式エクスポート
- `test_export_css_format`: CSS形式エクスポート
- `test_export_unsupported_format`: 未対応形式エクスポート

#### **テーマ検証テスト**
- `test_validate_theme_valid`: 有効テーマ検証
- `test_validate_theme_invalid`: 無効テーマ検証
- `test_validate_theme_with_warnings`: 警告付き検証
- `test_validate_theme_colors_valid`: 色値有効性検証
- `test_validate_theme_colors_invalid`: 色値無効性検証
- `test_validate_theme_empty_data`: 空データ検証
- `test_validate_theme_complex_structure`: 複雑構造検証
- `test_validate_theme_mixed_validity`: 混合有効性検証

#### **色処理テスト**
- `test_is_valid_color_hex_formats`: 16進数色形式
- `test_is_valid_color_named_colors`: 名前付き色
- `test_is_valid_color_invalid_formats`: 無効色形式
- `test_is_valid_color_edge_cases`: エッジケース

#### **色抽出・生成テスト**
- `test_extract_colors_from_qss`: QSSからの色抽出
- `test_extract_colors_from_css`: CSSからの色抽出
- `test_extract_colors_from_qss_no_colors`: 色なしQSS
- `test_extract_colors_from_css_no_colors`: 色なしCSS
- `test_generate_qss_from_theme`: テーマからのQSS生成
- `test_generate_css_from_theme`: テーマからのCSS生成
- `test_generate_qss_from_theme_minimal`: 最小テーマからのQSS
- `test_generate_css_from_theme_minimal`: 最小テーマからのCSS

### **2. Qtアダプター (7個)**

#### **基本機能テスト**
- `test_init`: 初期化テスト
- `test_detect_qt_framework`: Qtフレームワーク検出
- `test_get_framework_info`: フレームワーク情報取得
- `test_apply_theme_to_widget`: ウィジェットへのテーマ適用
- `test_get_widget_stylesheet`: ウィジェットスタイルシート取得
- `test_validate_widget`: ウィジェット検証
- `test_get_widget_info`: ウィジェット情報取得

### **3. テーマジェネレーター (25個)**

#### **基本機能テスト**
- `test_init`: 初期化テスト
- `test_preset_themes_structure`: プリセットテーマ構造
- `test_get_preset_themes`: プリセットテーマ取得
- `test_preset_themes_hex_format`: 16進数形式
- `test_preset_themes_unique_names`: 一意な名前

#### **色処理テスト**
- `test_is_dark_color_dark`: 暗い色判定
- `test_is_dark_color_light`: 明るい色判定
- `test_is_dark_color_edge_cases`: エッジケース

#### **色調整テスト**
- `test_adjust_color_brightness_increase`: 明度増加
- `test_adjust_color_brightness_decrease`: 明度減少
- `test_adjust_color_saturation_increase`: 彩度増加
- `test_adjust_color_saturation_decrease`: 彩度減少
- `test_adjust_color_boundaries`: 境界値

#### **コントラスト色生成テスト**
- `test_generate_contrasting_color_high_contrast`: 高コントラスト
- `test_generate_contrasting_color_low_contrast`: 低コントラスト
- `test_generate_contrasting_color_edge_cases`: エッジケース

#### **テーマ生成テスト**
- `test_generate_theme_from_background_dark`: 暗い背景
- `test_generate_theme_from_background_light`: 明るい背景
- `test_generate_theme_from_background_mid_tone`: 中間調
- `test_generate_theme_button_colors`: ボタン色
- `test_generate_theme_panel_colors`: パネル色
- `test_generate_theme_color_relationships`: 色の関係性
- `test_generate_theme_consistency`: 一貫性
- `test_generate_theme_edge_cases`: エッジケース
- `test_generate_theme_performance`: パフォーマンス

### **4. メインウィンドウ (25個)**

#### **基本機能テスト**
- `test_init`: 初期化テスト
- `test_adapters_creation`: アダプター作成
- `test_theme_generator_creation`: テーマジェネレーター作成
- `test_preview_window_creation`: プレビューウィンドウ作成
- `test_initial_theme_state`: 初期テーマ状態

#### **テーマ管理テスト**
- `test_load_custom_theme_file_success`: テーマファイル読み込み成功
- `test_load_custom_theme_file_cancelled`: テーマファイル読み込みキャンセル
- `test_on_theme_changed`: テーマ変更
- `test_on_theme_changed_none`: テーマ変更なし
- `test_apply_current_theme`: 現在のテーマ適用
- `test_save_current_theme`: 現在のテーマ保存
- `test_export_all_themes`: 全テーマエクスポート
- `test_theme_management`: テーマ管理
- `test_theme_selection_workflow`: テーマ選択ワークフロー
- `test_error_handling_workflow`: エラーハンドリングワークフロー

#### **色処理テスト**
- `test_choose_color`: 色選択
- `test_get_current_color`: 現在の色取得
- `test_set_color_button`: 色ボタン設定
- `test_apply_preset_color`: プリセット色適用

#### **テーマ生成テスト**
- `test_generate_theme_from_background`: 背景色からのテーマ生成
- `test_update_generated_theme_preview`: 生成テーマプレビュー更新
- `test_convert_theme_for_preview`: プレビュー用テーマ変換

#### **UI状態管理テスト**
- `test_ui_state_management`: UI状態管理
- `test_method_call_consistency`: メソッド呼び出し一貫性
- `test_theme_data_structure`: テーマデータ構造

### **5. プレビュー機能 (15個)**

#### **基本機能テスト**
- `test_init`: 初期化テスト
- `test_adapters_assignment`: アダプター割り当て
- `test_create_widget`: ウィジェット作成
- `test_update_preview`: プレビュー更新
- `test_apply_theme`: テーマ適用
- `test_refresh_preview`: プレビューのリフレッシュ
- `test_get_preview_widget`: プレビューウィジェット取得

#### **テーマ処理テスト**
- `test_theme_data_handling`: テーマデータ処理
- `test_color_handling`: 色処理
- `test_theme_conversion_workflow`: テーマ変換ワークフロー

#### **状態管理テスト**
- `test_preview_state_management`: プレビュー状態管理
- `test_error_handling_workflow`: エラーハンドリングワークフロー
- `test_ui_integration`: UI統合

#### **パフォーマンステスト**
- `test_performance_optimization`: パフォーマンス最適化

## 🔗 統合テスト詳細

### **1. 基本統合テスト (6個)**

#### **テーマワークフローテスト**
- `test_theme_load_and_save_workflow`: テーマ読み込み・保存ワークフロー
- `test_theme_validation_workflow`: テーマ検証ワークフロー
- `test_theme_export_workflow`: テーマエクスポートワークフロー

#### **Qtアダプターテスト**
- `test_qt_adapter_initialization`: Qtアダプター初期化

#### **エラーハンドリングテスト**
- `test_error_handling_integration`: エラーハンドリング統合

#### **パフォーマンステスト**
- `test_performance_integration`: パフォーマンス統合

### **2. 包括的統合テスト (10個)**

#### **完全ワークフローテスト**
- `test_complete_theme_workflow`: 完全なテーマワークフロー
- `test_multi_theme_management_workflow`: 複数テーマ管理ワークフロー
- `test_theme_conversion_workflow`: テーマ変換ワークフロー
- `test_error_recovery_workflow`: エラー回復ワークフロー

#### **パフォーマンス・効率性テスト**
- `test_performance_under_load`: 負荷下でのパフォーマンス
- `test_memory_efficiency_workflow`: メモリ効率ワークフロー
- `test_concurrent_theme_processing`: 並行テーマ処理

#### **互換性・一貫性テスト**
- `test_file_format_compatibility_workflow`: ファイル形式互換性
- `test_theme_consistency_workflow`: テーマ一貫性

#### **エンドツーエンドテスト**
- `test_end_to_end_user_scenario`: エンドツーエンドユーザーシナリオ

## 📋 テスト実行ガイド

### **基本的なテスト実行**

```bash
# 全テスト実行
python -m pytest tests/ -v

# 単体テストのみ
python -m pytest tests/unit/ -v

# 統合テストのみ
python -m pytest tests/integration/ -v

# 特定のテストファイル
python -m pytest tests/unit/test_theme_adapter.py -v

# 特定のテストクラス
python -m pytest tests/unit/test_theme_adapter.py::TestThemeAdapter -v

# 特定のテストメソッド
python -m pytest tests/unit/test_theme_adapter.py::TestThemeAdapter::test_init -v
```

### **カバレッジ測定**

```bash
# 全体カバレッジ
python -m pytest tests/ --cov=qt_theme_studio --cov-report=term-missing

# 特定モジュールのカバレッジ
python -m pytest tests/ --cov=qt_theme_studio.adapters.theme_adapter --cov-report=term-missing

# HTMLレポート生成
python -m pytest tests/ --cov=qt_theme_studio --cov-report=html
```

### **パフォーマンステスト**

```bash
# ベンチマークテスト
python -m pytest tests/ --benchmark-only

# 特定のパフォーマンステスト
python -m pytest tests/integration/test_comprehensive_integration.py::TestComprehensiveIntegration::test_performance_under_load -v
```

## 🎯 テスト戦略

### **テストピラミッド**
```
    🔺 E2E/統合テスト (16個)
   🔺🔺 単体テスト (98個)
  🔺🔺🔺 フィクスチャ・モック
```

### **テスト優先度**
1. **高優先度**: テーマ管理の基本機能
2. **中優先度**: UI操作とエラーハンドリング
3. **低優先度**: パフォーマンスとエッジケース

### **カバレッジ目標**
- **アダプター層**: 80%以上 ✅
- **ジェネレーター層**: 100% ✅
- **ロガー層**: 90%以上 ✅
- **ビュー層**: 30%以上
- **全体**: 45%以上

## 🚀 次のステップ

### **短期目標**
1. ビュー層のカバレッジ向上
2. help_dialogのテスト追加
3. 残りの未カバー部分の特定

### **中期目標**
1. カバレッジ80%達成
2. パフォーマンステストの強化
3. 自動化テストの実装

### **長期目標**
1. 継続的品質向上
2. テスト駆動開発の導入
3. 品質メトリクスの可視化
