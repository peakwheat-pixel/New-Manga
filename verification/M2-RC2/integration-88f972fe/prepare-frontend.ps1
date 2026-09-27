$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
Set-Location -LiteralPath $root
$log = Join-Path $PSScriptRoot 'frontend-setup.log'
$npm = (Get-Command npm).Source
$lines = @(
  'M2-RC2 frontend setup required by tauri generate_context! frontendDist',
  "started_utc=$([DateTime]::UtcNow.ToString('o'))",
  "shell=$($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)",
  "HEAD=$((& git rev-parse HEAD).Trim())",
  "npm=$npm / $((& $npm --version 2>&1) -join ' ')",
  'command=npm ci --prefix apps/desktop/frontend'
)
$output = & $npm ci --prefix apps/desktop/frontend 2>&1
$code = $LASTEXITCODE
$lines += @($output | ForEach-Object { [string]$_ }) + @("npm_ci_EXIT=$code")
if ($code -eq 0) {
  $lines += @('', 'command=npm run build --prefix apps/desktop/frontend')
  $output = & $npm run build --prefix apps/desktop/frontend 2>&1
  $code = $LASTEXITCODE
  $lines += @($output | ForEach-Object { [string]$_ }) + @("frontend_build_EXIT=$code")
}
$lines += "finished_utc=$([DateTime]::UtcNow.ToString('o'))"
[System.IO.File]::WriteAllLines($log, $lines, [System.Text.UTF8Encoding]::new($false))
if ($code -ne 0) { exit $code }
exit 0