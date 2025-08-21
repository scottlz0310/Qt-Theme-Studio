@echo off
REM Qt-Theme-Studio 開発環境自動セットアップスクリプト (Windows)
REM
REM このスクリプトは新規開発者向けにQt-Theme-Studioの
REM 開発環境をワンコマンドで構築します。
REM
REM 使用方法:
REM   setup_dev_environment.bat
REM   ダブルクリックで実行

setlocal enabledelayedexpansion

REM 色付きメッセージ用の設定（Windows 10以降）
REM ANSI エスケープシーケンスを有効化
for /f "tokens=2 delims=[]" %%x in ('ver') do set "version=%%x"
echo %version% | findstr /r "10\." >nul
if %errorlevel% equ 0 (
    REM Windows 10以降の場合、ANSI エスケープシーケンスを有効化
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1
)

REM ログ関数（簡易版）
:log_info
echo [INFO] %~1
goto :eof

:log_success
echo [SUCCESS] %~1
goto :eof

:log_warning
echo [WARNING] %~1
goto :eof

:log_error
echo [ERROR] %~1
goto :eof

:log_step
echo [STEP] %~1
goto :eof

REM エラーハンドリング
:error_exit
call :log_error "%~1"
call :log_error "セットアップが中断されました。"
call :log_info "問題を解決してから再度実行してください。"
pause
exit /b 1

REM 前提条件チェック
:check_prerequisites
call :log_step "前提条件をチェック中..."

REM Pythonの存在確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :error_exit "Pythonが見つかりません。Python 3.9以上をインストールしてください。"
)

REM Pythonバージョンチェック
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
call :log_info "検出されたPythonバージョン: %python_version%"

REM バージョン比較（簡易版 - 3.9以上かチェック）
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    call :error_exit "Python 3.9以上が必要です。現在のバージョン: %python_version%"
)

REM pipの存在確認
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    call :error_exit "pipが見つかりません。pipをインストールしてください。"
)

REM gitの存在確認
git --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log_warning "gitが見つかりません。バージョン管理機能が制限される可能性があります。"
)

call :log_success "前提条件チェックが完了しました"
goto :eof

REM 環境検出
:detect_environment
call :log_step "環境を検出中..."

REM Windows バージョン情報
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
call :log_info "Windows バージョン: %VERSION%"

REM アーキテクチャ情報
call :log_info "アーキテクチャ: %PROCESSOR_ARCHITECTURE%"

REM WSL環境内での実行チェック（通常はないが念のため）
if defined WSL_DISTRO_NAME (
    call :log_info "WSL環境内での実行が検出されました: %WSL_DISTRO_NAME%"
    call :log_warning "WindowsネイティブでのPython実行を推奨します"
)

REM PowerShellの存在確認
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_info "PowerShellが利用可能です"
) else (
    call :log_warning "PowerShellが見つかりません"
)

call :log_success "環境検出が完了しました"
goto :eof

REM 仮想環境の確認・作成
:setup_virtual_environment
call :log_step "仮想環境をセットアップ中..."

REM 既存の仮想環境をチェック
if defined VIRTUAL_ENV (
    call :log_info "既存の仮想環境が検出されました: %VIRTUAL_ENV%"
    set "PYTHON_CMD=python"
    goto :eof
)

REM Conda環境をチェック
if defined CONDA_DEFAULT_ENV (
    if not "%CONDA_DEFAULT_ENV%"=="base" (
        call :log_info "Conda環境が検出されました: %CONDA_DEFAULT_ENV%"
        set "PYTHON_CMD=python"
        goto :eof
    )
)

REM venvディレクトリの存在をチェック
if exist "venv" (
    call :log_info "既存のvenv環境が見つかりました"

    REM アクティベート
    call venv\Scripts\activate.bat
    set "PYTHON_CMD=python"
    call :log_success "既存の仮想環境をアクティベートしました"
    goto :eof
)

REM 新しい仮想環境を作成するか確認
echo.
call :log_info "仮想環境が見つかりません。"
set /p "create_venv=新しい仮想環境を作成しますか？ (Y/n): "

if /i "%create_venv%"=="n" (
    call :log_warning "仮想環境なしで続行します"
    set "PYTHON_CMD=python"
) else (
    call :log_info "仮想環境を作成中..."

    python -m venv venv
    if %errorlevel% neq 0 (
        call :error_exit "仮想環境の作成に失敗しました"
    )

    REM アクティベート
    call venv\Scripts\activate.bat
    set "PYTHON_CMD=python"

    call :log_success "仮想環境を作成してアクティベートしました"
    call :log_info "今後は以下のコマンドで仮想環境をアクティベートできます:"
    call :log_info "  venv\Scripts\activate.bat"
)
goto :eof

REM 開発環境セットアップスクリプトの実行
:run_dev_setup
call :log_step "開発環境セットアップスクリプトを実行中..."

if not exist "scripts\dev_setup.py" (
    call :error_exit "scripts\dev_setup.pyが見つかりません"
)

call :log_info "Python開発環境セットアップスクリプトを実行します..."

%PYTHON_CMD% scripts\dev_setup.py
if %errorlevel% neq 0 (
    call :error_exit "開発環境セットアップスクリプトの実行に失敗しました"
)

call :log_success "開発環境セットアップが完了しました"
goto :eof

REM Windows環境用の追加設定
:setup_windows_environment
call :log_step "Windows環境用の追加設定を適用中..."

REM Windows用の環境変数設定ファイルを作成
echo REM Windows環境用の環境変数設定 > .env.windows.bat
echo REM このファイルを実行して使用してください: call .env.windows.bat >> .env.windows.bat
echo. >> .env.windows.bat
echo REM 基本的なQt設定 >> .env.windows.bat
echo set QT_QPA_PLATFORM=windows >> .env.windows.bat
echo set QT_LOGGING_RULES=qt.qpa.*=false >> .env.windows.bat
echo set QT_ACCESSIBILITY=0 >> .env.windows.bat
echo. >> .env.windows.bat
echo echo Windows環境用の環境変数を設定しました >> .env.windows.bat
echo echo Qt-Theme-Studioを起動する場合: >> .env.windows.bat
echo echo   python qt_theme_studio_main.py >> .env.windows.bat
echo echo   # または >> .env.windows.bat
echo echo   python -m qt_theme_studio >> .env.windows.bat

call :log_info "Windows用の環境設定ファイルを作成しました: .env.windows.bat"

REM PowerShell用の設定ファイルも作成
echo # Windows環境用の環境変数設定 (PowerShell) > .env.windows.ps1
echo # このファイルをsourceして使用してください: . .\.env.windows.ps1 >> .env.windows.ps1
echo. >> .env.windows.ps1
echo # 基本的なQt設定 >> .env.windows.ps1
echo $env:QT_QPA_PLATFORM = "windows" >> .env.windows.ps1
echo $env:QT_LOGGING_RULES = "qt.qpa.*=false" >> .env.windows.ps1
echo $env:QT_ACCESSIBILITY = "0" >> .env.windows.ps1
echo. >> .env.windows.ps1
echo Write-Host "Windows環境用の環境変数を設定しました" >> .env.windows.ps1
echo Write-Host "Qt-Theme-Studioを起動する場合:" >> .env.windows.ps1
echo Write-Host "  python qt_theme_studio_main.py" >> .env.windows.ps1
echo Write-Host "  # または" >> .env.windows.ps1
echo Write-Host "  python -m qt_theme_studio" >> .env.windows.ps1

call :log_info "PowerShell用の環境設定ファイルを作成しました: .env.windows.ps1"
call :log_success "Windows環境用の設定が完了しました"
goto :eof

REM 最終検証
:verify_installation
call :log_step "インストールを検証中..."

REM 基本的なインポートテスト
%PYTHON_CMD% -c "import qt_theme_studio" >nul 2>&1
if %errorlevel% neq 0 (
    call :log_warning "qt_theme_studioモジュールのインポートに失敗しました"
    call :log_info "これは正常な場合があります（モジュール構造による）"
)

REM Qt フレームワークのテスト
call :log_info "Qt フレームワークをテスト中..."
%PYTHON_CMD% scripts\qt_detector.py --validate >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Qt フレームワークの検証が完了しました"
) else (
    call :log_warning "Qt フレームワークの検証で問題が発生しました"
)

REM pytestの動作確認
%PYTHON_CMD% -m pytest --version >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "pytestが利用可能です"
) else (
    call :log_warning "pytestが利用できません"
)

REM ruffの動作確認
%PYTHON_CMD% -m ruff --version >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "ruffが利用可能です"
) else (
    call :log_warning "ruffが利用できません"
)

call :log_success "インストール検証が完了しました"
goto :eof

REM 完了メッセージとガイダンス
:show_completion_message
echo.
echo 🎉 Qt-Theme-Studio 開発環境のセットアップが完了しました！
echo.
echo 📋 次のステップ:

if exist "venv" (
    if not defined VIRTUAL_ENV (
        echo   1. 仮想環境をアクティベートしてください:
        echo      venv\Scripts\activate.bat
        echo      # PowerShellの場合:
        echo      venv\Scripts\Activate.ps1
        echo.
    )
)

echo   2. アプリケーションを起動してみてください:
echo      python qt_theme_studio_main.py
echo      # または
echo      python -m qt_theme_studio
echo.
echo   3. 環境変数を設定する場合:
echo      call .env.windows.bat
echo      # PowerShellの場合:
echo      . .\.env.windows.ps1
echo.
echo   4. テストを実行してみてください:
echo      pytest
echo.
echo   5. コード品質チェックを実行してみてください:
echo      ruff check .
echo      ruff format .
echo.
echo 🔧 便利なコマンド:
echo   python scripts\quality_check.py     # 品質チェック統合実行
echo   python scripts\quality_dashboard.py # 品質ダッシュボード
echo   python scripts\qt_detector.py       # Qt フレームワーク検出
echo   pre-commit run --all-files          # pre-commitフック実行
echo.
echo 📚 詳細情報:
echo   README.md                           # プロジェクト概要
echo   docs\                               # ドキュメント
echo   .pre-commit-config.yaml             # pre-commit設定
echo   .env.windows.bat                    # Windows環境変数設定
echo   .env.windows.ps1                    # PowerShell環境変数設定
echo.
echo 問題が発生した場合は、ログを確認するか、issueを作成してください。
echo Happy coding! 🚀
echo.
pause
goto :eof

REM メイン処理
:main
echo 🚀 Qt-Theme-Studio 開発環境自動セットアップ
echo ==============================================
echo.

REM スクリプトの実行ディレクトリをプロジェクトルートに設定
cd /d "%~dp0"

call :log_info "プロジェクトルート: %CD%"
echo.

REM 各ステップを実行
call :check_prerequisites
call :detect_environment
call :setup_virtual_environment
call :run_dev_setup
call :setup_windows_environment
call :verify_installation
call :show_completion_message

goto :eof

REM メイン処理を呼び出し
call :main
