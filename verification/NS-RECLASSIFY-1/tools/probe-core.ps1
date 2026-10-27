<#
.SYNOPSIS
  NS-RECLASSIFY-1 AC1: re-probe every NOT_SUPPORTED command against the frozen core_service.exe
  with a payload built from the legacy Rust signature / Core contract.

.DESCRIPTION
  Evidence-only: writes a probe log, never touches product source, registry, parity snapshots
  or another task's data root. The frozen sidecar is the unlabelled AC11 copy (same sha256 as the
  one the S2 probe used). Each phase runs against its own isolated data root:
    fresh   - empty root for settings / plugins / backup / cleanup / credential faces
    fixture - private copy of BOOK-FIXTURE-1/isolated-data so region/reader commands see real ids
    host    - same fixture root, host-control envelope (OpenHostSession -> import/export faces)

  Rule for the report: a command counts as IMPLEMENTED only on a real result, or on a typed DOMAIN
  error (not_found/conflict) that a missing route cannot produce. UNKNOWN_COMMAND / HOST_ONLY_REQUIRED
  means the route is absent; INVALID_REQUEST means the payload is still wrong (and is reported as such,
  never silently upgraded to "implemented").
#>
[CmdletBinding()]
param(
    [string]$EnvRoot = 'G:/CODEX/New Manga.workspace/task-envs/NS-RECLASSIFY-1',
    [string]$SpecPath = '',
    [string]$OutputPath = '',
    [switch]$IncludeHostControl
)
$ErrorActionPreference = 'Stop'
if (-not $SpecPath) { $SpecPath = Join-Path $EnvRoot 'scripts/probe_spec.json' }
if (-not $OutputPath) { $OutputPath = Join-Path $EnvRoot 'probe/probe-results.json' }
$sidecarDir = Join-Path $EnvRoot 'sidecar'
$core = Join-Path $sidecarDir 'core_service.exe'
if (-not (Test-Path $core)) { throw "core_service.exe not found: $sidecarDir" }
New-Item -ItemType Directory -Force -Path (Split-Path $OutputPath) | Out-Null

$spec = Get-Content $SpecPath -Raw | ConvertFrom-Json
$fixture = $spec.fixture

function Expand-Token($value) {
    if ($null -eq $value) { return $null }
    if ($value -is [string]) {
        switch ($value) {
            '@book_id' { return $fixture.book_id }
            '@chapter_id' { return $fixture.chapter_id }
            '@page_id' { return $fixture.page_id }
            '@page_id_2' { return $fixture.page_id_2 }
            '@backup_id' { return $script:lastBackupId }
            '@network_profile_id' { return $script:networkProfileId }
            '@provider_profile_id' { return $script:providerProfileId }
            '@run_id' { return $script:runId }
            default {
                $v = $value
                if ($v -like '*@*') {
                    $v = $v.Replace('@provider_profile_id', [string]$script:providerProfileId).Replace('@network_profile_id', [string]$script:networkProfileId).Replace('@run_id', [string]$script:runId).Replace('@backup_id', [string]$script:lastBackupId)
                }
                return $v
            }
        }
    }
    if ($value -is [System.Management.Automation.PSCustomObject]) {
        $o = [ordered]@{}
        foreach ($p in $value.PSObject.Properties) { $o[$p.Name] = Expand-Token $p.Value }
        return $o
    }
    if ($value -is [array]) { return @($value | ForEach-Object { Expand-Token $_ }) }
    return $value
}

function ConvertTo-AsciiJson([string]$json) {
    $sb = [System.Text.StringBuilder]::new()
    foreach ($ch in $json.ToCharArray()) {
        $code = [int]$ch
        if ($code -gt 127) { [void]$sb.AppendFormat('\u{0:x4}', $code) } else { [void]$sb.Append($ch) }
    }
    return $sb.ToString()
}

function Start-Core([string]$DataRoot) {
    $envRoot = Join-Path $DataRoot '_env'
    foreach ($sub in @('Roaming', 'Local', 'Temp')) { New-Item -ItemType Directory -Force -Path (Join-Path $envRoot $sub) | Out-Null }
    foreach ($sub in @('derived', 'catalog', 'managed')) { New-Item -ItemType Directory -Force -Path (Join-Path $DataRoot $sub) | Out-Null }
    $si = New-Object System.Diagnostics.ProcessStartInfo
    $si.FileName = $core
    $si.WorkingDirectory = $sidecarDir
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

function Send-Line([System.Diagnostics.Process]$Process, [string]$Line, [int]$TimeoutMs = 60000) {
    $Process.StandardInput.WriteLine($Line)
    $Process.StandardInput.Flush()
    # core_service mixes unsolicited event frames into stdout; skip them until a response arrives
    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMs)
    while ([DateTime]::UtcNow -lt $deadline) {
        $read = $Process.StandardOutput.ReadLineAsync()
        if (-not $read.Wait([Math]::Max(1000, $TimeoutMs))) { return $null }
        $raw = $read.Result
        if ($null -eq $raw) { return $null }
        if ($raw.Contains('"event_type"') -and -not $raw.Contains('"request_id"')) { continue }
        return $raw
    }
    return $null
}

function Invoke-CoreProbe {
    param(
        [System.Diagnostics.Process]$Process, [string]$Id, [string]$Name,
        [string]$CoreCommand, [int]$Minor, $Payload, [string]$DataRoot, [string]$Phase
    )
    $payloadJson = if ($null -eq $Payload) { '{}' } else { (ConvertTo-Json -InputObject $Payload -Depth 8 -Compress) }
    if ([string]::IsNullOrWhiteSpace($payloadJson)) { $payloadJson = '{}' }
    $req = ConvertTo-AsciiJson ('{"protocol":"new-manga.core","version":{"major":2,"minor":' + $Minor +
        '},"request_id":"' + $Id + '","command":"' + $CoreCommand + '","payload":' + $payloadJson + '}')
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $raw = Send-Line $Process $req
    $sw.Stop()
    $obj = $null
    try { $obj = $raw | ConvertFrom-Json } catch { }
    $errorCode = if ($obj -and $obj.error) { $obj.error.code } else { $null }
    $errorCategory = if ($obj -and $obj.error) { $obj.error.category } else { $null }
    $errorMessage = if ($obj -and $obj.error) { $obj.error.message } else { $null }
    $basis = if ($null -eq $obj) { 'no_response' }
             elseif ($null -eq $obj.error) { 'success' }
             elseif ($errorCode -eq 'UNKNOWN_COMMAND') { 'route_absent' }
             elseif ($errorCode -eq 'HOST_ONLY_REQUIRED') { 'host_control_required' }
             elseif ($errorCode -eq 'PROTOCOL_VERSION_UNSUPPORTED') { 'route_absent' }
             elseif ($errorCode -eq 'INVALID_REQUEST') { 'payload_rejected' }
             elseif ($errorCategory -eq 'not_found' -or $errorCategory -eq 'conflict') { 'domain_error_handler_ran' }
             elseif ($errorCode -like 'PROVIDER_*') { 'provider_missing' }
             else { 'other_error' }
    return [ordered]@{
        phase          = $Phase
        ns_command     = $Name
        core_command   = $CoreCommand
        minor          = $Minor
        request_payload = ($payloadJson | ConvertFrom-Json)
        data_root      = $DataRoot
        elapsed_ms     = [math]::Round($sw.Elapsed.TotalMilliseconds, 1)
        ok             = ($null -ne $obj -and $null -eq $obj.error)
        error_code     = $errorCode
        error_category = $errorCategory
        error_message  = $errorMessage
        basis          = $basis
        result         = if ($obj) { $obj.result } else { $null }
        response_raw   = $raw
    }
}

$script:probeId = 0
$script:lastBackupId = $null
$script:networkProfileId = $null
$script:providerProfileId = $null
$script:runId = $null
$results = @()
$phases = [ordered]@{}
$startedUtc = [DateTime]::UtcNow.ToString('o')

foreach ($phase in $spec.phases) {
    $dataRoot = if ($phase.data -eq 'fixture') { Join-Path $EnvRoot 'probe/data' }
                else { Join-Path ([IO.Path]::GetTempPath()) ('ns-rc-' + [guid]::NewGuid().ToString('N').Substring(0, 8)) }
    if ($phase.data -eq 'fixture') {
        # the BOOK-FIXTURE copy carries a preview-namespace lock bound to the *original*
        # derived root; the Core refuses to start on a copy until those bindings are gone.
        Get-ChildItem $dataRoot -Recurse -Force -File -Include '*.lock','*.run-owner*' -ErrorAction SilentlyContinue |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }
    Write-Output "phase=$($phase.name) root=$dataRoot"
    $phaseResults = @()
    $process = $null
    try {
        $process = Start-Core $dataRoot
        foreach ($p in $phase.probes) {
            $script:probeId++
            $payload = Expand-Token $p.payload
            $id = 'rc-{0:d3}' -f $script:probeId
            $r = Invoke-CoreProbe -Process $process -Id $id -Name $p.ns -CoreCommand $p.core -Minor $p.minor -Payload $payload -DataRoot $dataRoot -Phase $phase.name
            if ($p.ns -eq 'backup_create' -and $r.ok -and $r.result.backup_id) { $script:lastBackupId = $r.result.backup_id }
            if ($p.ns -eq 'settings_network_profiles_create' -and $r.ok -and $r.result.profile.network_profile_id) { $script:networkProfileId = $r.result.profile.network_profile_id }
            if ($p.ns -eq 'settings_provider_profiles_create' -and $r.ok -and $r.result.profile.profile_id) { $script:providerProfileId = $r.result.profile.profile_id }
            if ($p.ns -eq 'library_start_run' -and $r.ok -and $r.result.run_id) { $script:runId = $r.result.run_id }
            $phaseResults += $r
            Write-Output ("  {0,-40} {1,-32} ok={2,-5} code={3,-22} basis={4}" -f $p.ns, $p.core, $r.ok, $r.error_code, $r.basis)
        }
        if ($phase.name -eq 'fixture') {
            # the frozen binary's delete-face protocol minor may differ from HEAD source; sweep it
            # with a non-existent book_id so nothing is destroyed while identifying the minor
            foreach ($minor in 3..12) {
                $script:probeId++
                $r = Invoke-CoreProbe -Process $process -Id ('rc-{0:d3}' -f $script:probeId) -Name 'minor_sweep_PermanentlyDeleteBook' -CoreCommand 'PermanentlyDeleteBook' -Minor $minor -Payload @{ book_id = 'no-such-book'; confirm_permanent_delete = $true } -DataRoot $dataRoot -Phase 'fixture'
                Write-Output ("  delete minor={0,-3} code={1,-22} basis={2}" -f $minor, $r.error_code, $r.basis)
                $phaseResults += $r
            }
        }
        # discovery helpers that are already IMPLEMENTED in the registry (controls, not NS)
        $script:probeId++
        $ctrl = Invoke-CoreProbe -Process $process -Id ('rc-{0:d3}' -f $script:probeId) -Name 'control_list_regions' -CoreCommand 'list_regions' -Minor 3 -Payload @{ page_id = $fixture.page_id } -DataRoot $dataRoot -Phase $phase.name
        $phaseResults += $ctrl
        $script:regionsSnapshot = $ctrl.result
    } catch {
        Write-Output "  PHASE ERROR $($phase.name): $($_.Exception.Message)"
        $phaseResults += [ordered]@{ phase = $phase.name; ns_command = '<phase-error>'; ok = $false;
            error_code = 'PHASE_ERROR'; error_message = $_.Exception.Message; basis = 'phase_error' }
    } finally {
        if ($process) {
            try { $process.StandardInput.Close() } catch { }
            if (-not $process.WaitForExit(8000)) { try { $process.Kill($true) } catch { } }
        }
        try { $stderr = $script:stderrTask.Result } catch { $stderr = '' }
        $phases[$phase.name] = [ordered]@{ stderr = $stderr }
        $results += $phaseResults
        # incremental write: a later phase failure must never lose an earlier phase's evidence
        [ordered]@{ phase = $phase.name; data_root = $dataRoot; results = $phaseResults; stderr = $stderr } |
            ConvertTo-Json -Depth 12 | Set-Content (Join-Path (Split-Path $OutputPath) ("phase-{0}.json" -f $phase.name)) -Encoding utf8
    }
}

# ---------------- host-control phase: import / export faces ----------------
$hostResults = @()
if ($IncludeHostControl) {
    $dataRoot = Join-Path $EnvRoot 'probe/data'
    Remove-Item (Join-Path $dataRoot 'library.db.run-owner.lock') -ErrorAction SilentlyContinue
    Write-Output "phase=host-control root=$dataRoot"
    $process = Start-Core $dataRoot
    try {
        $cred = [Convert]::ToBase64String((1..32 | ForEach-Object { 7 })) -replace '\+', '-' -replace '/', '_' -replace '=', ''
        $script:probeId++
        $openReq = '{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"rc-host-1","channel":"host-control","command":"OpenHostSession","payload":{"host_session_id":"ns-rc-host","host_session_credential":"' + $cred + '"}}'
        $openRaw = Send-Line $process (ConvertTo-AsciiJson $openReq)
        $openObj = $null; try { $openObj = $openRaw | ConvertFrom-Json } catch { }
        $coreSessionId = if ($openObj -and $openObj.result) { $openObj.result.core_session_id } else { $null }
        $hostResults += [ordered]@{
            phase = 'host-control'; ns_command = 'control_open_host_session'; core_command = 'OpenHostSession'
            ok = ($null -ne $openObj -and $null -eq $openObj.error); error_code = if ($openObj -and $openObj.error) { $openObj.error.code } else { $null }
            error_category = if ($openObj -and $openObj.error) { $openObj.error.category } else { $null }
            result = if ($openObj) { $openObj.result } else { $null }; response_raw = $openRaw
            core_session_id = $coreSessionId
        }
        Write-Output ("  OpenHostSession ok={0} code={1} core_session_id={2}" -f ($null -ne $openObj -and $null -eq $openObj.error), $(if ($openObj -and $openObj.error) { $openObj.error.code } else { '-' }), $coreSessionId)

        function Send-HostControl([string]$Command, $Payload, [string]$Id) {
            $payloadJson = if ($null -eq $Payload) { '{}' } else { (ConvertTo-Json -InputObject $Payload -Depth 8 -Compress) }
            $req = '{"protocol":"new-manga.core","version":{"major":2,"minor":3},"request_id":"' + $Id + '","channel":"host-control","core_session_id":"' + $coreSessionId + '","host_session_id":"ns-rc-host","host_session_credential":"' + $cred + '","command":"' + $Command + '","payload":' + $payloadJson + '}'
            $raw = Send-Line $process (ConvertTo-AsciiJson $req)
            $obj = $null; try { $obj = $raw | ConvertFrom-Json } catch { }
            return [ordered]@{
                phase = 'host-control'; ns_command = $Command; core_command = $Command
                request_payload = ($payloadJson | ConvertFrom-Json); ok = ($null -ne $obj -and $null -eq $obj.error)
                error_code = if ($obj -and $obj.error) { $obj.error.code } else { $null }
                error_category = if ($obj -and $obj.error) { $obj.error.category } else { $null }
                error_message = if ($obj -and $obj.error) { $obj.error.message } else { $null }
                result = if ($obj) { $obj.result } else { $null }; response_raw = $raw
            }
        }

        if ($coreSessionId) {
            # RegisterImportSource needs a real source file the host can vouch for
            $srcFile = Join-Path $EnvRoot 'probe/import-source.jpg'
            if (-not (Test-Path $srcFile)) {
                Copy-Item (Join-Path $EnvRoot 'probe/data/managed/*.jpg') $srcFile -ErrorAction SilentlyContinue
            }
            $r1 = Send-HostControl 'RegisterImportSource' @{ paths = @($srcFile) } 'rc-host-2'
            $hostResults += $r1
            Write-Output ("  RegisterImportSource ok={0} code={1}" -f $r1.ok, $r1.error_code)
            if ($r1.ok -and $r1.result.grant_id) {
                $script:probeId++
                $r2 = Invoke-CoreProbe -Process $process -Id ('rc-{0:d3}' -f $script:probeId) -Name 'library_import_file' -CoreCommand 'ImportPages' -Minor 3 -Payload @{ chapter_id = $fixture.chapter_id; grant_id = $r1.result.grant_id; source_paths = @($srcFile) } -DataRoot $dataRoot -Phase 'host-control'
                $hostResults += $r2
                Write-Output ("  ImportPages ok={0} code={1} basis={2}" -f $r2.ok, $r2.error_code, $r2.basis)
            } else {
                $hostResults += [ordered]@{ phase = 'host-control'; ns_command = 'library_import_file'; core_command = 'ImportPages'; ok = $false; error_code = 'PRECONDITION_FAILED'; error_message = 'RegisterImportSource did not return a grant_id'; basis = 'blocked_precondition' }
            }
            # export faces
            $r3 = Send-HostControl 'RegisterExportTarget' @{ path = (Join-Path $EnvRoot 'probe/export-target') } 'rc-host-3'
            $hostResults += $r3
            Write-Output ("  RegisterExportTarget ok={0} code={1}" -f $r3.ok, $r3.error_code)
            if ($r3.ok -and $r3.result.grant_id) {
                $script:probeId++
                $r4 = Invoke-CoreProbe -Process $process -Id ('rc-{0:d3}' -f $script:probeId) -Name 'library_start_export' -CoreCommand 'StartExport' -Minor 3 -Payload @{ chapter_id = $fixture.chapter_id; grant_id = $r3.result.grant_id; output_dir = (Join-Path $EnvRoot 'probe/export-target') } -DataRoot $dataRoot -Phase 'host-control'
                $hostResults += $r4
                Write-Output ("  StartExport ok={0} code={1} basis={2}" -f $r4.ok, $r4.error_code, $r4.basis)
                $script:probeId++
                $r5 = Invoke-CoreProbe -Process $process -Id ('rc-{0:d3}' -f $script:probeId) -Name 'library_get_export_snapshot' -CoreCommand 'GetExportSnapshot' -Minor 3 -Payload @{ run_id = $(if ($r4.result) { $r4.result.run_id } else { 'no-such-run' }) } -DataRoot $dataRoot -Phase 'host-control'
                $hostResults += $r5
                Write-Output ("  GetExportSnapshot ok={0} code={1} basis={2}" -f $r5.ok, $r5.error_code, $r5.basis)
                $script:probeId++
                $r6 = Invoke-CoreProbe -Process $process -Id ('rc-{0:d3}' -f $script:probeId) -Name 'library_cancel_export' -CoreCommand 'CancelExport' -Minor 3 -Payload @{ run_id = $(if ($r4.result) { $r4.result.run_id } else { 'no-such-run' }) } -DataRoot $dataRoot -Phase 'host-control'
                $hostResults += $r6
                Write-Output ("  CancelExport ok={0} code={1} basis={2}" -f $r6.ok, $r6.error_code, $r6.basis)
            }
        }
    } finally {
        try { $process.StandardInput.Close() } catch { }
        if (-not $process.WaitForExit(8000)) { try { $process.Kill($true) } catch { } }
        try { $stderrHost = $script:stderrTask.Result } catch { $stderrHost = '' }
        $phases['host-control'] = [ordered]@{ stderr = $stderrHost }
    }
}

$finishedUtc = [DateTime]::UtcNow.ToString('o')
$payload = [ordered]@{
    ac                = 'AC1'
    sidecar           = $core
    sidecar_sha256    = (Get-FileHash $core -Algorithm SHA256).Hash.ToLowerInvariant()
    probe_spec        = $SpecPath
    probe_spec_sha256 = (Get-FileHash $SpecPath -Algorithm SHA256).Hash.ToLowerInvariant()
    fixture           = $fixture
    timestamps        = [ordered]@{ started_utc = $startedUtc; finished_utc = $finishedUtc }
    phases            = $phases
    results           = $results
    host_control      = $hostResults
}
$payload | ConvertTo-Json -Depth 12 | Set-Content $OutputPath -Encoding utf8
Write-Output ""
Write-Output "wrote $OutputPath  ($($results.Count) app-channel probes, $($hostResults.Count) host-control probes)"






