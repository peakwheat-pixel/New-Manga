<#
.SYNOPSIS
  Probes which protocol-2.3 commands the frozen packaged core_service actually answers.

.DESCRIPTION
  Spawns core_service.exe from the AC11 unlabelled copy with an isolated data root, sends each
  candidate command as one ASCII-escaped JSON line (non-ASCII -> \uXXXX, the S1 contract), records
  status/result/error for every probe, and writes machine-readable evidence. Probe only: no source
  changes, no production data touched.

.EXAMPLE
  pwsh -NoProfile -File apps/desktop-avalonia/scripts/probe-core-commands.ps1
#>
[CmdletBinding()]
param(
    [string]$SidecarDirectory = 'G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy',
    [string]$OutputPath = '',
    # S4-CMD-BATCH-1: optional seeded region fixture root (produced by
    # scripts/seed_s4_region_fixture.py). When supplied, the region write face and the
    # reader progress face are probed with REAL ids against a disposable copy, instead of
    # the frozen S2 invalid-payload probes.
    [string]$RegionFixtureDataRoot = ''
)

$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $repoRoot 'verification/HOST-COMMAND-MIGRATION-1/parity/core-command-probe.json'
}
New-Item -ItemType Directory -Force -Path (Split-Path $OutputPath) | Out-Null
$core = Join-Path $SidecarDirectory 'core_service.exe'
if (-not (Test-Path $core)) { throw "core_service.exe not found under $SidecarDirectory" }

$dataRoot = Join-Path ([IO.Path]::GetTempPath()) ('newmanga-s2-probe-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
$regionMeta = $null
if (-not [string]::IsNullOrWhiteSpace($RegionFixtureDataRoot)) {
    $fixtureRoot = Resolve-Path $RegionFixtureDataRoot
    $metaPath = Join-Path $fixtureRoot 'fixture.json'
    if (-not (Test-Path (Join-Path $fixtureRoot 'library.db')) -or -not (Test-Path $metaPath)) {
        throw "region fixture incomplete under $fixtureRoot (need library.db + fixture.json)"
    }
    $regionMeta = Get-Content $metaPath -Raw | ConvertFrom-Json
    New-Item -ItemType Directory -Force -Path $dataRoot | Out-Null
    foreach ($name in @('library.db', 'library.db-wal', 'library.db-shm')) {
        $candidate = Join-Path $fixtureRoot $name
        if (Test-Path $candidate) { Copy-Item $candidate (Join-Path $dataRoot $name) -Force }
    }
    if (Test-Path (Join-Path $fixtureRoot 'managed')) {
        Copy-Item (Join-Path $fixtureRoot 'managed') (Join-Path $dataRoot 'managed') -Recurse -Force
    }
}
foreach ($sub in @('derived', 'catalog', 'managed')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $dataRoot $sub) | Out-Null
}

function ConvertTo-AsciiJson([string]$json) {
    $sb = [System.Text.StringBuilder]::new()
    foreach ($ch in $json.ToCharArray()) {
        $code = [int]$ch
        if ($code -gt 127) { [void]$sb.AppendFormat('\u{0:x4}', $code) } else { [void]$sb.Append($ch) }
    }
    return $sb.ToString()
}

$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = $core
$startInfo.WorkingDirectory = $SidecarDirectory
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.RedirectStandardInput = $true
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$startInfo.StandardInputEncoding = New-Object System.Text.UTF8Encoding($false)
$startInfo.StandardOutputEncoding = New-Object System.Text.UTF8Encoding($false)
$startInfo.Environment['NEWMANGA_DATA_ROOT'] = $dataRoot
$startInfo.Environment['M2RC1_DERIVED_ROOT'] = (Join-Path $dataRoot 'derived')
$startInfo.Environment['M2RC2_CATALOG_DB'] = (Join-Path $dataRoot 'catalog/catalog.sqlite')
$startInfo.Environment['M2RC1_MANAGED_ROOT'] = (Join-Path $dataRoot 'managed')

$process = [System.Diagnostics.Process]::Start($startInfo)
$stderrTask = $process.StandardError.ReadToEndAsync()
$requestId = 0

function Invoke-Core([string]$command, [int]$minor, $payload) {
    $script:requestId++
    $payloadJson = if ($null -eq $payload) { '{}' } else { $payload | ConvertTo-Json -Compress -Depth 8 }
    $line = ConvertTo-AsciiJson ('{"protocol":"new-manga.core","version":{"major":2,"minor":' + $minor + '},"request_id":"probe-' + $script:requestId + '","command":"' + $command + '","payload":' + $payloadJson + '}')
    $process.StandardInput.WriteLine($line)
    $process.StandardInput.Flush()
    $read = $process.StandardOutput.ReadLineAsync()
    if (-not $read.Wait(30000)) { throw "timeout waiting for $command" }
    $text = $read.Result
    try { $obj = $text | ConvertFrom-Json } catch { $obj = $null }
    return [ordered]@{
        command = $command
        minor = $minor
        request_payload = ($payloadJson | ConvertFrom-Json -ErrorAction SilentlyContinue)
        raw_request_ascii = ($line -match '^[\x00-\x7F]*$')
        response_raw = $text
        ok = ($null -ne $obj -and $null -eq $obj.error)
        error_code = if ($obj -and $obj.error) { $obj.error.code } else { $null }
        error_category = if ($obj -and $obj.error) { $obj.error.category } else { $null }
    }
}

$probes = @()
try {
    $probes += Invoke-Core 'core.ping' 3 $null
    $probes += Invoke-Core 'ListBooks' 3 $null
    $probes += Invoke-Core 'ListRecycleBinBooks' 3 $null
    $createBook = Invoke-Core 'CreateBook' 8 @{ title = '命令面探测・日本語テスト' }
    $probes += $createBook
    $bookId = $null
    if ($createBook.ok) {
        $bookId = ($createBook.response_raw | ConvertFrom-Json).result.book_id
    }
    $createChapter = $null
    if ($bookId) {
        $createChapter = Invoke-Core 'CreateChapter' 8 @{ book_id = $bookId; title = '第1章'; chapter_number = '1' }
        $probes += $createChapter
    }
    $chapterId = $null
    if ($createChapter -and $createChapter.ok) {
        $chapterId = ($createChapter.response_raw | ConvertFrom-Json).result.chapter_id
    }
    if ($bookId) {
        $probes += Invoke-Core 'ListChapters' 3 @{ book_id = $bookId }
    }
    if ($chapterId) {
        $probes += Invoke-Core 'ListChapterPages' 3 @{ chapter_id = $chapterId }
    }
    $probes += Invoke-Core 'settings.get' 3 $null
    $probes += Invoke-Core 'backup.list' 3 $null
    $probes += Invoke-Core 'plugins.list' 3 $null
    $probes += Invoke-Core 'cleanup.preview' 3 $null
    $probes += Invoke-Core 'GetExportHistory' 3 $null
    $probes += Invoke-Core 'ListRegions' 3 $null
    $probes += Invoke-Core 'ListRegionRevisions' 3 $null
    $probes += Invoke-Core 'ResolvePageResource' 3 $null
    # Lowercase routes actually used by the legacy Rust library_bridge (region/reader faces).
    $probes += Invoke-Core 'list_chapters' 3 @{ book_id = 'probe-book' }
    $probes += Invoke-Core 'list_chapter_pages' 3 @{ chapter_id = 'probe-chapter' }
    $probes += Invoke-Core 'list_regions' 3 @{ page_id = 'probe-page' }
    $probes += Invoke-Core 'list_region_revisions' 3 @{ region_id = 'probe-region' }
    $probes += Invoke-Core 'rerender_page' 3 @{ page_id = 'probe-page' }
    $probes += Invoke-Core 'resolve_page_resource' 3 @{ page_id = 'probe-page' }
    $probes += Invoke-Core 'set_region_type' 3 @{ region_id = 'probe-region'; new_region_type = 'probe' }
    $probes += Invoke-Core 'restore_region_revision' 3 @{ region_id = 'probe-region'; revision_no = 1; expected_revision = 1 }
    $probes += Invoke-Core 'GetReaderProjection' 3 @{ chapter_id = 'probe-chapter'; mode = 'scroll'; start_position = 0 }
    $probes += Invoke-Core 'SaveReadingProgress' 3 @{ chapter_id = 'probe-chapter'; position = 0 }
    if ($null -ne $regionMeta) {
        # S4-CMD-BATCH-1: real targets from the seeded region fixture (disposable copy).
        $pageId = $regionMeta.page_id
        $regionId = $regionMeta.region_id
        $chapterId = $regionMeta.chapter_id
        $regionsProbe = Invoke-Core 'list_regions' 3 @{ page_id = $pageId }
        $probes += $regionsProbe
        $currentRevision = $null
        $currentType = $null
        if ($regionsProbe.ok) {
            $regionsResult = ($regionsProbe.response_raw | ConvertFrom-Json).result
            $row = $regionsResult.regions | Where-Object { $_.region_id -eq $regionId } | Select-Object -First 1
            if ($null -ne $row) {
                $currentRevision = [int]$row.revision_no
                $currentType = $row.region_type
            }
        }
        $probes += Invoke-Core 'list_region_revisions' 3 @{ region_id = $regionId }
        $probes += Invoke-Core 'set_region_type' 3 @{
            region_id = $regionId
            new_region_type = if ($currentType -eq 'narration') { 'speech' } else { 'narration' }
            expected_revision = $currentRevision
        }
        $setTypeRevision = $null
        if ($currentRevision -ne $null) { $setTypeRevision = $currentRevision + 1 }
        $probes += Invoke-Core 'restore_region_revision' 3 @{
            region_id = $regionId
            revision_no = 1
            expected_revision = $setTypeRevision
        }
        $probes += Invoke-Core 'rerender_page' 3 @{ page_id = $pageId }
        $probes += Invoke-Core 'resolve_page_resource' 3 @{ page_id = $pageId }
        $probes += Invoke-Core 'SaveReadingProgress' 3 @{
            chapter_id = $chapterId
            mode = 'original'
            page_id = $pageId
            scroll_offset_y = 0
            elapsed_seconds_delta = 1.5
        }
        $probes += Invoke-Core 'GetReaderProjection' 3 @{
            chapter_id = $chapterId
            mode = 'original'
            start_position = 'beginning'
        }
    }
} finally {
    try { $process.StandardInput.Close() } catch { }
    if (-not $process.WaitForExit(5000)) { try { $process.Kill($true) } catch { } }
    $stderr = ''
    try { $stderr = $stderrTask.Result } catch { }
}

$payload = [ordered]@{
    ac = 'AC1/AC3'
    region_fixture = $RegionFixtureDataRoot
    region_fixture_meta = $regionMeta
    sidecar = $core
    sidecar_sha256 = (Get-FileHash $core -Algorithm SHA256).Hash.ToLowerInvariant()
    data_root = $dataRoot
    core_stderr = $stderr
    probes = $probes
    at_utc = [DateTime]::UtcNow.ToString('o')
}
$payload | ConvertTo-Json -Depth 10 | Set-Content $OutputPath -Encoding utf8
$payload | ConvertTo-Json -Depth 4

try { Remove-Item $dataRoot -Recurse -Force } catch { }
Write-Output "probe evidence: $OutputPath"
