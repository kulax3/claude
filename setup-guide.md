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

### Step 8: PCのスリープを無効化（常時起動）

**macOS の場合:**
```bash
# スリープ無効化（電源接続時）
sudo pmset -c sleep 0 disksleep 0

# 確認
pmset -g | grep sleep
```

システム設定 → バッテリー → 「電源アダプタ接続時はディスプレイをオフにしない」もチェック。

**Windows の場合:**
- 設定 → システム → 電源とスリープ → すべて「なし」に設定

### Step 9: リモートコントロールを設定

Claude Codeセッションを起動したまま以下を実行：

```
/remote-control
```

→ QRコードが表示されるのでスマホで読み込む  
→ セッションを切らなければずっとスマホから操作できる

**使い分け:**
| ツール | 用途 |
|--------|------|
| リモートコントロール | 承認作業・細かい操作の確認 |
| Discord MCP | タスクの依頼・一般的なやり取り |

### Step 10: Discord MCPを接続

スマホから画像・動画をアップロードしてそのまま処理を依頼できるようになる。

```bash
# Discord MCPをインストール
claude mcp add discord
```

詳細な設定手順はこちら（Claude Codeに「Discord MCPを設定して」と依頼すれば自動で進められる）:
https://github.com/anthropics/claude-plugins-official/blob/main/external_plugins/discord/README.md

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
