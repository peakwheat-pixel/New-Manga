# TASK-061 review (Qoder, non-author): suite runner in the brief's 口径.
# PowerShell + TASK-012-py312 venv + PYTHONDONTWRITEBYTECODE=1 + -p no:cacheprovider
# + QT_QPA_PLATFORM explicitly cleared (offscreen causes 2 known false failures here).
# Every log carries the shell/venv header and an EXIT code (protocol §6.12 / Q-009).
param(
    [Parameter(Mandatory = $true)][string]$Root,
    [string]$Target = "",
    [string]$Extra = "",
    [string]$LogFile = "",
    [string]$Label = ""
)

$targets = @($Target -split '\s+' | Where-Object { $_ -ne "" })
$extras = @($Extra -split '\s+' | Where-Object { $_ -ne "" })

Set-Location $Root
$env:PYTHONDONTWRITEBYTECODE = "1"
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
$python = "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe"
$pyVer = & $python -c "import sys,platform;print(sys.version.replace(chr(10),' ')+
' | '+platform.python_implementation()+' '+platform.machine())"
$head = (& git -C $Root rev-parse HEAD)
$offscreen = if (Test-Path Env:QT_QPA_PLATFORM) { Env:QT_QPA_PLATFORM.Value } else { "<unset>" }

$header = @(
    "LABEL=$Label"
    "ROOT=$Root"
    "HEAD=$head"
    "SHELL=PowerShell $($PSVersionTable.PSVersion) (powershell.exe -NoProfile)"
    "VENV=$python"
    "PYTHON=$pyVer"
    "PYTHONDONTWRITEBYTECODE=$env:PYTHONDONTWRITEBYTECODE"
    "QT_QPA_PLATFORM=$offscreen"
    "PYTEST=python -m pytest -q -rs -p no:cacheprovider $(($targets + $extras) -join ' ')"
    "----------------------------------------"
)

$collection = & $python -m pytest --collect-only -q -p no:cacheprovider @targets 2>&1 | Out-String
$collectedLine = ($collection -split "`r?`n" | Where-Object { $_ -match "tests collected|no tests ran|error" } | Select-Object -Last 1)
if ($null -eq $collectedLine) { $collectedLine = "n/a" }

$output = & $python -m pytest -q -rs -p no:cacheprovider @targets @extras 2>&1
$exit = $LASTEXITCODE
$text = $output | Out-String

if ($LogFile -ne "") {
  Set-Content -Path $LogFile -Value ($header -join "`r`n") -Encoding utf8
  Add-Content -Path $LogFile -Value $text
  Add-Content -Path $LogFile -Value "COLLECTED=$($collectedLine.Trim())"
  Add-Content -Path $LogFile -Value "EXIT=$exit"
  Add-Content -Path $LogFile -Value "HEAD=$head"
}
Write-Output "=== [$Label] root=$Root target=[$($targets -join ' ')] extra=[$($extras -join ' ')] ==="
Write-Output $text.Trim()
Write-Output "COLLECTED=$($collectedLine.Trim())"
Write-Output "EXIT=$exit"
