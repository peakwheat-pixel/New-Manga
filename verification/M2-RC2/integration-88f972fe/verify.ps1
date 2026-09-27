$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
Set-Location -LiteralPath $repoRoot
$evidence = $PSScriptRoot
$head = (& git rev-parse HEAD).Trim()
$python = (Get-Command python).Source
$cargo = (Get-Command cargo).Source
$npm = (Get-Command npm).Source
$node = (Get-Command node).Source
$commands = @(
  @{ Name='pytest'; Exe=$python; Args=@('-m','pytest','tests/m2_resource_channel','-q') },
  @{ Name='cargo'; Exe=$cargo; Args=@('test','--manifest-path','apps/desktop/src-tauri/Cargo.toml','--locked') },
  @{ Name='vitest'; Exe=$npm; Args=@('test','--prefix','apps/desktop/frontend','--','--run') },
  @{ Name='e2e'; Exe=$python; Args=@('verification/M2-RC2/run_e2e.py') },
  @{ Name='probe-ttl-nan'; Exe=$python; Args=@('verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py') }
)
$versions = @(
  "shell=$($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)",
  "python=$python / $((& $python --version 2>&1) -join ' ')",
  "cargo=$cargo / $((& $cargo --version 2>&1) -join ' ')",
  "node=$node / $((& $node --version 2>&1) -join ' ')",
  "npm=$npm / $((& $npm --version 2>&1) -join ' ')",
  "HEAD=$head",
  "worktree=$repoRoot"
)
$failures = @()
foreach ($entry in $commands) {
  $started = [DateTime]::UtcNow.ToString('o')
  $commandLine = "$($entry.Exe) $($entry.Args -join ' ')"
  $commandArgs = $entry.Args
  $output = & $entry.Exe @commandArgs 2>&1
  $code = $LASTEXITCODE
  $finished = [DateTime]::UtcNow.ToString('o')
  $lines = @(
    'M2-RC2 Codex integration verification',
    "started_utc=$started",
    "finished_utc=$finished"
  ) + $versions + @("command=$commandLine", '') + @($output | ForEach-Object { [string]$_ }) + @("EXIT=$code")
  [System.IO.File]::WriteAllLines((Join-Path $evidence "$($entry.Name).log"), $lines, [System.Text.UTF8Encoding]::new($false))
  Write-Output "$($entry.Name): EXIT=$code"
  if ($code -ne 0) { $failures += "$($entry.Name)=$code" }
}
if ($failures.Count) { Write-Error ("Verification failures: " + ($failures -join ', ')); exit 1 }
exit 0