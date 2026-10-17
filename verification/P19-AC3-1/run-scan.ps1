$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$evidence = (Resolve-Path $PSScriptRoot).Path
$raw = Join-Path $evidence 'raw'
New-Item -ItemType Directory -Force -Path $raw | Out-Null
$scanOut = Join-Path $raw 'scan.stdout.txt'
$scanErr = Join-Path $raw 'scan.stderr.txt'
$scanExit = Join-Path $raw 'scan.exit-code.txt'
$reproOut = Join-Path $raw 'settings-path-roundtrip.stdout.txt'
$reproErr = Join-Path $raw 'settings-path-roundtrip.stderr.txt'
$reproExit = Join-Path $raw 'settings-path-roundtrip.exit-code.txt'
$python = (Get-Command python).Source
$pythonVersion = (& $python --version 2>&1 | Out-String).Trim()
$metadata = @(
    "shell=PowerShell $($PSVersionTable.PSVersion)",
    "python=$pythonVersion",
    "python_executable=$python",
    "working_directory=$root",
    "scan_command=python verification/P19-AC3-1/scan_surface.py",
    "repro_command=python verification/P19-AC3-1/repro_settings_path_roundtrip.py",
    "scan_scope=read-only product source; writes limited to verification/P19-AC3-1",
    "repro_data_root=verification/P19-AC3-1/scratch (temporary database; auto-removed)"
)
$metadata | Set-Content -LiteralPath (Join-Path $raw 'run-metadata.txt') -Encoding utf8

Push-Location $root
try {
    & $python 'verification/P19-AC3-1/scan_surface.py' 2> $scanErr | Out-Null
    $scanCode = $LASTEXITCODE
    $scanCode | Set-Content -LiteralPath $scanExit -Encoding ascii
    if ($scanCode -ne 0) { throw "scan_surface.py exited $scanCode" }

    & $python 'verification/P19-AC3-1/repro_settings_path_roundtrip.py' 1> $reproOut 2> $reproErr
    $reproCode = $LASTEXITCODE
    $reproCode | Set-Content -LiteralPath $reproExit -Encoding ascii
    if ($reproCode -ne 0) { throw "repro_settings_path_roundtrip.py exited $reproCode" }

    Write-Output "SCAN_EXIT=$scanCode REPRO_EXIT=$reproCode"
    Write-Output "RAW=$raw"
} finally {
    Pop-Location
}
