# TASK-061 review (Qoder, non-author): probe runner, same 口径 as run.ps1
# (PowerShell + TASK-012-py312 venv + PYTHONDONTWRITEBYTECODE=1, QT_QPA_PLATFORM cleared).
param(
    [Parameter(Mandatory = $true)][string]$Root,
    [Parameter(Mandatory = $true)][string]$Probe,
    [string]$LogFile = "",
    [string]$Label = "",
    [string]$Tail = ""
)

Set-Location $Root
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
$python = "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe"
$pyVer = & $python -c "import sys,platform;print(sys.version.replace(chr(10),' ')+' | '+platform.python_implementation()+' '+platform.machine())"
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
    "PYTHONIOENCODING=$env:PYTHONIOENCODING"
    "QT_QPA_PLATFORM=$offscreen"
    "CMD=$python $Probe $Root $Tail"
    "----------------------------------------"
)

$output = & $python $Probe $Root $Tail 2>&1
$exit = $LASTEXITCODE
$text = $output | Out-String

if ($LogFile -ne "") {
  Set-Content -Path $LogFile -Value ($header -join "`r`n") -Encoding utf8
  Add-Content -Path $LogFile -Value $text
  Add-Content -Path $LogFile -Value "EXIT=$exit"
  Add-Content -Path $LogFile -Value "HEAD=$head"
}
Write-Output $text.Trim()
Write-Output "EXIT=$exit"
