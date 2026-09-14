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
    $resultEnum = @('PASS', 'FAIL', 'BLOCKED', 'NOT_RUN', 'N/A')

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
    foreach ($forbidden in @('AGENTS.md', 'doc/STATUS.md', 'doc/08_ACCEPTANCE_CRITERIA.md', 'doc/07_NON_FUNCTIONAL_REQUIREMENTS.md')) {
        if ($taskChanged -contains $forbidden) { throw "TASK-003 must not modify $forbidden" }
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
    if ($taskAC -cne $taskACBase) { throw 'D08 changed: product acceptance criteria must stay untouched' }
    $taskACPattern = '(?m)^## AC-[A-Z0-9-]+ \[P[012]\][^\n]*'
    $taskHeaders = @([regex]::Matches($taskAC, $taskACPattern) | ForEach-Object Value)
    if ($taskHeaders.Count -ne 185 -or ($taskHeaders | Select-Object -Unique).Count -ne 185) {
        throw 'Expected 185 unique AC headers'
    }
    Write-Output 'PASS: D08 unchanged; all 185 AC IDs, priorities and titles intact and unique'

    # --- 5. Stable ACG identifiers: table rows, uniqueness, full coverage -----
    $taskSpec3 = Read-TaskText 'doc/verification-plan/TASK-003_ACCEPTANCE_AND_FIXTURE_SPEC.md'
    $taskTrace = Read-TaskText 'doc/13_ACCEPTANCE_TRACEABILITY.md'
    $specAcg = @([regex]::Matches($taskSpec3, '(?m)^\| `(ACG-[A-Z0-9-]+)` \|') | ForEach-Object { $_.Groups[1].Value })
    $traceAcg = @([regex]::Matches($taskTrace, '(?m)^\| `(ACG-[A-Z0-9-]+)` \|') | ForEach-Object { $_.Groups[1].Value })
    if ($specAcg.Count -ne ($specAcg | Select-Object -Unique).Count) { throw 'Duplicate ACG row in the method spec' }
    if ($traceAcg.Count -ne ($traceAcg | Select-Object -Unique).Count) { throw 'Duplicate ACG row in D13' }
    if ((($specAcg | Sort-Object) -join ',') -cne (($traceAcg | Sort-Object) -join ',')) {
        throw 'ACG identifier sets differ between spec and D13'
    }
    if ($specAcg.Count -ne 24) { throw "Expected 24 ACG identifiers, found $($specAcg.Count)" }
    $acgExt = @($specAcg | Where-Object { $_ -like 'ACG-EXT-*' })
    $acgGlobal = @($specAcg | Where-Object { $_ -in @('ACG-AUTOTEST', 'ACG-UITEST', 'ACG-VISUAL', 'ACG-BENCH', 'ACG-DATASAFE', 'ACG-RELEASECHECK', 'ACG-READY') })
    if ($acgExt.Count -ne 7) { throw "Expected 7 ACG-EXT identifiers, found $($acgExt.Count)" }
    if ($acgGlobal.Count -ne 7) { throw "Expected 7 D08 global-spec ACG identifiers, found $($acgGlobal.Count)" }
    if ($taskTrace -match '(?m)^\| AC-DPI \|') { throw 'D13 still uses the old non-stable group label' }
    if ($taskSpec3 -notmatch '§74' -or $taskSpec3 -notmatch '§75') {
        throw 'Spec must document why D08 §74/§75 are excluded'
    }
    foreach ($acg in $specAcg) {
        $rows = @([regex]::Matches($taskTrace, "(?m)^\| ``$([regex]::Escape($acg))`` \|")).Count
        if ($rows -ne 1) { throw "ACG row missing or duplicated in D13: $acg" }
    }
    Write-Output "PASS: 24 unique ACG identifiers (10 topic + 7 global + 7 extension), rows unique in both tables"

    # --- 6. Every ACG result is a single legal enum value ---------------------
    foreach ($row in [regex]::Matches($taskTrace, '(?m)^\| `(ACG-[A-Z0-9-]+)` \|.*$')) {
        $cells = @($row.Value.Trim('|').Split('|') | ForEach-Object { $_.Trim() })
        $acgId = $cells[0]
        $acgResult = $cells[-1]
        if ($resultEnum -notcontains $acgResult) {
            throw "ACG row uses a non-enum result: $acgId -> '$acgResult'"
        }
    }
    if ($taskTrace -match 'PASS（契约层）') { throw 'ACG-SYNC still carries a composite result value' }
    Write-Output 'PASS: every ACG row carries exactly one legal result enum value'

    # --- 7. Method spec must not keep a result copy (single source of truth) --
    if ($taskSpec3 -match '(?m)\|\s*当前结果\s*\|') { throw 'Method spec still maintains a result column' }
    if ($taskSpec3 -match '(?m)\|\s*已取得（available）') { throw 'Method spec still maintains a result summary' }
    if ($taskSpec3 -notmatch '结果真值的唯一位置') { throw 'Method spec does not state the result-truth rule' }
    Write-Output 'PASS: method spec keeps no result copy; result truth stays in D13 / commit-bound reports'

    # --- 8. Fixture manifest fields, states, licence and hash discipline ------
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
    $fxRows = @([regex]::Matches($taskFixtures, '(?m)^\| `(?:FX|DS)-[A-Z0-9-]+` \|.*$'))
    if ($fxRows.Count -lt 20) { throw "Fixture manifest: expected at least 20 inventory rows, found $($fxRows.Count)" }
    $fxAvailable = 0
    foreach ($row in $fxRows) {
        $cells = @($row.Value.Trim('|').Split('|') | ForEach-Object { $_.Trim() })
        if ($cells.Count -ne 7) { throw "Fixture row does not have 7 columns: $($row.Value)" }
        $fxId = $cells[0]; $fxSource = $cells[2]; $fxHash = $cells[5]; $fxState = $cells[6]
        if ($resultEnum -notcontains $fxState -and $fxState -notin @('planned', 'missing', 'available', 'rejected')) {
            throw "Fixture row has an unknown state: $fxId -> $fxState"
        }
        if ($fxState -in @('planned', 'missing')) {
            if ($fxHash -ne 'NOT_AVAILABLE') { throw "Fixture row claims a content hash before acquisition: $fxId" }
        }
        if ($fxState -eq 'available') {
            $fxAvailable++
            if ($fxSource -match '待定') { throw "available fixture has unconfirmed licence: $fxId" }
            if ($fxHash -notmatch '^[0-9a-f]{64}$') { throw "available fixture lacks a real SHA256: $fxId" }
        }
    }
    if ($taskFixtures -notmatch 'NOT_AVAILABLE') { throw 'Fixture manifest: unacquired hash marker missing' }
    if ($taskFixtures -notmatch '(?m)^\| 未取得（missing） \|') { throw 'Fixture manifest: missing-state summary row absent' }
    Write-Output "PASS: fixture manifest fields/states, $($fxRows.Count) rows, hash discipline and licence rule ($fxAvailable available)"

    # --- 9. Capacity routing: every numbered AC-CAP has a dataset -------------
    foreach ($pair in @('AC-CAP-001→DS-E', 'AC-CAP-002→DS-B2', 'AC-CAP-003→DS-C', 'AC-CAP-004→DS-D')) {
        if (-not $taskSpec3.Contains($pair)) { throw "Capacity dataset route missing in spec: $pair" }
    }
    foreach ($ds in @('DS-B2', 'DS-C', 'DS-D', 'DS-E')) {
        if ($taskFixtures -notmatch "\| ``$ds`` \|") { throw "Capacity dataset missing from manifest: $ds" }
    }
    Write-Output 'PASS: AC-CAP-001..004 each route to an existing dataset (DS-E/DS-B2/DS-C/DS-D)'

    # --- 10. ACG-SMOKE covers the complete D08 §53 flow ----------------------
    foreach ($step in @('启动', '默认书架', '创建 Book', '创建 Chapter', '导入 Page', '进入工作台',
        '执行至少一个 Mock / Local Pipeline', '保存', '阅读', '导出', '关闭', '再启动', '数据仍存在')) {
        if (-not $taskSpec3.Contains($step)) { throw "ACG-SMOKE step missing from spec: $step" }
    }
    Write-Output 'PASS: ACG-SMOKE documents the full D08 §53 flow including restart persistence'

    # --- 11. F-08: exactly one edge added per file, and nothing removed -------
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
    $removed = @($f08Diff | Where-Object { $_ -match '^-' -and $_ -notmatch '^---' })
    if ($removed.Count -ne 0) { throw "F-08 removed content from D02/D04/D11: $($removed -join ' ; ')" }
    if ($added.Count -ne 3) { throw "F-08 touched more than the three state edges (added lines: $($added.Count))" }
    foreach ($line in $added) {
        if ($line -notmatch '^\+\s*(Blocked --> Cancelled|blocked --> cancelled)') {
            throw "F-08 introduced an unexpected change: $line"
        }
    }
    Write-Output 'PASS: F-08 is exactly one added edge per file in D02/D04/D11, with no deletions'

    # --- 12. Result enum, performance protocol and threshold discipline -------
    foreach ($token in $resultEnum) {
        if ($taskSpec3 -notmatch [regex]::Escape($token)) { throw "Spec is missing result enum token: $token" }
    }
    if ($taskSpec3 -notmatch '3 次预热' -or $taskSpec3 -notmatch '20 次' -or
        $taskSpec3 -notmatch '1 次预热' -or $taskSpec3 -notmatch '5 次' -or $taskSpec3 -notmatch 'P95') {
        throw 'Performance measurement protocol is not fixed as required'
    }
    foreach ($token in @('nearest-rank', '单调时钟', 'excluded', '冷启动', '计时边界')) {
        if ($taskSpec3 -notmatch [regex]::Escape($token)) { throw "Performance protocol incomplete, missing: $token" }
    }
    if ($taskSpec3 -notmatch 'UNAPPROVED_THRESHOLD') { throw 'Model threshold status marker missing' }
    if ($taskSpec3 -match '(?m)^\|\s*(OCR|翻译|Inpaint)[^\n]*\|\s*\d+(\.\d+)?\s*%') {
        throw 'Spec contains an invented model quality threshold'
    }
    if ($taskSpec3 -match '首次使用提示') { throw 'Spec contains the unapproved privacy prompt' }
    Write-Output 'PASS: result enum, full performance protocol, UNAPPROVED_THRESHOLD and scope discipline intact'

    # --- 13. Documentation links and code fences ------------------------------
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

    & git diff --check 9472df5 --
    if ($LASTEXITCODE -ne 0) { throw 'Whitespace errors in tracked diff' }
    Write-Output 'PASS: git diff --check; owner-authored guards only, independent Review still required'
} finally {
    Pop-Location
}
