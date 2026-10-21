# P09-MANAGED-READ-ROOT-TRUST-1 — per-suite regression runner (AC2/AC4).
#
# Suites MUST run in separate pytest processes: several suites do
# ``from conftest import ...`` and a combined invocation makes the wrong
# conftest win (baseline evidence: combining them fails collection).
#
# R-003 (Codex Review): every log carries an execution header (timestamp,
# shell, interpreter + resolved path, cwd, exact command) and the in-log
# ``EXIT=<code>`` line (protocol 09_COLLABORATION §6.12①).
#
# Usage (from the worktree root):
#   pwsh -NoProfile -File verification/P09-MANAGED-READ-ROOT-TRUST-1/run-suites.ps1
#
# Writes one log per suite plus summary.txt; exits non-zero if any suite fails.

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$logs = Join-Path $PSScriptRoot "logs"
New-Item -ItemType Directory -Force -Path $logs | Out-Null
$suites = @(
  "tests/core",
  "tests/storage",
  "tests/m2_resource_channel",
  "tests/security",
  "tests/library",
  "tests/reading_export",
  "tests/export",
  "tests/m2_acceptance"
)
$python = "C:/Python314/python.exe"
$pythonVersion = (& $python -c "import sys; print(sys.version.split()[0])" 2>&1) -join " "
$pythonPath = (& $python -c "import sys; print(sys.executable)" 2>&1) -join " "
$shell = "pwsh $($PSVersionTable.PSVersion.ToString())"
$os = [System.Environment]::OSVersion.VersionString
$summary = @()
$failed = $false
Push-Location $repo
try {
  foreach ($suite in $suites) {
    $name = $suite.Replace("tests/", "").Replace("/", "-")
    $log = Join-Path $logs "suite-$name.log"
    $command = "$python -m pytest $suite -q"
    $generated = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
    $body = & $python -m pytest $suite -q 2>&1 | Out-String
    $code = $LASTEXITCODE
    if ($code -ne 0) { $failed = $true }
    $header = @(
      "================================================================",
      "P09-MANAGED-READ-ROOT-TRUST-1 suite log",
      "generated : $generated",
      "shell     : $shell",
      "os        : $os",
      "python    : $python ($pythonVersion)",
      "python exe: $pythonPath",
      "cwd       : $repo",
      "suite     : $suite",
      "command   : $command",
      "exits     : pytest exit code recorded below as EXIT=<code>",
      "================================================================"
    )
    $header | Set-Content -Path $log -Encoding utf8
    Add-Content -Path $log -Value $body -Encoding utf8
    Add-Content -Path $log -Value "" -Encoding utf8
    Add-Content -Path $log -Value "EXIT=$code" -Encoding utf8
    $tail = ($body.Trim() -split "`r?`n" | Select-Object -Last 2) -join " | "
    $summary += "$suite exit=$code :: $tail"
    Write-Output "$suite exit=$code :: $tail"
  }
} finally {
  $summary | Set-Content -Path (Join-Path $logs "summary.txt") -Encoding utf8
  Pop-Location
}
if ($failed) { exit 1 }
exit 0
