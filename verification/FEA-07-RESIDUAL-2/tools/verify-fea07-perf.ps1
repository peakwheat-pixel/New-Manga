#!/usr/bin/env pwsh
# FEA-07-RESIDUAL-2 AC-R4a-3 (r2 R2-001): the dedicated serial performance gate.
#
# Runs the gated test (NEWMANGA_FEA07_PERF=1) that asserts uiThreadSchedulingGapMs in addition to the frozen
# p95 gate. This script is NOT part of the default test gate: the metric is load-sensitive (parallel
# full-suite run: 513.55 ms; serial: 249.44 ms), so the default suite only records it.
#
# Usage (from the repository root):
#   pwsh -NoProfile -File verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1
#   pwsh -NoProfile -File verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1 -Rounds 2
#
# Outputs:
#   verification/FEA-07-RESIDUAL-2/evidence/perf-gate-r2a.json   (rounds + distribution + verdict)
#   verification/FEA-07-RESIDUAL-2/evidence/perf-gate-round{n}.json (raw per-round metrics)
#   verification/FEA-07-RESIDUAL-2/logs/perf-gate.log
#   verification/FEA-07-RESIDUAL-2/logs/perf-gate-round{n}.log
param(
    [int]$Rounds = 3
)

$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$evidenceDir = Join-Path $root 'verification/FEA-07-RESIDUAL-2/evidence'
$logsDir = Join-Path $root 'verification/FEA-07-RESIDUAL-2/logs'
$testProject = Join-Path $root 'apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj'
$filter = 'FullyQualifiedName~Gated_HotSwitch_UiThreadSchedulingGapStaysWithinThePerfGateBudget'

$env:NEWMANGA_FEA07_PERF = '1'
$roundsData = @()
$summary = New-Object System.Collections.Generic.List[string]
$summary.Add('# FEA-07-RESIDUAL-2 AC-R4a-3 专用性能门禁（串行；NEWMANGA_FEA07_PERF=1）')
$summary.Add('# 用例：' + $filter)
$summary.Add('# 说明：默认套件只记录 uiThreadSchedulingGapMs；本门禁才断言 gap budget（负载敏感）。')
$summary.Add('')

foreach ($round in 1..$Rounds) {
    $rawPath = Join-Path $env:TEMP "nm-fea07-perf-gate-round$round.json"
    if (Test-Path -LiteralPath $rawPath) {
        Remove-Item -LiteralPath $rawPath -Force
    }

    $env:NEWMANGA_FEA07_PERF_GATE_PATH = $rawPath
    $output = & dotnet test $testProject -c Release --nologo --filter $filter 2>&1
    $exitCode = $LASTEXITCODE
    $roundLog = Join-Path $logsDir "perf-gate-round$round.log"
    $output | Out-File -FilePath $roundLog -Encoding utf8
    if (-not (Test-Path -LiteralPath $rawPath)) {
        throw "round $round produced no metrics file; see $roundLog"
    }

    $metrics = Get-Content -LiteralPath $rawPath -Raw | ConvertFrom-Json
    Copy-Item -LiteralPath $rawPath -Destination (Join-Path $evidenceDir "perf-gate-round$round.json") -Force
    $runGaps = @($metrics.runs | ForEach-Object { [double]$_.uiThreadSchedulingGapMs })

    $roundsData += [pscustomobject][ordered]@{
        round = $round
        exitCode = $exitCode
        worstGapMs = [double]$metrics.worstUiThreadSchedulingGapMs
        gapP95Ms = [double]$metrics.uiThreadSchedulingGapP95Ms
        runGapsMs = $runGaps
        medianP95Ms = [double]$metrics.medianP95Ms
        worstRunP95Ms = [double]$metrics.worstRunP95Ms
        p95Passed = [bool]$metrics.p95Passed
        gapPassed = [bool]$metrics.gapPassed
        passed = [bool]$metrics.passed
    }
    $summary.Add("round ${round}: exit=$exitCode worstGap=$($metrics.worstUiThreadSchedulingGapMs) ms; gapP95=$($metrics.uiThreadSchedulingGapP95Ms) ms; runGaps=[$($runGaps -join ', ')]; medianP95=$($metrics.medianP95Ms) ms; p95Passed=$($metrics.p95Passed); gapPassed=$($metrics.gapPassed)")
    if ($exitCode -ne 0) {
        throw "perf gate round $round failed (exit $exitCode); see $roundLog"
    }
}

$gapValues = @($roundsData | ForEach-Object { $_.worstGapMs })
$worstGap = ($gapValues | Measure-Object -Maximum).Maximum
$allGaps = @(@($roundsData | ForEach-Object { $_.runGapsMs }) | Sort-Object)
$gapP95 = $allGaps[[Math]::Min($allGaps.Count - 1, [int][Math]::Ceiling(0.95 * $allGaps.Count) - 1)]
$budgetFromMetrics = (Get-Content -LiteralPath (Join-Path $evidenceDir 'perf-gate-round1.json') -Raw | ConvertFrom-Json).uiThreadSchedulingGapBudgetMs
$margin = [Math]::Round(([double]$budgetFromMetrics - $worstGap) / [double]$budgetFromMetrics * 100, 2)

$gate = [ordered]@{
    metric = 'FEA-07-RESIDUAL-2 AC-R4a-3 dedicated serial performance gate'
    gateVariable = 'NEWMANGA_FEA07_PERF=1'
    frozenTest = 'NewManga.App.Tests.PerformanceBaselineTests.Gated_HotSwitch_UiThreadSchedulingGapStaysWithinThePerfGateBudget'
    command = 'pwsh -NoProfile -File verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1'
    serial = $true
    rounds = $roundsData
    worstGapMs = [double]$worstGap
    gapP95Ms = [double]$gapP95
    uiThreadSchedulingGapBudgetMs = [double]$budgetFromMetrics
    marginPercent = $margin
    verdict = if ($margin -ge 0) { 'PASS (serial perf gate)' } else { 'FAIL: gap over budget' }
    appliesTo = 'serial/idle perf-gate runs only; the default suite records uiThreadSchedulingGapMs without asserting it'
    loadedConditionNote = 'The same metric is load-sensitive: the parallel full-suite run recorded 513.55 ms (Review r2) and isolated repeats under load recorded 437.34 / 471.81 ms; see evidence/ui-gap-loaded-condition-r2a.json.'
}
$jsonPath = Join-Path $evidenceDir 'perf-gate-r2a.json'
$json = $gate | ConvertTo-Json -Depth 8
Set-Content -LiteralPath $jsonPath -Value $json -Encoding utf8

$summary.Add('')
$summary.Add("worstGap=$worstGap ms; gapP95=$gapP95 ms; budget=$budgetFromMetrics ms; margin=$margin%; verdict=$($gate.verdict)")
$summary.Add("json: $jsonPath")
$summary.Add('')
$summary.Add($json)
Set-Content -LiteralPath (Join-Path $logsDir 'perf-gate.log') -Value $summary -Encoding utf8

Write-Output "verdict=$($gate.verdict) worstGapMs=$worstGap gapP95Ms=$gapP95 marginPercent=$margin"
