# P09-MANAGED-READ-ROOT-TRUST-1 — per-suite regression runner (AC2/AC4).
#
# Suites MUST run in separate pytest processes: several suites do
# ``from conftest import ...`` and a combined invocation makes the wrong
# conftest win (baseline evidence: combining them fails collection).
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
$summary = @()
$failed = $false
Push-Location $repo
try {
  foreach ($suite in $suites) {
    $name = $suite.Replace("tests/", "").Replace("/", "-")
    $log = Join-Path $logs "suite-$name.log"
    & $python -m pytest $suite -q > $log 2>&1
    $code = $LASTEXITCODE
    if ($code -ne 0) { $failed = $true }
    $tail = (Get-Content $log -Tail 2) -join " | "
    $summary += "$suite exit=$code :: $tail"
    Write-Output "$suite exit=$code :: $tail"
  }
} finally {
  Pop-Location
}
$summary | Set-Content -Path (Join-Path $logs "summary.txt") -Encoding utf8
if ($failed) { exit 1 }
exit 0
