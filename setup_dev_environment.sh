#!/bin/bash
# Qt-Theme-Studio 開発環境自動セットアップスクリプト (Linux/Mac)
#
# このスクリプトは新規開発者向けにQt-Theme-Studioの
# 開発環境をワンコマンドで構築します。
#
# 使用方法:
#   ./setup_dev_environment.sh
#   bash setup_dev_environment.sh

set -e  # エラー時に終了

# 色付きメッセージ用の定数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# エラーハンドリング
error_exit() {
    log_error "$1"
    log_error "セットアップが中断されました。"
    log_info "問題を解決してから再度実行してください。"
    exit 1
}

# 前提条件チェック
check_prerequisites() {
    log_step "前提条件をチェック中..."

    # Pythonの存在確認
    if ! command -v python3 &> /dev/null; then
        error_exit "Python3が見つかりません。Python 3.9以上をインストールしてください。"
    fi

    # Pythonバージョンチェック
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "検出されたPythonバージョン: $python_version"

    # バージョン比較（簡易版）
    if [[ $(echo "$python_version 3.9" | awk '{print ($1 >= $2)}') -eq 0 ]]; then
        error_exit "Python 3.9以上が必要です。現在のバージョン: $python_version"
    fi

    # pipの存在確認
    if ! python3 -m pip --version &> /dev/null; then
        error_exit "pipが見つかりません。pipをインストールしてください。"
    fi

    # gitの存在確認
    if ! command -v git &> /dev/null; then
        log_warning "gitが見つかりません。バージョン管理機能が制限される可能性があります。"
    fi

    log_success "前提条件チェックが完了しました"
}

# OS環境の検出
detect_environment() {
    log_step "環境を検出中..."

    OS=$(uname -s)
    ARCH=$(uname -m)
    
    log_info "OS: $OS"
    log_info "アーキテクチャ: $ARCH"

    # WSL環境の検出
    if [[ -f /proc/version ]] && grep -qi microsoft /proc/version; then
        IS_WSL=true
        log_info "WSL環境が検出されました"
        
        # WSLgの検出
        if [[ -n "$WAYLAND_DISPLAY" ]]; then
            IS_WSLG=true
            log_info "WSLg環境が検出されました"
        else
            IS_WSLG=false
            log_info "WSL2 + VcXsrv環境と推定されます"
        fi
    else
        IS_WSL=false
        IS_WSLG=false
    fi

    # macOSの場合の追加チェック
    if [[ "$OS" == "Darwin" ]]; then
        log_info "macOS環境が検出されました"
        
        # Homebrewの存在確認
        if command -v brew &> /dev/null; then
            log_info "Homebrewが利用可能です"
        else
            log_warning "Homebrewが見つかりません。依存関係のインストールで問題が発生する可能性があります。"
        fi
    fi

    log_success "環境検出が完了しました"
}

# 仮想環境の確認・作成
setup_virtual_environment() {
    log_step "仮想環境をセットアップ中..."

    # 既存の仮想環境をチェック
    if [[ -n "$VIRTUAL_ENV" ]]; then
        log_info "既存の仮想環境が検出されました: $VIRTUAL_ENV"
        PYTHON_CMD="python"
        return 0
    fi

    # Conda環境をチェック
    if [[ -n "$CONDA_DEFAULT_ENV" ]] && [[ "$CONDA_DEFAULT_ENV" != "base" ]]; then
        log_info "Conda環境が検出されました: $CONDA_DEFAULT_ENV"
        PYTHON_CMD="python"
        return 0
    fi

    # venvディレクトリの存在をチェック
    if [[ -d "venv" ]]; then
        log_info "既存のvenv環境が見つかりました"
        
        # アクティベート
        source venv/bin/activate
        PYTHON_CMD="python"
        log_success "既存の仮想環境をアクティベートしました"
        return 0
    fi

    # 新しい仮想環境を作成するか確認
    echo
    log_info "仮想環境が見つかりません。"
    read -p "新しい仮想環境を作成しますか？ (Y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_warning "仮想環境なしで続行します"
        PYTHON_CMD="python3"
    else
        log_info "仮想環境を作成中..."
        
        if ! python3 -m venv venv; then
            error_exit "仮想環境の作成に失敗しました"
        fi

        # アクティベート
        source venv/bin/activate
        PYTHON_CMD="python"
        
        log_success "仮想環境を作成してアクティベートしました"
        log_info "今後は以下のコマンドで仮想環境をアクティベートできます:"
        log_info "  source venv/bin/activate"
    fi
}

# 開発環境セットアップスクリプトの実行
run_dev_setup() {
    log_step "開発環境セットアップスクリプトを実行中..."

    if [[ ! -f "scripts/dev_setup.py" ]]; then
        error_exit "scripts/dev_setup.pyが見つかりません"
    fi

    log_info "Python開発環境セットアップスクリプトを実行します..."
    
    if ! $PYTHON_CMD scripts/dev_setup.py; then
        error_exit "開発環境セットアップスクリプトの実行に失敗しました"
    fi

    log_success "開発環境セットアップが完了しました"
}

# WSL環境用の追加設定
setup_wsl_environment() {
    if [[ "$IS_WSL" != true ]]; then
        return 0
    fi

    log_step "WSL環境用の追加設定を適用中..."

    # 既存のWSL対応スクリプトとの統合
    if [[ -f "scripts/run_with_wsl2_fix.sh" ]]; then
        log_info "WSL2対応スクリプトが見つかりました"
        chmod +x scripts/run_with_wsl2_fix.sh
    fi

    if [[ -f "scripts/run_with_wslg.sh" ]]; then
        log_info "WSLg対応スクリプトが見つかりました"
        chmod +x scripts/run_with_wslg.sh
    fi

    # WSL用の環境変数設定ファイルを作成
    cat > .env.wsl << 'EOF'
# WSL環境用の環境変数設定
# このファイルをsourceして使用してください: source .env.wsl

# 基本的なQt設定
export QT_QPA_PLATFORM=xcb
export DISPLAY=:0
export QT_LOGGING_RULES="qt.qpa.*=false"
export QT_ACCESSIBILITY=0

# WSL2固有の設定
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
export QT_WAYLAND_FORCE_DPI=96

echo "WSL環境用の環境変数を設定しました"
echo "Qt-Theme-Studioを起動する場合:"
echo "  python qt_theme_studio_main.py"
echo "  # または既存のスクリプトを使用:"
echo "  ./scripts/run_with_wsl2_fix.sh"
EOF

    # WSLg環境の場合の追加設定
    if [[ "$IS_WSLG" == true ]]; then
        cat > .env.wslg << 'EOF'
# WSLg環境用の環境変数設定
# このファイルをsourceして使用してください: source .env.wslg

# WSLg用の設定
export WAYLAND_DISPLAY=wayland-0
export XDG_SESSION_TYPE=wayland
export QT_QPA_PLATFORM=wayland
export QT_WAYLAND_DISABLE_WINDOWDECORATION=0
export QT_WAYLAND_FORCE_DPI=96

# VcXsrvの設定をクリア
unset DISPLAY

echo "WSLg環境用の環境変数を設定しました"
echo "Qt-Theme-Studioを起動する場合:"
echo "  python qt_theme_studio_main.py"
echo "  # または既存のスクリプトを使用:"
echo "  ./scripts/run_with_wslg.sh"
EOF
        log_info "WSLg用の環境設定ファイルを作成しました: .env.wslg"
    fi

    log_info "WSL用の環境設定ファイルを作成しました: .env.wsl"
    log_success "WSL環境用の設定が完了しました"
}

# 最終検証
verify_installation() {
    log_step "インストールを検証中..."

    # 基本的なインポートテスト
    if ! $PYTHON_CMD -c "import qt_theme_studio" 2>/dev/null; then
        log_warning "qt_theme_studioモジュールのインポートに失敗しました"
        log_info "これは正常な場合があります（モジュール構造による）"
    fi

    # Qt フレームワークのテスト
    log_info "Qt フレームワークをテスト中..."
    if $PYTHON_CMD scripts/qt_detector.py --validate 2>/dev/null; then
        log_success "Qt フレームワークの検証が完了しました"
    else
        log_warning "Qt フレームワークの検証で問題が発生しました"
    fi

    # pytestの動作確認
    if $PYTHON_CMD -m pytest --version &>/dev/null; then
        log_success "pytestが利用可能です"
    else
        log_warning "pytestが利用できません"
    fi

    # ruffの動作確認
    if $PYTHON_CMD -m ruff --version &>/dev/null; then
        log_success "ruffが利用可能です"
    else
        log_warning "ruffが利用できません"
    fi

    log_success "インストール検証が完了しました"
}

# 完了メッセージとガイダンス
show_completion_message() {
    echo
    echo "🎉 Qt-Theme-Studio 開発環境のセットアップが完了しました！"
    echo
    echo "📋 次のステップ:"
    
    if [[ -d "venv" ]] && [[ -z "$VIRTUAL_ENV" ]]; then
        echo "  1. 仮想環境をアクティベートしてください:"
        echo "     source venv/bin/activate"
        echo
    fi

    echo "  2. アプリケーションを起動してみてください:"
    echo "     python qt_theme_studio_main.py"
    echo "     # または"
    echo "     python -m qt_theme_studio"
    echo

    if [[ "$IS_WSL" == true ]]; then
        echo "  3. WSL環境での起動（推奨）:"
        if [[ "$IS_WSLG" == true ]]; then
            echo "     source .env.wslg && python qt_theme_studio_main.py"
            echo "     # または"
            echo "     ./scripts/run_with_wslg.sh"
        else
            echo "     source .env.wsl && python qt_theme_studio_main.py"
            echo "     # または"
            echo "     ./scripts/run_with_wsl2_fix.sh"
        fi
        echo
    fi

    echo "  4. テストを実行してみてください:"
    echo "     pytest"
    echo
    echo "  5. コード品質チェックを実行してみてください:"
    echo "     ruff check ."
    echo "     ruff format ."
    echo
    echo "🔧 便利なコマンド:"
    echo "  python scripts/quality_check.py     # 品質チェック統合実行"
    echo "  python scripts/quality_dashboard.py # 品質ダッシュボード"
    echo "  python scripts/qt_detector.py       # Qt フレームワーク検出"
    echo "  pre-commit run --all-files          # pre-commitフック実行"
    echo
    echo "📚 詳細情報:"
    echo "  README.md                           # プロジェクト概要"
    echo "  docs/                               # ドキュメント"
    echo "  .pre-commit-config.yaml             # pre-commit設定"
    
    if [[ "$IS_WSL" == true ]]; then
        echo "  .env.wsl                            # WSL環境変数設定"
        if [[ "$IS_WSLG" == true ]]; then
            echo "  .env.wslg                           # WSLg環境変数設定"
        fi
    fi
    
    echo
    echo "問題が発生した場合は、ログを確認するか、issueを作成してください。"
    echo "Happy coding! 🚀"
}

# メイン処理
main() {
    echo "🚀 Qt-Theme-Studio 開発環境自動セットアップ"
    echo "=============================================="
    echo

    # スクリプトの実行ディレクトリをプロジェクトルートに設定
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"

    log_info "プロジェクトルート: $(pwd)"
    echo

    # 各ステップを実行
    check_prerequisites
    detect_environment
    setup_virtual_environment
    run_dev_setup
    setup_wsl_environment
    verify_installation
    show_completion_message
}

# スクリプトが直接実行された場合のみmainを呼び出し
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi