# Box Drive <-> Obsidian (iCloud) 同期スクリプト (Windows版)
# 用途: 社内共有(Box) と Claude Code用ノート(Obsidian/iCloud) を同期する

param(
    [ValidateSet("box-to-obs", "obs-to-box", "both")]
    [string]$Direction = "both"
)

# ── 設定 ──────────────────────────────────────────────────────────────────────
$BoxDir      = if ($env:BOX_DIR)      { $env:BOX_DIR }      else { "$env:USERPROFILE\Box" }
$ICloudBase  = if ($env:ICLOUD_DIR)   { $env:ICLOUD_DIR }   else { "$env:USERPROFILE\Apple\iCloud Drive" }
$VaultName   = if ($env:VAULT_NAME)   { $env:VAULT_NAME }   else { "Work" }
$SharedFolder = if ($env:SHARED_FOLDER) { $env:SHARED_FOLDER } else { "shared" }

$ObsidianDir = "$ICloudBase\Obsidian\$VaultName"
$BoxShared   = "$BoxDir\$SharedFolder"
$ObsShared   = "$ObsidianDir\$SharedFolder"

# ── ログ ──────────────────────────────────────────────────────────────────────
function Log { param($msg); Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg" }

# ── チェック ──────────────────────────────────────────────────────────────────
function Check-Dirs {
    if (-not (Test-Path $BoxDir)) {
        Write-Error "Box Drive が見つかりません: $BoxDir`n  → Box Drive アプリをインストール・サインインしてください"
        exit 1
    }
    if (-not (Test-Path $ObsidianDir)) {
        Write-Error "Obsidian iCloud フォルダが見つかりません: $ObsidianDir`n  → iCloud for Windows をインストールし、Obsidian vault '$VaultName' を作成してください"
        exit 1
    }
    New-Item -ItemType Directory -Force -Path $BoxShared  | Out-Null
    New-Item -ItemType Directory -Force -Path $ObsShared  | Out-Null
}

# ── 同期 (robocopy) ───────────────────────────────────────────────────────────
# /MIR  : ミラーリング（削除も反映）
# /XF   : 除外ファイル
# /XD   : 除外フォルダ
# /NP   : 進捗パーセント非表示
# /LOG+ : ログ追記
$LogFile = "$env:USERPROFILE\AppData\Local\Logs\box-obsidian-sync.log"
New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

function Sync-BoxToObs {
    Log "Box -> Obsidian 同期開始"
    robocopy $BoxShared $ObsShared /MIR /XF "*.tmp" "desktop.ini" /XD ".tmp" /NP /LOG+:$LogFile
    Log "Box -> Obsidian 同期完了"
}

function Sync-ObsToBox {
    Log "Obsidian -> Box 同期開始"
    robocopy $ObsShared $BoxShared /MIR /XF "*.tmp" "desktop.ini" /XD ".obsidian" ".tmp" /NP /LOG+:$LogFile
    Log "Obsidian -> Box 同期完了"
}

# ── メイン ────────────────────────────────────────────────────────────────────
Check-Dirs

switch ($Direction) {
    "box-to-obs" { Sync-BoxToObs }
    "obs-to-box" { Sync-ObsToBox }
    "both"       { Sync-BoxToObs; Sync-ObsToBox }
}

Log "完了"
