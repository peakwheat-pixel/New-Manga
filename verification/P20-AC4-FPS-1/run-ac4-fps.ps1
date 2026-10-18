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
#
# FPS-R1-01/02/03 hardening (codex-review-r1):
#   * The isolated root pins ALL data paths (NEWMANGA_DATA_ROOT,
#     M2RC1_DERIVED_ROOT, M2RC1_MANAGED_ROOT, M2RC2_CATALOG_DB) under a fresh
#     %TEMP% directory, re-reads them back and REFUSES to launch the exe when
#     any is missing or points outside the isolated root (fail closed — the
#     app would otherwise fall back to %APPDATA%\com.newmanga.m2rc1.desktop).
#   * The real %APPDATA%\com.newmanga.m2rc1.desktop tree is snapshotted
#     (per-path sha256) before launch and compared after teardown; any
#     difference fails the run.
#   * Only processes STARTED BY THIS RUN are cleaned up: the app PID plus its
#     recorded descendants (Win32_Process PPID chain), name-checked against
#     the app family whitelist. Pre-existing same-name processes are logged
#     as NOT_OURS and never touched.
#   * Any missing required artifact, failed capture, failed threshold
#     assertion, AppData mutation or lingering own process makes the script
#     exit NON-ZERO. Exit 0 means: every requested phase produced CSV+JSON,
#     every avg <= 50ms, AppData untouched, all own processes gone.
#
# Modes:
#   -Mode single|webtoon|both   interactive measurement (Coordinator)
#   -SmokeTest                  launch the exe for ~12s without measuring,
#                               then prove AppData untouched + clean teardown
#   -SafetySelfCheck            no launch at all: fail-closed injection tests
#                               against the env validation + snapshot
#                               negative/positive controls on a %TEMP% tree
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
    [switch]$BuildExe,
    [switch]$SmokeTest,
    [switch]$SafetySelfCheck,
    # Dev-mode source root (M2RC1_SRC_ROOT). When set, the app spawns from
    # source instead of the packaged sidecar; the path is verified to exist.
    # When empty, the packaged sidecar must exist next to the exe or the run
    # is refused (the app itself would panic on a missing M2RC1_SRC_ROOT).
    [string]$DevSrcRoot = ''
)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]

$script:failures = [System.Collections.Generic.List[string]]::new()
$script:appProcess = $null
$script:ourPids = [System.Collections.Generic.HashSet[int]]::new()
# Only processes whose names are in this family whitelist may be stopped via
# a recorded PID (double check against PID reuse).
$script:familyNames = @('m2rc1-desktop', 'core_service', 'host_bridge', 'acceptance_bridge', 'catalog_loader')

if (-not $OutDir) {
    $prefix = 'run'
    if ($SmokeTest) { $prefix = 'smoke' } elseif ($SafetySelfCheck) { $prefix = 'selfcheck' }
    $OutDir = Join-Path $RepoRoot ("verification\P20-AC4-FPS-1\$prefix-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
}
if (Test-Path -LiteralPath $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'fps-trace.log'
function T([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content -LiteralPath $trace -Encoding utf8; Write-Host $l }
function Fail([string]$code) { $script:failures.Add($code); T "FAIL $code" }

# ---------- isolated data-root environment (FPS-R1-01) ----------
$script:isoEnvNames = @('NEWMANGA_DATA_ROOT', 'M2RC1_DERIVED_ROOT', 'M2RC1_MANAGED_ROOT', 'M2RC2_CATALOG_DB')

function Set-IsolationEnv([string]$isoRoot, [string]$devSrcRoot) {
    # Pre-create the directories so the app never has to fall back to (or
    # create) anything under the real AppData.
    foreach ($sub in @('', 'derived', 'managed', 'catalog')) {
        $p = if ($sub) { Join-Path $isoRoot $sub } else { $isoRoot }
        New-Item -ItemType Directory -Force -Path $p | Out-Null
    }
    Set-Item -Path 'Env:\NEWMANGA_DATA_ROOT' -Value $isoRoot
    Set-Item -Path 'Env:\M2RC1_DERIVED_ROOT' -Value (Join-Path $isoRoot 'derived')
    Set-Item -Path 'Env:\M2RC1_MANAGED_ROOT' -Value (Join-Path $isoRoot 'managed')
    Set-Item -Path 'Env:\M2RC2_CATALOG_DB' -Value (Join-Path $isoRoot 'catalog\catalog.sqlite')
    if ($devSrcRoot) {
        if (-not (Test-Path -LiteralPath $devSrcRoot)) { return "ISOLATION_REFUSE_DEV_SRC_ROOT_MISSING $devSrcRoot" }
        Set-Item -Path 'Env:\M2RC1_SRC_ROOT' -Value $devSrcRoot
    }
    return $null
}

function Test-IsolationEnv([string]$isoRoot) {
    # Fail closed: every required data path must be set and must live inside
    # the isolated root (the root itself is allowed, e.g. NEWMANGA_DATA_ROOT),
    # otherwise the launch is refused.
    $isoNorm = [System.IO.Path]::GetFullPath($isoRoot).TrimEnd('\')
    foreach ($name in $script:isoEnvNames) {
        $v = [Environment]::GetEnvironmentVariable($name)
        if ([string]::IsNullOrWhiteSpace($v)) { return "ISOLATION_REFUSE_ENV_EMPTY $name" }
        $vf = [System.IO.Path]::GetFullPath($v).TrimEnd('\')
        $inside = $vf.Equals($isoNorm, [System.StringComparison]::OrdinalIgnoreCase) -or
            $vf.StartsWith($isoNorm + '\', [System.StringComparison]::OrdinalIgnoreCase)
        if (-not $inside) {
            return "ISOLATION_REFUSE_ENV_OUTSIDE_ISO $name=$v"
        }
    }
    return $null
}

function Clear-IsolationEnv() {
    foreach ($name in ($script:isoEnvNames + @('M2RC1_SRC_ROOT'))) {
        Remove-Item -Path ("Env:\" + $name) -ErrorAction SilentlyContinue
    }
}

# ---------- real-AppData snapshot (FPS-R1-01 proof) ----------
$script:appDataRoot = Join-Path $env:APPDATA 'com.newmanga.m2rc1.desktop'

function Get-TreeManifest([string]$dir) {
    if (-not (Test-Path -LiteralPath $dir)) { return $null }
    $entries = @{}
    Get-ChildItem -LiteralPath $dir -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
        $rel = $_.FullName.Substring($dir.Length).TrimStart('\', '/')
        $hash = 'UNREADABLE'
        try { $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash } catch { }
        $entries[$rel] = $hash
    }
    return $entries
}

function Save-Manifest($manifest, [string]$path) {
    if ($null -eq $manifest) { 'ABSENT' | Set-Content -LiteralPath $path -Encoding utf8; return }
    $lines = @($manifest.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Value)" })
    if (-not $lines) { $lines = @('EMPTY') }
    $lines | Set-Content -LiteralPath $path -Encoding utf8
}

function Compare-Manifests($before, $after, [string]$label) {
    if ($null -eq $before -and $null -eq $after) { T "APPDATA[$label] ABSENT before and after - untouched"; return $true }
    if ($null -eq $before) { T "APPDATA[$label] MUTATED: root was CREATED during the run"; return $false }
    if ($null -eq $after) { T "APPDATA[$label] MUTATED: root was REMOVED during the run"; return $false }
    $changed = @()
    foreach ($k in @($before.Keys)) {
        if (-not $after.ContainsKey($k)) { $changed += "REMOVED $k" }
        elseif ($before[$k] -ne $after[$k]) { $changed += "MODIFIED $k" }
    }
    foreach ($k in @($after.Keys)) {
        if (-not $before.ContainsKey($k)) { $changed += "ADDED $k" }
    }
    if ($changed.Count) { T "APPDATA[$label] MUTATED: $($changed -join '; ')"; return $false }
    T "APPDATA[$label] UNCHANGED (files=$($before.Count), per-path sha256 compared)"; return $true
}

# ---------- own-process ownership (FPS-R1-02) ----------

function Get-DescendantPids([int]$rootPid) {
    $kids = @{}
    foreach ($wp in Get-CimInstance Win32_Process -Property ProcessId, ParentProcessId -ErrorAction SilentlyContinue) {
        $ppid = [int]$wp.ParentProcessId
        if (-not $kids.ContainsKey($ppid)) { $kids[$ppid] = [System.Collections.Generic.List[int]]::new() }
        $kids[$ppid].Add([int]$wp.ProcessId)
    }
    $seen = [System.Collections.Generic.HashSet[int]]::new()
    $queue = [System.Collections.Generic.Queue[int]]::new()
    $queue.Enqueue($rootPid)
    while ($queue.Count -gt 0) {
        $cur = $queue.Dequeue()
        if ($kids.ContainsKey($cur)) {
            foreach ($child in $kids[$cur]) { if ($seen.Add($child)) { $queue.Enqueue($child) } }
        }
    }
    return $seen
}

function Update-OurPids() {
    if ($script:appProcess -and -not $script:appProcess.HasExited) {
        foreach ($procId in (Get-DescendantPids $script:appProcess.Id)) { [void]$script:ourPids.Add($procId) }
        T ("OUR_PIDS now: " + ($script:ourPids -join ','))
    }
}

function Stop-OurProcesses() {
    # Refresh the descendant set while the app is still alive (its PPID chain
    # is intact), then take the workers down before the app itself.
    if ($script:appProcess -and -not $script:appProcess.HasExited) {
        Update-OurPids
        [void]$script:appProcess.CloseMainWindow()
        Start-Sleep -Seconds 3
    }
    foreach ($procId in @($script:ourPids)) {
        $gp = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($gp -and $script:familyNames -contains $gp.ProcessName.ToLowerInvariant()) {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            T "KILL our pid=$procId name=$($gp.ProcessName)"
        } elseif ($gp) {
            T "SKIP recorded pid=$procId name=$($gp.ProcessName) (outside family whitelist - possible PID reuse, NOT touched)"
        }
    }
    if ($script:appProcess -and -not $script:appProcess.HasExited) {
        Stop-Process -Id $script:appProcess.Id -Force -ErrorAction SilentlyContinue
        T "KILL app pid=$($script:appProcess.Id)"
    }
    Start-Sleep -Seconds 2
    # Orphans: the app is gone but PPID values of lingering children still
    # point at it, so one more scan closes that gap (supervisor restarts die
    # with the app, which was the restarter).
    if ($script:appProcess) {
        foreach ($procId in (Get-DescendantPids $script:appProcess.Id)) {
            $gp = Get-Process -Id $procId -ErrorAction SilentlyContinue
            if ($gp -and $script:familyNames -contains $gp.ProcessName.ToLowerInvariant()) {
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                T "KILL orphan pid=$procId name=$($gp.ProcessName)"
            }
        }
    }
    Start-Sleep -Seconds 1
    $remaining = @()
    foreach ($procId in @($script:ourPids)) {
        $gp = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($gp) { $remaining += "$procId`: $($gp.ProcessName)" }
    }
    if ($script:appProcess) {
        try {
            $script:appProcess.Refresh()
            if (-not $script:appProcess.HasExited) { $remaining += "$($script:appProcess.Id): m2rc1-desktop" }
        } catch { }
    }
    if ($remaining.Count) {
        Fail ("OUR_PROCESSES_STILL_RUNNING: " + ($remaining -join '; '))
    } else {
        T 'TEARDOWN all our processes exited'
    }
}

# ---------- -SafetySelfCheck (no launch, no GUI) ----------
if ($SafetySelfCheck) {
    T 'SELFCHECK begin (no exe launch, no GUI)'
    $iso = Join-Path $env:TEMP ('p20fps-selfcheck-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
    T "iso_root=$iso"
    $refuse = Set-IsolationEnv $iso $DevSrcRoot
    if ($refuse) { Fail $refuse } else {
        # 1) all four env vars set and inside the iso root -> accepted
        $r = Test-IsolationEnv $iso
        if ($null -eq $r) { T 'SELFCHECK isolation-accept PASS (all paths set and inside iso root)' }
        else { Fail "SELFCHECK isolation-accept FAILED: $r" }

        # 2) missing one required var -> REFUSE (fail closed)
        $saved = $env:M2RC1_DERIVED_ROOT
        Remove-Item -Path 'Env:\M2RC1_DERIVED_ROOT' -ErrorAction SilentlyContinue
        $r = Test-IsolationEnv $iso
        if ($r -like 'ISOLATION_REFUSE_ENV_EMPTY*') { T "SELFCHECK refuse-missing PASS ($r)" }
        else { Fail "SELFCHECK refuse-missing FAILED: expected ISOLATION_REFUSE_ENV_EMPTY, got '$r'" }
        Set-Item -Path 'Env:\M2RC1_DERIVED_ROOT' -Value $saved

        # 3) a path pointing outside the iso root (e.g. real AppData) -> REFUSE
        $saved = $env:M2RC2_CATALOG_DB
        Set-Item -Path 'Env:\M2RC2_CATALOG_DB' -Value (Join-Path $script:appDataRoot 'catalog\catalog.sqlite')
        $r = Test-IsolationEnv $iso
        if ($r -like 'ISOLATION_REFUSE_ENV_OUTSIDE_ISO*') { T "SELFCHECK refuse-outside PASS ($r)" }
        else { Fail "SELFCHECK refuse-outside FAILED: expected ISOLATION_REFUSE_ENV_OUTSIDE_ISO, got '$r'" }
        Set-Item -Path 'Env:\M2RC2_CATALOG_DB' -Value $saved

        # 4) snapshot controls on a disposable %TEMP% tree
        $fake = Join-Path $env:TEMP ('p20fps-selfcheck-tree-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
        New-Item -ItemType Directory -Force -Path $fake | Out-Null
        Set-Content -LiteralPath (Join-Path $fake 'a.txt') -Value 'alpha' -Encoding utf8
        $m1 = Get-TreeManifest $fake
        Save-Manifest $m1 (Join-Path $OutDir 'selfcheck-manifest-before.txt')
        if (Compare-Manifests $m1 (Get-TreeManifest $fake) 'selfcheck-neg') {
            T 'SELFCHECK snapshot-negative PASS (identical trees compare UNCHANGED)'
        } else { Fail 'SELFCHECK snapshot-negative FAILED (identical trees compared as MUTATED)' }
        Set-Content -LiteralPath (Join-Path $fake 'a.txt') -Value 'beta' -Encoding utf8
        Set-Content -LiteralPath (Join-Path $fake 'b.txt') -Value 'new file' -Encoding utf8
        $m2 = Get-TreeManifest $fake
        Save-Manifest $m2 (Join-Path $OutDir 'selfcheck-manifest-after.txt')
        if (-not (Compare-Manifests $m1 $m2 'selfcheck-pos')) {
            T 'SELFCHECK snapshot-positive PASS (modified+added files detected as MUTATED)'
        } else { Fail 'SELFCHECK snapshot-positive FAILED (changes were NOT detected)' }

        # 5) real-AppData read-only baseline + immediate re-compare
        $real1 = Get-TreeManifest $script:appDataRoot
        Save-Manifest $real1 (Join-Path $OutDir 'appdata-baseline.txt')
        if (Compare-Manifests $real1 (Get-TreeManifest $script:appDataRoot) 'selfcheck-real') {
            T 'SELFCHECK real-appdata baseline PASS (recorded; read-only)'
        } else { Fail 'SELFCHECK real-appdata baseline FAILED (AppData changed between two reads)' }
    }
    Clear-IsolationEnv
    if ($script:failures.Count -eq 0) {
        T 'SELFCHECK PASS'
        @("runner=run-ac4-fps.ps1 -SafetySelfCheck", "result=PASS", "iso_root=$iso", "appdata_root=$script:appDataRoot") |
            Set-Content -LiteralPath (Join-Path $OutDir 'fps-metadata.txt') -Encoding utf8
        exit 0
    }
    T "SELFCHECK FAIL ($($script:failures.Count) failures)"
    exit 6
}

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

# ---------- launch setup (fail closed BEFORE the exe starts) ----------
$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
if (-not (Test-Path -LiteralPath $exe)) { T "NO_EXE $exe"; exit 2 }

# Without -DevSrcRoot the exe must resolve the PACKAGED sidecar next to it
# (mirrors main.rs resolve_packaged_sidecar_dir); otherwise the app would
# panic on its required M2RC1_SRC_ROOT and the run is refused instead.
if (-not $DevSrcRoot) {
    $sidecarProbe = Join-Path (Split-Path $exe) 'resources\core-sidecar\host_bridge.exe'
    if (-not (Test-Path -LiteralPath $sidecarProbe)) {
        T "ISOLATION_REFUSE_NO_PACKAGED_SIDECAR $sidecarProbe (dev-mode exe needs -DevSrcRoot, see main.rs M2RC1_SRC_ROOT contract)"
        exit 7
    }
}

$iso = Join-Path $env:TEMP ('p20fps-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
T "iso_root=$iso"
$refuse = Set-IsolationEnv $iso $DevSrcRoot
if ($refuse) { T $refuse; Clear-IsolationEnv; exit 7 }
$refuse = Test-IsolationEnv $iso
if ($refuse) { T $refuse; Clear-IsolationEnv; exit 7 }
T ("ISOLATION pinned: NEWMANGA_DATA_ROOT=$env:NEWMANGA_DATA_ROOT M2RC1_DERIVED_ROOT=$env:M2RC1_DERIVED_ROOT M2RC1_MANAGED_ROOT=$env:M2RC1_MANAGED_ROOT M2RC2_CATALOG_DB=$env:M2RC2_CATALOG_DB" + $(if ($DevSrcRoot) { " M2RC1_SRC_ROOT=$env:M2RC1_SRC_ROOT" } else { ' (packaged sidecar mode)' }))

# Baseline snapshot of the REAL user AppData (read-only) + pre-existing
# same-name processes, so the final comparison can prove we never touched
# either (FPS-R1-01/02 evidence).
$appdataBefore = Get-TreeManifest $script:appDataRoot
Save-Manifest $appdataBefore (Join-Path $OutDir 'appdata-baseline.txt')
T "APPDATA baseline recorded root=$script:appDataRoot present=$($null -ne $appdataBefore) files=$(if ($null -eq $appdataBefore) { 0 } else { $appdataBefore.Count })"
$preexisting = @(Get-Process -Name m2rc1-desktop, core_service, host_bridge -ErrorAction SilentlyContinue | ForEach-Object { "$($_.Id): $($_.ProcessName)" })
if ($preexisting.Count) { T "NOT_OURS pre-existing same-name processes (never touched): $($preexisting -join '; ')" }
else { T 'NOT_OURS no pre-existing same-name processes' }

$errLog = Join-Path $OutDir 'app-err.log'; $outLog = Join-Path $OutDir 'app-out.log'
$script:appProcess = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
T "LAUNCH app pid=$($script:appProcess.Id)"

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

$win = $null

try {
    # Everything after the launch lives inside try/finally so that the
    # normal, failure AND abort paths all run the teardown (FPS-R1-02).
    $dl = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $dl) { Start-Sleep -Milliseconds 400; if ($script:appProcess.HasExited) { break }; $win = Win; if ($win) { break } }
    if ($SmokeTest) {
        # Isolation smoke: launch, settle, teardown. No UIA interaction, no
        # sampling, no measurement — only the isolation/ownership guarantees.
        # Deliberately NO exit here: control falls through to the finally
        # block (teardown + AppData comparison) and the trailing exit-code
        # computation, so a mutation or lingering process still fails the run.
        T "SMOKE window_seen=$([bool]$win) app_exited=$($script:appProcess.HasExited)"
        T 'SMOKE settling 12s (let core_service / catalog writes happen into the iso root)...'
        Start-Sleep -Seconds 12
        Update-OurPids
        T "SMOKE settle done our_pids=$($script:ourPids -join ',')"
    } else {
    $dl = (Get-Date).AddSeconds(25)
    while ((Get-Date) -lt $dl) { if (Has $win '📚 书架') { break }; Start-Sleep -Milliseconds 300 }
    T "window=$([bool]$win) shell_ready=$(Has $win '📚 书架') fps_panel=$(Has $win 'FPS: Stop')"
    if (-not $win) { T 'NO_WINDOW'; exit 2 }
    if (-not (Has $win 'FPS: Stop')) { T 'SAMPLING_NOT_ENABLED (no FPS panel: none of the three switches was on at build/launch)'; exit 3 }
    Update-OurPids

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
                $shellCom.AppActivate($script:appProcess.Id) | Out-Null
                [System.Windows.Forms.SendKeys]::SendWait('{PGDN}')
            }
            $tick++
            Start-Sleep -Milliseconds $ScrollStepDelayMs
        }
        $sw.Stop()
        T "SCROLL end label=$label ticks=$tick"
    }

    function CaptureRound([string]$label) {
        Update-OurPids
        if (-not (InvokeBtn $win 'FPS: Reset & Start')) { T "CAPTURE_ABORT $label"; return $false }
        Start-Sleep -Milliseconds 500
        ScrollLoop $label
        Start-Sleep -Milliseconds 500
        if (-not (InvokeBtn $win 'FPS: Stop')) { T "CAPTURE_ABORT $label"; return $false }
        Start-Sleep -Milliseconds 500
        T "TITLE[$label] $($win.Current.Name)"
        $win.Current.Name | Add-Content -LiteralPath (Join-Path $OutDir "fps-$label-title.txt") -Encoding utf8

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
            # FPS-R1-03: a missing required artifact FAILS the run (the old
            # behaviour of only logging hid capture failures behind exit 0).
            Fail "CAPTURE_CSV_MISSING $label (UIA pickup failed; rerun or export manually via the in-app Save As)"
        }
        InvokeBtn $win 'FPS: Show JSON' | Out-Null
        Start-Sleep -Milliseconds 800
        $jsonText = GetUiText $out
        if ($jsonText) {
            $jsonPath = Join-Path $OutDir "fps-$label-summary.json"
            [System.IO.File]::WriteAllText($jsonPath, $jsonText.Replace("`r`n", "`n"))
            T "CAPTURE json label=$label chars=$($jsonText.Length) path=$jsonPath"
        } else {
            Fail "CAPTURE_JSON_MISSING $label (UIA pickup failed; rerun or export manually via the in-app Save As)"
        }
        return $true
    }

    # ---------- independent re-computation from the captured CSV ----------
    function Summarize([string]$csvPath, [string]$label) {
        if (-not (Test-Path -LiteralPath $csvPath)) { Fail "SUMMARY missing csv for $label"; return $null }
        $rows = @(Import-Csv $csvPath)
        if ($rows.Count -eq 0) { Fail "SUMMARY empty csv for $label"; return $null }
        $keptMs = @($rows | Where-Object { $_.excluded -eq '0' } | ForEach-Object { [double]$_.frame_time_ms })
        $excl = @($rows | Where-Object { $_.excluded -eq '1' })
        $allMs = @($rows | ForEach-Object { [double]$_.frame_time_ms })
        $avg = if ($keptMs.Count) { [math]::Round(($keptMs | Measure-Object -Average).Average, 3) } else { -1 }
        $max = if ($keptMs.Count) { [math]::Round(($keptMs | Measure-Object -Maximum).Maximum, 3) } else { -1 }
        $min = if ($keptMs.Count) { [math]::Round(($keptMs | Measure-Object -Minimum).Minimum, 3) } else { -1 }
        $allMax = if ($allMs.Count) { [math]::Round(($allMs | Measure-Object -Maximum).Maximum, 3) } else { -1 }
        $exclMax = if ($excl.Count) { [math]::Round((@($excl | ForEach-Object { [double]$_.frame_time_ms }) | Measure-Object -Maximum).Maximum, 3) } else { -1 }
        $p95 = -1
        if ($keptMs.Count) {
            $sorted = $keptMs | Sort-Object
            $idx = [Math]::Max(0, [Math]::Ceiling(0.95 * $sorted.Count) - 1)
            $p95 = [math]::Round($sorted[$idx], 3)
        }
        $reasonGroups = ($excl | Group-Object exclude_reason | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ';'
        T ("SUMMARY[{0}] samples={1} kept={2} excluded={3} reasons={4}" -f $label, $rows.Count, $keptMs.Count, $excl.Count, ($(if ($reasonGroups) { $reasonGroups } else { 'none' })))
        T ("SUMMARY[{0}] avg_ms={1} p95_ms={2} max_ms={3} min_ms={4} (nearest-rank p95; p95/max reported as measured, NOT a gate)" -f $label, $avg, $p95, $max, $min)
        # FPS-R1-05 dual reporting: the all-sample max and the excluded-sample
        # max are ALWAYS reported so a stall cannot hide behind an exclusion.
        T ("SUMMARY[{0}] all_max_ms={1} excluded_max_ms={2} (all-sample max includes excluded rows)" -f $label, $allMax, $exclMax)
        if ($keptMs.Count -eq 0) {
            Fail "SUMMARY no kept samples for $label"
        } else {
            T ("ASSERT " + $(if ($avg -gt 0 -and $avg -le 50) { 'PASS' } else { 'FAIL' }) + " ac4:fps-$label avg<=50ms (user ruling 2026-10-18; avg=$avg)")
            if (-not ($avg -gt 0 -and $avg -le 50)) { Fail "ASSERT ac4:fps-$label avg=${avg}ms exceeds the user-ruled 50ms criterion" }
        }
        return @{ label = $label; samples = $rows.Count; kept = $keptMs.Count; excluded = $excl.Count; avg = $avg; p95 = $p95; max = $max; min = $min; all_max = $allMax; excluded_max = $exclMax }
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
            $r = Summarize (Join-Path $OutDir "fps-$phase-samples.csv") $phase
            if ($r) { $results += $r }
            $jsonPath = Join-Path $OutDir "fps-$phase-summary.json"
            if (-not (Test-Path -LiteralPath $jsonPath)) { Fail "REQUIRED_ARTIFACT_MISSING fps-$phase-summary.json" }
        } else {
            Fail "CAPTURE_FAILED $phase"
        }
    }
    T ("PHASES requested=$($phases -join ',') completed=$(@($results | ForEach-Object { $_.label }) -join ',')")
    }
} finally {
    # Unified cleanup covering the normal, failure and abort paths; runs on
    # every exit taken inside the try block as well (FPS-R1-02).
    Stop-OurProcesses
    Clear-IsolationEnv

    # FPS-R1-01 proof: compare the real AppData against the pre-launch
    # snapshot; any mutation fails the run.
    $appdataAfter = Get-TreeManifest $script:appDataRoot
    Save-Manifest $appdataAfter (Join-Path $OutDir 'appdata-after.txt')
    if (-not (Compare-Manifests $appdataBefore $appdataAfter 'final')) {
        Fail 'APPDATA_MUTATED (user data root was written during the run)'
    }

    # Inventory of the isolated root (evidence the writes landed there).
    $isoFiles = @(Get-ChildItem -LiteralPath $iso -Recurse -File -Force -ErrorAction SilentlyContinue)
    $isoDirs = @(Get-ChildItem -LiteralPath $iso -Recurse -Directory -Force -ErrorAction SilentlyContinue)
    T "ISO inventory: files=$($isoFiles.Count) dirs=$($isoDirs.Count) root=$iso"
    if ($isoFiles.Count -eq 0 -and $isoDirs.Count -le 3) {
        T 'ISO_EMPTY_WARNING (nothing was written into the isolated root; investigate app logs)'
    }

    @(
        "runner=run-ac4-fps.ps1"
        "owner_delivery=ZCode (hook + tests + script); executor=Coordinator (dsh, epoch 8)"
        "mode=$Mode scroll_seconds=$ScrollSeconds scroll_mode=$ScrollMode smoke=$SmokeTest"
        "avg_threshold_ms=50 (user ruling 2026-10-18)"
        "p95_method=nearest-rank (sorted[ceil(0.95*n)-1]); p95 and max reported as measured"
        "all_max_ms/excluded_max_ms reported alongside kept stats (FPS-R1-05, no spike masking)"
        "tearing=NOT_VERIFIED_BY_RULING (limitation only, user ruling 2026-10-18)"
        "iso_root=$iso"
        "appdata_root=$script:appDataRoot (snapshotted before/after, per-path sha256)"
        "our_pids=$($script:ourPids -join ',') app_pid=$(if ($script:appProcess) { $script:appProcess.Id } else { 'none' })"
        "preexisting_same_name=$(if ($preexisting.Count) { $preexisting -join ';' } else { 'none' })"
        "exe_sha256=$((Get-FileHash $exe -Algorithm SHA256).Hash.ToLower())"
    ) | Set-Content -LiteralPath (Join-Path $OutDir 'fps-metadata.txt') -Encoding utf8
    T ("METADATA written; failures=$($script:failures.Count); restore default dist afterwards: cd apps\desktop\frontend; npm run build (without VITE_M2_FPS_SAMPLING)")
    T 'FPS MEASUREMENT END'
}

# FPS-R1-03: exit 0 ONLY when nothing failed. This covers the measurement
# modes AND -SmokeTest (neither exits early on success; every failure path —
# missing artifacts, failed captures/asserts, AppData mutation, lingering own
# processes — lands here with a non-zero exit).
if ($script:failures.Count -gt 0) {
    T "RESULT FAIL ($($script:failures.Count) failures): $($script:failures -join ' | ')"
    exit 6
}
if ($SmokeTest) {
    T 'RESULT PASS (smoke: AppData untouched, own processes gone, writes landed in the iso root)'
} else {
    T 'RESULT PASS (all requested phases complete, every avg<=50ms, AppData untouched, own processes gone)'
}
exit 0
