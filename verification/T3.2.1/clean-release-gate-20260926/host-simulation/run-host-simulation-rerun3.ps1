$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
# Recovery run 3 (final restoration confirmation): reuse rerun1 read-only program copy
# and isolated data root; new run id; launcher waits for exit and captures the exit code.
$artifactRoot = 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926'
$prior = Join-Path $artifactRoot 'host-simulation-20260926-rerun1'
$runRoot = Join-Path $artifactRoot 'host-simulation-20260926-rerun3'
$appDir = Join-Path $prior '程序目录只读\NewManga'
$exe = Join-Path $appDir 'NewManga.exe'
$profile = Join-Path $prior '用户配置隔离'
$localAppData = Join-Path $profile 'AppData\Local'
$roaming = Join-Path $profile 'AppData\Roaming'
$temp = Join-Path $runRoot 'temp'
$logs = Join-Path $runRoot 'logs'
if (!(Test-Path -LiteralPath $exe)) { throw "Missing fixed package exe: $exe" }
if (Test-Path -LiteralPath $logs) { throw "Refusing to reuse run output: $runRoot" }
New-Item -ItemType Directory -Path $logs,$temp -Force | Out-Null

$libDb = Join-Path $localAppData 'New Manga\library.db'
$beforeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $libDb).Hash.ToLowerInvariant()
$stdout = Join-Path $logs 'app.stdout.log'
$stderr = Join-Path $logs 'app.stderr.log'
$pathValue = "$env:SystemRoot\System32;$env:SystemRoot"
$env:PATH = $pathValue
$env:LOCALAPPDATA = $localAppData
$env:APPDATA = $roaming
$env:TEMP = $temp
$env:TMP = $temp
@('NEWMANGA_DATA_ROOT','PYTHONPATH','PYTHONHOME','PYTHONUSERBASE','QML2_IMPORT_PATH','QML_IMPORT_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','PYINSTALLER_CONFIG_DIR') | ForEach-Object { Remove-Item -LiteralPath "Env:$_" -ErrorAction SilentlyContinue }
$timer = [Diagnostics.Stopwatch]::StartNew()
$startUtc = [DateTimeOffset]::UtcNow
$p = Start-Process -FilePath $exe -WorkingDirectory $appDir -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
$ready = $false
$windowHandle = '0x0'
while ($timer.Elapsed.TotalSeconds -lt 60) {
  try { $p.Refresh(); $windowHandle = ('0x{0:X}' -f $p.MainWindowHandle.ToInt64()) } catch {}
  if ($p.HasExited) { break }
  if ($p.MainWindowHandle -ne [IntPtr]::Zero) { $ready = $true; break }
  Start-Sleep -Milliseconds 200
}
$timer.Stop()
$record = [ordered]@{
  run_id = 'host-simulation-20260926-rerun3'
  purpose = 'final restart-recovery confirmation against rerun1 isolated data root'
  data_root_reused = (Join-Path $localAppData 'New Manga')
  library_db_sha256_before = $beforeHash
  started_at_utc = $startUtc.ToString('o')
  pid = $p.Id
  effective_path = $pathValue
  app_window_handle = $windowHandle
  seconds_to_main_window_handle = [Math]::Round($timer.Elapsed.TotalMilliseconds / 1000, 3)
  main_window_handle_ready = $ready
  claim_scope = 'User-approved local host simulation; not a separate clean Windows machine or Sandbox.'
}
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $logs 'process-start.json') -Encoding utf8
Write-Output ('PID=' + $p.Id + '; READY=' + $ready + '; ELAPSED_SECONDS=' + [Math]::Round($timer.Elapsed.TotalMilliseconds / 1000,3))

$p.WaitForExit()
$exitCode = $p.ExitCode
Start-Sleep -Seconds 2
$residue = Get-Process -Name 'NewManga' -ErrorAction SilentlyContinue | Select-Object Id, ProcessName
$lockProbe = $null
try {
  $fs = [IO.File]::Open($libDb, 'Open', 'ReadWrite', 'None')
  $fs.Close(); $fs.Dispose()
  $lockProbe = 'EXCLUSIVE_OPEN_OK (no SQLite file lock held after exit)'
} catch {
  $lockProbe = 'LOCKED: ' + $_.Exception.Message
}
$afterHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $libDb).Hash.ToLowerInvariant()
$exit = [ordered]@{
  run_id = 'host-simulation-20260926-rerun3'
  pid = $p.Id
  exit_code = $exitCode
  exited_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
  newmanga_residue_processes = @($residue)
  sqlite_lock_probe = $lockProbe
  library_db_sha256_after = $afterHash
}
$exit | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $logs 'process-exit.json') -Encoding utf8
Write-Output ('PROCESS_EXIT=' + $exitCode)
Write-Output ('RESIDUE=' + @($residue).Count + '; LOCK_PROBE=' + $lockProbe)
