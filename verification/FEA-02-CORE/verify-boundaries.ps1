param([string]$BaseCommit = 'bf1c8eb00', [string]$ReleaseCommit = '2546410c4')
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $repoRoot
try {
    $protected = @('apps/desktop-avalonia/src/NewManga.App', 'apps/desktop-avalonia/src/NewManga.CoreClient', 'src', 'doc/contracts')
    $existingTests = @(git ls-tree -r --name-only $BaseCommit -- 'apps/desktop-avalonia/tests/')
    git diff --quiet $BaseCommit -- @protected @existingTests
    if ($LASTEXITCODE -ne 0) { throw 'Protected source/contract/existing-test path changed.' }
    # The release commit updates FEA-01 governance records; those pre-existing changes are not this delivery.
    git diff --quiet $ReleaseCommit -- doc/plan
    if ($LASTEXITCODE -ne 0) { throw 'Frozen documentation changed after task release.' }
    Write-Output 'PASS: Current/App, CoreClient, Python, frozen contracts and existing tests unchanged.'

    $solution = 'apps/desktop-avalonia/NewManga.sln'
    $baseline = (git show "${BaseCommit}:$solution") -join "`n"
    if ($LASTEXITCODE -ne 0) { throw 'Cannot load baseline solution.' }
    $current = [IO.File]::ReadAllText((Join-Path $repoRoot $solution)).Replace("`r`n", "`n").TrimStart([char]0xFEFF).TrimEnd("`n")
    $baseline = $baseline.TrimStart([char]0xFEFF).TrimEnd("`n")
    $projectIds = @('DB80AE71-4115-4A3C-A8D0-2F33B1D31F21', '0DFE5C63-8868-4753-B58A-D77E6E5CE614')
    foreach ($id in $projectIds) {
        $pattern = '(?m)^Project\([^\n]+\{' + $id + '\}"\nEndProject\n'
        if ([regex]::Matches($current, $pattern).Count -ne 1) { throw "Expected one new project: $id" }
        $current = [regex]::Replace($current, $pattern, '')
        $pattern = '(?m)^\t\t\{' + $id + '\}[^\n]*\n'
        # 12 configuration rows + one nesting row, belonging only to this new project.
        if ([regex]::Matches($current, $pattern).Count -ne 13) { throw "Unexpected new-project rows: $id" }
        $current = [regex]::Replace($current, $pattern, '')
    }
    if ($current -cne $baseline) { throw 'Existing solution content/configuration changed.' }
    Write-Output 'PASS: solution contains only two new projects and their own configuration/nesting rows.'

    $coreProject = [xml](Get-Content 'apps/desktop-avalonia/src/NewManga.ApplicationCore/NewManga.ApplicationCore.csproj' -Raw)
    if ($coreProject.SelectNodes('//ProjectReference|//PackageReference').Count -ne 0) {
        throw 'ApplicationCore must have no project/package dependencies.'
    }
    $currentReferences = rg -l 'ApplicationCore' apps/desktop-avalonia/src --glob '*.csproj' --glob '!NewManga.ApplicationCore.csproj'
    if ($LASTEXITCODE -gt 1 -or $currentReferences) { throw 'ApplicationCore unexpectedly wired into existing source projects.' }
    Write-Output 'PASS: no application wiring and no new production dependency.'

    $allowed = '^(apps/desktop-avalonia/(src/NewManga\.ApplicationCore/|tests/NewManga\.ApplicationCore\.Tests/|NewManga\.sln$)|verification/FEA-02-CORE/|doc/(tasks/FEA-02-CORE\.md$|STATUS\.md$|REBASELINE_PLAN\.md$|TASK_LEDGER\.md$|checkpoints/|handoffs/FEA-02-CORE-|reviews/FEA-02-CORE-))'
    $changed = @(git diff --name-only $ReleaseCommit) + @(git ls-files --others --exclude-standard)
    foreach ($path in $changed) {
        if ($path -notmatch $allowed) { throw "Outside write scope: $path" }
    }
    Write-Output 'PASS: changed and untracked paths remain inside the authorized task scope.'
} finally { Pop-Location }
