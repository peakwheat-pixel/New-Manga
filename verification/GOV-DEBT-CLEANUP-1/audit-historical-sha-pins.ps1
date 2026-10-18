[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$EvidenceDir = $PSScriptRoot
)

$ErrorActionPreference = 'Stop'

function Get-GitBlobBytes([string]$Commit, [string]$RelativePath) {
    $psi = [Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = 'git'
    $psi.WorkingDirectory = $RepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    [void]$psi.ArgumentList.Add('cat-file')
    [void]$psi.ArgumentList.Add('blob')
    [void]$psi.ArgumentList.Add("${Commit}:$RelativePath")
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $psi
    [void]$process.Start()
    $memory = [IO.MemoryStream]::new()
    $process.StandardOutput.BaseStream.CopyTo($memory)
    $process.WaitForExit()
    if ($process.ExitCode -ne 0) { $memory.Dispose(); $process.Dispose(); return $null }
    $bytes = $memory.ToArray()
    $memory.Dispose()
    $process.Dispose()
    return ,$bytes
}

function Get-Sha256Hex([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([Convert]::ToHexString($sha.ComputeHash($Bytes))).ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function Convert-LfToCrLf([byte[]]$Bytes) {
    $converted = [System.Collections.Generic.List[byte]]::new()
    for ($i = 0; $i -lt $Bytes.Length; $i++) {
        if ($Bytes[$i] -eq 10 -and ($i -eq 0 -or $Bytes[$i - 1] -ne 13)) { $converted.Add([byte]13) }
        $converted.Add($Bytes[$i])
    }
    return ,$converted.ToArray()
}

$raw = @(Get-Content -LiteralPath (Join-Path $EvidenceDir 'failed-task-checks-raw.txt'))
$failures = [System.Collections.Generic.List[object]]::new()
$task = $null
foreach ($line in $raw) {
    if ($line -match '^COMMAND\[\d+\]: .* -TaskPath (?<task>\S+)') { $task = $Matches['task']; continue }
    if ($task -and $line -match '^FAIL: Evidence SHA-256 不匹配：(?<path>.+)$') { $failures.Add([pscustomobject]@{ Task = $task; Path = $Matches['path'] }) }
}

$taskRows = @{}
foreach ($entry in ($failures | Select-Object -ExpandProperty Task -Unique)) {
    $taskTextPath = Join-Path $RepoRoot $entry
    $textLines = @(Get-Content -LiteralPath $taskTextPath)
    $inTable = $false
    foreach ($line in $textLines) {
        if ($line -match '^##\s+Canonical Evidence\s*$') { $inTable = $true; continue }
        if ($line -match '^##\s+' -and $inTable) { $inTable = $false }
        if (-not $inTable -or $line -notmatch '^\s*\|.*\|\s*$') { continue }
        $cells = @($line.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim().Trim('`') })
        if ($cells.Count -lt 5 -or $cells[0] -match '^(evidence_id|[-: ]+)$') { continue }
        $path = $cells[2]
        $full = if ([IO.Path]::IsPathRooted($path)) { [IO.Path]::GetFullPath($path) } else { [IO.Path]::GetFullPath((Join-Path $RepoRoot $path)) }
        $repoRelative = [IO.Path]::GetRelativePath($RepoRoot, $full).Replace('\', '/')
        $key = "$entry|$repoRelative"
        $taskRows[$key] = [pscustomobject]@{ Task = $entry; Path = $repoRelative; Commit = $cells[3]; PinnedSha256 = $cells[4].ToLowerInvariant() }
    }
}

$results = [System.Collections.Generic.List[object]]::new()
foreach ($failure in $failures) {
    $path = $failure.Path.Replace('\', '/')
    $key = "$($failure.Task)|$path"
    $row = $taskRows[$key]
    $full = Join-Path $RepoRoot $path
    $currentSha = if (Test-Path -LiteralPath $full -PathType Leaf) { (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
    $statusLines = @(& git -C $RepoRoot status --porcelain=v1 -- $path)
    $status = $statusLines -join ' '
    $commit = $row.Commit
    $resolvedCommit = $null
    $historicalLfSha = $null
    $historicalCrLfSha = $null
    $laterCommits = @()
    $commitBlob = $null
    $headBlob = $null
    $diskBlob = $null
    $isAncestor = $false
    $eol = ''
    if ($commit -match '^[0-9a-fA-F]{7,40}$') {
        $resolvedCommit = (& git -C $RepoRoot rev-parse "$commit^{commit}" 2>$null | Select-Object -First 1)
        if ($LASTEXITCODE -eq 0 -and $resolvedCommit) {
            $historicalBytes = Get-GitBlobBytes $resolvedCommit $path
            if ($null -ne $historicalBytes) {
                $historicalLfSha = Get-Sha256Hex $historicalBytes
                $historicalCrLfSha = Get-Sha256Hex (Convert-LfToCrLf $historicalBytes)
            }
            & git -C $RepoRoot rev-parse "$resolvedCommit`:$path" 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { $commitBlob = (& git -C $RepoRoot rev-parse "$resolvedCommit`:$path").Trim() }
            & git -C $RepoRoot merge-base --is-ancestor $resolvedCommit HEAD
            $isAncestor = $LASTEXITCODE -eq 0
            $laterCommits = @(& git -C $RepoRoot log --format=%H "$resolvedCommit..HEAD" -- $path)
        }
    }
    & git -C $RepoRoot rev-parse "HEAD:$path" 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $headBlob = (& git -C $RepoRoot rev-parse "HEAD:$path").Trim() }
    if (Test-Path -LiteralPath $full -PathType Leaf) { $diskBlob = (& git -C $RepoRoot hash-object -- $path).Trim() }
    $eol = (@(& git -C $RepoRoot ls-files --eol -- $path) | Select-Object -First 1)

    if (-not $row) { $cause = 'Canonical Evidence pin row not parsed; cause unverified' }
    elseif (-not $historicalLfSha) { $cause = 'Pinned commit does not contain/read this path; cause unverified' }
    elseif ($row.PinnedSha256 -notin @($historicalLfSha, $historicalCrLfSha)) { $cause = 'Stored SHA does not match cited commit bytes as LF or CRLF; historical pin/path binding is internally inconsistent' }
    elseif ($isAncestor -and $commitBlob -and $headBlob -and $headBlob -ne $commitBlob -and $laterCommits.Count -gt 0) {
        if ($status) { $cause = 'Source changed in later committed history; current working tree also differs, so current bytes include uncommitted drift' }
        else { $cause = 'Source file changed in later committed history; historical pin matches cited commit bytes' }
    }
    elseif ($commitBlob -and $headBlob -eq $commitBlob -and $diskBlob -eq $headBlob -and $currentSha -ne $row.PinnedSha256) {
        if ($row.PinnedSha256 -eq $historicalLfSha -and $eol -match 'w/crlf') { $cause = 'Working-tree CRLF conversion differs from LF pin; committed source blob has not changed' }
        else { $cause = 'Raw-byte SHA differs while committed source blob is unchanged; line-ending/encoding normalization likely' }
    }
    elseif ($status -or -not $headBlob -or $headBlob -ne $diskBlob) { $cause = 'Working-tree state differs; later legal committed change not proven' }
    else { $cause = 'SHA mismatch without a verified later committed source change; cause unverified' }

    $results.Add([pscustomobject]@{
        Task = $failure.Task
        Path = $path
        CitedCommit = if ($resolvedCommit) { $resolvedCommit } else { $commit }
        PinnedSha256 = if ($row) { $row.PinnedSha256 } else { '' }
        HistoricalCommitLfSha256 = $historicalLfSha
        HistoricalCommitCrLfSha256 = $historicalCrLfSha
        CurrentDiskSha256 = $currentSha
        WorkingTreeStatus = $status
        CheckoutEol = $eol
        CommitBlob = $commitBlob
        HeadBlob = $headBlob
        DiskCleanBlob = $diskBlob
        IsCitedCommitAncestor = $isAncestor
        LaterCommitCount = $laterCommits.Count
        Classification = $cause
    })
}

$tsvPath = Join-Path $EvidenceDir 'historical-sha-pin-audit.tsv'
$results | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation | Set-Content -LiteralPath $tsvPath -Encoding utf8
$grouped = @($results | Group-Object Classification | Sort-Object Name)
Write-Output "SHA_PIN_FAILURES=$($results.Count)"
Write-Output "UNIQUE_PATHS=$(@($results.Path | Sort-Object -Unique).Count)"
Write-Output "AUDIT=$tsvPath"
$grouped | ForEach-Object { Write-Output "$($_.Name)=$($_.Count)" }
