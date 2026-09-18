# TASK-054: suite runs in the recorded measurement standard.
# PowerShell + TASK-012-py312 venv + PYTHONDONTWRITEBYTECODE=1 + -p no:cacheprovider.
# QT_QPA_PLATFORM is cleared on purpose: the offscreen plugin makes two known
# false failures (font enumeration / pixel-size estimate) on this host.
param(
    [int]$Run = 1,
    [string]$Target = "",
    [string]$LogFile = ""
)
Set-Location "G:\CODEX\New Manga.worktrees\TASK-054-zcode"
$env:PYTHONDONTWRITEBYTECODE = "1"
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
$python = "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe"
$output = & $python -m pytest -q -rs -p no:cacheprovider $Target 2>&1
$exit = $LASTEXITCODE
$text = $output | Out-String
if ($LogFile -ne "") { Set-Content -Path $LogFile -Value $text -Encoding utf8 }
Write-Output "=== RUN $Run target=$Target ==="
Write-Output $text.Trim()
Write-Output "EXIT=$exit"
$line = ($text -split "`r?`n" | Where-Object { $_ -match "passed|failed|error" } | Select-Object -Last 1)
if ($null -ne $line) { Write-Output "SUMMARYLINE=$($line.Trim())" }
