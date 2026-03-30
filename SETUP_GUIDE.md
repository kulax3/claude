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

### 3-1. このリポジトリをPCに取得

```powershell
cd "$env:USERPROFILE\Documents"
git clone https://github.com/kulax3/claude.git
cd claude
```

### 3-2. 実行ポリシーの設定（初回のみ）

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3-3. セットアップ実行

```powershell
.\setup_env.ps1
```

これでタスクスケジューラに30分ごとの自動同期が登録される。

### 3-4. 手動で今すぐ同期

```powershell
powershell -File sync_box_obsidian.ps1 -Direction both
```

### 3-5. 同期確認

```powershell
# ログを見る
Get-Content "$env:USERPROFILE\AppData\Local\Logs\box-obsidian-sync.log" -Tail 20
```

---

## STEP 4｜スクリプト・設定をBoxにも共有する

スクリプトや `.claude\` の設定を社内メンバーとBoxで共有したい場合:

### 4-1. Boxに `scripts\` フォルダを作る

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\Box\scripts"
```

### 4-2. スクリプトをBoxにコピー

```powershell
$src  = "$env:USERPROFILE\Documents\claude"
$dest = "$env:USERPROFILE\Box\scripts"

Copy-Item "$src\sync_box_obsidian.ps1" $dest -Force
Copy-Item "$src\setup_env.ps1"         $dest -Force
Copy-Item "$src\CLAUDE.md"             $dest -Force
```

> **注意:** コピーはあくまで「配布用」。編集はgit側（`Documents\claude\`）で行う。

---

## STEP 5｜Obsidianのsharedフォルダ → Box同期の確認

`Documents\Obsidian\Work\shared\` にファイルを置くと、次の同期タイミングで `Box\shared\` にコピーされる。

```
shared\ に置く → 社内共有される
notes\  に置く → 自分のPCだけ（同期されない）
context\ に置く → Claude Codeが参照できる（同期されない）
```

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
