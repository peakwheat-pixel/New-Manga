# M2-S1 probe runner.
#
# Regenerates the synthetic fixtures in an isolated lab directory under
# %TEMP%, then runs every probe once. Each probe's exact command, stdout and
# exit code are written to verification/M2-S1/raw/<probe>.log; this script's
# own transcript (headers, commands, exit codes, input hashes) is what the
# caller tees into verification/M2-S1/raw/00-run-all.log.
#
# Large fixture bytes stay in the lab directory; only hashes, result JSON and
# logs are kept in the repository.
#
# Run:
#   pwsh -NoProfile -File verification/M2-S1/probes/run_all.ps1 `
#     | Tee-Object -FilePath verification/M2-S1/raw/00-run-all.log
#
# Optional:
#   -Lab <dir>        lab directory (default: %TEMP%\m2s1-lab)
#   -SkipFixtures     reuse existing fixtures instead of regenerating them
#
# No product code, no user library, no network, no physical-memory exhaustion.

param(
    [string]$Lab = (Join-Path $env:TEMP 'm2s1-lab'),
    [switch]$SkipFixtures
)

$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location $repo
$raw = Join-Path $repo 'verification\M2-S1\raw'
New-Item -ItemType Directory -Force -Path $raw, $Lab | Out-Null

$script:ProbeExit = -1

function Write-Header([string]$text) {
    Write-Output ''
    Write-Output ("#" * 78)
    Write-Output ("# " + $text)
    Write-Output ("#" * 78)
}

function Invoke-Probe([string]$name, [string[]]$argv) {
    $log = Join-Path $raw $name
    Write-Output ("`$ " + ($argv -join ' '))
    $output = @(& $argv[0] @($argv[1..($argv.Count - 1)]) 2>&1 | ForEach-Object { "$_" })
    $code = $LASTEXITCODE
    $output | Set-Content -Path $log -Encoding utf8
    Add-Content -Path $log -Value ("exit_code=" + $code) -Encoding utf8
    $script:ProbeExit = [int]$code
    Write-Output ("    log=verification/M2-S1/raw/{0} lines={1} exit_code={2}" -f $name, $output.Count, $code)
}

Write-Header 'M2-S1 probe run'
Write-Output ("repo        = " + $repo)
Write-Output ("lab         = " + $Lab)
Write-Output ("started_utc = " + [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))
Write-Output ("pwsh        = " + $PSVersionTable.PSVersion)
Write-Output ("python      = " + (& python --version))
Write-Output ("python_exe  = " + (Get-Command python).Source)
Write-Output ("media_limit = 67108864 bytes (64 MiB, probe configuration only)")

Write-Header 'P-00 probe script hashes (input identity)'
$hashes = Get-ChildItem (Join-Path $repo 'verification\M2-S1\probes') -File |
    Sort-Object Name |
    ForEach-Object {
        "{0}  {1}" -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower(), $_.Name
    }
$hashes | ForEach-Object { Write-Output $_ }
$hashes | Set-Content -Path (Join-Path $raw '01-probe-script-hashes.log') -Encoding utf8

Write-Header 'P-01 host environment'
Invoke-Probe '02-host-memory-and-environment.log' @('python', (Join-Path $PSScriptRoot '00_meminfo.py'))

if (-not $SkipFixtures) {
    Write-Header 'P-02 generate synthetic fixtures'
    Invoke-Probe '03-fixture-generation.log' @(
        'python', (Join-Path $PSScriptRoot 'make_fixtures.py'), '--lab', $Lab
    )
} else {
    Write-Header 'P-02 fixture generation skipped (-SkipFixtures)'
}

$fixtureManifest = Join-Path $Lab 'fixtures\fixtures.json'
if (Test-Path $fixtureManifest) {
    Copy-Item $fixtureManifest (Join-Path $raw 'fixtures.json') -Force
} else {
    Write-Output "WARNING: fixture manifest missing at $fixtureManifest"
}

$probes = @(
    @{ Log = '10-probe-A-capability-token.log'; Script = 'probe_a_token.py';      Out = 'probeA-result.json' },
    @{ Log = '11-probe-B-streaming-pipe.log';   Script = 'probe_b_stream.py';     Out = 'probeB-result.json' },
    @{ Log = '12-probe-C-windows-section.log';  Script = 'probe_c_section.py';    Out = 'probeC-result.json' },
    @{ Log = '13-probe-D-base64-control.log';   Script = 'probe_d_base64.py';     Out = 'probeD-result.json' },
    @{ Log = '14-probe-E-concurrency.log';      Script = 'probe_e_concurrency.py'; Out = 'probeE-result.json' }
)

Write-Header 'P-03 route probes'
$codes = [ordered]@{}
foreach ($probe in $probes) {
    $out = Join-Path $Lab $probe.Out
    Invoke-Probe $probe.Log @('python', (Join-Path $PSScriptRoot $probe.Script), '--lab', $Lab, '--out', $out)
    $codes[$probe.Out] = $script:ProbeExit
}

Write-Header 'P-04 collect result JSON (sha256 of the collected evidence)'
foreach ($probe in $probes) {
    $source = Join-Path $Lab $probe.Out
    if (Test-Path $source) {
        Copy-Item $source (Join-Path $raw $probe.Out) -Force
        "{0}  {1}  exit_code={2}" -f (Get-FileHash $source -Algorithm SHA256).Hash.ToLower(), $probe.Out, $codes[$probe.Out] |
            ForEach-Object { Write-Output $_ }
    } else {
        Write-Output ("MISSING {0} exit_code={1}" -f $probe.Out, $codes[$probe.Out])
    }
}

Write-Header 'P-05 exit-code summary'
$codes.GetEnumerator() | ForEach-Object { Write-Output ("{0} exit_code={1}" -f $_.Key, $_.Value) }
Write-Output ("all_zero = " + (@($codes.Values | Where-Object { $_ -ne 0 }).Count -eq 0))
Write-Output ("finished_utc = " + [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'))
