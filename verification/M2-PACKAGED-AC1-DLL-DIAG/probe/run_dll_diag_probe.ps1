<#
M2-PACKAGED-AC1-DLL-DIAG: minimal, read-only DLL-load probe (DSH; r1 review-fixed, NOT executed by DSH).

Contract for the executor (Codex):
  * fail-closed on the fixed installer input (R1): missing file or SHA256 drift THROWS (non-zero exit).
  * executes acceptance_bridge.exe ONLY from a self-owned lab copy that was copied successfully and
    hash-verified in this run (R2). Without -CopyBundle the script is STATIC-READ-ONLY and never
    starts the exe. A copy failure stops the run immediately. The original evidence bundle is never
    executed from and never written to.
  * writes ONLY under verification/M2-PACKAGED-AC1-DLL-DIAG/lab/ and .../raw/
  * never modifies the system PATH (the purge below is applied to the CHILD process env only)
  * never installs a dependency; uses the existing python at -PythonExe
  * does not touch src/apps/tests/packaging and prints no secrets

Steps: 1 installer hash gate (fail-closed) -> 2 static bundle closure enumeration
       -> 3 (optional) static installed-tree enumeration -> 4 copy bundle to own lab (no /MIR, no delete)
       -> 5 purged-PATH reproduction run (lab copy only) -> 6 PE import-table probe -> 7 manifest.

Usage:
  # static-only (default; never starts the packaged exe)
  pwsh -NoProfile -File verification/M2-PACKAGED-AC1-DLL-DIAG/probe/run_dll_diag_probe.ps1 `
    -InstallDir '<NSIS install dir of the clean-start lab>'
  # reproduction run: requires a verified lab copy
  pwsh -NoProfile -File verification/M2-PACKAGED-AC1-DLL-DIAG/probe/run_dll_diag_probe.ps1 -CopyBundle
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
function Fail([string]$m) { Say $m; Say 'ABORT=fail-closed'; Say "END=$((Get-Date).ToString('o'))"; throw $m }

Say "HOST=$([System.Environment]::OSVersion.VersionString); PS=$($PSVersionTable.PSVersion); PY=$PythonExe"
Say "BUNDLE=$Bundle"
Say "MODE=$(if ($CopyBundle) { 'copy-and-run' } else { 'static-read-only' })"
Say "START=$((Get-Date).ToString('o'))"

# ---- 1. installer hash gate: FIXED INPUT, FAIL-CLOSED (R1)
if (-not (Test-Path -LiteralPath $Installer -PathType Leaf)) {
    Fail "STEP1 installer-hash=FAIL_CLOSED installer not found: $Installer"
}
$h = (Get-FileHash -LiteralPath $Installer -Algorithm SHA256).Hash.ToLowerInvariant()
$instLen = (Get-Item -LiteralPath $Installer).Length
if ($h -ne $ExpectedInstallerSha256.ToLowerInvariant()) {
    Fail "STEP1 installer-hash=FAIL_CLOSED drift got=$h expected=$($ExpectedInstallerSha256.ToLowerInvariant()) bytes=$instLen"
}
Say "STEP1 installer-hash=PASS sha256=$h bytes=$instLen"

# ---- 2. static bundle closure enumeration (file existence only; NOT a load test)
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
Say 'STEP2 scope: ABSENT here means absent from THIS scanned built tree; it is NOT evidence about the installed tree or about load success/failure.'

# ---- 3. installed tree enumeration (static; fills the C12 UNKNOWN gap)
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
    } else { Say "STEP3 installed=NOT_RUN no resources\core-sidecar under $InstallDir" }
} else { Say 'STEP3 installed=NOT_RUN (pass -InstallDir to enumerate an installed tree)' }

# ---- 4. own-lab copy: copy-only (NO /MIR, no deletion sync), fail-closed (R2)
$RunBundle = $null
$CopyOk = $false
if ($CopyBundle) {
    $dst = Join-Path $Lab 'core-sidecar'
    Say "STEP4 lab-copy -> $dst (copy-only; no /MIR, no PURGE, source never modified)"
    robocopy $Bundle $dst /E /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    $rc = $LASTEXITCODE
    if ($rc -ge 8) { Say "STEP4 lab-copy=FAIL robocopy exit=$rc"; Say 'STEP4 -> reproduction step will NOT run (R2: copy failed)'; $CopyOk = $false }
    else {
        $checks = @('acceptance_bridge.exe', '_internal\PySide6\Qt6Gui.dll', '_internal\PySide6\Qt6Core.dll',
                    '_internal\PySide6\pyside6.abi3.dll', '_internal\shiboken6\shiboken6.abi3.dll')
        $bad = @()
        foreach ($rel in $checks) {
            $src = Join-Path $Bundle $rel
            $cpy = Join-Path $dst $rel
            if (-not (Test-Path -LiteralPath $cpy -PathType Leaf)) { $bad += "$rel (missing in lab: $cpy)"; continue }
            if (Test-Path -LiteralPath $src -PathType Leaf) {
                $a = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash
                $b = (Get-FileHash -LiteralPath $cpy -Algorithm SHA256).Hash
                if ($a -ne $b) { $bad += "$rel (sha256 mismatch src=$a lab=$b)" }
            }
        }
        if ($bad.Count -gt 0) { Say "STEP4 lab-copy=FAIL verification: $($bad -join '; ')"; Say 'STEP4 -> reproduction step will NOT run (R2)'; $CopyOk = $false }
        else { $RunBundle = $dst; $CopyOk = $true; Say "STEP4 lab-copy=OK verified robocopy_exit=$rc" }
    }
} else {
    Say 'STEP4 lab-copy=NOT_RUN (no -CopyBundle: static-read-only mode; the exe will not be started)'
}

# ---- 5. purged-PATH reproduction: own lab copy ONLY (never the original bundle)
if (-not $CopyOk) {
    Say 'STEP5 repro=NOT_RUN (no verified own-lab copy; R2 forbids starting the exe from the original bundle)'
} else {
    $exe = Join-Path $RunBundle 'acceptance_bridge.exe'
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
    Say "STEP5 repro EXIT=$code ELAPSED=$([math]::Round($sw.Elapsed.TotalSeconds,1))s log=$out lab=$RunBundle"
    Say "STEP5 traceback tail:`n$tail"
    if ($tail -match 'importing QtGui') { Say 'STEP5 verdict=REPRODUCED (same ImportError class)' }
    elseif ($code -eq 0) { Say 'STEP5 verdict=NO_REPRO (exit 0 in this isolated environment; original failure NOT reproduced; this does NOT mean the Gate is fixed)' }
    else { Say 'STEP5 verdict=DIFFERENT_FAILURE (see log)' }
}

# ---- 6. PE import-table probe (stdlib only; read-only; static scan targets)
$ScanBundle = if ($CopyOk) { $RunBundle } else { $Bundle }
if (Test-Path -LiteralPath $PythonExe -PathType Leaf) {
    $report = Join-Path $RawDir "pe-import-probe-$Stamp.json"
    & $PythonExe (Join-Path $ProbeRoot 'pe_import_probe.py') --bundle $ScanBundle --out $report 2>&1 |
        Tee-Object -FilePath $Log -Append
    Say "STEP6 pe-probe EXIT=$LASTEXITCODE report=$report scanned=$ScanBundle"
    Say 'STEP6 scope: import-table resolution is static; it is NOT a Windows loader (GetLastError) observation.'
} else { Say "STEP6 pe-probe=NOT_RUN python not found: $PythonExe" }

# ---- 7. manifest (paths + hashes only; no secrets)
$files = Get-ChildItem -LiteralPath $RawDir -File | Where-Object { $_.Name -like "*$Stamp*" }
foreach ($f in $files) {
    Say ("STEP7 artifact {0} bytes={1} sha256={2}" -f $f.Name, $f.Length,
        (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant())
}
Say "END=$((Get-Date).ToString('o')) log=$Log"
Say 'NOTE: no file was written into RUNNER-SNAPSHOT-DEBT-codex; system PATH was not modified.'
