<#
.SYNOPSIS
  Builds the new shell solution with warnings-as-errors (gate AC1/AC6) and saves the log.

.EXAMPLE
  pwsh -NoProfile -File scripts/build.ps1
#>
[CmdletBinding()]
param(
    [string]$Configuration = 'Debug'
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')
$evidence = Join-Path $repoRoot 'verification/HOST-CORECLIENT-1/build'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
$log = Join-Path $evidence "dotnet-build-$Configuration.log"

Push-Location $root
try {
    & dotnet build NewManga.sln -c $Configuration -warnaserror 2>&1 | Tee-Object -FilePath $log | Select-Object -Last 12
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}

Write-Output "log: $log"
if ($code -ne 0) {
    throw "dotnet build failed with exit code $code"
}
Write-Output "BUILD PASS ($Configuration, -warnaserror)"
