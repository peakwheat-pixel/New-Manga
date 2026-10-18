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
# FPS-R1-01/02/03 hardening round 2 (codex-review-r2):
#   * Window lookup is BOUND TO THIS RUN'S PID: Find-WindowByTitleForPid
#     enumerates all same-title windows and returns only the one whose
#     ProcessId equals the app PID started by this run. There is no fallback
#     to "first same-title window"; foreign same-title windows are logged as
#     NOT_OURS_WINDOW and can never be clicked, scrolled or killed. A missing
#     own window fails the run (exit 2 / SmokeTest failure).
#   * AppData snapshots FAIL CLOSED: any directory-enumeration error or
#     per-file hash error makes the snapshot incomplete, and an incomplete
#     baseline refuses the launch (exit 7) while an incomplete final
#     snapshot fails the run; a path unreadable on both sides also compares
#     as NOT-unchanged (UNREADABLE guard in Compare-Manifests).
#   * JSON artifacts are PARSED and cross-checked against the same round's
#     CSV (sample counts + first/last frame timestamps); a failed Show CSV /
#     Show JSON button never writes the stale textarea content. In -SmokeTest
#     a missing window, an early app exit or an empty isolated root is a
#     FAILURE, not a log line.
#
# Modes:
#   -Mode single|webtoon|both   interactive measurement (Coordinator)
#   -SmokeTest                  launch the exe for ~12s without measuring,
#                               then prove AppData untouched + clean teardown
#   -SafetySelfCheck            no app-exe launch: fail-closed injection tests
#                               (env validation, snapshot controls, AppData
#                               enumeration/hash fault injection, same-title
#                               decoy-window PID binding) on %TEMP% trees
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

# ---------- window lookup bound to THIS run's PID (FPS-R1-02 r2, P1) ----------
$script:winTitle = 'M2-RC1 resource channel runtime'
$script:notOursWindowPids = [System.Collections.Generic.HashSet[int]]::new()

function Find-WindowByTitleForPid([string]$title, [int]$ownerPid) {
    # Enumerate ALL same-title top-level windows and return ONLY the one whose
    # ProcessId equals $ownerPid (this run's app PID). There is NO fallback to
    # "first same-title window": a window owned by any other process is logged
    # once per pid as NOT_OURS_WINDOW and never returned, so no shell check,
    # UIA invoke or scroll can ever land on a foreign instance.
    try {
        $r = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $title)
        $all = $r.FindAll($TS::Children, $c)
        for ($i = 0; $i -lt $all.Count; $i++) {
            $el = $all.Item($i)
            try { $wpid = [int]$el.Current.ProcessId } catch { continue }
            if ($wpid -eq $ownerPid) { return $el }
            if ($script:notOursWindowPids.Add($wpid)) {
                Write-Trace "NOT_OURS_WINDOW same-title window pid=$wpid (not this run's process; never clicked, never scrolled, never killed)"
            }
        }
        return $null
    } catch { return $null }
}

function Assert-OurWindow($w) {
    # Guard for every downstream consumer of $win: the element must exist and
    # must STILL belong to this run's app PID. Refuse anything else.
    if (-not $w -or -not $script:appProcess) { return $false }
    try { $wpid = [int]$w.Current.ProcessId } catch { return $false }
    return ($wpid -eq [int]$script:appProcess.Id)
}

function Win() { return Find-WindowByTitleForPid $script:winTitle ([int]$script:appProcess.Id) }

# Find-UiaByName: first descendant of window $w matching name $n and control
# type $ct (UIA lookup helper used by Has/InvokeBtn/CaptureRound).
function Find-UiaByName($w, $n, $ct) { if (-not $w) { return $null }; $c1 = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $n); $c2 = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $ct); return $w.FindFirst($TS::Descendants, (New-Object System.Windows.Automation.AndCondition($c1, $c2))) }
function Has($w, $n) { if (-not $w) { return $false }; $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $n); return [bool]$w.FindFirst($TS::Descendants, $c) }
function InvokeBtn($w, $n) {
    $b = Find-UiaByName $w $n $CT::Button
    if (-not $b) { Write-Trace "BUTTON_NOT_FOUND $n"; return $false }
    try { $b.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); return $true } catch { Write-Trace "INVOKE_FAILED $n"; return $false }
}
function GetUiText($el) {
    if (-not $el) { return $null }
    try { return $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).Value } catch { return $null }
}

if (-not $OutDir) {
    $prefix = 'run'
    if ($SmokeTest) { $prefix = 'smoke' } elseif ($SafetySelfCheck) { $prefix = 'selfcheck' }
    $OutDir = Join-Path $RepoRoot ("verification\P20-AC4-FPS-1\$prefix-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
}
if (Test-Path -LiteralPath $OutDir) { Write-Host "REFUSE_OVERWRITE $OutDir"; exit 4 }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$trace = Join-Path $OutDir 'fps-trace.log'
# Write-Trace: append one timestamped line to the run trace log + console.
function Write-Trace([string]$m) { $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m; $l | Add-Content -LiteralPath $trace -Encoding utf8; Write-Host $l }
function Fail([string]$code) { $script:failures.Add($code); Write-Trace "FAIL $code" }

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

# $script:lastManifestErrors is (re)filled by each Get-TreeManifest call with
# ENUM_FAIL / HASH_FAIL records; any entry means the snapshot is INCOMPLETE.
# FPS-R1-01 r2: an incomplete snapshot must FAIL CLOSED — two partial
# manifests that read the same paths unsuccessfully would otherwise compare
# as "unchanged" and mask real writes.
$script:lastManifestErrors = [System.Collections.Generic.List[string]]::new()

function Get-TreeManifest([string]$dir) {
    $script:lastManifestErrors = [System.Collections.Generic.List[string]]::new()
    if (-not (Test-Path -LiteralPath $dir)) { return $null }
    $entries = @{}
    $enumErr = $null
    Get-ChildItem -LiteralPath $dir -Recurse -File -Force -ErrorAction SilentlyContinue -ErrorVariable enumErr | ForEach-Object {
        $rel = $_.FullName.Substring($dir.Length).TrimStart('\', '/')
        $hash = 'UNREADABLE'
        # -ErrorAction Stop is REQUIRED: without it a failed hash is a
        # non-terminating error that never reaches catch, $hash silently
        # becomes $null (not even 'UNREADABLE') and nothing is recorded.
        try { $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256 -ErrorAction Stop).Hash }
        catch { $script:lastManifestErrors.Add("HASH_FAIL $rel :: $($_.Exception.Message)") }
        $entries[$rel] = $hash
    }
    foreach ($e in @($enumErr)) { $script:lastManifestErrors.Add("ENUM_FAIL $dir :: $($e.Exception.Message)") }
    return $entries
}

function Test-ManifestComplete([string]$phase) {
    # Caller-side gate for the fail-closed rule above: false = the snapshot is
    # incomplete and "unchanged" can no longer be proven from it.
    if ($script:lastManifestErrors.Count -gt 0) {
        Write-Trace "APPDATA_SNAPSHOT_INCOMPLETE($phase) errors=$($script:lastManifestErrors.Count) first=[$($script:lastManifestErrors[0])]"
        return $false
    }
    return $true
}

function Save-Manifest($manifest, [string]$path) {
    if ($null -eq $manifest) { 'ABSENT' | Set-Content -LiteralPath $path -Encoding utf8; return }
    $lines = @($manifest.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Value)" })
    if (-not $lines) { $lines = @('EMPTY') }
    $lines | Set-Content -LiteralPath $path -Encoding utf8
}

function Compare-Manifests($before, $after, [string]$label) {
    if ($null -eq $before -and $null -eq $after) { Write-Trace "APPDATA[$label] ABSENT before and after - untouched"; return $true }
    if ($null -eq $before) { Write-Trace "APPDATA[$label] MUTATED: root was CREATED during the run"; return $false }
    if ($null -eq $after) { Write-Trace "APPDATA[$label] MUTATED: root was REMOVED during the run"; return $false }
    $changed = @()
    foreach ($k in @($before.Keys)) {
        if (-not $after.ContainsKey($k)) { $changed += "REMOVED $k" }
        elseif ($before[$k] -eq 'UNREADABLE' -or $after[$k] -eq 'UNREADABLE') { $changed += "UNREADABLE $k (hash unavailable on at least one side - cannot prove unchanged)" }
        elseif ($before[$k] -ne $after[$k]) { $changed += "MODIFIED $k" }
    }
    foreach ($k in @($after.Keys)) {
        if (-not $before.ContainsKey($k)) { $changed += "ADDED $k" }
    }
    if ($changed.Count) { Write-Trace "APPDATA[$label] MUTATED: $($changed -join '; ')"; return $false }
    Write-Trace "APPDATA[$label] UNCHANGED (files=$($before.Count), per-path sha256 compared)"; return $true
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
        Write-Trace ("OUR_PIDS now: " + ($script:ourPids -join ','))
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
            Write-Trace "KILL our pid=$procId name=$($gp.ProcessName)"
        } elseif ($gp) {
            Write-Trace "SKIP recorded pid=$procId name=$($gp.ProcessName) (outside family whitelist - possible PID reuse, NOT touched)"
        }
    }
    if ($script:appProcess -and -not $script:appProcess.HasExited) {
        Stop-Process -Id $script:appProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Trace "KILL app pid=$($script:appProcess.Id)"
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
                Write-Trace "KILL orphan pid=$procId name=$($gp.ProcessName)"
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
        Write-Trace 'TEARDOWN all our processes exited'
    }
}

# ---------- -SafetySelfCheck (no launch, no GUI) ----------
if ($SafetySelfCheck) {
    Write-Trace 'SELFCHECK begin (no app-exe launch; decoy-window + fault injection only)'
    $iso = Join-Path $env:TEMP ('p20fps-selfcheck-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
    Write-Trace "iso_root=$iso"
    $refuse = Set-IsolationEnv $iso $DevSrcRoot
    if ($refuse) { Fail $refuse } else {
        # 1) all four env vars set and inside the iso root -> accepted
        $r = Test-IsolationEnv $iso
        if ($null -eq $r) { Write-Trace 'SELFCHECK isolation-accept PASS (all paths set and inside iso root)' }
        else { Fail "SELFCHECK isolation-accept FAILED: $r" }

        # 2) missing one required var -> REFUSE (fail closed)
        $saved = $env:M2RC1_DERIVED_ROOT
        Remove-Item -Path 'Env:\M2RC1_DERIVED_ROOT' -ErrorAction SilentlyContinue
        $r = Test-IsolationEnv $iso
        if ($r -like 'ISOLATION_REFUSE_ENV_EMPTY*') { Write-Trace "SELFCHECK refuse-missing PASS ($r)" }
        else { Fail "SELFCHECK refuse-missing FAILED: expected ISOLATION_REFUSE_ENV_EMPTY, got '$r'" }
        Set-Item -Path 'Env:\M2RC1_DERIVED_ROOT' -Value $saved

        # 3) a path pointing outside the iso root (e.g. real AppData) -> REFUSE
        $saved = $env:M2RC2_CATALOG_DB
        Set-Item -Path 'Env:\M2RC2_CATALOG_DB' -Value (Join-Path $script:appDataRoot 'catalog\catalog.sqlite')
        $r = Test-IsolationEnv $iso
        if ($r -like 'ISOLATION_REFUSE_ENV_OUTSIDE_ISO*') { Write-Trace "SELFCHECK refuse-outside PASS ($r)" }
        else { Fail "SELFCHECK refuse-outside FAILED: expected ISOLATION_REFUSE_ENV_OUTSIDE_ISO, got '$r'" }
        Set-Item -Path 'Env:\M2RC2_CATALOG_DB' -Value $saved

        # 4) snapshot controls on a disposable %TEMP% tree
        $fake = Join-Path $env:TEMP ('p20fps-selfcheck-tree-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
        New-Item -ItemType Directory -Force -Path $fake | Out-Null
        Set-Content -LiteralPath (Join-Path $fake 'a.txt') -Value 'alpha' -Encoding utf8
        $m1 = Get-TreeManifest $fake
        Save-Manifest $m1 (Join-Path $OutDir 'selfcheck-manifest-before.txt')
        if (Compare-Manifests $m1 (Get-TreeManifest $fake) 'selfcheck-neg') {
            Write-Trace 'SELFCHECK snapshot-negative PASS (identical trees compare UNCHANGED)'
        } else { Fail 'SELFCHECK snapshot-negative FAILED (identical trees compared as MUTATED)' }
        Set-Content -LiteralPath (Join-Path $fake 'a.txt') -Value 'beta' -Encoding utf8
        Set-Content -LiteralPath (Join-Path $fake 'b.txt') -Value 'new file' -Encoding utf8
        $m2 = Get-TreeManifest $fake
        Save-Manifest $m2 (Join-Path $OutDir 'selfcheck-manifest-after.txt')
        if (-not (Compare-Manifests $m1 $m2 'selfcheck-pos')) {
            Write-Trace 'SELFCHECK snapshot-positive PASS (modified+added files detected as MUTATED)'
        } else { Fail 'SELFCHECK snapshot-positive FAILED (changes were NOT detected)' }

        # 5) real-AppData read-only baseline + immediate re-compare
        $real1 = Get-TreeManifest $script:appDataRoot
        Save-Manifest $real1 (Join-Path $OutDir 'appdata-baseline.txt')
        if (-not (Test-ManifestComplete 'selfcheck-real')) {
            Fail 'SELFCHECK real-appdata baseline FAILED (snapshot incomplete - enumeration/hash errors)'
        } elseif (Compare-Manifests $real1 (Get-TreeManifest $script:appDataRoot) 'selfcheck-real') {
            Write-Trace 'SELFCHECK real-appdata baseline PASS (recorded; read-only)'
        } else { Fail 'SELFCHECK real-appdata baseline FAILED (AppData changed between two reads)' }

        # 6) snapshot fail-closed injection (FPS-R1-01 r2): enumeration errors
        #    and hash errors must FAIL CLOSED, and a path unreadable on BOTH
        #    sides must NOT compare as UNCHANGED (the r1 leak).
        $fake2 = Join-Path $env:TEMP ('p20fps-selfcheck-fault-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
        $lockedDir = Join-Path $fake2 'denied'
        $fs = $null
        $denyApplied = $false
        try {
            New-Item -ItemType Directory -Force -Path $lockedDir | Out-Null
            Set-Content -LiteralPath (Join-Path $fake2 'ok.txt') -Value 'stable' -Encoding utf8
            Set-Content -LiteralPath (Join-Path $fake2 'locked.txt') -Value 'hash-locked' -Encoding utf8
            Set-Content -LiteralPath (Join-Path $lockedDir 'hidden.txt') -Value 'behind deny ACL' -Encoding utf8

            # 6a) hash failure: an exclusively locked file must surface as a
            #     manifest error instead of silently becoming UNREADABLE
            $fs = [System.IO.FileStream]::new((Join-Path $fake2 'locked.txt'), [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::None)
            $null = Get-TreeManifest $fake2
            $hashErrs = @($script:lastManifestErrors | Where-Object { $_ -like 'HASH_FAIL *' })
            if ($hashErrs.Count -ge 1) { Write-Trace "SELFCHECK snapshot-hashfail PASS (locked file surfaced as a manifest error: $($hashErrs[0]))" }
            else { Fail 'SELFCHECK snapshot-hashfail FAILED (exclusively locked file did NOT surface as a manifest error)' }

            # 6b) the r1 leak itself: the SAME path unreadable in both
            #     snapshots must compare as NOT-unchanged (fail closed)
            $mU1 = Get-TreeManifest $fake2
            $mU2 = Get-TreeManifest $fake2
            if (-not (Compare-Manifests $mU1 $mU2 'selfcheck-unreadable')) {
                Write-Trace 'SELFCHECK snapshot-unreadable-refuse PASS (double-UNREADABLE path compared as NOT unchanged)'
            } else { Fail 'SELFCHECK snapshot-unreadable-refuse FAILED (double-UNREADABLE path compared as UNCHANGED - the r1 leak is still open)' }
            $fs.Close(); $fs = $null

            # 6c) enumeration failure: a deny-ACL directory must surface as a
            #     manifest error. A token holding an ENABLED SeBackupPrivilege
            #     bypasses read-type DACL checks by Windows design, so a deny
            #     cannot bite there; in that case the ENUM_FAIL channel
            #     (Get-ChildItem -ErrorVariable -> error list) is proven live
            #     with a missing-directory probe instead — the very channel
            #     an ACL denial takes on a normal token.
            $privRows = @()
            try { $privRows = @((& 'C:\Windows\System32\whoami.exe' /priv /fo csv) | ConvertFrom-Csv) } catch { }
            $backupPriv = $privRows | Where-Object { $_.'Privilege Name' -eq 'SeBackupPrivilege' }
            $mySid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
            if ($backupPriv -and $backupPriv.State -eq 'Enabled') {
                Write-Trace "SELFCHECK note: token holds ENABLED SeBackupPrivilege (sid=$mySid) - read-type DACL denies are bypassed by design on this token"
                $evProbe = $null
                Get-ChildItem -LiteralPath (Join-Path $fake2 'no-such-subdir') -Recurse -File -Force -ErrorAction SilentlyContinue -ErrorVariable evProbe | Out-Null
                if (@($evProbe).Count -ge 1) {
                    Write-Trace 'SELFCHECK snapshot-enumfail PASS-by-channel (missing-directory probe produced an enumeration error record; the -ErrorVariable channel feeding ENUM_FAIL is live)'
                } else {
                    Fail 'SELFCHECK snapshot-enumfail FAILED (missing-directory probe produced no enumeration error record)'
                }
            } else {
                # Deny by real token SID; NO (OI)(CI) flags — those are
                # inherit-only and leave the directory itself listable.
                $denyOut = (icacls $lockedDir /deny "*${mySid}:R" 2>&1 | Out-String).Trim()
                if ($LASTEXITCODE -eq 0) {
                    $denyApplied = $true
                    $null = Get-TreeManifest $fake2
                    $enumErrs = @($script:lastManifestErrors | Where-Object { $_ -like 'ENUM_FAIL *' })
                    if ($enumErrs.Count -ge 1) { Write-Trace "SELFCHECK snapshot-enumfail PASS (deny-ACL directory surfaced as a manifest error: $($enumErrs[0]))" }
                    else { Fail 'SELFCHECK snapshot-enumfail FAILED (deny-ACL directory did NOT surface as a manifest error)' }
                } else {
                    Fail "SELFCHECK snapshot-enumfail FAILED (could not apply deny ACL for injection: $denyOut)"
                }
            }
        } finally {
            if ($fs) { $fs.Close() }
            if ($denyApplied) { $null = (icacls $lockedDir /remove:d "*$mySid" 2>&1 | Out-String) }
            Remove-Item -LiteralPath $fake2 -Recurse -Force -ErrorAction SilentlyContinue
        }

        # 7) window-PID binding injection (FPS-R1-02 r2, P1): with a
        #    same-title decoy window on screen owned by ANOTHER process, the
        #    finder must return it for its OWN pid (positive control) and
        #    return NOTHING for any other pid — never "first same-title
        #    window". This is the runnable proof that a foreign same-title
        #    instance can never be clicked or scrolled by the measurement.
        $decoyPid = 0
        try {
            $decoyCmd = 'Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.Form; $f.Text = ''M2-RC1 resource channel runtime''; $f.Width = 320; $f.Height = 200; [System.Windows.Forms.Application]::Run($f)'
            $enc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($decoyCmd))
            $decoy = Start-Process -FilePath powershell.exe -ArgumentList @('-NoProfile', '-STA', '-WindowStyle', 'Hidden', '-EncodedCommand', $enc) -PassThru
            $decoyPid = $decoy.Id
            Write-Trace "SELFCHECK decoy same-title window launched pid=$decoyPid (foreign process, this check's own launch)"
            $decoyWin = $null
            $dl = (Get-Date).AddSeconds(20)
            while ((Get-Date) -lt $dl) {
                Start-Sleep -Milliseconds 500
                if ($decoy.HasExited) { break }
                $decoyWin = Find-WindowByTitleForPid $script:winTitle $decoyPid
                if ($decoyWin) { break }
            }
            if ($decoyWin) {
                Write-Trace 'SELFCHECK window-pid find-own PASS (decoy found when its OWN pid is requested - the finder works)'
                $script:notOursWindowPids.Clear()
                $bogusPid = (([int]$decoyPid + 7919) % 4000000) + 1
                if ($bogusPid -eq [int]$decoyPid) { $bogusPid = $bogusPid + 1 }
                $bogusWin = Find-WindowByTitleForPid $script:winTitle $bogusPid
                if ($null -eq $bogusWin) {
                    Write-Trace "SELFCHECK window-pid refuse-foreign PASS (same-title decoy NOT returned for non-owner pid=$bogusPid; no first-match fallback)"
                } else {
                    Fail "SELFCHECK window-pid refuse-foreign FAILED (returned a window for non-owner pid=$bogusPid)"
                }
                if ($script:notOursWindowPids.Contains([int]$decoyPid)) {
                    Write-Trace 'SELFCHECK window-pid not-ours-trail PASS (foreign same-title window logged as NOT_OURS_WINDOW)'
                } else {
                    Fail 'SELFCHECK window-pid not-ours-trail FAILED (foreign same-title window was not logged as NOT_OURS_WINDOW)'
                }
            } else {
                Fail "SELFCHECK window-pid FAILED (decoy window never became visible; decoy exited=$($decoy.HasExited))"
            }
        } finally {
            if ($decoyPid -gt 0) {
                Stop-Process -Id $decoyPid -Force -ErrorAction SilentlyContinue
                Write-Trace "SELFCHECK decoy stopped pid=$decoyPid (this check's own launch)"
            }
        }
    }
    Clear-IsolationEnv
    if ($script:failures.Count -eq 0) {
        Write-Trace 'SELFCHECK PASS'
        @("runner=run-ac4-fps.ps1 -SafetySelfCheck", "result=PASS", "iso_root=$iso", "appdata_root=$script:appDataRoot") |
            Set-Content -LiteralPath (Join-Path $OutDir 'fps-metadata.txt') -Encoding utf8
        exit 0
    }
    Write-Trace "SELFCHECK FAIL ($($script:failures.Count) failures)"
    exit 6
}

# ---------- optional build phases ----------
if ($BuildFrontend) {
    Write-Trace "BUILD frontend with VITE_M2_FPS_SAMPLING=1"
    Push-Location (Join-Path $RepoRoot 'apps\desktop\frontend')
    $env:VITE_M2_FPS_SAMPLING = '1'
    npm run build
    $code = $LASTEXITCODE
    Remove-Item Env:\VITE_M2_FPS_SAMPLING -ErrorAction SilentlyContinue
    Pop-Location
    Write-Trace "BUILD frontend exit=$code"
    if ($code -ne 0) { Write-Trace 'BUILD_FRONTEND_FAILED'; exit 5 }
}
if ($BuildExe) {
    # src-tauri belongs to P20-CLOSE-BOUND-HARDEN-1; run this only when that
    # task is not building in parallel.
    Write-Trace 'BUILD debug exe (cargo build)'
    Push-Location (Join-Path $RepoRoot 'apps\desktop\src-tauri')
    cargo build
    $code = $LASTEXITCODE
    Pop-Location
    Write-Trace "BUILD exe exit=$code"
    if ($code -ne 0) { Write-Trace 'BUILD_EXE_FAILED'; exit 5 }
}

# ---------- launch setup (fail closed BEFORE the exe starts) ----------
$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
if (-not (Test-Path -LiteralPath $exe)) { Write-Trace "NO_EXE $exe"; exit 2 }

# Without -DevSrcRoot the exe must resolve the PACKAGED sidecar next to it
# (mirrors main.rs resolve_packaged_sidecar_dir); otherwise the app would
# panic on its required M2RC1_SRC_ROOT and the run is refused instead.
if (-not $DevSrcRoot) {
    $sidecarProbe = Join-Path (Split-Path $exe) 'resources\core-sidecar\host_bridge.exe'
    if (-not (Test-Path -LiteralPath $sidecarProbe)) {
        Write-Trace "ISOLATION_REFUSE_NO_PACKAGED_SIDECAR $sidecarProbe (dev-mode exe needs -DevSrcRoot, see main.rs M2RC1_SRC_ROOT contract)"
        exit 7
    }
}

$iso = Join-Path $env:TEMP ('p20fps-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
Write-Trace "iso_root=$iso"
$refuse = Set-IsolationEnv $iso $DevSrcRoot
if ($refuse) { Write-Trace $refuse; Clear-IsolationEnv; exit 7 }
$refuse = Test-IsolationEnv $iso
if ($refuse) { Write-Trace $refuse; Clear-IsolationEnv; exit 7 }
Write-Trace ("ISOLATION pinned: NEWMANGA_DATA_ROOT=$env:NEWMANGA_DATA_ROOT M2RC1_DERIVED_ROOT=$env:M2RC1_DERIVED_ROOT M2RC1_MANAGED_ROOT=$env:M2RC1_MANAGED_ROOT M2RC2_CATALOG_DB=$env:M2RC2_CATALOG_DB" + $(if ($DevSrcRoot) { " M2RC1_SRC_ROOT=$env:M2RC1_SRC_ROOT" } else { ' (packaged sidecar mode)' }))

# Baseline snapshot of the REAL user AppData (read-only) + pre-existing
# same-name processes, so the final comparison can prove we never touched
# either (FPS-R1-01/02 evidence).
$appdataBefore = Get-TreeManifest $script:appDataRoot
Save-Manifest $appdataBefore (Join-Path $OutDir 'appdata-baseline.txt')
Write-Trace "APPDATA baseline recorded root=$script:appDataRoot present=$($null -ne $appdataBefore) files=$(if ($null -eq $appdataBefore) { 0 } else { $appdataBefore.Count })"
# FPS-R1-01 r2: an incomplete baseline snapshot cannot prove "unchanged" —
# refuse to launch the app at all rather than run with a partial manifest.
if (-not (Test-ManifestComplete 'before')) {
    Fail 'APPDATA_SNAPSHOT_INCOMPLETE(before) (cannot prove AppData untouched - refusing to launch)'
    Clear-IsolationEnv
    exit 7
}
$preexisting = @(Get-Process -Name m2rc1-desktop, core_service, host_bridge -ErrorAction SilentlyContinue | ForEach-Object { "$($_.Id): $($_.ProcessName)" })
if ($preexisting.Count) { Write-Trace "NOT_OURS pre-existing same-name processes (never touched): $($preexisting -join '; ')" }
else { Write-Trace 'NOT_OURS no pre-existing same-name processes' }

$errLog = Join-Path $OutDir 'app-err.log'; $outLog = Join-Path $OutDir 'app-out.log'
$script:appProcess = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
Write-Trace "LAUNCH app pid=$($script:appProcess.Id)"

$win = $null

try {
    # Everything after the launch lives inside try/finally so that the
    # normal, failure AND abort paths all run the teardown (FPS-R1-02).
    $dl = (Get-Date).AddSeconds(30)
    while ((Get-Date) -lt $dl) { Start-Sleep -Milliseconds 400; if ($script:appProcess.HasExited) { break }; $win = Win; if ($win) { break } }
    if ($SmokeTest) {
        # Isolation smoke: launch, settle, teardown. No UIA interaction, no
        # sampling, no measurement — only the isolation/ownership guarantees.
        # FPS-R1-03 r2: window missing, early app exit or an empty isolated
        # root are FAILURE conditions (they used to be log-only, which let a
        # dead app pass as exit 0). Deliberately NO exit here: control falls
        # through to the finally block (teardown + AppData comparison) and the
        # trailing exit-code computation, so every failure lands on exit 6.
        Write-Trace "SMOKE window_seen=$([bool]$win) window_pid=$(if ($win) { $win.Current.ProcessId } else { 'none' }) app_pid=$($script:appProcess.Id) (must match) app_exited=$($script:appProcess.HasExited)"
        if (-not $win) { Fail "SMOKE_NO_WINDOW (no window titled '$script:winTitle' owned by app pid=$($script:appProcess.Id); same-title foreign windows are refused, never touched)" }
        if ($script:appProcess.HasExited) { Fail "SMOKE_APP_EXITED_EARLY exit_code=$($script:appProcess.ExitCode) (see app-err.log / app-out.log)" }
        Write-Trace 'SMOKE settling 12s (let core_service / catalog writes happen into the iso root)...'
        Start-Sleep -Seconds 12
        if ($script:appProcess.HasExited) { Fail "SMOKE_APP_EXITED_DURING_SETTLE exit_code=$($script:appProcess.ExitCode) (see app-err.log / app-out.log)" }
        Update-OurPids
        Write-Trace "SMOKE settle done our_pids=$($script:ourPids -join ',')"
    } else {
    $dl = (Get-Date).AddSeconds(25)
    while ((Get-Date) -lt $dl) { if (Has $win '📚 书架') { break }; Start-Sleep -Milliseconds 300 }
    # FPS-R1-02 r2 (P1): refuse to operate unless the window belongs to THIS
    # run's app PID. A same-title window from another process is never used.
    if (-not (Assert-OurWindow $win)) { Write-Trace "NO_WINDOW (no window titled '$script:winTitle' is owned by app pid=$($script:appProcess.Id); foreign same-title windows are refused)"; exit 2 }
    Write-Trace ("WINDOW_BOUND pid=$($script:appProcess.Id) title='$script:winTitle' (all shell checks / UIA invocations / scrolling below run ONLY on this window)")
    Write-Trace "window=true shell_ready=$(Has $win '📚 书架') fps_panel=$(Has $win 'FPS: Stop')"
    if (-not (Has $win 'FPS: Stop')) { Write-Trace 'SAMPLING_NOT_ENABLED (no FPS panel: none of the three switches was on at build/launch)'; exit 3 }
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
        Write-Trace "SCROLL begin mode=$ScrollMode seconds=$ScrollSeconds"
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $tick = 0
        while ($sw.Elapsed.TotalSeconds -lt $ScrollSeconds) {
            # FPS-R1-02 r2: never send input when our app has died mid-scroll.
            if ($script:appProcess.HasExited) { Fail "SCROLL_ABORT app pid=$($script:appProcess.Id) exited mid-scroll (exit_code=$($script:appProcess.ExitCode))"; break }
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
        Write-Trace "SCROLL end label=$label ticks=$tick"
    }

    function CaptureRound([string]$label) {
        Update-OurPids
        if (-not (InvokeBtn $win 'FPS: Reset & Start')) { Write-Trace "CAPTURE_ABORT $label"; return $false }
        Start-Sleep -Milliseconds 500
        ScrollLoop $label
        Start-Sleep -Milliseconds 500
        if (-not (InvokeBtn $win 'FPS: Stop')) { Write-Trace "CAPTURE_ABORT $label"; return $false }
        Start-Sleep -Milliseconds 500
        Write-Trace "TITLE[$label] $($win.Current.Name)"
        $win.Current.Name | Add-Content -LiteralPath (Join-Path $OutDir "fps-$label-title.txt") -Encoding utf8

        $out = Find-UiaByName $win 'FPS sampler data output' $CT::Document
        if (-not $out) { $out = Find-UiaByName $win 'FPS sampler data output' $CT::Edit }
        # ---- CSV capture: button result checked + structure validated ----
        # FPS-R1-03 r2: an ignored button failure could leave the PREVIOUS
        # payload sitting in the textarea; on button failure nothing is
        # written at all, and whatever IS picked up is validated as this
        # round's CSV (header + rows) before it becomes an artifact.
        $csvRows = $null
        if (-not (InvokeBtn $win 'FPS: Show CSV')) {
            Fail "CAPTURE_CSV_BUTTON_FAILED $label (Show CSV invoke failed; NOT writing the stale textarea content)"
        } else {
            Start-Sleep -Milliseconds 800
            $csvText = GetUiText $out
            if (-not $csvText) {
                # FPS-R1-03: a missing required artifact FAILS the run (the old
                # behaviour of only logging hid capture failures behind exit 0).
                Fail "CAPTURE_CSV_MISSING $label (UIA pickup failed; rerun or export manually via the in-app Save As)"
            } else {
                $csvRows = @($csvText | ConvertFrom-Csv)
                if ($csvRows.Count -eq 0) {
                    Fail "CAPTURE_CSV_EMPTY $label (header only, zero samples)"
                } else {
                    $names = @($csvRows[0].PSObject.Properties.Name)
                    $hdrMissing = @('seq', 'frame_ts_ms', 'frame_time_ms', 'instant_fps', 'excluded', 'exclude_reason') | Where-Object { $names -notcontains $_ }
                    if (@($hdrMissing).Count) {
                        Fail "CAPTURE_CSV_STRUCTURE $label (textarea is not this round's CSV; missing columns: $(@($hdrMissing) -join ','))"
                    } else {
                        $csvPath = Join-Path $OutDir "fps-$label-samples.csv"
                        [System.IO.File]::WriteAllText($csvPath, $csvText.Replace("`r`n", "`n"))
                        Write-Trace "CAPTURE csv label=$label rows=$($csvRows.Count) chars=$($csvText.Length) path=$csvPath (header+rows verified)"
                    }
                }
            }
        }

        # ---- JSON capture: PARSED and cross-checked against THIS round ----
        # FPS-R1-03 r2: the JSON button result is checked, the payload is
        # parsed as JSON, and its content must match the CSV captured above
        # (sample counts + first/last frame timestamps). A stale textarea
        # payload (previous CSV, previous round's summary) cannot pass.
        if (-not (InvokeBtn $win 'FPS: Show JSON')) {
            Fail "CAPTURE_JSON_BUTTON_FAILED $label (Show JSON invoke failed; NOT writing the stale textarea content)"
        } else {
            Start-Sleep -Milliseconds 800
            $jsonText = GetUiText $out
            if (-not $jsonText) {
                Fail "CAPTURE_JSON_MISSING $label (UIA pickup failed; rerun or export manually via the in-app Save As)"
            } else {
                $jsonObj = $null
                $parsed = $true
                try { $jsonObj = $jsonText | ConvertFrom-Json }
                catch { $parsed = $false; Fail "CAPTURE_JSON_PARSE_FAILED $label ($($_.Exception.Message); textarea was not this round's JSON)" }
                if ($parsed -and $jsonObj) {
                    $mism = @()
                    if ("$($jsonObj.meta.task)" -ne 'P20-AC4-FPS-1') { $mism += "meta.task=$($jsonObj.meta.task)" }
                    $jTotal = $jsonObj.summary.totalSamples
                    $jExcl = $jsonObj.summary.excludedCount
                    $jSamples = @($jsonObj.samples)
                    if ($csvRows) {
                        $csvExcl = @($csvRows | Where-Object { "$($_.excluded)" -eq '1' }).Count
                        if ("$jTotal" -ne "$($csvRows.Count)") { $mism += "totalSamples=$jTotal vs csv_rows=$($csvRows.Count)" }
                        if ($jSamples.Count -ne $csvRows.Count) { $mism += "samples[]=$($jSamples.Count) vs csv_rows=$($csvRows.Count)" }
                        if ("$jExcl" -ne "$csvExcl") { $mism += "excludedCount=$jExcl vs csv_excluded=$csvExcl" }
                        if ($jSamples.Count -gt 0 -and $csvRows.Count -gt 0) {
                            if ("$($jSamples[0].frameTsMs)" -ne "$($csvRows[0].frame_ts_ms)") { $mism += "first_frame_ts json=$($jSamples[0].frameTsMs) csv=$($csvRows[0].frame_ts_ms)" }
                            if ("$($jSamples[-1].frameTsMs)" -ne "$($csvRows[-1].frame_ts_ms)") { $mism += "last_frame_ts json=$($jSamples[-1].frameTsMs) csv=$($csvRows[-1].frame_ts_ms)" }
                        }
                    } else {
                        # The CSV side already failed above; still require a
                        # sane JSON shape so the file is never garbage.
                        if ("$jTotal" -notmatch '^\d+$' -or [long]"$jTotal" -lt 1) { $mism += "totalSamples=$jTotal (no CSV to cross-check; shape check only)" }
                    }
                    if ($mism.Count) {
                        Fail "CAPTURE_JSON_CONTENT_MISMATCH $label ($($mism -join '; ')) - the JSON is not this round's data"
                    } else {
                        $jsonPath = Join-Path $OutDir "fps-$label-summary.json"
                        [System.IO.File]::WriteAllText($jsonPath, $jsonText.Replace("`r`n", "`n"))
                        Write-Trace "CAPTURE json label=$label totalSamples=$jTotal excludedCount=$jExcl verified=parsed+cross-checked-vs-this-round's-csv path=$jsonPath"
                    }
                }
            }
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
        Write-Trace ("SUMMARY[{0}] samples={1} kept={2} excluded={3} reasons={4}" -f $label, $rows.Count, $keptMs.Count, $excl.Count, ($(if ($reasonGroups) { $reasonGroups } else { 'none' })))
        Write-Trace ("SUMMARY[{0}] avg_ms={1} p95_ms={2} max_ms={3} min_ms={4} (nearest-rank p95; p95/max reported as measured, NOT a gate)" -f $label, $avg, $p95, $max, $min)
        # FPS-R1-05 dual reporting: the all-sample max and the excluded-sample
        # max are ALWAYS reported so a stall cannot hide behind an exclusion.
        Write-Trace ("SUMMARY[{0}] all_max_ms={1} excluded_max_ms={2} (all-sample max includes excluded rows)" -f $label, $allMax, $exclMax)
        if ($keptMs.Count -eq 0) {
            Fail "SUMMARY no kept samples for $label"
        } else {
            Write-Trace ("ASSERT " + $(if ($avg -gt 0 -and $avg -le 50) { 'PASS' } else { 'FAIL' }) + " ac4:fps-$label avg<=50ms (user ruling 2026-10-18; avg=$avg)")
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
    Write-Trace ("PHASES requested=$($phases -join ',') completed=$(@($results | ForEach-Object { $_.label }) -join ',')")
    }
} finally {
    # Unified cleanup covering the normal, failure and abort paths; runs on
    # every exit taken inside the try block as well (FPS-R1-02).
    Stop-OurProcesses
    Clear-IsolationEnv

    # FPS-R1-01 proof: compare the real AppData against the pre-launch
    # snapshot; any mutation fails the run. An incomplete after-snapshot also
    # fails the run (r2): "unchanged" cannot be proven from a partial read.
    $appdataAfter = Get-TreeManifest $script:appDataRoot
    Save-Manifest $appdataAfter (Join-Path $OutDir 'appdata-after.txt')
    if (-not (Test-ManifestComplete 'after')) {
        Fail 'APPDATA_SNAPSHOT_INCOMPLETE(after) (cannot prove AppData untouched - fail closed)'
    }
    if (-not (Compare-Manifests $appdataBefore $appdataAfter 'final')) {
        Fail 'APPDATA_MUTATED (user data root was written during the run)'
    }

    # Inventory of the isolated root (evidence the writes landed there).
    # FPS-R1-03 r2: an empty isolated root is a FAILURE, not a warning — the
    # app ran but produced no expected writes anywhere we can prove.
    $isoFiles = @(Get-ChildItem -LiteralPath $iso -Recurse -File -Force -ErrorAction SilentlyContinue)
    $isoDirs = @(Get-ChildItem -LiteralPath $iso -Recurse -Directory -Force -ErrorAction SilentlyContinue)
    Write-Trace "ISO inventory: files=$($isoFiles.Count) dirs=$($isoDirs.Count) root=$iso"
    if ($isoFiles.Count -eq 0 -and $isoDirs.Count -le 3) {
        Fail 'ISO_EMPTY (nothing was written into the isolated root; investigate app-err.log / app-out.log)'
    }

    @(
        "runner=run-ac4-fps.ps1"
        "owner_delivery=ZCode (hook + tests + script); executor=Coordinator (dsh, epoch 8)"
        "r2_hardening=window lookup bound to this run's PID; AppData snapshots fail closed; JSON parsed+cross-checked vs CSV; SmokeTest window/early-exit/iso-empty are failures"
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
    Write-Trace ("METADATA written; failures=$($script:failures.Count); restore default dist afterwards: cd apps\desktop\frontend; npm run build (without VITE_M2_FPS_SAMPLING)")
    Write-Trace 'FPS MEASUREMENT END'
}

# FPS-R1-03: exit 0 ONLY when nothing failed. This covers the measurement
# modes AND -SmokeTest (neither exits early on success; every failure path —
# missing artifacts, failed captures/asserts, AppData mutation, lingering own
# processes — lands here with a non-zero exit).
if ($script:failures.Count -gt 0) {
    Write-Trace "RESULT FAIL ($($script:failures.Count) failures): $($script:failures -join ' | ')"
    exit 6
}
if ($SmokeTest) {
    Write-Trace 'RESULT PASS (smoke: AppData untouched, own processes gone, writes landed in the iso root)'
} else {
    Write-Trace 'RESULT PASS (all requested phases complete, every avg<=50ms, AppData untouched, own processes gone)'
}
exit 0
