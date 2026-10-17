# P20 AC3 deep-dive: sample the process tree Working Set over time to separate WebView2 warm-up
# from steady state, and break the total down per process.
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = '',
    [int]$SettleSeconds = 45
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20\ac3-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'ac3-trace.log'
$csv = Join-Path $OutDir 'ac3-memory-timeseries.csv'
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content $trace -Encoding utf8; Write-Host $l }

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20ac3-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$errLog = Join-Path $OutDir 'app-err.log'; $outLog = Join-Path $OutDir 'app-out.log'
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
T "AC3 start pid=$($p.Id) iso=$iso settle=${SettleSeconds}s"

$dl = (Get-Date).AddSeconds(30); $win = $false
while ((Get-Date) -lt $dl) {
    Start-Sleep -Milliseconds 300
    if ($p.HasExited) { break }
    try {
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        if ($root.FindFirst($TS::Children, $c)) { $win = $true; break }
    } catch {}
}
T "window_found=$win"

"elapsed_s,total_ws_mb,m2rc1_mb,core_service_mb,msedgewebview2_mb,proc_count" | Set-Content $csv -Encoding utf8
$samples = @()
$start = Get-Date
while (((Get-Date) - $start).TotalSeconds -lt $SettleSeconds) {
    $el = [math]::Round(((Get-Date) - $start).TotalSeconds, 1)
    $all = @(Get-Process -Name 'm2rc1-desktop','core_service','msedgewebview2' -ErrorAction SilentlyContinue)
    $sum = 0; $m2 = 0; $cs = 0; $wv = 0
    foreach ($pr in $all) {
        $ws = 0; try { $ws = $pr.WorkingSet64 } catch {}
        $sum += $ws
        switch ($pr.ProcessName) {
            'm2rc1-desktop' { $m2 += $ws }
            'core_service' { $cs += $ws }
            'msedgewebview2' { $wv += $ws }
        }
    }
    $row = [pscustomobject]@{
        Elapsed = $el
        Total = [math]::Round($sum / 1MB, 1)
        M2 = [math]::Round($m2 / 1MB, 1)
        Core = [math]::Round($cs / 1MB, 1)
        WebView = [math]::Round($wv / 1MB, 1)
        Count = $all.Count
    }
    $samples += $row
    "$el,$($row.Total),$($row.M2),$($row.Core),$($row.WebView),$($row.Count)" | Add-Content $csv -Encoding utf8
    Start-Sleep -Seconds 3
}

$last = $samples | Select-Object -Last 1
$minTotal = [math]::Round(($samples | Measure-Object Total -Minimum).Minimum, 1)
$maxTotal = [math]::Round(($samples | Measure-Object Total -Maximum).Maximum, 1)
T "SAMPLES n=$($samples.Count) min_total_mb=$minTotal max_total_mb=$maxTotal last_total_mb=$($last.Total)"
T "LAST_BREAKDOWN m2rc1=$($last.M2) core=$($last.Core) webview2=$($last.WebView) procs=$($last.Count)"
# per-process detail at the end
foreach ($pr in @(Get-Process -Name 'm2rc1-desktop','core_service','msedgewebview2' -ErrorAction SilentlyContinue | Sort-Object -Property WorkingSet64 -Descending | Select-Object -First 12)) {
    T ("PROC " + $pr.ProcessName + " pid=" + $pr.Id + " ws_mb=" + [math]::Round($pr.WorkingSet64 / 1MB, 1))
}
T ("ASSERT " + $(if ($last.Total -le 350) { 'PASS' } else { 'FAIL' }) + " ac3:idle-memory-steady (last_total_mb=$($last.Total) threshold=350)")
@(
    "runner=run-ac3-memory-deep.ps1"
    "settle_seconds=$SettleSeconds"
    "samples=$($samples.Count)"
    "min_total_mb=$minTotal"
    "max_total_mb=$maxTotal"
    "last_total_mb=$($last.Total)"
    "last_m2rc1_mb=$($last.M)"
    "last_core_service_mb=$($last.Core)"
    "last_msedgewebview2_mb=$($last.WebView)"
    "last_proc_count=$($last.Count)"
    "threshold_mb=350"
) | Set-Content (Join-Path $OutDir 'ac3-metadata.txt') -Encoding utf8
if (-not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }
Get-Process -Name 'core_service' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
exit ([int]($last.Total -gt 350))
