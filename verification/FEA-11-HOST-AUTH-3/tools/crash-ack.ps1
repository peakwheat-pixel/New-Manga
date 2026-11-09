# FEA-11-HOST-AUTH-2 AC-F3 crash-point driver (SKELETON — NOT RUN this round)
#
# C-17 §3.3 crash row: "Host 收 Core receipt 前后、Host ACK 落盘前 | Core pending gate；
# Host 未确认 | 读仍拒绝，重读 Core receipt 后核对 Registry/授权".
#
# Frozen AC-F3 shape: a REAL child process is killed after the Host journal reaches
# `core-committed` (external driver + `Process.Kill(entireProcessTree:true)`; NO
# Environment.FailFast, NO same-process second coordinator); a NEW process then reads
# the journal / registry / Core DB and recovers or ACKs exactly once, every gate opens,
# `page_bindings` / `source_binding_publications` row counts do not change, a second
# call is idempotent and `commit_digest` matches.
#
# ---------------------------------------------------------------------------
# STATUS 2026-11-09 (FEA-11-HOST-AUTH-3): the blocker recorded in the HOST-AUTH-2
# skeleton is RESOLVED by C-17 v1.2 (additive read-only `source_get_sync_plan_materialized`,
# frozen `cdeee487…`, 18/18 pins). A new process can now read back the persisted plan
# subset, re-mint a fresh source-read grant from the registry's single readable root and
# ACK exactly once. The two-phase driver below is READY, but it depends on the gated
# tests `CrashPoint_Park` / `CrashPoint_Recover` in Fea11HostAuthIpcTests, which are NOT
# implemented yet -> this driver currently reports NOT_RUN (never PASS).
#
# The known error code for "grant is not registered in the NEW Core" is
# SOURCE_ACCESS_DENIED ("source-read grant is not registered"), NOT SOURCE_GRANT_EXPIRED.
# ---------------------------------------------------------------------------
#
# Usage (once unblocked):
#   pwsh -NoProfile -File verification/FEA-11-HOST-AUTH-2/tools/crash-ack.ps1
# Env:
#   NEWMANGA_FEA11_IPC=1                (required; real isolated Python Core)
#   NEWMANGA_BUILD_PYTHON              (optional; default C:/Python314/python.exe)
# Exit codes:
#   0  = crash point satisfied (park -> kill -> recover -> idempotent)
#   10 = park phase did not reach core-committed
#   11 = kill was not proven (child still alive)
#   12 = recovery refused (typed) -> crash point NOT satisfied
#   2  = environment/fixture missing (never a silent skip)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$fixtureRoot = Join-Path ($repo + '.workspace') 'FEA-11\fixtures'
$statePath = Join-Path $fixtureRoot ('host-auth-crash-' + [guid]::NewGuid().ToString('N'))

if ($env:NEWMANGA_FEA11_IPC -ne '1') {
    Write-Host 'CRASH_POINT=NOT_RUN reason=NEWMANGA_FEA11_IPC_not_1'
    exit 2
}

New-Item -ItemType Directory -Force -Path $statePath | Out-Null
$parkFile = Join-Path $statePath 'park.json'
$releaseFile = Join-Path $statePath 'release'
$testProject = Join-Path $repo 'apps\desktop-avalonia\tests\NewManga.Host.Tests\NewManga.Host.Tests.csproj'

Write-Host "CRASH_POINT phase=park state=$statePath"

# Phase 1 (+2): the two env-gated facts are NOT IMPLEMENTED yet (planned names: CrashPoint_Park/CrashPoint_Recover); this script is a SKELETON carried by FEA-11-HOST-AUTH-3
# (NEWMANGA_FEA11_CRASH_PHASE=park|recover). `park` drives the REAL chain to
# journal=core-committed, writes park.json ({data_root, operation_id,
# commit_digest, grant_ids, page_id}) and then blocks on $releaseFile so the kill
# below is not a self-inflicted in-process shutdown.
$env:NEWMANGA_FEA11_CRASH_PHASE = 'park'
$env:NEWMANGA_FEA11_CRASH_STATE = $statePath
$parkArgs = @(
    'test', ('"' + $testProject + '"'), '-c', 'Release', '--nologo',
    '--filter', 'FullyQualifiedName~Fea11HostAuthIpcTests.CrashPoint_Park'
)
$park = Start-Process -FilePath 'dotnet' -PassThru -NoNewWindow -ArgumentList $parkArgs

$deadline = (Get-Date).AddMinutes(5)
while (-not (Test-Path $parkFile) -and (Get-Date) -lt $deadline -and -not $park.HasExited) {
    Start-Sleep -Milliseconds 200
}
if (-not (Test-Path $parkFile)) {
    Write-Host 'CRASH_POINT=FAIL reason=park_did_not_reach_core_committed'
    exit 10
}

$parkState = Get-Content $parkFile -Raw | ConvertFrom-Json
Write-Host ("CRASH_POINT park journal_state=" + $parkState.journal_state +
            " operation_id=" + $parkState.operation_id +
            " commit_digest=" + $parkState.commit_digest)
if ($parkState.journal_state -ne 'core-committed') {
    Write-Host 'CRASH_POINT=FAIL reason=journal_not_core_committed'
    exit 10
}

# --- P0 fix: enumerate the park process tree so the Python sidecar death is PROVEN. ---
function Get-DescendantPids([int]$RootId) {
    $all = Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name
    $result = @()
    $frontier = @($RootId)
    while ($frontier.Count -gt 0) {
        $next = @()
        foreach ($parent in $frontier) {
            $children = $all | Where-Object { $_.ParentProcessId -eq $parent }
            foreach ($child in $children) {
                if ($result -notcontains $child.ProcessId) {
                    $result += $child.ProcessId
                    $next += $child.ProcessId
                }
            }
        }
        $frontier = $next
    }
    return $result
}

$treePids = @(Get-DescendantPids $park.Id)
$pythonPids = @($treePids | Where-Object {
    $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $_" -ErrorAction SilentlyContinue
    $proc -and $proc.Name -match 'python'
})
$treePids | ForEach-Object { "PID_TREE $_" } | Out-File -FilePath (Join-Path $statePath 'pids-before.txt') -Encoding utf8
"PYTHON_PIDS $($pythonPids -join ',')" | Out-File -FilePath (Join-Path $statePath 'pids-before.txt') -Append -Encoding utf8
if ($pythonPids.Count -eq 0) {
    Write-Host 'CRASH_POINT=FAIL reason=no_python_sidecar_pid_found'
    exit 11
}
Write-Host ("CRASH_POINT pids tree=" + $treePids.Count + " python=" + $pythonPids.Count)

# Real external kill of the whole tree (frozen AC wording: entireProcessTree).
try {
    [System.Diagnostics.Process]::GetProcessById($park.Id).Kill($true)
}
catch {
    Write-Host ("CRASH_POINT=FAIL reason=kill_failed " + $_.Exception.Message)
    exit 11
}

# 30s polling: EVERY enumerated pid (dotnet + Python sidecar) must be gone.
$deadline = (Get-Date).AddSeconds(30)
$alive = @($treePids)
while ($alive.Count -gt 0 -and (Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 200
    $alive = @($treePids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue })
}
$alive | ForEach-Object { "PID_ALIVE_AFTER_KILL $_" } | Out-File -FilePath (Join-Path $statePath 'pids-after.txt') -Encoding utf8
if ($alive.Count -gt 0) {
    Write-Host ("CRASH_POINT=FAIL reason=tree_still_alive pids=" + ($alive -join ','))
    exit 11
}
Write-Host 'CRASH_POINT phase=kill killed=1 sidecar_proven_dead=1'

# Phase 2: a NEW process reads the journal / registry / Core DB and recovers once.
$env:NEWMANGA_FEA11_CRASH_PHASE = 'recover'
& dotnet test $testProject -c Release --nologo `
    --filter 'FullyQualifiedName~Fea11HostAuthIpcTests.CrashPoint_Recover'
$recoverExit = $LASTEXITCODE

$resultFile = Join-Path $statePath 'recover.json'
if ($recoverExit -ne 0 -or -not (Test-Path $resultFile)) {
    Write-Host ("CRASH_POINT=NOT_SATISFIED recover_exit=$recoverExit" +
                ' reason=see recover.json / test output')
    exit 12
}
$recoverState = Get-Content $resultFile -Raw | ConvertFrom-Json
$parkState = Get-Content $parkFile -Raw | ConvertFrom-Json

# --- P0 fix: every PASS field is COMPUTED from the recorded facts, never hard-coded. ---
$checks = [ordered]@{}
$checks['commit_digest_match'] = ($recoverState.commit_digest -eq $parkState.commit_digest)
$checks['distinct_host_pid'] = ($recoverState.host_pid -ne $parkState.host_pid)
$checks['distinct_core_session'] = ($recoverState.core_session_id -ne $parkState.core_session_id)
$checks['source_sha256_unchanged'] = ($recoverState.source_sha256 -eq $parkState.source_sha256)
$checks['rows_unchanged'] = (
    ($recoverState.db_counts.bindings -eq $parkState.db_counts.bindings) -and
    ($recoverState.db_counts.publications -eq $parkState.db_counts.publications)
)
$checks['gates_open'] = ($recoverState.gate_open -eq $true)
$checks['second_call_idempotent'] = (
    ($recoverState.second_call -eq 'recovered') -and
    ([int]$recoverState.second_call_frames -eq 0)
)
$journalGrants = @($parkState.grant_ids)
$freshGrant = $true
foreach ($grant in @($recoverState.grant_ids)) {
    if ($journalGrants -contains $grant) { $freshGrant = $false }
}
$checks['fresh_grant'] = $freshGrant

$failed = @()
foreach ($name in $checks.Keys) {
    $ok = $checks[$name]
    Write-Host ("CHECK " + $name + "=" + ($(if ($ok) { 1 } else { 0 })))
    if (-not $ok) { $failed += $name }
}
if ($failed.Count -gt 0) {
    Write-Host ("CRASH_POINT=FAIL reason=" + ($failed -join ','))
    exit 12
}

# --- R-r1-05: archive the complete crash evidence under verification/ (frozen AC). ---
$runId = Split-Path $statePath -Leaf
$archive = Join-Path $repo ("verification" + [IO.Path]::DirectorySeparatorChar + "FEA-11-HOST-AUTH-3" + [IO.Path]::DirectorySeparatorChar + "crash" + [IO.Path]::DirectorySeparatorChar + $runId)
New-Item -ItemType Directory -Force -Path $archive | Out-Null
Copy-Item $parkFile (Join-Path $archive 'park.json') -Force
Copy-Item $resultFile (Join-Path $archive 'recover.json') -Force
foreach ($name in @('pids-before.txt', 'pids-after.txt')) {
    $source = Join-Path $statePath $name
    if (Test-Path $source) { Copy-Item $source (Join-Path $archive $name) -Force }
}
$dataRoot = $parkState.data_root
if (Test-Path $dataRoot) {
    Copy-Item (Join-Path $dataRoot 'library.db') (Join-Path $archive 'library.db') -Force -ErrorAction SilentlyContinue
    if (Test-Path (Join-Path $dataRoot 'wire.ndjson')) {
        Copy-Item (Join-Path $dataRoot 'wire.ndjson') (Join-Path $archive 'wire-redacted.ndjson') -Force
    }
}
Write-Host ("CRASH_EVIDENCE archived=" + $archive)

$passMessage = "CRASH_POINT=PASS acknowledge_once=1" `
    + " gates_open=" + $checks['gates_open'] `
    + " rows_unchanged=" + $checks['rows_unchanged'] `
    + " second_call_idempotent=" + $checks['second_call_idempotent'] `
    + " commit_digest_match=" + $checks['commit_digest_match'] `
    + " distinct_host_pid=" + $checks['distinct_host_pid'] `
    + " distinct_core_session=" + $checks['distinct_core_session'] `
    + " fresh_grant=" + $checks['fresh_grant'] `
    + " source_sha256_unchanged=" + $checks['source_sha256_unchanged'] `
    + " sidecar_proven_dead=1"
Write-Host $passMessage
exit 0
