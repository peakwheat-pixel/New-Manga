$ErrorActionPreference = 'Stop'
# Closeout for rerun2: wait for graceful exit, then record process + SQLite lock evidence.
$runRoot = 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\host-simulation-20260926-rerun2'
$logs = Join-Path $runRoot 'logs'
$prior = 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\host-simulation-20260926-rerun1'
$libDb = Join-Path $prior '用户配置隔离\AppData\Local\New Manga\library.db'
$targetPid = 9320

$sw = [Diagnostics.Stopwatch]::StartNew()
$exited = $false
while ($sw.Elapsed.TotalSeconds -lt 30) {
  $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
  if (-not $proc) { $exited = $true; break }
  Start-Sleep -Milliseconds 250
}
$exitRecord = [ordered]@{
  run_id = 'host-simulation-20260926-rerun2'
  target_pid = $targetPid
  observed_exit_within_30s = $exited
  exit_code = 'NOT_CAPTURED (launcher did not WaitForExit in recovery run; process disappearance + no-residue + no-lock used instead)'
  exited_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
}
$exitRecord | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $logs 'process-exit.json') -Encoding utf8

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
$sidecars = Get-ChildItem -LiteralPath (Split-Path $libDb) -Filter 'library.db-*' -ErrorAction SilentlyContinue | Select-Object Name, Length
$afterHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $libDb).Hash.ToLowerInvariant()
$out = [ordered]@{
  exited = $exited
  newmanga_residue_processes = @($residue)
  sqlite_lock_probe = $lockProbe
  library_db_sidecar_files = @($sidecars)
  library_db_sha256_after = $afterHash
  captured_at_utc = [DateTimeOffset]::UtcNow.ToString('o')
}
$out | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $logs 'post-exit-check.json') -Encoding utf8
Write-Output ('EXITED=' + $exited)
Write-Output ('RESIDUE=' + (@($residue).Count))
Write-Output ('LOCK_PROBE=' + $lockProbe)
Write-Output ('LIB_DB_SHA256_AFTER=' + $afterHash)
