param(
    [string]$RepoRoot = 'G:\CODEX\New Manga'
)

$outLog = Join-Path $RepoRoot 'verification\P20\ac1-cargo-tauri-build.log'
$tauriDir = Join-Path $RepoRoot 'apps\desktop\src-tauri'

$startTime = (Get-Date).ToString('o')
"=== AC1 Probe: cargo tauri build ===" | Set-Content -Path $outLog -Encoding utf8
"Started at: $startTime" | Add-Content -Path $outLog -Encoding utf8
"Working directory: $tauriDir" | Add-Content -Path $outLog -Encoding utf8
"Command: cargo tauri build" | Add-Content -Path $outLog -Encoding utf8
"----------------------------------------" | Add-Content -Path $outLog -Encoding utf8

Push-Location $tauriDir
try {
    & cargo tauri build *>> $outLog
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}

$endTime = (Get-Date).ToString('o')
"----------------------------------------" | Add-Content -Path $outLog -Encoding utf8
"Exited at: $endTime" | Add-Content -Path $outLog -Encoding utf8
"Exit code: $code" | Add-Content -Path $outLog -Encoding utf8

Write-Host "AC1 probe finished with exit code $code"
exit $code
