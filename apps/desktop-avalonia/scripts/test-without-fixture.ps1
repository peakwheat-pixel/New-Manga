<#
.SYNOPSIS
  Proves that a bare `dotnet test` (no sidecar fixture env) is green: integration tests self-skip
  with an explicit reason instead of failing.

.DESCRIPTION
  Clears NEWMANGA_CORECLIENT_SIDECAR_DIR / NEWMANGA_EVIDENCE_DIR, runs all three test projects, and
  writes test/dotnet-test-Debug-no-fixture.log + test/no-fixture-summary.json with per-project
  counts and every skip reason. Fails if any test fails (skips are expected and listed).

.EXAMPLE
  pwsh -NoProfile -File apps/desktop-avalonia/scripts/test-without-fixture.ps1
#>
[CmdletBinding()]
param(
    [string]$Configuration = 'Debug',
    [switch]$CanonicalEvidence
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')
$evidence = if ($CanonicalEvidence) {
    Join-Path $repoRoot 'verification/UI-WORKBENCH-READER-1'
} else {
    'G:/CODEX/New Manga.workspace/task-envs/UI-WORKBENCH-READER-1/evidence-rerun'
}
$testEvidence = Join-Path $evidence 'test'
New-Item -ItemType Directory -Force -Path $testEvidence | Out-Null

# Intentionally no fixture: this is the plain-developer/CI scenario.
Remove-Item Env:NEWMANGA_CORECLIENT_SIDECAR_DIR -ErrorAction SilentlyContinue
Remove-Item Env:NEWMANGA_EVIDENCE_DIR -ErrorAction SilentlyContinue

$projects = @(
    @{ Name = 'coreclient'; Path = 'tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj' },
    @{ Name = 'host'; Path = 'tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj' },
    @{ Name = 'app'; Path = 'tests/NewManga.App.Tests/NewManga.App.Tests.csproj' }
)

$log = Join-Path $testEvidence "dotnet-test-$Configuration-no-fixture.log"
Remove-Item $log -ErrorAction SilentlyContinue
$tempResults = Join-Path ([IO.Path]::GetTempPath()) ('newmanga-no-fixture-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Force -Path $tempResults | Out-Null

$results = @()
Push-Location $root
try {
    foreach ($project in $projects) {
        $trx = Join-Path $tempResults "$($project.Name).trx"
        & dotnet test $project.Path -c $Configuration --no-build `
            --logger "trx;LogFileName=$trx" --logger "console;verbosity=normal" 2>&1 |
            Tee-Object -FilePath $log -Append
        $code = $LASTEXITCODE
        if (-not (Test-Path $trx)) { throw "missing trx for $($project.Name)" }

        [xml]$doc = Get-Content $trx -Raw
        $counter = $doc.TestRun.ResultSummary.Counters
        $skips = @()
        foreach ($result in @($doc.TestRun.Results.UnitTestResult | Where-Object outcome -eq 'NotExecuted')) {
            $reason = ''
            $message = $result.Output.ErrorInfo.Message
            if ($message) { $reason = ($message -replace '\s+', ' ').Trim() }
            $skips += [ordered]@{ test = $result.testName; reason = $reason }
        }

        $results += [ordered]@{
            project = $project.Name
            total = [int]$counter.total
            passed = [int]$counter.passed
            failed = [int]$counter.failed
            skipped = $skips.Count
            skip_list = $skips
        }
        if ($code -ne 0 -or [int]$counter.failed -ne 0) {
            throw "plain dotnet test $($project.Name) failed (exit=$code, failed=$($counter.failed))"
        }
    }
} finally {
    Pop-Location
    Remove-Item $tempResults -Recurse -Force -ErrorAction SilentlyContinue
}

$summary = [ordered]@{
    ac = 'AC6 reproducibility'
    command = 'dotnet test apps\desktop-avalonia\NewManga.sln   (no NEWMANGA_CORECLIENT_SIDECAR_DIR)'
    evidence_root = $evidence
    fixture = 'absent - integration tests self-skip with reason'
    projects = $results
    totals = [ordered]@{
        total = ($results | ForEach-Object { [int]$_.total } | Measure-Object -Sum).Sum
        passed = ($results | ForEach-Object { [int]$_.passed } | Measure-Object -Sum).Sum
        failed = ($results | ForEach-Object { [int]$_.failed } | Measure-Object -Sum).Sum
        skipped = ($results | ForEach-Object { [int]$_.skipped } | Measure-Object -Sum).Sum
    }
    at_utc = [DateTime]::UtcNow.ToString('o')
}
$summaryPath = Join-Path $testEvidence 'no-fixture-summary.json'
$summary | ConvertTo-Json -Depth 8 | Set-Content $summaryPath -Encoding utf8
$summary | ConvertTo-Json -Depth 5

Write-Output "evidence root: $evidence (use -CanonicalEvidence only when regenerating pins)"
Write-Output "log: $log"
if ($summary.totals.failed -ne 0) { throw "plain run must not fail" }
Write-Output "PLAIN RUN GREEN: $($summary.totals.passed)/$($summary.totals.total) passed, $($summary.totals.skipped) skipped (all with reasons)"
