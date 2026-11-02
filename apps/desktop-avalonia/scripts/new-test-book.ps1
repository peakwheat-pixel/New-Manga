# BOOK-FIXTURE-1 — 一键建书（隔离数据根，供真机 webtoon/Esc-H 复测）
#
# 做什么：在隔离数据根里创建 1 本 webtoon 测试书（页面只读引用
# test_assets/comic_golden_suite/日漫_JA/**，不复制进仓库），然后用**冻结的
# core_service.exe**（协议 2.3）复核 ListBooks / list_chapters /
# GetReaderProjection，证据 JSON 落到 verification/BOOK-FIXTURE-1/。
#
# 幂等：重复执行会复用同名书（status=existing），不会重复建书；-Force 才会
# 软删旧书后重新导入。
#
# 不污染真实 %APPDATA%：APPDATA/LOCALAPPDATA/TEMP/TMP 全部重定向到
# <DataRoot>/_env/ 下，脚本同时记录真实 %APPDATA%\com.newmanga.desktop 的
# 前后状态并断言未变化。
[CmdletBinding()]
param(
    [string]$DataRoot = $( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/BOOK-FIXTURE-1/isolated-data' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/BOOK-FIXTURE-1/isolated-data' } ),
    [string]$BookTitle = 'BOOK-FIXTURE-1 日漫_JA 测试书',
    [string]$ChapterTitle = '第 1 章',
    [int]$PageLimit = 8,
    [string]$PythonExe = $( if ($env:NEWMANGA_BUILD_PYTHON) { $env:NEWMANGA_BUILD_PYTHON } else { 'python' } ),
    [string]$SidecarDirectory = $( $v11rRepo = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent); if ($env:NEWMANGA_WORKSPACE_ROOT) { Join-Path $env:NEWMANGA_WORKSPACE_ROOT 'task-envs/FINAL-VALIDATION-1/sidecar-copy' } else { Join-Path (Join-Path (Split-Path $v11rRepo -Parent) ((Split-Path $v11rRepo -Leaf) + '.workspace')) 'task-envs/FINAL-VALIDATION-1/sidecar-copy' } ),
    [string]$PagesRoot = '',
    [string]$EvidencePath = '',
    [switch]$Force,
    [switch]$SkipVerify
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')
# Golden-suite pages are gitignored (test_assets/**/.gitignore = /*), so a
# LINKED WORKTREE checkout does not carry them. Resolve read-only in order:
# explicit -PagesRoot > this checkout > the main checkout working tree.
# Nothing is copied into the repo; the importer reads the files in place.
function Resolve-PagesRoot([string]$explicit) {
    if (-not [string]::IsNullOrWhiteSpace($explicit)) { return $explicit }
    $candidates = @(
        (Join-Path $repoRoot 'test_assets/comic_golden_suite/日漫_JA'),
        $( if ($env:NEWMANGA_REPO_ROOT) { Join-Path $env:NEWMANGA_REPO_ROOT 'test_assets/comic_golden_suite/日漫_JA' } else { Join-Path (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent) 'test_assets/comic_golden_suite/日漫_JA' } )
    )
    foreach ($candidate in $candidates) {
        if (-not (Test-Path $candidate)) { continue }
        $images = @(Get-ChildItem $candidate -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -match '\.(jpg|jpeg|png)$' })
        if ($images.Count -gt 0) { return $candidate }
    }
    throw "golden-suite pages not found (tried: $($candidates -join '; ')); pass -PagesRoot"
}
$pagesRoot = Resolve-PagesRoot $PagesRoot
$helper = Join-Path $PSScriptRoot 'new_test_book.py'
if ([string]::IsNullOrWhiteSpace($EvidencePath)) {
    $EvidencePath = Join-Path $repoRoot 'verification/BOOK-FIXTURE-1/book-fixture.json'
}
New-Item -ItemType Directory -Force -Path (Split-Path $EvidencePath) | Out-Null
if (-not (Test-Path $PythonExe)) { throw "python not found: $PythonExe" }

# ---- isolated env (nothing below touches the real profile) -----------------
$envDir = Join-Path $DataRoot '_env'
foreach ($sub in @('Roaming', 'Local', 'Temp')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $envDir $sub) | Out-Null
}
New-Item -ItemType Directory -Force -Path $DataRoot | Out-Null

# ---- real-profile snapshot (AC4: must stay untouched) ----------------------
$realAppData = $env:APPDATA
$realRoot = Join-Path $realAppData 'com.newmanga.desktop'
function Get-DirFingerprint([string]$Path) {
    if (-not (Test-Path $Path)) { return [ordered]@{ exists = $false } }
    $files = @(Get-ChildItem $Path -Recurse -File -ErrorAction SilentlyContinue)
    return [ordered]@{
        exists      = $true
        file_count  = $files.Count
        last_write  = (Get-Item $Path).LastWriteTimeUtc.ToString('o')
    }
}
$realBefore = Get-DirFingerprint $realRoot

$savedEnv = @{}
foreach ($name in @('NEWMANGA_DATA_ROOT', 'APPDATA', 'LOCALAPPDATA', 'TEMP', 'TMP', 'M2RC1_DERIVED_ROOT', 'M2RC2_CATALOG_DB', 'M2RC1_MANAGED_ROOT', 'PYTHONIOENCODING', 'PYTHONUTF8')) {
    $savedEnv[$name] = [Environment]::GetEnvironmentVariable($name)
}
$creation = $null
$creationLog = Join-Path (Split-Path $EvidencePath) 'new-test-book.helper.log'
$creationJson = Join-Path (Split-Path $EvidencePath) 'new-test-book.creation.json'
$sw = [Diagnostics.Stopwatch]::StartNew()
try {
    $env:NEWMANGA_DATA_ROOT = $DataRoot
    $env:APPDATA = Join-Path $envDir 'Roaming'
    $env:LOCALAPPDATA = Join-Path $envDir 'Local'
    $env:TEMP = Join-Path $envDir 'Temp'
    $env:TMP = Join-Path $envDir 'Temp'
    $env:M2RC1_DERIVED_ROOT = Join-Path $DataRoot 'derived'
    $env:M2RC2_CATALOG_DB = Join-Path $DataRoot 'catalog/catalog.sqlite'
    $env:M2RC1_MANAGED_ROOT = Join-Path $DataRoot 'managed'
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONUTF8 = '1'

    $helperArgs = @('--data-root', $DataRoot, '--pages-root', $pagesRoot, '--title', $BookTitle, '--chapter-title', $ChapterTitle, '--page-limit', "$PageLimit", '--json-out', $creationJson)
    if ($Force) { $helperArgs += '--force' }
    $helperOut = & $PythonExe $helper @helperArgs 2>&1
    $helperCode = $LASTEXITCODE
    $helperOut | Set-Content $creationLog -Encoding utf8
    if ($helperCode -ne 0) { throw "book creation failed (exit=$helperCode); see $creationLog" }
    if (-not (Test-Path $creationJson)) { throw "helper did not write $creationJson; see $creationLog" }
    $creation = Get-Content $creationJson -Raw -Encoding utf8 | ConvertFrom-Json
    if (-not $creation.book_id -or $creation.page_count -lt 1) { throw "helper returned no usable book/page data" }
} finally {
    $sw.Stop()
    foreach ($name in $savedEnv.Keys) { [Environment]::SetEnvironmentVariable($name, $savedEnv[$name]) }
}
$realAfter = Get-DirFingerprint $realRoot
$realUntouched = ($realBefore.exists -eq $realAfter.exists) -and
    ((-not $realBefore.exists) -or ($realBefore.last_write -eq $realAfter.last_write))

# ---- protocol verification against the frozen sidecar ----------------------
$verification = $null
if (-not $SkipVerify) {
    $coreExe = Join-Path $SidecarDirectory 'core_service.exe'
    if (-not (Test-Path $coreExe)) { throw "core_service.exe not found under $SidecarDirectory (use -SkipVerify to only create the book)" }
    Add-Type -TypeDefinition @"
using System;using System.Runtime.InteropServices;
public static class BfWin{public delegate bool EnumProc(IntPtr h,IntPtr l);[DllImport("user32.dll")]static extern bool EnumWindows(EnumProc p,IntPtr l);}
"@ -ErrorAction SilentlyContinue | Out-Null
    function ConvertTo-AsciiJson([string]$json) {
        $sb = [System.Text.StringBuilder]::new()
        foreach ($ch in $json.ToCharArray()) {
            $code = [int]$ch
            if ($code -gt 127) { [void]$sb.AppendFormat('\u{0:x4}', $code) } else { [void]$sb.Append($ch) }
        }
        return $sb.ToString()
    }
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $coreExe
    $startInfo.WorkingDirectory = $SidecarDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.StandardInputEncoding = New-Object System.Text.UTF8Encoding($false)
    $startInfo.StandardOutputEncoding = New-Object System.Text.UTF8Encoding($false)
    # The frozen Core must serve this exact isolated data root.
    $startInfo.Environment['NEWMANGA_DATA_ROOT'] = $DataRoot
    $startInfo.Environment['M2RC1_DERIVED_ROOT'] = Join-Path $DataRoot 'derived'
    $startInfo.Environment['M2RC2_CATALOG_DB'] = Join-Path $DataRoot 'catalog/catalog.sqlite'
    $startInfo.Environment['M2RC1_MANAGED_ROOT'] = Join-Path $DataRoot 'managed'
    $startInfo.Environment['APPDATA'] = Join-Path $envDir 'Roaming'
    $startInfo.Environment['LOCALAPPDATA'] = Join-Path $envDir 'Local'
    $startInfo.Environment['TEMP'] = Join-Path $envDir 'Temp'
    $process = [System.Diagnostics.Process]::Start($startInfo)
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $script:requestId = 0
    function Invoke-Core([string]$command, [int]$minor, $payload) {
        $script:requestId++
        $payloadJson = if ($null -eq $payload) { '{}' } else { $payload | ConvertTo-Json -Compress -Depth 8 }
        $line = ConvertTo-AsciiJson ('{"protocol":"new-manga.core","version":{"major":2,"minor":' + $minor + '},"request_id":"bf-' + $script:requestId + '","command":"' + $command + '","payload":' + $payloadJson + '}')
        $process.StandardInput.WriteLine($line)
        $process.StandardInput.Flush()
        $read = $process.StandardOutput.ReadLineAsync()
        if (-not $read.Wait(30000)) { throw "timeout waiting for $command" }
        return $read.Result | ConvertFrom-Json
    }
    try {
        $ping = Invoke-Core 'core.ping' 3 $null
        $listBooks = Invoke-Core 'ListBooks' 3 $null
        $bookSummary = @($listBooks.result) | Where-Object { $_.book_id -eq $creation.book_id }
        $chapters = Invoke-Core 'list_chapters' 3 @{ book_id = $creation.book_id }
        $projection = $null
        if ($chapters.result.chapters -and $chapters.result.chapters.Count -gt 0) {
            $projection = Invoke-Core 'GetReaderProjection' 3 @{ chapter_id = $chapters.result.chapters[0].chapter_id; mode = 'original'; start_position = 'beginning' }
        }
        $verification = [ordered]@{
            sidecar          = $coreExe
            sidecar_sha256   = (Get-FileHash $coreExe -Algorithm SHA256).Hash.ToLowerInvariant()
            ping_ok          = ($null -eq $ping.error -and $ping.result.status -eq 'ready')
            list_books_count = @($listBooks.result).Count
            book_found       = ($null -ne $bookSummary)
            page_count       = if ($bookSummary) { $bookSummary.page_count } else { $null }
            chapters         = @($chapters.result.chapters)
            reader_pages     = @($projection.result.pages)
            reader_layout    = if ($projection) { $projection.result.layout } else { $null }
            error            = if ($bookSummary) { $null } else { 'BOOK_NOT_FOUND_IN_LISTBOOKS' }
        }
        $verification.page_dimensions_parseable = (
            $verification.reader_pages.Count -gt 0 -and
            @($verification.reader_pages | Where-Object { $_.width_px -gt 0 -and $_.height_px -gt 0 }).Count -eq $verification.reader_pages.Count
        )
        $verification.book_summary = $bookSummary
        if ($verification.book_found -ne $true) { throw 'verification failed: book not found by list_books' }
        if (-not ($verification.page_count -gt 0)) { throw 'verification failed: page_count is not > 0' }
        if (-not $verification.page_dimensions_parseable) { throw 'verification failed: page dimensions unparsable' }
    } finally {
        try { Invoke-Core 'core.shutdown' 3 $null | Out-Null } catch { }
        try { $process.StandardInput.Close() } catch { }
        if (-not $process.WaitForExit(8000)) { try { $process.Kill($true) } catch { } }
        $coreStderr = ''
        try { $coreStderr = $stderrTask.Result } catch { }
    }
}

# ---- evidence --------------------------------------------------------------
$evidence = [ordered]@{
    ac                  = 'AC1/AC2'
    generated_at_utc    = [DateTime]::UtcNow.ToString('o')
    data_root           = $DataRoot
    isolated_env        = [ordered]@{
        APPDATA      = Join-Path $envDir 'Roaming'
        LOCALAPPDATA = Join-Path $envDir 'Local'
        TEMP         = Join-Path $envDir 'Temp'
    }
    real_appdata        = [ordered]@{ root = $realRoot; before = $realBefore; after = $realAfter; untouched = $realUntouched }
    creation            = $creation
    creation_duration_ms = [int]$sw.Elapsed.TotalMilliseconds
    verification        = $verification
    helper_log          = $creationLog
    core_stderr_tail    = if ($verification) { $coreStderr } else { $null }
}
$evidence | ConvertTo-Json -Depth 12 | Set-Content $EvidencePath -Encoding utf8
$evidence | ConvertTo-Json -Depth 4
if (-not $realUntouched) { throw 'real %APPDATA%\com.newmanga.desktop changed during the fixture run' }
