param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path,
    [string]$IsolationName = 'feat-create-4-isolation-20261017'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = [System.IO.Path]::GetFullPath($RepoRoot)
$isolation = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "apps/desktop/src-tauri/target/$IsolationName"))
$targetRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot 'apps/desktop/src-tauri/target'))
if (-not $isolation.StartsWith($targetRoot + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'refusing isolation path outside the worktree target directory'
}
if (Test-Path -LiteralPath $isolation) { throw "refusing to overwrite existing isolation directory: $isolation" }

$sourceRoot = Join-Path $env:APPDATA 'com.newmanga.m2rc1.desktop'
function Get-TreeSummary([string]$Path) {
    $files = @(Get-ChildItem -LiteralPath $Path -Recurse -File | Sort-Object FullName)
    $lines = foreach ($file in $files) {
        $relative = $file.FullName.Substring($Path.Length).TrimStart('\', '/')
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$relative|$($file.Length)|$hash"
    }
    $bytes = ($files | Measure-Object -Property Length -Sum).Sum
    $digest = [System.Security.Cryptography.SHA256]::Create()
    try {
        $treeHash = [Convert]::ToHexString($digest.ComputeHash([System.Text.UTF8Encoding]::new($false).GetBytes(($lines -join "`n")))).ToLowerInvariant()
    } finally { $digest.Dispose() }
    return [ordered]@{ files = $files.Count; bytes = [long]$bytes; tree_sha256 = $treeHash }
}

$before = [ordered]@{}
foreach ($name in @('catalog', 'data')) {
    $source = Join-Path $sourceRoot $name
    if (-not (Test-Path -LiteralPath $source -PathType Container)) { throw "missing source directory: $name" }
    $before[$name] = Get-TreeSummary $source
}

New-Item -ItemType Directory -Path $isolation | Out-Null
foreach ($name in @('catalog', 'data')) {
    Copy-Item -LiteralPath (Join-Path $sourceRoot $name) -Destination (Join-Path $isolation $name) -Recurse
}
foreach ($name in @('derived', 'managed', 'profile', 'local', 'tmp', 'webview')) {
    New-Item -ItemType Directory -Path (Join-Path $isolation $name) | Out-Null
}

$afterCopy = [ordered]@{}
foreach ($name in @('catalog', 'data')) {
    $afterCopy[$name] = Get-TreeSummary (Join-Path $sourceRoot $name)
    if ($before[$name].tree_sha256 -ne $afterCopy[$name].tree_sha256) { throw "source $name changed during copy" }
}
$copySummary = [ordered]@{}
foreach ($name in @('catalog', 'data')) {
    $copySummary[$name] = Get-TreeSummary (Join-Path $isolation $name)
    if ($before[$name].tree_sha256 -ne $copySummary[$name].tree_sha256) { throw "isolated $name copy does not match source snapshot" }
}

$snapshot = [ordered]@{
    source = '%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,data}'
    captured_at = (Get-Date).ToString('o')
    source_before = $before
    source_after_copy = $afterCopy
    isolated_copy = $copySummary
    isolation_root = "apps/desktop/src-tauri/target/$IsolationName"
    empty_directories = @('derived', 'managed', 'profile', 'local', 'tmp', 'webview')
    source_unchanged = $true
    copy_matches_source = $true
}
$snapshot | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'isolation-copy.json') -Encoding utf8
Write-Output 'isolation_copy=PASS catalog_data_hash_match=true source_unchanged=true derived_empty=true'
