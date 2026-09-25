$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
# Recovery run 2: reuse the rerun1 read-only program copy and isolated data root.
# New run/log id; never touches rerun1 logs/screenshots/database contents.
$artifactRoot = 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926'
$prior = Join-Path $artifactRoot 'host-simulation-20260926-rerun1'
$runRoot = Join-Path $artifactRoot 'host-simulation-20260926-rerun2'
$appDir = Join-Path $prior '程序目录只读\NewManga'
$exe = Join-Path $appDir 'NewManga.exe'
$profile = Join-Path $prior '用户配置隔离'
$localAppData = Join-Path $profile 'AppData\Local'
$roaming = Join-Path $profile 'AppData\Roaming'
$temp = Join-Path $runRoot 'temp'
$logs = Join-Path $runRoot 'logs'
$exports = Join-Path $runRoot 'exports'
if (!(Test-Path -LiteralPath $exe)) { throw "Missing fixed package exe: $exe" }
if (!(Test-Path -LiteralPath (Join-Path $localAppData 'New Manga\library.db'))) { throw "Missing isolated library.db to recover" }
if (Test-Path -LiteralPath $logs) { throw "Refusing to reuse run output: $runRoot" }
New-Item -ItemType Directory -Path $logs,$temp,$exports -Force | Out-Null

# Read-only before-snapshot of the recovery baseline (copy, not move).
$libDb = Join-Path $localAppData 'New Manga\library.db'
Copy-Item -LiteralPath $libDb -Destination (Join-Path $logs 'before-library.db.snapshot') -Force
$beforeHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $libDb).Hash.ToLowerInvariant()

$stdout = Join-Path $logs 'app.stdout.log'
$stderr = Join-Path $logs 'app.stderr.log'
$pathValue = "$env:SystemRoot\System32;$env:SystemRoot"
$os = Get-CimInstance Win32_OperatingSystem
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
  run_id = 'host-simulation-20260926-rerun2'
  purpose = 'restart recovery + pipeline diagnostic + reader export + graceful exit'
  data_root_reused = (Join-Path $localAppData 'New Manga')
  program_directory_reused = $appDir
  library_db_sha256_before = $beforeHash
  started_at_utc = $startUtc.ToString('o')
  pid = $p.Id
  effective_path = $pathValue
  localappdata = $env:LOCALAPPDATA
  app_window_handle = $windowHandle
  seconds_to_main_window_handle = [Math]::Round($timer.Elapsed.TotalMilliseconds / 1000, 3)
  main_window_handle_ready = $ready
  claim_scope = 'User-approved local host simulation; not a separate clean Windows machine or Sandbox.'
}
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $logs 'process-start.json') -Encoding utf8
Write-Output ('PID=' + $p.Id + '; WINDOW_HANDLE=' + $windowHandle + '; READY=' + $ready + '; ELAPSED_SECONDS=' + [Math]::Round($timer.Elapsed.TotalMilliseconds / 1000,3))
Write-Output ('LIB_DB_SHA256_BEFORE=' + $beforeHash)
Write-Output ('WAITING_FOR_INTERACTION')
