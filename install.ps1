# Install the game-studio skill and its agents without the plugin system (Windows PowerShell).
#   .\install.ps1 -Target C:\path\to\your-game   -> <game>\.claude\skills + .claude\agents
#   .\install.ps1 -User                          -> ~\.claude\skills + ~\.claude\agents
param([string]$Target = "", [switch]$User)
$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "plugins\game-studio"
if ($User) { $dest = Join-Path $HOME ".claude" }
elseif ($Target) { $dest = Join-Path (Resolve-Path $Target) ".claude" }
else { Write-Error "usage: .\install.ps1 -Target C:\path\to\your-game   |   .\install.ps1 -User"; exit 2 }
New-Item -ItemType Directory -Force -Path (Join-Path $dest "skills"), (Join-Path $dest "agents") | Out-Null
$skillDest = Join-Path $dest "skills\game-studio"
$backup = Join-Path $dest ("game-studio-backups\install." + [guid]::NewGuid().ToString("N"))
$backedUp = $false
if (Test-Path $skillDest) {
  New-Item -ItemType Directory -Force -Path (Join-Path $backup "skills") | Out-Null
  Move-Item $skillDest (Join-Path $backup "skills\game-studio")
  $backedUp = $true
}
foreach ($agentFile in Get-ChildItem (Join-Path $src "agents\*.md")) {
  $existing = Join-Path $dest ("agents\" + $agentFile.Name)
  if (Test-Path $existing) {
    New-Item -ItemType Directory -Force -Path (Join-Path $backup "agents") | Out-Null
    Move-Item $existing (Join-Path $backup ("agents\" + $agentFile.Name))
    $backedUp = $true
  }
}
Copy-Item -Recurse (Join-Path $src "skills\game-studio") $skillDest
Copy-Item (Join-Path $src "agents\*.md") (Join-Path $dest "agents")
Write-Host "Installed to $dest. Start a new Claude Code session in the project and paste the prompt from PROMPT.md."
if ($backedUp) { Write-Host "Previous installation preserved: $backup" }
