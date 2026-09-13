# Read-only TASK-001 document checks. No product tests or Mermaid rendering.
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
Push-Location $taskRoot
try {
    function Read-TaskText([string]$path) {
        return ([IO.File]::ReadAllText((Join-Path $taskRoot $path))).Replace("`r`n", "`n")
    }
    function Read-BaselineText([string]$path) {
        $lines = & git show "496b4ed:$path"
        if ($LASTEXITCODE -ne 0) { throw "Cannot read baseline: $path" }
        return ($lines -join "`n") + "`n"
    }
    $taskSpec = Read-TaskText 'doc/tasks/TASK-001.md'
    if ($taskSpec -notmatch '(?m)^approval: approved$' -or
        $taskSpec -notmatch '(?m)^status: (in_progress|in_review|approved|done)$') {
        throw 'TASK-001 must be authorized and active or delivered'
    }
    $taskAllowed = @([regex]::Matches($taskSpec, '(?m)^- ((?:doc|verification)/\S+)$') |
        ForEach-Object { $_.Groups[1].Value })
    $taskChanged = @(& git -c core.quotePath=false diff --name-only 496b4ed --)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read changed paths' }
    $taskChanged += @(& git -c core.quotePath=false ls-files --others --exclude-standard)
    if ($LASTEXITCODE -ne 0) { throw 'Cannot read untracked paths' }
    foreach ($taskPath in $taskChanged) {
        if (-not @($taskAllowed | Where-Object { $taskPath -like $_ }).Count) {
            throw "Outside TASK-001 scope: $taskPath"
        }
    }
    $taskOthers = @(Get-ChildItem doc/tasks/TASK-*.md | Where-Object BaseName -ne 'TASK-001')
    if ($taskOthers.Count -ne 26) { throw 'Expected 26 other tasks' }
    foreach ($taskFile in $taskOthers) {
        $taskText = Read-TaskText "doc/tasks/$($taskFile.Name)"
        if ($taskText -notmatch '(?m)^status: proposed$' -or
            $taskText -cne (Read-BaselineText "doc/tasks/$($taskFile.Name)")) {
            throw "Other task changed or started: $($taskFile.Name)"
        }
    }
    Write-Output 'PASS: changed paths authorized; other 26 tasks unchanged and proposed'

    $taskDocs = @(Get-ChildItem doc -Recurse -File -Filter '*.md')
    $taskDocs += Get-Item AGENTS.md
    $taskDocs += @(Get-ChildItem verification/TASK-001 -File -Filter '*.md')
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
        if ($taskFile.Name -match '^0[1-8]_') {
            foreach ($taskMatch in [regex]::Matches($taskText, '`(0[1-8]_[^`\r\n]+\.md)`')) {
                if (-not (Test-Path -LiteralPath (Join-Path 'doc' $taskMatch.Groups[1].Value))) {
                    throw "Missing source document: $($taskMatch.Groups[1].Value)"
                }
            }
            if ($taskText -match 'Failed\s*-->\s*Pending') { throw "Old Run retry transition: $($taskFile.Name)" }
        }
    }
    Write-Output "PASS: $taskLinks local links, source-document references and code fences"

    $taskModel = Read-TaskText 'doc/03_DATA_MODEL.md'
    $taskModelBase = Read-BaselineText 'doc/03_DATA_MODEL.md'
    # Only the source-reference lines may differ in D03.
    $taskRefPattern = '(?m)^> - `0[12]_[^`]+\.md`\n'
    if ([regex]::Replace($taskModel, $taskRefPattern, '') -cne
        [regex]::Replace($taskModelBase, $taskRefPattern, '')) { throw 'D03 model body changed' }
    $taskPipeline = Read-TaskText 'doc/06_TRANSLATION_PIPELINE.md'
    $taskStates03 = [regex]::Match($taskModel, '(?s)```text\n(not_started\npending\nrunning\n.*?)\n```').Groups[1].Value
    $taskStates06 = [regex]::Match($taskPipeline, '(?s)# 71\..*?```text\n(.*?)\n```').Groups[1].Value
    if (-not $taskStates03 -or $taskStates03 -cne $taskStates06) { throw 'StageState mismatch' }
    Write-Output 'PASS: D03 body unchanged; D03/D06 StageState enums match'

    $taskAC = Read-TaskText 'doc/08_ACCEPTANCE_CRITERIA.md'
    $taskACBase = Read-BaselineText 'doc/08_ACCEPTANCE_CRITERIA.md'
    $taskACPattern = '(?m)^## AC-[A-Z0-9-]+ \[P[012]\][^\n]*'
    $taskHeaders = @([regex]::Matches($taskAC, $taskACPattern) | ForEach-Object Value)
    $taskOldHeaders = @([regex]::Matches($taskACBase, $taskACPattern) | ForEach-Object Value)
    if ($taskHeaders.Count -ne 185 -or ($taskHeaders -join "`n") -cne ($taskOldHeaders -join "`n")) {
        throw 'AC IDs, priorities or titles changed'
    }
    Write-Output 'PASS: all 185 AC IDs, priorities and titles preserved'

    $taskIndex = Read-TaskText 'doc/tasks/README.md'
    $taskRoadmap = Read-TaskText 'doc/12_ROADMAP.md'
    if ($taskIndex.Contains('27 个任务均为 proposed') -or $taskRoadmap.Contains('状态都为 proposed')) {
        throw 'Stale all-tasks-proposed assertion'
    }
    $taskFlow = Read-TaskText 'doc/04_USER_FLOW.md'
    if ($taskFlow.Contains('恢复 / 重试 / 放弃') -or $taskFlow.Contains('恢复/重试/放弃')) {
        throw 'Crash action vocabulary is stale'
    }
    $taskMaps = Read-TaskText 'doc/11_ARCHITECTURE_MAPS.md'
    if ($taskMaps -match '(?m)^\s*paused\s*-->\s*cancelled') { throw 'Unsupported paused-to-cancelled transition' }
    if ($taskAC.Contains('字段存在性核验完成')) { throw 'Acceptance spec contains an author verification result' }
    $taskTrace = Read-TaskText 'doc/13_ACCEPTANCE_TRACEABILITY.md'
    if ($taskTrace.Contains('依据 G05/G06')) { throw 'AC-DOC-002 evidence is stale' }
    $taskFunctional = Read-TaskText 'doc/01_FUNCTIONAL_ARCHITECTURE.md'
    if (-not $taskFunctional.Contains('历史材料引用（本仓库无此文件）')) { throw 'Historical source paths are not labelled' }
    $taskNfr = Read-TaskText 'doc/07_NON_FUNCTIONAL_REQUIREMENTS.md'
    if ($taskNfr.Contains('四一级页面')) { throw 'Known NFR typo remains' }
    if (-not $taskSpec.Contains('- doc/reviews/TASK-001-*.md')) { throw 'Review report path is not reusable for re-review' }
    $taskHandoff = Read-TaskText 'doc/handoffs/TASK-001-615a073.md'
    if (-not $taskHandoff.Contains('SHA256（LF 行尾归一化）')) { throw 'Handoff hash normalization is undocumented' }
    if ($taskPipeline.Contains('| 同步项 | D03 证据 |') -or $taskNfr.Contains('| 同步项 | D03 证据 |')) {
        throw 'D03 synchronization mapping is duplicated'
    }
    Write-Output 'PASS: independent review regressions R-001 through R-010 addressed'

    & git diff --check 496b4ed --
    if ($LASTEXITCODE -ne 0) { throw 'Whitespace errors in tracked diff' }
    Write-Output 'PASS: git diff --check (tracked changes); semantic review still required'
} finally {
    Pop-Location
}
