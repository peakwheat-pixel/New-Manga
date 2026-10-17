# P20 AC2+AC3: measure cold start and idle memory of the whole process tree.
# AC2: main window first paint <= 2.0 s; Python Core ready <= 3.5 s.
# AC3: idle resident (Tauri + msedgewebview2* + python) Working Set sum <= 350 MB.
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = '',
    [int]$Rounds = 3
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]

if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20\nfr-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'nfr-trace.log'
$csv = Join-Path $OutDir 'coldstart-memory.csv'
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content $trace -Encoding utf8; Write-Host $l }

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
if (-not (Test-Path $exe)) { T "EXE_MISSING $exe"; exit 2 }
T ("EXE_SHA256=" + (Get-FileHash $exe -Algorithm SHA256).Hash.ToLower())
"round,cold_start_s,core_ready_s,idle_ws_mb,total_ws_mb,proc_count" | Set-Content $csv -Encoding utf8

# baseline: OS/hardware facts for the report
$os = (Get-CimInstance Win32_OperatingSystem)
$cpu = (Get-CimInstance Win32_Processor | Select-Object -First 1)
$gpu = @(Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name })
T ("HOST os=" + $os.Caption + " build=" + $os.BuildNumber + " cpu=" + $cpu.Name.Trim() + " ram_mb=" + [int]($os.TotalVisibleMemorySize/1024) + " gpu=" + ($gpu -join ';'))
$ramMb = [int]($os.TotalVisibleMemorySize / 1024)
$gpuNames = $gpu -join ';'
$hasDiscrete = [bool]($gpu | Where-Object { $_ -match 'NVIDIA|Radeon|GeForce|RTX|GTX|Arc' })

$results = @()
for ($r = 1; $r -le $Rounds; $r++) {
    $iso = Join-Path $env:TEMP ('p20nfr-' + [guid]::NewGuid().ToString('N').Substring(0,8))
    New-Item -ItemType Directory -Force -Path $iso | Out-Null
    $env:NEWMANGA_DATA_ROOT = $iso
    $errLog = Join-Path $OutDir "round$r-app-err.log"
    $outLog = Join-Path $OutDir "round$r-app-out.log"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
    $coldStart = -1; $coreReady = -1
    # main window first paint
    $dl = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $dl) {
        if ($p.HasExited) { break }
        try {
            $root = [System.Windows.Automation.AutomationElement]::RootElement
            $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
            if ($root.FindFirst($TS::Children, $c)) { $coldStart = [math]::Round($sw.Elapsed.TotalSeconds, 3); break }
        } catch {}
        Start-Sleep -Milliseconds 50
    }
    # Core ready: the allowlist line is printed by the sidecar once it serves commands
    $dl2 = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $dl2) {
        if (Test-Path $errLog) {
            $txt = Get-Content $errLog -Raw -ErrorAction SilentlyContinue
            if ($txt -and $txt -match 'm2rc2-allowlist') { $coreReady = [math]::Round($sw.Elapsed.TotalSeconds, 3); break }
        }
        if ($p.HasExited) { break }
        Start-Sleep -Milliseconds 50
    }
    # idle memory after settling
    Start-Sleep -Seconds 6
    $procs = @(Get-Process -Name 'm2rc1-desktop','core_service','msedgewebview2' -ErrorAction SilentlyContinue)
    $wsSum = 0; foreach ($pr in $procs) { try { $wsSum += $pr.WorkingSet64 } catch {} }
    $idleMb = [math]::Round($wsSum / 1MB, 1)
    $coreProcs = @($procs | Where-Object { $_.ProcessName -eq 'core_service' })
    $coreWs = 0; foreach ($cp in $coreProcs) { try { $coreWs += $cp.WorkingSet64 } catch {} }
    $coreWsMb = [math]::Round($coreWs / 1MB, 1)
    $pnames = ($procs | ForEach-Object { $_.ProcessName } | Sort-Object -Unique) -join '+'
    T "ROUND $r cold_start_s=$coldStart core_ready_s=$coreReady idle_ws_mb=$idleMb core_ws_mb=$coreWsMb procs=$pnames"
    "$r,$coldStart,$coreReady,$coreWsMb,$idleMb,$($procs.Count)" | Add-Content $csv -Encoding utf8
    $results += [pscustomobject]@{ Round = $r; ColdStart = $coldStart; CoreReady = $coreReady; IdleMb = $idleMb; CoreMb = $coreWsMb }
    if (-not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
    if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }
    foreach ($n in @('core_service')) { Get-Process -Name $n -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 3
}

$ok = @($results | Where-Object { $_.ColdStart -gt 0 })
$avgCold = if ($ok.Count) { [math]::Round(($ok | Measure-Object ColdStart -Average).Average, 3) } else { -1 }
$avgCore = if (@($results | Where-Object { $_.CoreReady -gt 0 }).Count) { [math]::Round((@($results | Where-Object { $_.CoreReady -gt 0 }) | Measure-Object CoreReady -Average).Average, 3) } else { -1 }
$maxIdle = if (@($results | Where-Object { $_.IdleMb -gt 0 }).Count) { [math]::Round((@($results | Where-Object { $_.IdleMb -gt 0 }) | Measure-Object IdleMb -Maximum).Maximum, 1) } else { -1 }
T "SUMMARY cold_avg_s=$avgCold core_avg_s=$avgCore idle_max_mb=$maxIdle rounds=$Rounds"
$ac2 = ($avgCold -gt 0 -and $avgCold -le 2.0) -and ($avgCore -gt 0 -and $avgCore -le 3.5)
$ac3 = ($maxIdle -gt 0 -and $maxIdle -le 350)
T ("ASSERT " + $(if ($ac2) { 'PASS' } else { 'FAIL' }) + " ac2:cold-start")
T ("ASSERT " + $(if ($ac3) { 'PASS' } else { 'FAIL' }) + " ac3:idle-memory")
@(
    "runner=run-nfr-coldstart-memory.ps1"
    "exe=$exe"
    "exe_sha256=$((Get-FileHash $exe -Algorithm SHA256).Hash.ToLower())"
    "rounds=$Rounds"
    "cold_start_avg_s=$avgCold"
    "core_ready_avg_s=$avgCore"
    "idle_ws_max_mb=$maxIdle"
    "ac2_threshold_s=2.0/3.5"
    "ac3_threshold_mb=350"
    "host_os=$($os.Caption) build=$($os.BuildNumber)"
    "host_cpu=$($cpu.Name.Trim())"
    "host_ram_mb=$ramMb"
    "host_gpu=$gpuNames"
    "host_has_discrete_gpu=$hasDiscrete"
) | Set-Content (Join-Path $OutDir 'nfr-metadata.txt') -Encoding utf8
exit ([int](-not ($ac2 -and $ac3)))
