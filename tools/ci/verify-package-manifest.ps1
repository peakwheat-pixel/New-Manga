<#
.SYNOPSIS
  VERSION-MANIFEST-GUARD-1: fail-closed consistency check between a release stage and its VERSION.json.

.DESCRIPTION
  Why this exists: INSTALLER-MATRIX-1 shipped a VERSION.json whose `app_build.repo_head` said
  `fe7da5d92...` while the staged exe actually embedded `5dda04437...`, and whose
  `sidecar_build.repo_head` was a hash that does not exist in the repository at all. Nothing caught it
  until an independent reviewer recomputed the hashes by hand. This script makes that recomputation
  mechanical and blocking.

  Checks (every mismatch is a failure, never a warning):
    1. app/NewManga.App.exe           sha256 + byte count == VERSION.json app_build
    2. app_build.repo_head            == the 40-hex head EMBEDDED in the exe's ProductVersion
    3. that head                     must exist in this repository (git cat-file -e)
    4. app/core-sidecar/core_service.exe  sha256 + byte count == VERSION.json sidecar_build
    5. *.onnx under core-sidecar      count and total bytes == VERSION.json models_bundled(_bytes)
       and models_bundled must equal (count -gt 0)

.PARAMETER StageDir
  The release stage directory (the one containing app/ and VERSION.json).

.PARAMETER RepoRoot
  Repository root used for the git existence check; defaults to this script's repo.

.EXAMPLE
  pwsh -NoProfile -File tools/ci/verify-package-manifest.ps1 -StageDir "G:\...\NewManga-0.1.1-win-x64"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$StageDir,
    [string]$RepoRoot = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

$failures = [System.Collections.Generic.List[string]]::new()
function Add-Failure([string]$message) { $script:failures.Add($message) }

function Get-Sha256Lower([string]$path) {
    return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}

Write-Host "verify-package-manifest: stage=$StageDir repo=$RepoRoot"

# ------------------------------------------------------------------------------- VERSION.json
$versionPath = Join-Path $StageDir 'VERSION.json'
if (-not (Test-Path -LiteralPath $versionPath)) {
    Write-Host "FAIL: VERSION.json not found at $versionPath"
    exit 1
}
$version = Get-Content -LiteralPath $versionPath -Raw | ConvertFrom-Json

if (-not $version.app_build) { Add-Failure "VERSION.json has no app_build section" }
if (-not $version.sidecar_build) { Add-Failure "VERSION.json has no sidecar_build section" }

# ------------------------------------------------------------------------------- app exe
$exePath = Join-Path $StageDir 'app\NewManga.App.exe'
if (-not (Test-Path -LiteralPath $exePath)) {
    Add-Failure "missing app/NewManga.App.exe"
} else {
    $exeHash = Get-Sha256Lower $exePath
    $exeBytes = (Get-Item -LiteralPath $exePath).Length
    if ($version.app_build) {
        if ($version.app_build.exe_sha256 -ne $exeHash) {
            Add-Failure "app_build.exe_sha256 mismatch: json=$($version.app_build.exe_sha256) actual=$exeHash"
        }
        if ([int64]$version.app_build.exe_bytes -ne $exeBytes) {
            Add-Failure "app_build.exe_bytes mismatch: json=$($version.app_build.exe_bytes) actual=$exeBytes"
        }
    }

    # repo_head must be the head EMBEDDED in the artifact, not a hand-typed claim.
    $productVersion = (Get-Item -LiteralPath $exePath).VersionInfo.ProductVersion
    if ($productVersion -match '\+([0-9a-fA-F]{40})$') {
        $embeddedHead = $Matches[1].ToLowerInvariant()
        if ($version.app_build -and $version.app_build.repo_head -ne $embeddedHead) {
            Add-Failure "app_build.repo_head mismatch: json=$($version.app_build.repo_head) embedded=$embeddedHead"
        }
        & git -C $RepoRoot cat-file -e $embeddedHead 2>$null
        if ($LASTEXITCODE -ne 0) {
            Add-Failure "embedded head $embeddedHead does not exist in $RepoRoot (git cat-file -e failed)"
        }
    } else {
        Add-Failure "exe ProductVersion '$productVersion' does not embed a 40-hex head; repo_head cannot be verified"
    }
}

# ------------------------------------------------------------------------------- sidecar core_service
$corePath = Join-Path $StageDir 'app\core-sidecar\core_service.exe'
if (-not (Test-Path -LiteralPath $corePath)) {
    Add-Failure "missing app/core-sidecar/core_service.exe"
} else {
    $coreHash = Get-Sha256Lower $corePath
    $coreBytes = (Get-Item -LiteralPath $corePath).Length
    if ($version.sidecar_build) {
        if ($version.sidecar_build.core_service_sha256 -ne $coreHash) {
            Add-Failure "sidecar_build.core_service_sha256 mismatch: json=$($version.sidecar_build.core_service_sha256) actual=$coreHash"
        }
        if ([int64]$version.sidecar_build.core_service_bytes -ne $coreBytes) {
            Add-Failure "sidecar_build.core_service_bytes mismatch: json=$($version.sidecar_build.core_service_bytes) actual=$coreBytes"
        }
    }
}

# ------------------------------------------------------------------------------- bundled ONNX models
$sidecarDir = Join-Path $StageDir 'app\core-sidecar'
$onnx = @()
if (Test-Path -LiteralPath $sidecarDir) {
    $onnx = @(Get-ChildItem -LiteralPath $sidecarDir -Recurse -File -Filter '*.onnx' -ErrorAction SilentlyContinue)
}
$onnxBytes = 0L
foreach ($file in $onnx) { $onnxBytes += $file.Length }

$declaredBundled = $version.models_bundled
if ($null -eq $declaredBundled) {
    Add-Failure "VERSION.json has no models_bundled field (must be derived from the stage, not omitted)"
} else {
    $actualBundled = $onnx.Count -gt 0
    if ([bool]$declaredBundled -ne $actualBundled) {
        Add-Failure "models_bundled mismatch: json=$declaredBundled actual=$actualBundled ($($onnx.Count) onnx files)"
    }
    if ($null -ne $version.models_bundled_bytes) {
        if ([int64]$version.models_bundled_bytes -ne $onnxBytes) {
            Add-Failure "models_bundled_bytes mismatch: json=$($version.models_bundled_bytes) actual=$onnxBytes"
        }
    } elseif ($actualBundled) {
        Add-Failure "stage bundles $($onnx.Count) onnx files but VERSION.json declares no models_bundled_bytes"
    }
}

# ------------------------------------------------------------------------------- report
if ($failures.Count -gt 0) {
    Write-Host ''
    Write-Host "verify-package-manifest: FAILED with $($failures.Count) problem(s)" -ForegroundColor Red
    foreach ($failure in $failures) { Write-Host "  FAIL: $failure" }
    exit 1
}

Write-Host "verify-package-manifest: OK (exe, core_service, $($onnx.Count) onnx / $onnxBytes B all match VERSION.json)"
exit 0
