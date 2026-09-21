param([Parameter(Mandatory = $true)][string]$LogFile)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$python = "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe"
$probe = Join-Path $root "verification\TASK-057\review-29546f7\t057_chokepoint_probe.py"

Set-Location $root
$env:PYTHONPATH = "src"
$env:PYTHONDONTWRITEBYTECODE = "1"
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue

@(
    "TASK=T1.3.1 / TASK-057"
    "LABEL=reviewer-chokepoint-probe"
    "WORKTREE=$root"
    "HEAD=$((& git rev-parse HEAD).Trim())"
    "SOURCE_TREE_STATE_BEGIN"
    ((& git status --short -- src tests doc | Out-String).Trim())
    "SOURCE_TREE_STATE_END"
    "SHELL=PowerShell $($PSVersionTable.PSVersion)"
    "VENV=$python"
    "PYTHON=$(& $python --version 2>&1)"
    "PYTHONPATH=src"
    "PYTHONDONTWRITEBYTECODE=1"
    "QT_QPA_PLATFORM=<unset>"
    "COMMAND=$python $probe $root"
) | Set-Content -LiteralPath $LogFile -Encoding utf8

$output = & $python $probe $root 2>&1
$exitCode = $LASTEXITCODE
$output | Add-Content -LiteralPath $LogFile -Encoding utf8
"EXIT=$exitCode" | Add-Content -LiteralPath $LogFile -Encoding utf8

$output
Write-Output "EXIT=$exitCode"
exit $exitCode
