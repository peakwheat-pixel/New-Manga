$ErrorActionPreference = "Continue"
$repoRoot = "G:\CODEX\New Manga.worktrees\PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity"
$log = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\acceptance-bridge-purged-path.log"
$exe = Join-Path $repoRoot "apps\desktop\src-tauri\target\core-sidecar\core-sidecar\acceptance_bridge.exe"

$labDir = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\lab_acceptance_test"
if (Test-Path $labDir) { Remove-Item -Path $labDir -Recurse -Force }
New-Item -ItemType Directory -Path $labDir -Force | Out-Null

$head = (git rev-parse HEAD).Trim()
"COMMAND: Start-Process $exe (purged PATH=C:\Windows\System32;C:\Windows, M2AC1_TEST_MODE=1, QT_QPA_PLATFORM=offscreen, stdin=EOF)" | Set-Content -Path $log -Encoding utf8
"GIT_HEAD: $head" | Add-Content -Path $log -Encoding utf8
"START_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $log -Encoding utf8

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe
$psi.EnvironmentVariables["PATH"] = "C:\Windows\System32;C:\Windows"
$psi.EnvironmentVariables["M2AC1_TEST_MODE"] = "1"
$psi.EnvironmentVariables["QT_QPA_PLATFORM"] = "offscreen"
$psi.EnvironmentVariables["NEWMANGA_DATA_ROOT"] = $labDir
$psi.EnvironmentVariables["LOCALAPPDATA"] = $labDir
$psi.EnvironmentVariables["APPDATA"] = $labDir
$psi.EnvironmentVariables["TEMP"] = $labDir
$psi.EnvironmentVariables["TMP"] = $labDir
$psi.UseShellExecute = $false
$psi.RedirectStandardInput = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true

$proc = [System.Diagnostics.Process]::Start($psi)
# Close stdin immediately to signal EOF to server.serve_forever()
$proc.StandardInput.Close()

$stdout = $proc.StandardOutput.ReadToEnd()
$stderr = $proc.StandardError.ReadToEnd()
$proc.WaitForExit(15000) # 15s timeout
$sw.Stop()

"END_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $log -Encoding utf8
"EXIT: $($proc.ExitCode)" | Add-Content -Path $log -Encoding utf8
"ELAPSED_SECONDS: $($sw.Elapsed.TotalSeconds)" | Add-Content -Path $log -Encoding utf8
"STDOUT:`n$stdout" | Add-Content -Path $log -Encoding utf8
"STDERR:`n$stderr" | Add-Content -Path $log -Encoding utf8

Get-Content -Path $log
