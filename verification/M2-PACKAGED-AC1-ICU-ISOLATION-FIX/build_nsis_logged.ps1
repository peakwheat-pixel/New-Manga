$ErrorActionPreference = "Continue"
$repoRoot = "G:\CODEX\New Manga.worktrees\PACKAGED-AC1-ICU-ISOLATION-FIX-antigravity"
$desktopDir = Join-Path $repoRoot "apps\desktop"
Set-Location $desktopDir

$log = Join-Path $repoRoot "verification\M2-PACKAGED-AC1-ICU-ISOLATION-FIX\raw\nsis-build.log"
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$head = (git rev-parse HEAD).Trim()
$nodeVer = (node --version).Trim()
$tauriVer = "2.x (via npx @tauri-apps/cli@2)"

"COMMAND: npx.cmd --yes @tauri-apps/cli@2 build (CWD=apps/desktop)" | Set-Content -Path $log -Encoding utf8
"GIT_HEAD: $head" | Add-Content -Path $log -Encoding utf8
"NODE_VERSION: $nodeVer" | Add-Content -Path $log -Encoding utf8
"TAURI_CLI: $tauriVer" | Add-Content -Path $log -Encoding utf8
"START_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $log -Encoding utf8

cmd.exe /c "npx.cmd --yes @tauri-apps/cli@2 build" *>&1 | Tee-Object -FilePath $log -Append
$exitCode = $LASTEXITCODE
$sw.Stop()

"END_TIME: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $log -Encoding utf8
"EXIT: $exitCode" | Add-Content -Path $log -Encoding utf8
"ELAPSED_SECONDS: $($sw.Elapsed.TotalSeconds)" | Add-Content -Path $log -Encoding utf8

$installerPath = Join-Path $desktopDir "src-tauri\target\release\bundle\nsis\m2rc1-desktop_0.1.0_x64-setup.exe"
if (Test-Path $installerPath) {
    $item = Get-Item $installerPath
    $hash = (Get-FileHash -Path $installerPath -Algorithm SHA256).Hash.ToLowerInvariant()
    "INSTALLER_PATH: $($item.FullName)" | Add-Content -Path $log -Encoding utf8
    "INSTALLER_SIZE: $($item.Length)" | Add-Content -Path $log -Encoding utf8
    "INSTALLER_SHA256: $hash" | Add-Content -Path $log -Encoding utf8
} else {
    "INSTALLER_PATH: NOT_FOUND" | Add-Content -Path $log -Encoding utf8
}

exit $exitCode
