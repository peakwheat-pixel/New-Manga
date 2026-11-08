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
# STATUS 2026-11-08: NOT RUN. The two-phase design below is implemented, but the
# AC's literal kill (entireProcessTree:true) also kills the Python Core, and the Core
# keeps source-read grants ONLY in process memory
# (src/infrastructure/resource_channel/source_read_refs.py::SourceReadGrantRegistry).
# C-17 §5.2:258 / runtime.py::_verify_fresh re-resolve every CompletionRequest
# grant_id, so a NEW process cannot re-verify the fresh authorization for an
# operation whose apply-time grant died with the Core (typed SOURCE_GRANT_EXPIRED),
# and dropping grant_ids would be the security relaxation C-17 §5.2:258 / §5.3:276 forbids.
# This is a CROSS-CARD blocker (Core grant durability or a Host-only kill with an
# externally supervised Core) — reported to DSH, NOT worked around here.
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
$park = Start-Process -FilePath 'dotnet' -PassThru -NoNewWindow -ArgumentList @(
    'test', $testProject, '-c', 'Release', '--nologo',
    '--filter', 'FullyQualifiedName~Fea11HostAuthIpcTests.CrashPoint_Park'
)

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

# Real external kill of the whole tree (frozen AC wording: entireProcessTree).
try {
    [System.Diagnostics.Process]::GetProcessById($park.Id).Kill($true)
}
catch {
    Write-Host ("CRASH_POINT=FAIL reason=kill_failed " + $_.Exception.Message)
    exit 11
}
$killDeadline = (Get-Date).AddSeconds(30)
while (-not $park.HasExited -and (Get-Date) -lt $killDeadline) {
    Start-Sleep -Milliseconds 100
    $park.Refresh()
}
if (-not $park.HasExited) {
    Write-Host 'CRASH_POINT=FAIL reason=child_still_alive'
    exit 11
}
Write-Host 'CRASH_POINT phase=kill killed=1'

# Phase 2: a NEW process reads the journal / registry / Core DB and recovers once.
$env:NEWMANGA_FEA11_CRASH_PHASE = 'recover'
& dotnet test $testProject -c Release --nologo `
    --filter 'FullyQualifiedName~Fea11HostAuthIpcTests.CrashPoint_Recover'
$recoverExit = $LASTEXITCODE

$resultFile = Join-Path $statePath 'recover.json'
if ($recoverExit -ne 0 -or -not (Test-Path $resultFile)) {
    Write-Host ("CRASH_POINT=NOT_SATISFIED recover_exit=$recoverExit" +
                ' reason=see recover.json / test output (expected blocker: grant not durable across Core restart)')
    exit 12
}
$recoverState = Get-Content $resultFile -Raw | ConvertFrom-Json
if ($recoverState.commit_digest -ne $parkState.commit_digest) {
    Write-Host 'CRASH_POINT=FAIL reason=commit_digest_drift'
    exit 12
}
Write-Host ("CRASH_POINT=PASS acknowledge_once=1 gates_open=1 rows_unchanged=1"
            + " second_call_idempotent=1 commit_digest_match=1")
exit 0
