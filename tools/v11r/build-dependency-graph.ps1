#Requires -Version 7.0
<#
.SYNOPSIS
  Regenerates the V11R-C-3 legacy-theme dependency graph from the current working tree.

.DESCRIPTION
  Scans every tracked file (git grep) for the twelve retired symbols, classifies each reference by the
  role of its file in the retirement plan, and writes:
    verification/V11R-C-3-READY/dependency-graph.json        machine-readable evidence
    verification/V11R-C-3-READY/dependency-graph-table.md   human-readable reference table
  The script only writes evidence files. Re-run it whenever main moves, because C-3's zero-reference
  gate depends on this graph being current.

.NOTES
  `LayoutKind` also appears as the CLR enum used by StructLayout P/Invoke declarations. Those references
  are classified as platform-struct-unrelated and never count as a legacy theme dependency.
#>
[CmdletBinding()]
param(
    [string]$RepositoryRoot = '',
    [string]$OutputDirectory = 'verification/V11R-C-3'
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = (& git rev-parse --show-toplevel).Trim()
}

$symbols = @(
    'ThemePackMetrics',
    'ThemePackService',
    'ThemePacks',
    'ThemePack',
    'LayoutProfiles',
    'LayoutProfile',
    'LayoutKind',
    'NavPlacement',
    'ShelfStyle',
    'SettingsStyle',
    'MotionProfile'
)
$excludePaths = @('archive/**', '**/bin/**', '**/obj/**', '**/node_modules/**', 'tools/v11r/**', 'verification/V11R-C-3-READY/**', 'verification/V11R-C-3/**')
$pattern = '\b(' + ($symbols -join '|') + ')\b'

$outputPath = Join-Path $RepositoryRoot $OutputDirectory
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null

function Get-ReferenceKind([string]$path) {
    if ($path -like 'apps/desktop-avalonia/src/NewManga.Theme/*') { return 'legacy-theme-source' }
    if ($path -like 'apps/desktop-avalonia/src/NewManga.App/*') { return 'legacy-shell-production' }
    if ($path -like 'apps/desktop-avalonia/tests/NewManga.App.Tests/*') { return 'legacy-tests' }
    if ($path -like 'apps/desktop-avalonia/tests/*.Tests/*') { return 'new-architecture-tests' }
    if ($path -like 'apps/desktop-avalonia/src/NewManga.ThemeEngine/*') { return 'new-architecture' }
    if ($path -like 'apps/desktop-avalonia/src/NewManga.DesignSystem/*') { return 'new-architecture' }
    if ($path -like 'apps/desktop-avalonia/src/NewManga.Host/*') { return 'new-architecture' }
    if ($path -like 'apps/desktop-avalonia/src/NewManga.CoreClient/*') { return 'new-architecture' }
    if ($path -like 'apps/desktop-avalonia/scripts/*' -or $path -like 'scripts/*' -or $path -like 'tools/*') { return 'build-script-unrelated' }
    if ($path -like 'doc/*' -or $path -like 'verification/*') { return 'evidence-or-documentation' }
    return 'other'
}

function Get-RetireFate([string]$kind) {
    switch ($kind) {
        'legacy-theme-source' { return 'DELETE-WITH-C3' }
        'legacy-shell-production' { return 'MIGRATE-THEN-DELETE' }
        'legacy-tests' { return 'REPLACE-BEFORE-DELETE' }
        'new-architecture' { return 'NOT-A-DEPENDENCY' }
        'new-architecture-tests' { return 'NOT-A-DEPENDENCY' }
        'build-script-unrelated' { return 'NOT-A-DEPENDENCY' }
        'platform-struct-unrelated' { return 'NOT-A-DEPENDENCY' }
        'evidence-or-documentation' { return 'EVIDENCE-PIN-PROTECTED' }
        default { return 'REVIEW' }
    }
}

$grepArguments = @('grep', '-n', '-E', $pattern, '--')
foreach ($exclude in $excludePaths) {
    $grepArguments += ":!$exclude"
}

$lines = & git -C $RepositoryRoot @grepArguments 2>$null
if ($LASTEXITCODE -notin @(0, 1)) {
    throw "git grep failed with exit code $LASTEXITCODE"
}
if ($null -eq $lines) { $lines = @() }

$entries = [System.Collections.Generic.List[object]]::new()
$fileRows = @{}
$fileTextCache = @{}
function Get-FileText([string]$relativePath) {
    if (-not $fileTextCache.ContainsKey($relativePath)) {
        $absolute = Join-Path $RepositoryRoot $relativePath
        $fileTextCache[$relativePath] = if (Test-Path -LiteralPath $absolute) {
            Get-Content -LiteralPath $absolute -Raw -ErrorAction SilentlyContinue
        } else {
            $null
        }
    }
    return $fileTextCache[$relativePath]
}
foreach ($line in $lines) {
    if ($line -notmatch '^(?<path>[^:]+):(?<line>\d+):(?<text>.*)$') { continue }
    $path = $Matches['path']
    $lineNumber = [int]$Matches['line']
    $text = $Matches['text']
    $symbol = $symbols | Where-Object { $text -match "\b$_\b" } | Select-Object -First 1
    $kind = Get-ReferenceKind $path
    if ($symbol -eq 'LayoutKind' -and $text -match 'StructLayout\(') {
        $kind = 'platform-struct-unrelated'
    }
    elseif ($symbol -in @('LayoutProfile', 'LayoutProfiles')) {
        # Same-name collision: NewManga.ThemeEngine.Models.LayoutProfile is a new-architecture type.
        # When the file references the ThemeEngine namespace (using or fully-qualified) and does not import
        # the legacy NewManga.Theme namespace, the match is a new-architecture reference, not a dependency.
        $content = Get-FileText $path
        if ($kind -in @('legacy-shell-production', 'legacy-tests', 'legacy-theme-source') -and
            $null -ne $content -and
            $content -match 'NewManga\.ThemeEngine' -and
            $content -notmatch 'using\s+NewManga\.Theme\s*;') {
            $kind = if ($path -like 'apps/desktop-avalonia/tests/*') { 'new-architecture-tests' } else { 'new-architecture' }
        }
    }

    $fate = Get-RetireFate $kind
    $entries.Add([ordered]@{
            symbol = $symbol
            file   = $path
            line   = $lineNumber
            kind   = $kind
            fate   = $fate
            text   = $text.Trim()
        })
    if (-not $fileRows.ContainsKey($path)) {
        $fileRows[$path] = [ordered]@{
            file       = $path
            kind       = $kind
            fate       = $fate
            references = 0
            symbols    = @{}
        }
    }
    $fileRows[$path].references++
    $fileRows[$path].symbols[$symbol] = 1
}

$files = $fileRows.Values | ForEach-Object {
    [ordered]@{
        file       = $_.file
        kind       = $_.kind
        fate       = $_.fate
        references = $_.references
        symbols    = @($_.symbols.Keys | Sort-Object)
    }
} | Sort-Object -Property @{ Expression = 'references'; Descending = $true }, file

$headCommit = (& git -C $RepositoryRoot rev-parse HEAD).Trim()
$baseCommit = (& git -C $RepositoryRoot rev-parse main 2>$null | Out-String).Trim()
if ([string]::IsNullOrWhiteSpace($baseCommit)) { $baseCommit = $headCommit }
$workingTreeDirty = ((& git -C $RepositoryRoot status --porcelain | Out-String).Trim().Length -gt 0)
$generatedAt = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

$kindSummary = @($entries | Group-Object { $_.kind } | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Count)" })
$fateSummary = @($entries | Group-Object { $_.fate } | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Count)" })
$symbolSummary = @($entries | Group-Object { $_.symbol } | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Count)" })

$summary = [ordered]@{
    totalReferences = $entries.Count
    totalFiles      = $files.Count
    byKind          = $kindSummary
    byFate          = $fateSummary
    bySymbol        = $symbolSummary
}

$document = [ordered]@{
    schema           = 'newmanga.v11r.c3-dependency-graph/1'
    task             = 'V11R-C-3'
    baseCommit       = $baseCommit
    repoHead         = $headCommit
    workingTreeDirty = $workingTreeDirty
    generatedAt      = $generatedAt
    symbols          = $symbols
    excludePaths     = $excludePaths
    summary          = $summary
    files            = @($files)
    references       = @($entries)
}

$jsonPath = Join-Path $outputPath 'dependency-graph.json'
$json = $document | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($jsonPath, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))

$table = [System.Text.StringBuilder]::new()
[void]$table.AppendLine('# V11R-C-3 旧主题符号引用表（脚本生成，勿手改）')
[void]$table.AppendLine()
[void]$table.AppendLine("- 基线 commit：``$commit``")
[void]$table.AppendLine("- 生成时间：$generatedAt")
[void]$table.AppendLine("- 总引用：$($entries.Count) 处 / $($files.Count) 文件")
[void]$table.AppendLine()
[void]$table.AppendLine('| 文件 | 类型 | 处置 | 引用数 | 符号 |')
[void]$table.AppendLine('|---|---|---|---:|---|')
foreach ($file in $files) {
    [void]$table.AppendLine("| ``$($file.file)`` | $($file.kind) | $($file.fate) | $($file.references) | $($file.symbols -join ', ') |")
}

$tablePath = Join-Path $outputPath 'dependency-graph-table.md'
[System.IO.File]::WriteAllText($tablePath, $table.ToString(), [System.Text.UTF8Encoding]::new($false))

Write-Output "base main   : $baseCommit"
Write-Output "repo HEAD   : $headCommit"
Write-Output "references  : $($entries.Count) in $($files.Count) files"
Write-Output "json        : $jsonPath"
Write-Output "table       : $tablePath"
$kindSummary | ForEach-Object { Write-Output "  kind  $_" }
$fateSummary | ForEach-Object { Write-Output "  fate  $_" }







