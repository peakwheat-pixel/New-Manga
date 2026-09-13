# Read-only checks for the initial takeover snapshot, not product tests.
# After approval or source-document revision, this snapshot check must be updated.
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskExpected = @{
    '01_FUNCTIONAL_ARCHITECTURE.md' = '5a1af01c966702bc8c7b7da7ab81bb62922444944097362334481d99d060cb78'
    '02_TECHNICAL_ARCHITECTURE_.md' = '499634aecf3e3cdece0e4b6ce80d4e9ec60c6a531f3e82a412e3397604f63189'
    '03_DATA_MODEL.md' = '1cecff6ae8610c721a4bf2fcf8b33a670f18c3a9f72aa612303420f7ff49a26b'
    '04_USER_FLOW.md' = '3b7f858a116b39967f23dc351012bb01f8ca5a71cea6f33259e3cca24e3d2399'
    '05_UI_MAPPING.md' = '9258a8ba14b383e80d86394d373e96ae0f2d981ba27845758a08b0749a1d2ee0'
    '06_TRANSLATION_PIPELINE.md' = '68a9e266542d5c22a1c6e7a98c5a9203879051bffc0c5dc9d5086c4fd50da439'
    '07_NON_FUNCTIONAL_REQUIREMENTS.md' = 'aa8cceb6c027e983fb3b560fdff3464361a366f1b1d629e06f1b860e829b5c00'
    '08_ACCEPTANCE_CRITERIA.md' = 'd3207cc18147ef0839d6a8af9efe8c4fabc2a48c63564a363a1e8196b439767c'
}
foreach ($taskName in $taskExpected.Keys) {
    $taskHash = (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $taskName) -Algorithm SHA256).Hash.ToLower()
    if ($taskHash -ne $taskExpected[$taskName]) { throw "Original changed: $taskName" }
}

$taskMarkdown = @(Get-ChildItem -LiteralPath $PSScriptRoot -Recurse -File -Filter '*.md' |
    Where-Object { -not $taskExpected.ContainsKey($_.Name) })
$taskMarkdown += Get-Item -LiteralPath (Join-Path $taskRoot 'AGENTS.md')
$taskLinkCount = 0
$taskDiagramCount = 0
foreach ($taskFile in $taskMarkdown) {
    $taskText = Get-Content -LiteralPath $taskFile.FullName -Raw -Encoding utf8
    foreach ($taskMatch in [regex]::Matches($taskText, '\[[^\]]*\]\(([^)]+)\)')) {
        $taskTarget = $taskMatch.Groups[1].Value.Trim('<', '>').Split('#')[0]
        if (-not $taskTarget -or $taskTarget -match '^[a-z]+://') { continue }
        $taskResolved = [IO.Path]::GetFullPath((Join-Path $taskFile.DirectoryName $taskTarget))
        if (-not (Test-Path -LiteralPath $taskResolved)) { throw "Broken link: $($taskFile.Name) -> $taskTarget" }
        $taskLinkCount++
    }
    if ([regex]::IsMatch($taskText, '(?m)[ \t]+\r?$')) { throw "Trailing whitespace: $($taskFile.Name)" }
    $taskOpenFence = $false
    foreach ($taskLine in ($taskText -split '\r?\n')) {
        if ($taskLine -match '^~~~') { $taskOpenFence = -not $taskOpenFence }
        if ($taskLine -eq '~~~mermaid') { $taskDiagramCount++ }
    }
    if ($taskOpenFence) { throw "Unclosed fence: $($taskFile.Name)" }
}

$taskGraph = @{}
$taskFiles = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'tasks') -File -Filter 'TASK-*.md')
if ($taskFiles.Count -ne 27) { throw 'Expected 27 planned tasks' }
foreach ($taskFile in $taskFiles) {
    $taskText = Get-Content -LiteralPath $taskFile.FullName -Raw -Encoding utf8
    $taskId = [regex]::Match($taskText, '(?m)^id: (TASK-\d{3})\r?$').Groups[1].Value
    if (-not $taskId -or $taskId -ne $taskFile.BaseName -or $taskGraph.ContainsKey($taskId)) { throw "Invalid task ID: $($taskFile.Name)" }
    foreach ($taskRule in @('status: proposed','approval: pending_user_review','owner: null','reviewer: null','base_commit: null','integration_commit: null')) {
        if (-not [regex]::IsMatch($taskText, ('(?m)^' + [regex]::Escape($taskRule) + '\r?$'))) { throw "Task not frozen: $taskId / $taskRule" }
    }
    $taskDeps = [regex]::Match($taskText, '(?m)^depends_on: \[(.*)\]\r?$').Groups[1].Value
    $taskGraph[$taskId] = @([regex]::Matches($taskDeps, 'TASK-\d{3}') | ForEach-Object { $_.Value })
    if (($taskText -split '- \[ \]').Count -lt 5) { throw "Missing acceptance criteria: $taskId" }
}
$taskVisited = @{}
function Test-TaskDependency([string]$taskNode) {
    if (-not $taskGraph.ContainsKey($taskNode)) { throw "Unknown dependency: $taskNode" }
    if ($taskVisited[$taskNode] -eq 1) { throw "Dependency cycle: $taskNode" }
    if ($taskVisited[$taskNode] -eq 2) { return }
    $taskVisited[$taskNode] = 1
    foreach ($taskDependency in $taskGraph[$taskNode]) { Test-TaskDependency $taskDependency }
    $taskVisited[$taskNode] = 2
}
foreach ($taskNode in $taskGraph.Keys) { Test-TaskDependency $taskNode }

$taskSourceAC = Get-Content -LiteralPath (Join-Path $PSScriptRoot '08_ACCEPTANCE_CRITERIA.md') -Raw -Encoding utf8
$taskACs = @([regex]::Matches($taskSourceAC, '(?m)^## (AC-[A-Z0-9-]+) \[(P[012])\]') | ForEach-Object { $_.Groups[1].Value })
$taskTrace = Get-Content -LiteralPath (Join-Path $PSScriptRoot '13_ACCEPTANCE_TRACEABILITY.md') -Raw -Encoding utf8
$taskMapped = @([regex]::Matches($taskTrace, '(?m)^\| (AC-[A-Z0-9-]+-\d{3}) \|') | ForEach-Object { $_.Groups[1].Value })
if ($taskACs.Count -ne 185 -or $taskMapped.Count -ne 185) { throw 'Incorrect AC count' }
if (@($taskMapped | Select-Object -Unique).Count -ne 185) { throw 'Duplicate AC mapping' }
if (Compare-Object $taskACs $taskMapped) { throw 'Missing or unexpected AC mapping' }
foreach ($taskMatch in [regex]::Matches($taskTrace, '\]\(tasks/(TASK-\d{3})\.md\)')) {
    if (-not $taskGraph.ContainsKey($taskMatch.Groups[1].Value)) { throw 'AC points to an unknown Task' }
}
$taskGroups = @([regex]::Matches($taskSourceAC, '(?m)^# \d+\. (AC-[A-Z-]+)') | ForEach-Object { $_.Groups[1].Value })
foreach ($taskGroup in $taskGroups) {
    if (-not $taskTrace.Contains($taskGroup)) { throw "Unmapped AC group: $taskGroup" }
}
foreach ($taskPath in @('src','tests','pyproject.toml','requirements.txt','package.json','.github')) {
    if (Test-Path -LiteralPath (Join-Path $taskRoot $taskPath)) { throw "Implementation detected: $taskPath" }
}
Write-Output "PASS: 8 original SHA256 hashes unchanged"
Write-Output "PASS: $($taskMarkdown.Count) new Markdown files, $taskLinkCount local links"
Write-Output 'PASS: 27 frozen tasks, dependencies exist and are acyclic'
Write-Output "PASS: 185 numbered ACs and $($taskGroups.Count) AC topic groups mapped"
Write-Output "PASS: $taskDiagramCount Mermaid fences structurally balanced (not render validation)"
Write-Output 'PASS: no application source, product tests or implementation scaffold created'
