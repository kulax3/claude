# 初回セットアップスクリプト (Windows版)
# Box Drive / Obsidian(iCloud) / Claude Code 連携環境を構築する
# ※ 管理者権限不要（タスクスケジューラはユーザーレベルで登録）

$BoxDir       = "$env:USERPROFILE\Box"
$ICloudBase   = "$env:USERPROFILE\Apple\iCloud Drive"
$VaultName    = "Work"
$SharedFolder = "shared"
$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$SyncScript   = "$ScriptDir\sync_box_obsidian.ps1"

Write-Host "=== ファイル同期環境セットアップ ===" -ForegroundColor Cyan
Write-Host ""

# ── 1. Box Drive 確認 ─────────────────────────────────────────────────────────
Write-Host "【1/4】Box Drive の確認"
if (Test-Path $BoxDir) {
    Write-Host "  OK Box Drive: $BoxDir" -ForegroundColor Green
} else {
    Write-Host "  NG Box Drive が見つかりません" -ForegroundColor Red
    Write-Host "     → https://www.box.com/ja-jp/resources/downloads から"
    Write-Host "       Box Drive をインストールしてサインインしてください"
    Write-Host "     → デフォルトパス: $BoxDir"
}

# ── 2. iCloud / Obsidian Vault 確認 ──────────────────────────────────────────
Write-Host ""
Write-Host "【2/4】Obsidian iCloud Vault の確認"
$VaultPath = "$ICloudBase\Obsidian\$VaultName"
if (Test-Path $VaultPath) {
    Write-Host "  OK Obsidian vault: $VaultPath" -ForegroundColor Green
} else {
    Write-Host "  NG Obsidian vault が見つかりません: $VaultPath" -ForegroundColor Yellow
    Write-Host "     → iCloud for Windows をインストール:"
    Write-Host "       Microsoft Store で 'iCloud' を検索してインストール"
    Write-Host "     → Obsidian を起動して iCloud 上に '$VaultName' vault を作成"
    Write-Host "     → vault 名が異なる場合は `$VaultName 変数を変更してください"
}

# ── 3. 同期フォルダ作成 ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "【3/4】同期フォルダの作成"
if ((Test-Path $BoxDir) -and (Test-Path $VaultPath)) {
    New-Item -ItemType Directory -Force -Path "$BoxDir\$SharedFolder"  | Out-Null
    New-Item -ItemType Directory -Force -Path "$VaultPath\$SharedFolder" | Out-Null
    Write-Host "  OK Box:      $BoxDir\$SharedFolder" -ForegroundColor Green
    Write-Host "  OK Obsidian: $VaultPath\$SharedFolder" -ForegroundColor Green
} else {
    Write-Host "  スキップ (Box または Obsidian vault が未準備)" -ForegroundColor Yellow
}

# ── 4. タスクスケジューラ登録（30分ごと自動同期）─────────────────────────────
Write-Host ""
Write-Host "【4/4】自動同期スケジュールの登録 (30分ごと)"

$TaskName = "BoxObsidianSync"
$Action   = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -NonInteractive -WindowStyle Hidden -File `"$SyncScript`" -Direction both"

$Trigger  = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once -At (Get-Date)
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -StartWhenAvailable

# 既存タスクを削除して再登録
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Limited | Out-Null

Write-Host "  OK タスク登録完了: $TaskName" -ForegroundColor Green
Write-Host "  OK ログ: $env:USERPROFILE\AppData\Local\Logs\box-obsidian-sync.log"

Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "手動で今すぐ同期したい場合:"
Write-Host "  powershell -File `"$SyncScript`" -Direction both"
Write-Host ""
Write-Host "自動同期を停止したい場合:"
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
