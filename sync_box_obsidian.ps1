# Box Drive <-> Obsidian 同期スクリプト (Windows)

param(
    [ValidateSet("box-to-obs", "obs-to-box", "both")]
    [string]$Direction = "both"
)

# ── 設定 ──────────────────────────────────────────────────────────────────────
$BoxShared = if ($env:BOX_SHARED) { $env:BOX_SHARED } else { "$env:USERPROFILE\Box\shared" }
$ObsShared = if ($env:OBS_SHARED) { $env:OBS_SHARED } else { "$env:USERPROFILE\Documents\Obsidian\Work\shared" }

$LogFile = "$env:USERPROFILE\AppData\Local\Logs\box-obsidian-sync.log"

# ── ログ ──────────────────────────────────────────────────────────────────────
function Log { param($msg); Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg" }

# ── チェック ──────────────────────────────────────────────────────────────────
if (-not (Test-Path (Split-Path $BoxShared))) {
    Write-Error "Box Drive が見つかりません。Box Drive をインストール・サインインしてください。"
    exit 1
}
if (-not (Test-Path (Split-Path $ObsShared))) {
    Write-Error "Obsidian vault が見つかりません: $(Split-Path $ObsShared)`nsetup_env.ps1 を先に実行するか、パスを確認してください。"
    exit 1
}

New-Item -ItemType Directory -Force -Path $BoxShared | Out-Null
New-Item -ItemType Directory -Force -Path $ObsShared | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

# ── 同期 ──────────────────────────────────────────────────────────────────────
function Sync($From, $To, $Label) {
    Log "$Label 同期開始: $From -> $To"
    robocopy $From $To /MIR /XF "*.tmp" "desktop.ini" /XD ".obsidian" ".tmp" /NP /LOG+:$LogFile
    Log "$Label 同期完了"
}

switch ($Direction) {
    "box-to-obs" { Sync $BoxShared $ObsShared "Box -> Obsidian" }
    "obs-to-box" { Sync $ObsShared $BoxShared "Obsidian -> Box" }
    "both"       { Sync $BoxShared $ObsShared "Box -> Obsidian"; Sync $ObsShared $BoxShared "Obsidian -> Box" }
}
