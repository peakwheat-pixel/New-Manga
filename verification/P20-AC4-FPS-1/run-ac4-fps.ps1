# P20-AC4-FPS-1: frame-time (FPS) sampling measurement on the real interactive desktop.
#
# Delivered by the Owner (ZCode); EXECUTION BELONGS TO THE COORDINATOR on the
# interactive desktop (window-level automation is out of the Owner's scope).
#
# Prerequisite chain (see MEASUREMENT-GUIDE.md):
#   1) -BuildFrontend: build frontend/dist with VITE_M2_FPS_SAMPLING=1
#   2) -BuildExe: rebuild the debug exe so the measurement dist is embedded
#      (Tauri embeds frontendDist at compile time; coordinate with
#      P20-CLOSE-BOUND-HARDEN-1 before touching src-tauri/target)
#   3) Sample content (one single page + one long webtoon page) is imported
#      MANUALLY through the bookshelf import dialog into the isolated root —
#      the script pauses and asks the operator between phases.
#
# The sampling hook is default-OFF; without one of the three switches the FPS
# panel never mounts and this script fails fast with SAMPLING_NOT_ENABLED.
#
# Tearing ("no visible tearing while zooming/panning") is NOT verified here:
# per the user ruling of 2026-10-18 it is recorded as a limitation only.
param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = '',
    [ValidateSet('single', 'webtoon', 'both')]
    [string]$Mode = 'both',
    [int]$ScrollSeconds = 20,
    [int]$ScrollStepDelayMs = 60,
    [ValidateSet('wheel', 'keys')]
    [string]$ScrollMode = 'wheel',
    [switch]$BuildFrontend,
    [switch]$BuildExe
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot ('verification\P20-AC4-FPS-1\run-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
if (Test-Path $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'fps-trace.log'
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content $trace -Encoding utf8; Write-Host $l }

# ---------- optional build phases ----------
if ($BuildFrontend) {
    T "BUILD frontend with VITE_M2_FPS_SAMPLING=1"
    Push-Location (Join-Path $RepoRoot 'apps\desktop\frontend')
    $env:VITE_M2_FPS_SAMPLING = '1'
    npm run build
    $code = $LASTEXITCODE
    Remove-Item Env:\VITE_M2_FPS_SAMPLING -ErrorAction SilentlyContinue
    Pop-Location
    T "BUILD frontend exit=$code"
    if ($code -ne 0) { T 'BUILD_FRONTEND_FAILED'; exit 5 }
}
if ($BuildExe) {
    # src-tauri belongs to P20-CLOSE-BOUND-HARDEN-1; run this only when that
    # task is not building in parallel.
    T 'BUILD debug exe (cargo build)'
    Push-Location (Join-Path $RepoRoot 'apps\desktop\src-tauri')
    cargo build
    $code = $LASTEXITCODE
    Pop-Location
    T "BUILD exe exit=$code"
    if ($code -ne 0) { T 'BUILD_EXE_FAILED'; exit 5 }
}

# ---------- launch (isolated root under %TEMP%, never %APPDATA%) ----------
$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
if (-not (Test-Path $exe)) { T "NO_EXE $exe"; exit 2 }
$iso = Join-Path $env:TEMP ('p20fps-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
T "iso_root=$iso"
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
function InvokeBtn($w, $n) {
    $b = F $w $n $CT::Button
    if (-not $b) { T "BUTTON_NOT_FOUND $n"; return $false }
    try { $b.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); return $true } catch { T "INVOKE_FAILED $n"; return $false }
}
function GetUiText($el) {
    if (-not $el) { return $null }
    try { return $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Value } catch { return $null }
}

$win = $null; $dl = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $dl) { Start-Sleep -Milliseconds 400; if ($p.HasExited) { break }; $win = Win; if ($win) { break } }
$dl = (Get-Date).AddSeconds(25)
while ((Get-Date) -lt $dl) { if (Has $win '📚 书架') { break }; Start-Sleep -Milliseconds 300 }
T "window=$([bool]$win) shell_ready=$(Has $win '📚 书架') fps_panel=$(Has $win 'FPS: Stop')"
if (-not $win) { T 'NO_WINDOW'; exit 2 }
if (-not (Has $win 'FPS: Stop')) { T 'SAMPLING_NOT_ENABLED (no FPS panel: none of the three switches was on at build/launch)'; Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; exit 3 }

# ---------- scroll injection ----------
Add-Type -AssemblyName System.Windows.Forms
if ($ScrollMode -eq 'wheel') {
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class M2Wheel {
    [StructLayout(LayoutKind.Sequential)]
    public struct MOUSEINPUT { public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo; }
    [StructLayout(LayoutKind.Sequential)]
    public struct INPUT { public uint type; public MOUSEINPUT mi; }
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern uint SendInput(uint n, INPUT[] inputs, int size);
    public static void Wheel(int x, int y, int delta) {
        SetCursorPos(x, y);
        INPUT[] i = new INPUT[1];
        i[0].type = 0; i[0].mi.dwFlags = 0x0800; i[0].mi.mouseData = unchecked((uint)delta);
        SendInput(1, i, Marshal.SizeOf(typeof(INPUT)));
    }
}
'@
}
$shellCom = New-Object -ComObject WScript.Shell
function ScrollLoop([string]$label) {
    T "SCROLL begin mode=$ScrollMode seconds=$ScrollSeconds"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $tick = 0
    while ($sw.Elapsed.TotalSeconds -lt $ScrollSeconds) {
        if ($ScrollMode -eq 'wheel') {
            # wheel over the reader area (window centre, below the panel)
            $r = $win.Current.BoundingRectangle
            [M2Wheel]::Wheel([int]($r.X + $r.Width / 2), [int]($r.Y + $r.Height / 2), -120) | Out-Null
        } else {
            $shellCom.AppActivate($p.Id) | Out-Null
            [System.Windows.Forms.SendKeys]::SendWait('{PGDN}')
        }
        $tick++
        Start-Sleep -Milliseconds $ScrollStepDelayMs
    }
    $sw.Stop()
    T "SCROLL end label=$label ticks=$tick"
}

function CaptureRound([string]$label) {
    if (-not (InvokeBtn $win 'FPS: Reset & Start')) { T "CAPTURE_ABORT $label"; return $false }
    Start-Sleep -Milliseconds 500
    ScrollLoop $label
    Start-Sleep -Milliseconds 500
    if (-not (InvokeBtn $win 'FPS: Stop')) { T "CAPTURE_ABORT $label"; return $false }
    Start-Sleep -Milliseconds 500
    T "TITLE[$label] $($win.Current.Name)"
    $titleLine = $win.Current.Name
    $titleLine | Add-Content (Join-Path $OutDir "fps-$label-title.txt") -Encoding utf8

    $out = F $win 'FPS sampler data output' $CT::Document
    if (-not $out) { $out = F $win 'FPS sampler data output' $CT::Edit }
    InvokeBtn $win 'FPS: Show CSV' | Out-Null
    Start-Sleep -Milliseconds 800
    $csvText = GetUiText $out
    if ($csvText) {
        $csvPath = Join-Path $OutDir "fps-$label-samples.csv"
        [System.IO.File]::WriteAllText($csvPath, $csvText.Replace("`r`n", "`n"))
        T "CAPTURE csv label=$label chars=$($csvText.Length) path=$csvPath"
    } else {
        T "CAPTURE csv FAILED via UIA for $label — use the in-app 'FPS: Export CSV' save dialog manually and copy into $OutDir"
    }
    InvokeBtn $win 'FPS: Show JSON' | Out-Null
    Start-Sleep -Milliseconds 800
    $jsonText = GetUiText $out
    if ($jsonText) {
        $jsonPath = Join-Path $OutDir "fps-$label-summary.json"
        [System.IO.File]::WriteAllText($jsonPath, $jsonText.Replace("`r`n", "`n"))
        T "CAPTURE json label=$label chars=$($jsonText.Length) path=$jsonPath"
    } else {
        T "CAPTURE json FAILED via UIA for $label — use 'FPS: Export JSON' manually"
    }
    return $true
}

# ---------- independent re-computation from the captured CSV ----------
function Summarize([string]$csvPath, [string]$label) {
    if (-not (Test-Path $csvPath)) { T "SUMMARY missing csv for $label"; return }
    $rows = @(Import-Csv $csvPath)
    $keptMs = @($rows | Where-Object { $_.excluded -eq '0' } | ForEach-Object { [double]$_.frame_time_ms })
    $excl = @($rows | Where-Object { $_.excluded -eq '1' })
    $avg = if ($keptMs.Count) { [math]::Round(($keptMs | Measure-Object -Average).Average, 3) } else { -1 }
    $max = if ($keptMs.Count) { [math]::Round(($keptMs | Measure-Object -Maximum).Maximum, 3) } else { -1 }
    $min = if ($keptMs.Count) { [math]::Round(($keptMs | Measure-Object -Minimum).Minimum, 3) } else { -1 }
    $p95 = -1
    if ($keptMs.Count) {
        $sorted = $keptMs | Sort-Object
        $idx = [Math]::Max(0, [Math]::Ceiling(0.95 * $sorted.Count) - 1)
        $p95 = [math]::Round($sorted[$idx], 3)
    }
    $reasonGroups = ($excl | Group-Object exclude_reason | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ';'
    T ("SUMMARY[{0}] samples={1} kept={2} excluded={3} reasons={4}" -f $label, $rows.Count, $keptMs.Count, $excl.Count, ($(if ($reasonGroups) { $reasonGroups } else { 'none' })))
    T ("SUMMARY[{0}] avg_ms={1} p95_ms={2} max_ms={3} min_ms={4} (nearest-rank p95; p95/max reported as measured, NOT a gate)" -f $label, $avg, $p95, $max, $min)
    T ("ASSERT " + $(if ($avg -gt 0 -and $avg -le 50) { 'PASS' } else { 'FAIL' }) + " ac4:fps-$label avg<=50ms (user ruling 2026-10-18; avg=$avg)")
    return @{ label = $label; samples = $rows.Count; kept = $keptMs.Count; excluded = $excl.Count; avg = $avg; p95 = $p95; max = $max; min = $min }
}

# ---------- operator phases ----------
$results = @()
$phases = @(); if ($Mode -eq 'both') { $phases = @('single', 'webtoon') } else { $phases = @($Mode) }
foreach ($phase in $phases) {
    if ($phase -eq 'single') {
        Read-Host "ACTION: import/prepare a SINGLE-PAGE sample, open the reader on it (paged mode), then press ENTER to start sampling"
    } else {
        Read-Host "ACTION: switch the reader to the WEBTOON long-strip sample (webtoon mode), then press ENTER to start sampling"
    }
    if (CaptureRound $phase) {
        $results += Summarize (Join-Path $OutDir "fps-$phase-samples.csv") $phase
    }
}

# teardown: every process gone before we leave
if ($p -and -not $p.HasExited) { $p.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 }
if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force }
Get-Process core_service, host_bridge -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Remove-Item Env:\NEWMANGA_DATA_ROOT -ErrorAction SilentlyContinue

@(
    "runner=run-ac4-fps.ps1"
    "owner_delivery=ZCode (hook + tests + script); executor=Coordinator (dsh, epoch 8)"
    "mode=$Mode scroll_seconds=$ScrollSeconds scroll_mode=$ScrollMode"
    "avg_threshold_ms=50 (user ruling 2026-10-18)"
    "p95_method=nearest-rank (sorted[ceil(0.95*n)-1]); p95 and max reported as measured"
    "tearing=NOT_VERIFIED_BY_RULING (limitation only, user ruling 2026-10-18)"
    "iso_root=$iso"
    "exe_sha256=$((Get-FileHash $exe -Algorithm SHA256).Hash.ToLower())"
) | Set-Content (Join-Path $OutDir 'fps-metadata.txt') -Encoding utf8
T ("METADATA written; restore default dist afterwards: cd apps\desktop\frontend; npm run build (without VITE_M2_FPS_SAMPLING)")
T 'FPS MEASUREMENT END'
exit 0
