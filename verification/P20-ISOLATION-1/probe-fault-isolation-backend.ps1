# P20-ISOLATION-1 backend fault isolation & self-healing probe
# Verifies AC2 (automatic respawn with backoff) & window/host process survival
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = ''
)
$ErrorActionPreference = 'Continue'
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20-ISOLATION-1\backend-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
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

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20iso1-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso
$errLog = Join-Path $OutDir 'app-err.log'
$outLog = Join-Path $OutDir 'app-out.log'

T "START m2rc1-desktop.exe with iso data root: $iso"
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
$rootPid = $p.Id
T "Root PID=$rootPid"

# Wait 6 seconds for app and sidecar to fully initialize (matching AC6 test methodology)
Start-Sleep -Seconds 6

$owned = Get-Owned $rootPid
$core = $owned | Where-Object { $_.Name -eq 'core_service.exe' } | Select-Object -First 1
$corePid = if ($core) { [int]$core.ProcessId } else { -1 }

T "Initial core_service pid=$corePid"
A ($corePid -gt 0) 'sidecar-running-initially'

if ($corePid -gt 0) {
    T "Simulating abnormal exit: KILLING core_service pid=$corePid"
    Stop-Process -Id $corePid -Force -ErrorAction SilentlyContinue

    Start-Sleep -Seconds 2
    $mainAlive = [bool](Get-Process -Id $rootPid -ErrorAction SilentlyContinue)
    T "After kill (2s): main_process_alive=$mainAlive"
    A $mainAlive 'main-process-survives-sidecar-kill'

    # Check respawn within 8 seconds of kill
    $respawnedCorePid = -1
    for ($i = 0; $i -lt 16; $i++) {
        Start-Sleep -Milliseconds 500
        $ownedNow = Get-Owned $rootPid
        $newCore = $ownedNow | Where-Object { $_.Name -eq 'core_service.exe' -and [int]$_.ProcessId -ne $corePid } | Select-Object -First 1
        if ($newCore) {
            $respawnedCorePid = [int]$newCore.ProcessId
            T "Observed respawned core_service pid=$respawnedCorePid at elapsed ~$(2 + $i * 0.5)s"
            break
        }
    }

    A ($respawnedCorePid -gt 0) 'ac2:sidecar-respawned-after-crash'

    # Sleep another 3 seconds to let supervisor reach recovered state
    Start-Sleep -Seconds 3
}

# Clean up processes
T "Shutting down test processes..."
if (-not $p.HasExited) {
    $p.CloseMainWindow() | Out-Null
    Start-Sleep -Milliseconds 500
}
Get-Process -Id $rootPid -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500
Get-Owned $rootPid | ForEach-Object {
    Get-Process -Id ([int]$_.ProcessId) -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Clean any orphaned core_service or host_bridge
Get-Process -Name 'core_service', 'host_bridge' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

T "Finished. Logs stored in $OutDir"
