#!/usr/bin/env pwsh
# FEA-07-RESIDUAL-2 AC-R4a-3 (r1 P2-004): re-run the frozen hot-switch measurement three independent times
# and record the observed uiThreadSchedulingGapMs distribution, so the fixed 400 ms budget has committed raw
# calibration runs instead of only the two ad-hoc observations quoted in the test comment.
#
# Usage (from the repository root):
#   pwsh -NoProfile -File verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1
#
# Outputs:
#   verification/FEA-07-RESIDUAL-2/evidence/ui-gap-calibration-r4a.json
#   verification/FEA-07-RESIDUAL-2/logs/ui-gap-calibration.log
#   verification/FEA-07-RESIDUAL-2/logs/ui-gap-round{1,2,3}.log
$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$evidenceDir = Join-Path $root 'verification/FEA-07-RESIDUAL-2/evidence'
$logsDir = Join-Path $root 'verification/FEA-07-RESIDUAL-2/logs'
$testProject = Join-Path $root 'apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj'
$filter = 'FullyQualifiedName~HotSwitch_P95MedianOfThreeIndependentRuns'
$budgetMs = 400

$rounds = @()
$summary = New-Object System.Collections.Generic.List[string]
$summary.Add('# uiThreadSchedulingGapMs 定标（FEA-07-RESIDUAL-2 AC-R4a-3 / r1 P2-004）')
$summary.Add('# 命令：dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --filter "' + $filter + '"，每轮独立进程。')
$summary.Add('')

foreach ($round in 1..3) {
    $metricsPath = Join-Path $env:TEMP "nm-fea07-uigap-round$round.json"
    if (Test-Path -LiteralPath $metricsPath) {
        Remove-Item -LiteralPath $metricsPath -Force
    }

    $env:NEWMANGA_FEA07_METRICS_PATH = $metricsPath
    $output = & dotnet test $testProject -c Release --nologo --filter $filter 2>&1
    $exitCode = $LASTEXITCODE
    $roundLog = Join-Path $logsDir "ui-gap-round$round.log"
    $output | Out-File -FilePath $roundLog -Encoding utf8
    if ($exitCode -ne 0) {
        throw "round $round failed (exit $exitCode); see $roundLog"
    }

    $metrics = Get-Content -LiteralPath $metricsPath -Raw | ConvertFrom-Json
    $rounds += [pscustomobject][ordered]@{
        round = $round
        worstGapMs = [double]$metrics.worstUiThreadSchedulingGapMs
        runGapsMs = @($metrics.runs | ForEach-Object { [double]$_.uiThreadSchedulingGapMs })
        uiThreadHeartbeatTicks = @($metrics.runs | ForEach-Object { [int]$_.uiThreadHeartbeatTicks })
        medianP95Ms = [double]$metrics.medianP95Ms
        worstRunP95Ms = [double]$metrics.worstRunP95Ms
        passed = [bool]$metrics.passed
    }
    $summary.Add("round ${round}: worstGap=$($metrics.worstUiThreadSchedulingGapMs) ms; runGaps=[$($rounds[-1].runGapsMs -join ', ')]; heartbeatTicks=[$($rounds[-1].uiThreadHeartbeatTicks -join ', ')]; medianP95=$($metrics.medianP95Ms) ms; passed=$($metrics.passed)")
}

$worst = ($rounds | Measure-Object -Property worstGapMs -Maximum).Maximum
$margin = [Math]::Round(($budgetMs - $worst) / $budgetMs * 100, 2)
$verdict = if ($margin -ge 10) {
    "KEEP 400 ms（余量 $margin% ≥ 10%）"
} else {
    "REVIEW：余量 $margin% < 10%，先报 DSH 再改门槛"
}

$calibration = [ordered]@{
    metric = 'FEA-07-RESIDUAL-2 AC-R4a-3 uiThreadSchedulingGapMs calibration'
    budgetUiThreadSchedulingGapMs = $budgetMs
    independentRounds = 3
    frozenTest = 'NewManga.App.Tests.PerformanceBaselineTests.HotSwitch_P95MedianOfThreeIndependentRuns_StaysWithinTheFrozenW5Budget'
    command = 'dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --filter FullyQualifiedName~HotSwitch_P95MedianOfThreeIndependentRuns'
    heartbeatIntervalMs = 5
    perRoundShape = '4 warmup + 20 measured one-way switches; 3 sub-runs per round (the frozen median gate)'
    rounds = $rounds
    worstGapMs = [double]$worst
    marginPercent = $margin
    verdict = $verdict
    history = 'Pre-rework ad-hoc observations: 215.28 ms (Background-priority heartbeat) and 232.90 ms (Normal-priority heartbeat). They are quoted here as history only; this file is the committed calibration evidence.'
    notes = 'Any future budget change must keep the frozen 1000 ms p95 gate and the 3-run median shape untouched; only this calibrated gap budget may move, with DSH sign-off.'
}

$jsonPath = Join-Path $evidenceDir 'ui-gap-calibration-r4a.json'
$calibrationJson = $calibration | ConvertTo-Json -Depth 8
Set-Content -LiteralPath $jsonPath -Value $calibrationJson -Encoding utf8

$summary.Add('')
$summary.Add("worstGap=$worst ms; budget=$budgetMs ms; margin=$margin%; verdict=$verdict")
$summary.Add("json: $jsonPath")
$summary.Add('')
$summary.Add($calibrationJson)
Set-Content -LiteralPath (Join-Path $logsDir 'ui-gap-calibration.log') -Value $summary -Encoding utf8

Write-Output "verdict=$verdict worstGapMs=$worst marginPercent=$margin"
