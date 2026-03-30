#!/bin/bash
# Box Drive <-> Obsidian (iCloud) 同期スクリプト
# 用途: 社内共有(Box) と Claude Code用ノート(Obsidian/iCloud) を同期する

set -euo pipefail

# ── 設定 ──────────────────────────────────────────────────────────────────────
BOX_DIR="${BOX_DIR:-$HOME/Library/CloudStorage/Box-Box}"
OBSIDIAN_DIR="${OBSIDIAN_DIR:-$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents}"
VAULT_NAME="${VAULT_NAME:-Work}"          # Obsidian vault 名
SHARED_FOLDER="${SHARED_FOLDER:-shared}"  # 同期対象フォルダ名

BOX_SHARED="$BOX_DIR/$SHARED_FOLDER"
OBS_SHARED="$OBSIDIAN_DIR/$VAULT_NAME/$SHARED_FOLDER"

# ── ログ ──────────────────────────────────────────────────────────────────────
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# ── チェック ──────────────────────────────────────────────────────────────────
check_dirs() {
    if [ ! -d "$BOX_DIR" ]; then
        echo "ERROR: Box Drive が見つかりません: $BOX_DIR"
        echo "  → Box Drive アプリをインストール・サインインしてください"
        exit 1
    fi
    if [ ! -d "$OBSIDIAN_DIR" ]; then
        echo "ERROR: Obsidian iCloud フォルダが見つかりません: $OBSIDIAN_DIR"
        echo "  → Obsidian アプリを起動し、iCloud vault を作成してください"
        exit 1
    fi
    mkdir -p "$BOX_SHARED" "$OBS_SHARED"
}

# ── 同期方向の選択 ─────────────────────────────────────────────────────────────
usage() {
    echo "Usage: $0 [box-to-obs | obs-to-box | both]"
    echo ""
    echo "  box-to-obs  Box -> Obsidian (社内共有ファイルをObsidianに取り込む)"
    echo "  obs-to-box  Obsidian -> Box (Obsidianのノートを社内共有に反映)"
    echo "  both        双方向同期 (rsync --update で新しい方を優先)"
    exit 1
}

DIRECTION="${1:-both}"

sync_box_to_obs() {
    log "Box -> Obsidian 同期開始"
    rsync -av --update --delete \
        --exclude=".DS_Store" \
        --exclude="*.tmp" \
        "$BOX_SHARED/" "$OBS_SHARED/"
    log "Box -> Obsidian 同期完了"
}

sync_obs_to_box() {
    log "Obsidian -> Box 同期開始"
    rsync -av --update --delete \
        --exclude=".DS_Store" \
        --exclude="*.tmp" \
        --exclude=".obsidian/" \
        "$OBS_SHARED/" "$BOX_SHARED/"
    log "Obsidian -> Box 同期完了"
}

# ── メイン ────────────────────────────────────────────────────────────────────
check_dirs

case "$DIRECTION" in
    box-to-obs) sync_box_to_obs ;;
    obs-to-box) sync_obs_to_box ;;
    both)
        sync_box_to_obs
        sync_obs_to_box
        ;;
    *) usage ;;
esac

log "完了"
