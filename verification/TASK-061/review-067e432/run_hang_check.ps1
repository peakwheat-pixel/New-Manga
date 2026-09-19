# TASK-061 review (Qoder, non-author): run a pytest command under a hard wall-clock
# budget and record whether it TERMINATED.  Used to document the pre-fix hang:
# a test that fails by stranding a non-daemon worker thread produces a summary but
# never an exit code, so the "EXIT=" discipline cannot be satisfied by the run itself.
param(
    [Parameter(Mandatory = $true)][string]$Root,
    [Parameter(Mandatory = $true)][string]$Target,
    [int]$BudgetSeconds = 45,
    [string]$LogFile = "",
    [string]$Label = ""
)

$env:PYTHONDONTWRITEBYTECODE = "1"
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
$python = "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe"
$pyVer = & $python -c "import sys,platform;print(sys.version.replace(chr(10),' ')+' | '+platform.python_implementation()+' '+platform.machine())"
$head = (& git -C $Root rev-parse HEAD)
$args = @("-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider") + ($Target -split '\s+' | Where-Object { $_ -ne "" })

$outFile = "$env:TEMP\t061-hang-$Label.out.txt"
$errFile = "$env:TEMP\t061-hang-$Label.err.txt"
$proc = Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $Root `
    -NoNewWindow -PassThru -RedirectStandardOutput $outFile -RedirectStandardError $errFile
# ExitCode on a Start-Process -PassThru object is only populated if the object
# was subscribed to the exit event before the process ended.
$proc.EnableRaisingEvents = $true
$waited = Wait-Process -Id $proc.Id -Timeout $BudgetSeconds -ErrorAction SilentlyContinue
$exited = $proc.HasExited
if ($exited) {
    # ExitCode is only populated once the Process object has cached the exit
    # event; Wait-Process alone does not do that.
    $proc.WaitForExit()
    $code = $proc.ExitCode
} else {
    $code = "never (killed after $BudgetSeconds s)"
}
if ($exited) {
    $verdict = "TERMINATED with exit code $code"
} else {
    Stop-Process -Id $proc.Id -Force
    Start-Sleep -Milliseconds 500
    $verdict = "HUNG: still running after $BudgetSeconds s, killed. The summary line (if any) was printed, but the interpreter never left threading._shutdown()."
}
$body = Get-Content $outFile -Raw -ErrorAction SilentlyContinue
$errb = Get-Content $errFile -Raw -ErrorAction SilentlyContinue

$lines = @(
    "LABEL=$Label"
    "ROOT=$Root"
    "HEAD=$head"
    "SHELL=PowerShell $($PSVersionTable.PSVersion) (powershell.exe -NoProfile)"
    "VENV=$python"
    "PYTHON=$pyVer"
    "PYTHONDONTWRITEBYTECODE=1"
    "QT_QPA_PLATFORM=<unset>"
    "CMD=python $($args -join ' ')"
    "BUDGET_SECONDS=$BudgetSeconds"
    "----------------------------------------"
    "$($body.Trim())"
    "----------------------------------------stderr"
    "$($errb.Trim())"
    "========================================verdict"
    "$verdict"
    "TERMINATED=$exited"
    "EXIT=$code"
    "HEAD=$head"
)
if ($LogFile -ne "") { Set-Content -Path $LogFile -Value ($lines -join "`r`n") -Encoding utf8 }
Write-Output ($lines -join "`r`n")
