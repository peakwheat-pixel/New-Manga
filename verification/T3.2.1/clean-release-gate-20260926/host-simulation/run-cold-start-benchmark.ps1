$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
# AC9 cold-start benchmark: 5 launches of the fixed Build 2 package against an
# explicit --data-root (also the AC8 explicit --data-root evidence).
$artifactRoot = 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926'
$prior = Join-Path $artifactRoot 'host-simulation-20260926-rerun1'
$appDir = Join-Path $prior '程序目录只读\NewManga'
$exe = Join-Path $appDir 'NewManga.exe'
$benchRoot = Join-Path $artifactRoot 'cold-start-benchmark'
$dataRoot = Join-Path $benchRoot 'data-root'
$logs = Join-Path $benchRoot 'logs'
if (!(Test-Path -LiteralPath $exe)) { throw "Missing fixed package exe: $exe" }
New-Item -ItemType Directory -Path $dataRoot,$logs -Force | Out-Null

$pathValue = "$env:SystemRoot\System32;$env:SystemRoot"
$results = @()
for ($i = 1; $i -le 5; $i++) {
  $runLogs = Join-Path $logs ("run" + $i)
  New-Item -ItemType Directory -Path $runLogs -Force | Out-Null
  $stdout = Join-Path $runLogs 'app.stdout.log'
  $stderr = Join-Path $runLogs 'app.stderr.log'
  $env:PATH = $pathValue
  # Keep LOCALAPPDATA isolated per benchmark run as well; --data-root wins regardless.
  $env:LOCALAPPDATA = Join-Path $benchRoot ("la-run" + $i)
  $env:APPDATA = Join-Path $benchRoot ("ra-run" + $i)
  $env:TEMP = $runLogs
  $env:TMP = $runLogs
  @('NEWMANGA_DATA_ROOT','PYTHONPATH','PYTHONHOME','PYTHONUSERBASE','QML2_IMPORT_PATH','QML_IMPORT_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','PYINSTALLER_CONFIG_DIR') | ForEach-Object { Remove-Item -LiteralPath "Env:$_" -ErrorAction SilentlyContinue }

  $timer = [Diagnostics.Stopwatch]::StartNew()
  $startUtc = [DateTimeOffset]::UtcNow
  $p = Start-Process -FilePath $exe -WorkingDirectory $appDir -ArgumentList ('--data-root="' + $dataRoot + '"') -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
  $null = $p.Handle  # force process-handle cache so ExitCode is populated after WaitForExit
  $ready = $false
  $windowHandle = '0x0'
  while ($timer.Elapsed.TotalSeconds -lt 60) {
    try { $p.Refresh(); $windowHandle = ('0x{0:X}' -f $p.MainWindowHandle.ToInt64()) } catch {}
    if ($p.HasExited) { break }
    if ($p.MainWindowHandle -ne [IntPtr]::Zero) { $ready = $true; break }
    Start-Sleep -Milliseconds 50
  }
  $timer.Stop()
  $elapsed = [Math]::Round($timer.Elapsed.TotalMilliseconds / 1000, 3)
  if ($ready) { Start-Sleep -Seconds 2 }

  $closed = $false
  if (-not $p.HasExited) { $closed = $p.CloseMainWindow(); if ($closed -eq $true) { $p.WaitForExit(30000) | Out-Null } }
  Start-Sleep -Milliseconds 500
  $exitCode = if ($p.HasExited) { $p.ExitCode } else { $null }
  $timedOut = -not $p.HasExited
  if ($timedOut) { Stop-Process -Id $p.Id -Force; $p.WaitForExit() | Out-Null }
  $results += [ordered]@{
    run = $i
    pid = $p.Id
    started_at_utc = $startUtc.ToString('o')
    args = "--data-root $dataRoot"
    seconds_to_main_window_handle = $elapsed
    main_window_handle_ready = $ready
    graceful_close_requested = [bool]$closed
    exit_code = $exitCode
    forced_kill = $timedOut
  }
  Write-Output ("RUN" + $i + " PID=" + $p.Id + " READY=" + $ready + " ELAPSED=" + $elapsed + " EXIT=" + $exitCode)
}

$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $logs 'cold-start-results.json') -Encoding utf8
Write-Output 'BENCHMARK_COMPLETE'
