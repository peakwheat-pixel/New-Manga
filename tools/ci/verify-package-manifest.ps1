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

# reviewer-imc F-04: a trailing separator on -StageDir used to make every relative-path
# comparison fail ("lists N files that are not in the stage"). Normalize once, trim both ends.
$StageDir = (Resolve-Path -LiteralPath $StageDir).Path.TrimEnd('\', '/')

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

# ------------------------------------------------------------------------------- package-manifest.json cross-check
# INSTALLER-METADATA-CONSISTENCY-1: this file ships as the package's own description, yet nothing
# compared it with VERSION.json or with the files on disk. The 2026-11-15 stage carried a
# package-manifest.json from 2026-10-28 saying version 0.1.0 / models_bundled false / models_bytes 0
# while the very same stage had 3 onnx / 632,552,582 B and VERSION.json said 0.1.1. Every check below
# is a failure, never a warning.
$manifestPath = Join-Path $StageDir 'package-manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    Add-Failure "package-manifest.json not found at $manifestPath (the package must describe itself)"
} else {
    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    } catch {
        Add-Failure "package-manifest.json is not valid JSON: $manifestPath"
        $manifest = $null
    }
    if ($manifest) {
        if ([string]$manifest.version -ne [string]$version.version) {
            Add-Failure "package-manifest.json version mismatch: manifest=$($manifest.version) VERSION.json=$($version.version)"
        }
        if ([string]$manifest.variant -ne [string]$version.variant) {
            Add-Failure "package-manifest.json variant mismatch: manifest=$($manifest.variant) VERSION.json=$($version.variant)"
        }
        if ($null -eq $manifest.models_bundled) {
            Add-Failure "package-manifest.json has no models_bundled field"
        } elseif ([bool]$manifest.models_bundled -ne ($onnx.Count -gt 0)) {
            Add-Failure "package-manifest.json models_bundled mismatch: manifest=$($manifest.models_bundled) actual=$($onnx.Count -gt 0) ($($onnx.Count) onnx files)"
        }
        if ($null -eq $manifest.models_bytes) {
            Add-Failure "package-manifest.json has no models_bytes field"
        } elseif ([int64]$manifest.models_bytes -ne $onnxBytes) {
            Add-Failure "package-manifest.json models_bytes mismatch: manifest=$($manifest.models_bytes) actual=$onnxBytes"
        }
        # The manifest must describe the stage that is on disk, not an older build of it.
        # package.ps1 enumerates the stage BEFORE writing package-manifest.json, so the manifest
        # itself is legitimately absent from its own list: exclude it from the on-disk count.
        $listed = @($manifest.files)
        $actualFiles = @(Get-ChildItem -LiteralPath $StageDir -Recurse -File |
            Where-Object { -not ($_.FullName -eq $manifestPath) })
        if ($listed.Count -ne $actualFiles.Count) {
            Add-Failure "package-manifest.json lists $($listed.Count) file(s) but the stage holds $($actualFiles.Count) (excluding the manifest itself)"
        }
        # F-06: compare SETS, not just counts -- a manifest with a duplicated entry could otherwise
        # hide a file it never lists.
        $actualByRel = @{}
        foreach ($file in $actualFiles) {
            $rel = $file.FullName.Substring($StageDir.Length + 1).Replace('\', '/')
            $actualByRel[$rel] = $file
        }
        $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
        $missing = [System.Collections.Generic.List[string]]::new()
        $duplicates = [System.Collections.Generic.List[string]]::new()
        $badBytes = [System.Collections.Generic.List[string]]::new()
        $badHash = [System.Collections.Generic.List[string]]::new()
        foreach ($entry in $listed) {
            $rel = [string]$entry.path
            if (-not $rel) { Add-Failure "package-manifest.json has an entry with no path"; continue }
            if (-not $seen.Add($rel)) { $duplicates.Add($rel); continue }
            if (-not $actualByRel.ContainsKey($rel)) { $missing.Add($rel); continue }
            $file = $actualByRel[$rel]
            # F-05: bytes and sha256 per file -- a same-size content swap must not pass.
            if ($null -ne $entry.bytes -and [int64]$entry.bytes -ne $file.Length) {
                $badBytes.Add("$rel (manifest=$($entry.bytes) actual=$($file.Length))")
            }
            $declared = ([string]$entry.sha256).ToLowerInvariant()
            if ($declared -and $declared -ne (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()) {
                $badHash.Add($rel)
            }
        }
        $unlisted = [System.Collections.Generic.List[string]]::new()
        foreach ($rel in $actualByRel.Keys) { if (-not $seen.Contains($rel)) { $unlisted.Add($rel) } }
        if ($missing.Count -gt 0) {
            $preview = ($missing | Select-Object -First 5) -join ', '
            Add-Failure "package-manifest.json lists $($missing.Count) file(s) that are not in the stage (e.g. $preview)"
        }
        if ($duplicates.Count -gt 0) {
            $preview = ($duplicates | Select-Object -First 5) -join ', '
            Add-Failure "package-manifest.json repeats $($duplicates.Count) path(s) (e.g. $preview)"
        }
        if ($unlisted.Count -gt 0) {
            $preview = ($unlisted | Select-Object -First 5) -join ', '
            Add-Failure "package-manifest.json does not list $($unlisted.Count) file(s) present in the stage (e.g. $preview)"
        }
        if ($badBytes.Count -gt 0) {
            $preview = ($badBytes | Select-Object -First 5) -join '; '
            Add-Failure "package-manifest.json bytes mismatch for $($badBytes.Count) file(s): $preview"
        }
        if ($badHash.Count -gt 0) {
            $preview = ($badHash | Select-Object -First 5) -join ', '
            Add-Failure "package-manifest.json sha256 mismatch for $($badHash.Count) file(s) (e.g. $preview)"
        }
    }
}

# ------------------------------------------------------------------------------- licence consistency
# reviewer-tgl P1-2: the guard checked bytes, never the licence declaration, so a stage that bundled
# AGPL weights under a GPL-3.0-or-later claim would have passed. Mirror build-installer's rules here so
# the failure surfaces at the stage gate too, not only at packaging time.
$declaredLicense = [string]$version.license
if (-not $declaredLicense) {
    Add-Failure "VERSION.json has no license field"
} elseif ($onnx.Count -gt 0) {
    if ($declaredLicense -ne 'GPL-3.0-or-later') {
        Add-Failure "licence mismatch: stage bundles $($onnx.Count) onnx file(s) but VERSION.json license='$declaredLicense' (expected GPL-3.0-or-later while the bundled weights declare Apache-2.0)"
    }
    $tplPath = Join-Path $StageDir 'THIRD_PARTY_LICENSES.md'
    if (-not (Test-Path -LiteralPath $tplPath)) {
        Add-Failure "stage has no THIRD_PARTY_LICENSES.md; the bundled weights' upstream declarations cannot be proven"
    } else {
        $tplLines = Get-Content -LiteralPath $tplPath -Encoding UTF8
        foreach ($onnxFile in $onnx) {
            $rel = $onnxFile.FullName.Substring((Join-Path $StageDir 'app/core-sidecar').Length + 1).Replace('\', '/')
            $row = $tplLines | Where-Object { $_ -match '^\|' -and ($_ -match [regex]::Escape($rel) -or $_ -match [regex]::Escape($onnxFile.Name)) } | Select-Object -First 1
            if (-not $row) {
                Add-Failure "THIRD_PARTY_LICENSES.md has no row for bundled weight '$rel'"
            } elseif ($row -match '待核实') {
                Add-Failure "THIRD_PARTY row for '$rel' still says 待核实 but the package claims GPL-3.0-or-later"
            } elseif ($row -notmatch 'Apache-2\.0') {
                Add-Failure "THIRD_PARTY row for '$rel' does not record the Apache-2.0 upstream declaration"
            }
        }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $StageDir 'LICENSE-Apache-2.0.txt'))) {
        Add-Failure "stage bundles weights but has no LICENSE-Apache-2.0.txt (Apache-2.0 section 4 requires shipping the licence)"
    }
} elseif ($declaredLicense -ne 'GPL-3.0-or-later') {
    Add-Failure "base stage (no weights) must declare GPL-3.0-or-later, got '$declaredLicense'"
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
