# Read-only TASK-003 verification checks. Owner-authored guard; NOT independent approval.
# No product, SQL, model, Mermaid-render or performance tests are performed here.
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
Push-Location $taskRoot
try {
    function Read-TaskText([string]$path) {
        return ([IO.File]::ReadAllText((Join-Path $taskRoot $path))).Replace("`r`n", "`n")
    }
    function Read-BaselineText([string]$path) {
        $lines = & git show "9472df5:$path"
        if ($LASTEXITCODE -ne 0) { throw "Cannot read baseline: $path" }
        return ($lines -join "`n") + "`n"
    }

    # --- 1. Task authorization and fixed baseline -----------------------------
    $taskSpec = Read-TaskText 'doc/tasks/TASK-003.md'
    if ($taskSpec -notmatch '(?m)^approval: approved$' -or
        $taskSpec -notmatch '(?m)^status: (in_progress|in_review|approved|done)$' -or
        $taskSpec -notmatch '(?m)^base_commit: 9472df5') {
        throw 'TASK-003 must be authorized on base_commit 9472df5'
    }
    if ($taskSpec -notmatch '(?m)^reviewer: Codex$' -or $taskSpec -notmatch '(?m)^owner: DeepSeek Harness$') {
        throw 'TASK-003 owner/reviewer separation changed'
    }

    # --- 2. Changed paths stay inside allowed_paths ---------------------------
    $taskAllowed = @([regex]::Matches($taskSpec, '(?m)^- ((?:doc|verification)/\S+)$') |
        ForEach-Object { $_.Groups[1].Value })
    if ($taskAllowed.Count -lt 8) { throw 'TASK-003 allowed_paths list looks truncated' }
    $taskChanged = @(& git -c core.quotePath=false diff --name-only 9472df5 --)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read changed paths' }
    $taskChanged += @(& git -c core.quotePath=false ls-files --others --exclude-standard)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read untracked paths' }
    foreach ($taskPath in $taskChanged) {
        if (-not @($taskAllowed | Where-Object { $taskPath -like $_ }).Count) {
            throw "Outside TASK-003 scope: $taskPath"
        }
    }

    # --- 3. Other tasks stay frozen -------------------------------------------
    foreach ($frozen in @('TASK-001', 'TASK-002')) {
        if ((Read-TaskText "doc/tasks/$frozen.md") -cne (Read-BaselineText "doc/tasks/$frozen.md")) {
            throw "$frozen changed after integration"
        }
    }
    $taskOthers = @(Get-ChildItem doc/tasks/TASK-*.md | Where-Object BaseName -notin @('TASK-001', 'TASK-002', 'TASK-003'))
    if ($taskOthers.Count -ne 24) { throw 'Expected 24 frozen tasks' }
    foreach ($taskFile in $taskOthers) {
        $taskText = Read-TaskText "doc/tasks/$($taskFile.Name)"
        if ($taskText -notmatch '(?m)^status: proposed$' -or
            $taskText -cne (Read-BaselineText "doc/tasks/$($taskFile.Name)")) {
            throw "Frozen task changed or started: $($taskFile.Name)"
        }
    }
    Write-Output 'PASS: changed paths authorized; TASK-001/002 unchanged; other 24 tasks frozen'

    # --- 4. All 185 numbered AC keep ID, priority and title -------------------
    $taskAC = Read-TaskText 'doc/08_ACCEPTANCE_CRITERIA.md'
    $taskACBase = Read-BaselineText 'doc/08_ACCEPTANCE_CRITERIA.md'
    $taskACPattern = '(?m)^## AC-[A-Z0-9-]+ \[P[012]\][^\n]*'
    $taskHeaders = @([regex]::Matches($taskAC, $taskACPattern) | ForEach-Object Value)
    $taskOldHeaders = @([regex]::Matches($taskACBase, $taskACPattern) | ForEach-Object Value)
    if ($taskHeaders.Count -ne 185 -or ($taskHeaders -join "`n") -cne ($taskOldHeaders -join "`n")) {
        throw 'AC IDs, priorities or titles changed'
    }
    if ($taskHeaders.Count -ne ($taskHeaders | Select-Object -Unique).Count) { throw 'Duplicate AC header' }
    Write-Output 'PASS: all 185 AC IDs, priorities and titles unchanged and unique'

    # --- 5. Stable ACG-* group identifiers ------------------------------------
    $taskSpec3 = Read-TaskText 'doc/verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md'
    $taskTrace = Read-TaskText 'doc/13_ACCEPTANCE_TRACEABILITY.md'
    $acgSpec = @([regex]::Matches($taskSpec3, '`(ACG-[A-Z0-9-]+)`') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
    $acgTrace = @([regex]::Matches($taskTrace, '`(ACG-[A-Z0-9-]+)`') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique)
    if ($acgSpec.Count -ne 10) { throw "Expected 10 ACG identifiers in the spec, found $($acgSpec.Count)" }
    if ($acgTrace.Count -ne 10) { throw "Expected 10 ACG identifiers in D13, found $($acgTrace.Count)" }
    if ((($acgSpec | Sort-Object) -join ',') -cne (($acgTrace | Sort-Object) -join ',')) {
        throw 'ACG identifier sets differ between spec and D13'
    }
    foreach ($acg in $acgSpec) {
        $rows = @([regex]::Matches($taskTrace, "(?m)^\| ``$([regex]::Escape($acg))`` \|")).Count
        if ($rows -ne 1) { throw "ACG row missing or duplicated in D13: $acg" }
    }
    if ($taskTrace -match '(?m)^\| AC-DPI \|') { throw 'D13 still uses the old non-stable group label' }
    Write-Output "PASS: 10 unique ACG identifiers, consistent between spec and D13 ($((($acgSpec | Sort-Object) -join ', ')))"

    # --- 6. Fixture manifest required fields ----------------------------------
    $taskFixtures = Read-TaskText 'doc/fixtures/MANIFEST.md'
    if ($taskFixtures -notmatch '(?m)^\| `ID` \| 素材唯一标识 \|') { throw 'Fixture manifest: ID field missing' }
    foreach ($field in @('场景', '来源/许可', '生成方式', '预期属性', 'Hash', '状态')) {
        if ($taskFixtures -notmatch [regex]::Escape("| ``$field`` |")) { throw "Fixture manifest: field not documented: $field" }
    }
    if ($taskFixtures -notmatch '(?m)^\| ID \| 场景 \| 来源/许可 \| 生成方式 \| 预期属性 \| Hash \| 状态 \|$') {
        throw 'Fixture manifest: inventory table header is not the required 7-column form'
    }
    foreach ($state in @('planned', 'missing', 'available', 'rejected')) {
        if ($taskFixtures -notmatch "(?m)^$state\s") { throw "Fixture manifest: state not enumerated: $state" }
    }
    $fxRows = @([regex]::Matches($taskFixtures, '(?m)^\| `(FX|DS)-[A-Z0-9-]+` \|'))
    if ($fxRows.Count -lt 19) { throw "Fixture manifest: expected at least 19 inventory rows, found $($fxRows.Count)" }
    if ($taskFixtures -notmatch 'NOT_AVAILABLE') { throw 'Fixture manifest: unacquired hash marker missing' }
    foreach ($row in [regex]::Matches($taskFixtures, '(?m)^\| `(?:FX|DS)-[A-Z0-9-]+` \|.*$')) {
        $cells = @($row.Value.Trim('|').Split('|') | ForEach-Object { $_.Trim() })
        if ($cells.Count -ne 7) { throw "Fixture row does not have 7 columns: $($row.Value)" }
        if ($cells[6] -in @('planned', 'missing') -and $cells[5] -ne 'NOT_AVAILABLE') {
            throw "Fixture row claims a content hash before acquisition: $($cells[0])"
        }
    }
    Write-Output "PASS: fixture manifest fields, states and $($fxRows.Count) inventory rows present; no fabricated hashes"

    # --- 7. F-08: Blocked -> Cancelled present, and nothing else added --------
    foreach ($pair in @(
        @{ File = 'doc/02_TECHNICAL_ARCHITECTURE_.md'; Edge = '    Blocked --> Cancelled: Stop' },
        @{ File = 'doc/04_USER_FLOW.md';             Edge = '    Blocked --> Cancelled: 停止' },
        @{ File = 'doc/11_ARCHITECTURE_MAPS.md';     Edge = '    blocked --> cancelled: stop' })) {
        if (-not (Read-TaskText $pair.File).Contains($pair.Edge)) {
            throw "F-08 edge missing in $($pair.File)"
        }
    }
    $f08Diff = @(& git diff 9472df5 -- doc/02_TECHNICAL_ARCHITECTURE_.md doc/04_USER_FLOW.md doc/11_ARCHITECTURE_MAPS.md)
    $added = @($f08Diff | Where-Object { $_ -match '^\+' -and $_ -notmatch '^\+\+\+' })
    if ($added.Count -ne 3) { throw "F-08 touched more than the three state edges (added lines: $($added.Count))" }
    foreach ($line in $added) {
        if ($line -notmatch '^\+\s*(Blocked --> Cancelled|blocked --> cancelled)') {
            throw "F-08 introduced an unexpected change: $line"
        }
    }
    Write-Output 'PASS: F-08 closed with exactly one Blocked-to-Cancelled edge in each of D02/D04/D11'

    # --- 8. Documentation links and code fences -------------------------------
    $taskDocs = @(Get-ChildItem doc -Recurse -File -Filter '*.md')
    $taskDocs += Get-Item AGENTS.md
    $taskLinks = 0
    foreach ($taskFile in $taskDocs) {
        $taskText = [IO.File]::ReadAllText($taskFile.FullName)
        foreach ($taskMatch in [regex]::Matches($taskText, '\[[^\]]*\]\(([^)]+)\)')) {
            $taskTarget = $taskMatch.Groups[1].Value.Trim('<', '>').Split('#')[0]
            if (-not $taskTarget -or $taskTarget -match '^[a-z]+://') { continue }
            if (-not (Test-Path -LiteralPath (Join-Path $taskFile.DirectoryName $taskTarget))) {
                throw "Broken link: $($taskFile.Name) -> $taskTarget"
            }
            $taskLinks++
        }
        $taskFence = $null
        foreach ($taskLine in ($taskText -split '\r?\n')) {
            if (-not $taskFence -and $taskLine -match '^(`{3,}|~{3,})') {
                $taskFence = $Matches[1]
            } elseif ($taskFence -and $taskLine -match ('^' + [regex]::Escape($taskFence) + '\s*$')) {
                $taskFence = $null
            }
        }
        if ($taskFence) { throw "Unclosed code fence: $($taskFile.Name)" }
    }
    Write-Output "PASS: $taskLinks local links and all code fences valid"

    # --- 9. Result enum, performance protocol and threshold discipline --------
    foreach ($token in @('PASS', 'FAIL', 'BLOCKED', 'NOT_RUN', 'N/A')) {
        if ($taskSpec3 -notmatch [regex]::Escape($token)) { throw "Spec is missing result enum token: $token" }
    }
    if ($taskSpec3 -notmatch '3 次预热' -or $taskSpec3 -notmatch '20 次' -or
        $taskSpec3 -notmatch '1 次预热' -or $taskSpec3 -notmatch '5 次' -or $taskSpec3 -notmatch 'P95') {
        throw 'Performance measurement protocol is not fixed as required'
    }
    if ($taskSpec3 -notmatch 'UNAPPROVED_THRESHOLD') { throw 'Model threshold status marker missing' }
    if ($taskSpec3 -match '(?m)^\|\s*(OCR|翻译|Inpaint)[^\n]*\|\s*\d+(\.\d+)?\s*%') {
        throw 'Spec contains an invented model quality threshold'
    }
    Write-Output 'PASS: result enum, performance protocol and UNAPPROVED_THRESHOLD discipline present'

    & git diff --check 9472df5 --
    if ($LASTEXITCODE -ne 0) { throw 'Whitespace errors in tracked diff' }
    Write-Output 'PASS: git diff --check; owner-authored guards only, independent Review still required'
} finally {
    Pop-Location
}
