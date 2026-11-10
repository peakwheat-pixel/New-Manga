#!/usr/bin/env pwsh
# FEA-15-A2-1 AC4: four-page real-process smoke with DUAL-ROOT isolation.
# Starts the installed Fluent app once per page (--exit-after), records the main
# window handle and exit code, and proves the REAL AppData roots are untouched.
param(
    [Parameter(Mandatory = $true)][string]$Exe,
    [Parameter(Mandatory = $true)][string]$IsoRoot,
    [Parameter(Mandatory = $true)][string]$Out
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force $IsoRoot | Out-Null
$dataRoot = Join-Path $IsoRoot 'data'
$themeHome = Join-Path $IsoRoot 'theme'
New-Item -ItemType Directory -Force $dataRoot, $themeHome | Out-Null

function Get-Fingerprint([string]$directory) {
    if (-not (Test-Path -LiteralPath $directory)) {
        return [pscustomobject]@{ exists = $false; files = 0; bytes = 0; digest = '<absent>' }
    }
    $entries = Get-ChildItem -LiteralPath $directory -Recurse -Force -File |
        Sort-Object FullName |
        ForEach-Object { "$($_.FullName)|$($_.Length)|$($_.LastWriteTimeUtc.Ticks)" }
    $text = ($entries -join "`n")
    $sha = [System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($text))
    return [pscustomobject]@{
        exists = $true
        files = @($entries).Count
        bytes = (Get-ChildItem -LiteralPath $directory -Recurse -Force -File | Measure-Object -Property Length -Sum).Sum
        digest = [Convert]::ToHexString($sha).ToLowerInvariant()
    }
}

$realData = Join-Path $env:APPDATA 'com.newmanga.desktop'
$realTheme = Join-Path $env:APPDATA 'NewManga'
$beforeData = Get-Fingerprint $realData
$beforeTheme = Get-Fingerprint $realTheme

$rows = @()
foreach ($page in @('bookshelf', 'workbench', 'reader', 'settings')) {
    $arguments = @(
        '--frontend=builtin.fluent',
        "--page=$page",
        "--data-root=`"$dataRoot`"",
        "--theme-home=`"$themeHome`"",
        '--exit-after=8000'
    )
    $process = Start-Process -FilePath $Exe -ArgumentList $arguments -PassThru
    $handle = [int64]0
    $deadline = [DateTime]::UtcNow.AddSeconds(20)
    while ([DateTime]::UtcNow -lt $deadline -and -not $process.HasExited) {
        $process.Refresh()
        if ($process.MainWindowHandle -ne 0) {
            $handle = [int64]$process.MainWindowHandle
            break
        }
        Start-Sleep -Milliseconds 100
    }
    $exited = $process.WaitForExit(30000)
    $code = if ($exited) { $process.ExitCode } else { -1 }
    if (-not $exited) { $process.Kill() }
    $rows += [pscustomobject]@{
        page = $page
        window_handle = $handle
        window_found = ($handle -ne 0)
        exit_code = $code
        exited = $exited
    }
    Start-Sleep -Milliseconds 300
}

$afterData = Get-Fingerprint $realData
$afterTheme = Get-Fingerprint $realTheme
$isolation = ($beforeData.digest -eq $afterData.digest) -and ($beforeTheme.digest -eq $afterTheme.digest)
$result = [pscustomobject]@{
    ac = 'A2-AC4'
    exe = $Exe
    iso_root = $IsoRoot
    pages = $rows
    pages_ok = (@($rows | Where-Object { $_.window_found -and $_.exit_code -eq 0 }).Count -eq 4)
    real_appdata = [pscustomobject]@{
        data_root = [pscustomobject]@{ before = $beforeData; after = $afterData }
        theme_root = [pscustomobject]@{ before = $beforeTheme; after = $afterTheme }
        unchanged = $isolation
    }
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Out -Encoding utf8
Write-Output "pages_ok=$($result.pages_ok) appdata_unchanged=$isolation"
foreach ($row in $rows) {
    Write-Output "page=$($row.page) window=$($row.window_found) exit=$($row.exit_code)"
}
if (-not $result.pages_ok -or -not $isolation) { exit 1 }
exit 0
