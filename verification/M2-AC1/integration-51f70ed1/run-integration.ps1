$ErrorActionPreference = 'Continue'
$env:PYTHONUTF8 = '1'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
Set-Location -LiteralPath $repoRoot

$python = 'G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe'
$cargo = (Get-Command cargo).Source
$npm = (Get-Command npm).Source
$head = (& git rev-parse HEAD).Trim()

function Invoke-LoggedCommand {
    param(
        [string]$Name,
        [string]$Executable,
        [string[]]$Arguments,
        [string]$CommandText
    )
    $logPath = Join-Path $PSScriptRoot "$Name.log"
    @(
        "# shell: PowerShell $($PSVersionTable.PSVersion)"
        "# worktree: $repoRoot"
        "# worktree HEAD: $head"
        "# PYTHONUTF8: $env:PYTHONUTF8"
        "# executable: $Executable"
        "# command: $CommandText"
    ) | Set-Content -LiteralPath $logPath -Encoding utf8
    & $Executable @Arguments *>> $logPath
    $exitCode = $LASTEXITCODE
    Add-Content -LiteralPath $logPath -Value "# EXIT: $exitCode" -Encoding utf8
    Write-Host "$Name EXIT=$exitCode"
    return $exitCode
}

if (-not (Test-Path -LiteralPath $python)) { throw "Missing project Python: $python" }
@(
    "# project Python: $python"
    "# Python: $(& $python --version 2>&1)"
    "# Cargo: $(& $cargo --version 2>&1)"
    "# Node: $(& node --version 2>&1)"
    "# npm: $(& $npm --version 2>&1)"
) | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'environment.txt') -Encoding utf8

$install = Invoke-LoggedCommand 'npm-ci' $npm @('ci', '--prefix', 'apps/desktop/frontend') 'npm ci --prefix apps/desktop/frontend'
$frontendBuild = Invoke-LoggedCommand 'frontend-build' $npm @('run', 'build', '--prefix', 'apps/desktop/frontend') 'npm run build --prefix apps/desktop/frontend'
$core = Invoke-LoggedCommand 'pytest-m2-acceptance' $python @('-m', 'pytest', 'tests/m2_acceptance', '-q') 'python -m pytest tests/m2_acceptance -q'
$tauri = Invoke-LoggedCommand 'cargo-test' $cargo @('test', '--manifest-path', 'apps/desktop/src-tauri/Cargo.toml', '--locked') 'cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked'
$react = Invoke-LoggedCommand 'vitest' $npm @('test', '--prefix', 'apps/desktop/frontend', '--', '--run') 'npm test --prefix apps/desktop/frontend -- --run'
$e2e = Invoke-LoggedCommand 'e2e-command' $python @('verification/M2-AC1/run_e2e.py') 'python verification/M2-AC1/run_e2e.py'

$e2eLog = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'e2e-command.log') -Raw
$match = [regex]::Match($e2eLog, 'GATE (?:PASS|FAIL|BLOCKED)\s+evidence:\s*(.+)')
if ($match.Success -and (Test-Path -LiteralPath $match.Groups[1].Value.Trim())) {
    Copy-Item -LiteralPath $match.Groups[1].Value.Trim() -Destination (Join-Path $PSScriptRoot 'e2e-artifacts') -Recurse
} else {
    Add-Content -LiteralPath (Join-Path $PSScriptRoot 'e2e-command.log') -Value '# artifact copy: BLOCKED (runner did not report an evidence directory)' -Encoding utf8
}

$full = Invoke-LoggedCommand 'pytest-full-suite' $python @('-m', 'pytest', '-q', '-p', 'no:cacheprovider', '-rs') 'python -m pytest -q -p no:cacheprovider -rs'
@(
    "core acceptance EXIT=$core"
    "npm ci EXIT=$install"
    "frontend build EXIT=$frontendBuild"
    "Tauri regression EXIT=$tauri"
    "React regression EXIT=$react"
    "M2 E2E gate EXIT=$e2e"
    "Full suite EXIT=$full"
) | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'summary.txt') -Encoding utf8

if ($install -ne 0 -or $frontendBuild -ne 0 -or $core -ne 0 -or $tauri -ne 0 -or $react -ne 0 -or $e2e -ne 0) { exit 1 }
exit 0
