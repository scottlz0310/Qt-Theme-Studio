#!/usr/bin/env python3
"""
Qt-Theme-Studio リリースビルドスクリプト

このスクリプトは以下の処理を実行します:
1. 依存関係の確認
2. テストの実行
3. パッケージのビルド
4. 実行ファイルの作成
5. 配布用アーカイブの作成
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

def run_command(command, check=True, capture_output=False):
    """コマンドを実行する"""
    print(f"実行中: {command}")
    if isinstance(command, str):
        command = command.split()

    result = subprocess.run(
        command,
        check=check,
        capture_output=capture_output,
        text=True
    )

    if capture_output:
        return result.stdout.strip()
    return result

def check_dependencies():
    """依存関係を確認する"""
    print("=== 依存関係の確認 ===")

    # Python バージョン確認
    python_version = sys.version_info
    print(f"Python バージョン: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version < (3, 8):
        raise RuntimeError("Python 3.8 以上が必要です")

    # 必要なパッケージの確認
    required_packages = [
        "build",
        "pyinstaller",
        "pytest",
        "qt_theme_studio"
    ]

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} インストール済み")
        except ImportError:
            print(f"✗ {package} が見つかりません")
            raise RuntimeError(f"{package} をインストールしてください: pip install {package}")

def run_tests():
    """テストを実行する"""
    print("=== 包括的テストスイートの実行 ===")

    # 環境変数を設定
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    try:
        # 全テストを実行(高速モード)
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/", "-v", "--tb=short",
            "--maxfail=1",  # 1個でも失敗したら停止(品質保証)
            "--durations=10",  # 遅いテストトップ10を表示
            "-x"  # 最初の失敗で停止
        ], env=env, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 全テストが成功しました！")
            print(f"実行時間: {result.stdout.split()[-1] if result.stdout else '不明'}")
        else:
            print("❌ テストが失敗しました:")
            print(result.stdout)
            print(result.stderr)
            raise RuntimeError("テストスイートが失敗しました。リリースを中止します。")

    except subprocess.CalledProcessError as e:
        print(f"❌ テスト実行エラー (終了コード: {e.returncode})")
        raise RuntimeError("テストの実行に失敗しました。リリースを中止します。")

def build_package():
    """Python パッケージをビルドする"""
    print("=== Python パッケージのビルド ===")

    # 既存のdistディレクトリを削除
    if Path("dist").exists():
        shutil.rmtree("dist")

    # パッケージビルド
    run_command([sys.executable, "-m", "build"])

    print("✓ Python パッケージのビルド完了")

def build_executable():
    """実行ファイルをビルドする"""
    print("=== 実行ファイルのビルド ===")

    # PyInstallerでビルド
    spec_file = "qt-theme-studio.spec"
    if Path(spec_file).exists():
        run_command(["pyinstaller", spec_file, "--clean"])
    else:
        # specファイルがない場合は基本的なビルド
        run_command([
            "pyinstaller",
            "--onefile",
            "--windowed" if platform.system() == "Windows" else "--onefile",
            "--name", "qt-theme-studio",
            "launch_theme_studio.py"
        ])

    print("✓ 実行ファイルのビルド完了")

def create_distribution():
    """配布用アーカイブを作成する"""
    print("=== 配布用アーカイブの作成 ===")

    # バージョン情報を取得
    try:
        with open("pyproject.toml", encoding="utf-8") as f:
            content = f.read()
            # 簡単なバージョン抽出(本来はtomlライブラリを使用すべき)
            for line in content.split("\n"):
                if line.strip().startswith("version"):
                    version = line.split("=")[1].strip().strip('"\'')
                    break
            else:
                version = "1.0.0"
    except:
        version = "1.0.0"

    system = platform.system().lower()
    arch = platform.machine().lower()

    # 配布ディレクトリを作成
    dist_name = f"qt-theme-studio-{version}-{system}-{arch}"
    dist_dir = Path("dist") / dist_name

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)

    # 実行ファイルをコピー
    exe_name = "qt-theme-studio.exe" if system == "windows" else "qt-theme-studio"
    exe_path = Path("dist") / exe_name

    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / exe_name)

    # ドキュメントをコピー
    docs = ["README.md", "INSTALL.md", "RELEASE_NOTES.md", "CHANGELOG.md"]
    for doc in docs:
        if Path(doc).exists():
            shutil.copy2(doc, dist_dir / doc)

    # サンプルファイルをコピー
    if Path("examples").exists():
        shutil.copytree("examples", dist_dir / "examples")

    # アーカイブを作成
    if system == "windows":
        archive_name = f"{dist_name}.zip"
        shutil.make_archive(
            str(Path("dist") / dist_name),
            "zip",
            str(dist_dir.parent),
            dist_name
        )
    else:
        archive_name = f"{dist_name}.tar.gz"
        shutil.make_archive(
            str(Path("dist") / dist_name),
            "gztar",
            str(dist_dir.parent),
            dist_name
        )

    print(f"✓ 配布用アーカイブを作成しました: {archive_name}")

    # ファイルサイズを表示
    archive_path = Path("dist") / archive_name
    if archive_path.exists():
        size_mb = archive_path.stat().st_size / (1024 * 1024)
        print(f"  ファイルサイズ: {size_mb:.2f} MB")

def create_checksums():
    """チェックサムファイルを作成する"""
    print("=== チェックサムファイルの作成 ===")

    import hashlib

    dist_dir = Path("dist")
    checksum_file = dist_dir / "checksums.txt"

    with open(checksum_file, "w", encoding="utf-8") as f:
        f.write("# Qt-Theme-Studio チェックサム\n")
        f.write("# SHA256ハッシュ値\n\n")

        for file_path in dist_dir.glob("*"):
            if file_path.is_file() and file_path.name != "checksums.txt":
                # SHA256ハッシュを計算
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as file:
                    for chunk in iter(lambda: file.read(4096), b""):
                        sha256_hash.update(chunk)

                hash_value = sha256_hash.hexdigest()
                f.write(f"{hash_value}  {file_path.name}\n")

    print(f"✓ チェックサムファイルを作成しました: {checksum_file}")

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description="Qt-Theme-Studio リリースビルド")
    parser.add_argument("--skip-tests", action="store_true", help="テストをスキップ")
    parser.add_argument("--skip-executable", action="store_true", help="実行ファイルビルドをスキップ")
    parser.add_argument("--package-only", action="store_true", help="Pythonパッケージのみビルド")

    args = parser.parse_args()

    try:
        print("Qt-Theme-Studio リリースビルドを開始します")
        print(f"プラットフォーム: {platform.system()} {platform.machine()}")
        print(f"Python: {sys.version}")
        print()

        # 依存関係確認
        check_dependencies()

        # テスト実行
        if not args.skip_tests:
            run_tests()

        # パッケージビルド
        build_package()

        if not args.package_only:
            # 実行ファイルビルド
            if not args.skip_executable:
                build_executable()

            # 配布用アーカイブ作成
            create_distribution()

            # チェックサム作成
            create_checksums()

        print()
        print("=== ビルド完了 ===")
        print("生成されたファイル:")

        dist_dir = Path("dist")
        for file_path in sorted(dist_dir.glob("*")):
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"  {file_path.name} ({size_mb:.2f} MB)")

        print()
        print("リリースの準備が完了しました！")

    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
