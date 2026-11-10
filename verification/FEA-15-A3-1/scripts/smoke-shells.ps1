#!/usr/bin/env pwsh
# FEA-15-A3-1 AC1/AC2/AC3: four-shell + four-page real-process smoke with
# DUAL-ROOT isolation. Every launch records the main window handle and exit code;
# the real AppData roots are fingerprinted before/after and must stay identical.
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
    $sha = [System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes(($entries -join "`n")))
    return [pscustomobject]@{
        exists = $true
        files = @($entries).Count
        bytes = (Get-ChildItem -LiteralPath $directory -Recurse -Force -File | Measure-Object -Property Length -Sum).Sum
        digest = [Convert]::ToHexString($sha).ToLowerInvariant()
    }
}

function Invoke-Case([string]$name, [string[]]$extraArgs) {
    $arguments = @($extraArgs) + @(
        "--data-root=`"$dataRoot`"",
        "--theme-home=`"$themeHome`"",
        '--exit-after=6000'
    )
    $process = Start-Process -FilePath $Exe -ArgumentList $arguments -PassThru
    $handle = [int64]0
    $deadline = [DateTime]::UtcNow.AddSeconds(20)
    while ([DateTime]::UtcNow -lt $deadline -and -not $process.HasExited) {
        $process.Refresh()
        if ($process.MainWindowHandle -ne 0) { $handle = [int64]$process.MainWindowHandle; break }
        Start-Sleep -Milliseconds 100
    }
    $exited = $process.WaitForExit(30000)
    $code = if ($exited) { $process.ExitCode } else { -1 }
    if (-not $exited) { $process.Kill() }
    $row = [pscustomobject]@{
        case = $name
        args = ($extraArgs -join ' ')
        window_handle = $handle
        window_found = ($handle -ne 0)
        exit_code = $code
        exited = $exited
    }
    Write-Host "case=$name window=$($row.window_found) exit=$code"
    Start-Sleep -Milliseconds 300
    return $row
}

$realData = Join-Path $env:APPDATA 'com.newmanga.desktop'
$realTheme = Join-Path $env:APPDATA 'NewManga'
$beforeData = Get-Fingerprint $realData
$beforeTheme = Get-Fingerprint $realTheme

$rows = @()
$rows += Invoke-Case 'shell.legacy' @('--shell=legacy')
$rows += Invoke-Case 'shell.current-v2' @('--frontend=builtin.current-v2')
$rows += Invoke-Case 'shell.fluent' @('--frontend=builtin.fluent')
$rows += Invoke-Case 'shell.presentation-host' @('--presentation-host=true', '--frontend=builtin.fluent')
foreach ($page in @('bookshelf', 'workbench', 'reader', 'settings')) {
    $rows += Invoke-Case "page.$page" @('--frontend=builtin.fluent', "--page=$page")
}

$afterData = Get-Fingerprint $realData
$afterTheme = Get-Fingerprint $realTheme
$isolation = ($beforeData.digest -eq $afterData.digest) -and ($beforeTheme.digest -eq $afterTheme.digest)
$shells = @($rows | Where-Object { $_.case -like 'shell.*' })
$pages = @($rows | Where-Object { $_.case -like 'page.*' })
$result = [pscustomobject]@{
    ac = 'A3-AC1/AC2/AC3'
    exe = $Exe
    iso_root = $IsoRoot
    cases = $rows
    shells_ok = (@($shells | Where-Object { $_.window_found -and $_.exit_code -eq 0 }).Count -eq $shells.Count)
    pages_ok = (@($pages | Where-Object { $_.window_found -and $_.exit_code -eq 0 }).Count -eq $pages.Count)
    real_appdata = [pscustomobject]@{
        data_root = [pscustomobject]@{ before = $beforeData; after = $afterData }
        theme_root = [pscustomobject]@{ before = $beforeTheme; after = $afterTheme }
        unchanged = $isolation
    }
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Out -Encoding utf8
Write-Output "shells_ok=$($result.shells_ok) pages_ok=$($result.pages_ok) appdata_unchanged=$isolation"
if (-not $result.shells_ok -or -not $result.pages_ok -or -not $isolation) { exit 1 }
exit 0
