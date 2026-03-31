# 初回セットアップスクリプト (Windows)
# Box Drive と Obsidian (ローカル) の同期環境を構築する

# ── 設定（必要に応じて変更）─────────────────────────────────────────────────
$ObsVaultPath = "C:\Users\seizouDesk2\obsidianseizou"  # Obsidian vault のパス
$BoxShared    = "$env:USERPROFILE\Box\shared"                # Box の共有フォルダ

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$SyncScript = "$ScriptDir\sync_box_obsidian.ps1"

Write-Host "=== セットアップ開始 ===" -ForegroundColor Cyan

# ── 1. Box Drive 確認 ─────────────────────────────────────────────────────────
Write-Host "`n【1/3】Box Drive の確認"
if (Test-Path "$env:USERPROFILE\Box") {
    Write-Host "  OK: $env:USERPROFILE\Box" -ForegroundColor Green
} else {
    Write-Host "  NG: Box Drive が見つかりません" -ForegroundColor Red
    Write-Host "     → https://www.box.com/ja-jp/resources/downloads からインストール"
}

# ── 2. Obsidian vault フォルダ作成 ────────────────────────────────────────────
Write-Host "`n【2/3】フォルダの準備"
New-Item -ItemType Directory -Force -Path "$ObsVaultPath\shared" | Out-Null
New-Item -ItemType Directory -Force -Path $BoxShared             | Out-Null
Write-Host "  OK Obsidian: $ObsVaultPath\shared" -ForegroundColor Green
Write-Host "  OK Box:      $BoxShared"            -ForegroundColor Green

# ── 3. タスクスケジューラ登録（30分ごと自動同期）─────────────────────────────
Write-Host "`n【3/3】自動同期の登録 (30分ごと)"

$TaskName = "BoxObsidianSync"
$Action   = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -NonInteractive -WindowStyle Hidden -File `"$SyncScript`" -Direction both"
$Trigger  = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once -At (Get-Date)
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -StartWhenAvailable

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Limited | Out-Null

Write-Host "  OK タスク登録完了: $TaskName" -ForegroundColor Green

Write-Host "`n=== 完了 ===" -ForegroundColor Cyan
Write-Host "手動同期: powershell -File `"$SyncScript`" -Direction both"
Write-Host "ログ確認: Get-Content `"$env:USERPROFILE\AppData\Local\Logs\box-obsidian-sync.log`" -Tail 50"
