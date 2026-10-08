<#
M2-PACKAGED-AC1-DLL-DIAG: minimal, read-only DLL-load probe (created by DSH, NOT executed by DSH).

Contract for the executor (Codex):
  * writes ONLY under verification/M2-PACKAGED-AC1-DLL-DIAG/lab/ and .../raw/
  * never writes into G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex
  * never modifies the system PATH (the purge below is applied to the CHILD process env only)
  * never installs a dependency; uses the existing python at -PythonExe
  * does not touch src/apps/tests/packaging and prints no secrets

Steps: 1 hash gate -> 2 enumerate bundle closure -> 3 (optional) enumerate installed tree
       -> 4 copy bundle to lab (opt-in) -> 5 purged-PATH reproduction run
       -> 6 PE import-table probe -> 7 manifest.

Usage:
  pwsh -NoProfile -File verification/M2-PACKAGED-AC1-DLL-DIAG/probe/run_dll_diag_probe.ps1
  # optional, to use a real NSIS install tree for step 3/5:
  #   -InstallDir 'C:\...\m2ac5-cleanstart-xxxx\install'
  # optional, when the bundle must be copied to the lab before execution:
  #   -CopyBundle
#>
[CmdletBinding()]
param(
    [string]$Bundle = 'G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex/apps/desktop/src-tauri/target/core-sidecar/core-sidecar',
    [string]$Installer = 'G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex/apps/desktop/src-tauri/target/release/bundle/nsis/m2rc1-desktop_0.1.0_x64-setup.exe',
    [string]$ExpectedInstallerSha256 = '1cecca95d25439fca682cbe4336123d3b3352db229dd58c4e7d724b4d6c6ccb8',
    [string]$PythonExe = 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe',
    [string]$InstallDir = '',
    [switch]$CopyBundle
)

$ErrorActionPreference = 'Stop'
$ProbeRoot = Split-Path -Parent $PSCommandPath
$TaskRoot = Split-Path -Parent $ProbeRoot
$Stamp = (Get-Date).ToString('yyyyMMdd-HHmmss')
$RawDir = Join-Path $TaskRoot 'raw'
$LabRoot = Join-Path $TaskRoot 'lab'
$Lab = Join-Path $LabRoot $Stamp
New-Item -ItemType Directory -Force -Path $RawDir, $Lab | Out-Null
$Log = Join-Path $RawDir "probe-$Stamp.log"

function Say([string]$m) { $m | Tee-Object -FilePath $Log -Append }

Say "HOST=$([System.Environment]::OSVersion.VersionString); PS=$($PSVersionTable.PSVersion); PY=$PythonExe"
Say "BUNDLE=$Bundle"
Say "START=$((Get-Date).ToString('o'))"

# ---- 1. installer hash gate (fixed input, re-measured; no write to the evidence tree)
if (Test-Path -LiteralPath $Installer -PathType Leaf) {
    $h = (Get-FileHash -LiteralPath $Installer -Algorithm SHA256).Hash.ToLowerInvariant()
    $len = (Get-Item -LiteralPath $Installer).Length
    if ($h -eq $ExpectedInstallerSha256) { Say "STEP1 installer-hash=PASS sha256=$h bytes=$len" }
    else { Say "STEP1 installer-hash=DRIFT got=$h expected=$ExpectedInstallerSha256 bytes=$len" }
} else { Say "STEP1 installer-hash=BLOCKED installer not found: $Installer" }

# ---- 2. bundle closure enumeration (file existence only; NOT a load test)
$expect = @(
    '_internal/PySide6/Qt6Core.dll', '_internal/PySide6/Qt6Gui.dll',
    '_internal/PySide6/QtCore.pyd', '_internal/PySide6/QtGui.pyd',
    '_internal/PySide6/pyside6.abi3.dll', '_internal/shiboken6/shiboken6.abi3.dll',
    '_internal/msvcp140.dll', '_internal/VCRUNTIME140.dll', '_internal/VCRUNTIME140_1.dll',
    '_internal/ucrtbase.dll', '_internal/python312.dll',
    '_internal/icuuc.dll', '_internal/icudt78.dll', '_internal/icuin.dll', '_internal/icuin78.dll',
    '_internal/d3dcompiler_47.dll', '_internal/opengl32sw.dll',
    '_internal/PySide6/Qt/plugins/platforms/qoffscreen.dll'
)
foreach ($rel in $expect) {
    $full = Join-Path $Bundle ($rel -replace '/', '\')
    $state = if (Test-Path -LiteralPath $full -PathType Leaf) { 'PRESENT' } else { 'ABSENT' }
    Say "STEP2 closure $state $rel"
}
$pyd = Get-ChildItem -LiteralPath (Join-Path $Bundle '_internal\PySide6') -Filter '*.pyd' -ErrorAction SilentlyContinue |
    ForEach-Object { $_.Name }
Say "STEP2 PySide6 pyd files: $($pyd -join ', ')"
$topDll = Get-ChildItem -LiteralPath (Join-Path $Bundle '_internal') -Filter '*.dll' -ErrorAction SilentlyContinue |
    ForEach-Object { $_.Name } | Sort-Object
Say "STEP2 _internal top-level dll count=$($topDll.Count)"
Say "STEP2 _internal top-level dlls: $($topDll -join ', ')"

# ---- 3. installed tree enumeration (fills the C12 UNKNOWN gap)
if ($InstallDir) {
    $inst = Join-Path $InstallDir 'resources\core-sidecar'
    if (Test-Path -LiteralPath $inst -PathType Container) {
        foreach ($rel in $expect) {
            $full = Join-Path $inst ($rel -replace '/', '\')
            $state = if (Test-Path -LiteralPath $full -PathType Leaf) { 'PRESENT' } else { 'ABSENT' }
            Say "STEP3 installed $state $rel"
        }
        $instDll = Get-ChildItem -LiteralPath (Join-Path $inst '_internal') -Filter '*.dll' -ErrorAction SilentlyContinue |
            ForEach-Object { $_.Name } | Sort-Object
        Say "STEP3 installed _internal dll count=$($instDll.Count)"
    } else { Say "STEP3 installed=BLOCKED no resources\core-sidecar under $InstallDir" }
} else { Say "STEP3 installed=NOT_RUN (pass -InstallDir to enumerate an installed tree)" }

# ---- 4. optional lab copy (the only way to execute without writing into the evidence tree)
$RunBundle = $Bundle
if ($CopyBundle) {
    $dst = Join-Path $Lab 'core-sidecar'
    Say "STEP4 lab-copy -> $dst"
    robocopy $Bundle $dst /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { Say "STEP4 lab-copy=FAIL robocopy exit=$LASTEXITCODE" } else { $RunBundle = $dst; Say "STEP4 lab-copy=OK" }
}

# ---- 5. purged-PATH reproduction of the packaged import failure
$exe = Join-Path $RunBundle 'acceptance_bridge.exe'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    Say 'STEP5 repro=NOT_RUN acceptance_bridge.exe not found'
} else {
    $shim = Join-Path $Lab 'appdata'
    foreach ($d in 'roaming', 'local', 'temp') { New-Item -ItemType Directory -Force -Path (Join-Path $shim $d) | Out-Null }
    $env:PATH = "$env:SystemRoot\System32;$env:SystemRoot"
    $env:APPDATA = Join-Path $shim 'roaming'
    $env:LOCALAPPDATA = Join-Path $shim 'local'
    $env:TEMP = Join-Path $shim 'temp'
    $env:TMP = $env:TEMP
    $env:M2AC1_TEST_MODE = '1'
    $env:QT_QPA_PLATFORM = 'offscreen'
    $out = Join-Path $RawDir "probe-ac1-run-$Stamp.log"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $exe *> $out
    $code = $LASTEXITCODE
    $sw.Stop()
    $tail = (Get-Content -LiteralPath $out -Tail 25) -join "`n"
    Say "STEP5 repro EXIT=$code ELAPSED=$([math]::Round($sw.Elapsed.TotalSeconds,1))s log=$out"
    Say "STEP5 traceback tail:`n$tail"
    if ($tail -match 'importing QtGui') { Say 'STEP5 verdict=REPRODUCED (same ImportError class)' }
    elseif ($code -eq 0) { Say 'STEP5 verdict=NO_REPRO (exit 0 in this environment; original failure NOT reproduced)' }
    else { Say 'STEP5 verdict=DIFFERENT_FAILURE (see log)' }
}

# ---- 6. PE import-table probe (stdlib only; read-only)
if (Test-Path -LiteralPath $PythonExe -PathType Leaf) {
    $report = Join-Path $RawDir "pe-import-probe-$Stamp.json"
    & $PythonExe (Join-Path $ProbeRoot 'pe_import_probe.py') --bundle $RunBundle --out $report 2>&1 |
        Tee-Object -FilePath $Log -Append
    Say "STEP6 pe-probe EXIT=$LASTEXITCODE report=$report"
} else { Say "STEP6 pe-probe=NOT_RUN python not found: $PythonExe" }

# ---- 7. manifest (paths + hashes only; no secrets)
$files = Get-ChildItem -LiteralPath $RawDir -File | Where-Object { $_.Name -like "*$Stamp*" }
foreach ($f in $files) {
    Say ("STEP7 artifact {0} bytes={1} sha256={2}" -f $f.Name, $f.Length,
        (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant())
}
Say "END=$((Get-Date).ToString('o')) log=$Log"
Say 'NOTE: no file was written into RUNNER-SNAPSHOT-DEBT-codex; system PATH was not modified.'
