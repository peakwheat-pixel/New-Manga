# test-artifact-lock-fault.ps1
# CBH-04 & CBH-05: Fault injection suite for artifact write errors, lock contention and metadata consistency.

param(
    [string]$TargetScript = "verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1"
)

$ErrorActionPreference = "Stop"

Write-Host "=== CBH-04 / CBH-05 Artifact Lock Fault Injection Suite ==="
$scriptPath = (Resolve-Path $TargetScript).Path
Write-Host "Target script: $scriptPath"

$testRoot = Join-Path $env:TEMP ("cbh04_test_" + [System.Guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null
Write-Host "Test scratch directory: $testRoot"

$allPassed = $true

function Assert-Condition {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) {
        Write-Host "[FAIL] $Message" -ForegroundColor Red
        $script:allPassed = $false
    } else {
        Write-Host "[PASS] $Message" -ForegroundColor Green
    }
}

try {
    # -------------------------------------------------------------
    # Case 1: Normal baseline artifact generation (MockExitCode = 0)
    # -------------------------------------------------------------
    Write-Host "`n--- Case 1: Baseline artifact write without lock contention ---"
    $outDir1 = Join-Path $testRoot "case1_normal"
    $proc1 = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-MockExitCode", "0", "-OutDir", "`"$outDir1`"" -PassThru -Wait
    
    Assert-Condition ($proc1.ExitCode -eq 0) "Process exited with code 0"
    $exitFile1 = Join-Path $outDir1 "ac5.exit"
    $consoleFile1 = Join-Path $outDir1 "ac5-console.log"
    $metaJson1 = Join-Path $outDir1 "ac5-metadata.json"
    
    Assert-Condition (Test-Path $exitFile1) "ac5.exit exists"
    $exitVal1 = (Get-Content $exitFile1 -Raw).Trim()
    Assert-Condition ($exitVal1 -eq "0") "ac5.exit content ($exitVal1) matches process exit code 0"
    Assert-Condition (Test-Path $consoleFile1) "ac5-console.log exists"
    Assert-Condition (Test-Path $metaJson1) "ac5-metadata.json exists"
    $jsonObj1 = Get-Content $metaJson1 -Raw | ConvertFrom-Json
    Assert-Condition ($jsonObj1.exit_code -eq 0) "Metadata exit_code equals 0"
    Assert-Condition ($jsonObj1.console_written -eq $true) "Metadata console_written is true"

    # -------------------------------------------------------------
    # Case 2: Console file locked (e.g. caller Tee-Object lock)
    # -------------------------------------------------------------
    Write-Host "`n--- Case 2: Console log locked with FileShare.None (Success simulation) ---"
    $outDir2 = Join-Path $testRoot "case2_console_lock"
    New-Item -ItemType Directory -Path $outDir2 -Force | Out-Null
    $lockedFile2 = Join-Path $outDir2 "ac5-console.log"
    
    # Open exclusive lock
    $fs2 = [System.IO.File]::Open($lockedFile2, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    Write-Host "Exclusive lock held on: $lockedFile2"
    
    try {
        $proc2 = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-MockExitCode", "0", "-OutDir", "`"$outDir2`"" -PassThru -Wait
    } finally {
        $fs2.Close()
        $fs2.Dispose()
        Write-Host "Exclusive lock released."
    }

    Assert-Condition ($proc2.ExitCode -eq 0) "Process exited with code 0 despite console log lock"
    $exitFile2 = Join-Path $outDir2 "ac5.exit"
    Assert-Condition (Test-Path $exitFile2) "ac5.exit exists"
    $exitVal2 = (Get-Content $exitFile2 -Raw).Trim()
    Assert-Condition ($exitVal2 -eq "0") "ac5.exit content matches process exit code 0"
    
    $metaJson2 = Join-Path $outDir2 "ac5-metadata.json"
    Assert-Condition (Test-Path $metaJson2) "ac5-metadata.json was written independently"
    $jsonObj2 = Get-Content $metaJson2 -Raw | ConvertFrom-Json
    Assert-Condition ($jsonObj2.exit_code -eq 0) "Metadata exit_code equals 0"
    Assert-Condition ($jsonObj2.console_written -eq $false) "Metadata console_written correctly reports false"
    Assert-Condition (-not [string]::IsNullOrEmpty($jsonObj2.console_warning)) "Metadata records console lock warning"
    
    $fallbackConsole2 = Join-Path $outDir2 "ac5-console-fallback.log"
    Assert-Condition (Test-Path $fallbackConsole2) "ac5-console-fallback.log was written"

    # -------------------------------------------------------------
    # Case 3: Console file locked with Failure exit code
    # -------------------------------------------------------------
    Write-Host "`n--- Case 3: Console log locked with Failure simulation (MockExitCode = 1) ---"
    $outDir3 = Join-Path $testRoot "case3_fail_console_lock"
    New-Item -ItemType Directory -Path $outDir3 -Force | Out-Null
    $lockedFile3 = Join-Path $outDir3 "ac5-console.log"
    
    $fs3 = [System.IO.File]::Open($lockedFile3, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    Write-Host "Exclusive lock held on: $lockedFile3"
    
    try {
        $proc3 = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-MockExitCode", "1", "-OutDir", "`"$outDir3`"" -PassThru -Wait
    } finally {
        $fs3.Close()
        $fs3.Dispose()
        Write-Host "Exclusive lock released."
    }

    Assert-Condition ($proc3.ExitCode -eq 1) "Process exited with code 1"
    $exitFile3 = Join-Path $outDir3 "ac5.exit"
    Assert-Condition (Test-Path $exitFile3) "ac5.exit exists"
    $exitVal3 = (Get-Content $exitFile3 -Raw).Trim()
    Assert-Condition ($exitVal3 -eq "1") "ac5.exit content matches process exit code 1"
    
    $metaJson3 = Join-Path $outDir3 "ac5-metadata.json"
    Assert-Condition (Test-Path $metaJson3) "ac5-metadata.json exists"
    $jsonObj3 = Get-Content $metaJson3 -Raw | ConvertFrom-Json
    Assert-Condition ($jsonObj3.exit_code -eq 1) "Metadata exit_code equals 1"

    # -------------------------------------------------------------
    # Case 4: Binary missing / execution failure path
    # -------------------------------------------------------------
    Write-Host "`n--- Case 4: Missing binary failure path with full artifact generation ---"
    $outDir4 = Join-Path $testRoot "case4_missing_binary"
    $bogusExe = Join-Path $testRoot "nonexistent_app.exe"
    $proc4 = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-AppExe", "`"$bogusExe`"", "-OutDir", "`"$outDir4`"" -PassThru -Wait
    
    Assert-Condition ($proc4.ExitCode -eq 1) "Process exited with code 1 on missing binary"
    $exitFile4 = Join-Path $outDir4 "ac5.exit"
    Assert-Condition (Test-Path $exitFile4) "ac5.exit exists"
    $exitVal4 = (Get-Content $exitFile4 -Raw).Trim()
    Assert-Condition ($exitVal4 -eq "1") "ac5.exit content matches process exit code 1"
    $metaJson4 = Join-Path $outDir4 "ac5-metadata.json"
    Assert-Condition (Test-Path $metaJson4) "ac5-metadata.json exists"
    $jsonObj4 = Get-Content $metaJson4 -Raw | ConvertFrom-Json
    Assert-Condition ($jsonObj4.exit_code -eq 1) "Metadata exit_code equals 1"

} finally {
    Remove-Item -Path $testRoot -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "`nTest scratch directory cleaned."
}

if ($allPassed) {
    Write-Host "`n=== ALL CBH-04/CBH-05 FAULT INJECTION TESTS PASSED ===" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n=== SOME TESTS FAILED ===" -ForegroundColor Red
    exit 1
}
