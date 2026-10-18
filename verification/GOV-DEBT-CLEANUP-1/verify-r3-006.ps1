[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$EvidenceDir = $PSScriptRoot
)

$ErrorActionPreference = 'Stop'
$specs = @(
    [pscustomobject]@{ Task = 'FEAT-CREATE-1'; Commit = 'c633170d11494f82b5a080eeebc6fa031aa0c282' },
    [pscustomobject]@{ Task = 'FEAT-CREATE-2'; Commit = 'ebe47ff86bd3c155c2d9ebdb41029d41ec4a796c' }
)
$head = (& git -C $RepoRoot rev-parse HEAD).Trim()
$results = [System.Collections.Generic.List[object]]::new()

foreach ($spec in $specs) {
    & git -C $RepoRoot merge-base --is-ancestor $spec.Commit $head
    $ancestorExit = $LASTEXITCODE
    $files = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot "verification/$($spec.Task)") -File | Sort-Object Name)
    foreach ($file in $files) {
        $relative = [IO.Path]::GetRelativePath($RepoRoot, $file.FullName).Replace('\', '/')
        & git -C $RepoRoot cat-file -e "$($spec.Commit):$relative" 2>$null
        $containsExit = $LASTEXITCODE
        $commitBlob = if ($containsExit -eq 0) { (& git -C $RepoRoot rev-parse "$($spec.Commit):$relative").Trim() } else { $null }
        $diskBlob = (& git -C $RepoRoot hash-object -- $relative).Trim()
        $results.Add([pscustomobject]@{
            Task = $spec.Task
            Commit = $spec.Commit
            IsHeadAncestor = ($ancestorExit -eq 0)
            Path = $relative
            Bytes = $file.Length
            CommitContainsPath = ($containsExit -eq 0)
            CommitBlobEqualsDisk = ($containsExit -eq 0 -and $commitBlob -eq $diskBlob)
            Sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        })
    }
}

$jsonPath = Join-Path $EvidenceDir 'r3-006-verification.json'
$results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $jsonPath -Encoding utf8
Write-Output "COMMAND: pwsh -NoProfile -File verification/GOV-DEBT-CLEANUP-1/verify-r3-006.ps1"
Write-Output "HEAD: $head"
Write-Output "EVIDENCE: $jsonPath"
$results | Format-Table Task, Path, Bytes, CommitContainsPath, CommitBlobEqualsDisk, Sha256 -AutoSize | Out-String | Write-Output
