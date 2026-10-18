# run-desktop-close-verification.ps1
# P20-CLOSE-BOUND-1 AC5: Real Interactive Desktop Window Close & Process Tree Verification Script
# NOTE: This script is intended to be run by the Coordinator in an interactive Windows desktop session
# with fully functional WebView2 runtime. Non-interactive agent sessions lack desktop GUI interaction (0x80070578).

param(
    [string]$AppExe = "apps/desktop/src-tauri/target/release/m2rc1-desktop.exe",
    [string]$AppArgs = "",
    [string]$SidecarDir = "resources/core-sidecar",
    [int]$HardBoundSeconds = 5,
    [string]$OutDir = "",
    [Nullable[int]]$MockExitCode = $null
)

$ErrorActionPreference = "Stop"

# Determine and create OutDir self-contained
$resolvedOutDir = if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $timestampSuffix = Get-Date -Format "yyyyMMdd-HHmmss"
    Join-Path $PSScriptRoot "ac5-$timestampSuffix"
} else {
    if ([System.IO.Path]::IsPathRooted($OutDir)) {
        $OutDir
    } else {
        Join-Path (Get-Location).Path $OutDir
    }
}
if (-not (Test-Path $resolvedOutDir)) {
    New-Item -ItemType Directory -Path $resolvedOutDir -Force | Out-Null
}

$logLines = [System.Collections.Generic.List[string]]::new()
function Write-Log {
    param([string]$Message, [string]$ForegroundColor = "")
    $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz"
    $line = "[$ts] $Message"
    $logLines.Add($line)
    if ($ForegroundColor) {
        Write-Host $line -ForegroundColor $ForegroundColor
    } else {
        Write-Host $line
    }
}

$scriptExitCode = 0
$appExitCode = $null
$startTime = Get-Date
$startIso = $startTime.ToString("yyyy-MM-ddTHH:mm:ss.fffffffzzz")
$releaseHash = "none"
$gitHead = "unknown"
try {
    $gitHead = (git rev-parse HEAD 2>$null).Trim()
} catch {}

Write-Log "=== P20-CLOSE-BOUND-1 AC5 Interactive Desktop Verification ==="
Write-Log "Output Directory: $resolvedOutDir"

# 1. Setup isolated data roots under $env:TEMP (strict isolation guarantee)
$isolatedId = [System.Guid]::NewGuid().ToString("N").Substring(0, 8)
$isolatedRoot = Join-Path $env:TEMP "p20close-$isolatedId"
$dataRoot = Join-Path $isolatedRoot "data"
$derivedRoot = Join-Path $isolatedRoot "derived"
$catalogDb = Join-Path $isolatedRoot "catalog/catalog.sqlite"

try {
    New-Item -ItemType Directory -Path $dataRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $derivedRoot -Force | Out-Null
    New-Item -ItemType Directory -Path (Split-Path $catalogDb) -Force | Out-Null

    Write-Log "Isolated root prepared at: $isolatedRoot"

    if ($null -ne $MockExitCode) {
        Write-Log "MOCK EXECUTION: Simulating desktop run with exit code: $MockExitCode"
        $scriptExitCode = [int]$MockExitCode
        $appExitCode = [int]$MockExitCode
        Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
        return
    }

    # 2. Set environment variables for isolated execution
    $env:NEWMANGA_DATA_ROOT = $dataRoot
    $env:M2RC1_DERIVED_ROOT = $derivedRoot
    $env:M2RC2_CATALOG_DB = $catalogDb
    $env:M2RC1_MANAGED_ROOT = Join-Path $isolatedRoot "managed"
    New-Item -ItemType Directory -Path $env:M2RC1_MANAGED_ROOT -Force | Out-Null

    # Verify binary existence
    if (-not (Test-Path $AppExe) -and ($AppExe -eq "apps/desktop/src-tauri/target/release/m2rc1-desktop.exe")) {
        # Check debug binary if default release not found
        $AppExe = "apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe"
    }
    $resolvedExe = $null
    if (Test-Path $AppExe) {
        $resolvedExe = (Resolve-Path $AppExe).Path
    } else {
        $cmd = Get-Command $AppExe -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source) {
            $resolvedExe = $cmd.Source
        }
    }
    if (-not $resolvedExe) {
        Write-Log "Could not find desktop binary at: $AppExe. Please build the desktop app first." -ForegroundColor Red
        $scriptExitCode = 1
        return
    } else {
        Write-Log "Launching desktop application: $resolvedExe"
        try {
            $releaseHash = (Get-FileHash $resolvedExe -Algorithm SHA256).Hash.ToLower()
        } catch {}

        $pinfo = New-Object System.Diagnostics.ProcessStartInfo
        $pinfo.FileName = $resolvedExe
        if (-not [string]::IsNullOrEmpty($AppArgs)) {
            $pinfo.Arguments = $AppArgs
        }
        $pinfo.UseShellExecute = $false
        $pinfo.RedirectStandardOutput = $true
        $pinfo.RedirectStandardError = $true
        $pinfo.CreateNoWindow = $false

        $proc = New-Object System.Diagnostics.Process
        $proc.StartInfo = $pinfo
        $proc.Start() | Out-Null
        $appPid = $proc.Id

        Write-Log "App launched with PID: $appPid. Waiting for window initialization and sidecar spawn (up to 15s)..."

        $sidecarPids = @()
        $foundWindow = $false
        $pollStart = Get-Date

        while (($null -eq $foundWindow -or -not $foundWindow) -and ((Get-Date) - $pollStart).TotalSeconds -lt 15) {
            $proc.Refresh()
            if ($proc.HasExited) {
                Write-Log "Process exited during initialization polling (PID=$appPid)"
                break
            }
            Start-Sleep -Milliseconds 500
            
            # Query process tree
            $children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $appPid }
            if ($children) {
                $sidecarPids = $children | ForEach-Object { $_.ProcessId }
            }
            
            # Check main window handle
            $proc.Refresh()
            if ($proc.MainWindowHandle -ne 0) {
                $foundWindow = $true
                Write-Log "Main window detected! Handle: $($proc.MainWindowHandle)"
                break
            }
        }

        Write-Log "Process tree state: Main PID=$appPid, Child PIDs=$($sidecarPids -join ',')"

        # 3. Request normal window close (CloseMainWindow / WM_CLOSE) if still running
        $closeStart = Get-Date
        if (-not $proc.HasExited) {
            Write-Log "Sending CloseMainWindow request..."
            $closeSuccess = $proc.CloseMainWindow()
            Write-Log "CloseMainWindow returned: $closeSuccess"
        }

        # 4. Wait for application exit within hard upper bound
        $exitedInBound = $proc.WaitForExit($HardBoundSeconds * 1000)
        $closeEnd = Get-Date
        $closeElapsedMs = ($closeEnd - $closeStart).TotalMilliseconds

        Write-Log "App process exited: $exitedInBound (Took $closeElapsedMs ms, bound was $($HardBoundSeconds * 1000) ms)"

        if (-not $exitedInBound) {
            Write-Log "TIMEOUT FAILED: Main application did NOT exit within $HardBoundSeconds seconds (Took $closeElapsedMs ms)! Force killing for test cleanup..." -ForegroundColor Red
            $proc.Kill()
            Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
            $appExitCode = -1
            $scriptExitCode = 1
        } else {
            $appExitCode = $proc.ExitCode
            Write-Log "App process exit code: $appExitCode"

            # 5. Process Tree & Zero Residual Orphan Check (scoped to PID tree and isolated root)
            Start-Sleep -Milliseconds 500
            $allProcs = Get-CimInstance Win32_Process
            $treePids = [System.Collections.Generic.HashSet[int]]::new()
            [void]$treePids.Add($appPid)
            foreach ($spid in $sidecarPids) { [void]$treePids.Add($spid) }
            $q = [System.Collections.Generic.Queue[int]]::new()
            foreach ($tp in $treePids) { $q.Enqueue($tp) }
            while ($q.Count -gt 0) {
                $curPid = $q.Dequeue()
                foreach ($procItem in $allProcs) {
                    if ($procItem.ParentProcessId -eq $curPid) {
                        if ($treePids.Add($procItem.ProcessId)) {
                            $q.Enqueue($procItem.ProcessId)
                        }
                    }
                }
            }
            $residualProcs = @()
            foreach ($procItem in $allProcs) {
                $cmd = if ($procItem.CommandLine) { $procItem.CommandLine } else { "" }
                $isTree = $treePids.Contains($procItem.ProcessId)
                $isIsolated = ($cmd.Contains($isolatedRoot))
                if ($isTree -or $isIsolated) {
                    $residualProcs += $procItem
                }
            }

            Write-Log "=== Process Tree Verification Summary ==="
            Write-Log "Exit within bound: $exitedInBound"
            Write-Log "Exit duration: $closeElapsedMs ms"
            Write-Log "Residual process count: $($residualProcs.Count)"
            Write-Log "Desktop application exit code: $appExitCode"

            if ($residualProcs.Count -gt 0) {
                Write-Log "FAILED: Residual processes found:" -ForegroundColor Red
                $residualProcs | ForEach-Object {
                    Write-Log "  Name=$($_.Name), PID=$($_.ProcessId), ParentPID=$($_.ParentProcessId)"
                }
                Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
                $scriptExitCode = 2
            } elseif ($appExitCode -ne 0) {
                Write-Log "FAILED: Application exited with non-zero exit code: $appExitCode" -ForegroundColor Red
                Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
                $scriptExitCode = $appExitCode
            } else {
                Write-Log "SUCCESS: Application exited within bound ($closeElapsedMs ms), exit code 0, and zero orphan processes remaining. Clean exit verified." -ForegroundColor Green
                # Cleanup isolated directory
                Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
                Write-Log "Isolated root cleaned."
                $scriptExitCode = 0
            }
        }
    }
} catch {
    Write-Log "Script execution threw exception: $_" -ForegroundColor Red
    $scriptExitCode = 1
} finally {
    $endTime = Get-Date
    $endIso = $endTime.ToString("yyyy-MM-ddTHH:mm:ss.fffffffzzz")
    $durationSeconds = [math]::Round(($endTime - $startTime).TotalSeconds, 2)
    $shellStr = "pwsh (PowerShell $($PSVersionTable.PSVersion))"

    # Write ac5-console.log (isolated error handling with fallback)
    $consoleLogFile = Join-Path $resolvedOutDir "ac5-console.log"
    $fallbackConsole = Join-Path $resolvedOutDir "ac5-console-fallback.log"
    $consoleWritten = $false
    $consoleFallbackWritten = $false
    $consoleError = $null
    try {
        [System.IO.File]::WriteAllLines($consoleLogFile, $logLines, [System.Text.Encoding]::UTF8)
        $consoleWritten = $true
    } catch {
        $consoleError = $_.Exception.Message
        # If console log is locked (e.g. by caller Tee-Object), write to fallback file
        try {
            [System.IO.File]::WriteAllLines($fallbackConsole, $logLines, [System.Text.Encoding]::UTF8)
            $consoleFallbackWritten = $true
        } catch {
            # Ignore secondary fallback write failure
        }
    }

    # Write ac5.exit with strict consistency guarantee and fallback path
    $exitFile = Join-Path $resolvedOutDir "ac5.exit"
    $fallbackExit = Join-Path $resolvedOutDir "ac5.exit-fallback"
    $exitWritten = $false
    $exitFallbackWritten = $false
    $exitWarning = $null
    try {
        [System.IO.File]::WriteAllText($exitFile, $scriptExitCode.ToString(), [System.Text.Encoding]::UTF8)
        # Read back to assert disk content matches exit code
        $readBackExit = [System.IO.File]::ReadAllText($exitFile).Trim()
        if ($readBackExit -ne $scriptExitCode.ToString()) {
            Write-Log "CRITICAL ERROR: ac5.exit content ($readBackExit) does not match script exit code ($scriptExitCode)" -ForegroundColor Red
            $scriptExitCode = 1
            # Re-write ac5.exit to match elevated exit code 1
            [System.IO.File]::WriteAllText($exitFile, "1", [System.Text.Encoding]::UTF8)
        }
        $exitWritten = $true
    } catch {
        $exitWarning = $_.Exception.Message
        Write-Host "Warning: Failed to write primary ac5.exit ($exitWarning), attempting fallback..."
        try {
            [System.IO.File]::WriteAllText($fallbackExit, $scriptExitCode.ToString(), [System.Text.Encoding]::UTF8)
            $readBackFallback = [System.IO.File]::ReadAllText($fallbackExit).Trim()
            if ($readBackFallback -eq $scriptExitCode.ToString()) {
                $exitFallbackWritten = $true
                Write-Host "Fallback exit code recorded successfully in: $fallbackExit"
            }
        } catch {
            $exitWarning += " | Fallback write failed: " + $_.Exception.Message
        }
    }

    # Write ac5-metadata.txt (isolated with fallback)
    $metaTxtFile = Join-Path $resolvedOutDir "ac5-metadata.txt"
    $fallbackMetaTxt = Join-Path $resolvedOutDir "ac5-metadata-fallback.txt"
    $metaTxtWritten = $false
    $metaTxtFallbackWritten = $false
    $metaTxtError = $null
    try {
        $metaBuilder = New-Object System.Text.StringBuilder
        $metaBuilder.AppendLine("runner=run-desktop-close-verification.ps1 (self-contained evidence logging)") | Out-Null
        $metaBuilder.AppendLine("outdir=$resolvedOutDir") | Out-Null
        $metaBuilder.AppendLine("start_local=$startIso") | Out-Null
        $metaBuilder.AppendLine("end_local=$endIso") | Out-Null
        $metaBuilder.AppendLine("duration_s=$durationSeconds") | Out-Null
        $metaBuilder.AppendLine("exit_code=$scriptExitCode") | Out-Null
        $metaBuilder.AppendLine("desktop_exit_code=$appExitCode") | Out-Null
        $metaBuilder.AppendLine("release_sha256=$releaseHash") | Out-Null
        $metaBuilder.AppendLine("head=$gitHead") | Out-Null
        $metaBuilder.AppendLine("shell=$shellStr") | Out-Null
        $metaBuilder.AppendLine("console_written=$consoleWritten") | Out-Null
        $metaBuilder.AppendLine("console_fallback_written=$consoleFallbackWritten") | Out-Null
        $metaBuilder.AppendLine("exit_written=$exitWritten") | Out-Null
        $metaBuilder.AppendLine("exit_fallback_written=$exitFallbackWritten") | Out-Null
        if ($consoleError) {
            $metaBuilder.AppendLine("console_warning=$consoleError") | Out-Null
        }
        if ($exitWarning) {
            $metaBuilder.AppendLine("exit_warning=$exitWarning") | Out-Null
        }
        $metaBuilder.AppendLine("note=Self-contained evidence generation by run-desktop-close-verification.ps1 without relying on caller Tee.") | Out-Null
        [System.IO.File]::WriteAllText($metaTxtFile, $metaBuilder.ToString(), [System.Text.Encoding]::UTF8)
        $metaTxtWritten = $true
    } catch {
        $metaTxtError = $_.Exception.Message
        try {
            [System.IO.File]::WriteAllText($fallbackMetaTxt, $metaBuilder.ToString(), [System.Text.Encoding]::UTF8)
            $metaTxtFallbackWritten = $true
        } catch {}
    }

    # Write ac5-metadata.json (isolated with fallback)
    $metaJsonFile = Join-Path $resolvedOutDir "ac5-metadata.json"
    $fallbackMetaJson = Join-Path $resolvedOutDir "ac5-metadata-fallback.json"
    $metaJsonWritten = $false
    $metaJsonFallbackWritten = $false
    $metaJsonError = $null
    try {
        $metaObj = [ordered]@{
            runner = "run-desktop-close-verification.ps1"
            outdir = $resolvedOutDir
            start_local = $startIso
            end_local = $endIso
            duration_s = $durationSeconds
            exit_code = $scriptExitCode
            desktop_exit_code = $appExitCode
            release_sha256 = $releaseHash
            head = $gitHead
            shell = $shellStr
            console_written = $consoleWritten
            console_fallback_written = $consoleFallbackWritten
            exit_written = $exitWritten
            exit_fallback_written = $exitFallbackWritten
            metadata_txt_written = $metaTxtWritten
            metadata_txt_fallback_written = $metaTxtFallbackWritten
        }
        if ($consoleError) {
            $metaObj["console_warning"] = $consoleError
        }
        if ($exitWarning) {
            $metaObj["exit_warning"] = $exitWarning
        }
        if ($metaTxtError) {
            $metaObj["metadata_txt_warning"] = $metaTxtError
        }
        $metaJsonContent = ($metaObj | ConvertTo-Json -Depth 4)
        [System.IO.File]::WriteAllText($metaJsonFile, $metaJsonContent, [System.Text.Encoding]::UTF8)
        $metaJsonWritten = $true
    } catch {
        $metaJsonError = $_.Exception.Message
        try {
            if ($metaJsonContent) {
                [System.IO.File]::WriteAllText($fallbackMetaJson, $metaJsonContent, [System.Text.Encoding]::UTF8)
                $metaJsonFallbackWritten = $true
            }
        } catch {}
    }

    Write-Host "Self-contained evidence recorded in: $resolvedOutDir"
    exit $scriptExitCode
}

exit $scriptExitCode
