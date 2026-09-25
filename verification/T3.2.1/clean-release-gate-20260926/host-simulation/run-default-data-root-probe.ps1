$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
# AC8 default-data-root probe: launch the fixed package with NO overrides so it
# uses the real %LOCALAPPDATA%\New Manga; record creation, then close gracefully.
$artifactRoot = 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926'
$prior = Join-Path $artifactRoot 'host-simulation-20260926-rerun1'
$appDir = Join-Path $prior '程序目录只读\NewManga'
$exe = Join-Path $appDir 'NewManga.exe'
$logs = Join-Path $artifactRoot 'default-data-root-probe'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$realLocalAppData = [Environment]::GetFolderPath('LocalApplicationData')
$expectedRoot = Join-Path $realLocalAppData 'New Manga'
$existedBefore = Test-Path -LiteralPath $expectedRoot

$stdout = Join-Path $logs 'app.stdout.log'
$stderr = Join-Path $logs 'app.stderr.log'
$env:PATH = "$env:SystemRoot\System32;$env:SystemRoot"
Remove-Item -LiteralPath 'Env:NEWMANGA_DATA_ROOT' -ErrorAction SilentlyContinue
Remove-Item -LiteralPath 'Env:PYTHONPATH' -ErrorAction SilentlyContinue
Remove-Item -LiteralPath 'Env:PYTHONHOME' -ErrorAction SilentlyContinue
Remove-Item -LiteralPath 'Env:QT_PLUGIN_PATH' -ErrorAction SilentlyContinue

$timer = [Diagnostics.Stopwatch]::StartNew()
$p = Start-Process -FilePath $exe -WorkingDirectory $appDir -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
$null = $p.Handle
$ready = $false
while ($timer.Elapsed.TotalSeconds -lt 60) {
  try { $p.Refresh() } catch {}
  if ($p.HasExited) { break }
  if ($p.MainWindowHandle -ne [IntPtr]::Zero) { $ready = $true; break }
  Start-Sleep -Milliseconds 50
}
$elapsed = [Math]::Round($timer.Elapsed.TotalMilliseconds / 1000, 3)
Start-Sleep -Seconds 2
$createdNow = $false
if (Test-Path -LiteralPath $expectedRoot) {
  $createdNow = -not $existedBefore
}
$contents = if (Test-Path -LiteralPath $expectedRoot) { Get-ChildItem -LiteralPath $expectedRoot | Select-Object Name } else { @() }

$closed = $false
if (-not $p.HasExited) { $closed = $p.CloseMainWindow(); if ($closed -eq $true) { $p.WaitForExit(30000) | Out-Null } }
$exitCode = if ($p.HasExited) { $p.ExitCode } else { $null }
$timedOut = -not $p.HasExited
if ($timedOut) { Stop-Process -Id $p.Id -Force; $p.WaitForExit() | Out-Null }
$residue = Get-Process -Name 'NewManga' -ErrorAction SilentlyContinue | Select-Object Id

$out = [ordered]@{
  purpose = 'AC8 default data root (%LOCALAPPDATA%\New Manga) probe with no overrides'
  expected_root = $expectedRoot
  root_existed_before = $existedBefore
  root_present_after = (Test-Path -LiteralPath $expectedRoot)
  root_created_by_probe = $createdNow
  root_contents = @($contents)
  pid = $p.Id
  seconds_to_main_window_handle = $elapsed
  main_window_handle_ready = $ready
  graceful_close_requested = [bool]$closed
  exit_code = $exitCode
  forced_kill = $timedOut
  newmanga_residue = @($residue)
  captured_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
}
$out | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $logs 'default-data-root-probe.json') -Encoding utf8
Write-Output ('EXPECTED_ROOT=' + $expectedRoot)
Write-Output ('EXISTED_BEFORE=' + $existedBefore + ' PRESENT_AFTER=' + (Test-Path -LiteralPath $expectedRoot))
Write-Output ('READY=' + $ready + ' ELAPSED=' + $elapsed + ' EXIT=' + $exitCode + ' RESIDUE=' + @($residue).Count)
