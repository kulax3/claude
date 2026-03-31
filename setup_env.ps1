# Setup script (Windows)
# Box Drive + Obsidian sync environment

$ObsVaultPath = "C:\Users\seizouDesk2\Documents\claude"
$BoxShared    = "C:\Users\seizouDesk2\Box\I-1 Claude\seizou\kawana"

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$SyncScript = "$ScriptDir\sync_box_obsidian.ps1"
$LogFile    = "$env:USERPROFILE\AppData\Local\Logs\box-obsidian-sync.log"

Write-Host "=== Setup Start ===" -ForegroundColor Cyan

# 1. Check Box Drive
Write-Host "`n[1/3] Box Drive check"
if (Test-Path "$env:USERPROFILE\Box") {
    Write-Host "  OK: $env:USERPROFILE\Box" -ForegroundColor Green
} else {
    Write-Host "  NG: Box Drive not found" -ForegroundColor Red
    Write-Host "     -> Install from https://www.box.com/ja-jp/resources/downloads"
}

# 2. Create folders
Write-Host "`n[2/3] Creating folders"
New-Item -ItemType Directory -Force -Path "$ObsVaultPath\shared"  | Out-Null
New-Item -ItemType Directory -Force -Path "$ObsVaultPath\context" | Out-Null
New-Item -ItemType Directory -Force -Path $BoxShared              | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $LogFile)   | Out-Null
Write-Host "  OK Obsidian shared : $ObsVaultPath\shared"  -ForegroundColor Green
Write-Host "  OK Obsidian context: $ObsVaultPath\context" -ForegroundColor Green
Write-Host "  OK Box             : $BoxShared"             -ForegroundColor Green

# 3. Register Task Scheduler (every 30 min)
Write-Host "`n[3/3] Registering auto-sync task (every 30 min)"

$TaskName = "BoxObsidianSync"
$Action   = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -NonInteractive -WindowStyle Hidden -File '$SyncScript' -Direction both"
$Trigger  = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once -At (Get-Date)
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -StartWhenAvailable

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Limited | Out-Null

Write-Host "  OK Task registered: $TaskName" -ForegroundColor Green

Write-Host "`n=== Done ===" -ForegroundColor Cyan
Write-Host "Manual sync : powershell -File '$SyncScript' -Direction both"
Write-Host "Check log   : Get-Content '$LogFile' -Tail 50"
