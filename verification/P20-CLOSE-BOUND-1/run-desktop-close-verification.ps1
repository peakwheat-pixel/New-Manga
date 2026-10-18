# run-desktop-close-verification.ps1
# P20-CLOSE-BOUND-1 AC5: Real Interactive Desktop Window Close & Process Tree Verification Script
# NOTE: This script is intended to be run by the Coordinator in an interactive Windows desktop session
# with fully functional WebView2 runtime. Non-interactive agent sessions lack desktop GUI interaction (0x80070578).

param(
    [string]$AppExe = "apps/desktop/src-tauri/target/release/m2rc1-desktop.exe",
    [string]$SidecarDir = "resources/core-sidecar",
    [int]$HardBoundSeconds = 5,
    [string]$OutDir = ""
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

    # 2. Set environment variables for isolated execution
    $env:NEWMANGA_DATA_ROOT = $dataRoot
    $env:M2RC1_DERIVED_ROOT = $derivedRoot
    $env:M2RC2_CATALOG_DB = $catalogDb
    $env:M2RC1_MANAGED_ROOT = Join-Path $isolatedRoot "managed"
    New-Item -ItemType Directory -Path $env:M2RC1_MANAGED_ROOT -Force | Out-Null

    # Verify binary existence
    if (-not (Test-Path $AppExe)) {
        # Check debug binary if release not found
        $AppExe = "apps/desktop/src-tauri/target/debug/m2rc1-desktop.exe"
    }
    if (-not (Test-Path $AppExe)) {
        Write-Log "Could not find m2rc1-desktop binary. Please build the desktop app first." -ForegroundColor Red
        $scriptExitCode = 1
    } else {
        $resolvedExe = (Resolve-Path $AppExe).Path
        Write-Log "Launching desktop application: $resolvedExe"
        try {
            $releaseHash = (Get-FileHash $resolvedExe -Algorithm SHA256).Hash.ToLower()
        } catch {}

        $pinfo = New-Object System.Diagnostics.ProcessStartInfo
        $pinfo.FileName = $resolvedExe
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

        # 3. Request normal window close (CloseMainWindow / WM_CLOSE)
        Write-Log "Sending CloseMainWindow request..."
        $closeStart = Get-Date
        $closeSuccess = $proc.CloseMainWindow()
        Write-Log "CloseMainWindow returned: $closeSuccess"

        # 4. Wait for application exit within hard upper bound
        $exitedInBound = $proc.WaitForExit($HardBoundSeconds * 1000)
        $closeEnd = Get-Date
        $closeElapsedMs = ($closeEnd - $closeStart).TotalMilliseconds

        Write-Log "App process exited: $exitedInBound (Took $closeElapsedMs ms, bound was $($HardBoundSeconds * 1000) ms)"

        if (-not $exitedInBound) {
            Write-Log "TIMEOUT FAILED: Main application did NOT exit within $HardBoundSeconds seconds (Took $closeElapsedMs ms)! Force killing for test cleanup..." -ForegroundColor Red
            $proc.Kill()
            Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
            $scriptExitCode = 1
        } else {
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

            if ($residualProcs.Count -gt 0) {
                Write-Log "FAILED: Residual processes found:" -ForegroundColor Red
                $residualProcs | ForEach-Object {
                    Write-Log "  Name=$($_.Name), PID=$($_.ProcessId), ParentPID=$($_.ParentProcessId)"
                }
                Remove-Item -Path $isolatedRoot -Recurse -Force -ErrorAction SilentlyContinue
                $scriptExitCode = 2
            } else {
                Write-Log "SUCCESS: Application exited within bound ($closeElapsedMs ms) and zero orphan processes remaining. Clean exit verified." -ForegroundColor Green
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

    # Write ac5-console.log
    $consoleLogFile = Join-Path $resolvedOutDir "ac5-console.log"
    [System.IO.File]::WriteAllLines($consoleLogFile, $logLines, [System.Text.Encoding]::UTF8)

    # Write ac5.exit
    $exitFile = Join-Path $resolvedOutDir "ac5.exit"
    [System.IO.File]::WriteAllText($exitFile, $scriptExitCode.ToString(), [System.Text.Encoding]::UTF8)

    # Read back to assert disk content matches exit code
    $readBackExit = [System.IO.File]::ReadAllText($exitFile).Trim()
    if ($readBackExit -ne $scriptExitCode.ToString()) {
        Write-Log "CRITICAL ERROR: ac5.exit content ($readBackExit) does not match script exit code ($scriptExitCode)" -ForegroundColor Red
        $scriptExitCode = 1
    }

    # Write ac5-metadata.txt
    $metaTxtFile = Join-Path $resolvedOutDir "ac5-metadata.txt"
    $metaBuilder = New-Object System.Text.StringBuilder
    $metaBuilder.AppendLine("runner=run-desktop-close-verification.ps1 (self-contained evidence logging)") | Out-Null
    $metaBuilder.AppendLine("outdir=$resolvedOutDir") | Out-Null
    $metaBuilder.AppendLine("start_local=$startIso") | Out-Null
    $metaBuilder.AppendLine("end_local=$endIso") | Out-Null
    $metaBuilder.AppendLine("duration_s=$durationSeconds") | Out-Null
    $metaBuilder.AppendLine("exit_code=$scriptExitCode") | Out-Null
    $metaBuilder.AppendLine("release_sha256=$releaseHash") | Out-Null
    $metaBuilder.AppendLine("head=$gitHead") | Out-Null
    $metaBuilder.AppendLine("shell=$shellStr") | Out-Null
    $metaBuilder.AppendLine("note=Self-contained evidence generation by run-desktop-close-verification.ps1 without relying on caller Tee.") | Out-Null
    [System.IO.File]::WriteAllText($metaTxtFile, $metaBuilder.ToString(), [System.Text.Encoding]::UTF8)

    # Write ac5-metadata.json
    $metaJsonFile = Join-Path $resolvedOutDir "ac5-metadata.json"
    $metaObj = [ordered]@{
        runner = "run-desktop-close-verification.ps1"
        outdir = $resolvedOutDir
        start_local = $startIso
        end_local = $endIso
        duration_s = $durationSeconds
        exit_code = $scriptExitCode
        release_sha256 = $releaseHash
        head = $gitHead
        shell = $shellStr
    }
    [System.IO.File]::WriteAllText($metaJsonFile, ($metaObj | ConvertTo-Json -Depth 4), [System.Text.Encoding]::UTF8)

    Write-Host "Self-contained evidence recorded in: $resolvedOutDir"
    exit $scriptExitCode
}

exit $scriptExitCode
