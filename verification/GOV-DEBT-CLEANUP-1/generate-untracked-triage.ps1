[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$EvidenceDir = $PSScriptRoot
)

$ErrorActionPreference = 'Stop'
$evidencePrefix = 'verification/GOV-DEBT-CLEANUP-1/'
$paths = @(& git -C $RepoRoot ls-files --others --exclude-standard -- verification/ | Where-Object { $_ -and $_ -notlike "$evidencePrefix*" } | Sort-Object)
$pathLookup = @{}
foreach ($path in $paths) { $pathLookup[$path.ToLowerInvariant()] = $path }

$activeIds = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$planPath = Join-Path $RepoRoot 'doc/REBASELINE_PLAN.md'
$planText = Get-Content -LiteralPath $planPath -Raw
$readyLine = [regex]::Match($planText, '(?m)^READY 节点：\s*(?<items>.+)$')
if ($readyLine.Success) {
    $readyItems = ($readyLine.Groups['items'].Value -split '[。;；]', 2)[0]
    foreach ($m in [regex]::Matches($readyItems, '[A-Za-z][A-Za-z0-9._-]+')) { [void]$activeIds.Add($m.Value) }
}

$statusPath = Join-Path $RepoRoot 'doc/STATUS.md'
$statusLines = @(Get-Content -LiteralPath $statusPath)
foreach ($line in $statusLines) {
    if ($line -match '^-\s*当前 Task：.*?\(tasks/([A-Za-z0-9._-]+\.md)\)') { [void]$activeIds.Add([IO.Path]::GetFileNameWithoutExtension($Matches[1])) }
    if ($line -match '^-\s*\*\*在飞\*\*：.*?\(tasks/([A-Za-z0-9._-]+\.md)\)') { [void]$activeIds.Add([IO.Path]::GetFileNameWithoutExtension($Matches[1])) }
    if ($line -match '^\|\s*([A-Za-z0-9._-]+)\s*\|.*\|\s*(ready|in_progress|blocked|in_review|changes_requested|approved)\s*\|') { [void]$activeIds.Add($Matches[1]) }
}

$taskFiles = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'doc/tasks') -Filter '*.md' -File | Sort-Object FullName)
$sources = [System.Collections.Generic.List[object]]::new()
foreach ($taskFile in $taskFiles) {
    $taskId = [IO.Path]::GetFileNameWithoutExtension($taskFile.Name)
    $textLines = @(Get-Content -LiteralPath $taskFile.FullName)
    $inCanonical = $false
    $lineNo = 0
    $hasCanonical = $false
    foreach ($line in $textLines) {
        $lineNo++
        if ($line -match '^##\s+Canonical Evidence\s*$') { $inCanonical = $true; continue }
        if ($line -match '^##\s+' -and $inCanonical) { $inCanonical = $false }
        if ($inCanonical) { $hasCanonical = $true }
        if ($activeIds.Contains($taskId) -and $line -match '^evidence_dir:\s*(?<dir>[^\s]+)') {
            $normalizedDir = $Matches['dir'].TrimEnd('/')
            foreach ($target in $paths) {
                if ($target.StartsWith($normalizedDir + '/', [StringComparison]::OrdinalIgnoreCase)) {
                    if (-not $pathLookup.ContainsKey($target.ToLowerInvariant() + '|dir')) { $pathLookup[$target.ToLowerInvariant() + '|dir'] = [System.Collections.Generic.List[string]]::new() }
                    $pathLookup[$target.ToLowerInvariant() + '|dir'].Add("$($taskFile.FullName.Substring($RepoRoot.Length + 1).Replace('\\','/')):$lineNo (evidence_dir scope)")
                }
            }
        }
    }
    if ($hasCanonical -or $activeIds.Contains($taskId)) {
        $sources.Add([pscustomobject]@{ Path = $taskFile.FullName; Relative = [IO.Path]::GetRelativePath($RepoRoot, $taskFile.FullName).Replace('\', '/'); Kind = 'Task'; TaskId = $taskId })
    }
}

$mechanismRelative = @(
    'AGENTS.md', 'doc/00_INDEX.md', 'doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md',
    'doc/STATUS.md', 'doc/REBASELINE_PLAN.md', 'doc/09_COLLABORATION.md',
    'doc/WORKSPACE_GOVERNANCE.md', 'doc/templates/TASK.md',
    'doc/templates/REVIEW.md', 'doc/templates/HANDOFF.md'
)
foreach ($relative in $mechanismRelative) {
    $full = Join-Path $RepoRoot $relative
    if (Test-Path -LiteralPath $full -PathType Leaf) { $sources.Add([pscustomobject]@{ Path = $full; Relative = $relative; Line = 0; Text = ''; Kind = '机制文档' }) }
}
$toolFiles = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'tools') -File -Recurse | Where-Object { $_.Extension -in @('.ps1', '.psm1', '.py', '.cmd', '.bat', '.sh', '.js', '.ts', '.json', '.yaml', '.yml', '.toml') } | Sort-Object FullName)
foreach ($file in $toolFiles) { $sources.Add([pscustomobject]@{ Path = $file.FullName; Relative = [IO.Path]::GetRelativePath($RepoRoot, $file.FullName).Replace('\', '/'); Line = 0; Text = ''; Kind = '机制脚本' }) }

$referenceMap = @{}
$pathRegex = [regex]::new('(?i)(?:\.\.[/\\])*verification[/\\][^\s`''"<>\]\[|,;]+')
foreach ($source in $sources) {
    $lineNo = 0
    $inCanonical = $false
    foreach ($line in (Get-Content -LiteralPath $source.Path)) {
        $lineNo++
        $eligible = $true
        $kind = $source.Kind
        if ($source.Kind -eq 'Task') {
            if ($line -match '^##\s+Canonical Evidence\s*$') { $inCanonical = $true; continue }
            if ($line -match '^##\s+' -and $inCanonical) { $inCanonical = $false }
            $eligible = $inCanonical -or $activeIds.Contains($source.TaskId)
            if ($inCanonical) { $kind = 'Canonical Evidence pin' } else { $kind = 'READY/在飞 Task' }
        }
        if (-not $eligible) { continue }
        $normalizedLine = $line.Replace('\', '/')
        foreach ($match in $pathRegex.Matches($normalizedLine)) {
            $value = $match.Value
            $index = $value.IndexOf('verification/', [StringComparison]::OrdinalIgnoreCase)
            if ($index -lt 0) { continue }
            $candidate = $value.Substring($index).TrimEnd('.', ':', ';', ',', ')', '}', ']')
            if ($candidate.EndsWith('/**')) { continue }
            $key = $candidate.ToLowerInvariant()
            if (-not $pathLookup.ContainsKey($key)) { continue }
            if (-not $referenceMap.ContainsKey($key)) { $referenceMap[$key] = [System.Collections.Generic.List[string]]::new() }
            $referenceMap[$key].Add("$($source.Relative):$lineNo ($kind)")
        }
    }
}

$rows = [System.Collections.Generic.List[object]]::new()
foreach ($relative in $paths) {
    $item = Get-Item -LiteralPath (Join-Path $RepoRoot $relative)
    $key = $relative.ToLowerInvariant()
    $refs = [System.Collections.Generic.List[string]]::new()
    if ($referenceMap.ContainsKey($key)) { foreach ($ref in $referenceMap[$key]) { if (-not $refs.Contains($ref)) { $refs.Add($ref) } } }
    $dirKey = $key + '|dir'
    if ($pathLookup.ContainsKey($dirKey)) { foreach ($ref in $pathLookup[$dirKey]) { if (-not $refs.Contains($ref)) { $refs.Add($ref) } } }

    if ($refs.Count -gt 0) {
        $class = '保留'
        $reason = '被当前 READY/在飞 Task、Canonical Evidence pin 或机制文档/脚本明确引用；引用来源已逐条列出。'
    } else {
        $class = '建议入库'
        switch ($item.Extension.ToLowerInvariant()) {
            '.md' { $reason = '任务、Review、提示、检查点或调查记录，保存决策脉络与恢复上下文。' }
            '.log' { $reason = '原始运行日志；可独立复核命令结果、错误和运行顺序。' }
            '.exit' { $reason = '逐次运行退出码 sidecar；保留可审计的进程结果。' }
            '.json' { $reason = '结构化原始运行/Review/manifest 记录，保留机器可读状态与输入输出。' }
            '.jsonl' { $reason = '逐事件原始记录，保留顺序和会话/运行 trace。' }
            '.txt' { $reason = '命令、结果或辅助原始文本，保留独立复核材料。' }
            '.png' { $reason = '截图或图像证据，保留视觉状态快照。' }
            '.svg' { $reason = '矢量证据或图示，保留可复核视觉/结构内容。' }
            '.bin' { $reason = '原始二进制产物；没有已核实的无损再生产命令。' }
            '.patch' { $reason = '原始差异补丁，保留变更内容及来源。' }
            '.ps1' { $reason = '可执行验证脚本，保留复现程序与参数实现。' }
            '.csv' { $reason = '结构化数据清单，保留筛选结果与统计输入。' }
            default { $reason = '独立证据材料；尚未找到能证明其无损再生产的确切命令。' }
        }
    }
    $rows.Add([pscustomobject]@{ Path = $relative; Bytes = [long]$item.Length; Group = ($relative -split '/')[1]; Class = $class; References = (@($refs) -join '<br>'); Reason = $reason })
}

$rows | Select-Object Path, Bytes, Group, Class, References, Reason | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation | Set-Content -LiteralPath (Join-Path $EvidenceDir 'untracked-file-inventory.tsv') -Encoding utf8
$paths | Set-Content -LiteralPath (Join-Path $EvidenceDir 'untracked-verification-paths.txt') -Encoding utf8

$counts = @($rows | Group-Object Group | Sort-Object Name)
$classCounts = @($rows | Group-Object Class | Sort-Object Name)
$eligibleCleanup = @($rows | Where-Object Class -eq '建议清理（待用户授权）')
$cleanupBytes = [long](($eligibleCleanup | Measure-Object Bytes -Sum).Sum)
$report = [System.Collections.Generic.List[string]]::new()
$report.Add('# AC1：verification 未跟踪证据逐项分类')
$report.Add('')
$report.Add('生成依据：`git ls-files --others --exclude-standard -- verification/`；生成时排除本 Task 自身的 `verification/GOV-DEBT-CLEANUP-1/`，避免清单递归自包含。仅以当前 READY/在飞 Task、Task 的 Canonical Evidence 表、治理机制文档/脚本中的精确路径命中或当前 Task `evidence_dir` 作为“保留”引用证据。未命中的文件按文件类型说明独立证据价值。')
$report.Add('')
$report.Add("基线文件数：$($rows.Count)；总字节：$([long](($rows | Measure-Object Bytes -Sum).Sum))。文件集合相对于生成时刻的 Git 未跟踪清单；本目录生成物不属于该集合。")
$report.Add('')
$report.Add('## 分组计数')
$report.Add('')
$report.Add('| verification 子目录 | 文件数 | 字节 |')
$report.Add('|---|---:|---:|')
foreach ($group in $counts) { $sum = [long](($group.Group | Measure-Object Bytes -Sum).Sum); $report.Add("| ``$($group.Name)`` | $($group.Count) | $sum |") }
$report.Add('')
$report.Add('## 分类计数')
$report.Add('')
$report.Add('| 判定 | 文件数 | 字节 |')
$report.Add('|---|---:|---:|')
foreach ($group in $classCounts) { $sum = [long](($group.Group | Measure-Object Bytes -Sum).Sum); $report.Add("| $($group.Name) | $($group.Count) | $sum |") }
$report.Add('')
$report.Add("建议清理（待用户授权）：$($eligibleCleanup.Count) 个，$cleanupBytes 字节。未确认同时满足无引用且有精确再生产命令或纯临时特征的文件，因此本轮不建议清理任何证据。")
$report.Add('')
$report.Add('## 逐文件清单')
$report.Add('')
$report.Add('| 文件 | 字节 | 判定 | 引用来源（文件:行） | 理由 |')
$report.Add('|---|---:|---|---|---|')
foreach ($row in $rows) {
    $safePath = $row.Path.Replace('|', '\|')
    $refs = if ($row.References) { $row.References } else { '无命中' }
    $report.Add("| ``$safePath`` | $($row.Bytes) | $($row.Class) | $refs | $($row.Reason) |")
}
$reportPath = Join-Path $EvidenceDir 'untracked-evidence-triage.md'
Set-Content -LiteralPath $reportPath -Value $report -Encoding utf8

Write-Output "UNTRACKED_FILES=$($rows.Count)"
Write-Output "UNTRACKED_BYTES=$([long](($rows | Measure-Object Bytes -Sum).Sum))"
Write-Output "CLEANUP_CANDIDATES=$($eligibleCleanup.Count)"
Write-Output "CLEANUP_BYTES=$cleanupBytes"
Write-Output "REPORT=$reportPath"
Write-Output 'CLASS_COUNTS:'
$classCounts | ForEach-Object { Write-Output "$($_.Name)=$($_.Count)" }
