# 環境構築 手順書

## 全体像

```
iPhone (Obsidian Mobile)
  ↕ Dropbox (任意)
Obsidian\Work\          ← データ置き場（メイン）
  shared\               ← Boxと同期するフォルダ
  context\              ← Claude Codeに渡すメモ
  ↕ sync_box_obsidian.ps1
Box\shared\             ← 社内共有
  scripts\              ← スクリプト・設定も共有

claude\ (git)           ← スクリプト・設定指示の管理
```

---

## STEP 1｜アプリのインストール

### 1-1. Box Drive
1. https://www.box.com/ja-jp/resources/downloads を開く
2. 「Box Drive」をダウンロード・インストール
3. サインインする
4. インストール後、`C:\Users\<あなたのユーザー名>\Box\` が作られる

### 1-2. Obsidian
1. https://obsidian.md を開く
2. 「Download」→ Windows版をインストール
3. 起動 → 「Create new vault」
4. Vault name: `Work`
5. Location: `C:\Users\<あなたのユーザー名>\Documents\Obsidian\`
6. 「Create」

### 1-3. Git（初めての場合）
1. https://git-scm.com からインストール
2. インストール中の選択肢はすべてデフォルトでOK
3. インストール後、PowerShellを開いて確認:
   ```powershell
   git --version
   # git version 2.x.x と表示されればOK
   ```

---

## STEP 2｜Obsidianのフォルダ構成を作る

PowerShellを開いて実行:

```powershell
$vault = "$env:USERPROFILE\Documents\Obsidian\Work"

New-Item -ItemType Directory -Force "$vault\shared"   # Boxと同期するフォルダ
New-Item -ItemType Directory -Force "$vault\context"  # Claude Codeに渡すメモ
New-Item -ItemType Directory -Force "$vault\notes"    # 個人メモ（同期しない）
```

Obsidianを開くと左側のパネルにフォルダが表示される。

---

## STEP 3｜同期スクリプトを設定・実行する

### 3-1. このリポジトリをPCに取得（git clone）

PowerShellを開いて以下を実行:

```powershell
cd "$env:USERPROFILE\Documents"
git clone https://github.com/kulax3/claude.git
cd claude
```

**何が起きているか:**
- `git clone` = GitHubにあるスクリプト一式をPCにダウンロードする
- 実行後、`Documents\claude\` フォルダが作られ、中にスクリプトが入る

```
Documents\claude\
  sync_box_obsidian.ps1   ← 同期スクリプト
  setup_env.ps1           ← セットアップスクリプト
  CLAUDE.md               ← Claude Codeへの指示書
  SETUP_GUIDE.md          ← この手順書
```

### 3-2. 実行ポリシーの設定（初回のみ）

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**何が起きているか:**
Windowsはデフォルトで外部から取得したスクリプトの実行をブロックしている。
この設定で「自分のユーザーに限りスクリプトを実行可能」にする。
`Y` を押してEnter。

### 3-3. セットアップ実行

```powershell
.\setup_env.ps1
```

**何が起きているか（内部でやっていること）:**
1. Box Drive が存在するか確認
2. Obsidian vault が存在するか確認
3. `shared\` フォルダを両方に作成
4. Windowsのタスクスケジューラに「30分ごとに sync_box_obsidian.ps1 を実行」を登録

### 3-4. タスクスケジューラの登録確認

```powershell
Get-ScheduledTask -TaskName "BoxObsidianSync" | Select-Object TaskName, State
```

`State: Ready` と表示されれば登録成功。

タスクスケジューラの画面で確認したい場合:
1. スタートメニューで「タスクスケジューラ」を検索して開く
2. 左パネル「タスク スケジューラ ライブラリ」をクリック
3. 一覧に `BoxObsidianSync` があればOK

### 3-5. 手動で今すぐ同期してみる

```powershell
powershell -File "$env:USERPROFILE\Documents\claude\sync_box_obsidian.ps1" -Direction both
```

### 3-6. ログで結果を確認

```powershell
Get-Content "$env:USERPROFILE\AppData\Local\Logs\box-obsidian-sync.log" -Tail 20
```

正常時はこのような出力が表示される:
```
[2025-01-01 10:00:00] Box -> Obsidian 同期開始: ...
[2025-01-01 10:00:01] Box -> Obsidian 同期完了
[2025-01-01 10:00:01] Obsidian -> Box 同期開始: ...
[2025-01-01 10:00:02] Obsidian -> Box 同期完了
[2025-01-01 10:00:02] スクリプト -> Box\scripts\ コピー完了
```

---

## STEP 4｜スクリプト・設定をBoxに自動共有する

**手動コピーは不要。** 同期スクリプト（sync_box_obsidian.ps1）を実行するたびに、スクリプト類が `Box\scripts\` に自動でコピーされる仕組みになっている。

```
Documents\claude\          →（同期のたびに自動コピー）→    Box\scripts\
  sync_box_obsidian.ps1                                      sync_box_obsidian.ps1
  setup_env.ps1                                              setup_env.ps1
  CLAUDE.md                                                  CLAUDE.md
  SETUP_GUIDE.md                                             SETUP_GUIDE.md
```

**社内メンバーがBoxからスクリプトを使う手順:**
1. `Box\scripts\` フォルダを開く
2. `setup_env.ps1` を自分のPCの適当な場所にコピー
3. STEP 3-2〜3-3 と同じ手順でセットアップ

> **編集は必ずgit側（`Documents\claude\`）で行うこと。**
> Box側のファイルは次の同期で上書きされるため、Box側を直接編集しても消える。

---

## STEP 5｜動作確認：sharedフォルダの同期をテストする

実際にファイルを置いて同期されるか確認する。

### 5-1. テストファイルをObsidianのsharedに置く

```powershell
# テスト用ファイルを作成
"テスト" | Out-File "$env:USERPROFILE\Documents\Obsidian\Work\shared\test.md"
```

またはObsidianアプリで `shared\` フォルダに新規ノートを作っても同じ。

### 5-2. 同期を実行

```powershell
powershell -File "$env:USERPROFILE\Documents\claude\sync_box_obsidian.ps1" -Direction obs-to-box
```

### 5-3. Boxに反映されたか確認

```powershell
Test-Path "$env:USERPROFILE\Box\shared\test.md"
# True と表示されれば成功
```

エクスプローラーで `Box\shared\` を開いて `test.md` が存在することを目で確認してもよい。

### 5-4. フォルダ別の動作まとめ

| フォルダ | Boxと同期 | 社内共有 | Claude Code参照 |
|----------|-----------|----------|-----------------|
| `shared\` | される | される | できる（パス指定） |
| `notes\` | されない | されない | できる（パス指定） |
| `context\` | されない | されない | できる（パス指定） |

---

## STEP 6｜基本的なgit操作

### 毎日の流れ

```powershell
cd "$env:USERPROFILE\Documents\claude"

# 現在の状態を確認
git status

# 変更したファイルを記録する
git add CLAUDE.md                    # ファイルを指定して追加
git commit -m "CLAUDE.mdを更新"      # 変更内容をひと言で書く
git push                             # GitHubに送る
```

### よく使うコマンド

```powershell
git status          # 何が変わったか確認
git log --oneline   # 変更履歴を一覧表示
git diff            # 変更の中身を表示
git pull            # GitHubから最新を取得
```

### 間違えたとき

```powershell
# 直前のcommitを取り消す（ファイルの変更は残る）
git reset HEAD~1

# ファイルの変更を元に戻す
git checkout -- ファイル名
```

---

## STEP 7｜（任意）iPhoneとDropboxで同期

> iCloudよりDropboxのほうがObsidianとの相性が安定している。

### 7-1. Dropboxのインストール（Windows）
1. https://www.dropbox.com からインストール
2. サインイン後、`C:\Users\<ユーザー名>\Dropbox\` が作られる

### 7-2. Obsidian vaultをDropboxに移動

```powershell
# 現在のvaultをDropboxに移動
Move-Item "$env:USERPROFILE\Documents\Obsidian\Work" "$env:USERPROFILE\Dropbox\Obsidian\Work"
```

### 7-3. Obsidianで新しいvaultのパスを設定
1. Obsidianを開く
2. 「Open folder as vault」
3. `C:\Users\<ユーザー名>\Dropbox\Obsidian\Work` を選択

### 7-4. sync_box_obsidian.ps1 のパスを更新

`setup_env.ps1` の以下の行を変更:

```powershell
# 変更前
$ObsVaultPath = "$env:USERPROFILE\Documents\Obsidian\Work"

# 変更後
$ObsVaultPath = "$env:USERPROFILE\Dropbox\Obsidian\Work"
```

変更後、再度セットアップを実行:
```powershell
.\setup_env.ps1
```

### 7-5. iPhoneの設定
1. App StoreでObsidianをインストール
2. 起動 → 「Open vault from Dropbox」
3. `Obsidian\Work` を選択

これでiPhone ↔ Dropbox ↔ Windows が自動同期される。

---

## トラブルシューティング

| 症状 | 確認すること |
|------|------------|
| 同期されない | Box Driveがサインインされているか |
| スクリプトが動かない | `Set-ExecutionPolicy` を実行したか |
| gitが使えない | `git --version` でインストール確認 |
| Obsidianでフォルダが見えない | Obsidianの左パネルを更新（F5） |
