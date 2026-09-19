# POSTHOC-WINDOW-2026-09-19 Qoder review: suite runner in the brief's口径.
# PowerShell + TASK-012-py312 venv + PYTHONDONTWRITEBYTECODE=1 + -p no:cacheprovider
# + QT_QPA_PLATFORM cleared (offscreen makes two known false failures on this host).
param(
    [int]$Run = 1,
    [string]$Target = "",
    [string]$LogFile = ""
)

Set-Location "G:\CODEX\New Manga.worktrees\POSTHOC-WINDOW-2026-09-19-qoder"
$env:PYTHONDONTWRITEBYTECODE = "1"
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
$python = "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe"

$collection = & $python -m pytest --collect-only -q -p no:cacheprovider $Target 2>&1 | Out-String
$collectedLine = ($collection -split "`r?`n" | Where-Object { $_ -match "tests collected|error" } | Select-Object -Last 1)

$output = & $python -m pytest -q -rs -p no:cacheprovider $Target 2>&1
$exit = $LASTEXITCODE
$text = $output | Out-String
if ($LogFile -ne "") {
  Set-Content -Path $LogFile -Value $text -Encoding utf8
  Add-Content -Path $LogFile -Value "COLLECTED=$($collectedLine.Trim())"
  Add-Content -Path $LogFile -Value "EXIT=$exit"
}
Write-Output "=== RUN $Run target=[$Target] ==="
Write-Output $text.Trim()
Write-Output "COLLECTED=$($collectedLine.Trim())"
Write-Output "EXIT=$exit"
