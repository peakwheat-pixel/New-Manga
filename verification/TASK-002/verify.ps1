# Read-only TASK-002 contract checks. No product, SQL, Mermaid, model, or performance tests.
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
Push-Location $taskRoot
try {
    function Read-TaskText([string]$path) {
        return ([IO.File]::ReadAllText((Join-Path $taskRoot $path))).Replace("`r`n", "`n")
    }
    function Read-BaselineText([string]$path) {
        $lines = & git show "b1b3f5d:$path"
        if ($LASTEXITCODE -ne 0) { throw "Cannot read baseline: $path" }
        return ($lines -join "`n") + "`n"
    }

    $taskSpec = Read-TaskText 'doc/tasks/TASK-002.md'
    if ($taskSpec -notmatch '(?m)^approval: approved$' -or
        $taskSpec -notmatch '(?m)^status: (in_progress|in_review|approved|done)$' -or
        $taskSpec -notmatch '(?m)^base_commit: b1b3f5d$') {
        throw 'TASK-002 must be authorized on b1b3f5d'
    }
    $taskAllowed = @([regex]::Matches($taskSpec, '(?m)^- ((?:doc|verification)/\S+)$') |
        ForEach-Object { $_.Groups[1].Value })
    $taskChanged = @(& git -c core.quotePath=false diff --name-only b1b3f5d --)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read changed paths' }
    $taskChanged += @(& git -c core.quotePath=false ls-files --others --exclude-standard)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read untracked paths' }
    foreach ($taskPath in $taskChanged) {
        if (-not @($taskAllowed | Where-Object { $taskPath -like $_ }).Count) {
            throw "Outside TASK-002 scope: $taskPath"
        }
    }

    if ((Read-TaskText 'doc/tasks/TASK-001.md') -cne (Read-BaselineText 'doc/tasks/TASK-001.md')) {
        throw 'TASK-001 changed after integration'
    }
    $taskOthers = @(Get-ChildItem doc/tasks/TASK-*.md | Where-Object BaseName -notin @('TASK-001', 'TASK-002'))
    if ($taskOthers.Count -ne 25) { throw 'Expected 25 frozen tasks' }
    foreach ($taskFile in $taskOthers) {
        $taskText = Read-TaskText "doc/tasks/$($taskFile.Name)"
        if ($taskText -notmatch '(?m)^status: proposed$' -or
            $taskText -cne (Read-BaselineText "doc/tasks/$($taskFile.Name)")) {
            throw "Frozen task changed or started: $($taskFile.Name)"
        }
    }
    Write-Output 'PASS: changed paths authorized; TASK-001 unchanged; other 25 tasks frozen'

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
    Write-Output "PASS: $taskLinks local links and code fences"

    $taskContract = Read-TaskText 'doc/contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md'
    foreach ($taskSection in 1..12) {
        if ($taskContract -notmatch "(?m)^## $taskSection\.") { throw "Missing contract section $taskSection" }
    }
    if ($taskContract -match '(?i)\b(TBD|TODO|FIXME)\b') { throw 'Contract contains a placeholder' }
    foreach ($taskToken in @(
        'Region.current_revision_id', 'StepRunInputRef', 'StepRunOutputRef', 'StepResultCandidate',
        'PipelineRunStatus', 'PipelineTaskStatus', 'StepRunStatus', 'PlanDecision', 'StageState', 'ReviewState',
        'EMPTY_TARGET_SELECTION', 'OUTPUT_MAPPING_MISMATCH', 'COMPOSITION_BASE_CHANGED',
        'restart_after_interruption', 'abandoned_after_interruption'
    )) {
        if (-not $taskContract.Contains($taskToken)) { throw "Missing frozen contract token: $taskToken" }
    }
    $taskVectors = @([regex]::Matches($taskContract, '(?m)^\| V(\d{2}) \|') | ForEach-Object Value)
    if ($taskVectors.Count -ne 19 -or ($taskVectors | Select-Object -Unique).Count -ne 19) {
        throw 'Expected 19 unique TASK-002 verification vectors'
    }
    foreach ($taskToken in @(
        '### 11.1 覆盖矩阵', '| Revision、人工保护、Pin |', '| Translation Memory |',
        '| RunTarget 与快照 |', '| 输入输出映射 |', '| 状态、控制与进度 |',
        '| Invalidation 与 SFX |', '| 原子提交、Candidate 与局部合成 |',
        '| V16 | 正常 |', '| V17 | 边界 |', '| V18 | 边界/失败 |', '| V19 | 正常/边界 |'
    )) {
        if (-not $taskContract.Contains($taskToken)) { throw "Missing verification coverage: $taskToken" }
    }
    Write-Output 'PASS: 12 contract sections, required tokens, coverage matrix, and V01-V19 present; no placeholders'

    $taskTechnical = Read-TaskText 'doc/02_TECHNICAL_ARCHITECTURE_.md'
    foreach ($taskToken in @('Pending --> Blocked', 'Running --> Blocked', 'Paused --> Cancelled', 'Interrupted --> Cancelled',
        'TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md')) {
        if (-not $taskTechnical.Contains($taskToken)) { throw "Technical architecture not synchronized: $taskToken" }
    }
    if ($taskTechnical.Contains('Restart / Abandon 的完整落库语义，由 TASK-002 冻结')) {
        throw 'Technical architecture still marks Restart/Abandon unresolved'
    }
    $taskPipeline = Read-TaskText 'doc/06_TRANSLATION_PIPELINE.md'
    foreach ($taskToken in @('SKIP_LOCK', 'blocked_page_count', 'restart_after_interruption',
        'abandoned_after_interruption', 'OUTPUT_MAPPING_MISMATCH', 'StepResultCandidate')) {
        if (-not $taskPipeline.Contains($taskToken)) { throw "Pipeline not synchronized: $taskToken" }
    }
    if ($taskPipeline -match '(?s)### BLOCKED.*?Page Lock.*?Provider 不可用') {
        throw 'Locks remain classified as BLOCKED'
    }
    $taskFlow = Read-TaskText 'doc/04_USER_FLOW.md'
    if ($taskFlow.Contains('Restart / Abandon 的完整语义留待 TASK-002 冻结')) {
        throw 'Crash semantics still marked unresolved'
    }
    if (-not $taskFlow.Contains('Running --> Blocked')) { throw 'User flow lacks running-to-blocked aggregation' }
    $taskMaps = Read-TaskText 'doc/11_ARCHITECTURE_MAPS.md'
    if ($taskMaps.Contains('Restart/Abandon 的落库方式') -or
        $taskMaps.Contains('candidate 或 needs_review 的具体存储仍是') -or
        $taskMaps.Contains('interrupted --> interrupted')) {
        throw 'Derived architecture still marks frozen semantics unresolved'
    }
    if (-not $taskMaps.Contains('running --> blocked')) { throw 'Derived state machine lacks running-to-blocked aggregation' }
    $taskUi = Read-TaskText 'doc/05_UI_MAPPING.md'
    foreach ($taskToken in @('## Blocked', '阻塞 1', '[查看原因] [重新规划]', '## Cancelled / Failed')) {
        if (-not $taskUi.Contains($taskToken)) { throw "UI mapping not synchronized: $taskToken" }
    }
    Write-Output 'PASS: D02-D06/D08/D11 reference the frozen contract without known stale conflicts'

    $taskAC = Read-TaskText 'doc/08_ACCEPTANCE_CRITERIA.md'
    $taskACBase = Read-BaselineText 'doc/08_ACCEPTANCE_CRITERIA.md'
    $taskACPattern = '(?m)^## AC-[A-Z0-9-]+ \[P[012]\][^\n]*'
    $taskHeaders = @([regex]::Matches($taskAC, $taskACPattern) | ForEach-Object Value)
    $taskOldHeaders = @([regex]::Matches($taskACBase, $taskACPattern) | ForEach-Object Value)
    if ($taskHeaders.Count -ne 185 -or ($taskHeaders -join "`n") -cne ($taskOldHeaders -join "`n")) {
        throw 'AC IDs, priorities or titles changed'
    }
    if (-not $taskAC.Contains('阻塞页数与原因')) { throw 'AC-PROGRESS-002 does not cover blocked progress' }
    $taskGaps = Read-TaskText 'doc/10_CURRENT_STATE_AND_GAPS.md'
    foreach ($taskGap in 6..13) {
        if ($taskGaps -notmatch "(?m)^\| G$('{0:d2}' -f $taskGap) \|") { throw "Missing TASK-002 disposition for G$taskGap" }
    }
    Write-Output 'PASS: all 185 AC headers preserved; G06-G13 dispositions recorded'

    & git diff --check b1b3f5d --
    if ($LASTEXITCODE -ne 0) { throw 'Whitespace errors in tracked diff' }
    Write-Output 'PASS: git diff --check; checks are owner-authored guards, not independent approval'
} finally {
    Pop-Location
}
