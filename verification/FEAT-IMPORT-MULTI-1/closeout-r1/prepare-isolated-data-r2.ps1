$ErrorActionPreference = 'Stop'
$evidence = Join-Path $PSScriptRoot 'gui-run-r2'
$isolation = Join-Path $env:TEMP 'feat-import-multi-r2'
$sourceRoot = Join-Path $env:APPDATA 'com.newmanga.m2rc1.desktop'
if (Test-Path -LiteralPath $evidence) { throw 'refusing to overwrite GUI evidence directory' }
if (Test-Path -LiteralPath $isolation) { throw 'refusing to reuse TEMP isolation root' }
if (Get-Process -Name 'm2rc1-desktop' -ErrorAction SilentlyContinue) { throw 'm2rc1-desktop is already running; refusing to start a second GUI run' }

function Get-TreeSummary([string]$Path) {
    $files = @(Get-ChildItem -LiteralPath $Path -Recurse -File -Force | Sort-Object FullName)
    $lines = foreach ($file in $files) {
        $relative = $file.FullName.Substring($Path.Length).TrimStart('\', '/')
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$relative|$($file.Length)|$hash"
    }
    $bytes = ($files | Measure-Object -Property Length -Sum).Sum
    $digest = [System.Security.Cryptography.SHA256]::Create()
    try { $treeHash = [Convert]::ToHexString($digest.ComputeHash([System.Text.UTF8Encoding]::new($false).GetBytes(($lines -join "`n")))).ToLowerInvariant() }
    finally { $digest.Dispose() }
    return [ordered]@{ files = $files.Count; bytes = [long]$bytes; tree_sha256 = $treeHash }
}

foreach ($name in @('catalog', 'data')) {
    if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot $name) -PathType Container)) { throw "source AppData directory missing: $name" }
}
$before = [ordered]@{}
foreach ($name in @('catalog', 'data')) { $before[$name] = Get-TreeSummary (Join-Path $sourceRoot $name) }

New-Item -ItemType Directory -Path $evidence | Out-Null
New-Item -ItemType Directory -Path $isolation | Out-Null
foreach ($name in @('catalog', 'data')) {
    Copy-Item -LiteralPath (Join-Path $sourceRoot $name) -Destination (Join-Path $isolation $name) -Recurse
}
foreach ($name in @('derived', 'managed', 'profile', 'local', 'tmp', 'webview', 'fresh-data', 'fixtures')) {
    New-Item -ItemType Directory -Path (Join-Path $isolation $name) | Out-Null
}
foreach ($name in @('multi-select', 'folder-direct')) {
    New-Item -ItemType Directory -Path (Join-Path $isolation "fixtures/$name") | Out-Null
}

$sourceAfterCopy = [ordered]@{}
$isolatedCopy = [ordered]@{}
foreach ($name in @('catalog', 'data')) {
    $sourceAfterCopy[$name] = Get-TreeSummary (Join-Path $sourceRoot $name)
    $isolatedCopy[$name] = Get-TreeSummary (Join-Path $isolation $name)
    if ($before[$name].tree_sha256 -ne $sourceAfterCopy[$name].tree_sha256) { throw "source AppData $name changed during read-only copy" }
    if ($before[$name].tree_sha256 -ne $isolatedCopy[$name].tree_sha256) { throw "isolated copy of $name differs from source snapshot" }
}
$derivedEntries = @(Get-ChildItem -LiteralPath (Join-Path $isolation 'derived') -Force)
if ($derivedEntries.Count -ne 0) { throw 'isolated derived directory was not empty after preparation' }
$snapshot = [ordered]@{
    source = '%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,data}'
    source_before = $before
    source_after_copy = $sourceAfterCopy
    isolated_copy = $isolatedCopy
    isolation_root = '%TEMP%\feat-import-multi-r2'
    empty_initial_directories = @('derived', 'fresh-data', 'managed', 'profile', 'local', 'tmp', 'webview')
    source_unchanged = $true
    copy_matches_source = $true
}
$snapshot | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $evidence 'isolation-copy.json') -Encoding utf8
Write-Output 'isolation_copy=PASS catalog_data_hash_match=true source_unchanged=true derived_empty=true runtime_data_empty=true'
