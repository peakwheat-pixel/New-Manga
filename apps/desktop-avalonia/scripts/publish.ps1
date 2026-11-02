<#
.SYNOPSIS
  Publishes the new shell with the S0-validated single-file recipe and asserts the size gate.

.DESCRIPTION
  Recipe (S0 spike, GO): SingleFile + SelfContained + PublishTrimmed + IncludeNativeLibrariesForSelfExtract
  + ReadyToRun + compression -> one exe (~29 MB), cold start ~400 ms. Writes publish evidence JSON.

.EXAMPLE
  pwsh -NoProfile -File scripts/publish.ps1
#>
[CmdletBinding()]
param(
    [string]$OutputDirectory = ''
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')
$evidence = Join-Path $repoRoot 'verification/HOST-CORECLIENT-1/publish'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $root 'artifacts/win-x64-single'
}
if (Test-Path $OutputDirectory) {
    Remove-Item $OutputDirectory -Recurse -Force
}

$log = Join-Path $evidence 'publish.log'

Push-Location $root
try {
    & dotnet publish src/NewManga.App/NewManga.App.csproj -c Release -r win-x64 --self-contained `
        -p:PublishSingleFile=true `
        -p:PublishTrimmed=true `
        -p:IncludeNativeLibrariesForSelfExtract=true `
        -p:PublishReadyToRun=true `
        -p:EnableCompressionInSingleFile=true `
        -o $OutputDirectory 2>&1 | Tee-Object -FilePath $log | Select-Object -Last 20
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($code -ne 0) {
    throw "dotnet publish failed with exit code $code"
}

$files = Get-ChildItem $OutputDirectory -File
$totalBytes = ($files | Measure-Object Length -Sum).Sum
$exe = $files | Where-Object Name -like 'NewManga.App.exe'
$payload = [ordered]@{
    ac              = 'AC1'
    command         = 'dotnet publish src/NewManga.App -c Release -r win-x64 --self-contained -p:PublishSingleFile=true -p:PublishTrimmed=true -p:IncludeNativeLibrariesForSelfExtract=true -p:PublishReadyToRun=true -p:EnableCompressionInSingleFile=true'
    output_directory = (Resolve-Path $OutputDirectory).Path
    file_count      = $files.Count
    files           = @($files | ForEach-Object { [ordered]@{ name = $_.Name; bytes = $_.Length } })
    total_bytes     = $totalBytes
    total_mb        = [math]::Round($totalBytes / 1MB, 2)
    exe_bytes       = if ($exe) { $exe.Length } else { 0 }
    size_threshold_mb = 45
    single_file_pass = ($files.Count -eq 1 -and $null -ne $exe -and $totalBytes -le 45MB)
    at_utc          = [DateTime]::UtcNow.ToString('o')
}
$payload | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $evidence 'publish_files.json') -Encoding utf8
$payload | ConvertTo-Json -Depth 3

if (-not $payload.single_file_pass) {
    throw "publish gate failed: expected exactly one exe <= 45MB, got $($files.Count) file(s), $($payload.total_mb) MB"
}
Write-Output "PUBLISH PASS: 1 file, $($payload.total_mb) MB"
