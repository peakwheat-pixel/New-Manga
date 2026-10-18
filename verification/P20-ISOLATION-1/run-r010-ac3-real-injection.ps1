# P20-ISOLATION-1 R-010 Real Fault Injection Verification Script
# AC3: Verifies that uncommitted draft inputs and operation states are preserved
# across a real sidecar crash (SIGKILL/TerminateProcess) and subsequent recovery,
# and that the draft can be successfully submitted once the sidecar recovers.
#
# Execution: Requires interactive Windows desktop session (Coordinator/Reviewer execution).
# This script outputs structured, machine-evaluable ASSERT lines and captures screenshot evidence.

param(
    [string]$RepoRoot = 'G:\CODEX\New Manga',
    [string]$OutDir = ''
)

$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$TS = [System.Windows.Automation.TreeScope]

if (-not $OutDir) {
    $OutDir = Join-Path $RepoRoot ('verification\P20-ISOLATION-1\r010-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
}
if (Test-Path $OutDir) {
    Write-Host "REFUSE_OVERWRITE $OutDir"
    exit 4
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$trace = Join-Path $OutDir 'trace.log'
$script:scriptFails = 0

function T([string]$m) {
    $l = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss.fff'), $m
    $l | Add-Content $trace -Encoding utf8
    Write-Host $l
}

function A([bool]$cond, [string]$name) {
    if (-not $cond) {
        $script:scriptFails++
    }
    T ("ASSERT {0} {1}" -f $(if ($cond) { 'PASS' } else { 'FAIL' }), $name)
}

function Shot([string]$tag) {
    $b = Join-Path $OutDir "$tag.png"
    $sc = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap($sc.Width, $sc.Height)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($sc.Location, [System.Drawing.Point]::Empty, $sc.Size)
    $bmp.Save($b, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    T "SHOT $tag -> $b"
}

function Get-Owned([int]$rootPid) {
    $all = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name)
    $bp = @{}
    foreach ($x in $all) {
        $k = [int]$x.ParentProcessId
        if (-not $bp.ContainsKey($k)) { $bp[$k] = @() }
        $bp[$k] += $x
    }
    $res = New-Object System.Collections.ArrayList
    $q = New-Object System.Collections.Queue
    $q.Enqueue($rootPid)
    $seen = @{}
    while ($q.Count -gt 0) {
        $c = [int]$q.Dequeue()
        if ($seen.ContainsKey($c)) { continue }
        $seen[$c] = $true
        if ($bp.ContainsKey($c)) {
            foreach ($ch in $bp[$c]) {
                [void]$res.Add($ch)
                $q.Enqueue([int]$ch.ProcessId)
            }
        }
    }
    return $res
}

function GetWin() {
    try {
        $r = [System.Windows.Automation.AutomationElement]::RootElement
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, 'M2-RC1 resource channel runtime')
        return $r.FindFirst($TS::Children, $c)
    } catch {
        return $null
    }
}

function AllNames($w) {
    if (-not $w) { return @() }
    return @($w.FindAll($TS::Descendants, [System.Windows.Automation.Condition]::TrueCondition) | ForEach-Object {
        try { $_.Current.Name } catch {}
    } | Where-Object { $_ })
}

function FindElByName($parent, [string]$name) {
    if (-not $parent) { return $null }
    try {
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $name)
        return $parent.FindFirst($TS::Descendants, $c)
    } catch { return $null }
}

function FindFirstEdit($parent) {
    if (-not $parent) { return $null }
    try {
        $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)
        return $parent.FindFirst($TS::Descendants, $c)
    } catch { return $null }
}

# R-010 fix (Codex R3): the original code called FindFirstEdit on the WHOLE window, which returned the
# bookshelf search box (first Edit in DOM order) instead of the create dialog's title field, so the
# "draft preserved" PASS lines proved nothing. This locator scopes the search to the create dialog:
#   1) prefer an Edit inside the ancestor container that also holds the "作品标题" label;
#   2) otherwise take the first Edit whose accessible name/value does NOT look like a search box;
#   3) expose which element was chosen so the trace is auditable.
function FindDialogTitleEdit($win) {
    if (-not $win) { return $null }
    try {
        $editCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Edit)
        $allEdits = @($win.FindAll($TS::Descendants, $editCond))
        # 1) label-anchored: find the "作品标题" text node, then take an Edit from its ancestor chain
        $labelCond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, '作品标题')
        $label = $win.FindFirst($TS::Descendants, $labelCond)
        if ($label) {
            $walker = [System.Windows.Automation.TreeWalker]::ControlViewWalker
            $node = $label
            for ($i = 0; $i -lt 6 -and $node; $i++) {
                $cand = $node.FindFirst($TS::Descendants, $editCond)
                if ($cand) { Write-Host "R010_LOCATOR label-anchored (depth=$i) name='$($cand.Current.Name)'"; return $cand }
                try { $node = $walker.GetParent($node) } catch { $node = $null }
            }
        }
        # 2) fallback: first Edit that does not look like the search box
        foreach ($e in $allEdits) {
            $n = ''; $v = ''
            try { $n = $e.Current.Name } catch {}
            try { $vp = $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern); $v = $vp.Current.Value } catch {}
            $looksSearch = ($n -match '搜索|Search') -or ($v -match '搜索|Search')
            if (-not $looksSearch) { Write-Host "R010_LOCATOR fallback edit name='$n' value='$v'"; return $e }
        }
        # 3) last resort: report the failure instead of silently using the wrong element
        Write-Host "R010_LOCATOR NOT_FOUND (edits=$($allEdits.Count))"
        return $null
    } catch { Write-Host "R010_LOCATOR ERROR $($_.Exception.Message)"; return $null }
}

function ClickEl($el) {
    if (-not $el) { return $false }
    try {
        $pattern = $el.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        if ($pattern) {
            $pattern.Invoke()
            return $true
        }
    } catch {}
    return $false
}

function SetElText($el, [string]$val) {
    if (-not $el) { return $false }
    try {
        $pattern = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
        if ($pattern) {
            $pattern.SetValue($val)
            return $true
        }
    } catch {}
    return $false
}

function GetElText($el) {
    if (-not $el) { return '' }
    try {
        $pattern = $el.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
        if ($pattern) {
            return $pattern.Current.Value
        }
    } catch {}
    return ''
}

$DRAFT_TITLE = "Real Injection Draft Manga " + (Get-Date -Format 'HHmmss')
$FAIL_REGEX = '后端服务异常|正在尝试热重启|自动重启失败'
$RECOVER_REGEX = '后端服务已恢复正常'

$exe = Join-Path $RepoRoot 'apps\desktop\src-tauri\target\debug\m2rc1-desktop.exe'
$iso = Join-Path $env:TEMP ('p20r010-' + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Force -Path $iso | Out-Null
$env:NEWMANGA_DATA_ROOT = $iso

$errLog = Join-Path $OutDir 'app-err.log'
$outLog = Join-Path $OutDir 'app-out.log'
$p = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru -RedirectStandardError $errLog -RedirectStandardOutput $outLog
$rootPid = $p.Id
T "R-010 AC3 start pid=$rootPid iso=$iso draft_title='$DRAFT_TITLE'"

# 1. Wait for window and shell
$win = $null
$dl = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $dl) {
    Start-Sleep -Milliseconds 300
    if ($p.HasExited) { break }
    $win = GetWin
    if ($win) { break }
}
$dl = (Get-Date).AddSeconds(25)
while ((Get-Date) -lt $dl) {
    $n = AllNames $win
    if ($n -contains '📚 书架') { break }
    Start-Sleep -Milliseconds 300
}
A ([bool]$win) 'r010:window-present'
A (($n -contains '📚 书架')) 'r010:shell-ready'

# 2. Check running sidecar
$owned = Get-Owned $rootPid
$core = $owned | Where-Object { $_.Name -eq 'core_service.exe' } | Select-Object -First 1
$corePid = if ($core) { [int]$core.ProcessId } else { -1 }
T "core_service initial pid=$corePid"
A ($corePid -gt 0) 'r010:sidecar-running-initially'

if ($corePid -gt 0 -and $win) {
    # 3. Open Create Title Dialog
    T "Finding '+ 新建作品' button..."
    $btnNew = FindElByName $win '+ 新建作品'
    if (-not $btnNew) {
        # Fallback: scan for any button containing '新建作品'
        $allButtons = $win.FindAll($TS::Descendants, (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::Button)))
        foreach ($b in $allButtons) {
            if ($b.Current.Name -match '新建作品') {
                $btnNew = $b
                break
            }
        }
    }
    A ([bool]$btnNew) 'r010:new-book-button-found'
    ClickEl $btnNew | Out-Null
    Start-Sleep -Milliseconds 600

    # 4. Find the modal dialog and title input
    $names = AllNames $win
    $dialogPresent = ($names -contains '新建作品')
    A $dialogPresent 'r010:create-title-dialog-opened'

    $inputEl = FindDialogTitleEdit $win
    A ([bool]$inputEl) 'r010:title-input-element-found'
    SetElText $inputEl $DRAFT_TITLE | Out-Null
    Start-Sleep -Milliseconds 200

    $readBack = GetElText $inputEl
    T "Draft title entered: '$readBack'"
    A ($readBack -eq $DRAFT_TITLE) 'r010:draft-title-entered-successfully'
    $editName = ''; try { $editName = $inputEl.Current.Name } catch {}
    A ($editName -notmatch '搜索|Search') "r010:input-is-not-search-box (name='$editName')"
    A ((AllNames $win) -contains '新建作品') 'r010:dialog-still-open-with-draft'

    # 5. REAL FAULT INJECTION: Kill sidecar while draft input is active and uncommitted
    $killAt = Get-Date
    T "INJECT FAULT: Terminating core_service pid=$corePid at $($killAt.ToString('HH:mm:ss.fff'))"
    Stop-Process -Id $corePid -Force -ErrorAction SilentlyContinue

    # 6. Verify draft is preserved during crash state and failure banner appears
    $seenFailBanner = $false
    $draftPreservedDuringCrash = $false
    $deadline = (Get-Date).AddSeconds(10)
    while ((Get-Date) -lt $deadline) {
        $names = AllNames $win
        $banner = ($names | Where-Object { $_ -match $FAIL_REGEX }) -join ' | '
        if ($banner) {
            $seenFailBanner = $true
        }
        $currentDraft = GetElText $inputEl
        $hasDialog = ($names -contains '新建作品')
        if ($hasDialog -and $currentDraft -eq $DRAFT_TITLE) {
            $draftPreservedDuringCrash = $true
            Shot '01-draft-preserved-during-crash'
            break
        }
        Start-Sleep -Milliseconds 100
    }
    A $seenFailBanner 'r010:failure-banner-observed-during-crash'
    A $draftPreservedDuringCrash 'r010:draft-preserved-during-crash'

    # 7. Wait for sidecar auto-recovery and verify draft is still intact
    T "Waiting for sidecar auto-recovery..."
    $seenRecoverBanner = $false
    $newCorePid = -1
    $draftPreservedAfterRecovery = $false
    $deadline = (Get-Date).AddSeconds(15)
    while ((Get-Date) -lt $deadline) {
        $c2 = @(Get-Owned $rootPid | Where-Object { $_.Name -eq 'core_service.exe' })
        if ($c2.Count -gt 0) {
            $newCorePid = [int]$c2[0].ProcessId
        }
        $names = AllNames $win
        $recBanner = ($names | Where-Object { $_ -match $RECOVER_REGEX }) -join ' | '
        if ($recBanner) {
            $seenRecoverBanner = $true
        }
        $currentDraft = GetElText $inputEl
        $hasDialog = ($names -contains '新建作品')
        if ($newCorePid -gt 0 -and $hasDialog -and $currentDraft -eq $DRAFT_TITLE) {
            $draftPreservedAfterRecovery = $true
            Shot '02-draft-preserved-after-recovery'
            break
        }
        Start-Sleep -Milliseconds 100
    }
    T "Sidecar recovered: new_pid=$newCorePid seen_recover_banner=$seenRecoverBanner"
    A ($newCorePid -gt 0) 'r010:sidecar-respawned'
    A $draftPreservedAfterRecovery 'r010:draft-preserved-after-recovery'

    # 8. Submit the preserved draft title
    T "Submitting preserved draft title..."
    $btnSubmit = FindElByName $win '创建作品'
    A ([bool]$btnSubmit) 'r010:submit-button-found'
    ClickEl $btnSubmit | Out-Null
    Start-Sleep -Seconds 2

    # 9. Verify the book was created in the bookshelf
    $finalNames = AllNames $win
    $bookCreated = ($finalNames -contains $DRAFT_TITLE)
    Shot '03-draft-submitted-successfully'
    A $bookCreated 'r010:draft-successfully-submitted-and-persisted'
}

# Cleanup
if ($p -and -not $p.HasExited) {
    $p.CloseMainWindow() | Out-Null
    Start-Sleep -Seconds 2
}
if ($p -and -not $p.HasExited) {
    Stop-Process -Id $p.Id -Force
}
Get-Owned $rootPid | ForEach-Object {
    Get-Process -Id ([int]$_.ProcessId) -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

T ("R-010 AC3 END script_fails=" + $script:scriptFails)
exit ([int]($script:scriptFails -gt 0))
