#!/usr/bin/env pwsh
# FEA-07-RESIDUAL-2 AC-R4a-3 (r1 P2-004, r2 R2-004): raw uiThreadSchedulingGapMs calibration.
#
# Runs the DEFAULT hot-switch test (which, since r2, only records uiThreadSchedulingGapMs and asserts the frozen
# p95 gate) three independent times and stores the raw per-round metrics, so the serial perf-gate budget has
# committed raw runs. This script applies NO gap assertion by construction — the gap assertion lives in the
# gated test and is run by tools/verify-fea07-perf.ps1.
#
# Usage (from the repository root):
#   pwsh -NoProfile -File verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1
#
# Outputs:
#   verification/FEA-07-RESIDUAL-2/evidence/ui-gap-calibration-r4a.json
#   verification/FEA-07-RESIDUAL-2/evidence/ui-gap-calibration-round{n}.json   (raw per-round metrics)
#   verification/FEA-07-RESIDUAL-2/logs/ui-gap-calibration.log
#   verification/FEA-07-RESIDUAL-2/logs/ui-gap-round{1,2,3}.log
#
# The 700 ms number below is the SERIAL PERF-GATE budget (see verify-fea07-perf.ps1); this script only reports
# the margin, it never asserts it.
param(
    [int]$Rounds = 3,
    [double]$PerfGateBudgetMs = 700
)

$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$evidenceDir = Join-Path $root 'verification/FEA-07-RESIDUAL-2/evidence'
$logsDir = Join-Path $root 'verification/FEA-07-RESIDUAL-2/logs'
$testProject = Join-Path $root 'apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj'
$filter = 'FullyQualifiedName~HotSwitch_P95MedianOfThreeIndependentRuns'

$roundData = @()
$summary = New-Object System.Collections.Generic.List[string]
$summary.Add('# uiThreadSchedulingGapMs raw 定标（FEA-07-RESIDUAL-2 AC-R4a-3 / r2 R2-004）')
$summary.Add('# 模式：raw（默认套件只记录 gap，不做 gap 断言；gap 断言在 gated 专用门禁）')
$summary.Add('# 命令：dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --filter "' + $filter + '"，每轮独立进程。')
$summary.Add('')

foreach ($round in 1..$Rounds) {
    $rawPath = Join-Path $env:TEMP "nm-fea07-uigap-round$round.json"
    if (Test-Path -LiteralPath $rawPath) {
        Remove-Item -LiteralPath $rawPath -Force
    }

    $env:NEWMANGA_FEA07_METRICS_PATH = $rawPath
    $output = & dotnet test $testProject -c Release --nologo --filter $filter 2>&1
    $exitCode = $LASTEXITCODE
    $roundLog = Join-Path $logsDir "ui-gap-round$round.log"
    $output | Out-File -FilePath $roundLog -Encoding utf8
    if ($exitCode -ne 0) {
        throw "round $round failed (exit $exitCode); see $roundLog (raw mode applies no gap assertion, so a failure here is the p95 gate)"
    }

    Copy-Item -LiteralPath $rawPath -Destination (Join-Path $evidenceDir "ui-gap-calibration-round$round.json") -Force
    $metrics = Get-Content -LiteralPath $rawPath -Raw | ConvertFrom-Json
    $roundData += [pscustomobject][ordered]@{
        round = $round
        worstGapMs = [double]$metrics.worstUiThreadSchedulingGapMs
        runGapsMs = @($metrics.runs | ForEach-Object { [double]$_.uiThreadSchedulingGapMs })
        uiThreadHeartbeatTicks = @($metrics.runs | ForEach-Object { [int]$_.uiThreadHeartbeatTicks })
        medianP95Ms = [double]$metrics.medianP95Ms
        worstRunP95Ms = [double]$metrics.worstRunP95Ms
        gapGateApplied = [bool]$metrics.gapGateApplied
        p95Passed = [bool]$metrics.p95Passed
    }
    $summary.Add("round ${round}: worstGap=$($metrics.worstUiThreadSchedulingGapMs) ms; runGaps=[$($roundData[-1].runGapsMs -join ', ')]; heartbeatTicks=[$($roundData[-1].uiThreadHeartbeatTicks -join ', ')]; medianP95=$($metrics.medianP95Ms) ms; gapGateApplied=$($metrics.gapGateApplied); p95Passed=$($metrics.p95Passed)")
}

$worst = ($roundData | Measure-Object -Property worstGapMs -Maximum).Maximum
$allGaps = @(@($roundData | ForEach-Object { $_.runGapsMs }) | Sort-Object)
$gapP95 = $allGaps[[Math]::Min($allGaps.Count - 1, [int][Math]::Ceiling(0.95 * $allGaps.Count) - 1)]
$margin = [Math]::Round(($PerfGateBudgetMs - $worst) / $PerfGateBudgetMs * 100, 2)

$calibration = [ordered]@{
    metric = 'FEA-07-RESIDUAL-2 AC-R4a-3 uiThreadSchedulingGapMs raw calibration'
    mode = 'raw (no gap assertion; the assertion is only in the gated serial perf gate)'
    perfGateBudgetMs = $PerfGateBudgetMs
    independentRounds = $Rounds
    frozenTest = 'NewManga.App.Tests.PerformanceBaselineTests.HotSwitch_P95MedianOfThreeIndependentRuns_StaysWithinTheFrozenW5Budget'
    command = 'dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --filter FullyQualifiedName~HotSwitch_P95MedianOfThreeIndependentRuns'
    heartbeatIntervalMs = 5
    perRoundShape = '4 warmup + 20 measured one-way switches; 3 sub-runs per round (the frozen median gate)'
    appliesTo = 'serial/idle runs; the default suite never asserts the gap (r2 R2-001)'
    rounds = $roundData
    worstGapMs = [double]$worst
    gapP95Ms = [double]$gapP95
    marginVsPerfGateBudgetPercent = $margin
    note = 'Raw calibration only. The gated assertion and its verdict live in evidence/perf-gate-r2a.json (tools/verify-fea07-perf.ps1).'
}

$jsonPath = Join-Path $evidenceDir 'ui-gap-calibration-r4a.json'
$json = $calibration | ConvertTo-Json -Depth 8
Set-Content -LiteralPath $jsonPath -Value $json -Encoding utf8

$summary.Add('')
$summary.Add("worstGap=$worst ms; gapP95=$gapP95 ms; perfGateBudget=$PerfGateBudgetMs ms; margin=$margin% (report only)")
$summary.Add("json: $jsonPath")
$summary.Add('')
$summary.Add($json)
Set-Content -LiteralPath (Join-Path $logsDir 'ui-gap-calibration.log') -Value $summary -Encoding utf8

Write-Output "raw-calibration worstGapMs=$worst gapP95Ms=$gapP95 marginVsPerfGateBudgetPercent=$margin"

