# UI-DESIGN-1 selfcheck (AC8)
# (a) every contract command/event name referenced in design doc section 6 must be
#     verbatim-findable in the referenced contract file (and the design doc itself);
# (b) every local markdown link in the design doc must resolve to an existing file;
# (c) git diff --name-only + git status --porcelain must stay inside the allowed
#     write scope and must NOT touch the 19 user-dirty paths;
# (d) AC1 structural checklist: four page sections each with the six required
#     elements, plus shell/binding/gap/token/compliance/non-goal sections.
# Output: raw log to selfcheck-output.txt (same directory). Exit 0 = all PASS.

$ErrorActionPreference = 'Continue'

$root = (Resolve-Path (Join-Path $PSCommandPath '..\..\..')).Path
$designDoc = Join-Path $root 'doc\design\AD001_FOUR_PAGE_UI_BASELINE.md'
$outFile = Join-Path $root 'verification\UI-DESIGN-1\selfcheck-output.txt'

$script:log = New-Object System.Collections.Generic.List[string]
$script:failed = 0

function Log([string]$m) {
    $script:log.Add($m)
    Write-Host $m
}
function Section([string]$t) { Log ""; Log "===== $t =====" }
function Check([bool]$ok, [string]$label) {
    if ($ok) { Log ("[PASS] " + $label) }
    else { Log ("[FAIL] " + $label); $script:failed++ }
}

function ReadUtf8([string]$p) {
    if (-not (Test-Path $p)) { return $null }
    return [System.IO.File]::ReadAllLines($p, [System.Text.Encoding]::UTF8)
}

Section ("UI-DESIGN-1 selfcheck @ " + (Get-Date -Format o))
Log ("repo root   : " + $root)
Log ("design doc  : " + $designDoc)
git -C $root rev-parse HEAD 2>&1 | ForEach-Object { Log ("HEAD        : " + $_) }

$docLines = ReadUtf8 $designDoc
Check ($null -ne $docLines) "design doc readable"

# ---------------------------------------------------------------- (a) contract names
Section "(a) contract command/event names: verbatim Select-String hit"
$m2c1 = Join-Path $root 'doc\contracts\M2-C1_TYPED_IPC_CONTRACT.md'
$rc4  = Join-Path $root 'doc\contracts\M2-RC4_DOMAIN_COMMANDS.md'
$p09  = Join-Path $root 'doc\contracts\P09_IMPORT_CONTRACT.md'
$p10  = Join-Path $root 'doc\contracts\P10_CREDENTIAL_CONFIG_CONTRACT.md'
$p11  = Join-Path $root 'doc\contracts\P11_LONG_TASK_LIFECYCLE_CONTRACT.md'

$m2c1Lines = ReadUtf8 $m2c1
$rc4Lines  = ReadUtf8 $rc4

# name -> contract file (the file each name is bound to in design section 6)
$terms = [ordered]@{
    'ListBooks'              = $m2c1
    'ImportPages'            = $m2c1
    'StartRun'               = $m2c1
    'ControlRun'             = $m2c1
    'ResumeBlockedRun'       = $m2c1
    'GetRunSnapshot'         = $m2c1
    'GetTaskProjection'      = $m2c1
    'RetryFailedTargets'     = $m2c1
    'TaskFailed'             = $m2c1
    'RunPaused'              = $m2c1
    'RunCompleted'           = $m2c1
    'CurrentPageStepChanged' = $m2c1
    'ResolvePageResource'    = $m2c1
    'resolve_page_resource'  = $m2c1
    'ListRegions'            = $m2c1
    'list_regions'           = $m2c1
    'SetRegionType'          = $m2c1
    'set_region_type'        = $m2c1
    'list_chapters'          = $m2c1
    'list_chapter_pages'     = $m2c1
    'GetReaderProjection'    = $m2c1
    'SaveReadingProgress'    = $m2c1
    'ReadingProgressChanged' = $m2c1
    'StartExport'            = $m2c1
    'CancelExport'           = $m2c1
    'GetExportSnapshot'      = $m2c1
    'GetExportHistory'       = $m2c1
    'ExportProgressChanged'  = $m2c1
    'settings_get'           = $m2c1
    'settings_update_section'= $m2c1
    'ErrorEnvelope'          = $m2c1
    'PipelineCommand'        = $m2c1
    'list_region_revisions'  = $rc4
    'restore_region_revision'= $rc4
    'rerender_page'          = $rc4
}

foreach ($k in $terms.Keys) {
    $file = $terms[$k]
    $cLines = if ($file -eq $m2c1) { $m2c1Lines } else { $rc4Lines }
    $hitContract = -1
    for ($i = 0; $i -lt $cLines.Count; $i++) {
        if ($cLines[$i].Contains($k)) { $hitContract = $i + 1; break }
    }
    $hitDoc = -1
    for ($i = 0; $i -lt $docLines.Count; $i++) {
        if ($docLines[$i].Contains($k)) { $hitDoc = $i + 1; break }
    }
    $fname = Split-Path $file -Leaf
    if ($hitContract -ge 1 -and $hitDoc -ge 1) {
        Log ("[PASS] {0,-24} contract:{1}:L{2}  designdoc:L{3}" -f $k, $fname, $hitContract, $hitDoc)
    }
    else {
        Log ("[FAIL] {0,-24} contractHit=L{1} designDocHit=L{2}" -f $k, $hitContract, $hitDoc)
        $script:failed++
    }
}
# contract files must exist at all
foreach ($f in @($m2c1, $rc4, $p09, $p10, $p11)) {
    Check (Test-Path $f) ("contract exists: " + (Split-Path $f -Leaf))
}

# ---------------------------------------------------------------- (b) local links
Section "(b) local markdown links in design doc resolve"
$linkRegex = [regex]'\[[^\]]*\]\(([^)\s]+)[^)]*\)'
$docDir = Split-Path $designDoc -Parent
$links = 0; $ext = 0; $anchor = 0; $bad = 0
foreach ($line in $docLines) {
    foreach ($m in $linkRegex.Matches($line)) {
        $t = $m.Groups[1].Value
        if ($t -match '^(https?:|mailto:)') { $ext++; continue }
        if ($t.StartsWith('#')) { $anchor++; continue }
        $links++
        $p = Join-Path $docDir ($t -replace '#.*$', '')
        $p = [System.IO.Path]::GetFullPath($p)
        if (Test-Path -LiteralPath $p) { Log ("[PASS] link -> " + $t) }
        else { Log ("[FAIL] link -> " + $t); $bad++ }
    }
}
$script:failed += $bad
Log ("summary: local=" + $links + " external(skipped)=" + $ext + " pure-anchor(skipped)=" + $anchor)
Check ($bad -eq 0 -and $links -gt 0) "all local links resolve"

# ---------------------------------------------------------------- (c) git scope
Section "(c) git write scope"
$diff = @(git -C $root diff --name-only HEAD 2>$null)
$status = @(git -C $root status --porcelain 2>$null)
Log "git diff --name-only HEAD:"
foreach ($l in $diff) { Log ("  " + $l) }
Log "git status --porcelain:"
foreach ($l in $status) { Log ("  " + $l) }

$allowedExact = @(
    'doc/design/AD001_FOUR_PAGE_UI_BASELINE.md',
    'doc/tasks/UI-DESIGN-1.md'
)
$allowedPrefix = @(
    'doc/handoffs/UI-DESIGN-1-',
    'verification/UI-DESIGN-1/'
)
$forbidden = @(
    'AGENTS.md', '.qoder-credits/report.json', 'doc/00_INDEX.md',
    'doc/01_FUNCTIONAL_ARCHITECTURE.md', 'doc/03_DATA_MODEL.md',
    'doc/04_USER_FLOW.md', 'doc/06_TRANSLATION_PIPELINE.md',
    'doc/09_COLLABORATION.md', 'doc/11_ARCHITECTURE_MAPS.md',
    'doc/12_ROADMAP.md', 'doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md',
    'doc/WORKTREE_SAFETY_INVENTORY.md',
    'doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md', 'doc/tasks/P02-NEW-TIME-X6.md',
    'doc/tasks/P02.md', 'doc/templates/HANDOFF.md', 'doc/templates/REVIEW.md',
    'doc/templates/TASK.md', 'verification/PROJECT-ROADMAP-20261008/ROADMAP.md'
)

$paths = New-Object System.Collections.Generic.List[string]
foreach ($l in $diff) { if ($l) { $paths.Add(($l -replace '\\','/').Trim()) } }
foreach ($l in $status) {
    if ($l -and $l.Length -gt 3) {
        $p = ($l.Substring(3) -replace '\\','/').Trim()
        if ($p) { if (-not $paths.Contains($p)) { $paths.Add($p) } }
    }
}

$scopeOk = $true
foreach ($p in $paths) {
    $ok = $false
    if ($allowedExact -contains $p) { $ok = $true }
    foreach ($pre in $allowedPrefix) { if ($p.StartsWith($pre)) { $ok = $true } }
    if ($forbidden -contains $p) { $ok = $false; Log ("[FAIL] touched forbidden path: " + $p); $scopeOk = $false }
    if (-not $ok) { Log ("[FAIL] out-of-scope path: " + $p); $scopeOk = $false }
}
if ($scopeOk -and $paths.Count -gt 0) {
    Log ("[PASS] all " + $paths.Count + " changed paths inside allowed scope; none of the 19 dirty paths touched")
}
elseif ($paths.Count -eq 0) { Log "[WARN] no changes detected (run before editing?)" }
if (-not $scopeOk) { $script:failed++ }

# ---------------------------------------------------------------- (d) AC1 checklist
Section "(d) AC1/AC2 structure checklist"
$required = @(
    '## 1. 导航 Shell', '## 2. 书架 Bookshelf', '## 3. 工作台 Workbench',
    '## 4. 阅读器 Reader', '## 5. 设置 Settings', '## 6. 契约绑定表',
    '## 7. Wire Gap List', '## 8. 设计令牌', '## 9. 边界合规自证', '## 10. 非目标'
)
foreach ($h in $required) {
    $found = $docLines | Where-Object { $_.Contains($h) }
    Check ($null -ne $found -and $found.Count -ge 1) ("section present: " + $h)
}
$perPage = @{
    '## 2. 书架'   = @('区域职责','布局结构','组件分解','状态矩阵','交互清单','键盘与焦点')
    '## 3. 工作台' = @('区域职责','布局结构','组件分解','状态矩阵','交互清单','键盘与焦点')
    '## 4. 阅读器' = @('区域职责','布局结构','组件分解','状态矩阵','交互清单','键盘与焦点')
    '## 5. 设置'   = @('区域职责','布局结构','组件分解','状态矩阵','交互清单','键盘与焦点')
}
$docText = $docLines -join "`n"
foreach ($page in $perPage.Keys) {
    $start = -1
    for ($i = 0; $i -lt $docLines.Count; $i++) { if ($docLines[$i].Contains($page)) { $start = $i; break } }
    $end = $docLines.Count
    for ($j = $start + 1; $j -lt $docLines.Count; $j++) {
        if ($docLines[$j] -match '^## \d+\. ') { $end = $j; break }
    }
    $seg = ($docLines[$start..($end-1)] -join "`n")
    foreach ($el in $perPage[$page]) {
        Check ($seg.Contains($el)) ($page + " contains element: " + $el)
    }
}
# binding/gap row counts
$wRows = ($docLines | Where-Object { $_ -match '^\| W\d+ \|' }).Count
$gRows = ($docLines | Where-Object { $_ -match '^\| G\d+ \|' }).Count
Log ("binding table rows (W#): " + $wRows + " ; gap rows (G#): " + $gRows)
Check ($wRows -ge 25 -and $gRows -ge 20) "binding >=25 rows and gap >=20 rows"

# ---------------------------------------------------------------- summary
Section "SUMMARY"
if ($script:failed -eq 0) {
    Log "RESULT: ALL CHECKS PASS"
} else {
    Log ("RESULT: " + $script:failed + " CHECK(S) FAILED")
}

[System.IO.File]::WriteAllLines($outFile, $script:log, (New-Object System.Text.UTF8Encoding($false)))
Write-Host ("log written: " + $outFile)
if ($script:failed -eq 0) { exit 0 } else { exit 1 }
