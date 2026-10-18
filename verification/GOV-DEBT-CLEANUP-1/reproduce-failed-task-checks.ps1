[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$EvidenceDir = $PSScriptRoot
)

$ErrorActionPreference = 'Stop'
$taskFiles = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'doc/tasks') -Filter 'P*.md' -File | Sort-Object Name)
$records = [System.Collections.Generic.List[object]]::new()
$raw = [System.Collections.Generic.List[string]]::new()
$index = 0

foreach ($file in $taskFiles) {
    $index++
    $relative = 'doc/tasks/' + $file.Name
    $raw.Add("COMMAND[$index]: pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath $relative")
    $output = & pwsh -NoProfile -File (Join-Path $RepoRoot 'tools/governance/check.ps1') -TaskPath $relative 2>&1
    $exitCode = $LASTEXITCODE
    $lines = @($output | ForEach-Object { $_.ToString() })
    $raw.Add("EXIT_CODE[$index]: $exitCode")
    $raw.AddRange([string[]]$lines)
    $errors = @($lines | Where-Object { $_ -match '^FAIL:' })
    if ($exitCode -ne 0) {
        $records.Add([pscustomobject]@{
            TaskPath = $relative
            ExitCode = $exitCode
            ErrorCount = $errors.Count
            Errors = ($errors -join ' || ')
        })
    }
}

$rawPath = Join-Path $EvidenceDir 'failed-task-checks-raw.txt'
$summaryPath = Join-Path $EvidenceDir 'failed-task-checks.tsv'
Set-Content -LiteralPath $rawPath -Value $raw -Encoding utf8
$records | ConvertTo-Csv -Delimiter "`t" -NoTypeInformation | Set-Content -LiteralPath $summaryPath -Encoding utf8

Write-Output "TASKS_CHECKED=$($taskFiles.Count)"
Write-Output "FAILED_TASKS=$($records.Count)"
Write-Output "RAW_OUTPUT=$rawPath"
Write-Output "SUMMARY=$summaryPath"
$records | Format-Table TaskPath, ExitCode, ErrorCount -AutoSize | Out-String | Write-Output
