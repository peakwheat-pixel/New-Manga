# P20 AC3 (corrected): count ONLY WebView2 processes that belong to our app.
# The earlier measurement used Get-Process -Name msedgewebview2, which also swept in the Windows
# Shell's own WebView2 processes (MicrosoftWindows.Client.CBS ... EBWebView), inflating the total.
# Here ownership is decided by walking the ParentProcessId chain up to m2rc1-desktop.
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = '',
    [int]$SettleSeconds = 40
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20\ac3b-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'ac3b-trace.log'
$csv = Join-Path $OutDir 'ac3b-memory-timeseries.csv'
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content $trace -Encoding utf8; Write-Host $l }

# snapshot of processes that exist BEFORE we start, so we can exclude them
$before = @{}
foreach ($pr in Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name) { $before[[int]$pr.ProcessId] = $true }

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20ac3b-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$errLog = Join-Path $OutDir 'app-err.log'; $outLog = Join-Path $OutDir 'app-out.log'
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
$rootPid = $p.Id
T "AC3b start pid=$rootPid iso=$iso settle=${SettleSeconds}s"

$dl = (Get-Date).AddSeconds(30); $win = $false
while ((Get-Date) -lt $dl) {
    Start-Sleep -Milliseconds 300
    if ($p.HasExited) { break }
    try {
        $r = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        if ($r.FindFirst($TS::Children, $c)) { $win = $true; break }
    } catch {}
}
T "window_found=$win"

function Get-OwnedProcesses([int]$rootPid) {
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name)
    $byParent = @{}
    foreach ($x in $all) { $pid2 = [int]$x.ParentProcessId; if (-not $byParent.ContainsKey($pid2)) { $byParent[$pid2] = @() }; $byParent[$pid2] += $x }
    $owned = New-Object System.Collections.ArrayList
    $queue = New-Object System.Collections.Queue
    $queue.Enqueue($rootPid)
    $seen = @{}
    while ($queue.Count -gt 0) {
        $cur = [int]$queue.Dequeue()
        if ($seen.ContainsKey($cur)) { continue }
        $seen[$cur] = $true
        if ($byParent.ContainsKey($cur)) {
            foreach ($ch in $byParent[$cur]) {
                [void]$owned.Add($ch)
                $queue.Enqueue([int]$ch.ProcessId)
            }
        }
    }
    return $owned
}

"elapsed_s,total_ws_mb,m2rc1_mb,core_service_mb,webview_owned_mb,owned_proc_count,webview_proc_count" | Set-Content $csv -Encoding utf8
$samples = @()
$start = Get-Date
while (((Get-Date) - $start).TotalSeconds -lt $SettleSeconds) {
    $el = [math]::Round(((Get-Date) - $start).TotalSeconds, 1)
    $owned = Get-OwnedProcesses $rootPid
    $sum = 0; $m2 = 0; $cs = 0; $wv = 0; $wvCount = 0
    foreach ($o in $owned) {
        $pr = Get-Process -Id ([int]$o.ProcessId) -ErrorAction SilentlyContinue
        if (-not $pr) { continue }
        $ws = 0; try { $ws = $pr.WorkingSet64 } catch {}
        $sum += $ws
        switch ($o.Name) {
            'm2rc1-desktop.exe' { $m2 += $ws }
            'core_service.exe' { $cs += $ws }
            'msedgewebview2.exe' { $wv += $ws; $wvCount++ }
        }
    }
    $row = [pscustomobject]@{
        Elapsed = $el; Total = [math]::Round($sum / 1MB, 1); M2 = [math]::Round($m2 / 1MB, 1)
        Core = [math]::Round($cs / 1MB, 1); WebView = [math]::Round($wv / 1MB, 1)
        Owned = $owned.Count; WvCount = $wvCount
    }
    $samples += $row
    "$el,$($row.Total),$($row.M2),$($row.Core),$($row.WebView),$($row.Owned),$($row.WvCount)" | Add-Content $csv -Encoding utf8
    Start-Sleep -Seconds 3
}
$last = $samples | Select-Object -Last 1
$minTotal = [math]::Round(($samples | Measure-Object Total -Minimum).Minimum, 1)
$maxTotal = [math]::Round(($samples | Measure-Object Total -Maximum).Maximum, 1)
T "SAMPLES n=$($samples.Count) min_total_mb=$minTotal max_total_mb=$maxTotal last_total_mb=$($last.Total)"
T "LAST_BREAKDOWN m2rc1=$($last.M2) core=$($last.Core) webview_owned=$($last.WebView) owned_procs=$($last.Owned) webview_procs=$($last.WvCount)"
foreach ($o in (Get-OwnedProcesses $rootPid)) { $pr = Get-Process -Id ([int]$o.ProcessId) -ErrorAction SilentlyContinue; if ($pr) { T ("OWNED " + $pr.ProcessName + " pid=" + $pr.Id + " ws_mb=" + [math]::Round($pr.WorkingSet64 / 1MB, 1)) } }
$pass = ($last.Total -gt 0 -and $last.Total -le 350)
T ("ASSERT " + $(if ($pass) { 'PASS' } else { 'FAIL' }) + " ac3:idle-memory-owned-only (last_total_mb=$($last.Total) threshold=350)")
@(
    "runner=run-ac3-memory-owned.ps1"
    "method=parent-chain ownership filter (excludes Windows Shell WebView2)"
    "settle_seconds=$SettleSeconds"
    "min_total_mb=$minTotal"; "max_total_mb=$maxTotal"; "last_total_mb=$($last.Total)"
    "last_m2rc1_mb=$($last.M2)"; "last_core_service_mb=$($last.Core)"; "last_webview_owned_mb=$($last.WebView)"
    "last_owned_proc_count=$($last.Owned)"; "last_webview_proc_count=$($last.WvCount)"
    "threshold_mb=350"
) | Set-Content (Join-Path $OutDir 'ac3b-metadata.txt') -Encoding utf8
if (-not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }
Get-Process -Id $rootPid -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
exit ([int](-not $pass))
