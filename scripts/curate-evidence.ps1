# R-19 evidence curation: tests write to %TEMP%; this script copies the curated set into the repo.
param([Parameter(Mandatory=$true)][string]$Task, [string]$Source)
$root = Split-Path -Parent $PSScriptRoot
$src = if ($Source) { $Source } else { Join-Path $env:TEMP "newmanga-evidence\$Task" }
$dst = Join-Path $root "verification\$Task"
if (-not (Test-Path $src)) { Write-Error "evidence source not found: $src (run the tests first)"; exit 1 }
New-Item -ItemType Directory -Force $dst | Out-Null
Copy-Item (Join-Path $src '*') $dst -Recurse -Force
Write-Host "curated $Task -> $dst"
