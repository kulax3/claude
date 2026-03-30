#!/bin/bash
# 初回セットアップスクリプト
# Box Drive / Obsidian(iCloud) / Claude Code 連携環境を構築する

set -euo pipefail

echo "=== ファイル同期環境セットアップ ==="
echo ""

# ── 設定値 ────────────────────────────────────────────────────────────────────
BOX_DIR="$HOME/Library/CloudStorage/Box-Box"
OBSIDIAN_ICLOUD="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents"
VAULT_NAME="Work"
SHARED_FOLDER="shared"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── 1. Box Drive 確認 ─────────────────────────────────────────────────────────
echo "【1/4】Box Drive の確認"
if [ -d "$BOX_DIR" ]; then
    echo "  ✓ Box Drive: $BOX_DIR"
else
    echo "  ✗ Box Drive が見つかりません"
    echo "    → https://www.box.com/ja-jp/resources/downloads から"
    echo "      Box Drive をインストールしてサインインしてください"
    echo ""
fi

# ── 2. Obsidian iCloud Vault 確認 ─────────────────────────────────────────────
echo "【2/4】Obsidian iCloud Vault の確認"
VAULT_PATH="$OBSIDIAN_ICLOUD/$VAULT_NAME"
if [ -d "$VAULT_PATH" ]; then
    echo "  ✓ Obsidian vault: $VAULT_PATH"
else
    echo "  ✗ Obsidian vault が見つかりません: $VAULT_PATH"
    echo "    → Obsidian を起動して iCloud 上に '$VAULT_NAME' という名前の"
    echo "      vault を作成してください"
    echo "    → または VAULT_NAME 変数を変更してください"
    echo ""
fi

# ── 3. 同期フォルダ作成 ───────────────────────────────────────────────────────
echo "【3/4】同期フォルダの作成"
if [ -d "$BOX_DIR" ] && [ -d "$VAULT_PATH" ]; then
    mkdir -p "$BOX_DIR/$SHARED_FOLDER"
    mkdir -p "$VAULT_PATH/$SHARED_FOLDER"
    echo "  ✓ Box:      $BOX_DIR/$SHARED_FOLDER"
    echo "  ✓ Obsidian: $VAULT_PATH/$SHARED_FOLDER"
else
    echo "  スキップ (Box または Obsidian vault が未準備)"
fi

# ── 4. launchd による自動同期の登録 ──────────────────────────────────────────
echo "【4/4】自動同期スケジュールの登録 (30分ごと)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.user.box-obsidian-sync.plist"
SYNC_SCRIPT="$REPO_DIR/sync_box_obsidian.sh"

chmod +x "$SYNC_SCRIPT"

cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.box-obsidian-sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${SYNC_SCRIPT}</string>
        <string>both</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${HOME}/Library/Logs/box-obsidian-sync.log</string>
    <key>StandardErrorPath</key>
    <string>${HOME}/Library/Logs/box-obsidian-sync.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>VAULT_NAME</key>
        <string>${VAULT_NAME}</string>
        <key>SHARED_FOLDER</key>
        <string>${SHARED_FOLDER}</string>
    </dict>
</dict>
</plist>
PLIST

# すでにロード済みなら一度アンロード
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"
echo "  ✓ 登録完了: $PLIST_PATH"
echo "  ✓ ログ: ~/Library/Logs/box-obsidian-sync.log"

echo ""
echo "=== セットアップ完了 ==="
echo ""
echo "手動で今すぐ同期したい場合:"
echo "  bash $SYNC_SCRIPT both"
echo ""
echo "自動同期を停止したい場合:"
echo "  launchctl unload $PLIST_PATH"
