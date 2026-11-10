#!/usr/bin/env pwsh
# FEA-14-SET-1 (R-013 / scope L2-6): capture the real %APPDATA%\NewManga fingerprint
# before and after the typography projection tests run, and record whether anything
# changed (sha256 + size + mtime). Read-only with respect to AppData.
param(
    [string]$Out = "verification/FEA-14-SET-1/logs/appdata-redline.log"
)

$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location -LiteralPath $root

function Get-Fingerprint([string]$directory) {
    if (-not (Test-Path -LiteralPath $directory)) { return @() }
    return @(
        Get-ChildItem -LiteralPath $directory -Recurse -Force -File |
            Sort-Object FullName |
            ForEach-Object {
                [pscustomobject]@{
                    Path = $_.FullName
                    Bytes = $_.Length
                    MtimeUtc = $_.LastWriteTimeUtc.ToString('o')
                    Sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
                }
            }
    )
}

function Format-Rows($rows) {
    $lines = [System.Collections.Generic.List[string]]::new()
    if ($rows.Count -eq 0) { $lines.Add('  <absent or empty>') }
    foreach ($row in $rows) {
        $lines.Add("  $($row.Path) | $($row.Bytes) bytes | $($row.MtimeUtc) | $($row.Sha256)")
    }
    return @($lines)
}

$appData = Join-Path $env:APPDATA 'NewManga'
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('FEA-14-SET-1 APPDATA RED LINE')
$lines.Add("time=$(Get-Date -Format o)")
$lines.Add("appdata=$env:APPDATA")
$lines.Add("target=$appData")
$lines.Add("HEAD=$(git rev-parse HEAD)")
$lines.Add('')

$before = Get-Fingerprint $appData
$lines.Add('BEFORE:')
Format-Rows $before | ForEach-Object { $lines.Add($_) }

$output = dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter 'FullyQualifiedName~SettingsTypographyPanelTests' -v q 2>&1 | Out-String
$exit = $LASTEXITCODE
$lines.Add('')
$lines.Add("projection-tests-exit=$exit")
($output -split "`r?`n" | Select-Object -Last 6) | ForEach-Object { $lines.Add("  $_") }

$after = Get-Fingerprint $appData
$lines.Add('')
$lines.Add('AFTER:')
Format-Rows $after | ForEach-Object { $lines.Add($_) }

$beforeJson = ($before | ConvertTo-Json -Compress -Depth 3)
$afterJson = ($after | ConvertTo-Json -Compress -Depth 3)
$changed = $beforeJson -ne $afterJson
$lines.Add('')
$lines.Add("VERDICT: $(if ($changed) { 'CHANGED' } else { 'UNCHANGED (no AppData writes)' })")
$lines | Set-Content -LiteralPath $Out -Encoding utf8
Write-Host "wrote $Out"
if ($exit -ne 0 -or $changed) { exit 1 }
exit 0
