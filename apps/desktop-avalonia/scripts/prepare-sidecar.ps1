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
    # SIDECAR-SCHEMA-STALE-1 P2 (DSH 2026-11-16): models/ used to be excluded unconditionally, which broke
    # RunBindingFixTests.ModelsBuild_* -- without the detector/OCR weights the run never leaves 'pending'.
    # Pass -IncludeModels for callers that exercise a models build.
    [switch]$IncludeModels,
    # SIDECAR-SCHEMA-STALE-1 P0-2 (DSH 2026-11-16, per r1 review): the default used to point at
    # 'apps/desktop/src-tauri/target/release/resources/core-sidecar' -- the RETIRED Tauri shell (AD-002).
    # That stale 2026-10-23 tree is what made his fixture copy carry schema v6 while the source tree is at
    # v14, so every sidecar test failed handshake. Provide one of:
    #   -Source <dir>                  explicit packaged sidecar (contains core_service.exe)
    #   NEWMANGA_SIDECAR_SOURCE=<dir>  override the default
    #   (default)                      the Avalonia build, i.e. staging/m2ac5 output
    [string]$Source = $( if ($env:NEWMANGA_SIDECAR_SOURCE) { $env:NEWMANGA_SIDECAR_SOURCE } else { Join-Path (Split-Path $PSScriptRoot -Parent) 'build/sidecar/core-sidecar/core-sidecar' }),
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
# SIDECAR-SCHEMA-STALE-1 P2 (DSH 2026-11-16): the blanket models exclusion broke
# RunBindingFixTests.ModelsBuild_*, which needs the detector/OCR weights to finish a run -- without them
# the detect step fail-closes with PROVIDER_NOT_CONFIGURED and the task stays 'pending' forever. Callers
# that exercise a models build must pass -IncludeModels.
$excluded = @('/XD', 'python')
if (-not $IncludeModels) { $excluded = @('/XD', 'models', 'python') }
$robocopyArgs = @($Source, $Destination, '/E') + $excluded + @('/NFL', '/NDL', '/NJH', '/NJS', '/NP')
& robocopy @robocopyArgs | Out-Null
if ($LASTEXITCODE -ge 8) {
    throw "robocopy failed with exit code $LASTEXITCODE (source=$Source destination=$Destination)"
}

$files = Get-ChildItem $Destination -Recurse -File
$totalMb = [math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Output "sidecar copy ready: $Destination ($($files.Count) files, $totalMb MB)"
Write-Output "NEWMANGA_CORECLIENT_SIDECAR_DIR=$Destination"
