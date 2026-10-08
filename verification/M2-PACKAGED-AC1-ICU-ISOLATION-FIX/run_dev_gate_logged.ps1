$ErrorActionPreference = "Continue"
$repoRoot = "G:\CODEX\New Manga.worktrees\PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity"
Set-Location $repoRoot

$log = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\dev-gate-execution.log"
$devE2eLog = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\dev-e2e.log"
$outDir = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\dev"
$exePath = Join-Path $repoRoot "apps\desktop\src-tauri\target\release\m2rc1-desktop.exe"
$runner = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\run_e2e.py"
$pythonExe = "G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe"



$head = (git rev-parse HEAD).Trim()
$pyVer = (& $pythonExe --version).Trim()

$header = @(
    "COMMAND: $pythonExe $runner --exe $exePath --skip-build --output-dir $outDir",
    "GIT_HEAD: $head",
    "PYTHON_INTERPRETER: $pythonExe ($pyVer)",
    "START_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)
$header | Set-Content -Path $log -Encoding utf8
$header | Set-Content -Path $devE2eLog -Encoding utf8

$sw = [System.Diagnostics.Stopwatch]::StartNew()
& $pythonExe $runner --exe $exePath --skip-build --output-dir $outDir *>&1 | Tee-Object -FilePath $log -Append
$exitCode = $LASTEXITCODE
$sw.Stop()

$footer = @(
    "END_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "EXIT: $exitCode",
    "ELAPSED_SECONDS: $($sw.Elapsed.TotalSeconds)"
)
$footer | Add-Content -Path $log -Encoding utf8
$footer | Add-Content -Path $devE2eLog -Encoding utf8

# Copy full output to dev-e2e.log as well
Get-Content -Path $log | Set-Content -Path $devE2eLog -Encoding utf8

exit $exitCode
