#!/usr/bin/env pwsh
# FEA-14-SET-1 (R-013): replay the two mutation patches and prove they turn the pure
# resolver matrix RED. Run from any directory inside the repository worktree.
#
# The script refuses to run when the mutated production file has uncommitted changes,
# applies each patch, runs the targeted tests, restores the file with `git checkout --`
# and finally verifies the file is clean again.
param(
    [string]$LogPath = "verification/FEA-14-SET-1/logs/mutations-replay.log"
)

$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location -LiteralPath $root

$target = 'apps/desktop-avalonia/src/NewManga.App/Services/TypographySnapshot.cs'
$testProject = 'apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj'
$filter = 'FullyQualifiedName~TypographyResolverTests'
$mutations = @(
    @{ Id = 'M1'; Patch = 'verification/FEA-14-SET-1/mutations/M1-missing-not-recorded.patch'; Description = 'missing stack segments are not recorded' },
    @{ Id = 'M2'; Patch = 'verification/FEA-14-SET-1/mutations/M2-stack-head-not-resolved.patch'; Description = 'the first stack segment is trusted without probing' }
)

$lines = [System.Collections.Generic.List[string]]::new()
function Add-Line([string]$text) {
    $lines.Add($text)
    Write-Host $text
}

Add-Line "FEA-14-SET-1 MUTATION REPLAY"
Add-Line "time=$(Get-Date -Format o)"
Add-Line "root=$root"
Add-Line "HEAD=$(git rev-parse HEAD)"
Add-Line "powershell=$($PSVersionTable.PSVersion)"
Add-Line ""

$dirty = git status --porcelain -- $target
if ($dirty) {
    Add-Line "REFUSE: $target has uncommitted changes:"
    Add-Line ($dirty -join "`n")
    $lines | Set-Content -LiteralPath $LogPath -Encoding utf8
    exit 2
}

$failures = 0
foreach ($mutation in $mutations) {
    Add-Line "== $($mutation.Id): $($mutation.Description) =="
    Add-Line "patch=$($mutation.Patch)"
    git apply --check $mutation.Patch 2>&1 | ForEach-Object { Add-Line "check: $_" }
    if ($LASTEXITCODE -ne 0) {
        Add-Line "RESULT: APPLY-CHECK-FAILED (exit $LASTEXITCODE)"
        $failures++
        continue
    }

    git apply $mutation.Patch
    Add-Line "applied: yes"

    $output = dotnet test $testProject --filter $filter -v q 2>&1 | Out-String
    $exit = $LASTEXITCODE
    Add-Line "test-exit=$exit"
    Add-Line "test-output-tail:"
    ($output -split "`r?`n" | Select-Object -Last 12) | ForEach-Object { Add-Line "  $_" }

    # Restore immediately, before any further work, so a crash cannot leave the mutation in place.
    git checkout -- $target
    if ($LASTEXITCODE -ne 0) {
        Add-Line "RESULT: RESTORE-FAILED"
        $lines | Set-Content -LiteralPath $LogPath -Encoding utf8
        exit 3
    }

    $stillDirty = git status --porcelain -- $target
    if ($stillDirty) {
        Add-Line "RESULT: RESTORE-VERIFY-FAILED"
        $failures++
    }
    elseif ($exit -eq 0) {
        Add-Line "RESULT: MUTATION-SURVIVED (tests stayed green)"
        $failures++
    }
    else {
        Add-Line "RESULT: RED (mutation detected)"
    }
    Add-Line ""
}

# Baseline after all patches were restored: the targeted matrix must be green again.
$baseline = dotnet test $testProject --filter $filter -v q 2>&1 | Out-String
$baselineExit = $LASTEXITCODE
Add-Line "== baseline after restore =="
Add-Line "test-exit=$baselineExit"
($baseline -split "`r?`n" | Select-Object -Last 6) | ForEach-Object { Add-Line "  $_" }
if ($baselineExit -ne 0) { $failures++ }

Add-Line ""
Add-Line "VERDICT: $(if ($failures -eq 0) { 'PASS (both mutations RED, baseline green)' } else { "FAIL ($failures problem(s))" })"
$lines | Set-Content -LiteralPath $LogPath -Encoding utf8
exit $(if ($failures -eq 0) { 0 } else { 1 })
