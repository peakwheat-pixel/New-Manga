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

function Resolve-ManifestReference([string]$Section, [string]$RepoRoot) {
    # A Resource Manifest section may reference exactly one repository-relative JSON file.
    # Anything ambiguous or outside verification/** is refused rather than guessed at.
    $refs = [System.Collections.Generic.List[string]]::new()
    foreach ($m in [regex]::Matches($Section, '`([^`\s]+\.json)`')) { $refs.Add($m.Groups[1].Value.Trim()) }
    if ($refs.Count -eq 0) { return @{ Path = $null; Error = $null } }
    if ($refs.Count -gt 1) { return @{ Path = $null; Error = "Resource Manifest 引用了多个 JSON：$($refs -join ', ')" } }
    $ref = $refs[0]
    if ($ref -match '^(?i:[a-z]+:)' -or $ref.StartsWith('/') -or $ref.StartsWith('\')) {
        return @{ Path = $null; Error = "Resource Manifest 引用不得为绝对路径或 URL：$ref" }
    }
    if ($ref -match '[*?\[\]]') { return @{ Path = $null; Error = "Resource Manifest 引用不得含 glob：$ref" } }
    if ($ref -match '%[^%]+%' -or $ref -match '\$[A-Za-z_{(]') { return @{ Path = $null; Error = "Resource Manifest 引用不得含环境变量或宏：$ref" } }
    $full = Join-Path $RepoRoot ($ref -replace '/', [IO.Path]::DirectorySeparatorChar)
    $norm = $ref -replace '\\', '/'
    if ($norm -notmatch '^verification/') { return @{ Path = $null; Error = "Resource Manifest 引用必须位于 verification/**：$ref" } }
    if ($norm -match '\.\./') { return @{ Path = $null; Error = "Resource Manifest 引用不得越出仓库：$ref" } }
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { return @{ Path = $null; Error = "Resource Manifest 引用的文件不存在：$ref" } }
    $item = Get-Item -LiteralPath $full
    if ($item.LinkType) { return @{ Path = $null; Error = "Resource Manifest 引用不得为符号链接：$ref" } }
    return @{ Path = $full; Error = $null }
}

function Test-ExternalResourceManifest([string]$ManifestPath, [string]$TaskId, [string]$RepoRoot) {
    # Validates the referenced JSON against the fixed v1 schema, then applies the same
    # disposition rules the table path uses, plus the strict ALREADY_ABSENT semantics.
    $problems = [System.Collections.Generic.List[string]]::new()
    $notes = [System.Collections.Generic.List[string]]::new()
    try { $json = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch { return @{ Errors = @("Resource Manifest JSON 无法解析：$ManifestPath"); Resources = @() } }
    if ($json.schema_version -ne 1) { $problems.Add("Resource Manifest schema_version 必须为 1") }
    if ($json.task_id -ne $TaskId) { $problems.Add("Resource Manifest task_id '$($json.task_id)' 与 Task '$TaskId' 不一致") }
    if (-not $json.resources -or $json.resources.Count -eq 0) { $problems.Add("Resource Manifest resources 不得为空") }

    $allowed = @('DELETE_SAFE','MIGRATE','ARCHIVE','PRESERVE_REFERENCED','PRESERVE_USER_DATA','PRESERVE_UNKNOWN','NOT_APPLICABLE','ALREADY_ABSENT')
    $sameLocationSentinels = @(
        'Same ignored target/dist locations in this worktree',
        'Same source location',
        'Same shared build environment',
        'Same local cache location',
        'Same main-repository paths'
    )
    $counts = @{ deleted = 0; moved = 0; migrated = 0; archived = 0 }
    $resources = @()
    foreach ($res in $json.resources) {
        $disposition = ([string]$res.disposition).ToUpperInvariant()
        if ($disposition -notin $allowed) { $problems.Add("Resource disposition 无效：$disposition"); continue }
        if ([string]::IsNullOrWhiteSpace([string]$res.process_check)) { $problems.Add("Resource Manifest 缺少引用/进程检查结果：$($res.source_path)") }
        if ($res.deleted) { $counts.deleted++ }
        if ($res.moved) { $counts.moved++ }
        if ($res.modified -eq $null) { }

        $rawDest = if ($res.destination_path -ne $null) { [string]$res.destination_path } else { '' }
        $trimmedDest = $rawDest.Trim()
        $isSentinel = $sameLocationSentinels -contains $trimmedDest
        $isBlank = [string]::IsNullOrWhiteSpace($rawDest)
        $isDash = ($trimmedDest -eq '-')
        $isSameLocation = $isSentinel -or $isBlank -or $isDash

        if ($isSameLocation) {
            $destDesc = if ($isBlank) { '(blank)' } elseif ($isDash) { '-' } else { $rawDest }
            $resId = if (-not [string]::IsNullOrWhiteSpace([string]$res.resource_type)) {
                [string]$res.resource_type
            } elseif (-not [string]::IsNullOrWhiteSpace([string]$res.source_path)) {
                [string]$res.source_path
            } else {
                'resource'
            }
            $notes.Add("Resource '$resId' destination '$destDesc' 解释为同源，使用 source_path '$([string]$res.source_path)'")
        }

        if ($disposition -eq 'ALREADY_ABSENT') {
            if ([string]::IsNullOrWhiteSpace([string]$res.absent_evidence)) { $problems.Add("ALREADY_ABSENT 缺少 absent_evidence：$($res.source_path)") }
            $exprs = if ($isSameLocation) { @([string]$res.source_path) } else { @([string]$res.source_path, [string]$res.destination_path) }
            foreach ($expr in $exprs) {
                if ([string]::IsNullOrWhiteSpace($expr)) { continue }
                if ($expr -match '[{}*?\[\]]' -or $expr -match '%[^%]+%') { continue }
                # Resolve-LocalPath handles rooted paths; a bare Join-Path would glue an
                # absolute expression onto the repo root (G:\...\C:\Windows\...), making every
                # existing absolute target look absent and letting a fake disappearance pass.
                $cand = Resolve-LocalPath $expr $RepoRoot
                if ($cand -and (Test-Path -LiteralPath $cand)) { $problems.Add("ALREADY_ABSENT 但目标仍存在：$expr") }
            }
        } elseif ($disposition -eq 'NOT_APPLICABLE' -and ([string]$res.absent_evidence)) {
            $problems.Add("NOT_APPLICABLE 不得用于已消失资源：$($res.source_path)")
        }
        $resources += [pscustomobject]@{
            Disposition = $disposition
            Source = [string]$res.source_path
            Destination = [string]$res.destination_path
            Sha256 = [string]$res.sha256
            ManifestPath = [string]$res.manifest_path
            IsSameLocation = $isSameLocation
            IsSentinel = $isSentinel
        }
    }
    if ($json.closeout_counts) {
        foreach ($k in @('deleted','moved','migrated','archived')) {
            $declared = 0
            try { $declared = [int]$json.closeout_counts.$k } catch { $problems.Add("closeout_counts.$k 必须为整数") }
            if ($declared -lt 0) { $problems.Add("closeout_counts.$k 不得为负") }
        }
        # Declared counts are a record of closeout actions, which may cover files that are not
        # themselves listed in resources. P19-UI-FIX-1 declares moved=6 for six logs renamed
        # inside its evidence dir while all seven listed resources carry moved=false - accurate,
        # not inconsistent. Differences are surfaced as notes, never as failures.
        foreach ($k in @('deleted','moved','migrated','archived')) {
            $declared = 0
            try { $declared = [int]$json.closeout_counts.$k } catch { }
            if ($declared -ne $counts[$k]) { $notes.Add("closeout_counts.$k=$declared 与 resources 中布尔为 true 的项数 $($counts[$k]) 不同（声明口径包含未列入 resources 的处置动作）") }
        }
    } else { $problems.Add("Resource Manifest 缺少 closeout_counts") }
    return @{ Errors = $problems; Notes = $notes; Resources = $resources }
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
    'doc/TASK_LEDGER.md',
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

# r38 §5-3: the ledger must not go stale. doc/TASK_LEDGER.md is generated by
# tools/governance/task_ledger.py, so a task-status change without a rerun leaves
# a file that still claims yesterday's totals. Comparing the reported metrics
# against a fresh scan is cheap and catches exactly that.
$ledgerPath = Join-Path $repoRoot 'doc/TASK_LEDGER.md'
if (Test-Path -LiteralPath $ledgerPath -PathType Leaf) {
    $ledgerText = Get-Content -LiteralPath $ledgerPath -Raw
    $fresh = @{}
    $terminalSet = @('done', 'closed_with_limitations', 'cancelled', 'superseded', 'historical')
    $taskFiles = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'doc/tasks') -Filter '*.md' -File |
        Where-Object { $_.BaseName -ne 'README' })
    $nonTerminal = 0
    foreach ($f in $taskFiles) {
        $head = Get-Content -LiteralPath $f.FullName -TotalCount 40
        $st = $null
        foreach ($line in $head) {
            if ($line -match '^status:\s*(.+?)\s*$') { $st = $Matches[1].Trim('"', "'").ToLowerInvariant(); break }
        }
        if ($st -and $st -notin $terminalSet) { $nonTerminal++ }
    }
    $fresh['task files'] = $taskFiles.Count
    $fresh['non-terminal'] = $nonTerminal
    if ($ledgerText -match '\|\s*task files\s*\|\s*(\d+)\s*\|') {
        $declared = [int]$Matches[1]
        if ($declared -ne $fresh['task files']) {
            Add-Error "TASK_LEDGER 已过期：声明 $declared 个 Task，实际 $($fresh['task files']) 个（重跑 tools/governance/task_ledger.py --write）"
        }
    } else { Add-Error 'TASK_LEDGER 缺少 task files 指标。' }
    if ($ledgerText -match '\|\s*non-terminal\s*\|\s*(\d+)\s*\|') {
        $declared = [int]$Matches[1]
        if ($declared -ne $fresh['non-terminal']) {
            Add-Error "TASK_LEDGER 已过期：声明 $declared 个非终态 Task，实际 $($fresh['non-terminal']) 个（重跑 tools/governance/task_ledger.py --write）"
        }
    } else { Add-Error 'TASK_LEDGER 缺少 non-terminal 指标。' }
    if ($fresh['non-terminal'] -gt 0) {
        Add-Warning "存在 $($fresh['non-terminal']) 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）"
    }
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
    @{ Path = 'doc/REBASELINE_PLAN.md'; Bytes = 7000; Lines = 64 }
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
        } elseif ($metadata['governance_version'] -in @('2', '3')) {
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
                        if ($sha) {
                            if ($sha -notmatch '^[0-9a-f]{64}$') { Add-Error "Evidence SHA-256 格式无效：$path" }
                            else {
                                # r194: a pin may be against worktree bytes (CRLF under
                                # core.autocrlf=true) or against the committed blob (LF).
                                # Both are legitimate readings of "the same file" and which
                                # one a task recorded depends on when it was authored, so
                                # accept either. The blob branch is only computed when the
                                # commit really contains the path; otherwise it would compare
                                # against nothing and pass silently.
                                $worktreeSha = (Get-FileHash -LiteralPath $evidencePath -Algorithm SHA256).Hash.ToLowerInvariant()
                                $matches = ($worktreeSha -eq $sha)
                                if (-not $matches -and $commit) {
                                    $repoRel = [IO.Path]::GetRelativePath($repoRoot, $evidencePath).Replace('\', '/')
                                    if ($repoRel -ne '..' -and -not $repoRel.StartsWith('../')) {
                                        $blobHex = & git -C $repoRoot rev-parse "${commit}:$repoRel" 2>$null
                                        if ($LASTEXITCODE -eq 0 -and $blobHex) {
                                            $tmp = [IO.Path]::GetTempFileName()
                                            try {
                                                & git -C $repoRoot cat-file blob $blobHex > $tmp 2>$null
                                                $blobSha = (Get-FileHash -LiteralPath $tmp -Algorithm SHA256).Hash.ToLowerInvariant()
                                                if ($blobSha -eq $sha) { $matches = $true }
                                            } finally { Remove-Item -LiteralPath $tmp -ErrorAction SilentlyContinue }
                                        }
                                    }
                                }
                                if (-not $matches) { Add-Error "Evidence SHA-256 不匹配：$path" }
                            }
                        }
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
                $manifestSection = Get-Section $taskText 'Resource Manifest'
                $resourceRows = @(Get-TableRows $manifestSection)
                $externalManifestUsed = $false
                if ($resourceRows.Count -eq 0) {
                    $ref = Resolve-ManifestReference $manifestSection $repoRoot
                    if ($ref.Error) { Add-Error $ref.Error }
                    elseif ($ref.Path) {
                        $externalManifestUsed = $true
                        $checked = Test-ExternalResourceManifest $ref.Path $taskId $repoRoot
                        foreach ($p in $checked.Errors) { Add-Error $p }
                        if ($checked.Notes) { foreach ($n in $checked.Notes) { Add-Warning "$($taskId): $n" } }
                        foreach ($r in $checked.Resources) {
                            if ($r.Disposition -in @('MIGRATE','ARCHIVE','PRESERVE_REFERENCED','PRESERVE_USER_DATA','PRESERVE_UNKNOWN')) {
                                if ($r.IsSameLocation) {
                                    $target = $r.Source
                                    if ([string]::IsNullOrWhiteSpace($target) -or $target.Trim() -eq '-') { continue }
                                    if ($target -match '[{}*?\[\]]' -or $target -match '%[^%]+%') { continue }
                                    $finalPath = try { Resolve-LocalPath $target $repoRoot } catch { $null }
                                    if ($finalPath -and (Test-Path -LiteralPath $finalPath)) { continue }
                                    if ($r.IsSentinel) {
                                        # AC1: 五个已核实 sentinel 是同源位置说明，若 source 未在本地存在（例如已清理的构建缓存），明确跳过 destination 存在性校验
                                        continue
                                    }
                                    Add-Error "Resource 最终路径未验证：$target"
                                    continue
                                }
                                if ([string]::IsNullOrWhiteSpace($r.Destination) -or $r.Destination -match '^(?i:none|n/?a|-)$') { continue }
                                if ($r.Destination -match '[{}*?\[\]]' -or $r.Destination -match '%[^%]+%') { continue }
                                $finalPath = try { Resolve-LocalPath $r.Destination $repoRoot } catch { $null }
                                if (-not $finalPath -or -not (Test-Path -LiteralPath $finalPath)) { Add-Error "Resource 最终路径未验证：$($r.Destination)" }
                            }
                        }
                    } else { Add-Error 'DONE 必须逐项填写 Resource Manifest；无资源时写 NOT_APPLICABLE。' }
                }
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
            if ($metadata['governance_version'] -eq '3' -and $taskStatus -in @('in_review', 'approved', 'done', 'closed_with_limitations')) {
                # §4.3 AC 状态标记门禁：每个 AC 必须有合法 <<STATUS>>，且与勾选一致。
                $acMatches = @([regex]::Matches($taskText, '(?m)^[ \t]*-[ \t]*\[([ xX])\][ \t]*\*\*AC[^\r\n]*\r?$'))
                if ($acMatches.Count -eq 0) {
                    Add-Error 'lifecycle v3 Task 进入 REVIEW/DONE 时未找到任何 AC 行。'
                }
                foreach ($am in $acMatches) {
                    # r188: the AC match may end with \r on a CRLF file (the pattern above
                    # tolerates it so AC lines are visible either way). Downstream marker matching
                    # anchors on $, so strip the \r once here instead of making every later
                    # pattern CRLF-aware.
                    $acLine = $am.Value.TrimEnd([char]13)
                    $isChecked = ($am.Groups[1].Value -ne ' ')
                    $acLabel = if ($acLine -match '\*\*(AC[0-9A-Za-z._-]+)') { $matches[1] } else { 'AC?' }
                    $mk = [regex]::Match($acLine, '<<(MET|PARTIAL|BLOCKED|NOT_APPLICABLE)(?::[ \t]*([^>]*))?>>[ \t]*$')
                    if (-not $mk.Success) {
                        Add-Error "AC 状态标记缺失或非法（需行末 <<MET>> / <<PARTIAL: 原因>> / <<BLOCKED: 原因>> / <<NOT_APPLICABLE: 原因>>）：$acLabel"
                        continue
                    }
                    $acState = $mk.Groups[1].Value
                    $acReason = $mk.Groups[2].Value.Trim()
                    $acText = ($acLine -replace '\s+', ' ')
                    if ($acText.Length -gt 220) { $acText = $acText.Substring(0, 220) + '…' }
                    switch ($acState) {
                        'MET' {
                            if (-not $isChecked) { Add-Error "AC 标记为 MET 但未勾选：$acLabel" }
                            if ($acReason) { Add-Error "AC 标记为 MET 时不得附原因（依据应进 Canonical Evidence）：$acLabel" }
                        }
                        'NOT_APPLICABLE' {
                            if (-not $isChecked) { Add-Error "AC 标记为 NOT_APPLICABLE 时必须勾选：$acLabel" }
                            if (-not $acReason) { Add-Error "AC 标记为 NOT_APPLICABLE 时必须有原因：$acLabel" }
                        }
                        default {
                            if ($taskStatus -eq 'done') { Add-Error "DONE Task 不得包含未达成状态（$acState）的 AC：$acLabel；范围未达成时请使用 closed_with_limitations。" }
                            if ($isChecked) { Add-Error "AC 标记为 $acState 时不得勾选：$acLabel" }
                            if (-not $acReason) { Add-Error "AC 标记为 $acState 时必须有原因：$acLabel" }
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
