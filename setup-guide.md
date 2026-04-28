# ローカルに戻ったら実行するセットアップ手順

Claude Codeを本格活用するための10の準備。**上から順に実行**してください。

---

## Phase 1: 基本セットアップ（まず最初に）

### Step 1: ターミナル最適化

```
/terminal-setup
```
→ `Shift + Enter` で改行できるようになる

### Step 2: テーマ設定

```
/theme
```
→ ライト / ダーク / 色覚サポートから選択

### Step 3: ツール許可リストを設定

```
/allowed-tools
```
→ 毎回確認されるツールを事前に許可登録して承認の手間を削減

### Step 4: GitHubアプリのインストール

```
/install-github-app
```
→ ClaudeがPRレビューやコメントを自動で行えるようになる

### Step 5: 設定の確認・調整

```
/config
```
→ モデル選択（Sonnet / Opus）や各種オプションを一括設定

---

## Phase 2: スキルとエージェントの構築

### Step 6: Skill Creatorをインストール

```
/plugin
```
→ プラグイン一覧を開き、マーケットプレイスで「Skill Creator」を検索してインストール

以降は「こういうスキルを作りたい」と伝えるだけで、
Skill Creatorがテストケース生成や品質評価まで自動でやってくれる。

### Step 7: エージェントチームを構築

`~/.claude/agents/` ディレクトリにエージェントを配置する。
このリポジトリの `agents/` フォルダにテンプレートを用意済み → コピーして使う。

```bash
mkdir -p ~/.claude/agents/
cp agents/*.md ~/.claude/agents/
```

または `/agent` コマンドで新規作成もできる。

---

## Phase 3: リモートアクセス環境の構築（外出先から操作するために）

### Step 8: このリポジトリをローカルに取り込む

まずローカルPCでターミナルを開き、以下を実行する。

```bash
# すでにcloneしてある場合
cd ~/claude
git fetch origin claude/setup-dev-config-KYQd0
git checkout claude/setup-dev-config-KYQd0
git pull origin claude/setup-dev-config-KYQd0

# まだcloneしていない場合
git clone https://github.com/kulax3/claude.git ~/claude
cd ~/claude
git checkout claude/setup-dev-config-KYQd0
```

### Step 9: PCのスリープを完全に無効化する（常時起動）

外出先から接続するためにPCを常時起動状態にしておく。

**macOS の場合:**

```bash
# ① スリープ・ディスクスリープを無効化（電源接続時）
sudo pmset -c sleep 0 disksleep 0 hibernatemode 0

# ② 設定が反映されたか確認（sleep の値がすべて 0 になっていればOK）
pmset -g | grep -E "sleep|hibernate"
```

次にGUIからも設定する:
1. システム設定 → バッテリー（またはエネルギー）を開く
2. 「電源アダプタ」タブ → 「ディスプレイをオフにするまでの時間」を「しない」に設定
3. 「ハードディスクが可能な場合はスリープさせる」のチェックを外す

**Windows の場合:**

1. スタートメニュー → 設定 → システム → 電源とスリープ を開く
2. 「スリープ」の項目を「なし」に変更
3. 「画面をオフにする」も「なし」に変更

### Step 10: エージェントテンプレートをコピーする

このリポジトリに用意済みのエージェントをClaude Codeのホームに配置する。

```bash
# エージェント用ディレクトリを作成
mkdir -p ~/.claude/agents/

# テンプレートをコピー
cp ~/claude/agents/*.md ~/.claude/agents/

# コピーされたか確認
ls ~/.claude/agents/
```

### Step 11: Claude Codeを起動してリモートコントロールを有効化する

```bash
# ① Opusモデル + Effort High で起動
claude --model opus --effort high
```

起動したら、Claude Codeのチャット内で以下を実行:

```
/remote-control
```

2. QRコードが表示される
3. スマホのカメラアプリまたはQRコードリーダーで読み込む
4. スマホのブラウザでClaude Codeの画面が開けば接続成功

> セッションを閉じると接続が切れるため、**PCのターミナルはそのまま開いておく**。
> `claude --resume` で再接続した場合は `/remote-control` を再度実行する。

**使い分け（外出先での運用）:**

| ツール | 用途 |
|--------|------|
| リモートコントロール | 承認作業・細かい操作の確認 |
| Discord MCP | タスクの依頼・ファイルの送信 |

### Step 12: Discord MCPを接続する

スマホから画像・動画をDiscordにアップロードするだけで、Claude Codeに処理を依頼できるようになる。

**① Discordサーバーとボットを準備する:**

1. Discord公式サイト（discord.com）でアカウント作成・ログイン
2. 新しいサーバーを作成（個人用で問題ない）
3. Discord Developer Portal（discord.com/developers）でアプリケーションを作成
4. 「Bot」メニューでボットを作成 → トークンをコピーして控えておく
5. 「OAuth2 → URL Generator」でボットをサーバーに招待

**② Claude CodeにDiscord MCPを追加する:**

```bash
claude mcp add discord
```

プロンプトに従いボットトークンとチャンネルIDを入力する。

**③ 動作確認:**

Discordのサーバーに「テスト」と送信してClaude Codeが反応すれば完了。

詳細手順はClaude Codeに「Discord MCPを設定して」と依頼すれば自動で進められる。

---

## Phase 4: 高度な設定

### モデルとEffortの最適化

```bash
# Opusモデル + Effort High で起動（推奨）
claude --model opus --effort high

# 自動承認モード（慣れてから使う）
claude --dangerously-skip-permissions
```

**Effortの目安:**
- `high`: 日常使いのベストバランス（推奨）
- `max`: 精度最優先・動作は遅い

### ブラウザ操作ツールの導入

```bash
# Claude in Chrome（フラグを付けるだけで動く）
claude --chrome

# Playwright MCP（Chromeが不安定な場合の補完）
/plugin install playwright
```

### Obsidianでメモ管理

- マークダウンファイルをローカルに保存するため、Claude Codeが直接読み書きできる
- MCP設定不要でNotionより連携がシンプル
- タスク完了ごとにメモを蓄積しておくとナレッジが積み上がる

---

## 日常的な使い方のコツ

### 作業開始時の指示テンプレート

```
まずこのタスクについて考えて、計画（Plan）を立てて、
私の承認を得てから実行してください。

タスク: [ここに内容を記載]
```

### セッション再開

```bash
claude --resume    # 前回の会話を再開
claude --continue  # 前回の会話を継続
```

### 記憶させたいことを保存

チャット中に `#` を付けてメッセージを送ると CLAUDE.md に自動記録される。

---

## ショートカット早見表

| 操作 | 効果 |
|------|------|
| `Shift + Tab` | 編集の自動承認モード切替 |
| `Shift + Enter` | 改行（`/terminal-setup` 後に有効） |
| `Esc` | 動作を即停止（セッションは壊れない） |
| `Esc` × 2 | 履歴を遡る |
| `Ctrl + R` | 詳細出力・現在のコンテキスト確認 |
| `#` + メッセージ | CLAUDE.md に自動記録 |
| `!` + コマンド | 一時的にBashモードで実行 |
