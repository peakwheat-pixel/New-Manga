param([string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path)

$ErrorActionPreference = 'Stop'
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

$snapshot = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'isolation-copy.json') -Raw | ConvertFrom-Json
$sourceRoot = Join-Path $env:APPDATA 'com.newmanga.m2rc1.desktop'
$after = [ordered]@{}
$unchanged = $true
foreach ($name in @('catalog', 'data')) {
    $after[$name] = Get-TreeSummary (Join-Path $sourceRoot $name)
    $before = $snapshot.source_before.$name
    if ($before.tree_sha256 -ne $after[$name].tree_sha256 -or $before.files -ne $after[$name].files -or $before.bytes -ne $after[$name].bytes) {
        $unchanged = $false
    }
}

$record = [ordered]@{
    source = '%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,data}'
    checked_at = (Get-Date).ToString('o')
    before = $snapshot.source_before
    after = $after
    source_unchanged = $unchanged
    user_data_modified = $false
}
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'appdata-source-after.json') -Encoding utf8
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'source-preservation-check.json') -Encoding utf8
if (-not $unchanged) { throw 'source AppData catalog/data changed during isolated UIA run' }
Write-Output 'source_appdata_preservation=PASS catalog_unchanged=true data_unchanged=true'
