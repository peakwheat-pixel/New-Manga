# M2-AC5 sidecar build script (build tooling only).
#
# Runs PyInstaller with the frozen spec and drops the onedir bundle into the
# Avalonia build tree (`apps/desktop-avalonia/build/sidecar/core-sidecar/`), which
# the tauri bundle then declares as `resources` (see tauri.conf.json). The
# output lives under the gitignored `apps/desktop-avalonia/build/` tree so build artifacts can
# never enter a commit.
#
# CORE-SLIM-2 (AC2/AC3): after the PyInstaller build this script copies the
# PINNED ONNX model bundle from the local task-envs snapshot into the sidecar:
#   <bundle>/models/detector/rtdetr-v2-fixed.onnx          (RT-DETR-v2, opset17)
#   <bundle>/models/ocr/manga-ocr-onnx/                     (encoder/decoder/vocab)
# The Tauri resource mechanism packages the whole core-sidecar directory, so
# the models ride along with zero tauri.conf.json change. Each ONNX/vocab file
# is SHA-256-checked against the pins frozen in
# src/infrastructure/providers/detection_manga_onnx.py and
# src/infrastructure/providers/ocr_manga_onnx.py (duplicated here as literals
# because a PowerShell build script cannot import src/**). A missing snapshot
# file or a hash mismatch FAILS the build — never a silent skip. The torch
# safetensors snapshot and docTR weights are deliberately NOT bundled any more
# (CORE-SLIM-2: the shipped closure is torch-free; both paths remain optional
# operator-installed fallbacks).
#
# Usage (from the repository root):
#   powershell -File packaging/m2ac5/build_sidecar.ps1 [-PythonExe <path>] [-WeightsSource <dir>] [-OcrWeightsSource <dir>] [-SfxWeightsSource <dir>] [-Force] [-SkipWeights] [-BundlePythonRuntime <dir>] [-SkipPythonRuntime]
#
# PLUGIN-RUNTIME-PACKAGED-PYTHON-1: the plugin-hook Python runtime is bundled
# into <bundle>/python/ by DEFAULT (resolved from the build interpreter's
# sys.base_prefix). Pass -SkipPythonRuntime to opt out (debug only).
#
# The default build venv is the dedicated M2-AC5 build env (packager + ML
# runtime closure; see packaging/m2ac5/requirements-build.txt).

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$PythonExe = $( if ($env:NEWMANGA_BUILD_PYTHON) { $env:NEWMANGA_BUILD_PYTHON } else { 'python' } ),
    # M2-AC5-BUILD-FRESH-CHECKOUT: force a full PyInstaller rebuild even when
    # the onedir bundle already exists (default: incremental short-circuit).
    [switch]$Force,
    # M2-PROD-DETECT-2 DSH r1 R10 review-fix: the weights snapshot location is
    # no longer hardcoded in the copy step — override it here for a different
    # machine/checkout. The snapshot files must STILL match the SHA-256 pins
    # below (the copy fails closed on any mismatch), so this parameter only
    # relocates the source, never relaxes the verification.
    [Parameter(Mandatory = $false)]
    [string]$WeightsSource = $( $v11rRepo = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/CORE-SLIM-2/models/detector' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/CORE-SLIM-2/models/detector' } ),
    # CORE-SLIM-2: directory holding the manga-ocr ONNX bundle directory
    # (manga-ocr-onnx/ with encoder_model.onnx + decoder_model.onnx + vocab.txt
    # + tokenizer/config json). Same relocation-only semantics.
    [Parameter(Mandatory = $false)]
    [string]$OcrWeightsSource = $( $v11rRepo = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/CORE-SLIM-2/models/ocr' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/CORE-SLIM-2/models/ocr' } ),
    # M2-SFX-PROD-1 / M2-SFX-T4-SWITCH: source directory holding the pinned
    # SFX ONNX export (yolo11s-seg.onnx). Since the v2b switch the default
    # points at the v2b deploy directory (the previous chiqui7 file stays in
    # the sibling weights/ directory, untouched, for the rollback path).
    # Same relocation-only semantics as -WeightsSource:
    # the file must STILL match the SHA-256 pin below or the build fails.
    [Parameter(Mandatory = $false)]
    [string]$SfxWeightsSource = $( $v11rRepo = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/M2-SFX-DETECT/weights-v2b' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/M2-SFX-DETECT/weights-v2b' } ),
    # M2-PROD-DETECT-2: skip the manga weights copy step (debug only — the
    # shipped bundle then has NO in-bundle weights; per the DSH r1 R5/R6
    # review-fix the frozen assembly does NOT crash: it prints one stderr
    # warning listing the probed candidates and the detect step fails closed
    # with the typed PROVIDER_NOT_CONFIGURED until the weights are placed).
    # M2-SFX-PROD-1: also skips the sfx weights copy (same debug semantics —
    # the sfx provider fails closed NOT_CONFIGURED at detect time, the app
    # assembles and the manga chain lives on).
    [switch]$SkipWeights,
    # PLUGIN-RUNTIME-PACKAGED-PYTHON-1: copy a complete relocatable Python
    # runtime into <bundle>/python/ so plugin hooks run in the packaged app.
    # The directory must contain python.exe (the interpreter used to run
    # PyInstaller is a natural candidate: its Lib/DLLs are the same ABI).
    [Parameter(Mandatory = $false)]
    [string]$BundlePythonRuntime = "",
    # PLUGIN-RUNTIME-PACKAGED-PYTHON-1: opt out of the bundled plugin-hook
    # runtime (debug only; the packaged app then fails closed for plugin hooks).
    [switch]$SkipPythonRuntime
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path


# --------------------------------------------------------------------------
# PLUGIN-RUNTIME-PACKAGED-PYTHON-1: complete relocatable Python runtime.
if ($BundlePythonRuntime) {
    if (-not (Test-Path -LiteralPath (Join-Path $BundlePythonRuntime "python.exe") -PathType Leaf)) {
        throw "BundlePythonRuntime does not contain python.exe: $BundlePythonRuntime"
    }
    . (Join-Path $repoRoot "packaging/bundle_python_runtime.ps1")
}

# M2-PROD-DETECT-2 (AC2): pinned manga weights into the bundle.
# (Defined BEFORE any call site: PowerShell resolves script-scope functions
# in sequential execution order.)
# --------------------------------------------------------------------------

function Copy-MangaDetectorOnnx {
    param(
        [Parameter(Mandatory = $true)][string]$Bundle,
        [Parameter(Mandatory = $true)][string]$WeightsSource
    )

    # CORE-SLIM-2: RT-DETR-v2 fixed-shape ONNX export (opset 17, 1x3x640x640).
    # Destination INSIDE the onedir bundle: <bundle>/models/detector/
    # (the frozen provider probes Path(sys.executable).parent/models/detector/
    # <file>, and the data root's models/detector/<file> first).
    $destDir = Join-Path $Bundle "models/detector"
    $name = "rtdetr-v2-fixed.onnx"
    # SHA-256 pin, duplicated verbatim from
    # src/infrastructure/providers/detection_manga_onnx.py
    # (MANGA_ONNX_SHA256). The provider re-verifies it at load time; a stale
    # literal here would fail closed at detect, and a corrupted snapshot fails
    # here at build.
    $pin = "c7fb5af1a8982416b56955e621c1b10397730807956998066e2fbc132c77bbc3"
    $src = Join-Path $weightsSource $name
    if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
        throw "manga detector ONNX missing: $src (run the CORE-SLIM-2 model staging step, or rebuild with -SkipWeights for a debug-only bundle)"
    }
    $actual = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $pin) {
        throw "manga detector ONNX sha256 mismatch for $name : got $actual, expected $pin — refusing to bundle"
    }
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    Copy-Item -LiteralPath $src -Destination (Join-Path $destDir $name) -Force
    Write-Host "build_sidecar: manga detector ONNX bundled (rtdetr-v2-fixed.onnx, sha256 verified) -> $destDir"
}

function Copy-MangaOcrOnnx {
    param(
        [Parameter(Mandatory = $true)][string]$Bundle,
        [Parameter(Mandatory = $true)][string]$OcrWeightsSource
    )

    # CORE-SLIM-2: manga-ocr encoder + decoder ONNX pair plus its tokenizer
    # files. Destination: <bundle>/models/ocr/manga-ocr-onnx/ (the frozen
    # provider probes <exe dir>/models/ocr/manga-ocr-onnx).
    $destDir = Join-Path $Bundle "models/ocr/manga-ocr-onnx"
    $sourceDir = Join-Path $OcrWeightsSource "manga-ocr-onnx"
    # SHA-256 pins, duplicated verbatim from
    # src/infrastructure/providers/ocr_manga_onnx.py.
    $pins = [ordered]@{
        "encoder_model.onnx"     = "15fa8155fe9bc1a7d25d9bb353debaa4def033d0174e907dbd2dd6d995def85f"
        "decoder_model.onnx"     = "ef7765261e9d1cdc34d89356986c2bbc2a082897f753a89605ae80fdfa61f5e8"
        "vocab.txt"              = "5cb5c5586d98a2f331d9f8828e4586479b0611bfba5d8c3b6dadffc84d6a36a3"
    }
    foreach ($name in $pins.Keys) {
        $src = Join-Path $sourceDir $name
        if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
            throw "manga-ocr ONNX missing: $src (run the CORE-SLIM-2 model staging step, or rebuild with -SkipWeights for a debug-only bundle)"
        }
        $actual = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $pins[$name]) {
            throw "manga-ocr ONNX sha256 mismatch for $name : got $actual, expected $($pins[$name]) — refusing to bundle"
        }
    }
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    foreach ($name in $pins.Keys) {
        Copy-Item -LiteralPath (Join-Path $sourceDir $name) -Destination (Join-Path $destDir $name) -Force
    }
    # The tokenizer/config files are small and pinned by the provider's
    # behaviour, not by hash (they are not executable weights); copy the
    # complete set so a future re-export cannot half-update the bundle.
    foreach ($name in @("config.json", "preprocessor_config.json", "generation_config.json", "tokenizer_config.json", "special_tokens_map.json")) {
        $src = Join-Path $sourceDir $name
        if (Test-Path -LiteralPath $src -PathType Leaf) {
            Copy-Item -LiteralPath $src -Destination (Join-Path $destDir $name) -Force
        }
    }
    Write-Host "build_sidecar: manga-ocr ONNX bundled (encoder/decoder/vocab, sha256 verified) -> $destDir"
}

# --------------------------------------------------------------------------
# M2-SFX-PROD-1 (AC7): pinned chiqui7 ONNX into the bundle.
# Same discipline as Copy-MangaWeights: sha256-verified copy into
# <bundle>/models/detector/ (a FILE this time, not a directory — the frozen
# assembly resolves it through the same shared lookup, file semantics like
# doctr). A missing file or hash mismatch FAILS the build — never a silent
# skip. The user ruling 2026-10-01 (route A: chiqui7 MIT accepted) is what
# makes this bundling step legitimate.
# --------------------------------------------------------------------------

function Copy-SfxWeights {
    param(
        [Parameter(Mandatory = $true)][string]$Bundle,
        [Parameter(Mandatory = $true)][string]$WeightsSource
    )

    # Destination INSIDE the onedir bundle: <bundle>/models/detector/<file>.
    $destDir = Join-Path $Bundle "models/detector"

    # SHA-256 pin, duplicated verbatim from
    # src/infrastructure/providers/detection_sfx.py (SFX_WEIGHTS_SHA256;
    # M2-SFX-T4-SWITCH switch: local train-v2b release, deployment chain
    # base .pt 1f0fd609… -> best.pt c22f0175… -> best.onnx 944e8114…;
    # rollback = the previous chiqui7 pin d87389af… + weights in place).
    # A build script cannot import
    # src/**, so the value is a literal here — if the provider pin ever
    # changes, these MUST be updated in lockstep (the copy step fails closed
    # on any mismatch, so a stale literal cannot ship silently).
    $pins = [ordered]@{
        "yolo11s-seg.onnx" = "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
    }

    foreach ($name in $pins.Keys) {
        $src = Join-Path $weightsSource $name
        if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
            throw "sfx weights file missing: $src (place the pinned v2b ONNX export there — local-release:sfx-train-v2/v2b, see detection_sfx.py — or rebuild with -SkipWeights for a debug-only bundle)"
        }
        $actual = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $pins[$name]) {
            throw "sfx weights sha256 mismatch for $name : got $actual, expected $($pins[$name]) — refusing to bundle"
        }
    }

    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    foreach ($name in $pins.Keys) {
        Copy-Item -LiteralPath (Join-Path $weightsSource $name) -Destination (Join-Path $destDir $name) -Force
    }
    Write-Host "build_sidecar: sfx weights bundled (yolo11s-seg.onnx, sha256 verified) -> $destDir"
}

# PLUGIN-RUNTIME-PACKAGED-PYTHON-1: resolve the runtime to bundle (default:
# the build interpreter's base installation) and load the shared helper.
if (-not $SkipPythonRuntime) {
    . (Join-Path $repoRoot "packaging/bundle_python_runtime.ps1")
    if (-not $BundlePythonRuntime) {
        if (Test-Path -LiteralPath $PythonExe -PathType Leaf) {
            $basePrefix = (& $PythonExe -I -c "import sys; print(sys.base_prefix)" 2>$null)
            if ($LASTEXITCODE -eq 0 -and $basePrefix -and (Test-Path -LiteralPath (Join-Path $basePrefix "python.exe") -PathType Leaf)) {
                $BundlePythonRuntime = $basePrefix.Trim()
            }
        }
    }
    if (-not $BundlePythonRuntime) {
        # fail-closed: a release bundle must ship the plugin-hook interpreter
        # (an explicit -SkipPythonRuntime is the only way to opt out).
        throw "build_sidecar: cannot resolve the plugin-hook Python runtime (pass -BundlePythonRuntime <dir> with python.exe, or -SkipPythonRuntime to opt out explicitly)"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $BundlePythonRuntime "python.exe") -PathType Leaf)) {
        throw "BundlePythonRuntime does not contain python.exe: $BundlePythonRuntime"
    }
}

# M2-AC5-BUILD-FRESH-CHECKOUT: incremental short-circuit. When the target
# onedir bundle is already present, skip the (expensive) PyInstaller rebuild
# and exit 0 so automated callers can invoke this unconditionally. The check
# runs before the build-venv probe on purpose: taking the skip path must not
# require the build venv to exist. Use -Force for a full rebuild (all other
# behavior, parameters and the output layout are unchanged). The weights
# step still runs on the skip path (idempotent sha256-verified copy), so a
# previously -SkipWeights-built bundle gets its weights on the next call.
$existingBundle = Join-Path $repoRoot "apps/desktop-avalonia/build/sidecar/core-sidecar"
if (-not $Force -and (Test-Path -LiteralPath $existingBundle -PathType Container)) {
    Write-Host "build_sidecar: target exists, skipping PyInstaller (use -Force to rebuild)"
    if (-not $SkipWeights) {
        Copy-MangaDetectorOnnx -Bundle $existingBundle -WeightsSource $WeightsSource
        Copy-MangaOcrOnnx -Bundle $existingBundle -OcrWeightsSource $OcrWeightsSource
        Copy-SfxWeights -Bundle $existingBundle -WeightsSource $SfxWeightsSource
    }
    # PLUGIN-RUNTIME-PACKAGED-PYTHON-1: the skip path must NOT leave the
    # bundle without its plugin-hook interpreter. Copy it when missing (or
    # always refresh it), then exit.
    if ($BundlePythonRuntime) {
        Copy-PluginPythonRuntime -Bundle $existingBundle -RuntimeDir $BundlePythonRuntime
    }
    exit 0
}

if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "build venv python not found: $PythonExe (create it per packaging/m2ac5/README.md)"
}
$PythonExe = (Resolve-Path -LiteralPath $PythonExe).Path

$gitHead = (git -C $repoRoot rev-parse HEAD 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $gitHead) { throw "Unable to resolve source HEAD at $repoRoot" }

$targetRoot = Join-Path $repoRoot "apps/desktop-avalonia/build/sidecar"
$distPath = Join-Path $targetRoot "core-sidecar"
$workPath = Join-Path $targetRoot "pyinstaller-work"

$pyinstallerVersion = (& $PythonExe -m PyInstaller --version)
Write-Host "build_sidecar: git HEAD=$gitHead pyinstaller=$pyinstallerVersion python=$PythonExe"

# M2-PACKAGED-AC1-ICU-ISOLATION-FIX (R-004): Sanitize local PATH during PyInstaller
# execution to isolate confirmed alien native toolchains (poppler) that leak into
# bindepend and harvest incompatible ICU binaries shadowing Windows System32 icuuc.dll.
$origPath = $env:PATH
try {
    $sanitizedEntries = @()
    $pathEntries = $env:PATH -split ';' | Where-Object {
        if (-not $_ -or -not (Test-Path -LiteralPath $_)) {
            return $false
        }
        # R-004: Restrict sanitization specifically to confirmed alien native toolchains
        if ($_ -match '(?i)[\\/]dependencies[\\/]native[\\/]poppler' -or $_ -match '(?i)[\\/]poppler[\\/].*bin') {
            $sanitizedEntries += $_
            return $false
        }
        return $true
    }
    $env:PATH = ($pathEntries -join ';')
    if ($sanitizedEntries.Count -gt 0) {
        Write-Host "build_sidecar: sanitized $($sanitizedEntries.Count) confirmed alien toolchain entries from PATH for PyInstaller execution:"
        foreach ($se in $sanitizedEntries) {
            Write-Host "  [PATH-SANITIZED] $se"
        }
    } else {
        Write-Host "build_sidecar: PATH checked for PyInstaller execution (0 alien toolchain entries found on PATH)"
    }

    & $PythonExe -m PyInstaller `
        --noconfirm `
        --clean `
        --distpath $distPath `
        --workpath $workPath `
        (Join-Path $repoRoot "packaging/m2ac5/core_sidecar.spec")
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed (exit=$LASTEXITCODE)" }
}
finally {
    $env:PATH = $origPath
}

# layout sanity gate: the Rust host resolves exactly these names
# (M2-PROD-SFX-PROBE-1: + sfx_detect_probe.exe, the one-shot frozen SFX-detect
# probe — not an IPC command, the catalog_loader precedent shape).
$bundle = Join-Path $distPath "core-sidecar"
foreach ($exe in @("host_bridge.exe", "core_service.exe", "acceptance_bridge.exe", "catalog_loader.exe", "sfx_detect_probe.exe")) {
    if (-not (Test-Path -LiteralPath (Join-Path $bundle $exe) -PathType Leaf)) {
        throw "sidecar bundle incomplete: missing $exe under $bundle"
    }
}

# M2-PACKAGED-AC1-ICU-ISOLATION-FIX (R-005): assert that no shadowing ICU binaries
# exist anywhere in the built bundle layout. Qt6Core requires Windows System32 icuuc.dll;
# bundling an unisolated or shadowing icuuc*.dll/icudt*.dll in the sidecar bundle root or _internal
# causes native WinError 127 symbol missing failure.
# Note: this is an explicit fail-closed safety constraint guarding against System32 shadowing
# rather than an assumption that no future consumer will ever need a versioned ICU.
$bundleIcuFiles = Get-ChildItem -Path $bundle -Recurse -File | Where-Object {
    $_.Name -like "icuuc*.dll" -or $_.Name -like "icudt*.dll"
}
if ($bundleIcuFiles.Count -gt 0) {
    $leakedList = ($bundleIcuFiles | ForEach-Object { $_.FullName }) -join "; "
    throw "sidecar bundle layout assertion FAILED (fail-closed policy): found unexpected ICU binaries in bundle that could shadow System32: $leakedList"
}
Write-Host "build_sidecar: verified 0 shadowing ICU binaries across bundle layout under $bundle (fail-closed guard satisfied)"

if (-not $SkipWeights) {
    Copy-MangaDetectorOnnx -Bundle $bundle -WeightsSource $WeightsSource
Copy-MangaOcrOnnx -Bundle $bundle -OcrWeightsSource $OcrWeightsSource
    Copy-SfxWeights -Bundle $bundle -WeightsSource $SfxWeightsSource
}
if ($BundlePythonRuntime) {
    Copy-PluginPythonRuntime -Bundle $bundle -RuntimeDir $BundlePythonRuntime
}
Write-Host "build_sidecar: OK -> $bundle (HEAD=$gitHead, pyinstaller=$pyinstallerVersion)"

