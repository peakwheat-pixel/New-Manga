<#
.SYNOPSIS
  Runs the full dotnet test suite against the real (unlabelled) sidecars and stores evidence.

.DESCRIPTION
  Sets NEWMANGA_CORECLIENT_SIDECAR_DIR (AC11 unlabelled copy) and NEWMANGA_EVIDENCE_DIR
  (verification/HOST-CORECLIENT-1) so integration tests can write raw wire evidence, then runs
  `dotnet test` on the solution.

.EXAMPLE
  pwsh -NoProfile -File scripts/test.ps1
#>
[CmdletBinding()]
param(
    [string]$Configuration = 'Debug',
    [string]$SidecarDirectory = 'G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy'
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')
$evidence = Join-Path $repoRoot 'verification/HOST-CORECLIENT-1'
New-Item -ItemType Directory -Force -Path (Join-Path $evidence 'test') | Out-Null

if (-not (Test-Path (Join-Path $SidecarDirectory 'core_service.exe'))) {
    & (Join-Path $PSScriptRoot 'prepare-sidecar.ps1') -Destination $SidecarDirectory
}

$env:NEWMANGA_CORECLIENT_SIDECAR_DIR = (Resolve-Path $SidecarDirectory).Path
$env:NEWMANGA_EVIDENCE_DIR = (Resolve-Path $evidence).Path
Write-Output "NEWMANGA_CORECLIENT_SIDECAR_DIR=$env:NEWMANGA_CORECLIENT_SIDECAR_DIR"
Write-Output "NEWMANGA_EVIDENCE_DIR=$env:NEWMANGA_EVIDENCE_DIR"

$log = Join-Path $evidence "test/dotnet-test-$Configuration.log"
$trx = Join-Path $evidence "test/results-$Configuration.trx"
Push-Location $root
try {
    & dotnet test NewManga.sln -c $Configuration --no-build --logger "trx;LogFileName=$trx" --logger "console;verbosity=normal" 2>&1 |
        Tee-Object -FilePath $log | Select-Object -Last 25
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}

Write-Output "log: $log"
if ($code -ne 0) {
    throw "dotnet test failed with exit code $code"
}
Write-Output "TEST PASS ($Configuration)"
