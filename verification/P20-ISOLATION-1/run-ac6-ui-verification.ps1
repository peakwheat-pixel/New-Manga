# P20-ISOLATION-1: 端到端故障注入与自愈验证脚本 (Interactive Desktop UI Verification)
# 针对 AC1 (用户可见异常提示) 与 AC2 (心跳探测与自动回收重启) 在交互式桌面上进行完整验证。
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = ''
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]

if (-not $OutDir) { 
    $OutDir = Join-Path $RepoRoot ('verification\P20-ISOLATION-1\run-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) 
}
if (Test-Path $OutDir) { 
    Write-Host "REFUSE_OVERWRITE $OutDir"
    exit 4 
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'trace.log'

function T([string]$m) { 
    $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m
    $l | Add-Content $trace -Encoding utf8
    Write-Host $l 
}
function A([bool]$c, [string]$name) { 
    T ("ASSERT {0} {1}" -f $(if ($c) { 'PASS' } else { 'FAIL' }), $name) 
}

function Get-Owned([int]$rootPid) {
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name)
    $byParent = @{}
    foreach ($x in $all) { 
        $k = [int]$x.ParentProcessId
        if (-not $byParent.ContainsKey($k)) { $byParent[$k] = @() }
        $byParent[$k] += $x 
    }
    $res = New-Object System.Collections.ArrayList
    $q = New-Object System.Collections.Queue
    $q.Enqueue($rootPid)
    $seen = @{}
    while ($q.Count -gt 0) {
        $cur = [int]$q.Dequeue()
        if ($seen.ContainsKey($cur)) { continue }
        $seen[$cur] = $true
        if ($byParent.ContainsKey($cur)) { 
            foreach ($ch in $byParent[$cur]) { 
                [void]$res.Add($ch)
                $q.Enqueue([int]$ch.ProcessId) 
            } 
        }
    }
    return $res
}

function WindowAlive([int]$rootPid) {
    if (-not (Get-Process -Id $rootPid -ErrorAction SilentlyContinue)) { return $false }
    try {
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        return [bool]($root.FindFirst($TS::Children, $c))
    } catch { 
        return $false 
    }
}

function Dump-UI-Names([string]$targetFile) {
    try {
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        $w = $root.FindFirst($TS::Children, $c)
        if ($w) {
            $names = @($w.FindAll($TS::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | ForEach-Object { try { $_.Current.Name } catch {} } | Where-Object { $_ })
            $joined = $names -join ' | '
            $joined | Set-Content $targetFile -Encoding utf8
            return $names
        }
    } catch { 
        T "Dump-UI-Names failed: $($_.Exception.Message)" 
    }
    return @()
}

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
if (-not (Test-Path $exe)) {
    T "Executable not found: $exe"
    exit 2
}

$iso = Join-Path $env:TEMP ('p20ac6-iso-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$errLog = Join-Path $OutDir 'app-err.log'
$outLog = Join-Path $OutDir 'app-out.log'

T "Starting desktop app with isolated root=$iso"
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
$rootPid = $p.Id
T "App started with rootPid=$rootPid"

# 等待主应用与 sidecar 完全就绪（稳态，至少 6 秒）
Start-Sleep -Seconds 6

$alive0 = WindowAlive $rootPid
A $alive0 'ac6:window-before-kill'

$owned = Get-Owned $rootPid
$core = $owned | Where-Object { $_.Name -eq 'core_service.exe' } | Select-Object -First 1
$corePid = if ($core) { [int]$core.ProcessId } else { -1 }
T "Initial core_service pid=$corePid owned_count=$($owned.Count)"
A ($corePid -gt 0) 'ac6:sidecar-running'

if ($corePid -gt 0 -and $alive0) {
    # 记录杀死前 UI 状态
    $preNames = Dump-UI-Names (Join-Path $OutDir 'ui-before-kill.txt')
    T "UI elements count before kill: $($preNames.Count)"

    T "KILL core_service pid=$corePid (injecting abnormal termination)"
    Stop-Process -Id $corePid -Force -ErrorAction SilentlyContinue

    # 等待 2s 观察 UI 故障横幅反应（要求 <= 5s）
    Start-Sleep -Seconds 2
    $alive1 = WindowAlive $rootPid
    $stillRunning = [bool](Get-Process -Id $rootPid -ErrorAction SilentlyContinue)
    T "After kill: window_alive=$alive1 main_process_alive=$stillRunning"
    A ($stillRunning -and $alive1) 'ac6:main-window-survives-sidecar-death'

    # Dump 杀死后的 UI 状态
    $killNames = Dump-UI-Names (Join-Path $OutDir 'ui-after-kill.txt')
    T "UI elements count after kill: $($killNames.Count)"
    $errish = @($killNames | Where-Object { $_ -match '异常|错误|失败|重启|后端|Core|error|failed|restart' })
    T ("UI error markers detected: " + ($errish -join ' ; '))
    A ($errish.Count -gt 0) 'ac6:user-visible-error-indicated'

    # 轮询等待自动重启（自愈），持续观察 10s
    T "Observing self-heal respawn (up to 10s)..."
    $respawned = $false
    $newCorePid = -1
    for ($i = 1; $i -le 10; $i++) {
        Start-Sleep -Seconds 1
        $ownedNow = Get-Owned $rootPid
        $newCore = @($ownedNow | Where-Object { $_.Name -eq 'core_service.exe' -and $_.ProcessId -ne $corePid })
        if ($newCore.Count -gt 0) {
            $respawned = $true
            $newCorePid = [int]$newCore[0].ProcessId
            T "Respawn detected at +${i}s! New core_service pid=$newCorePid"
            break
        }
    }
    A $respawned 'ac6:sidecar-auto-respawned'

    # 若成功重启，等待 2s 再次 dump UI 检查是否恢复正常提示
    if ($respawned) {
        Start-Sleep -Seconds 2
        $respawnNames = Dump-UI-Names (Join-Path $OutDir 'ui-after-respawn.txt')
        T "UI elements count after respawn: $($respawnNames.Count)"
        $recovMarkers = @($respawnNames | Where-Object { $_ -match '恢复|正常|healthy|recovered' })
        T ("UI recovery markers: " + ($recovMarkers -join ' ; '))
    }

    # 最终窗口存活状态
    $alive2 = WindowAlive $rootPid
    A $alive2 'ac6:window-still-alive-after-test'
    if (Test-Path $errLog) { 
        T ("app_err_tail: " + ((Get-Content $errLog -Tail 5) -join ' / ')) 
    }
} else {
    T "Skipping kill injection: corePid=$corePid alive0=$alive0"
}

# 清理与关闭
T "Cleaning up processes..."
if (-not $p.HasExited) { 
    $p.CloseMainWindow() | Out-Null
    Start-Sleep -Seconds 2 
}
Get-Process -Id $rootPid -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Get-Owned $rootPid | ForEach-Object { 
    Get-Process -Id ([int]$_.ProcessId) -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue 
}

# 确保无残留孤儿 core_service 或 m2rc1-desktop
Get-Process -Name 'core_service' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name 'm2rc1-desktop' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

@(
    "runner=run-ac6-ui-verification.ps1"
    "root_pid=$rootPid"
    "initial_core_pid=$corePid"
    "respawned=$respawned"
    "new_core_pid=$newCorePid"
    "window_alive_before_kill=$alive0"
) | Set-Content (Join-Path $OutDir 'metadata.txt') -Encoding utf8

T "Verification finished. Artifacts saved in $OutDir"
