$ErrorActionPreference = "Stop"

$workspaceRoot = "G:/CODEX/New Manga.workspace"
$mutationDir = "$workspaceRoot/temp/P22-REBASE-1/mutation"
$verificationDir = "G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1/verification/P22-REBASE-1"
$worktreeRoot = "G:/CODEX/New Manga.workspace/worktrees/P22-REBASE-1"

Write-Host "Creating mutation directory at $mutationDir..."
if (Test-Path $mutationDir) {
    Remove-Item -Recurse -Force $mutationDir
}
New-Item -ItemType Directory -Force -Path $mutationDir | Out-Null

Write-Host "Copying worktree to mutation workspace..."
Copy-Item -Path "$worktreeRoot/apps" -Destination "$mutationDir/apps" -Recurse -Force
Copy-Item -Path "$worktreeRoot/verification" -Destination "$mutationDir/verification" -Recurse -Force

$mutBridgeFile = "$mutationDir/apps/desktop/src-tauri/src/library_bridge.rs"
$bridgeContent = [System.IO.File]::ReadAllText($mutBridgeFile)

# Replace the transaction lock acquisition with a dummy unheld lock guard () so it compiles cleanly
$bridgeContent = $bridgeContent.Replace("`r`n", "`n")

$targetLock = @"
        let _tx_guard = self.transaction_lock.lock().map_err(|_| {
            LibraryError::unavailable("Internal mutex poisoned (transaction)")
        })?;
"@.Replace("`r`n", "`n")

$dummyLock = @"
        // [MUTATION: TRANSACTION LOCK BYPASSED]
        let _tx_guard = ();
"@.Replace("`r`n", "`n")

$mutatedContent = $bridgeContent.Replace($targetLock, $dummyLock)

if ($mutatedContent -eq $bridgeContent) {
    throw "Failed to apply mutation: pattern not matched"
}

[System.IO.File]::WriteAllText($mutBridgeFile, $mutatedContent)
Write-Host "Mutation successfully applied to $mutBridgeFile"

$cargoTargetDir = "$workspaceRoot/builds/P22-REBASE-1/cargo-target-mutation"
$cargoHome = "$workspaceRoot/task-envs/P22-REBASE-1/cargo_home"
$tmpDir = "$workspaceRoot/task-envs/P22-REBASE-1/tmp"
$pycacheDir = "$workspaceRoot/task-envs/P22-REBASE-1/pycache"
$venvPython = "$workspaceRoot/task-envs/P22-REBASE-1/venv/Scripts/python.exe"

$env:CARGO_TARGET_DIR = $cargoTargetDir
$env:CARGO_HOME = $cargoHome
$env:TEMP = $tmpDir
$env:TMP = $tmpDir
$env:PYTHONPYCACHEPREFIX = $pycacheDir
$env:M2RC1_PYTHON = $venvPython

$mutSrcTauri = "$mutationDir/apps/desktop/src-tauri"
$stdoutLog = "$verificationDir/mutation-test.stdout.log"
$stderrLog = "$verificationDir/mutation-test.stderr.log"
$exitFile = "$verificationDir/mutation-test.exit"

Write-Host "Executing mutation test..."
$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = "cargo"
$pinfo.Arguments = "test --locked library_bridge::tests::same_channel_concurrent_round_trips_keep_response_ownership -- --nocapture"
$pinfo.WorkingDirectory = $mutSrcTauri
$pinfo.RedirectStandardOutput = $true
$pinfo.RedirectStandardError = $true
$pinfo.UseShellExecute = $false

$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $pinfo
$proc.Start() | Out-Null
$stdoutTask = $proc.StandardOutput.ReadToEndAsync()
$stderrTask = $proc.StandardError.ReadToEndAsync()
$proc.WaitForExit(60000)

$mutExit = $proc.ExitCode
$mutStdout = $stdoutTask.Result
$mutStderr = $stderrTask.Result

[System.IO.File]::WriteAllText($stdoutLog, $mutStdout)
[System.IO.File]::WriteAllText($stderrLog, $mutStderr)
[System.IO.File]::WriteAllText($exitFile, "$mutExit")

Write-Host "Mutation test completed with EXIT=$mutExit"

$panicMessage = "none"
if ($mutStderr -match "panicked at [^\r\n]+") {
    $panicMessage = $Matches[0]
} elseif ($mutStdout -match "panicked at [^\r\n]+") {
    $panicMessage = $Matches[0]
}

$compilationOk = ($mutStderr -match "Running unittests" -or $mutStdout -match "Running unittests")
$panicDetected = ($mutStderr -match "panicked" -or $mutStdout -match "panicked")

$report = [PSCustomObject]@{
    mutation_target = "apps/desktop/src-tauri/src/library_bridge.rs"
    mutation_description = "Bypassed transaction_lock by replacing guard with () in round_trip"
    exit_code = $mutExit
    expected_non_zero = $true
    compilation_succeeded = $compilationOk
    panic_detected = $panicDetected
    panic_message = $panicMessage
    status = if ($mutExit -ne 0 -and $compilationOk -and $panicDetected) { "MUTATION_DISCRIMINATED" } else { "MUTATION_FAILED" }
    timestamp_utc = ([DateTime]::UtcNow.ToString("o"))
}

$report | ConvertTo-Json -Depth 4 | Set-Content -Path "$verificationDir/mutation-report.json" -Encoding UTF8
Write-Host "Mutation report:"
$report | ConvertTo-Json -Depth 4
