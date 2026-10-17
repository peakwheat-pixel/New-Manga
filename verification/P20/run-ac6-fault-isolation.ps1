# P20 AC6: fault isolation. Kill the Python core_service sidecar while the app runs and observe
# whether the main window survives (must not blank out / exit) and whether it reports the failure.
# Also records whether the sidecar is respawned (heartbeat/self-heal), as a fact.
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = ''
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20\ac6-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'ac6-trace.log'
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content $trace -Encoding utf8; Write-Host $l }
function A([bool]$c, [string]$name) { T ("ASSERT {0} {1}" -f $(if ($c) { 'PASS' } else { 'FAIL' }), $name) }

function Get-Owned([int]$rootPid) {
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name)
    $byParent = @{}
    foreach ($x in $all) { $k = [int]$x.ParentProcessId; if (-not $byParent.ContainsKey($k)) { $byParent[$k] = @() }; $byParent[$k] += $x }
    $res = New-Object System.Collections.ArrayList
    $q = New-Object System.Collections.Queue; $q.Enqueue($rootPid); $seen = @{}
    while ($q.Count -gt 0) {
        $cur = [int]$q.Dequeue(); if ($seen.ContainsKey($cur)) { continue }; $seen[$cur] = $true
        if ($byParent.ContainsKey($cur)) { foreach ($ch in $byParent[$cur]) { [void]$res.Add($ch); $q.Enqueue([int]$ch.ProcessId) } }
    }
    return $res
}
function WindowAlive([int]$rootPid) {
    if (-not (Get-Process -Id $rootPid -ErrorAction SilentlyContinue)) { return $false }
    try {
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        return [bool]($root.FindFirst($TS::Children, $c))
    } catch { return $false }
}

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20ac6-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$errLog = Join-Path $OutDir 'app-err.log'; $outLog = Join-Path $OutDir 'app-out.log'
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
$rootPid = $p.Id
T "AC6 start pid=$rootPid iso=$iso"
Start-Sleep -Seconds 6
$alive0 = WindowAlive $rootPid
A $alive0 'ac6:window-before-kill'
$owned = Get-Owned $rootPid
$core = $owned | Where-Object { $_.Name -eq 'core_service.exe' } | Select-Object -First 1
$corePid = if ($core) { [int]$core.ProcessId } else { -1 }
T "core_service pid=$corePid owned=$($owned.Count)"
A ($corePid -gt 0) 'ac6:sidecar-running'

if ($corePid -gt 0) {
    T "KILL core_service pid=$corePid (simulated abnormal exit)"
    Stop-Process -Id $corePid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    $alive1 = WindowAlive $rootPid
    $stillRunning = [bool](Get-Process -Id $rootPid -ErrorAction SilentlyContinue)
    T "after_kill window_alive=$alive1 main_process_alive=$stillRunning"
    A ($stillRunning -and $alive1) 'ac6:main-window-survives-sidecar-death'
    # capture whatever the UI now shows (error banner? blank?)
    try {
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        $w = $root.FindFirst($TS::Children, $c)
        if ($w) {
            $names = @($w.FindAll($TS::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | ForEach-Object { try { $_.Current.Name } catch {} } | Where-Object { $_ })
            $joined = $names -join ' | '
            $joined | Set-Content (Join-Path $OutDir 'ui-after-kill.txt') -Encoding utf8
            T "ui_after_kill_elements=$($names.Count)"
            $errish = @($names | Where-Object { $_ -match '异常|错误|失败|重启|后端|Core|error|failed|restart' })
            T ("ui_error_markers=" + ($errish -join ' ; '))
            A ($errish.Count -gt 0) 'ac6:user-visible-error-indicated'
        }
    } catch { T "ui_dump_failed $($_.Exception.Message)" }
    # did the sidecar come back? (heartbeat / respawn)
    Start-Sleep -Seconds 8
    $owned2 = Get-Owned $rootPid
    $core2 = @($owned2 | Where-Object { $_.Name -eq 'core_service.exe' })
    T "after_8s core_service_count=$($core2.Count) pids=$(($core2 | ForEach-Object { $_.ProcessId }) -join ',')"
    T ("FACT respawned=" + ($core2.Count -gt 0))
    # final window state
    $alive2 = WindowAlive $rootPid
    A $alive2 'ac6:window-still-alive-after-8s'
    if (Test-Path $errLog) { T ("app_err_tail=" + ((Get-Content $errLog -Tail 3) -join ' / ')) }
}

if (-not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
Get-Process -Id $rootPid -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Get-Owned $rootPid | ForEach-Object { Get-Process -Id ([int]$_.ProcessId) -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue }
@(
    "runner=run-ac6-fault-isolation.ps1"
    "core_pid=$corePid"
    "window_alive_before_kill=$alive0"
) | Set-Content (Join-Path $OutDir 'ac6-metadata.txt') -Encoding utf8
T "AC6 END"
