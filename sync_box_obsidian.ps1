# Box Drive <-> Obsidian sync script (Windows)

param(
    [ValidateSet("box-to-obs", "obs-to-box", "both")]
    [string]$Direction = "both"
)

$BoxShared    = if ($env:BOX_SHARED)    { $env:BOX_SHARED }    else { "$env:USERPROFILE\Box\I-1　Claude\seizou\kawana" }
$ObsShared    = if ($env:OBS_SHARED)    { $env:OBS_SHARED }    else { "C:\Users\seizouDesk2\obsidianseizou\shared" }
$ScriptsSrc   = if ($env:SCRIPTS_SRC)   { $env:SCRIPTS_SRC }   else { "$env:USERPROFILE\Documents\claude" }
$ScriptsDest  = if ($env:SCRIPTS_DEST)  { $env:SCRIPTS_DEST }  else { "$env:USERPROFILE\Box\scripts" }

$LogFile = "$env:USERPROFILE\AppData\Local\Logs\box-obsidian-sync.log"

function Log { param($msg); Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg" }

if (-not (Test-Path (Split-Path $BoxShared))) {
    Write-Error "Box Drive not found. Please install and sign in to Box Drive."
    exit 1
}
if (-not (Test-Path (Split-Path $ObsShared))) {
    Write-Error "Obsidian vault not found: $(Split-Path $ObsShared)"
    exit 1
}

New-Item -ItemType Directory -Force -Path $BoxShared | Out-Null
New-Item -ItemType Directory -Force -Path $ObsShared | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

function Sync($From, $To, $Label) {
    Log "$Label : $From -> $To"
    robocopy $From $To /MIR /XF "*.tmp" "desktop.ini" /XD ".obsidian" ".tmp" /NP /LOG+:$LogFile
    Log "$Label done"
}

switch ($Direction) {
    "box-to-obs" { Sync $BoxShared $ObsShared "Box -> Obsidian" }
    "obs-to-box" { Sync $ObsShared $BoxShared "Obsidian -> Box" }
    "both"       { Sync $BoxShared $ObsShared "Box -> Obsidian"; Sync $ObsShared $BoxShared "Obsidian -> Box" }
}

# Copy scripts to Box\scripts\
if (Test-Path (Split-Path $ScriptsDest)) {
    New-Item -ItemType Directory -Force -Path $ScriptsDest | Out-Null
    robocopy $ScriptsSrc $ScriptsDest /MIR `
        /XD ".git" ".claude" `
        /XF "*.xlsx" "*.py" "hello.txt" `
        /NP /LOG+:$LogFile
    Log "Scripts copied to Box\scripts\"
}
