[CmdletBinding()]
param(
    [string]$EvidenceDir = $PSScriptRoot,
    [string]$ReportPath = (Join-Path $PSScriptRoot 'failed-task-rootcause.md')
)

$ErrorActionPreference = 'Stop'
$rawPath = Join-Path $EvidenceDir 'failed-task-checks-raw.txt'
$lines = @(Get-Content -LiteralPath $rawPath)
$pinAuditPath = Join-Path $EvidenceDir 'historical-sha-pin-audit.tsv'
$pinAudit = if (Test-Path -LiteralPath $pinAuditPath) { @(Import-Csv -LiteralPath $pinAuditPath -Delimiter "`t") } else { @() }
$records = [System.Collections.Generic.List[object]]::new()
$current = $null
foreach ($line in $lines) {
    if ($line -match '^COMMAND\[\d+\]: .* -TaskPath (?<task>\S+)') {
        if ($current) { $records.Add($current) }
        $current = [pscustomobject]@{ Task = $Matches['task']; ExitCode = $null; Errors = [System.Collections.Generic.List[string]]::new() }
        continue
    }
    if (-not $current) { continue }
    if ($line -match '^EXIT_CODE\[\d+\]: (?<code>\d+)') { $current.ExitCode = [int]$Matches['code']; continue }
    if ($line -match '^FAIL:') { $current.Errors.Add($line) }
}
if ($current) { $records.Add($current) }
$failed = @($records | Where-Object ExitCode -ne 0)

$report = [System.Collections.Generic.List[string]]::new()
$report.Add('# AC2：失败 Task 根因清单')
$report.Add('')
$report.Add('复现命令模板：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/<X>.md`。原始输出保存在 `failed-task-checks-raw.txt`，每个 Task 均有命令和退出码。生成脚本扫描当前 `doc/tasks/P*.md`，本次共检查 78 个文件。')
$report.Add('')
$report.Add("Task 背景记载历史失败数为 41；本次工作区当前实测为 $($failed.Count) 个失败（共 $($records.Count) 个 P* Task）。当前目录中有 $(@($failed | Where-Object { -not (git ls-files --error-unmatch $_.Task 2>$null) }).Count) 个失败 Task 文件尚未跟踪。两次计数存在差异，本清单按本次复现结果逐项记录，不臆测历史清单的差额。")
$report.Add('')
$laterChangeCount = @($pinAudit | Where-Object Classification -like 'Source file changed in later committed history; historical pin matches cited commit bytes*').Count
$crlfCount = @($pinAudit | Where-Object Classification -like 'Working-tree CRLF conversion*').Count
$inconsistentPinCount = @($pinAudit | Where-Object Classification -like 'Stored SHA does not match cited commit bytes*').Count
$uniqueShaPaths = @($pinAudit.Path | Sort-Object -Unique).Count
$report.Add("SHA pin 复核：$($pinAudit.Count) 条 SHA 错误涉及 $uniqueShaPaths 个唯一路径。`historical-sha-pin-audit.tsv` 对照了 pin commit 的 LF/CRLF 字节、当前磁盘 SHA、Git blob、后续提交和工作树状态；结果为 $laterChangeCount 条后续已提交源文件变更、$crlfCount 条仅为 Windows CRLF checkout 与 LF pin 的字节口径差异、$inconsistentPinCount 条 pin/commit 原始字节绑定不一致。后两类不能归因成后续合法源码变更。历史 pin 均未修改.")
$report.Add('')
$report.Add('失败类型总览（按 checker 原文聚合）：')
$report.Add('')
$allErrors = @($failed | ForEach-Object { $_.Errors })
$typeCounts = @{}
foreach ($errorLine in $allErrors) {
    $message = $errorLine -replace '^FAIL:\s*', ''
    $type = if ($message -match '^([^：:]+)[：:]') { $Matches[1] } else { $message }
    if (-not $typeCounts.ContainsKey($type)) { $typeCounts[$type] = 0 }
    $typeCounts[$type]++
}
$report.Add('| 失败类型 | 次数 |')
$report.Add('|---|---:|')
foreach ($type in ($typeCounts.Keys | Sort-Object)) { $report.Add("| $type | $($typeCounts[$type]) |") }
$report.Add('')
$report.Add('## 逐 Task 清单')
$report.Add('')
$report.Add('| Task | 失败类型 | 涉及文件/记录 | 根因分类 | 不破坏可追溯性的处置建议 |')
$report.Add('|---|---|---|---|---|')

foreach ($record in $failed) {
    $errorText = @($record.Errors)
    $types = [System.Collections.Generic.List[string]]::new()
    $roots = [System.Collections.Generic.List[string]]::new()
    $paths = [System.Collections.Generic.List[string]]::new()
    foreach ($errorLine in $errorText) {
        $message = $errorLine -replace '^FAIL:\s*', ''
        if ($message -match '^([^：:]+)[：:]') { $type = $Matches[1] } else { $type = $message }
        if (-not $types.Contains($type)) { $types.Add($type) }
        if ($message -match '^Evidence SHA-256 不匹配：(?<shaPath>.+)$') {
            $audit = @($pinAudit | Where-Object { $_.Task -eq $record.Task -and $_.Path -eq $Matches['shaPath'] })
            if ($audit.Count -eq 0) { $root = 'SHA-256 不匹配；源文件后续合法变更未证实' }
            elseif (@($audit | Where-Object Classification -like 'Source file changed in later committed history; historical pin matches cited commit bytes*').Count -gt 0) { $root = '源文件后续合法变更（pin commit 原字节匹配，后续提交已改变源码）' }
            elseif (@($audit | Where-Object Classification -like 'Source changed in later committed history; current working tree also differs*').Count -gt 0) { $root = '源文件后续提交变更；当前工作树另有未提交漂移' }
            elseif (@($audit | Where-Object Classification -like 'Working-tree CRLF conversion*').Count -gt 0) { $root = '路径/工作区字节口径：CRLF checkout 与 LF pin 不同，Git 源 blob 未变' }
            elseif (@($audit | Where-Object Classification -like 'Raw-byte SHA differs while committed source blob is unchanged*').Count -gt 0) { $root = '路径/工作区字节口径：换行或编码变化，Git 源 blob 未变' }
            elseif (@($audit | Where-Object Classification -like 'Stored SHA does not match cited commit bytes*').Count -gt 0) { $root = '历史 pin 与所列 commit 原始字节不一致；原 pin/commit 绑定需调查' }
            else { $root = '源文件当前修改或后续变更未能证明为已提交合法变化' }
        }
        elseif ($message -match 'Resource SHA-256 不匹配') { $root = '资源 Manifest SHA 与当前字节不一致；历史 pin 保留并需核实资源变化时间' }
        elseif ($message -match '当前 DAG 未登记|READY Task 未出现在 Plan') { $root = 'DAG 未登记/READY 指针不一致' }
        elseif ($message -match '失效的本地引用|Evidence commit 不含所 pin 文件') { $root = '路径写法或 Canonical Evidence 的 commit/path 绑定错误' }
        elseif ($message -match 'Resource manifest 不存在|DONE 必须逐项填写 Resource Manifest|DONE evidence_dir 含未登记文件|Resource 最终路径未验证') { $root = '缺 Manifest / 资源或证据清单未闭合' }
        elseif ($message -match 'Canonical evidence 路径缺失') { $root = 'Canonical Evidence 指向的文件缺失或路径错配' }
        else { $root = '其他：证据文件缺失、Evidence class 无效或 DONE AC 状态未闭合' }
        if (-not $roots.Contains($root)) { $roots.Add($root) }
        foreach ($match in [regex]::Matches($message, '(?:verification|doc|src|apps|tests|tools)/[^\s:，,；;|`]+')) {
            $path = $match.Value.TrimEnd('.', ')', ']', '}', ',')
            if (-not $paths.Contains($path)) { $paths.Add($path) }
        }
    }
    if ($paths.Count -eq 0) { $paths.Add($record.Task) }
    $pathCell = (@($paths | ForEach-Object { '``' + $_.Replace('|', '\|') + '``' }) -join '<br>')
    $typeCell = (@($types | ForEach-Object { $_.Replace('|', '\|') }) -join '<br>')
    $rootCell = (@($roots | ForEach-Object { $_.Replace('|', '\|') }) -join '<br>')
    $advice = '保留原 Task 与 SHA/commit/path pin 原文；在新的治理附录追加本次错误原文、调查证据与状态。不得刷新历史 sha256。若需修正，新增当前有效路径/pin 与 old→new 映射；缺少原字节时明确标记不可恢复。'
    if ($rootCell -match 'DAG 未登记') { $advice = '保留历史状态与 DAG 事实；由 Coordinator 决定将 Task 标为 historical/终态或经授权重新登记，不能只为 PASS 改 DAG。' }
    elseif ($rootCell -match 'Manifest') { $advice = '保留既有资源与证据；基于实际文件、SHA、路径和引用检查追加完整 Manifest 行。无法核实的项标为 PRESERVE_UNKNOWN/NOT_RUN，不伪造 closeout。' }
    elseif ($rootCell -match '路径写法') { $advice = '保留旧 pin；追加可解析的当前路径映射及原路径失败记录。只对非 pin 导航链接登记路径迁移，不改写历史 SHA 或原始证据。' }
    $taskName = $record.Task.Replace('|', '\|')
    $report.Add("| ``$taskName`` | $typeCell | $pathCell | $rootCell | $advice |")
}

$report.Add('')
$report.Add('## 处置边界')
$report.Add('')
$report.Add('- 历史 `sha256` 和 commit pin 原样保留；本清单没有对 41 个历史失败 Task 写入修复或刷新 pin。')
$report.Add('- “源文件后续变更”只说明当前字节与历史 pin 不同；只有确认历史 pin 对应原提交字节且后续提交改变同一路径，才可追加“后续合法变更”的结论。')
$report.Add('- `NOT_RUN`/`BLOCKED` 按原始证据保留，不转写为 PASS。')
Set-Content -LiteralPath $ReportPath -Value $report -Encoding utf8
Write-Output "FAILED_TASKS=$($failed.Count)"
Write-Output "ERROR_INSTANCES=$($allErrors.Count)"
Write-Output "REPORT=$ReportPath"
