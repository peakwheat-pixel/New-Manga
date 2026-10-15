[CmdletBinding()]
param(
    [string]$TaskPath
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Add-Error([string]$Message) { $script:errors.Add($Message) }
function Add-Warning([string]$Message) { $script:warnings.Add($Message) }

function Resolve-LocalPath([string]$Value, [string]$BaseDirectory) {
    $path = $Value.Trim().Trim('`').Trim('<', '>')
    if ([string]::IsNullOrWhiteSpace($path)) { return $null }
    $path = [uri]::UnescapeDataString(($path -split '[?#]', 2)[0])
    if ($path -match '^(?i:https?|mailto|codex)://' -or $path.StartsWith('#')) { return $null }
    $path = $path.Replace('/', [IO.Path]::DirectorySeparatorChar)
    if (-not [IO.Path]::IsPathRooted($path)) { $path = Join-Path $BaseDirectory $path }
    return [IO.Path]::GetFullPath($path)
}

function Get-FrontMatter([string]$Text) {
    $match = [regex]::Match($Text, '(?s)^---\s*\r?\n(?<body>.*?)\r?\n---\s*(?:\r?\n|$)')
    $fields = @{}
    if (-not $match.Success) { return $fields }
    foreach ($line in ($match.Groups['body'].Value -split '\r?\n')) {
        if ($line -match '^([A-Za-z0-9_-]+):\s*(.*?)\s*$') {
            $value = $Matches[2].Trim().Trim("'").Trim('"')
            $fields[$Matches[1]] = $value
        }
    }
    return $fields
}

function Get-Section([string]$Text, [string]$Heading) {
    $pattern = '(?ms)^##\s+' + [regex]::Escape($Heading) + '\s*\r?\n(?<body>.*?)(?=^##\s+|\z)'
    $match = [regex]::Match($Text, $pattern)
    if ($match.Success) { return $match.Groups['body'].Value }
    return ''
}

function Get-TableRows([string]$Section) {
    $rows = [System.Collections.Generic.List[object]]::new()
    foreach ($line in ($Section -split '\r?\n')) {
        if ($line -notmatch '^\s*\|.*\|\s*$') { continue }
        $cells = @($line.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim().Trim('`') })
        if ($cells.Count -gt 0 -and $cells[0] -notmatch '^[-: ]+$' -and $cells[0] -notmatch '^(?i:evidence_id|resource_type)$') { $rows.Add($cells) }
    }
    return $rows
}

$staticFiles = @(
    'AGENTS.md',
    'doc/00_INDEX.md',
    'doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md',
    'doc/STATUS.md',
    'doc/REBASELINE_PLAN.md',
    'doc/09_COLLABORATION.md',
    'doc/WORKSPACE_GOVERNANCE.md',
    'doc/tasks/README.md',
    'doc/templates/TASK.md',
    'doc/templates/REVIEW.md',
    'doc/templates/HANDOFF.md'
)

foreach ($relative in $staticFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $relative) -PathType Leaf)) { Add-Error "缺少当前治理入口：$relative" }
}

$statusPath = Join-Path $repoRoot 'doc/STATUS.md'
$statusText = Get-Content -LiteralPath $statusPath -Raw
$activeMatch = [regex]::Match($statusText, '(?m)^-\s*当前 Task：.*?\((?<path>tasks/[^)]+\.md)\)')
$activeTaskPath = $null
if ($activeMatch.Success) { $activeTaskPath = [IO.Path]::GetFullPath((Join-Path (Join-Path $repoRoot 'doc') $activeMatch.Groups['path'].Value)) }
if (-not $TaskPath) {
    if (-not $activeMatch.Success) { Add-Error 'STATUS 未提供可解析的当前 Task 指针。' }
    else { $TaskPath = $activeTaskPath }
} elseif (-not [IO.Path]::IsPathRooted($TaskPath)) {
    $TaskPath = Join-Path $repoRoot $TaskPath
}

$selectedFiles = [System.Collections.Generic.List[string]]::new()
foreach ($relative in $staticFiles) {
    $fullPath = Join-Path $repoRoot $relative
    if (Test-Path -LiteralPath $fullPath -PathType Leaf) { $selectedFiles.Add((Resolve-Path -LiteralPath $fullPath).Path) }
}
if ($TaskPath -and (Test-Path -LiteralPath $TaskPath -PathType Leaf)) {
    $TaskPath = (Resolve-Path -LiteralPath $TaskPath).Path
    if (-not $selectedFiles.Contains($TaskPath)) { $selectedFiles.Add($TaskPath) }
} else { Add-Error "当前 Task 文件不存在：$TaskPath" }

# Check only the declared current-document set and the selected Task; target files are existence-checked, not opened.
foreach ($file in $selectedFiles) {
    $text = Get-Content -LiteralPath $file -Raw
    foreach ($link in [regex]::Matches($text, '(?<!\!)\[[^\]]+\]\((?<target>[^)\s]+)(?:\s+[^)]*)?\)')) {
        $target = $link.Groups['target'].Value
        $resolved = Resolve-LocalPath $target (Split-Path -Parent $file)
        if ($resolved -and -not (Test-Path -LiteralPath $resolved)) { Add-Error "失效的本地引用：$([IO.Path]::GetRelativePath($repoRoot, $file)) → $target" }
    }
}

$architecture = 'Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy'
$adPath = Join-Path $repoRoot 'doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md'
$adText = Get-Content -LiteralPath $adPath -Raw
if ($adText -notlike "*$architecture*") { Add-Error 'AD-001 缺少冻结的唯一目标架构哨兵。' }
$truthPaths = @('AGENTS.md', 'doc/00_INDEX.md', 'doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md', 'doc/STATUS.md', 'doc/REBASELINE_PLAN.md')
$conflictPatterns = @(
    '(?i)(?:current|target|future)\s+architecture\s*(?:is|=)\s*(?:Windows\s*\+\s*)?Python\s*\+\s*PySide6',
    '(?:当前目标架构|唯一继续演进的产品架构)\s*(?:为|是|=|：|:)\s*(?:Windows\s*\+\s*)?Python\s*\+\s*PySide6',
    'PySide6\s*(?:\+|/)\s*QML\s*(?:为|是)\s*(?:当前|目标|未来)架构'
)
foreach ($relative in $truthPaths) {
    $file = Join-Path $repoRoot $relative
    $lineNumber = 0
    foreach ($line in (Get-Content -LiteralPath $file)) {
        $lineNumber++
        foreach ($pattern in $conflictPatterns) {
            if ($line -match $pattern) { Add-Error "目标架构冲突标记：${relative}:$lineNumber"; break }
        }
    }
}

foreach ($budget in @(
    @{ Path = 'doc/STATUS.md'; Bytes = 3200; Lines = 45 },
    @{ Path = 'doc/REBASELINE_PLAN.md'; Bytes = 2500; Lines = 35 }
)) {
    $file = Join-Path $repoRoot $budget.Path
    $bytes = (Get-Item -LiteralPath $file).Length
    $lineCount = (Get-Content -LiteralPath $file).Count
    if ($bytes -gt $budget.Bytes -or $lineCount -gt $budget.Lines) { Add-Error "$($budget.Path) 超过防膨胀预算：$bytes bytes / $lineCount lines" }
    elseif ($bytes -ge [math]::Floor($budget.Bytes * 0.8) -or $lineCount -ge [math]::Floor($budget.Lines * 0.8)) { Add-Warning "$($budget.Path) 已达到预算的 80%：$bytes bytes / $lineCount lines" }
}

if ($TaskPath -and (Test-Path -LiteralPath $TaskPath -PathType Leaf)) {
    $taskText = Get-Content -LiteralPath $TaskPath -Raw
    $metadata = Get-FrontMatter $taskText
    if (-not $metadata.ContainsKey('status')) { Add-Error 'Task front matter 缺少 status。' }
    else {
        $taskStatus = $metadata['status'].ToLowerInvariant()
        $validStatuses = @('proposed', 'ready', 'in_progress', 'blocked', 'in_review', 'changes_requested', 'approved', 'done', 'closed_with_limitations', 'cancelled', 'superseded', 'historical')
        if ($taskStatus -notin $validStatuses) { Add-Error "Task status 无效：$taskStatus" }
        $isStatusActiveTask = $activeTaskPath -and [IO.Path]::GetFullPath($TaskPath) -eq $activeTaskPath
        if ($isStatusActiveTask -and $taskStatus -in @('done', 'closed_with_limitations', 'cancelled', 'superseded', 'historical')) { Add-Error "STATUS 仍指向终态 Task：$taskStatus" }
        $taskId = $metadata['id']
        if ($taskId -and [IO.Path]::GetFileNameWithoutExtension($TaskPath) -ne $taskId) { Add-Error "Task 文件名与 front matter id 不一致：$taskId" }
        $readyIds = @()
        if ($taskId) {
            $planText = Get-Content -LiteralPath (Join-Path $repoRoot 'doc/REBASELINE_PLAN.md') -Raw
            $currentDag = ($planText -split '(?m)^##\s+历史快照', 2)[0]
            $readyMatch = [regex]::Match($currentDag, '(?m)^READY 节点：\s*(?<nodes>.+)$')
            if (-not $readyMatch.Success) { Add-Error 'REBASELINE_PLAN 当前 DAG 缺少 READY 节点声明。' }
            else {
                $readyList = ($readyMatch.Groups['nodes'].Value -split '[。;；]', 2)[0].Trim()
                if ($readyList -notmatch '^(?i:无|none)[.]?$') {
                    $readyIds = @([regex]::Matches($readyList, '[A-Za-z][A-Za-z0-9._-]+') | ForEach-Object { $_.Value })
                    foreach ($readyId in $readyIds) {
                        $readyTaskPath = Join-Path (Join-Path $repoRoot 'doc/tasks') "$readyId.md"
                        if (-not (Test-Path -LiteralPath $readyTaskPath -PathType Leaf)) { Add-Error "READY DAG 节点缺少 Task 文件：$readyId"; continue }
                        $readyTask = Get-FrontMatter (Get-Content -LiteralPath $readyTaskPath -Raw)
                        if ($readyTask['status'] -ne 'ready') { Add-Error "READY DAG 只允许 status: ready；$readyId 当前为 $($readyTask['status'])" }
                    }
                }
            }
            if ($taskStatus -in @('ready', 'in_progress', 'blocked', 'in_review', 'changes_requested', 'approved') -and $currentDag -notmatch [regex]::Escape($taskId)) { Add-Error "当前 DAG 未登记非终态 Task：$taskId" }
            if ($taskStatus -eq 'ready' -and $readyIds -notcontains $taskId) { Add-Error "READY Task 未出现在 Plan 的 READY 节点：$taskId" }
        }
        if (-not $metadata.ContainsKey('governance_version')) {
            Add-Warning '当前 Task 是 lifecycle v1；保留其原状态与证据，不强制回填旧 Task。'
        } elseif ($metadata['governance_version'] -eq '2') {
            if ($taskStatus -in @('in_review', 'approved', 'done', 'closed_with_limitations')) {
                $evidenceRows = @(Get-TableRows (Get-Section $taskText 'Canonical Evidence'))
                if ($evidenceRows.Count -eq 0) { Add-Error '进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence。' }
                foreach ($row in $evidenceRows) {
                    if ($row.Count -lt 6) { Add-Error 'Canonical Evidence 表格需要 6 列。'; continue }
                    $path = $row[2]
                    $commit = $row[3]
                    $sha = $row[4].ToLowerInvariant()
                    $class = $row[5].ToUpperInvariant()
                    $evidencePath = Resolve-LocalPath $path $repoRoot
                    if (-not $evidencePath -or -not (Test-Path -LiteralPath $evidencePath -PathType Leaf)) { Add-Error "Canonical evidence 路径缺失：$path"; continue }
                    if ($class -notin @('CANONICAL', 'SOURCE_PIN')) { Add-Error "Evidence class 无效：$class" }
                    if ($commit -match '^(?i:null|pending|todo|-)$') { $commit = '' }
                    if ($sha -match '^(?i:null|pending|todo|-)$') { $sha = '' }
                    if (-not $commit -and -not $sha) { Add-Error "Evidence 必须有 commit 或 SHA-256 pin：$path" }
                    if ($commit) {
                        if ($commit -notmatch '^[0-9a-fA-F]{7,40}$') { Add-Error "Evidence commit 格式无效：$path" }
                        else {
                            $repoRelative = [IO.Path]::GetRelativePath($repoRoot, $evidencePath).Replace('\', '/')
                            if ($repoRelative -eq '..' -or $repoRelative.StartsWith('../')) { Add-Error "仓外 evidence 不能用仓库 commit pin：$path" }
                            else {
                                & git -C $repoRoot cat-file -e "${commit}:$repoRelative" 2>$null
                                if ($LASTEXITCODE -ne 0) { Add-Error "Evidence commit 不含所 pin 文件：$commit`:$repoRelative" }
                            }
                        }
                    }
                    if ($sha) {
                        if ($sha -notmatch '^[0-9a-f]{64}$') { Add-Error "Evidence SHA-256 格式无效：$path" }
                        elseif ((Get-FileHash -LiteralPath $evidencePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $sha) { Add-Error "Evidence SHA-256 不匹配：$path" }
                    }
                }
                $evidenceDir = $metadata['evidence_dir']
                if ($evidenceDir -and $evidenceDir -notmatch '^(?i:null|pending|todo)$') {
                    $evidenceRoot = Resolve-LocalPath $evidenceDir $repoRoot
                    if ($evidenceRoot -and (Test-Path -LiteralPath $evidenceRoot -PathType Container)) {
                        $listed = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
                        foreach ($row in $evidenceRows) {
                            if ($row.Count -ge 3) {
                                $path = Resolve-LocalPath $row[2] $repoRoot
                                if ($path) { [void]$listed.Add($path) }
                            }
                        }
                        $extras = @(Get-ChildItem -LiteralPath $evidenceRoot -File -Recurse | Where-Object { -not $listed.Contains($_.FullName) })
                        if ($extras.Count -gt 0) {
                            $names = ($extras | Select-Object -First 8 -ExpandProperty FullName) -join ', '
                            if ($taskStatus -eq 'done') { Add-Error "DONE evidence_dir 含未登记文件：$names" }
                            else { Add-Warning "evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：$names" }
                        }
                    }
                }
            }
            $integrationCommit = $metadata['integration_commit']
            $hasIntegrationCommit = $integrationCommit -and $integrationCommit -notmatch '^(?i:null|pending|todo|-)$'
            $terminalStatus = $taskStatus -in @('done', 'closed_with_limitations', 'cancelled', 'superseded', 'historical')
            $closeoutRequired = $terminalStatus -or ($taskStatus -eq 'approved' -and $hasIntegrationCommit)
            if ($taskStatus -eq 'done' -and -not $hasIntegrationCommit) { Add-Error 'DONE 必须记录 integration_commit。' }
            if ($taskStatus -in @('done', 'closed_with_limitations') -and $metadata['canonical_evidence_status'] -ne 'complete') { Add-Error "$($taskStatus.ToUpperInvariant()) 必须设置 canonical_evidence_status: complete。" }
            if ($closeoutRequired) {
                if ($metadata['resource_closeout_status'] -ne 'complete') { Add-Error '终态或已集成的 approved Task 必须设置 resource_closeout_status: complete。' }
            }
            if ($closeoutRequired) {
                if (($taskStatus -eq 'done' -or ($taskStatus -eq 'approved' -and $hasIntegrationCommit)) -and $taskText -match '(?m)^\s*-\s*\[ \]') { Add-Error 'DONE 不能保留未完成 Acceptance Criteria；范围未完成时使用 closed_with_limitations。' }
                $resourceRows = @(Get-TableRows (Get-Section $taskText 'Resource Manifest'))
                if ($resourceRows.Count -eq 0) { Add-Error 'DONE 必须逐项填写 Resource Manifest；无资源时写 NOT_APPLICABLE。' }
                $allowedDisposition = @('DELETE_SAFE', 'MIGRATE', 'ARCHIVE', 'PRESERVE_REFERENCED', 'PRESERVE_USER_DATA', 'PRESERVE_UNKNOWN', 'NOT_APPLICABLE')
                foreach ($row in $resourceRows) {
                    if ($row.Count -lt 6) { Add-Error 'Resource Manifest 表格需要 6 列。'; continue }
                    $source = $row[1]
                    $disposition = $row[2].ToUpperInvariant()
                    $destination = $row[3]
                    $integrity = $row[4]
                    $result = $row[5]
                    if ($disposition -notin $allowedDisposition) { Add-Error "Resource disposition 无效：$disposition" }
                    if ([string]::IsNullOrWhiteSpace($result) -or $result -match '^(?i:待关闭|todo|pending|tbd)$') { Add-Error 'Resource Manifest 缺少引用/进程检查结果。' }
                    if ($disposition -eq 'DELETE_SAFE') {
                        $sourcePath = Resolve-LocalPath $source $repoRoot
                        if ($sourcePath -and (Test-Path -LiteralPath $sourcePath)) { Add-Error "DELETE_SAFE 来源仍存在：$source" }
                    }
                    if ($disposition -in @('MIGRATE', 'ARCHIVE', 'PRESERVE_REFERENCED', 'PRESERVE_USER_DATA', 'PRESERVE_UNKNOWN')) {
                        $finalPath = if ($destination -and $destination -notmatch '^(?i:none|n/?a|-)$') { Resolve-LocalPath $destination $repoRoot } else { $null }
                        if (-not $finalPath -or -not (Test-Path -LiteralPath $finalPath)) { Add-Error "Resource 最终路径未验证：$destination" }
                    }
                    if ($disposition -ne 'NOT_APPLICABLE') {
                        if ([string]::IsNullOrWhiteSpace($integrity) -or $integrity -match '^(?i:待关闭|todo|pending|tbd)$') { Add-Error "Resource 缺少 SHA-256/manifest 证据：$source" }
                        elseif ($integrity -notmatch '^[0-9a-fA-F]{64}$') {
                            $manifestPath = Resolve-LocalPath $integrity $repoRoot
                            if (-not $manifestPath -or -not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { Add-Error "Resource manifest 不存在：$integrity" }
                        } elseif ($disposition -in @('PRESERVE_REFERENCED', 'PRESERVE_USER_DATA', 'PRESERVE_UNKNOWN')) {
                            $finalPath = Resolve-LocalPath $destination $repoRoot
                            if ($finalPath -and (Test-Path -LiteralPath $finalPath -PathType Leaf) -and (Get-FileHash -LiteralPath $finalPath -Algorithm SHA256).Hash -ne $integrity) { Add-Error "Resource SHA-256 不匹配：$destination" }
                        }
                    }
                }
            }
        }
    }
}

Write-Output "Governance scope: $($selectedFiles.Count) current documents; no historical directory scan."
if ($TaskPath) { Write-Output "Task: $([IO.Path]::GetRelativePath($repoRoot, $TaskPath))" }
foreach ($warning in $warnings) { Write-Output "WARN: $warning" }
foreach ($errorItem in $errors) { Write-Output "FAIL: $errorItem" }
if ($errors.Count -gt 0) { Write-Output "Governance check: FAIL ($($errors.Count) errors, $($warnings.Count) warnings)"; exit 1 }
Write-Output "Governance check: PASS ($($warnings.Count) warnings)"
