# M2-S2 probe suite runner (mirrors the M2-S1 run_all.ps1 pattern).
#
# Runs the isolated security-verification probes against the temporary lab
# directory, saving every raw log next to this script's ../raw/ folder.
#
#   pwsh -NoProfile -File verification/M2-S2/probes/run_all.ps1

$ErrorActionPreference = "Stop"
$repoRoot = (Get-Item (Join-Path $PSCommandPath "..\..\..\..")).FullName
$probes = Join-Path $repoRoot "verification\M2-S2\probes"
$raw = Join-Path $repoRoot "verification\M2-S2\raw"
New-Item -ItemType Directory -Force -Path $raw | Out-Null

$lab = Join-Path $env:TEMP "m2s2-lab"

function Run-Step([string]$Name, [string[]]$Command, [string]$Log) {
    Write-Host "=== $Name ==="
    & $Command[0] $Command[1..($Command.Length - 1)] 2>&1 | Tee-Object -FilePath (Join-Path $raw $Log)
    Write-Host "--- $Name exit=$LASTEXITCODE"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "!!! step $Name exited with $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

# script identity (sha256) so a reviewer can pin what was run
Get-ChildItem $probes -Filter *.py | Get-FileHash -Algorithm SHA256 |
    Format-Table -AutoSize |
    Out-String -Width 200 |
    Tee-Object -FilePath (Join-Path $raw "01-script-hashes.log")

# environment snapshot
$envLines = @(
    "python: $(python --version 2>&1)",
    "python exe: $((python -c "import sys; print(sys.executable)"))",
    "OS: $([System.Environment]::OSVersion.VersionString)",
    "host: $env:COMPUTERNAME user: $env:USERNAME",
    "lab: $lab"
)
$envLines | Tee-Object -FilePath (Join-Path $raw "02-environment.log")
$envLines | ForEach-Object { Write-Host $_ }

# first run
Run-Step "make fixtures" @("python", (Join-Path $probes "make_fixtures.py"), "--lab", $lab) "03-make-fixtures.log"
Run-Step "probe S2-TOCTOU (first run)" @("python", (Join-Path $probes "probe_s2_toctou.py"), "--lab", $lab, "--out", (Join-Path $lab "toctou-result.json")) "04-toctou-first.log"
Run-Step "probe S2-MAPPING (first run)" @("python", (Join-Path $probes "probe_s2_mapping.py"), "--lab", $lab, "--out", (Join-Path $lab "mapping-result.json")) "05-mapping-first.log"

# copy first-run results aside for the consistency check
Copy-Item (Join-Path $lab "toctou-result.json") (Join-Path $lab "toctou-first.json") -Force
Copy-Item (Join-Path $lab "mapping-result.json") (Join-Path $lab "mapping-first.json") -Force

# repeat run (lab and result files already exist -- probes must be re-entrant)
Run-Step "make fixtures (repeat)" @("python", (Join-Path $probes "make_fixtures.py"), "--lab", $lab) "06-make-fixtures-repeat.log"
Run-Step "probe S2-TOCTOU (repeat)" @("python", (Join-Path $probes "probe_s2_toctou.py"), "--lab", $lab, "--out", (Join-Path $lab "toctou-result.json")) "07-toctou-repeat.log"
Run-Step "probe S2-MAPPING (repeat)" @("python", (Join-Path $probes "probe_s2_mapping.py"), "--lab", $lab, "--out", (Join-Path $lab "mapping-result.json")) "08-mapping-repeat.log"

# repeatability comparison
Run-Step "repeat consistency" @("python", (Join-Path $probes "compare_runs.py"), "--first-dir", $lab, "--repeat-dir", $lab, "--out", (Join-Path $raw "09-repeat-consistency.json")) "09-repeat-consistency.log"

# archive the first-run result JSONs next to the logs
Copy-Item (Join-Path $lab "toctou-first.json") (Join-Path $raw "toctou-result.json") -Force
Copy-Item (Join-Path $lab "mapping-first.json") (Join-Path $raw "mapping-result.json") -Force

Write-Host "=== all steps finished ==="
exit 0
