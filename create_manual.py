import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# ---- 共通スタイル定義 ----
def header_fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def make_border():
    s = Side(style="thin", color="AAAAAA")
    return Border(left=s, right=s, top=s, bottom=s)

def set_header(ws, row, col, value, bg="2E75B6", fg="FFFFFF", size=11):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(bold=True, color=fg, size=size)
    c.fill = header_fill(bg)
    c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    c.border = make_border()
    return c

def set_cell(ws, row, col, value, bg=None, bold=False, wrap=True, indent=0):
    c = ws.cell(row=row, column=col, value=value)
    c.font = Font(bold=bold, size=10)
    c.alignment = Alignment(wrap_text=wrap, vertical="top", indent=indent)
    c.border = make_border()
    if bg:
        c.fill = header_fill(bg)
    return c

def set_section(ws, row, col_span, value, bg="D6E4F0"):
    c = ws.cell(row=row, column=1, value=value)
    c.font = Font(bold=True, size=10, color="1F4E79")
    c.fill = header_fill(bg)
    c.alignment = Alignment(vertical="center", indent=1)
    c.border = make_border()
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=col_span)

# ========================================================
# シート1: インストール & 初期設定
# ========================================================
ws1 = wb.active
ws1.title = "1.インストール・初期設定"
ws1.sheet_view.showGridLines = False
ws1.freeze_panes = "A2"

cols = ["手順", "操作内容", "PowerShellコマンド / 備考"]
widths = [6, 36, 62]
for i, (h, w) in enumerate(zip(cols, widths), 1):
    set_header(ws1, 1, i, h)
    ws1.column_dimensions[get_column_letter(i)].width = w
ws1.row_dimensions[1].height = 22

rows = [
    # (step, 内容, コマンド/備考)
    ("section", "■ 前提条件の確認", None),
    ("1", "Node.js (v18以上) のインストール確認",
     "node -v\n# v18.0.0 以上であること"),
    ("2", "npm の確認",
     "npm -v"),
    ("3", "Git のインストール確認",
     "git --version\n# インストールされていない場合は https://git-scm.com/ からDL"),
    ("section", "■ Claude Code のインストール", None),
    ("4", "Claude Code を npm でグローバルインストール",
     "npm install -g @anthropic-ai/claude-code"),
    ("5", "インストール確認",
     "claude --version"),
    ("6", "PATH が通っていない場合（PowerShell プロファイル編集）",
     '# プロファイルを開く\nnotepad $PROFILE\n\n# 以下を追記\n$env:PATH += ";$env:APPDATA\\npm"'),
    ("section", "■ 認証設定", None),
    ("7", "Claude Code を起動して認証",
     "claude\n# ブラウザが開くので Anthropic アカウントでログイン"),
    ("8", "API キーで認証する場合",
     '$env:ANTHROPIC_API_KEY = "sk-ant-xxxx"\nclaude'),
    ("9", "API キーを恒久的に設定（PowerShell プロファイルに追記）",
     '# notepad $PROFILE を開き以下を追記\n$env:ANTHROPIC_API_KEY = "sk-ant-xxxx"'),
    ("section", "■ 動作確認", None),
    ("10", "ヘルプ表示",
     "claude --help"),
    ("11", "バージョン確認",
     "claude --version"),
    ("12", "作業ディレクトリで起動",
     "cd C:\\MyProject\nclaude"),
]

r = 2
for row in rows:
    if row[0] == "section":
        set_section(ws1, r, 3, row[1])
        ws1.row_dimensions[r].height = 18
        r += 1
    else:
        set_cell(ws1, r, 1, row[0], bold=True, wrap=False)
        set_cell(ws1, r, 2, row[1])
        set_cell(ws1, r, 3, row[2], bg="F5F5F5")
        ws1.row_dimensions[r].height = max(15 * row[2].count("\n") + 15, 30) if row[2] else 30
        r += 1


# ========================================================
# シート2: Git 操作マニュアル（手厚く）
# ========================================================
ws2 = wb.create_sheet("2.Git操作（詳細）")
ws2.sheet_view.showGridLines = False
ws2.freeze_panes = "A2"

cols2 = ["カテゴリ", "操作", "PowerShellコマンド", "説明・注意点"]
widths2 = [18, 28, 46, 46]
for i, (h, w) in enumerate(zip(cols2, widths2), 1):
    set_header(ws2, 1, i, h)
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.row_dimensions[1].height = 22

git_rows = [
    ("section4", "■ 初期設定"),
    ("初期設定", "ユーザー名を設定",
     'git config --global user.name "Your Name"',
     "全リポジトリ共通の表示名"),
    ("初期設定", "メールアドレスを設定",
     'git config --global user.email "you@example.com"',
     "コミットに紐づくメールアドレス"),
    ("初期設定", "デフォルトブランチを main に設定",
     "git config --global init.defaultBranch main",
     "git init 時のデフォルトブランチ名"),
    ("初期設定", "改行コードの自動変換（Windows推奨）",
     "git config --global core.autocrlf true",
     "Windows↔Linux 間の CRLF/LF 差異を自動吸収"),
    ("初期設定", "設定確認",
     "git config --list",
     "現在の全設定を一覧表示"),

    ("section4", "■ リポジトリ操作"),
    ("リポジトリ", "新規リポジトリを作成",
     "git init",
     "カレントディレクトリを Git 管理下に置く"),
    ("リポジトリ", "リモートをクローン",
     "git clone <URL>",
     "例: git clone https://github.com/user/repo.git"),
    ("リポジトリ", "リモートを確認",
     "git remote -v",
     "fetch / push 先の URL を表示"),
    ("リポジトリ", "リモートを追加",
     "git remote add origin <URL>",
     "origin という名前でリモートを登録"),
    ("リポジトリ", "リモート URL を変更",
     "git remote set-url origin <新URL>",
     "SSH → HTTPS 切り替えなどに使用"),

    ("section4", "■ ブランチ操作"),
    ("ブランチ", "ブランチ一覧（ローカル）",
     "git branch",
     "* が現在のブランチ"),
    ("ブランチ", "ブランチ一覧（リモート含む）",
     "git branch -a",
     "remotes/origin/xxx がリモートブランチ"),
    ("ブランチ", "新規ブランチを作成して切り替え",
     "git checkout -b <branch-name>",
     "例: git checkout -b feature/my-feature"),
    ("ブランチ", "既存ブランチに切り替え",
     "git checkout <branch-name>",
     ""),
    ("ブランチ", "ブランチ名を変更（ローカル）",
     "git branch -m <旧名> <新名>",
     ""),
    ("ブランチ", "ローカルブランチを削除",
     "git branch -d <branch-name>",
     "-D で強制削除（マージ未済でも削除）"),
    ("ブランチ", "リモートブランチを削除",
     "git push origin --delete <branch-name>",
     "注意: チームで共有しているブランチは要確認"),

    ("section4", "■ 変更の確認"),
    ("確認", "状態確認",
     "git status",
     "変更済・未追跡・ステージ済ファイルを表示"),
    ("確認", "差分確認（ワーク vs インデックス）",
     "git diff",
     "ステージ前の変更を確認"),
    ("確認", "差分確認（インデックス vs HEAD）",
     "git diff --staged",
     "コミット前の変更を確認"),
    ("確認", "コミット履歴（1行表示）",
     "git log --oneline",
     "簡潔に履歴を確認"),
    ("確認", "コミット履歴（グラフ付き）",
     "git log --oneline --graph --all",
     "ブランチ分岐が視覚的に確認できる"),
    ("確認", "特定ファイルの変更履歴",
     "git log --follow -p <ファイルパス>",
     "ファイルのリネームをまたいで追跡"),

    ("section4", "■ ステージング & コミット"),
    ("コミット", "ファイルをステージ（個別）",
     "git add <ファイルパス>",
     "例: git add main.py"),
    ("コミット", "全変更をステージ",
     "git add .",
     "注意: .gitignore で不要ファイルを除外しておく"),
    ("コミット", "ステージを取り消す",
     "git restore --staged <ファイルパス>",
     "コミットせずにステージを外す"),
    ("コミット", "コミット",
     'git commit -m "変更内容の説明"',
     "メッセージは変更理由が伝わる内容に"),
    ("コミット", "空コミット（CI トリガー等）",
     'git commit --allow-empty -m "trigger CI"',
     "ファイル変更なしでコミットを作成"),
    ("コミット", "直前のコミットメッセージを修正",
     'git commit --amend -m "新しいメッセージ"',
     "⚠ プッシュ済みのコミットに使うと履歴が diverge する"),

    ("section4", "■ プッシュ & フェッチ & プル"),
    ("リモート同期", "初回プッシュ（上流ブランチを設定）",
     "git push -u origin <branch-name>",
     "-u で以降は git push だけで済む"),
    ("リモート同期", "通常プッシュ",
     "git push",
     "上流ブランチが設定済みの場合"),
    ("リモート同期", "強制プッシュ（注意）",
     "git push --force-with-lease",
     "⚠ 他者の変更を上書きしないよう --force-with-lease を使う\n  --force は原則禁止"),
    ("リモート同期", "リモートの変更を取得（マージしない）",
     "git fetch origin",
     "ローカルブランチに影響なく最新を確認できる"),
    ("リモート同期", "特定ブランチのみフェッチ",
     "git fetch origin <branch-name>",
     ""),
    ("リモート同期", "フェッチ＋マージ",
     "git pull origin <branch-name>",
     "git fetch + git merge の短縮形"),
    ("リモート同期", "リベース形式でプル",
     "git pull --rebase origin <branch-name>",
     "マージコミットを作らずに最新を取り込む"),

    ("section4", "■ マージ & リベース"),
    ("統合", "ブランチをマージ",
     "git merge <branch-name>",
     "カレントブランチに指定ブランチを取り込む"),
    ("統合", "Fast-forward を禁止してマージ",
     "git merge --no-ff <branch-name>",
     "マージコミットを必ず作成する（履歴が明確）"),
    ("統合", "リベース",
     "git rebase <branch-name>",
     "コミット履歴を直線に整理する\n⚠ 共有ブランチへのリベースは禁止"),
    ("統合", "コンフリクト解消後に続行",
     "git rebase --continue",
     "コンフリクト修正・git add の後に実行"),
    ("統合", "リベースを中止",
     "git rebase --abort",
     "リベース前の状態に戻る"),

    ("section4", "■ 取り消し操作"),
    ("取り消し", "ワーク変更を破棄（ファイル単位）",
     "git restore <ファイルパス>",
     "⚠ 未コミットの変更は復元不可"),
    ("取り消し", "直前のコミットを取り消し（変更は残す）",
     "git reset HEAD~1",
     "コミットのみ取り消し。変更はワークに残る"),
    ("取り消し", "直前のコミットを完全に取り消し",
     "git reset --hard HEAD~1",
     "⚠ 変更も消える。プッシュ済みには使わない"),
    ("取り消し", "コミットを打ち消す新コミットを作成",
     "git revert <commit-hash>",
     "プッシュ済みの変更を安全に取り消す推奨方法"),
    ("取り消し", "変更を一時退避",
     "git stash",
     "ブランチ切り替え前に未コミット変更を退避"),
    ("取り消し", "退避した変更を戻す",
     "git stash pop",
     "最新のスタッシュを適用して削除"),
    ("取り消し", "スタッシュ一覧",
     "git stash list",
     "stash@{0} が最新"),

    ("section4", "■ タグ操作"),
    ("タグ", "タグを作成（軽量）",
     "git tag v1.0.0",
     ""),
    ("タグ", "タグを作成（注釈付き・推奨）",
     'git tag -a v1.0.0 -m "Release v1.0.0"',
     "リリース管理に推奨"),
    ("タグ", "タグをプッシュ",
     "git push origin v1.0.0",
     "git push はタグを自動プッシュしない"),
    ("タグ", "全タグをプッシュ",
     "git push origin --tags",
     ""),

    ("section4", "■ トラブルシューティング"),
    ("トラブル", "リモートとローカルが diverge した場合",
     "git pull --rebase origin <branch-name>",
     "コンフリクトがあれば解消 → git rebase --continue"),
    ("トラブル", "誤って add したファイルを除外",
     "git restore --staged <ファイル>",
     ""),
    ("トラブル", "コミット履歴を綺麗にしたい",
     "git rebase -i HEAD~<n>",
     "直近 n 件のコミットをまとめる (squash)\n⚠ プッシュ済みには使わない"),
    ("トラブル", "リモートで削除されたブランチをローカルから掃除",
     "git fetch --prune",
     "git branch -a で残っているゴーストブランチを削除"),
    ("トラブル", "特定ファイルを Git 管理から外す",
     "git rm --cached <ファイル>",
     ".gitignore に追加してからこのコマンドを実行"),
    ("トラブル", "HTTP 認証エラー (403) の場合",
     "# 認証情報を再設定\ngit config --global credential.helper manager",
     "Windows では Git Credential Manager が推奨"),
]

r2 = 2
for row in git_rows:
    if row[0] == "section4":
        set_section(ws2, r2, 4, row[1])
        ws2.row_dimensions[r2].height = 18
        r2 += 1
    else:
        cat, op, cmd, note = row
        set_cell(ws2, r2, 1, cat, bg="EBF3FB", bold=True)
        set_cell(ws2, r2, 2, op)
        set_cell(ws2, r2, 3, cmd, bg="F0F4F8")
        set_cell(ws2, r2, 4, note)
        line_count = max(cmd.count("\n"), note.count("\n")) + 1
        ws2.row_dimensions[r2].height = max(line_count * 14 + 8, 30)
        r2 += 1


# ========================================================
# シート3: Claude Code でのファイル操作
# ========================================================
ws3 = wb.create_sheet("3.Claudeファイル操作")
ws3.sheet_view.showGridLines = False
ws3.freeze_panes = "A2"

cols3 = ["操作", "Claude への指示例", "Claude が実行すること", "備考"]
widths3 = [22, 38, 38, 32]
for i, (h, w) in enumerate(zip(cols3, widths3), 1):
    set_header(ws3, 1, i, h)
    ws3.column_dimensions[get_column_letter(i)].width = w
ws3.row_dimensions[1].height = 22

file_rows = [
    ("section3", "■ ファイル作成・編集"),
    ("新規ファイル作成",
     '"hello.txt を作って、中に「動いた」と書いて"',
     "Write ツールでファイルを作成し内容を書き込む",
     "日本語指示でOK"),
    ("ファイル編集（部分）",
     '"main.py の hello_world 関数に引数 name を追加して"',
     "Read → Edit ツールで該当箇所だけ変更",
     ""),
    ("ファイル内容確認",
     '"main.py の内容を見せて"',
     "Read ツールでファイルを読み込んで表示",
     ""),
    ("ファイル削除",
     '"temp.py を削除して"',
     "Bash で rm を実行",
     "復元不可のため確認が入ることがある"),
    ("section3", "■ コード生成"),
    ("関数追加",
     '"main ファイルに hello world 関数を追加して"',
     "対象ファイルを Read してから Edit で追記",
     "既存コードを確認してから変更"),
    ("クラス作成",
     '"User クラスを models.py に作って"',
     "Write または Edit でクラスを生成",
     ""),
    ("テスト作成",
     '"hello_world のテストを test_main.py に書いて"',
     "Write でテストファイルを生成",
     ""),
    ("section3", "■ Git 操作（Claude 経由）"),
    ("コミット",
     '"変更をコミットして"',
     "git add → git commit を Bash で実行",
     "コミットメッセージも自動生成"),
    ("ブランチ作成＋プッシュ",
     '"feature ブランチを作ってプッシュして"',
     "git checkout -b → git push -u を実行",
     ""),
    ("状態確認",
     '"git の状態を教えて"',
     "git status / git log を実行して結果を説明",
     ""),
    ("section3", "■ PowerShell での操作"),
    ("Claude Code 起動",
     "PowerShell でプロジェクトフォルダへ移動して claude を実行",
     "インタラクティブセッション開始",
     "cd C:\\MyProject && claude"),
    ("ワンショット実行",
     'claude "main.py を読んでバグを探して"',
     "Claude が分析して結果を返す（非対話型）',",
     "--print オプションで出力のみ"),
    ("ファイルを渡す",
     'Get-Content main.py | claude "このコードを改善して"',
     "パイプ経由でコードを渡して処理",
     ""),
]

r3 = 2
for row in file_rows:
    if row[0] == "section3":
        set_section(ws3, r3, 4, row[1])
        ws3.row_dimensions[r3].height = 18
        r3 += 1
    else:
        op, inst, action, note = row
        set_cell(ws3, r3, 1, op, bold=True, bg="EBF3FB")
        set_cell(ws3, r3, 2, inst)
        set_cell(ws3, r3, 3, action, bg="F0F4F8")
        set_cell(ws3, r3, 4, note)
        ws3.row_dimensions[r3].height = 36
        r3 += 1


# ========================================================
# シート4: クイックリファレンス（一覧）
# ========================================================
ws4 = wb.create_sheet("4.クイックリファレンス")
ws4.sheet_view.showGridLines = False

set_header(ws4, 1, 1, "よく使う Git コマンド — クイックリファレンス", bg="1F4E79", size=13)
ws4.merge_cells("A1:C1")
ws4.row_dimensions[1].height = 28
ws4.column_dimensions["A"].width = 28
ws4.column_dimensions["B"].width = 50
ws4.column_dimensions["C"].width = 38

set_header(ws4, 2, 1, "目的", bg="2E75B6")
set_header(ws4, 2, 2, "コマンド", bg="2E75B6")
set_header(ws4, 2, 3, "メモ", bg="2E75B6")

qr = [
    ("リポジトリ初期化",          "git init",                                ""),
    ("クローン",                   "git clone <URL>",                         ""),
    ("状態確認",                   "git status",                              "毎作業前に実行"),
    ("差分確認",                   "git diff",                                ""),
    ("ステージ（個別）",           "git add <file>",                          ""),
    ("ステージ（全体）",           "git add .",                               ""),
    ("コミット",                   'git commit -m "message"',                 ""),
    ("ブランチ作成＋切替",         "git checkout -b <branch>",                ""),
    ("ブランチ切替",               "git checkout <branch>",                   ""),
    ("初回プッシュ",               "git push -u origin <branch>",             "上流ブランチを設定"),
    ("プッシュ",                   "git push",                                ""),
    ("フェッチ",                   "git fetch origin",                        "マージしない"),
    ("プル（マージ）",             "git pull origin <branch>",                ""),
    ("プル（リベース）",           "git pull --rebase origin <branch>",       "履歴を綺麗に"),
    ("ブランチ一覧",               "git branch -a",                           ""),
    ("ログ（1行）",                "git log --oneline",                       ""),
    ("ログ（グラフ）",             "git log --oneline --graph --all",         ""),
    ("コミット取消（変更残す）",   "git reset HEAD~1",                        ""),
    ("コミット打ち消し",           "git revert <hash>",                       "プッシュ済みに使用"),
    ("変更退避",                   "git stash",                               ""),
    ("退避復元",                   "git stash pop",                           ""),
    ("タグ作成（注釈付き）",       'git tag -a v1.0.0 -m "msg"',             ""),
    ("タグプッシュ",               "git push origin v1.0.0",                  ""),
    ("削除ブランチ掃除",           "git fetch --prune",                       ""),
]

for i, (purpose, cmd, memo) in enumerate(qr, 3):
    bg = "F2F7FC" if i % 2 == 0 else None
    set_cell(ws4, i, 1, purpose, bg=bg, bold=True)
    set_cell(ws4, i, 2, cmd, bg="F5F5F5" if not bg else "EAEAEA")
    set_cell(ws4, i, 3, memo, bg=bg)
    ws4.row_dimensions[i].height = 22

output_path = "/home/user/claude/ClaudeCode_Manual.xlsx"
wb.save(output_path)
print(f"saved: {output_path}")
