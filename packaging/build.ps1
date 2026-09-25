# Build script for New Manga Windows onedir package (T3.2.1)
[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [Parameter(Mandatory = $true)]
    [string]$PythonExe,

    [Parameter(Mandatory = $false)]
    [string]$WorkDir = "",

    [Parameter(Mandatory = $true)]
    [string]$ConfigDir
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path

if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "Python interpreter does not exist: $PythonExe"
}
$PythonExe = (Resolve-Path -LiteralPath $PythonExe).Path

# Query and record Git HEAD for build auditability (R-011)
$gitHead = (git -C $repoRoot rev-parse HEAD 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $gitHead) { throw "Unable to resolve source HEAD at $repoRoot" }
$gitStatus = @(git -C $repoRoot status --porcelain=v1)
if ($LASTEXITCODE -ne 0) { throw "Unable to inspect source working tree at $repoRoot" }
if ($gitStatus.Count -ne 0) { throw "Build source working tree is not clean; refusing uncommitted inputs" }
$sourceDateEpoch = (git -C $repoRoot show -s --format=%ct HEAD)
if ($LASTEXITCODE -ne 0 -or -not $sourceDateEpoch) { throw "Unable to resolve source commit timestamp" }

Write-Host "=== New Manga Package Build ==="
Write-Host "Repository root: $repoRoot"
Write-Host "Git Delivery Head: $gitHead"
Write-Host "Source tree: clean"
Write-Host "SOURCE_DATE_EPOCH: $sourceDateEpoch"
Write-Host "Python: $PythonExe"
Write-Host "Target output dir: $OutputDir"

# Resolve work and configuration directories. Existing paths are never cleaned.
if (-not $WorkDir) {
    $WorkDir = Join-Path ([System.IO.Path]::GetTempPath()) ("newmanga-buildwork-" + [System.Guid]::NewGuid().ToString("N"))
}
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
$WorkDir = [System.IO.Path]::GetFullPath($WorkDir)
$ConfigDir = [System.IO.Path]::GetFullPath($ConfigDir)
foreach ($path in @($OutputDir, $WorkDir, $ConfigDir)) {
    if (Test-Path -LiteralPath $path) {
        throw "Refusing to reuse an existing output/work/config directory: $path"
    }
    New-Item -ItemType Directory -Path $path | Out-Null
}

$specFile = Join-Path $repoRoot "packaging\new_manga.spec"
if (-not (Test-Path $specFile)) {
    throw "Spec file not found at: $specFile"
}

# Sanitize build PATH to prevent leaking unapproved host native binaries (T3.2.1-REPAIR-9)
$origPath = $env:PATH
$savedEnv = @{}
foreach ($name in @("PYTHONPATH", "PYTHONNOUSERSITE", "PYINSTALLER_CONFIG_DIR", "PYTHONDONTWRITEBYTECODE", "PYTHONHASHSEED", "SOURCE_DATE_EPOCH")) {
    $savedEnv[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}
$scriptsDir = Split-Path -Parent $PythonExe
$pythonDir = Split-Path -Parent $scriptsDir
$systemRoot = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Windows)
$system32 = Join-Path $systemRoot "System32"
$sysWbem = Join-Path $system32 "Wbem"
$sysPowershell = Join-Path $system32 "WindowsPowerShell\v1.0"

$cleanPath = @(
    $scriptsDir,
    $pythonDir,
    $system32,
    $systemRoot,
    $sysWbem,
    $sysPowershell
) -join [System.IO.Path]::PathSeparator

Write-Host "Sanitized build PATH: $cleanPath"
$env:PATH = $cleanPath

try {
    # Constrain import discovery to the supplied venv and source root.
    Write-Host "Running PyInstaller..."
    $env:PYTHONPATH = (Join-Path $repoRoot "src")
    $env:PYTHONNOUSERSITE = "1"
    $env:PYINSTALLER_CONFIG_DIR = $ConfigDir
    $env:PYTHONDONTWRITEBYTECODE = "1"
    $env:PYTHONHASHSEED = "0"
    $env:SOURCE_DATE_EPOCH = $sourceDateEpoch
    $prevEA = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    & $PythonExe -m PyInstaller --noconfirm --distpath $OutputDir --workpath $WorkDir $specFile
    $buildExit = $LASTEXITCODE

    $ErrorActionPreference = $prevEA
    if ($buildExit -ne 0) {
        throw "PyInstaller build failed with exit code: $buildExit"
    }

    $artifactDir = Join-Path $OutputDir "NewManga"
    if (-not (Test-Path $artifactDir)) {
        throw "Build artifact directory missing: $artifactDir"
    }

    $exePath = Join-Path $artifactDir "NewManga.exe"
    if (-not (Test-Path $exePath)) {
        throw "Target executable missing: $exePath"
    }

    # Verify Qt/ICU runtime symbol closure on built distribution (T3.2.1-REPAIR-9)
    $closureScript = Join-Path $repoRoot "packaging\check_qt_closure.py"
    if (-not (Test-Path $closureScript)) {
        throw "Closure check script missing: $closureScript"
    }
    Write-Host "Verifying Qt/ICU runtime symbol closure on built distribution..."
    $prevEA = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    & $PythonExe $closureScript --dist-dir $artifactDir
    $closureExit = $LASTEXITCODE

    $ErrorActionPreference = $prevEA
    if ($closureExit -ne 0) {
        throw "Qt/ICU runtime symbol closure verification failed with exit code: $closureExit"
    }

    # Generate SHA-256 manifest
    $manifestScript = Join-Path $repoRoot "packaging\manifest.py"
    $manifestFile = Join-Path $OutputDir "artifact-manifest.sha256"
    Write-Host "Generating SHA-256 manifest..."
    & $PythonExe $manifestScript --root $artifactDir --output $manifestFile
    if ($LASTEXITCODE -ne 0) {
        throw "Manifest generation failed with exit code: $LASTEXITCODE"
    }

    Write-Host "=== Build Completed Successfully ==="
    Write-Host "Artifact: $artifactDir"
    Write-Host "Manifest: $manifestFile"
} finally {
    $env:PATH = $origPath
    foreach ($name in $savedEnv.Keys) {
        [Environment]::SetEnvironmentVariable($name, $savedEnv[$name], "Process")
    }
}
