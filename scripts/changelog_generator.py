#!/usr/bin/env python3
"""
Qt-Theme-Studio 変更履歴自動生成スクリプト

このスクリプトは以下の処理を実行します:
1. Gitコミットメッセージから変更履歴を生成
2. プルリクエスト情報の統合
3. 日本語での変更履歴フォーマット
4. セマンティックバージョニングに基づく分類
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)


class ChangelogGenerator:
    """変更履歴生成クラス"""

    def __init__(self):
        """初期化"""
        self.logger = self._setup_logger()
        self.commit_patterns = {
            "feat": "追加",
            "add": "追加", 
            "feature": "追加",
            "fix": "修正",
            "bugfix": "修正",
            "hotfix": "修正",
            "change": "変更",
            "update": "変更",
            "modify": "変更",
            "refactor": "変更",
            "remove": "削除",
            "delete": "削除",
            "deprecate": "非推奨",
            "security": "セキュリティ",
            "sec": "セキュリティ",
            "perf": "変更",
            "performance": "変更",
            "style": "変更",
            "docs": "変更",
            "doc": "変更",
            "test": "変更",
            "ci": "変更",
            "build": "変更",
            "chore": "変更"
        }

    def _setup_logger(self):
        """ロガーをセットアップ"""
        import logging
        
        logger = logging.getLogger("changelog_generator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """コマンドを実行"""
        self.logger.info(f"コマンド実行: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                check=check,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"コマンド実行エラー: {e}")
            self.logger.error(f"標準出力: {e.stdout}")
            self.logger.error(f"標準エラー: {e.stderr}")
            raise

    def get_git_commits(self, since_tag: Optional[str] = None, until_tag: Optional[str] = None) -> List[Dict]:
        """Gitコミット情報を取得"""
        self.logger.info("Gitコミット情報を取得中...")
        
        # コミット範囲を決定
        if since_tag and until_tag:
            commit_range = f"{since_tag}..{until_tag}"
        elif since_tag:
            commit_range = f"{since_tag}..HEAD"
        elif until_tag:
            commit_range = until_tag
        else:
            # 最新の20コミットを取得
            commit_range = "HEAD~20..HEAD"

        # Gitログを取得
        try:
            result = self.run_command([
                "git", "log", commit_range,
                "--pretty=format:%H|%s|%an|%ae|%ad|%b",
                "--date=iso"
            ])
            
            commits = []
            current_commit = None
            
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                    
                if '|' in line and len(line.split('|')) >= 5:
                    # 新しいコミット行
                    if current_commit:
                        commits.append(current_commit)
                    
                    parts = line.split('|', 5)
                    current_commit = {
                        "hash": parts[0],
                        "subject": parts[1],
                        "author": parts[2],
                        "email": parts[3],
                        "date": parts[4],
                        "body": parts[5] if len(parts) > 5 else ""
                    }
                else:
                    # コミット本文の続き
                    if current_commit:
                        current_commit["body"] += "\n" + line
            
            # 最後のコミットを追加
            if current_commit:
                commits.append(current_commit)
            
            self.logger.info(f"{len(commits)}個のコミットを取得しました")
            return commits
            
        except subprocess.CalledProcessError:
            self.logger.warning("Gitコミット情報の取得に失敗しました")
            return []

    def get_git_tags(self) -> List[str]:
        """Gitタグ一覧を取得"""
        try:
            result = self.run_command(["git", "tag", "-l", "--sort=-version:refname"])
            tags = [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]
            self.logger.info(f"{len(tags)}個のタグを取得しました")
            return tags
        except subprocess.CalledProcessError:
            self.logger.warning("Gitタグの取得に失敗しました")
            return []

    def classify_commit(self, commit: Dict) -> Tuple[str, str]:
        """コミットを分類"""
        subject = commit["subject"].lower()
        
        # プレフィックスパターンをチェック
        for pattern, category in self.commit_patterns.items():
            if subject.startswith(f"{pattern}:") or subject.startswith(f"{pattern}("):
                return category, self._clean_commit_message(commit["subject"])
        
        # キーワードベースの分類
        if any(keyword in subject for keyword in ["fix", "修正", "バグ", "bug"]):
            return "修正", self._clean_commit_message(commit["subject"])
        elif any(keyword in subject for keyword in ["feat", "add", "新機能", "追加"]):
            return "追加", self._clean_commit_message(commit["subject"])
        elif any(keyword in subject for keyword in ["remove", "delete", "削除"]):
            return "削除", self._clean_commit_message(commit["subject"])
        elif any(keyword in subject for keyword in ["security", "セキュリティ"]):
            return "セキュリティ", self._clean_commit_message(commit["subject"])
        else:
            return "変更", self._clean_commit_message(commit["subject"])

    def _clean_commit_message(self, message: str) -> str:
        """コミットメッセージをクリーンアップ"""
        # プレフィックスを削除
        for pattern in self.commit_patterns.keys():
            if message.lower().startswith(f"{pattern}:"):
                message = message[len(pattern)+1:].strip()
                break
            elif message.lower().startswith(f"{pattern}("):
                # feat(scope): message の形式
                paren_end = message.find(')')
                if paren_end != -1:
                    colon_pos = message.find(':', paren_end)
                    if colon_pos != -1:
                        message = message[colon_pos+1:].strip()
                break
        
        # 先頭を大文字に
        if message:
            message = message[0].upper() + message[1:]
        
        return message

    def get_pull_request_info(self, commit_hash: str) -> Optional[Dict]:
        """プルリクエスト情報を取得（GitHub CLI使用）"""
        try:
            # GitHub CLIでPR情報を取得
            result = self.run_command([
                "gh", "pr", "list", "--state", "merged", 
                "--search", f"sha:{commit_hash}",
                "--json", "number,title,url,author"
            ], check=False)
            
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                if prs:
                    return prs[0]
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            # GitHub CLIが利用できない場合は無視
            pass
        
        return None

    def generate_changelog_section(self, commits: List[Dict], version: str = "未リリース") -> str:
        """変更履歴セクションを生成"""
        self.logger.info(f"バージョン {version} の変更履歴を生成中...")
        
        # コミットを分類
        categories = {
            "追加": [],
            "変更": [],
            "修正": [],
            "削除": [],
            "非推奨": [],
            "セキュリティ": []
        }
        
        for commit in commits:
            category, message = self.classify_commit(commit)
            
            # プルリクエスト情報を取得
            pr_info = self.get_pull_request_info(commit["hash"])
            
            entry = {
                "message": message,
                "hash": commit["hash"][:7],
                "author": commit["author"],
                "pr": pr_info
            }
            
            categories[category].append(entry)
        
        # 変更履歴セクションを構築
        lines = []
        
        # バージョンヘッダー
        if version == "未リリース":
            lines.append(f"## [{version}]")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
            lines.append(f"## [{version}] - {date_str}")
        
        lines.append("")
        
        # 各カテゴリーを出力
        for category, entries in categories.items():
            if entries:
                lines.append(f"### {category}")
                lines.append("")
                
                for entry in entries:
                    line = f"- {entry['message']}"
                    
                    # プルリクエスト情報を追加
                    if entry["pr"]:
                        line += f" ([#{entry['pr']['number']}]({entry['pr']['url']}))"
                    
                    # コミットハッシュを追加
                    line += f" ({entry['hash']})"
                    
                    lines.append(line)
                
                lines.append("")
        
        # 空のカテゴリーがある場合は「なし」を追加
        for category in categories.keys():
            if not categories[category]:
                lines.append(f"### {category}")
                lines.append("")
                lines.append("- なし")
                lines.append("")
        
        return "\n".join(lines)

    def update_changelog_file(self, new_section: str, version: str = "未リリース") -> bool:
        """CHANGELOG.mdファイルを更新"""
        changelog_path = Path("CHANGELOG.md")
        
        try:
            if changelog_path.exists():
                with open(changelog_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                # 新しいCHANGELOG.mdを作成
                content = self._create_initial_changelog()
            
            # 新しいセクションを挿入
            if version == "未リリース":
                # [未リリース]セクションを更新
                pattern = r"## \[未リリース\].*?(?=## \[|\Z)"
                if re.search(pattern, content, re.DOTALL):
                    content = re.sub(pattern, new_section, content, flags=re.DOTALL)
                else:
                    # [未リリース]セクションが存在しない場合は追加
                    header_end = content.find("\n## [")
                    if header_end != -1:
                        content = content[:header_end] + "\n" + new_section + "\n" + content[header_end:]
                    else:
                        content += "\n" + new_section
            else:
                # 新しいバージョンセクションを追加
                unreleased_end = content.find("\n## [", content.find("## [未リリース]"))
                if unreleased_end != -1:
                    content = content[:unreleased_end] + "\n" + new_section + "\n" + content[unreleased_end:]
                else:
                    content += "\n" + new_section
            
            # ファイルに書き込み
            with open(changelog_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.logger.info(f"CHANGELOG.mdを更新しました: {changelog_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"CHANGELOG.md更新エラー: {e}")
            return False

    def _create_initial_changelog(self) -> str:
        """初期CHANGELOG.mdを作成"""
        return """# 変更履歴

Qt-Theme-Studioの変更履歴を記録します。

このプロジェクトは[Semantic Versioning](https://semver.org/lang/ja/)に従います。

## [未リリース]

### 追加
- なし

### 変更
- なし

### 修正
- なし

### 削除
- なし

### 非推奨
- なし

### セキュリティ
- なし

---

## 変更履歴の形式について

- **追加**: 新機能
- **変更**: 既存機能の変更
- **非推奨**: 将来削除される機能
- **削除**: 削除された機能
- **修正**: バグ修正
- **セキュリティ**: セキュリティ関連の修正
"""

    def generate_changelog(self, since_tag: Optional[str] = None, 
                          until_tag: Optional[str] = None,
                          version: str = "未リリース",
                          output_file: Optional[str] = None) -> bool:
        """変更履歴を生成"""
        self.logger.info("変更履歴生成を開始します")
        
        try:
            # コミット情報を取得
            commits = self.get_git_commits(since_tag, until_tag)
            
            if not commits:
                self.logger.warning("コミットが見つかりませんでした")
                return False
            
            # 変更履歴セクションを生成
            changelog_section = self.generate_changelog_section(commits, version)
            
            # 出力
            if output_file:
                # 指定されたファイルに出力
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(changelog_section)
                self.logger.info(f"変更履歴を {output_file} に出力しました")
            else:
                # CHANGELOG.mdを更新
                success = self.update_changelog_file(changelog_section, version)
                if not success:
                    return False
            
            self.logger.info("変更履歴生成が完了しました")
            return True
            
        except Exception as e:
            self.logger.error(f"変更履歴生成エラー: {e}")
            return False

    def preview_changelog(self, since_tag: Optional[str] = None,
                         until_tag: Optional[str] = None,
                         version: str = "未リリース") -> str:
        """変更履歴をプレビュー"""
        commits = self.get_git_commits(since_tag, until_tag)
        if not commits:
            return "コミットが見つかりませんでした"
        
        return self.generate_changelog_section(commits, version)


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="Qt-Theme-Studio 変更履歴自動生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 最新の変更履歴を生成
  python scripts/changelog_generator.py

  # 特定のタグ以降の変更履歴を生成
  python scripts/changelog_generator.py --since v1.0.0

  # 特定のバージョンの変更履歴を生成
  python scripts/changelog_generator.py --since v1.0.0 --version v1.1.0

  # プレビューのみ
  python scripts/changelog_generator.py --preview

  # ファイルに出力
  python scripts/changelog_generator.py --output changelog_preview.md
        """
    )
    
    parser.add_argument(
        "--since", 
        help="開始タグ（このタグ以降のコミットを含める）"
    )
    parser.add_argument(
        "--until", 
        help="終了タグ（このタグまでのコミットを含める）"
    )
    parser.add_argument(
        "--version", 
        default="未リリース",
        help="バージョン番号（デフォルト: 未リリース）"
    )
    parser.add_argument(
        "--output", 
        help="出力ファイル（指定しない場合はCHANGELOG.mdを更新）"
    )
    parser.add_argument(
        "--preview", 
        action="store_true",
        help="プレビューのみ（ファイルを更新しない）"
    )
    parser.add_argument(
        "--list-tags", 
        action="store_true",
        help="利用可能なタグ一覧を表示"
    )
    
    args = parser.parse_args()
    
    generator = ChangelogGenerator()
    
    try:
        if args.list_tags:
            # タグ一覧を表示
            tags = generator.get_git_tags()
            if tags:
                print("利用可能なタグ:")
                for tag in tags:
                    print(f"  {tag}")
            else:
                print("タグが見つかりませんでした")
            return
        
        if args.preview:
            # プレビューのみ
            changelog = generator.preview_changelog(args.since, args.until, args.version)
            print(changelog)
        else:
            # 変更履歴を生成
            success = generator.generate_changelog(
                args.since, args.until, args.version, args.output
            )
            
            if success:
                print("✅ 変更履歴の生成が完了しました")
                sys.exit(0)
            else:
                print("❌ 変更履歴の生成に失敗しました")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⏹️ 処理が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"💥 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()