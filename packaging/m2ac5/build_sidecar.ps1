# M2-AC5 sidecar build script (build tooling only).
#
# Runs PyInstaller with the frozen spec and drops the onedir bundle into the
# desktop target tree (`apps/desktop/src-tauri/target/core-sidecar/`), which
# the tauri bundle then declares as `resources` (see tauri.conf.json). The
# output lives under the gitignored `target/` tree so build artifacts can
# never enter a commit.
#
# Usage (from the repository root):
#   powershell -File packaging/m2ac5/build_sidecar.ps1 [-PythonExe <path>]
#
# The default build venv is the dedicated M2-AC5 build env (pyinstaller only;
# see packaging/m2ac5/requirements-build.txt).

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$PythonExe = "G:/CODEX/New Manga.task-envs/m2ac5-build/Scripts/python.exe",
    # M2-AC5-BUILD-FRESH-CHECKOUT: force a full PyInstaller rebuild even when
    # the onedir bundle already exists (default: incremental short-circuit).
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path

# M2-AC5-BUILD-FRESH-CHECKOUT: incremental short-circuit. When the target
# onedir bundle is already present, skip the (expensive) PyInstaller rebuild
# and exit 0 so automated callers can invoke this unconditionally. The check
# runs before the build-venv probe on purpose: taking the skip path must not
# require the build venv to exist. Use -Force for a full rebuild (all other
# behavior, parameters and the output layout are unchanged).
$existingBundle = Join-Path $repoRoot "apps/desktop/src-tauri/target/core-sidecar/core-sidecar"
if (-not $Force -and (Test-Path -LiteralPath $existingBundle -PathType Container)) {
    Write-Host "build_sidecar: target exists, skipping (use -Force to rebuild)"
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
Write-Host "build_sidecar: OK -> $bundle (HEAD=$gitHead, pyinstaller=$pyinstallerVersion)"
