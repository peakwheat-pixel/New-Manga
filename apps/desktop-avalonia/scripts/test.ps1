<#
.SYNOPSIS
  ONE-COMMAND gate: builds the new shell and runs all 57 tests against the real sidecars.

.DESCRIPTION
  Self-contained: prepares the AC11 unlabelled sidecar copy if missing, exports
  NEWMANGA_CORECLIENT_SIDECAR_DIR + NEWMANGA_EVIDENCE_DIR, runs `dotnet build -warnaserror`, then
  runs each test project separately with a deterministic TRX file and writes test/summary.json.
  With the fixture present every integration test executes (57 passed / 0 skipped); without the
  fixture plain `dotnet test` stays green via explicit Skips (see scripts/test-without-fixture.ps1).

.EXAMPLE
  pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1
#>
[CmdletBinding()]
param(
    [string]$Configuration = 'Debug',
    [string]$SidecarDirectory = 'G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy',
    [switch]$CanonicalEvidence
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')
# Reviewer reruns must never overwrite the pinned canonical evidence: default output goes to the
# workspace task-env. Only the owner regenerates pins with -CanonicalEvidence.
$evidence = if ($CanonicalEvidence) {
    Join-Path $repoRoot 'verification/UI-SHELL-THEME-1'
} else {
    'G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1/evidence-rerun'
}
$testEvidence = Join-Path $evidence 'test'
New-Item -ItemType Directory -Force -Path $testEvidence | Out-Null

if (-not (Test-Path (Join-Path $SidecarDirectory 'core_service.exe'))) {
    & (Join-Path $PSScriptRoot 'prepare-sidecar.ps1') -Destination $SidecarDirectory
}

$env:NEWMANGA_CORECLIENT_SIDECAR_DIR = (Resolve-Path $SidecarDirectory).Path
$env:NEWMANGA_EVIDENCE_DIR = (Resolve-Path $evidence).Path

$projects = @(
    @{ Name = 'coreclient'; Path = 'tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj' },
    @{ Name = 'host'; Path = 'tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj' },
    @{ Name = 'app'; Path = 'tests/NewManga.App.Tests/NewManga.App.Tests.csproj' }
)

$buildLog = Join-Path $evidence "build/dotnet-build-$Configuration.log"
New-Item -ItemType Directory -Force -Path (Split-Path $buildLog) | Out-Null
$testLog = Join-Path $testEvidence "dotnet-test-$Configuration.log"
Remove-Item $testLog -ErrorAction SilentlyContinue
Remove-Item (Join-Path $testEvidence "results-$Configuration.trx") -ErrorAction SilentlyContinue

Push-Location $root
try {
    & dotnet build NewManga.sln -c $Configuration -warnaserror 2>&1 | Tee-Object -FilePath $buildLog | Select-Object -Last 3
    if ($LASTEXITCODE -ne 0) { throw "dotnet build failed with exit code $LASTEXITCODE" }

    # AC1: regenerate the Rust production command surface in memory and compare with the committed snapshot.
    $python = (Get-Command python -ErrorAction SilentlyContinue)?.Source
    if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue)?.Source }
    if (-not $python) { throw "python is required for the AC1 command-surface extractor (scripts/extract-command-surface.py)" }
    & $python (Join-Path $root 'scripts/extract-command-surface.py') --check 2>&1 | Tee-Object -FilePath $testLog -Append
    if ($LASTEXITCODE -ne 0) { throw "AC1 command-surface extractor --check failed" }

    # AC3: re-probe the frozen core_service command surface used by the parity registry.
    $probeOutput = Join-Path $evidence 'parity/core-command-probe.json'
    New-Item -ItemType Directory -Force -Path (Split-Path $probeOutput) | Out-Null
    & (Join-Path $PSScriptRoot 'probe-core-commands.ps1') -SidecarDirectory $env:NEWMANGA_CORECLIENT_SIDECAR_DIR -OutputPath $probeOutput 2>&1 |
        Tee-Object -FilePath $testLog -Append

    $results = @()
    foreach ($project in $projects) {        $trx = Join-Path $testEvidence "results-$($project.Name).trx"
        Remove-Item $trx -ErrorAction SilentlyContinue
        & dotnet test $project.Path -c $Configuration --no-build `
            --logger "trx;LogFileName=$trx" --logger "console;verbosity=minimal" 2>&1 |
            Tee-Object -FilePath $testLog -Append
        $code = $LASTEXITCODE
        if (-not (Test-Path $trx)) { throw "missing trx for $($project.Name)" }

        [xml]$doc = Get-Content $trx -Raw
        $counter = $doc.TestRun.ResultSummary.Counters
        $skipped = @($doc.TestRun.Results.UnitTestResult | Where-Object outcome -eq 'NotExecuted')
        $results += [ordered]@{
            project = $project.Name
            total = [int]$counter.total
            passed = [int]$counter.passed
            failed = [int]$counter.failed
            skipped = $skipped.Count
            trx = "test/results-$($project.Name).trx"
            trx_sha256 = (Get-FileHash $trx -Algorithm SHA256).Hash.ToLowerInvariant()
        }
        if ($code -ne 0 -or [int]$counter.failed -ne 0) {
            throw "dotnet test $($project.Name) failed (exit=$code, failed=$($counter.failed))"
        }
    }
} finally {
    Pop-Location
}

$summary = [ordered]@{
    ac = 'AC1/AC2/AC3/AC4/AC5/AC6'
    command = 'pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1'
    evidence_root = $evidence
    configuration = $Configuration
    fixture = 'NEWMANGA_CORECLIENT_SIDECAR_DIR (AC11 unlabelled copy)'
    sidecar_directory = $env:NEWMANGA_CORECLIENT_SIDECAR_DIR
    projects = $results
    totals = [ordered]@{
        total = ($results | ForEach-Object { [int]$_.total } | Measure-Object -Sum).Sum
        passed = ($results | ForEach-Object { [int]$_.passed } | Measure-Object -Sum).Sum
        failed = ($results | ForEach-Object { [int]$_.failed } | Measure-Object -Sum).Sum
        skipped = ($results | ForEach-Object { [int]$_.skipped } | Measure-Object -Sum).Sum
    }
    at_utc = [DateTime]::UtcNow.ToString('o')
}
$summaryPath = Join-Path $testEvidence 'summary.json'
$summary | ConvertTo-Json -Depth 6 | Set-Content $summaryPath -Encoding utf8
$summary | ConvertTo-Json -Depth 4

Write-Output "log: $testLog"
Write-Output "evidence root: $evidence (use -CanonicalEvidence only when regenerating pins)"
Write-Output "summary: $summaryPath"
if ($summary.totals.failed -ne 0) { throw "totals failed=$($summary.totals.failed)" }
Write-Output "TEST PASS ($Configuration): $($summary.totals.passed)/$($summary.totals.total) passed, $($summary.totals.skipped) skipped"
