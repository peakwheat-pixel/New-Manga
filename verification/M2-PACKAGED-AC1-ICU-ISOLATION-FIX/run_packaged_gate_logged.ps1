$ErrorActionPreference = "Continue"
$repoRoot = "G:\CODEX\New Manga.worktrees\PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity"
Set-Location $repoRoot

$log = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\packaged-gate-execution.log"
$e2eLog = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\packaged-e2e.log"
$outDir = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\packaged"
$installer = Join-Path $repoRoot "apps\desktop\src-tauri\target\release\bundle\nsis\m2rc1-desktop_0.1.0_x64-setup.exe"
$runner = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\run_clean_start_e2e.py"
$pythonExe = "G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe"

$head = (git rev-parse HEAD).Trim()
$pyVer = (& $pythonExe --version).Trim()
$instItem = Get-Item $installer
$instHash = (Get-FileHash -Path $installer -Algorithm SHA256).Hash.ToLowerInvariant()

$header = @(
    "COMMAND: $pythonExe $runner --installer $installer --output-dir $outDir",
    "GIT_HEAD: $head",
    "PYTHON_INTERPRETER: $pythonExe ($pyVer)",
    "TESTED_INSTALLER_PATH: $($instItem.FullName)",
    "TESTED_INSTALLER_SIZE: $($instItem.Length)",
    "TESTED_INSTALLER_SHA256: $instHash",
    "START_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
)
$header | Set-Content -Path $log -Encoding utf8
$header | Set-Content -Path $e2eLog -Encoding utf8

$sw = [System.Diagnostics.Stopwatch]::StartNew()
& $pythonExe $runner --installer $installer --output-dir $outDir *>&1 | Tee-Object -FilePath $log -Append
$exitCode = $LASTEXITCODE
$sw.Stop()

$footer = @(
    "END_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "EXIT: $exitCode",
    "ELAPSED_SECONDS: $($sw.Elapsed.TotalSeconds)"
)
$footer | Add-Content -Path $log -Encoding utf8
$footer | Add-Content -Path $e2eLog -Encoding utf8

# Ensure e2eLog has full mirror of log
Get-Content -Path $log | Set-Content -Path $e2eLog -Encoding utf8

exit $exitCode
