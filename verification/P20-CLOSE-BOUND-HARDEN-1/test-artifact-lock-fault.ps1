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
    Assert-Condition ($jsonObj5.exit_code.ToString() -eq $fallbackVal5) "Metadata exit_code ($($jsonObj5.exit_code)) matches fallback exit value ($fallbackVal5)"
    Assert-Condition ($jsonObj5.exit_code -eq $proc5.ExitCode) "Metadata exit_code ($($jsonObj5.exit_code)) matches process ExitCode ($($proc5.ExitCode))"

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

    $primaryExit6 = Join-Path $outDir6 "ac5.exit"
    Assert-Condition (Test-Path $primaryExit6) "Primary ac5.exit exists"
    $primaryExitVal6 = (Get-Content $primaryExit6 -Raw).Trim()
    Assert-Condition ($primaryExitVal6 -eq "0") "Primary ac5.exit content equals 0"
    Assert-Condition ($jsonObj6.exit_code.ToString() -eq $primaryExitVal6) "Fallback metadata exit_code ($($jsonObj6.exit_code)) matches primary ac5.exit ($primaryExitVal6)"
    Assert-Condition ($jsonObj6.exit_code -eq $proc6.ExitCode) "Fallback metadata exit_code matches process ExitCode ($($proc6.ExitCode))"

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

    $primaryExit7 = Join-Path $outDir7 "ac5.exit"
    Assert-Condition (Test-Path $primaryExit7) "Primary ac5.exit exists"
    $primaryExitVal7 = (Get-Content $primaryExit7 -Raw).Trim()
    Assert-Condition ($jsonObj7.exit_code.ToString() -eq $primaryExitVal7) "Metadata exit_code ($($jsonObj7.exit_code)) matches primary ac5.exit ($primaryExitVal7)"
    Assert-Condition ($jsonObj7.exit_code -eq $proc7.ExitCode) "Metadata exit_code matches process ExitCode ($($proc7.ExitCode))"

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
    $jsonObj8 = Get-Content (Join-Path $outDir8 "ac5-metadata-fallback.json") -Raw | ConvertFrom-Json
    Assert-Condition ($jsonObj8.exit_code.ToString() -eq $val8) "Fallback metadata exit_code ($($jsonObj8.exit_code)) matches fallback exit ($val8)"
    Assert-Condition ($jsonObj8.exit_code -eq $proc8.ExitCode) "Fallback metadata exit_code matches process ExitCode ($($proc8.ExitCode))"

    # -------------------------------------------------------------
    # Case 9: Real binary launch path under various artifact locks (Non-Mock execution)
    # -------------------------------------------------------------
    Write-Host "`n--- Case 9: Real binary invocation lock suite (Non-Mock execution) ---"
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

        # Case 9a: Console log locked with real binary
        Write-Host "`n--- Case 9a: Console log locked with real binary ---"
        $outDir9a = Join-Path $testRoot "case9a_real_console_lock"
        New-Item -ItemType Directory -Path $outDir9a -Force | Out-Null
        $lockedConsole9a = Join-Path $outDir9a "ac5-console.log"
        $fs9a = [System.IO.File]::Open($lockedConsole9a, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        try {
            $proc9a = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-AppExe", "`"$realBinary`"", "-OutDir", "`"$outDir9a`"" -PassThru -Wait
        } finally {
            $fs9a.Close(); $fs9a.Dispose()
        }
        $metaJson9a = Join-Path $outDir9a "ac5-metadata.json"
        Assert-Condition (Test-Path $metaJson9a) "ac5-metadata.json exists for Case 9a"
        $exitFile9a = Join-Path $outDir9a "ac5.exit"
        Assert-Condition (Test-Path $exitFile9a) "ac5.exit exists for Case 9a"
        $jsonObj9a = Get-Content $metaJson9a -Raw | ConvertFrom-Json
        $actualExit9a = (Get-Content $exitFile9a -Raw).Trim()
        Assert-Condition ($jsonObj9a.exit_code.ToString() -eq $actualExit9a) "Case 9a: ac5.exit ($actualExit9a) matches metadata exit_code ($($jsonObj9a.exit_code))"
        Assert-Condition ($jsonObj9a.exit_code -eq $proc9a.ExitCode) "Case 9a: metadata exit_code matches process ExitCode ($($proc9a.ExitCode))"
        Assert-Condition ($jsonObj9a.console_fallback_written -eq $true) "Case 9a: ac5-console-fallback.log written under console lock"

        # Case 9b: ac5.exit locked with real binary (Fallback exit assertion)
        Write-Host "`n--- Case 9b: ac5.exit locked with real binary (Fallback path) ---"
        $outDir9b = Join-Path $testRoot "case9b_real_exit_lock"
        New-Item -ItemType Directory -Path $outDir9b -Force | Out-Null
        $lockedExit9b = Join-Path $outDir9b "ac5.exit"
        $fs9b = [System.IO.File]::Open($lockedExit9b, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        try {
            $proc9b = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-AppExe", "`"$realBinary`"", "-OutDir", "`"$outDir9b`"" -PassThru -Wait
        } finally {
            $fs9b.Close(); $fs9b.Dispose()
        }
        $fallbackExit9b = Join-Path $outDir9b "ac5.exit-fallback"
        Assert-Condition (Test-Path $fallbackExit9b) "ac5.exit-fallback exists for Case 9b"
        $metaJson9b = Join-Path $outDir9b "ac5-metadata.json"
        Assert-Condition (Test-Path $metaJson9b) "ac5-metadata.json exists for Case 9b"
        $jsonObj9b = Get-Content $metaJson9b -Raw | ConvertFrom-Json
        $actualFallbackExit9b = (Get-Content $fallbackExit9b -Raw).Trim()
        Assert-Condition ($jsonObj9b.exit_code.ToString() -eq $actualFallbackExit9b) "Case 9b: ac5.exit-fallback ($actualFallbackExit9b) matches metadata exit_code ($($jsonObj9b.exit_code))"
        Assert-Condition ($jsonObj9b.exit_code -eq $proc9b.ExitCode) "Case 9b: metadata exit_code matches process ExitCode ($($proc9b.ExitCode))"
        Assert-Condition ($jsonObj9b.exit_written -eq $false) "Case 9b: metadata reports exit_written is false"
        Assert-Condition ($jsonObj9b.exit_fallback_written -eq $true) "Case 9b: metadata reports exit_fallback_written is true"

        # Case 9c: ac5-metadata.json locked with real binary (Fallback metadata assertion)
        Write-Host "`n--- Case 9c: ac5-metadata.json locked with real binary (Fallback metadata) ---"
        $outDir9c = Join-Path $testRoot "case9c_real_metadata_lock"
        New-Item -ItemType Directory -Path $outDir9c -Force | Out-Null
        $lockedJson9c = Join-Path $outDir9c "ac5-metadata.json"
        $fs9c = [System.IO.File]::Open($lockedJson9c, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        try {
            $proc9c = Start-Process -FilePath "pwsh" -ArgumentList "-NoProfile", "-File", "`"$scriptPath`"", "-AppExe", "`"$realBinary`"", "-OutDir", "`"$outDir9c`"" -PassThru -Wait
        } finally {
            $fs9c.Close(); $fs9c.Dispose()
        }
        $primaryExit9c = Join-Path $outDir9c "ac5.exit"
        Assert-Condition (Test-Path $primaryExit9c) "ac5.exit exists for Case 9c"
        $fallbackJson9c = Join-Path $outDir9c "ac5-metadata-fallback.json"
        Assert-Condition (Test-Path $fallbackJson9c) "ac5-metadata-fallback.json exists for Case 9c"
        $jsonObj9c = Get-Content $fallbackJson9c -Raw | ConvertFrom-Json
        $actualExit9c = (Get-Content $primaryExit9c -Raw).Trim()
        Assert-Condition ($jsonObj9c.exit_code.ToString() -eq $actualExit9c) "Case 9c: ac5.exit ($actualExit9c) matches fallback metadata exit_code ($($jsonObj9c.exit_code))"
        Assert-Condition ($jsonObj9c.exit_code -eq $proc9c.ExitCode) "Case 9c: fallback metadata exit_code matches process ExitCode ($($proc9c.ExitCode))"
        Assert-Condition ($jsonObj9c.exit_written -eq $true) "Case 9c: fallback metadata reports exit_written is true"
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
