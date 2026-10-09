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
if (Test-Path $skillDest) { Remove-Item -Recurse -Force $skillDest }
Copy-Item -Recurse (Join-Path $src "skills\game-studio") $skillDest
Copy-Item (Join-Path $src "agents\*.md") (Join-Path $dest "agents")
Write-Host "Installed to $dest. Start a new Claude Code session in the project and paste the prompt from PROMPT.md."
