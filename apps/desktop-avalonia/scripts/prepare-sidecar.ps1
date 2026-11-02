<#
.SYNOPSIS
  Copies the packaged Python Core sidecars to an unlabelled workspace directory.

.DESCRIPTION
  AC11: the repository tree carries a Low mandatory label, so a process started from it inherits
  Low IL and the Python Core cannot write its data root. Every host test must therefore run from an
  unlabelled copy (robocopy without ACL copy). models/ and python/ are not needed by
  core_service/host_bridge/catalog_loader and are skipped to keep the copy small.

.EXAMPLE
  pwsh -NoProfile -File scripts/prepare-sidecar.ps1
#>
[CmdletBinding()]
param(
    [string]$Source = $( if ($env:NEWMANGA_REPO_ROOT) { Join-Path $env:NEWMANGA_REPO_ROOT 'apps/desktop/src-tauri/target/release/resources/core-sidecar' } else { Join-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent) 'apps/desktop/src-tauri/target/release/resources/core-sidecar' } ),
    [string]$Destination = $( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/HOST-CORECLIENT-1/sidecar-copy' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/HOST-CORECLIENT-1/sidecar-copy' } )
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Source)) {
    throw @"
Packaged sidecar directory not found: $Source
V11R-A-4: this path is no longer hardcoded to a maintainer checkout. Provide one of:
  -Source <dir>                     explicit packaged sidecar (contains core_service.exe)
  NEWMANGA_REPO_ROOT=<repo>         repository root containing apps/desktop/src-tauri/...
  packaging/m2ac5/build_sidecar.ps1 -SkipWeights   build a weights-free sidecar first
"@
}

foreach ($exe in @('core_service.exe', 'host_bridge.exe', 'catalog_loader.exe')) {
    if (-not (Test-Path (Join-Path $Source $exe))) {
        throw "Missing $exe under $Source (pass -Source with a complete packaged sidecar)"
    }
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
# /E recurse, exclude models+python (not used by these entries), no ACL copy -> destination label wins.
$robocopyArgs = @($Source, $Destination, '/E', '/XD', 'models', 'python', '/NFL', '/NDL', '/NJH', '/NJS', '/NP')
& robocopy @robocopyArgs | Out-Null
if ($LASTEXITCODE -ge 8) {
    throw "robocopy failed with exit code $LASTEXITCODE (source=$Source destination=$Destination)"
}

$files = Get-ChildItem $Destination -Recurse -File
$totalMb = [math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Output "sidecar copy ready: $Destination ($($files.Count) files, $totalMb MB)"
Write-Output "NEWMANGA_CORECLIENT_SIDECAR_DIR=$Destination"
