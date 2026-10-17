$iso = Join-Path $env:TEMP ('test-smoke-' + [guid]::NewGuid().ToString('N').Substring(0,8))
$udf = Join-Path $env:TEMP ('test-udf-' + [guid]::NewGuid().ToString('N').Substring(0,8))
$env:NEWMANGA_DATA_ROOT = $iso
$env:WEBVIEW2_USER_DATA_FOLDER = $udf
$env:RUST_BACKTRACE = '1'
$exe = 'G:\CODEX\New Manga\apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$errLog = Join-Path $env:TEMP 'test-smoke-err.log'
$outLog = Join-Path $env:TEMP 'test-smoke-out.log'

$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
Start-Sleep -Seconds 4
$exited = $p.HasExited
$code = if ($exited) { $p.ExitCode } else { 'RUNNING' }
Write-Host "Process: $($p.Id) Exited: $exited Code: $code"
if (Test-Path $errLog) {
    Write-Host "=== Stderr ==="
    Get-Content $errLog -Tail 15
}
if (-not $exited) {
    $p.CloseMainWindow() | Out-Null
    Start-Sleep -Seconds 1
    if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }
}
