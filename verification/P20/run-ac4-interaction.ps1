# P20 AC4 (measurable part): end-to-end interaction latency for navigation and in-page actions.
# This measures the time from an accessibility Invoke to the expected post-condition becoming
# observable, which INCLUDES UIA round-trip overhead, so it is an upper bound rather than a pure
# in-page latency. Frame rate is NOT measured here (it needs WPR/GPUView or frontend instrumentation)
# and is reported as not-measured rather than implied.
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = '',
    [int]$Repeat = 5
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20\ac4-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'ac4-trace.log'
$csv = Join-Path $OutDir 'ac4-latency.csv'
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content $trace -Encoding utf8; Write-Host $l }

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20ac4-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$errLog = Join-Path $OutDir 'app-err.log'; $outLog = Join-Path $OutDir 'app-out.log'
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
function Win() {
    try {
        $r = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        return $r.FindFirst($TS::Children, $c)
    } catch { return $null }
}
function F($w, $n, $ct) { if (-not $w) { return $null }; $c1 = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $n); $c2 = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $ct); return $w.FindFirst($TS::Descendants, (New-Object System.Windows.Automation.AndCondition($c1, $c2))) }
function Has($w, $n) { if (-not $w) { return $false }; $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $n); return [bool]$w.FindFirst($TS::Descendants, $c) }

$win = $null; $dl = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $dl) { Start-Sleep -Milliseconds 400; if ($p.HasExited) { break }; $win = Win; if ($win) { break } }
# wait for frontend shell
$dl = (Get-Date).AddSeconds(25)
while ((Get-Date) -lt $dl) { if (Has $win '📚 书架') { break }; Start-Sleep -Milliseconds 300 }
T "window=$([bool]$win) shell_ready=$(Has $win '📚 书架')"
if (-not $win) { T 'NO_WINDOW'; exit 2 }

# navigation post-conditions: marker text that appears on the target page
$nav = @(
    @{ Btn = '📚 书架';   Marker = '+' },                      # shelf shows its create affordance
    @{ Btn = '🛠️ 工作台'; Marker = '选择作品与章节' },
    @{ Btn = '📖 阅读器'; Marker = '← 返回书架' },              # back-to-shelf control exists only in the reader page
    @{ Btn = '⚙️ 设置';   Marker = 'Provider' }
)
"action,round,latency_ms,ok" | Set-Content $csv -Encoding utf8
$all = @()
foreach ($step in $nav) {
    for ($r = 1; $r -le $Repeat; $r++) {
        $btn = F $win $step.Btn $CT::Button
        if (-not $btn) { T "NAV '$($step.Btn)' NOT_FOUND"; "$($step.Btn),$r,-1,0" | Add-Content $csv; continue }
        # ensure we start from a different page when possible
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        try { $btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke() } catch { T "INVOKE_FAILED $($step.Btn)"; continue }
        $seen = $false
        while ($sw.Elapsed.TotalMilliseconds -lt 5000) {
            if (Has $win $step.Marker) { $seen = $true; break }
            Start-Sleep -Milliseconds 10
        }
        $sw.Stop()
        $ms = [math]::Round($sw.Elapsed.TotalMilliseconds, 1)
        T ("NAV '{0}' round={1} latency_ms={2} ok={3}" -f $step.Btn, $r, $ms, $seen)
        "$($step.Btn),$r,$ms,$([int]$seen)" | Add-Content $csv
        $all += [pscustomobject]@{ Action = $step.Btn; Ms = $ms; Ok = $seen }
        Start-Sleep -Milliseconds 250
    }
}
# in-page action: switch settings categories (lighter interaction)
$catOk = $false
$setBtn = F $win '⚙️ 设置' $CT::Button
if ($setBtn) {
    $setBtn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 800
    for ($r = 1; $r -le $Repeat; $r++) {
        $cat = F $win '网络/代理' $CT::Button
        if (-not $cat) { break }
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        try { $cat.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke() } catch { continue }
        $seen = $false
        while ($sw.Elapsed.TotalMilliseconds -lt 5000) { if ((Has $win '网络/代理') -and (Has $win 'Provider')) { $seen = $true; break }; Start-Sleep -Milliseconds 10 }
        $sw.Stop(); $ms = [math]::Round($sw.Elapsed.TotalMilliseconds, 1)
        T ("CAT '网络/代理' round={0} latency_ms={1} ok={2}" -f $r, $ms, $seen)
        "网络/代理,$r,$ms,$([int]$seen)" | Add-Content $csv
        $all += [pscustomobject]@{ Action = '网络/代理'; Ms = $ms; Ok = $seen }
        $catOk = $catOk -or $seen
        Start-Sleep -Milliseconds 250
    }
}
$valid = @($all | Where-Object { $_.Ms -ge 0 -and $_.Ok })
$avg = if ($valid.Count) { [math]::Round(($valid | Measure-Object Ms -Average).Average, 1) } else { -1 }
$p95 = if ($valid.Count) { $s = $valid | Sort-Object Ms; $i = [Math]::Min([Math]::Floor($s.Count * 0.95), $s.Count - 1); [math]::Round($s[$i].Ms, 1) } else { -1 }
$maxMs = if ($valid.Count) { [math]::Round(($valid | Measure-Object Ms -Maximum).Maximum, 1) } else { -1 }
T "SUMMARY samples=$($valid.Count) avg_ms=$avg p95_ms=$p95 max_ms=$maxMs"
T ("ASSERT " + $(if ($avg -gt 0 -and $avg -le 50) { 'PASS' } else { 'FAIL' }) + " ac4:interaction-latency-avg<=50ms (avg=$avg)")
T "FACT ac4:fps NOT_MEASURED (requires WPR/GPUView or frontend instrumentation)"
@(
    "runner=run-ac4-interaction.ps1"
    "method=accessibility Invoke to observable post-condition; INCLUDES UIA overhead so it is an upper bound"
    "samples=$($valid.Count)"; "avg_ms=$avg"; "p95_ms=$p95"; "max_ms=$maxMs"; "threshold_ms=50"
    "fps=NOT_MEASURED"
    "exe_sha256=$((Get-FileHash $exe -Algorithm SHA256).Hash.ToLower())"
) | Set-Content (Join-Path $OutDir 'ac4-metadata.txt') -Encoding utf8
if ($p -and -not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force }
Get-Process core_service,host_bridge -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
T "AC4 END"
