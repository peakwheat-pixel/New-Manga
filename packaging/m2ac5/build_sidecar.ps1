# M2-AC5 sidecar build script (build tooling only).
#
# Runs PyInstaller with the frozen spec and drops the onedir bundle into the
# desktop target tree (`apps/desktop/src-tauri/target/core-sidecar/`), which
# the tauri bundle then declares as `resources` (see tauri.conf.json). The
# output lives under the gitignored `target/` tree so build artifacts can
# never enter a commit.
#
# M2-PROD-DETECT-2 (AC2, proxy ruling 3): after the PyInstaller build this
# script copies the PINNED manga weights (ogkalu/comic-text-and-bubble-
# detector, three files) from the local task-envs snapshot into
# `<bundle>/models/detector/ogkalu-comic-text-and-bubble-detector/`. The
# Tauri resource mechanism packages the whole core-sidecar directory, so the
# weights ride along with zero tauri.conf.json change. Each file is
# SHA-256-checked against the pins frozen in
# src/infrastructure/providers/detection_manga.py (duplicated here as
# literals because a PowerShell build script cannot import src/**). A
# missing snapshot file or a hash mismatch FAILS the build — never a silent
# skip. docTR weights are deliberately NOT bundled (ruling 3: the release
# form fails closed NOT_CONFIGURED when switched back to doctr).
#
# Usage (from the repository root):
#   powershell -File packaging/m2ac5/build_sidecar.ps1 [-PythonExe <path>] [-Force] [-SkipWeights]
#
# The default build venv is the dedicated M2-AC5 build env (packager + ML
# runtime closure; see packaging/m2ac5/requirements-build.txt).

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$PythonExe = "G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe",
    # M2-AC5-BUILD-FRESH-CHECKOUT: force a full PyInstaller rebuild even when
    # the onedir bundle already exists (default: incremental short-circuit).
    [switch]$Force,
    # M2-PROD-DETECT-2 DSH r1 R10 review-fix: the weights snapshot location is
    # no longer hardcoded in the copy step — override it here for a different
    # machine/checkout. The snapshot files must STILL match the SHA-256 pins
    # below (the copy fails closed on any mismatch), so this parameter only
    # relocates the source, never relaxes the verification.
    [Parameter(Mandatory = $false)]
    [string]$WeightsSource = "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector",
    # M2-PROD-DETECT-2: skip the manga weights copy step (debug only — the
    # shipped bundle then has NO in-bundle weights; per the DSH r1 R5/R6
    # review-fix the frozen assembly does NOT crash: it prints one stderr
    # warning listing the probed candidates and the detect step fails closed
    # with the typed PROVIDER_NOT_CONFIGURED until the weights are placed).
    [switch]$SkipWeights
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path


# --------------------------------------------------------------------------
# M2-PROD-DETECT-2 (AC2): pinned manga weights into the bundle.
# (Defined BEFORE any call site: PowerShell resolves script-scope functions
# in sequential execution order.)
# --------------------------------------------------------------------------

function Copy-MangaWeights {
    param(
        [Parameter(Mandatory = $true)][string]$Bundle,
        [Parameter(Mandatory = $true)][string]$WeightsSource
    )

    # Destination INSIDE the onedir bundle: <bundle>/models/detector/<dirname>/
    # — the same layout the frozen assembly probes at
    # Path(sys.executable).parent/models/detector/<dirname> (proxy ruling 4).
    $destDir = Join-Path $Bundle "models/detector/ogkalu-comic-text-and-bubble-detector"

    # SHA-256 pins, duplicated verbatim from
    # src/infrastructure/providers/detection_manga.py (MANGA_MODEL_SHA256 /
    # MANGA_CONFIG_SHA256 / MANGA_PREPROCESSOR_SHA256; HF revision 16e8a622).
    # A build script cannot import src/**, so the values are literals here —
    # if the provider pins ever change, these MUST be updated in lockstep
    # (the copy step fails closed on any mismatch, so a stale literal cannot
    # ship silently).
    $pins = [ordered]@{
        "model.safetensors"        = "037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d"
        "config.json"              = "b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072"
        "preprocessor_config.json" = "7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca"
    }

    foreach ($name in $pins.Keys) {
        $src = Join-Path $weightsSource $name
        if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
            throw "weights snapshot file missing: $src (place the pinned snapshot of ogkalu/comic-text-and-bubble-detector there, or rebuild with -SkipWeights for a debug-only bundle)"
        }
        $actual = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $pins[$name]) {
            throw "weights snapshot sha256 mismatch for $name : got $actual, expected $($pins[$name]) — refusing to bundle"
        }
    }

    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    foreach ($name in $pins.Keys) {
        Copy-Item -LiteralPath (Join-Path $weightsSource $name) -Destination (Join-Path $destDir $name) -Force
    }
    Write-Host "build_sidecar: manga weights bundled (3 files, sha256 verified) -> $destDir"
}

# M2-AC5-BUILD-FRESH-CHECKOUT: incremental short-circuit. When the target
# onedir bundle is already present, skip the (expensive) PyInstaller rebuild
# and exit 0 so automated callers can invoke this unconditionally. The check
# runs before the build-venv probe on purpose: taking the skip path must not
# require the build venv to exist. Use -Force for a full rebuild (all other
# behavior, parameters and the output layout are unchanged). The weights
# step still runs on the skip path (idempotent sha256-verified copy), so a
# previously -SkipWeights-built bundle gets its weights on the next call.
$existingBundle = Join-Path $repoRoot "apps/desktop/src-tauri/target/core-sidecar/core-sidecar"
if (-not $Force -and (Test-Path -LiteralPath $existingBundle -PathType Container)) {
    Write-Host "build_sidecar: target exists, skipping (use -Force to rebuild)"
    if (-not $SkipWeights) {
        Copy-MangaWeights -Bundle $existingBundle -WeightsSource $WeightsSource
    }
    exit 0
}

if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "build venv python not found: $PythonExe (create it per packaging/m2ac5/README.md)"
}
$PythonExe = (Resolve-Path -LiteralPath $PythonExe).Path

$gitHead = (git -C $repoRoot rev-parse HEAD 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $gitHead) { throw "Unable to resolve source HEAD at $repoRoot" }

$targetRoot = Join-Path $repoRoot "apps/desktop/src-tauri/target"
$distPath = Join-Path $targetRoot "core-sidecar"
$workPath = Join-Path $targetRoot "pyinstaller-work"

$pyinstallerVersion = (& $PythonExe -m PyInstaller --version)
Write-Host "build_sidecar: git HEAD=$gitHead pyinstaller=$pyinstallerVersion python=$PythonExe"

& $PythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --distpath $distPath `
    --workpath $workPath `
    (Join-Path $repoRoot "packaging/m2ac5/core_sidecar.spec")
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed (exit=$LASTEXITCODE)" }

# layout sanity gate: the Rust host resolves exactly these names
$bundle = Join-Path $distPath "core-sidecar"
foreach ($exe in @("host_bridge.exe", "core_service.exe", "acceptance_bridge.exe", "catalog_loader.exe")) {
    if (-not (Test-Path -LiteralPath (Join-Path $bundle $exe) -PathType Leaf)) {
        throw "sidecar bundle incomplete: missing $exe under $bundle"
    }
}

if (-not $SkipWeights) {
    Copy-MangaWeights -Bundle $bundle -WeightsSource $WeightsSource
}
Write-Host "build_sidecar: OK -> $bundle (HEAD=$gitHead, pyinstaller=$pyinstallerVersion)"
