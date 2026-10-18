# test-artifact-lock-fault.ps1
# CBH-04 & CBH-05 (CBH-R1-03): Fault injection suite for artifact write errors, lock contention and metadata consistency.

param(
    [string]$TargetScript = "verification/P20-CLOSE-BOUND-1/run-desktop-close-verification.ps1",
    [string]$AppExe = ""
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
    $metaTxt1 = Join-Path $outDir1 "ac5-metadata.txt"
    
    Assert-Condition (Test-Path $exitFile1) "ac5.exit exists"
    $exitVal1 = (Get-Content $exitFile1 -Raw).Trim()
    Assert-Condition ($exitVal1 -eq "0") "ac5.exit content ($exitVal1) matches process exit code 0"
    Assert-Condition (Test-Path $consoleFile1) "ac5-console.log exists"
    Assert-Condition (Test-Path $metaJson1) "ac5-metadata.json exists"
    Assert-Condition (Test-Path $metaTxt1) "ac5-metadata.txt exists"
    $jsonObj1 = Get-Content $metaJson1 -Raw | ConvertFrom-Json
    Assert-Condition ($jsonObj1.exit_code -eq 0) "Metadata exit_code equals 0"
    Assert-Condition ($jsonObj1.console_written -eq $true) "Metadata console_written is true"
    Assert-Condition ($jsonObj1.exit_written -eq $true) "Metadata exit_written is true"
    Assert-Condition ($jsonObj1.metadata_txt_written -eq $true) "Metadata metadata_txt_written is true"

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
    Assert-Condition ($jsonObj2.console_fallback_written -eq $true) "Metadata console_fallback_written reports true"
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
    Assert-Condition ($jsonObj3.console_written -eq $false) "Metadata console_written reports false"
    Assert-Condition ($jsonObj3.console_fallback_written -eq $true) "Metadata console_fallback_written reports true"

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

    # -------------------------------------------------------------
    # Case 5: ac5.exit locked with FileShare.None (Fallback path test)
    # -------------------------------------------------------------
    Write-Host "`n--- Case 5: ac5.exit locked with FileShare.None (Fallback assertion) ---"
    $outDir5 = Join-Path $testRoot "case5_exit_lock"
    New-Item -ItemType Directory -Path $outDir5 -Force | Out-Null
    $lockedExit5 = Join-Path $outDir5 "ac5.exit"
    
    $fs5 = [System.IO.File]::Open($lockedExit5, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    Write-Host "Exclusive lock held on: $lockedExit5"
    
    try {
        $proc5 = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-MockExitCode", "0", "-OutDir", "`"$outDir5`"" -PassThru -Wait
    } finally {
        $fs5.Close()
        $fs5.Dispose()
        Write-Host "Exclusive lock on ac5.exit released."
    }

    Assert-Condition ($proc5.ExitCode -eq 0) "Process exited with code 0"
    $fallbackExit5 = Join-Path $outDir5 "ac5.exit-fallback"
    Assert-Condition (Test-Path $fallbackExit5) "ac5.exit-fallback exists"
    $fallbackVal5 = (Get-Content $fallbackExit5 -Raw).Trim()
    Assert-Condition ($fallbackVal5 -eq "0") "ac5.exit-fallback content ($fallbackVal5) matches exit code 0"
    
    $metaJson5 = Join-Path $outDir5 "ac5-metadata.json"
    Assert-Condition (Test-Path $metaJson5) "ac5-metadata.json exists"
    $jsonObj5 = Get-Content $metaJson5 -Raw | ConvertFrom-Json
    Assert-Condition ($jsonObj5.exit_written -eq $false) "Metadata exit_written is false"
    Assert-Condition ($jsonObj5.exit_fallback_written -eq $true) "Metadata exit_fallback_written is true"
    Assert-Condition (-not [string]::IsNullOrEmpty($jsonObj5.exit_warning)) "Metadata records exit_warning"

    # -------------------------------------------------------------
    # Case 6: ac5-metadata.json locked with FileShare.None
    # -------------------------------------------------------------
    Write-Host "`n--- Case 6: ac5-metadata.json locked with FileShare.None (Fallback assertion) ---"
    $outDir6 = Join-Path $testRoot "case6_json_lock"
    New-Item -ItemType Directory -Path $outDir6 -Force | Out-Null
    $lockedJson6 = Join-Path $outDir6 "ac5-metadata.json"
    
    $fs6 = [System.IO.File]::Open($lockedJson6, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    Write-Host "Exclusive lock held on: $lockedJson6"
    
    try {
        $proc6 = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-MockExitCode", "0", "-OutDir", "`"$outDir6`"" -PassThru -Wait
    } finally {
        $fs6.Close()
        $fs6.Dispose()
        Write-Host "Exclusive lock on ac5-metadata.json released."
    }

    Assert-Condition ($proc6.ExitCode -eq 0) "Process exited with code 0"
    $fallbackJson6 = Join-Path $outDir6 "ac5-metadata-fallback.json"
    Assert-Condition (Test-Path $fallbackJson6) "ac5-metadata-fallback.json exists"
    $jsonObj6 = Get-Content $fallbackJson6 -Raw | ConvertFrom-Json
    Assert-Condition ($jsonObj6.exit_code -eq 0) "Fallback metadata exit_code equals 0"
    Assert-Condition ($jsonObj6.exit_written -eq $true) "Fallback metadata exit_written is true"

    # -------------------------------------------------------------
    # Case 7: ac5-metadata.txt locked with FileShare.None
    # -------------------------------------------------------------
    Write-Host "`n--- Case 7: ac5-metadata.txt locked with FileShare.None (Fallback assertion) ---"
    $outDir7 = Join-Path $testRoot "case7_txt_lock"
    New-Item -ItemType Directory -Path $outDir7 -Force | Out-Null
    $lockedTxt7 = Join-Path $outDir7 "ac5-metadata.txt"
    
    $fs7 = [System.IO.File]::Open($lockedTxt7, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    Write-Host "Exclusive lock held on: $lockedTxt7"
    
    try {
        $proc7 = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-MockExitCode", "0", "-OutDir", "`"$outDir7`"" -PassThru -Wait
    } finally {
        $fs7.Close()
        $fs7.Dispose()
        Write-Host "Exclusive lock on ac5-metadata.txt released."
    }

    Assert-Condition ($proc7.ExitCode -eq 0) "Process exited with code 0"
    $fallbackTxt7 = Join-Path $outDir7 "ac5-metadata-fallback.txt"
    Assert-Condition (Test-Path $fallbackTxt7) "ac5-metadata-fallback.txt exists"
    $metaJson7 = Join-Path $outDir7 "ac5-metadata.json"
    $jsonObj7 = Get-Content $metaJson7 -Raw | ConvertFrom-Json
    Assert-Condition ($jsonObj7.metadata_txt_written -eq $false) "Metadata metadata_txt_written is false"
    Assert-Condition ($jsonObj7.metadata_txt_fallback_written -eq $true) "Metadata metadata_txt_fallback_written is true"
    Assert-Condition (-not [string]::IsNullOrEmpty($jsonObj7.metadata_txt_warning)) "Metadata records metadata_txt_warning"

    # -------------------------------------------------------------
    # Case 8: All artifacts simultaneously locked with FileShare.None
    # -------------------------------------------------------------
    Write-Host "`n--- Case 8: All 4 artifacts simultaneously locked (Extreme contention) ---"
    $outDir8 = Join-Path $testRoot "case8_all_locked"
    New-Item -ItemType Directory -Path $outDir8 -Force | Out-Null
    $lockedConsole8 = Join-Path $outDir8 "ac5-console.log"
    $lockedExit8 = Join-Path $outDir8 "ac5.exit"
    $lockedTxt8 = Join-Path $outDir8 "ac5-metadata.txt"
    $lockedJson8 = Join-Path $outDir8 "ac5-metadata.json"

    $fsc8 = [System.IO.File]::Open($lockedConsole8, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    $fse8 = [System.IO.File]::Open($lockedExit8, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    $fst8 = [System.IO.File]::Open($lockedTxt8, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    $fsj8 = [System.IO.File]::Open($lockedJson8, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)

    try {
        $proc8 = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-MockExitCode", "0", "-OutDir", "`"$outDir8`"" -PassThru -Wait
    } finally {
        $fsc8.Close(); $fsc8.Dispose()
        $fse8.Close(); $fse8.Dispose()
        $fst8.Close(); $fst8.Dispose()
        $fsj8.Close(); $fsj8.Dispose()
        Write-Host "All 4 locks released."
    }

    Assert-Condition ($proc8.ExitCode -eq 0) "Process exited with code 0 under extreme lock contention"
    Assert-Condition (Test-Path (Join-Path $outDir8 "ac5-console-fallback.log")) "ac5-console-fallback.log exists"
    Assert-Condition (Test-Path (Join-Path $outDir8 "ac5.exit-fallback")) "ac5.exit-fallback exists"
    Assert-Condition (Test-Path (Join-Path $outDir8 "ac5-metadata-fallback.txt")) "ac5-metadata-fallback.txt exists"
    Assert-Condition (Test-Path (Join-Path $outDir8 "ac5-metadata-fallback.json")) "ac5-metadata-fallback.json exists"
    $val8 = (Get-Content (Join-Path $outDir8 "ac5.exit-fallback") -Raw).Trim()
    Assert-Condition ($val8 -eq "0") "Fallback exit code matches 0 under extreme lock contention"

    # -------------------------------------------------------------
    # Case 9: Real binary launch path without MockExitCode
    # -------------------------------------------------------------
    Write-Host "`n--- Case 9: Real binary invocation lock test (Non-Mock execution) ---"
    $realBinary = if (-not [string]::IsNullOrEmpty($AppExe)) {
        $AppExe
    } elseif (Test-Path "apps/desktop/src-tauri/target/release/m2rc1-desktop.exe") {
        "apps/desktop/src-tauri/target/release/m2rc1-desktop.exe"
    } elseif (Test-Path "apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe") {
        "apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe"
    } else {
        $null
    }

    if ($realBinary) {
        Write-Host "Using real desktop binary: $realBinary"
        $outDir9 = Join-Path $testRoot "case9_real_binary"
        New-Item -ItemType Directory -Path $outDir9 -Force | Out-Null
        $lockedConsole9 = Join-Path $outDir9 "ac5-console.log"
        $fs9 = [System.IO.File]::Open($lockedConsole9, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        
        try {
            # Run without -MockExitCode against real binary
            $proc9 = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-AppExe", "`"$realBinary`"", "-OutDir", "`"$outDir9`"" -PassThru -Wait
        } finally {
            $fs9.Close()
            $fs9.Dispose()
        }

        # Assert artifacts were properly created even if app fails (e.g. headless window init 0x80070578)
        $metaJson9 = Join-Path $outDir9 "ac5-metadata.json"
        Assert-Condition (Test-Path $metaJson9) "ac5-metadata.json exists for real binary launch"
        $exitFile9 = Join-Path $outDir9 "ac5.exit"
        Assert-Condition (Test-Path $exitFile9) "ac5.exit exists for real binary launch"
        $jsonObj9 = Get-Content $metaJson9 -Raw | ConvertFrom-Json
        $actualExit9 = (Get-Content $exitFile9 -Raw).Trim()
        Assert-Condition ($jsonObj9.exit_code.ToString() -eq $actualExit9) "ac5.exit matches metadata exit_code ($actualExit9) for real binary"
        Assert-Condition ($jsonObj9.console_fallback_written -eq $true) "ac5-console-fallback.log written for real binary under console lock"
    } else {
        Write-Host "Skipping Case 9 (no real binary found in workspace)"
    }

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
