param(
    [Parameter(Mandatory = $true)][string]$Label,
    [Parameter(Mandatory = $true)][string]$Target,
    [Parameter(Mandatory = $true)][string]$LogFile
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$targets = @($Target -split '\s+' | Where-Object { $_ })
$python = "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe"

Set-Location $root
$env:PYTHONPATH = "src"
$env:PYTHONDONTWRITEBYTECODE = "1"
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue

$head = (& git rev-parse HEAD).Trim()
$treeState = (& git status --short | Out-String).Trim()
$pythonVersion = (& $python --version 2>&1 | Out-String).Trim()
$shellVersion = $PSVersionTable.PSVersion.ToString()
$collectCommand = "$python -m pytest $Target --collect-only -q -p no:cacheprovider"
$testCommand = "$python -m pytest $Target -q -p no:cacheprovider -rs"

@(
    "TASK=T1.3.2 / TASK-065"
    "LABEL=$Label"
    "WORKTREE=$root"
    "HEAD=$head"
    "TREE_STATE_BEGIN"
    $treeState
    "TREE_STATE_END"
    "SHELL=PowerShell $shellVersion"
    "VENV=$python"
    "PYTHON=$pythonVersion"
    "PYTHONPATH=src"
    "PYTHONDONTWRITEBYTECODE=1"
    "QT_QPA_PLATFORM=<unset>"
    "COLLECT_COMMAND=$collectCommand"
) | Set-Content -LiteralPath $LogFile -Encoding utf8

$collection = & $python -m pytest @targets --collect-only -q -p no:cacheprovider 2>&1
$collectExit = $LASTEXITCODE
$collection | Add-Content -LiteralPath $LogFile -Encoding utf8
"COLLECT_EXIT=$collectExit" | Add-Content -LiteralPath $LogFile -Encoding utf8
"TEST_COMMAND=$testCommand" | Add-Content -LiteralPath $LogFile -Encoding utf8

$output = & $python -m pytest @targets -q -p no:cacheprovider -rs 2>&1
$exitCode = $LASTEXITCODE
$output | Add-Content -LiteralPath $LogFile -Encoding utf8
"EXIT=$exitCode" | Add-Content -LiteralPath $LogFile -Encoding utf8

$output
Write-Output "EXIT=$exitCode"
exit $exitCode
