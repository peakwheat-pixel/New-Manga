# NS-WIRE-A1 AC1/AC2 probe: execute the 8 batch commands directly against the frozen
# core_service.exe (unlabelled copy) and record request/response envelopes.
#
# This probe is *evidence*, not product code: it confirms (a) the Core route each legacy
# command maps to, (b) the payload/minor that actually works, (c) typed error codes for
# the negative cases. The C# dispatcher execution is covered by CommandIntegrationTests.
[CmdletBinding()]
param(
    [string]$SidecarDirectory = 'G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1/sidecar-copy',
    [string]$OutputPath = 'G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-A1/verification/NS-WIRE-A1/probe-results.json',
    [string]$FixtureDataRoot = 'G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data',
    [string]$FixtureChapterId = '240bdba549b74281bfc6d901b1a7abd7'
)
$ErrorActionPreference = 'Stop'
$core = Join-Path $SidecarDirectory 'core_service.exe'
if (-not (Test-Path $core)) { throw "core_service.exe not found: $SidecarDirectory" }
New-Item -ItemType Directory -Force -Path (Split-Path $OutputPath) | Out-Null

function ConvertTo-AsciiJson([string]$json) {
    $sb = [System.Text.StringBuilder]::new()
    foreach ($ch in $json.ToCharArray()) {
        $code = [int]$ch
        if ($code -gt 127) { [void]$sb.AppendFormat('\u{0:x4}', $code) } else { [void]$sb.Append($ch) }
    }
    return $sb.ToString()
}

function Invoke-CoreProbe {
    param(
        [System.Diagnostics.Process]$Process,
        [string]$Name,
        [string]$LegacyCommand,
        [int]$Minor,
        [string]$PayloadJson,
        [string]$DataRoot
    )
    $script:probeId++
    $payload = if ([string]::IsNullOrWhiteSpace($PayloadJson)) { '{}' } else { $PayloadJson }
    $line = ConvertTo-AsciiJson ('{"protocol":"new-manga.core","version":{"major":2,"minor":' + $Minor + '},"request_id":"a1-' + $script:probeId + '","command":"' + $LegacyCommand + '","payload":' + $payload + '}')
    $Process.StandardInput.WriteLine($line)
    $Process.StandardInput.Flush()
    $read = $Process.StandardOutput.ReadLineAsync()
    if (-not $read.Wait(30000)) { throw "timeout waiting for $LegacyCommand" }
    $raw = $read.Result
    $obj = $null
    try { $obj = $raw | ConvertFrom-Json } catch { }
    return [ordered]@{
        name = $Name
        legacy_command = $LegacyCommand
        minor = $Minor
        request_payload = ($payload | ConvertFrom-Json -ErrorAction SilentlyContinue)
        data_root = $DataRoot
        ok = ($null -ne $obj -and $null -eq $obj.error)
        error_code = if ($obj -and $obj.error) { $obj.error.code } else { $null }
        error_category = if ($obj -and $obj.error) { $obj.error.category } else { $null }
        result = if ($obj) { $obj.result } else { $null }
        response_raw = $raw
    }
}

function Start-Core([string]$DataRoot) {
    $envRoot = Join-Path $DataRoot '_env'
    foreach ($sub in @('Roaming', 'Local', 'Temp')) { New-Item -ItemType Directory -Force -Path (Join-Path $envRoot $sub) | Out-Null }
    foreach ($sub in @('derived', 'catalog', 'managed')) { New-Item -ItemType Directory -Force -Path (Join-Path $DataRoot $sub) | Out-Null }
    $si = New-Object System.Diagnostics.ProcessStartInfo
    $si.FileName = $core
    $si.WorkingDirectory = $SidecarDirectory
    $si.UseShellExecute = $false
    $si.CreateNoWindow = $true
    $si.RedirectStandardInput = $true
    $si.RedirectStandardOutput = $true
    $si.RedirectStandardError = $true
    $si.StandardInputEncoding = New-Object System.Text.UTF8Encoding($false)
    $si.StandardOutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $si.Environment['NEWMANGA_DATA_ROOT'] = $DataRoot
    $si.Environment['M2RC1_DERIVED_ROOT'] = (Join-Path $DataRoot 'derived')
    $si.Environment['M2RC2_CATALOG_DB'] = (Join-Path $DataRoot 'catalog/catalog.sqlite')
    $si.Environment['M2RC1_MANAGED_ROOT'] = (Join-Path $DataRoot 'managed')
    $si.Environment['APPDATA'] = Join-Path $envRoot 'Roaming'
    $si.Environment['LOCALAPPDATA'] = Join-Path $envRoot 'Local'
    $si.Environment['TEMP'] = Join-Path $envRoot 'Temp'
    $process = [System.Diagnostics.Process]::Start($si)
    $script:stderrTask = $process.StandardError.ReadToEndAsync()
    return $process
}

$script:probeId = 0
$results = @()
$timestamps = [ordered]@{ started_utc = [DateTime]::UtcNow.ToString('o') }

# --- batch on a fresh isolated root (all commands except the reader projection) ----------
$freshRoot = Join-Path ([IO.Path]::GetTempPath()) ('ns-a1-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
$process = Start-Core $freshRoot
try {
    $results += Invoke-CoreProbe $process 'settings_update_section' 'settings.update_section' 3 '{"section":"ocr","values":{}}' $freshRoot
    $results += Invoke-CoreProbe $process 'settings_provider_profiles_list' 'settings_provider_profiles_list' 7 '{}' $freshRoot
    $results += Invoke-CoreProbe $process 'settings_network_profiles_list' 'settings_network_profiles_list' 7 '{}' $freshRoot
    $results += Invoke-CoreProbe $process 'settings_resolve_overrides' 'settings_resolve_overrides' 7 '{"keys":["sfx.policy"]}' $freshRoot
    $results += Invoke-CoreProbe $process 'backup_create' 'backup.create' 3 '{"backup_type":"manual"}' $freshRoot
    $results += Invoke-CoreProbe $process 'plugins_set_enabled' 'plugins.set_enabled' 3 '{"enabled":false}' $freshRoot
    $results += Invoke-CoreProbe $process 'cleanup_run' 'cleanup.run' 3 '{}' $freshRoot
    # negative controls: wrong minor for P15 face, and reader projection on an empty chapter
    $results += Invoke-CoreProbe $process 'negative_p15_wrong_minor' 'settings_provider_profiles_list' 3 '{}' $freshRoot
    $results += Invoke-CoreProbe $process 'negative_reader_empty_chapter' 'GetReaderProjection' 3 '{"chapter_id":"no-such-chapter","mode":"original","start_position":"beginning"}' $freshRoot
} finally {
    try { $process.StandardInput.Close() } catch { }
    if (-not $process.WaitForExit(8000)) { try { $process.Kill($true) } catch { } }
    try { $stderr1 = $script:stderrTask.Result } catch { $stderr1 = '' }
}

# --- reader projection success path against the BOOK-FIXTURE-1 data root -----------------
$readerProbe = $null
if (Test-Path (Join-Path $FixtureDataRoot 'library.db')) {
    $readerRoot = Join-Path ([IO.Path]::GetTempPath()) ('ns-a1-reader-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
    $process2 = Start-Core $FixtureDataRoot
    try {
        $results += Invoke-CoreProbe $process2 'library_get_reader_projection' 'GetReaderProjection' 3 ('{"chapter_id":"' + $FixtureChapterId + '","mode":"original","start_position":"beginning"}') $FixtureDataRoot
        $script:readerProbe = $results[-1]
    } finally {
        try { $process2.StandardInput.Close() } catch { }
        if (-not $process2.WaitForExit(8000)) { try { $process2.Kill($true) } catch { } }
        try { $stderr2 = $script:stderrTask.Result } catch { $stderr2 = '' }
    }
}

$timestamps.finished_utc = [DateTime]::UtcNow.ToString('o')
$payload = [ordered]@{
    ac = 'AC1/AC2'
    sidecar = $core
    sidecar_sha256 = (Get-FileHash $core -Algorithm SHA256).Hash.ToLowerInvariant()
    fixture_data_root = $FixtureDataRoot
    fixture_chapter_id = $FixtureChapterId
    timestamps = $timestamps
    results = $results
}
$payload | ConvertTo-Json -Depth 12 | Set-Content $OutputPath -Encoding utf8
$payload | ConvertTo-Json -Depth 5
