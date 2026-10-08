param(
    [Parameter(Mandatory=$true)]
    [string]$CommandText,
    [Parameter(Mandatory=$true)]
    [string]$LogRelativePath,
    [string]$WorkingDirectory = $PWD.Path
)

$logFull = Join-Path $PWD.Path $LogRelativePath
$logDir = Split-Path $logFull -Parent
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

$psVer = $PSVersionTable.PSVersion.ToString()
$startTime = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")

$header = @"
=== Traceability Execution Record ===
Shell: PowerShell $psVer
WorkingDirectory: $WorkingDirectory
Command: $CommandText
StartTime: $startTime
=====================================
"@

$header | Out-File -FilePath $logFull -Encoding utf8
Write-Output $header

Push-Location $WorkingDirectory
try {
    Invoke-Expression "$CommandText *>&1" | Tee-Object -FilePath $logFull -Append
    $cmdExit = $LASTEXITCODE
    if ($null -eq $cmdExit) { $cmdExit = 0 }
} finally {
    Pop-Location
}

$endTime = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
$footer = @"
=====================================
EndTime: $endTime
EXIT=$cmdExit
=====================================
"@

$footer | Out-File -FilePath $logFull -Append -Encoding utf8
Write-Output $footer

exit $cmdExit
