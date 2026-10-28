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
    [string]$Source = 'G:/CODEX/New Manga/apps/desktop/src-tauri/target/release/resources/core-sidecar',
    [string]$Destination = 'G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy'
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Source)) {
    throw "Packaged sidecar directory not found: $Source"
}

foreach ($exe in @('core_service.exe', 'host_bridge.exe', 'catalog_loader.exe')) {
    if (-not (Test-Path (Join-Path $Source $exe))) {
        throw "Missing $exe under $Source"
    }
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
# /E recurse, exclude models+python (not used by these entries), no ACL copy -> destination label wins.
$robocopyArgs = @($Source, $Destination, '/E', '/XD', 'models', 'python', '/NFL', '/NDL', '/NJH', '/NJS', '/NP')
& robocopy @robocopyArgs | Out-Null
if ($LASTEXITCODE -ge 8) {
    throw "robocopy failed with exit code $LASTEXITCODE"
}

$files = Get-ChildItem $Destination -Recurse -File
$totalMb = [math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Output "sidecar copy ready: $Destination ($($files.Count) files, $totalMb MB)"
Write-Output "NEWMANGA_CORECLIENT_SIDECAR_DIR=$Destination"
