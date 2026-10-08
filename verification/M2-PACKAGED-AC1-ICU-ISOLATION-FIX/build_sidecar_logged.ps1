$ErrorActionPreference = "Continue"
$repoRoot = "G:\CODEX\New Manga.worktrees\PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity"
Set-Location $repoRoot

$log = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\sidecar-build.log"
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$head = (git rev-parse HEAD).Trim()

"COMMAND: pwsh -NoProfile -File packaging/m2ac5/build_sidecar.ps1 -Force" | Set-Content -Path $log -Encoding utf8
"GIT_HEAD: $head" | Add-Content -Path $log -Encoding utf8
"START_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $log -Encoding utf8

pwsh -NoProfile -File (Join-Path $repoRoot "packaging\m2ac5\build_sidecar.ps1") -Force *>&1 | Tee-Object -FilePath $log -Append
$exitCode = $LASTEXITCODE
$sw.Stop()

"END_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $log -Encoding utf8
"EXIT: $exitCode" | Add-Content -Path $log -Encoding utf8
"ELAPSED_SECONDS: $($sw.Elapsed.TotalSeconds)" | Add-Content -Path $log -Encoding utf8

exit $exitCode
