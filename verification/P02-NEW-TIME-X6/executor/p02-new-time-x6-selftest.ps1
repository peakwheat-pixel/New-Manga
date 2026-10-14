#Requires -Version 7.4
<#
.SYNOPSIS
    P02-NEW-TIME-X6 — pure-function selftest for p02-new-time-x6.ps1.
    PowerShell 7 only, no new dependencies.

.DESCRIPTION
    Pure selftest per Task AC1: covers parser integrity, CreateNew collision /
    fail-stop on an existing output target, partial-output preservation (streamed
    lines survive a mid-run failure; the partial file is never deleted or
    rewritten), history-path isolation (I1 semantics: an exact family segment or
    a family segment extended with the hyphen delimiter matches; non-delimiter
    extensions do not), forbidden-API / dynamic-enumeration static bans, the I2
    external freeze-manifest input seam (missing, sentinel, malformed,
    hash-mismatch, incomplete, binding-failed and history-violating freeze input
    all fail closed through pure/unit seams; a valid structure passes the pure
    gate), JSON-Pointer integrity, raw-output fidelity (including NUL), failure
    classification mapping, RunId validation, the exact frozen git argv, and
    the git-branch-matches-freeze short-name/full-ref branch comparison
    (AC3-BRANCH-REF-MISMATCH resolution: the runtime symbolic-ref full ref
    must match the manifest short branch name via the refs/heads/ prefix;
    wrong branch, non-heads namespace and detached-HEAD all fail closed).
    Adds the pure static helper-observation envelope regression
    (AC3-WHOAMI-HELPER-OUTPUT-SHAPE resolution): BOTH Invoke-HelperProcess
    producer paths (success and exception) must emit
    output.value.{stdout,stderr} verbatim ConvertTo-RawBytesRecord records —
    the same envelope every consumer and /output/value/... pointer reads.
    Adds the git-toplevel-matches-worktree path comparison regression
    (AC3-GIT-TOPLEVEL-PATH-SEPARATOR resolution): BOTH the Git-reported
    toplevel and the frozen worktree path are normalized to Windows
    separators inside the pure Test-GitToplevelMatchesWorktree helper before
    the case-insensitive compare, so the same absolute directory in slash or
    backslash form matches while a different volume/directory/leaf fails
    closed.
    Adds the X6-SR-01/X6-SR-02 (I1 bounded repair) regressions: the index
    integrity check must resolve its sampled index through THIS worktree's
    own 'git rev-parse --absolute-git-dir' gitdir (never the main repository
    .git that the common-dir form returns for a linked worktree), and the
    freeze-manifest placement gate must protect BOTH the Task worktree AND
    the main repository root, reject '.'/'..' path segments before any
    comparison, compare on lexically normalized absolute paths, and require
    a reparse-free manifest path chain before the manifest bytes are read.
    Runs NO live executor, NO git child, NO whoami child, NO dynamic process
    enumeration, NO profile/registry/ACL write API, NO post-run Review/
    Build/Cargo/AC1-AC7/Windows Sandbox — those are recorded as explicitly
    SKIPPED. (The X6 one-shot itself is NOT this selftest; it runs only after
    Codex freeze + final pre-run, per Task Gate.)

    The executor script is never executed or dot-sourced. Pure functions are
    extracted from its parsed AST as in-memory function definitions only; the
    executor's top-level param/preflight/main sequence never runs.

    All filesystem fixtures live exclusively under the authorized task temp root:
        G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/<stamp>-pure-selftest/
    Fixtures are preserved for review (never deleted).

    Output: human-readable assert/skip log on stdout plus one SUMMARY-JSON line.
    Exit 0 iff all asserts pass and no assert fails; skips are listed separately
    and never counted as passes.
#>
[CmdletBinding()]
param(
    [string]$CollectorPath = (Join-Path $PSScriptRoot 'p02-new-time-x6.ps1'),
    [string]$SelfPath = $PSCommandPath,
    [string]$TempRoot = 'G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6',
    [string]$Stamp = (Get-Date -Format 'yyyyMMdd-HHmmss')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:AssertsPassed = 0
$script:AssertsFailed = 0
$script:FailedNames = [Collections.Generic.List[string]]::new()
$script:Skips = [Collections.Generic.List[object]]::new()
$script:StartedUtc = [DateTime]::UtcNow.ToString('o')

function Assert-True {
    param([bool]$Condition, [string]$Name, [string]$Detail = '')
    if ($Condition) {
        $script:AssertsPassed++
        Write-Output ("[ASSERT PASS] {0}" -f $Name)
    } else {
        $script:AssertsFailed++
        $script:FailedNames.Add($Name)
        Write-Output ("[ASSERT FAIL] {0} :: {1}" -f $Name, $Detail)
    }
}

function Assert-Throws {
    param([scriptblock]$Body, [string]$Name, [string]$Detail = '')
    $threw = $false
    try { & $Body | Out-Null } catch { $threw = $true }
    Assert-True $threw $Name $Detail
}

function Add-Skip {
    param([string]$Name, [string]$Reason)
    $script:Skips.Add([ordered]@{ name = $Name; reason = $Reason })
    Write-Output ("[SKIP] {0} :: {1}" -f $Name, $Reason)
}

# ---------------------------------------------------------------------------
# Environment header (full shell path / version / argv / UTC per test log rules)
# ---------------------------------------------------------------------------
$pwshExePath = $null
try { $pwshExePath = (Get-Process -Id $PID).Path } catch { $pwshExePath = $null }
Write-Output '=== P02-NEW-TIME-X6 pure selftest ==='
Write-Output ("shell: {0}" -f $pwshExePath)
Write-Output ("pwsh version: {0} {1} / {2}" -f $PSVersionTable.PSVersion, $PSVersionTable.PSEdition, $ExecutionContext.SessionState.LanguageMode)
Write-Output ("os: {0}" -f $PSVersionTable.OS)
Write-Output ("startedUtc: {0}" -f $script:StartedUtc)
Write-Output ("argv: {0}" -f (($PSCommandPath, $CollectorPath, $SelfPath, $TempRoot, $Stamp) -join ' | '))
Write-Output ("collectorPath: {0}" -f $CollectorPath)
Write-Output ("selfPath: {0}" -f $SelfPath)
Write-Output ("fixtureDir: {0}" -f (Join-Path $TempRoot "$Stamp-pure-selftest"))
Write-Output ''

# ---------------------------------------------------------------------------
# [SKIP] items — live scopes forbidden for this Owner task (listed separately)
# ---------------------------------------------------------------------------
Add-Skip 'live-x6-executor-run' 'Task: live X6 one-shot execution is NOT authorized in this Owner delivery round; requires DSH bounded source Review, Codex adjudication, parser/selftest gates plus Codex freeze and final pre-run = PRE_RUN_PASS first.'
Add-Skip 'live-git-child' 'Forbidden here: no git child process during the pure selftest; git argv builders are verified as pure functions.'
Add-Skip 'live-whoami-child' 'Forbidden here: no whoami child during the pure selftest; identity comparison stays a documented live-scope check.'
Add-Skip 'live-registry-acl-profile-getter' 'Forbidden here: no registry/ACL/profile API at all in this Task scope (read or write).'
Add-Skip 'executor-dynamic-process-enumeration' 'Forbidden scopes: attempt6 executor (never referenced/read/executed), Toolhelp/Process32*/Get-Process enumeration — all NOT_RUN by Task forbidden scope.'
Add-Skip 'x6-post-run-review-build-cargo-ac-sandbox' 'Forbidden scopes: X6, post-run Review, Build/Cargo, product AC1-AC7, Windows Sandbox — later Gates, never released by this Task; all NOT_RUN.'
Add-Skip 'historical-input-access' 'Forbidden scopes: no H1/P2-1 historical input, conclusion, finding or missing-source record is read, rewritten, backfilled or re-awarded; history isolation is enforced statically.'

# ---------------------------------------------------------------------------
# Parser: both scripts must parse with zero syntax errors
# ---------------------------------------------------------------------------
Write-Output '--- parser ---'
$tokens = $null; $parseErrors = $null
$collectorAst = [System.Management.Automation.Language.Parser]::ParseFile($CollectorPath, [ref]$tokens, [ref]$parseErrors)
Assert-True (@($parseErrors).Count -eq 0) 'parser-collector-zero-errors' ("errors=$(@($parseErrors).Count)")
$collectorText = [IO.File]::ReadAllText($CollectorPath)

$tokens2 = $null; $parseErrors2 = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile($SelfPath, [ref]$tokens2, [ref]$parseErrors2)
Assert-True (@($parseErrors2).Count -eq 0) 'parser-selftest-zero-errors' ("errors=$(@($parseErrors2).Count)")

# ---------------------------------------------------------------------------
# Static AST contract assertions over the executor source (no execution)
# ---------------------------------------------------------------------------
Write-Output '--- static AST contract (executor source, never executed) ---'
$functionNames = $collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true) |
    ForEach-Object { $_.Name }
$requiredFunctions = @(
    'Require', 'Get-Sha256HexFromBytes', 'ConvertTo-SafeUtf8Text', 'Split-NulRecords',
    'ConvertTo-RawBytesRecord', 'Resolve-JsonPointer',
    'New-PathProbeAbsentValue', 'New-PathProbeErrorValue',
    'Get-PathProbeValueFromAttributes', 'Get-ProbeCheckResult',
    'Get-CollectorFailureClassification',
    'Test-PathContainsHistorySegment', 'Assert-TaskPathIsolation',
    'Test-FreezeManifestBytes', 'Get-ManifestField',
    'Test-PathContainsDotSegment', 'Test-PathOutsideRepository',
    'Test-PathUnderAnyForbiddenPrefix',
    'Test-FreezeManifestShape', 'Test-FreezeManifestBinding',
    'New-GitPrefixArgv', 'New-StatusArgv', 'New-CheckIgnoreArgv',
    'Test-BranchRefMatchesManifest',
    'Test-GitToplevelMatchesWorktree',
    'New-ObservationRecord', 'Add-ObservationException', 'New-CheckRecord',
    'Get-VolumeEvidence', 'Test-PathAncestorsOrdinary',
    'New-OutputPreflightCapture', 'New-OutputPostCreateFacts', 'Open-ExclusiveCreateNew',
    'New-MetaLineObject', 'New-ClosedLineObject'
)
$missingFunctions = @($requiredFunctions | Where-Object { $functionNames -notcontains $_ })
Assert-True ($missingFunctions.Count -eq 0) 'ast-required-pure-functions-present' ("missing=$($missingFunctions -join ',')")

# --- forbidden APIs (Task forbidden scope: no File.Replace, no dynamic process
#     enumeration, no profile/registry/ACL write API) ---
$forbiddenMembers = @(
    'Replace', 'SetNamedSecurityInfo', 'SetSecurityInfo', 'SetAccessControl',
    'CreateAppContainerProfile', 'DeleteAppContainerProfile', 'DeriveAppContainerSidFromAppContainerName',
    'GetAppContainerRegistryLocation', 'GetAppContainerFolderPath',
    'CreateToolhelp32Snapshot', 'Process32FirstW', 'Process32NextW', 'DefinePInvokeMethod',
    'MoveFile', 'MoveFileEx', 'DeleteFile', 'DeleteFileW', 'RegSetValueEx', 'RegCreateKeyEx'
)
$memberHits = @($collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.InvokeMemberExpressionAst] }, $true) |
    ForEach-Object { try { [string]$_.Member.Value } catch { $null } } |
    Where-Object { $forbiddenMembers -contains $_ })
Assert-True ($memberHits.Count -eq 0) 'ast-no-forbidden-member-invocations' ("hits=$($memberHits -join ',')")

$forbiddenCommands = @('Start-Process', 'Invoke-Expression', 'Stop-Process', 'Remove-Item', 'Set-Acl', 'New-ItemProperty', 'Set-ItemProperty', 'Move-Item', 'Rename-Item', 'Copy-Item', 'Out-File', 'Set-Content', 'Add-Content')
$commandHits = @($collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true) |
    ForEach-Object { try { [string]$_.GetCommandName() } catch { $null } } |
    Where-Object { $forbiddenCommands -contains $_ })
Assert-True ($commandHits.Count -eq 0) 'ast-no-shell-launch-eval-or-write-commands' ("hits=$($commandHits -join ',')")

# Get-Process must not appear anywhere in the collector source (dynamic process
# enumeration ban is absolute in the collector).
Assert-True (-not $collectorText.Contains('Get-Process')) 'ast-no-get-process-anywhere' 'dynamic process enumeration (Get-Process) is forbidden in the collector source'

$fileModes = @([regex]::Matches($collectorText, '\[IO\.FileMode\]::(\w+)') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
Assert-True (@($fileModes | Where-Object { $_ -ne 'CreateNew' }).Count -eq 0 -and $fileModes.Count -gt 0) 'ast-filemode-create-new-only' ("modes=$($fileModes -join ',')")
$fileShares = @([regex]::Matches($collectorText, '\[IO\.FileShare\]::(\w+)') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
Assert-True (@($fileShares | Where-Object { $_ -ne 'None' }).Count -eq 0 -and $fileShares.Count -gt 0) 'ast-fileshare-none-only' ("shares=$($fileShares -join ',')")
# File.Replace ban is enforced semantically via the 'Replace' member ban above;
# here we additionally assert no static File.Replace invocation AST exists.
$fileReplaceAst = @($collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.InvokeMemberExpressionAst] }, $true) |
    Where-Object {
        $m = $null
        try { $m = [string]$_.Member.Value } catch { $m = $null }
        $m -ceq 'Replace' -and $null -ne $_.Expression -and $_.Expression.Extent.Text -like '*File*'
    })
Assert-True ($fileReplaceAst.Count -eq 0) 'ast-no-file-replace-invocation' 'File.Replace invocation is forbidden (Task forbidden scope)'

foreach ($literal in @(
        'GIT_OPTIONAL_LOCKS', 'GIT_TERMINAL_PROMPT', 'GIT_TRACE', 'GIT_CONFIG',
        'NEW_TIME_EVIDENCE', 'CANNOT_SUBSTITUTE_H1_P2_1_TIME_EVIDENCE',
        'P02-NEW-TIME-X6-executor-1', 'P02-NEW-TIME-X6-freeze-manifest-1',
        'agent-output/zcode/P02-NEW-TIME-X6',
        'ForbiddenWritePrefixes', 'EXECUTED_X6_DYNAMIC_CLOSURE',
        'FreezeManifestPath', 'FreezeManifestSha256', 'FREEZE_MANIFEST_INVALID',
        'INPUT_NOT_FROZEN', 'HISTORY_SCOPE_VIOLATION',
        'BLOCKED_OUTPUT_PRECHECK', 'BLOCKED_INPUT_NOT_FROZEN', 'BLOCKED_SOURCE_PIN_DRIFT',
        'BLOCKED_BY_FAILED_CHECKS', 'BLOCKED_EXCEPTION_FAIL_CLOSED',
        'core.hooksPath=NUL', 'core.fsmonitor=false', '--no-optional-locks',
        'porcelain=v2', 'NOT_RUN', 'bc502e7aae07074fff7228d585674e87d53efcfd',
        '--absolute-git-dir', 'MainRepositoryRoot'
)) {
    Assert-True ($collectorText.Contains($literal)) "ast-literal-present:$literal" 'literal not found in collector source'
}

# I2 circular-reference bans: the collector source must NOT embed the frozen
# delivery HEAD (sentinel or real), the old sentinel mechanism, or ANY 64-hex
# literal (every such pin — including the collector's own full SHA — must come
# exclusively from the external freeze manifest). The sentinel DETECTION token
# is verification logic, not a frozen input: it must appear exactly once and
# only inside the -like residue scan.
foreach ($bannedToken in @('FrozenDeliveryHead', 'FrozenCwd', 'task-document')) {
    Assert-True (-not $collectorText.Contains($bannedToken)) "i2-ban-source-embeds:$bannedToken" 'the collector must not embed this former frozen-input token (external freeze manifest is the only channel)'
}
$sentinelLines = @(Select-String -Path $CollectorPath -Pattern 'REPLACE_BEFORE_LIVE' -SimpleMatch)
Assert-True (@($sentinelLines).Count -eq 1 -and $sentinelLines[0].Line -like '*-like*') 'i2-sentinel-token-only-in-detection-scan' ("occurrences=$(@($sentinelLines).Count); the sentinel residue scan is the ONLY allowed use")
$hex64Literals = @([regex]::Matches($collectorText, '\b[A-Fa-f0-9]{64}\b') | ForEach-Object { $_.Value })
Assert-True (@($hex64Literals).Count -eq 0) 'i2-ban-source-embeds-64hex-literals' ("found=$(@($hex64Literals).Count) — no 64-hex constant (self SHA or pin) may live in the collector source")

$gitPrefixDollar = "return [string[]]@('--no-pager', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=NUL')"
Assert-True ($collectorText.Contains($gitPrefixDollar)) 'ast-git-prefix-literal-exact' 'prefix argv literal differs from frozen form'

# git-branch-matches-freeze (AC3-BRANCH-REF-MISMATCH fix): the runtime full
# symbolic-ref must be compared through the pure helper against the manifest
# SHORT branch name; the old direct $branchRef -ceq $manifestBranch compare of
# a full ref against a short name must never come back.
$branchCompareCall = '$branchOk = Test-BranchRefMatchesManifest -BranchRef $branchRef -ManifestBranch $manifestBranch'
Assert-True ($collectorText.Contains($branchCompareCall)) 'ast-branch-ref-compare-via-pure-helper' 'git-branch-matches-freeze must route the runtime symbolic-ref through Test-BranchRefMatchesManifest'
Assert-True (-not $collectorText.Contains('$branchRef -ceq $manifestBranch')) 'ast-branch-ref-no-direct-full-vs-short-compare' 'a direct case-sensitive compare of the full runtime ref against the manifest short name is the fixed defect and must stay removed'

# git-toplevel-matches-worktree (AC3-GIT-TOPLEVEL-PATH-SEPARATOR fix): the
# runtime toplevel and the frozen worktree must BOTH be normalized to Windows
# separators inside the pure helper before the case-insensitive compare; the
# old single-sided $toplevel -ieq ($manifestWorktree -replace '/', '\')
# compare (which failed the same absolute path reported by Git for Windows
# with forward slashes) must never come back.
$toplevelCompareCall = '$toplevelOk = Test-GitToplevelMatchesWorktree -Toplevel $toplevel -Worktree $manifestWorktree'
Assert-True ($collectorText.Contains($toplevelCompareCall)) 'ast-toplevel-compare-via-pure-helper' 'git-toplevel-matches-worktree must route both sides through Test-GitToplevelMatchesWorktree'
Assert-True (-not $collectorText.Contains('$toplevel -ieq ($manifestWorktree')) 'ast-toplevel-no-single-sided-normalization' 'a single-sided normalized compare (the AC3-GIT-TOPLEVEL-PATH-SEPARATOR defect) must stay removed'

# git index source (X6-SR-01 fix): the index integrity check must resolve the
# sampled index through THIS worktree's own absolute git dir; the common-dir
# form (which returns the MAIN repository .git for a linked worktree, so the
# old check sampled the wrong index and was vulnerable to unrelated main-repo
# git activity) must never come back.
Assert-True ($collectorText.Contains("@('rev-parse', '--absolute-git-dir')")) 'ast-index-git-dir-source-absolute-git-dir' 'the worktree git dir must be queried with rev-parse --absolute-git-dir (the linked-worktree gitdir, never the main repository .git)'
Assert-True (-not $collectorText.Contains('--git-common-dir')) 'ast-ban-common-dir-index-source' 'the common-dir gitdir query (returns the MAIN repository .git for a linked worktree; the X6-SR-01 defect) must stay removed from the collector source'
Assert-True ($collectorText.Contains("Add-Check -Id 'worktree-git-index-after-unchanged'")) 'ast-worktree-index-check-id-present' 'the index-unchanged check must be named for the worktree gitdir index it actually samples'

# freeze-manifest placement (X6-SR-02 fix): the placement gate must reject
# dot-segment paths before any comparison, compare on lexically normalized
# paths, protect BOTH the Task worktree AND the main repository root, and
# require a reparse-free manifest path chain before the bytes are read.
Assert-True ($collectorText.Contains('Test-PathOutsideRepository -Path $FreezeManifestPath -RepositoryRoots @($script:Worktree, $script:MainRepositoryRoot)')) 'ast-freeze-placement-dual-root-gate' 'the freeze manifest must be gated outside BOTH the Task worktree and the main repository root'
Assert-True ($collectorText.Contains('Test-PathContainsDotSegment -Path $FreezeManifestPath')) 'ast-freeze-placement-dot-segment-gate' 'a freeze manifest path containing a . or .. segment must be rejected before any comparison'
Assert-True ($collectorText.Contains('Test-PathAncestorsOrdinary -Path $FreezeManifestPath')) 'ast-freeze-placement-reparse-chain-gate' 'the freeze manifest path chain must be verified reparse-free before the manifest bytes are read'
Assert-True (-not $collectorText.Contains('Test-PathOutsideRepository -Path $FreezeManifestPath -Worktree $script:Worktree')) 'ast-freeze-placement-single-root-form-removed' 'the single-root worktree-only placement check (the X6-SR-02 defect) must stay removed'

# --- helper-process observation output envelope (AC3-WHOAMI-HELPER-OUTPUT-SHAPE
#     resolution): BOTH Invoke-HelperProcess producer paths (the success path
#     right after exit capture AND the exception path inside the catch guard)
#     must build output.value.{stdout,stderr} carrying the verbatim
#     ConvertTo-RawBytesRecord records — the SAME envelope Invoke-InProcessGetter
#     emits and every existing consumer and /output/value/... JSON pointer
#     reads. Pure static source assertions only: no collector, git child,
#     whoami child or live query is ever started here.
$helperFnAst = $collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -ceq 'Invoke-HelperProcess' }, $true) | Select-Object -First 1
Assert-True ($null -ne $helperFnAst) 'helper-shape-producer-function-found' 'Invoke-HelperProcess definition not found in the collector AST'
$helperFnText = if ($null -ne $helperFnAst) { $helperFnAst.Extent.Text } else { '' }
$helperConstructions = [regex]::Matches($helperFnText, '\$obs\.output = \[ordered\]@\{')
Assert-True (@($helperConstructions).Count -eq 2) 'helper-shape-exactly-two-producer-constructions' ("constructions=$(@($helperConstructions).Count); expected exactly one success path and one exception path, no more")
$helperWrapped = [regex]::Matches($helperFnText, '\$obs\.output = \[ordered\]@\{\s+value = \[ordered\]@\{')
Assert-True (@($helperWrapped).Count -eq 2) 'helper-shape-both-constructions-value-wrapped' ("wrapped=$(@($helperWrapped).Count); every output construction must open with value = [ordered]@{")
$helperLegacy = [regex]::Matches($helperFnText, '\$obs\.output = \[ordered\]@\{\s+stdout')
Assert-True (@($helperLegacy).Count -eq 0) 'helper-shape-no-legacy-unwrapped-output' 'the legacy unwrapped output.{stdout,stderr} construction (the AC3-WHOAMI-HELPER-OUTPUT-SHAPE defect) must stay removed from both paths'
$successEnvelope = [regex]::Match($helperFnText, '\$obs\.output = \[ordered\]@\{\s+value = \[ordered\]@\{\s+stdout = ConvertTo-RawBytesRecord -Bytes \(\$stdoutMs\.ToArray\(\)\)\s+stderr = ConvertTo-RawBytesRecord -Bytes \(\$stderrMs\.ToArray\(\)\)\s+\}\s+\}\s+if \(\$AllowedExit -contains \$process\.ExitCode\)')
Assert-True $successEnvelope.Success 'helper-shape-success-path-value-envelope' 'the success path (directly before the AllowedExit state decision) must emit output.value.{stdout,stderr} verbatim ConvertTo-RawBytesRecord records'
$exceptionEnvelope = [regex]::Match($helperFnText, 'if \(\$null -eq \$obs\.output\) \{\s+(?:#[^\r\n]*\s*)*\$obs\.output = \[ordered\]@\{\s+value = \[ordered\]@\{\s+stdout = ConvertTo-RawBytesRecord -Bytes \(\$stdoutMs\.ToArray\(\)\)\s+stderr = ConvertTo-RawBytesRecord -Bytes \(\$stderrMs\.ToArray\(\)\)')
Assert-True $exceptionEnvelope.Success 'helper-shape-exception-path-value-envelope' 'the exception path (inside the catch output guard) must emit the SAME output.value.{stdout,stderr} envelope — no second producer shape'
$valueConsumerReads = [regex]::Matches($collectorText, '\.observation\.output\.value\.stdout\.')
Assert-True ((@($valueConsumerReads).Count -ge 9) -and $collectorText.Contains('$whoami.observation.output.value.stdout.text')) 'helper-shape-consumers-read-value-envelope' ("reads=$(@($valueConsumerReads).Count); whoami and all git helper consumers must keep reading output.value.stdout")
$helperValuePointers = [regex]::Matches($collectorText, '/output/value/stdout')
Assert-True (@($helperValuePointers).Count -ge 4) 'helper-shape-json-pointers-target-value-envelope' ("pointers=$(@($helperValuePointers).Count); the git-pin checks /output/value/stdout pointers must stay intact")

# --- history isolation static bans (Task forbidden scope) ---
Write-Output '--- history isolation static bans ---'
foreach ($banned in @('attempt6', 'agent-output/codex/P02PRE', 'agent-output/zcode/P02PRE', 'verification/P02PRE', 'P02PRE-R1H-H1-CURRENT', 'p02pre-r1h-round6')) {
    Assert-True (-not $collectorText.Contains($banned)) "history-ban-source-must-not-reference:$banned" 'collector source must not reference historical inputs/outputs/conclusions'
}

# --- Task identity pins ---
$runIdParam = $collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.ParameterAst] -and $args[0].Name.VariablePath.UserPath -ceq 'RunId' }, $true) | Select-Object -First 1
$runIdValidated = ($null -ne $runIdParam) -and ($runIdParam.Extent.Text.Contains('ValidatePattern'))
Assert-True $runIdValidated 'runid-param-validatepattern' 'RunId parameter must carry ValidatePattern (unique RunId contract)'

$addCheckFn = $collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -eq 'Add-Check' }, $true) | Select-Object -First 1
$addCheckResolves = ($null -ne $addCheckFn) -and ($addCheckFn.Extent.Text.Contains('Resolve-JsonPointer'))
Assert-True $addCheckResolves 'add-check-resolves-pointer-at-runtime' 'Add-Check must resolve every observedPointer against existing observations at runtime'

$freezeValidators = @('Test-FreezeManifestShape', 'Test-FreezeManifestBinding')
$fsApiTokens = @('[IO.File]', '[IO.Directory]', 'ReadAllBytes', 'GetAttributes', 'Get-Item', 'Test-Path ', '.Exists(')
foreach ($fnName in $freezeValidators) {
    $fnAst = $collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -eq $fnName }, $true) | Select-Object -First 1
    $isPure = $null -ne $fnAst
    if ($null -ne $fnAst) {
        foreach ($tok in $fsApiTokens) {
            if ($fnAst.Extent.Text.Contains($tok)) { $isPure = $false }
        }
    }
    Assert-True $isPure "freeze-validator-is-pure:$fnName" "$fnName must be a pure validator (no filesystem API; path-string checks like IsPathRooted are allowed)"
}
$bytesFn = $collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -eq 'Test-FreezeManifestBytes' }, $true) | Select-Object -First 1
$bytesFnPure = ($null -ne $bytesFn) -and ($bytesFn.Extent.Text.Contains('Get-Sha256HexFromBytes'))
Assert-True $bytesFnPure 'freeze-bytes-binding-uses-shared-hash' 'Test-FreezeManifestBytes must bind via the shared pure SHA-256 helper'

$manifestParam = $collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.ParameterAst] -and $args[0].Name.VariablePath.UserPath -ceq 'FreezeManifestSha256' }, $true) | Select-Object -First 1
$manifestParamValidated = ($null -ne $manifestParam) -and ($manifestParam.Extent.Text.Contains('ValidatePattern'))
Assert-True $manifestParamValidated 'freeze-manifest-sha-param-validatepattern' 'FreezeManifestSha256 must carry a ValidatePattern (independent argv-side integrity binding)'

# The freeze gate and the output-exists check must run BEFORE the first
# CreateNew in the main sequence (I2: all invalid input fails before any
# output/process side effect).
function Find-LineNumber([string]$Pattern, [int]$Skip = 0) {
    $matches2 = @(Select-String -Path $CollectorPath -Pattern $Pattern -SimpleMatch)
    if ($matches2.Count -le $Skip) { return -1 }
    return $matches2[$Skip].LineNumber
}
$lineShapeCall = Find-LineNumber 'Test-FreezeManifestShape -Manifest $manifest -RunId $RunId'
$lineBindingCall = Find-LineNumber 'Test-FreezeManifestBinding -Manifest $manifest -RunId $RunId'
$lineOutputExists = Find-LineNumber 'Require (-not [IO.File]::Exists($outputFile))'
$lineCreateNew = Find-LineNumber '$script:Stream = Open-ExclusiveCreateNew'
Assert-True ($lineShapeCall -gt 0 -and $lineBindingCall -gt $lineShapeCall -and $lineOutputExists -gt $lineBindingCall -and $lineCreateNew -gt $lineOutputExists) 'i2-freeze-gate-and-output-exists-precede-createnew' ("shape=$lineShapeCall binding=$lineBindingCall outputExists=$lineOutputExists createNew=$lineCreateNew")
$linePreflightCall = Find-LineNumber '$script:OutputPreflight = New-OutputPreflightCapture'
$linePostCreate = Find-LineNumber '$script:OutputPostCreate = New-OutputPostCreateFacts'
Assert-True ($linePreflightCall -gt 0 -and $lineCreateNew -gt $linePreflightCall -and $linePostCreate -gt $lineCreateNew) 'capture-before-createnew-before-postfacts' ("preflight=$linePreflightCall createNew=$lineCreateNew postFacts=$linePostCreate")

# Outer catch must call the shared failure classification helper.
Assert-True ($collectorText.Contains('Get-CollectorFailureClassification -Message $message -BlockedReasons $script:BlockedReasons')) `
    'catch-calls-shared-classification' 'collector outer catch must call shared Get-CollectorFailureClassification helper'

# Partial preservation: the writer flushes every line and the finally block only
# disposes (never deletes/rewrites); exit code is reported separately.
$writerFn = $collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -eq 'Write-StreamLine' }, $true) | Select-Object -First 1
$writerFlushes = ($null -ne $writerFn) -and ($writerFn.Extent.Text.Contains('Flush'))
Assert-True $writerFlushes 'partial-preservation-stream-flushes-every-line' 'Write-StreamLine must flush every line immediately so partial evidence survives'
# Deletion ban enforced semantically: no Remove-Item/DeleteFile/Delete member or
# command may exist anywhere in the collector (checked in the bans above); the
# finally block must only dispose streams.
$finallyBlock = [regex]::Match($collectorText, 'finally \{[\s\S]*\n\}').Value
Assert-True ($finallyBlock.Contains('Dispose') -and -not $finallyBlock.Contains('Remove-Item') -and -not $finallyBlock.Contains('Delete')) 'partial-preservation-finally-only-disposes' 'the collector finally block must only dispose (never delete/truncate the partial output)'
Assert-True ($collectorText.Contains('exit $script:ExitCode')) 'exit-code-reported-separately' 'OS exit must come from the recorded ExitCode, not from swallowing failures'

# ---------------------------------------------------------------------------
# Extract pure functions from the executor AST into memory (definitions only;
# the executor top-level param/preflight/main never runs)
# ---------------------------------------------------------------------------
Write-Output '--- extract pure functions from collector AST (in-memory definitions only) ---'
foreach ($name in $requiredFunctions) {
    $fnAst = $collectorAst.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -eq $name }, $true) |
        Select-Object -First 1
    Assert-True ($null -ne $fnAst) "extract-function-present:$name" 'function definition not found'
    if ($null -ne $fnAst) {
        Invoke-Expression $fnAst.Extent.Text
    }
}

# ---------------------------------------------------------------------------
# Raw-output fidelity fixtures (including NUL)
# ---------------------------------------------------------------------------
Write-Output '--- raw-output fidelity (NUL-inclusive) ---'
$emptySha256 = 'E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855'
$abcSha256 = 'BA7816BF8F01CFEA414140DE5DAE2223B00361A396177A9CB410FF61F20015AD'

$emptyRecord = ConvertTo-RawBytesRecord -Bytes ([byte[]]@())
Assert-True ($emptyRecord.bytesCount -eq 0 -and $emptyRecord.sha256 -ceq $emptySha256 -and $emptyRecord.base64 -ceq '') 'raw-empty-not-missing' 'empty byte stream must stay a real observation with empty SHA-256, not null'

$abcBytes = [Text.Encoding]::UTF8.GetBytes('abc')
$abcRecord = ConvertTo-RawBytesRecord -Bytes $abcBytes
Assert-True ($abcRecord.sha256 -ceq $abcSha256) 'raw-sha256-known-vector-abc' ("got=$($abcRecord.sha256)")
Assert-True ($abcRecord.text -ceq 'abc' -and -not $abcRecord.textOmitted) 'raw-utf8-text-lossless' ("text=$($abcRecord.text)")

$nulBytes = [byte[]](0x3F, 0x3F, 0x20, 0x61, 0x00, 0x3F, 0x3F, 0x20, 0x62, 0x00)
$nulRecord = ConvertTo-RawBytesRecord -Bytes $nulBytes
Assert-True ($nulRecord.bytesCount -eq 10 -and $nulRecord.nulCount -eq 2) 'raw-nul-counts' ("bytes=$($nulRecord.bytesCount) nul=$($nulRecord.nulCount)")
Assert-True ($null -eq $nulRecord.text -and $nulRecord.textOmitted -and $nulRecord.textOmitReason.Contains('NUL')) 'raw-nul-text-omitted-with-reason' ("reason=$($nulRecord.textOmitReason)")
$roundtrip = [Convert]::FromBase64String($nulRecord.base64)
$roundtripEqual = ($roundtrip.Length -eq $nulBytes.Length)
if ($roundtripEqual) { for ($i = 0; $i -lt $nulBytes.Length; $i++) { if ($roundtrip[$i] -ne $nulBytes[$i]) { $roundtripEqual = $false; break } } }
Assert-True $roundtripEqual 'raw-nul-base64-roundtrip-byte-exact' 'base64 decode must equal original bytes including NULs'

$invalidUtf8 = [byte[]](0xFF, 0xFE, 0x41)
$invalidRecord = ConvertTo-RawBytesRecord -Bytes $invalidUtf8
Assert-True ($null -eq $invalidRecord.text -and $invalidRecord.textOmitted -and $invalidRecord.textOmitReason.Contains('UTF-8')) 'raw-invalid-utf8-text-null' ("reason=$($invalidRecord.textOmitReason)")
Assert-True ($null -ne $invalidRecord.base64) 'raw-invalid-utf8-base64-retained' 'base64 must remain canonical when text impossible'

# Split-NulRecords fidelity
$statusLike = [byte[]]([Text.Encoding]::UTF8.GetBytes('? doc/tasks/a.md') + [byte[]](0) + [Text.Encoding]::UTF8.GetBytes('? tools/p02/b.ps1') + [byte[]](0))
$splitRecords = @(Split-NulRecords -Bytes $statusLike)
Assert-True ($splitRecords.Count -eq 2) 'split-two-records' ("count=$($splitRecords.Count)")
Assert-True ($splitRecords[0].text -ceq '? doc/tasks/a.md' -and $splitRecords[1].text -ceq '? tools/p02/b.ps1') 'split-record-texts-exact' ("t0=$($splitRecords[0].text) t1=$($splitRecords[1].text)")
$rebuilt = [byte[]](@() + [Text.Encoding]::UTF8.GetBytes($splitRecords[0].text) + [byte[]](0) + [Text.Encoding]::UTF8.GetBytes($splitRecords[1].text) + [byte[]](0))
$rebuiltEqual = ($rebuilt.Length -eq $statusLike.Length)
if ($rebuiltEqual) { for ($i = 0; $i -lt $statusLike.Length; $i++) { if ($rebuilt[$i] -ne $statusLike[$i]) { $rebuiltEqual = $false; break } } }
Assert-True $rebuiltEqual 'split-join-roundtrip-byte-exact' 'rejoined records must equal the original NUL stream'

$unterminated = @(Split-NulRecords -Bytes ([Text.Encoding]::UTF8.GetBytes('xy')))
Assert-True ($unterminated.Count -eq 1 -and $unterminated[0].unterminated -eq $true -and $unterminated[0].text -ceq 'xy') 'split-unterminated-trailing-recorded' ("count=$($unterminated.Count) flag=$($unterminated[0].unterminated)")
$zeroRecords = @(Split-NulRecords -Bytes ([byte[]](0, 0)))
Assert-True ($zeroRecords.Count -eq 2 -and $zeroRecords[0].text -ceq '' -and $zeroRecords[0].length -eq 0) 'split-zero-length-records-verbatim' ("count=$($zeroRecords.Count)")
$invalidRecordSplit = @(Split-NulRecords -Bytes ([byte[]](0xFF, 0x00)))
Assert-True ($invalidRecordSplit.Count -eq 1 -and $null -eq $invalidRecordSplit[0].text) 'split-invalid-utf8-text-null' 'non-UTF-8 record text must be null, never synthesized'

# ---------------------------------------------------------------------------
# JSON Pointer integrity (fixture graph + closed-line shape)
# ---------------------------------------------------------------------------
Write-Output '--- json pointer integrity ---'
$graph = [ordered]@{
    schema = 'P02-NEW-TIME-X6-executor-1'
    observations = @(
        [ordered]@{ id = 'git-status-verbatim'; output = [ordered]@{ stdout = [ordered]@{ base64 = 'QUJD'; sha256 = 'X'; nulCount = 0 } } },
        [ordered]@{ id = 'identity-sid'; output = [ordered]@{ value = [ordered]@{ sid = 'S-1-5-21' } } }
    )
    checks = @(
        [ordered]@{ id = 'c1'; observedPointer = '/observations/0/output/stdout/base64' },
        [ordered]@{ id = 'c2'; observedPointer = '/observations/1/output/value/sid' }
    )
}
$r1 = Resolve-JsonPointer -Graph $graph -Pointer '/observations/0/output/stdout/base64'
Assert-True ($r1.found -and $r1.value -ceq 'QUJD') 'pointer-resolve-nested-value' ("found=$($r1.found) value=$($r1.value)")
$r2 = Resolve-JsonPointer -Graph $graph -Pointer '/observations/9/output/stdout'
Assert-True (-not $r2.found) 'pointer-dangling-index-not-found' 'out-of-range index must report found=false, never fabricate'
$r3 = Resolve-JsonPointer -Graph $graph -Pointer 'observations/0'
Assert-True (-not $r3.found) 'pointer-missing-leading-slash-rejected' 'malformed pointer must report found=false'
$escapeGraph = [ordered]@{ 'a/b' = [ordered]@{ 'c~d' = 'escaped' } }
$r4 = Resolve-JsonPointer -Graph $escapeGraph -Pointer '/a~1b/c~0d'
Assert-True ($r4.found -and $r4.value -ceq 'escaped') 'pointer-rfc6901-escape-tokens' ("found=$($r4.found) value=$($r4.value)")
$allChecksResolvable = $true
foreach ($c in $graph.checks) {
    $rr = Resolve-JsonPointer -Graph $graph -Pointer $c.observedPointer
    if (-not $rr.found) { $allChecksResolvable = $false }
}
Assert-True $allChecksResolvable 'pointer-all-check-pointers-resolve' 'every check observedPointer must resolve inside the closed graph'

# ---------------------------------------------------------------------------
# Fail-closed check factory + observation records
# ---------------------------------------------------------------------------
Write-Output '--- fail-closed check factory and observation records ---'
Assert-Throws -Body { New-CheckRecord -Id 'x' -Category 'c' -Expected 'e' -ObservedPointer 'collection A' -ObservedSummary 's' -Result 'PASS' } `
    -Name 'check-factory-rejects-unparseable-label' -Detail 'collection-style label must throw'
Assert-Throws -Body { New-CheckRecord -Id 'x' -Category 'c' -Expected 'e' -ObservedPointer '' -ObservedSummary 's' -Result 'PASS' } `
    -Name 'check-factory-rejects-empty-pointer' -Detail 'empty pointer must throw'
Assert-Throws -Body { New-CheckRecord -Id '' -Category 'c' -Expected 'e' -ObservedPointer '/observations/0' -ObservedSummary 's' -Result 'PASS' } `
    -Name 'check-factory-rejects-empty-id' -Detail 'empty id must throw'
Assert-Throws -Body { New-CheckRecord -Id 'x' -Category 'c' -Expected '' -ObservedPointer '/observations/0' -ObservedSummary 's' -Result 'PASS' } `
    -Name 'check-factory-rejects-empty-expected' -Detail 'empty expected must throw'
Assert-Throws -Body { New-CheckRecord -Id 'x' -Category 'c' -Expected 'e' -ObservedPointer '/observations/0' -ObservedSummary 's' -Result 'MAYBE' } `
    -Name 'check-factory-rejects-unknown-result' -Detail 'result enum must be enforced'
$validCheck = New-CheckRecord -Id 'x' -Category 'c' -Expected 'e' -ObservedPointer '/observations/0/output/stdout' -ObservedSummary 's' -Result 'NOT_VERIFIED' -Note 'n'
Assert-True ($validCheck.id -ceq 'x' -and $validCheck.observedPointer -ceq '/observations/0/output/stdout' -and $validCheck.result -ceq 'NOT_VERIFIED') 'check-factory-valid-record-shape' 'valid record must carry all contract fields'

Assert-Throws -Body { New-ObservationRecord -Id 'x' -Kind 'live-probe' } -Name 'observation-factory-rejects-unknown-kind' -Detail 'unknown observation kind must throw'
$obs = New-ObservationRecord -Id 'x' -Kind 'helper-process'
Assert-True ($obs.state -ceq 'NOT_STARTED' -and $obs.seq -eq -1) 'observation-factory-initial-state' 'fresh observation must start NOT_STARTED with seq -1'
Assert-Throws -Body { New-ObservationRecord -Id '' -Kind 'helper-process' } -Name 'observation-factory-rejects-empty-id' -Detail 'empty id must throw'

$errObs = Add-ObservationException -Observation $obs -Stage 'getter' -ErrorRecord ([pscustomobject]@{ Exception = [InvalidOperationException]::new('boom') })
Assert-True ($errObs.state -ceq 'ERROR' -and $errObs.exception.type -ceq 'System.InvalidOperationException' -and $errObs.exception.stage -ceq 'getter') 'observation-exception-shape' 'exception observations must carry stage/type/message'

# ---------------------------------------------------------------------------
# Probe classification + check-result mapping (absence vs non-absence errors)
# ---------------------------------------------------------------------------
Write-Output '--- probe classification ---'
function New-WrappedException {
    # Real two-level exception wrapper (InnerException set via the constructor).
    try {
        try { throw [UnauthorizedAccessException]::new('inner cause') } catch { throw [InvalidOperationException]::new('outer wrapper', $_.Exception) }
    } catch { return $_.Exception }
}
function New-WrappedWrappedFileNotFound {
    # Outer wrapper whose INNER exception is FileNotFound: the collector must
    # unwrap before classifying, so this is a legal absence, not an error.
    try {
        try { throw [IO.FileNotFoundException]::new('inner file-not-found') } catch { throw [InvalidOperationException]::new('outer wrapper', $_.Exception) }
    } catch { return $_.Exception }
}
$absentValue = Get-PathProbeValueFromAttributes -Path 'Z:/no/such/path' -Attributes $null -Exception ([IO.FileNotFoundException]::new('gone'))
Assert-True ($absentValue.absent -eq $true -and $absentValue.exists -eq $false -and $null -eq $absentValue.attributeError) 'probe-genuine-absence-shape' 'FileNotFound must classify as legal absence with complete field shape'
$wrappedAbsence = Get-PathProbeValueFromAttributes -Path 'Z:/no/such/path' -Attributes $null -Exception (New-WrappedWrappedFileNotFound)
Assert-True ($wrappedAbsence.absent -eq $true) 'probe-inner-file-not-found-unwrapped' 'a wrapped FileNotFound inner exception must still classify as legal absence'
$errorValue = Get-PathProbeValueFromAttributes -Path 'Z:/no/such/path' -Attributes $null -Exception ([UnauthorizedAccessException]::new('denied'))
Assert-True ($errorValue.absent -eq $false -and $null -ne $errorValue.attributeError -and $null -ne $errorValue.hresult) 'probe-non-absence-error-shape' 'access errors must NOT report legal absence'
$wrappedError = Get-PathProbeValueFromAttributes -Path 'Z:/no/such/path' -Attributes $null -Exception (New-WrappedException)
Assert-True ($wrappedError.absent -eq $false -and $null -ne $wrappedError.attributeError) 'probe-inner-error-unwrapped' 'a wrapped non-IO inner exception must unwrap to a non-absence error'
Assert-True ((Get-ProbeCheckResult -ProbeValue $errorValue) -ceq 'NOT_VERIFIED') 'probe-error-maps-to-not-verified' 'non-absence errors must map to NOT_VERIFIED, never PASS'
$attrValue = Get-PathProbeValueFromAttributes -Path 'Z:/some/file' -Attributes ([IO.FileAttributes]::Archive) -Exception $null
Assert-True ($attrValue.exists -and -not $attrValue.isDirectory -and $attrValue.isFile) 'probe-attribute-exists-shape' 'attributes without exception must classify as existing'
Assert-True ((Get-ProbeCheckResult -ProbeValue $attrValue) -ceq 'PASS') 'probe-ok-maps-to-pass' 'clean probes map to PASS'

# ---------------------------------------------------------------------------
# History path isolation (pure; positive + negative + discrimination)
# ---------------------------------------------------------------------------
Write-Output '--- history path isolation ---'
$frozenSegments = @('P02PRE-R1H-H1', 'P02PRE-R1H-H2', 'P02PRE-R1H-P2-1')
Assert-True (-not (Test-PathContainsHistorySegment -Path 'G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/run-x.json' -ForbiddenSegments $frozenSegments)) 'isolation-clean-task-path-passes' 'the Task output path must not match any frozen historical segment'
Assert-True (Test-PathContainsHistorySegment -Path 'G:/x/P02PRE-R1H-H2/run-y.json' -ForbiddenSegments $frozenSegments) 'isolation-segment-hit-detected' 'a path containing an exact frozen historical segment must be detected'
Assert-True (Test-PathContainsHistorySegment -Path 'G:/x/p02pre-r1h-p2-1/ev.json' -ForbiddenSegments $frozenSegments) 'isolation-case-insensitive-segment-hit' 'exact segment matching must be case-insensitive'
# I1 (DSH R-01 / Codex adjudication): real historical directory names extend a
# family name with a hyphen delimiter; they MUST match. Names use path strings
# only — no historical file or directory is enumerated, opened or read.
Assert-True (Test-PathContainsHistorySegment -Path 'G:/CODEX/New Manga.workspace/agent-output/zcode/P02PRE-R1H-H2-COLLECTOR/run-y.json' -ForbiddenSegments $frozenSegments) 'isolation-real-family-h2-collector-hits' 'real H2-family directory name (hyphen-delimited extension) must be detected'
Assert-True (Test-PathContainsHistorySegment -Path 'G:/CODEX/New Manga/verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/ev.md' -ForbiddenSegments $frozenSegments) 'isolation-real-family-p2-1-trace-hits' 'real P2-1-family directory name (hyphen-delimited extension) must be detected'
Assert-True (Test-PathContainsHistorySegment -Path 'G:/CODEX/New Manga/verification/P02PRE-R1H-H1-CURRENT-INPUT-REVIEW/ev.md' -ForbiddenSegments $frozenSegments) 'isolation-real-family-h1-current-hits' 'real H1-family directory name (hyphen-delimited extension) must be detected'
Assert-True (Test-PathContainsHistorySegment -Path 'G:/x/P02PRE-R1H-H1-CURRENT/old.json' -ForbiddenSegments $frozenSegments) 'isolation-real-family-h1-current-short-hits' 'the short real H1-family directory name from the R-01 repro must also be detected'
Assert-True (Test-PathContainsHistorySegment -Path 'G:/x/p02pre-r1h-h2-collector/run-y.json' -ForbiddenSegments $frozenSegments) 'isolation-real-family-case-insensitive-hits' 'hyphen-delimited family matching must be case-insensitive'
Assert-True (-not (Test-PathContainsHistorySegment -Path 'G:/x/P02PRE-R1H-H2X/ev.json' -ForbiddenSegments $frozenSegments)) 'isolation-superstring-not-segment' 'a longer segment whose character after the family name is not the hyphen delimiter (e.g. H2X) must NOT match'
Assert-True (-not (Test-PathContainsHistorySegment -Path 'G:/x/P02PRE-R1H-H2COLLECTOR/ev.json' -ForbiddenSegments $frozenSegments)) 'isolation-family-prefix-without-delimiter-not-matched' 'a family-prefixed segment without the hyphen delimiter must NOT match (no arbitrary substring)'
Assert-True (-not (Test-PathContainsHistorySegment -Path '' -ForbiddenSegments $frozenSegments) -and -not (Test-PathContainsHistorySegment -Path 'G:/x' -ForbiddenSegments @())) 'isolation-empty-inputs-safe' 'empty path or empty segment list must not throw or match'

$isoManifest = Assert-TaskPathIsolation -Paths @(
    'G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/run-x.json',
    'G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6',
    'G:/x/P02PRE-R1H-H1/old.json'
) -ForbiddenSegments $frozenSegments
Assert-True ($isoManifest.pathCount -eq 3 -and $isoManifest.anyUnderHistory -eq $true -and @($isoManifest.underHistoryPaths).Count -eq 1) 'isolation-manifest-counts' ("pathCount=$($isoManifest.pathCount) any=$($isoManifest.anyUnderHistory) hits=$(@($isoManifest.underHistoryPaths).Count)")
Assert-True ($isoManifest.underHistoryPaths[0] -like '*P02PRE-R1H-H1*') 'isolation-manifest-names-hit-path' 'the manifest must name the exact offending path'
Assert-True (@($isoManifest.pathManifest).Count -eq 3 -and $isoManifest.pathManifest[0].underHistory -eq $false) 'isolation-manifest-full-shape' 'every manifest entry must carry {path, underHistory}'

$isoClean = Assert-TaskPathIsolation -Paths @(
    'G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/run-x.json',
    'G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6'
) -ForbiddenSegments $frozenSegments
Assert-True ($isoClean.anyUnderHistory -eq $false) 'isolation-manifest-clean-passes' 'a clean Task-only manifest must show anyUnderHistory=false'

$isoRealFamily = Assert-TaskPathIsolation -Paths @(
    'G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/run-x.json',
    'G:/CODEX/New Manga.workspace/agent-output/zcode/P02PRE-R1H-H2-COLLECTOR/run-y.json'
) -ForbiddenSegments $frozenSegments
Assert-True ($isoRealFamily.anyUnderHistory -eq $true -and @($isoRealFamily.underHistoryPaths).Count -eq 1 -and $isoRealFamily.underHistoryPaths[0] -like '*H2-COLLECTOR*') 'isolation-manifest-names-real-family-hit' 'the manifest must name the real hyphen-delimited family directory as the offending path'

# ---------------------------------------------------------------------------
# Task X6 forbidden write scope (pure): the historical verification/P02/ root
# is a forbidden write root; the sibling Task directory verification/
# P02-NEW-TIME-X6/ must NOT be mis-flagged by the shorter root (separator
# boundary semantics), and the Task's own agent-output root stays legal.
# ---------------------------------------------------------------------------
Write-Output '--- x6 forbidden write prefix guard ---'
$x6WritePrefixes = [string[]]@('G:\CODEX\New Manga\verification\P02\')
Assert-True (Test-PathUnderAnyForbiddenPrefix -Path 'G:/CODEX/New Manga/verification/P02/run-x.json' -ForbiddenPrefixes $x6WritePrefixes) 'x6-write-guard-historical-p02-slash-form-hits' 'an output target under the slash-form historical verification/P02/ root must be rejected'
Assert-True (Test-PathUnderAnyForbiddenPrefix -Path 'G:\CODEX\New Manga\verification\P02\run-x.json' -ForbiddenPrefixes $x6WritePrefixes) 'x6-write-guard-historical-p02-backslash-form-hits' 'an output target under the backslash-form historical verification/P02/ root must be rejected'
Assert-True (Test-PathUnderAnyForbiddenPrefix -Path 'g:/codex/new manga/verification/p02/deep/nested/run-x.json' -ForbiddenPrefixes $x6WritePrefixes) 'x6-write-guard-case-insensitive-deep-hit' 'deep nested paths under the historical root must be rejected case-insensitively'
Assert-True (Test-PathUnderAnyForbiddenPrefix -Path 'G:\CODEX\New Manga\verification\P02' -ForbiddenPrefixes $x6WritePrefixes) 'x6-write-guard-root-itself-hits' 'the forbidden write root itself (no trailing separator) must be rejected'
Assert-True (-not (Test-PathUnderAnyForbiddenPrefix -Path 'G:\CODEX\New Manga\verification\P02-NEW-TIME-X6\executor\p02-new-time-x6.ps1' -ForbiddenPrefixes $x6WritePrefixes)) 'x6-write-guard-sibling-task-dir-not-hit' 'the sibling Task directory verification/P02-NEW-TIME-X6/ must NOT be flagged by the shorter verification/P02/ root (separator boundary)'
Assert-True (-not (Test-PathUnderAnyForbiddenPrefix -Path 'G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/run-x.json' -ForbiddenPrefixes $x6WritePrefixes)) 'x6-write-guard-task-output-dir-not-hit' 'the Task agent-output output root must stay legal'
Assert-True (-not (Test-PathUnderAnyForbiddenPrefix -Path 'G:\CODEX\OtherManga\verification\P02\run-x.json' -ForbiddenPrefixes $x6WritePrefixes)) 'x6-write-guard-other-repository-root-not-hit' 'a different repository root with the same trailing leaf names must not be flagged'
Assert-True (-not (Test-PathUnderAnyForbiddenPrefix -Path '' -ForbiddenPrefixes $x6WritePrefixes) -and -not (Test-PathUnderAnyForbiddenPrefix -Path 'G:/x/y.json' -ForbiddenPrefixes @())) 'x6-write-guard-empty-inputs-safe' 'empty path or empty prefix list must not throw or match'
Assert-True (-not (Test-PathUnderAnyForbiddenPrefix -Path 'G:/CODEX/New Manga/verification/P02X/run-x.json' -ForbiddenPrefixes $x6WritePrefixes)) 'x6-write-guard-superstring-leaf-not-hit' 'a directory whose name merely extends the root name without a separator boundary (P02X) must NOT be flagged'

# ---------------------------------------------------------------------------
# I2 external freeze-manifest input seam (pure/unit): missing, sentinel,
# malformed, hash-mismatch, incomplete, binding-failed and history-violating
# freeze input must all fail closed BEFORE any output/process side effect in
# the collector; a valid structure must pass the pure gate.
# ---------------------------------------------------------------------------
Write-Output '--- freeze manifest input seam ---'
$baselines = [ordered]@{
    manifestSchema = 'P02-NEW-TIME-X6-freeze-manifest-1'
    taskId = 'P02-NEW-TIME-X6'
    baseCommit = 'bc502e7aae07074fff7228d585674e87d53efcfd'
    expectedBranch = 'agent/zcode/P02-NEW-TIME-X6'
    worktree = 'G:/wt'
    outputDir = 'G:/out'
    pwshExe = 'C:/pwsh.exe'
    gitExe = 'C:/git.exe'
    whoamiExe = 'C:/whoami.exe'
    psVersion = '7.6.6'
    psEdition = 'Core'
    languageMode = 'FullLanguage'
    gitVersion = 'git version 2.52.0.windows.1'
    identityName = 'home-my\49745'
    identitySid = 'S-1-5-21-1'
}
$manifestHead = 'a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d4'
$collectorSelfSha = 'CDEFAB0123456789CDEFAB0123456789CDEFAB0123456789CDEFAB0123456789'
$validJson = @"
{
  "schema": "P02-NEW-TIME-X6-freeze-manifest-1",
  "task": "P02-NEW-TIME-X6",
  "runId": "selftest-run",
  "deliveryHead": "$manifestHead",
  "baseCommit": "bc502e7aae07074fff7228d585674e87d53efcfd",
  "branch": "agent/zcode/P02-NEW-TIME-X6",
  "cwd": "G:/wt",
  "worktree": "G:/wt",
  "outputDir": "G:/out",
  "outputTargets": ["run-selftest-run.json"],
  "identity": { "name": "home-my\\49745", "sid": "S-1-5-21-1" },
  "tools": { "pwshExe": "C:/pwsh.exe", "gitExe": "C:/git.exe", "whoamiExe": "C:/whoami.exe" },
  "expectedRuntime": { "psVersion": "7.6.6", "psEdition": "Core", "languageMode": "FullLanguage", "gitVersion": "git version 2.52.0.windows.1" },
  "contractPins": [ {"name":"collab","path":"G:/wt/doc/09_COLLABORATION.md","size":10,"sha256":"$collectorSelfSha"} ],
  "taskDeliverablePins": [ {"name":"executor-source","path":"G:/wt/verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1","size":9,"sha256":"$collectorSelfSha"} ],
  "mutableObservationPaths": [ "G:/wt/doc/STATUS.md" ]
}
"@
$validManifest = ConvertFrom-Json -InputObject $validJson
$shapeOk = Test-FreezeManifestShape -Manifest $validManifest -RunId 'selftest-run' -ExpectedBaselines $baselines
Assert-True ($shapeOk.valid -eq $true -and @($shapeOk.errors).Count -eq 0) 'freeze-manifest-valid-shape-passes' ("errors=$($shapeOk.errors -join ';')")
$bindingOk = Test-FreezeManifestBinding -Manifest $validManifest -RunId 'selftest-run' -ExpectedBaselines $baselines
Assert-True ($bindingOk.valid -eq $true -and @($bindingOk.errors).Count -eq 0) 'freeze-manifest-valid-binding-passes' ("errors=$($bindingOk.errors -join ';')")

foreach ($missingField in @('deliveryHead', 'cwd', 'outputTargets', 'contractPins', 'taskDeliverablePins', 'mutableObservationPaths', 'identity')) {
    $missing = ConvertFrom-Json -InputObject $validJson
    $missing.PSObject.Properties.Remove($missingField)
    $shapeMissing = Test-FreezeManifestShape -Manifest $missing -RunId 'selftest-run' -ExpectedBaselines $baselines
    Assert-True ($shapeMissing.valid -eq $false) "freeze-manifest-missing-field-fails:$missingField" ("errors=$($shapeMissing.errors -join ';')")
}

$sentinel = ConvertFrom-Json -InputObject $validJson
$sentinel.identity.name = 'REPLACE_BEFORE_LIVE_WITH_IDENTITY'
$shapeSentinel = Test-FreezeManifestShape -Manifest $sentinel -RunId 'selftest-run' -ExpectedBaselines $baselines
Assert-True ($shapeSentinel.valid -eq $false -and (@($shapeSentinel.errors | Where-Object { $_ -like '*sentinel*' }).Count -ge 1)) 'freeze-manifest-sentinel-residue-fails' ("errors=$($shapeSentinel.errors -join ';')")

$badHeadLen = ConvertFrom-Json -InputObject $validJson
$badHeadLen.deliveryHead = 'a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8a1b2c3d'
$shapeBadLen = Test-FreezeManifestShape -Manifest $badHeadLen -RunId 'selftest-run' -ExpectedBaselines $baselines
Assert-True ($shapeBadLen.valid -eq $false) 'freeze-manifest-head-40hex-format-fails' ("errors=$($shapeBadLen.errors -join ';')")

$incompletePin = ConvertFrom-Json -InputObject $validJson
$incompletePin.contractPins = @(ConvertFrom-Json -InputObject '{"name":"p1"}')
$shapeIncomplete = Test-FreezeManifestShape -Manifest $incompletePin -RunId 'selftest-run' -ExpectedBaselines $baselines
Assert-True ($shapeIncomplete.valid -eq $false -and (@($shapeIncomplete.errors | Where-Object { $_.StartsWith('contractPins[0]') }).Count -ge 1)) 'freeze-manifest-incomplete-pin-fails' ("errors=$($shapeIncomplete.errors -join ';')")

$bindingRunId = Test-FreezeManifestBinding -Manifest $validManifest -RunId 'other-run' -ExpectedBaselines $baselines
Assert-True ($bindingRunId.valid -eq $false -and (@($bindingRunId.errors | Where-Object { $_ -like '*runId*' }).Count -ge 1)) 'freeze-manifest-binding-runid-mismatch-fails' ("errors=$($bindingRunId.errors -join ';')")
$wrongBase = ConvertFrom-Json -InputObject $validJson
$wrongBase.baseCommit = 'ffffffffffffffffffffffffffffffffffffffff'
$bindingBase = Test-FreezeManifestBinding -Manifest $wrongBase -RunId 'selftest-run' -ExpectedBaselines $baselines
Assert-True ($bindingBase.valid -eq $false -and (@($bindingBase.errors | Where-Object { $_ -like '*baseCommit*' }).Count -ge 1)) 'freeze-manifest-binding-base-mismatch-fails' ("errors=$($bindingBase.errors -join ';')")
$noSelfPin = ConvertFrom-Json -InputObject $validJson
$otherPinJson = '{"name":"other","path":"G:/wt/x/other.ps1","size":1,"sha256":"' + $collectorSelfSha + '"}'
$noSelfPin.taskDeliverablePins = @(ConvertFrom-Json -InputObject $otherPinJson)
$bindingSelfPin = Test-FreezeManifestBinding -Manifest $noSelfPin -RunId 'selftest-run' -ExpectedBaselines $baselines
Assert-True ($bindingSelfPin.valid -eq $false -and (@($bindingSelfPin.errors | Where-Object { $_ -like '*self-pin*' }).Count -ge 1)) 'freeze-manifest-binding-missing-collector-self-pin-fails' ("errors=$($bindingSelfPin.errors -join ';')")

$manifestBytes = [Text.Encoding]::UTF8.GetBytes($validJson)
$integrityMismatch = Test-FreezeManifestBytes -Bytes $manifestBytes -ExpectedSha256 ('FF' * 32)
Assert-True ($integrityMismatch.match -eq $false -and $integrityMismatch.actualSha256 -ine ('FF' * 32)) 'freeze-manifest-hash-mismatch-fails' 'tampered or stale manifest bytes must fail the argv-side integrity binding'
$goodSha = Get-Sha256HexFromBytes -Bytes $manifestBytes
$integrityMatch = Test-FreezeManifestBytes -Bytes $manifestBytes -ExpectedSha256 $goodSha
Assert-True ($integrityMatch.match -eq $true) 'freeze-manifest-hash-match-passes' 'matching bytes must pass the integrity binding'

Assert-Throws -Body { ConvertFrom-Json -InputObject '{"schema": definitely not json' } `
    -Name 'freeze-manifest-malformed-json-fails' -Detail 'malformed JSON must fail before the shape gate (collector wraps this as FREEZE_MANIFEST_INVALID)'

$histManifest = ConvertFrom-Json -InputObject $validJson
$histManifest.taskDeliverablePins[0].path = 'G:/wt/P02PRE-R1H-H2-COLLECTOR/x.ps1'
$histPaths = @($histManifest.taskDeliverablePins | ForEach-Object { $_.path })
$histIso = Assert-TaskPathIsolation -Paths $histPaths -ForbiddenSegments $frozenSegments
Assert-True ($histIso.anyUnderHistory -eq $true -and $histIso.underHistoryPaths[0] -like '*H2-COLLECTOR*') 'freeze-manifest-history-violating-paths-fail-closed' 'a manifest pinning a historical family directory must be rejected by the history gate before any side effect'

# X6-SR-02 (I1): the placement rule now protects BOTH the Task worktree and
# the main repository root, compares on lexically normalized absolute paths,
# and rejects dot-segment/alias forms before any comparison. Pure in-memory
# assertions only ([IO.Path]::GetFullPath over an absolute path is lexical;
# no filesystem access).
$dualRoots = @('G:/wt', 'G:/mainrepo')
Assert-True (Test-PathOutsideRepository -Path 'G:/outside/freeze.json' -RepositoryRoots $dualRoots) 'freeze-manifest-outside-both-roots-accepted' 'a manifest outside BOTH the worktree and the main repository satisfies the placement rule'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:/wt/inside/freeze.json' -RepositoryRoots $dualRoots)) 'freeze-manifest-inside-worktree-rejected' 'a manifest inside the worktree must be rejected (no commit-cycle inputs)'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:/wt' -RepositoryRoots $dualRoots)) 'freeze-manifest-worktree-root-rejected' 'the worktree root itself is inside a protected root'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:/mainrepo/freeze.json' -RepositoryRoots $dualRoots)) 'freeze-manifest-inside-main-repository-rejected' 'a manifest inside the MAIN repository checkout must be rejected even though it is outside the worktree (X6-SR-02)'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:/mainrepo' -RepositoryRoots $dualRoots)) 'freeze-manifest-main-repository-root-rejected' 'the main repository root itself is a protected root'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:/mainrepo/verification/P02/freeze.json' -RepositoryRoots $dualRoots)) 'freeze-manifest-main-repo-historical-p02-rejected' 'a manifest planted in the main repository historical verification/P02/ tree must be rejected by the main-root guard'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:/zz/../wt/freeze.json' -RepositoryRoots $dualRoots)) 'freeze-manifest-dot-dot-alias-rejected' 'a path aliasing into the worktree through a .. segment must never count as outside (fail-closed before normalization)'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:/wt/./freeze.json' -RepositoryRoots $dualRoots)) 'freeze-manifest-dot-segment-alias-rejected' 'a path containing a . segment must never count as outside'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:\wt\inside\freeze.json' -RepositoryRoots $dualRoots)) 'freeze-manifest-backslash-form-inside-rejected' 'backslash separator forms must normalize to the same protected root'
Assert-True (-not (Test-PathOutsideRepository -Path 'g:/WT/freeze.json' -RepositoryRoots $dualRoots)) 'freeze-manifest-case-insensitive-inside-rejected' 'case drift must not cross the root boundary (case-insensitive compare)'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:/outside/freeze.json' -RepositoryRoots @())) 'freeze-manifest-empty-root-list-fail-closed' 'an empty protected-root list must fail closed (never accept)'
$realRoots = @('G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6', 'G:/CODEX/New Manga')
Assert-True (Test-PathOutsideRepository -Path 'G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/x6-run-1/freeze-manifest.json' -RepositoryRoots $realRoots) 'freeze-manifest-task-agent-output-root-accepted' 'the Task agent-output root stays a legal freeze location (outside BOTH real roots; the sibling .workspace directory is not the main repository)'
Assert-True (-not (Test-PathOutsideRepository -Path 'G:/CODEX/New Manga/verification/P02-NEW-TIME-X6/freeze.json' -RepositoryRoots $realRoots)) 'freeze-manifest-main-repo-sibling-task-path-rejected' 'a path under the main repository (even a same-named Task directory) must be rejected'

Assert-True (Test-PathContainsDotSegment -Path 'G:/a/../b.json') 'dot-segment-detector-hits-parent' 'the dot-segment detector must flag a .. segment'
Assert-True (Test-PathContainsDotSegment -Path 'G:/a/./b.json') 'dot-segment-detector-hits-current' 'the dot-segment detector must flag a . segment'
Assert-True (Test-PathContainsDotSegment -Path 'G:\a\..\b.json') 'dot-segment-detector-backslash-form' 'the dot-segment detector must accept backslash separators'
Assert-True (-not (Test-PathContainsDotSegment -Path 'G:/a/b.json')) 'dot-segment-detector-clean-path-passes' 'an ordinary path must not be flagged'
Assert-True (-not (Test-PathContainsDotSegment -Path 'G:/a/b.json.') -and -not (Test-PathContainsDotSegment -Path 'G:/a/.hidden')) 'dot-segment-detector-filename-dots-ignored' 'dots inside or around a filename (extension, dotfile) are not dot segments'
Assert-True (-not (Test-PathContainsDotSegment -Path '')) 'dot-segment-detector-empty-safe' 'empty input must not throw or match'

$manifestInvalidRes = Get-CollectorFailureClassification -Message 'FREEZE_MANIFEST_INVALID: manifest bytes do not match the argv-supplied expected SHA-256'
Assert-True ($manifestInvalidRes.exitCode -eq 3 -and $manifestInvalidRes.disposition -ceq 'BLOCKED_INPUT_NOT_FROZEN') 'freeze-manifest-invalid-maps-to-exit-3' 'every freeze-manifest defect must map to exit 3 / BLOCKED_INPUT_NOT_FROZEN'
Assert-True ($manifestInvalidRes.exitCode -ne 5 -and $manifestInvalidRes.exitCode -ne 6) 'reversal-manifest-invalid-not-5-or-6' 'freeze-manifest defects must never map to the blocked-checks or unknown-exception class'

# ---------------------------------------------------------------------------
# Failure classification & exit/disposition mapping
# ---------------------------------------------------------------------------
Write-Output '--- failure classification & exit/disposition mapping ---'
$precheckRes = Get-CollectorFailureClassification -Message 'OUTPUT_PRECHECK_FAILED: target already exists'
Assert-True ($precheckRes.exitCode -eq 2 -and $precheckRes.disposition -ceq 'BLOCKED_OUTPUT_PRECHECK') 'precheck-maps-to-exit-2' 'output precheck failure must map to exit 2 / BLOCKED_OUTPUT_PRECHECK'
$notFrozenRes = Get-CollectorFailureClassification -Message 'INPUT_NOT_FROZEN: Codex must freeze every sentinel before live'
Assert-True ($notFrozenRes.exitCode -eq 3 -and $notFrozenRes.disposition -ceq 'BLOCKED_INPUT_NOT_FROZEN') 'not-frozen-maps-to-exit-3' 'unfrozen input must map to exit 3 / BLOCKED_INPUT_NOT_FROZEN'
$driftRes = Get-CollectorFailureClassification -Message 'SOURCE_PIN_DRIFT: protected file changed'
Assert-True ($driftRes.exitCode -eq 4 -and $driftRes.disposition -ceq 'BLOCKED_SOURCE_PIN_DRIFT') 'drift-maps-to-exit-4' 'source pin drift must map to exit 4 / BLOCKED_SOURCE_PIN_DRIFT'
$historyRes = Get-CollectorFailureClassification -Message 'HISTORY_SCOPE_VIOLATION: a fixed path references a historical evidence family'
Assert-True ($historyRes.exitCode -eq 5 -and $historyRes.disposition -ceq 'BLOCKED_BY_FAILED_CHECKS') 'history-violation-maps-to-exit-5' 'history scope violation must map to exit 5 / BLOCKED_BY_FAILED_CHECKS'
$chainRes = Get-CollectorFailureClassification -Message 'FIXED_PATH_CHAIN_CHECK_FAILED: reparse point on output dir'
Assert-True ($chainRes.exitCode -eq 5 -and $chainRes.disposition -ceq 'BLOCKED_BY_FAILED_CHECKS') 'fixed-chain-maps-to-exit-5' 'fixed path-chain failure must map to exit 5 / BLOCKED_BY_FAILED_CHECKS'
$chainFallbackRes = Get-CollectorFailureClassification -Message 'System.Exception: generic unclassified failure' -BlockedReasons @('CHECK_FAIL:path-chain-fixed-paths')
Assert-True ($chainFallbackRes.exitCode -eq 5 -and $chainFallbackRes.disposition -ceq 'BLOCKED_BY_FAILED_CHECKS') 'chain-fallback-blocked-reason-maps-to-exit-5' 'CHECK_FAIL:path-chain-fixed-paths fallback must map to exit 5'
$unknownRes = Get-CollectorFailureClassification -Message 'System.Exception: generic unclassified failure'
Assert-True ($unknownRes.exitCode -eq 6 -and $unknownRes.disposition -ceq 'BLOCKED_EXCEPTION_FAIL_CLOSED') 'unknown-maps-to-exit-6' 'ordinary unknown exception must map to exit 6 / BLOCKED_EXCEPTION_FAIL_CLOSED'

# Reversal discrimination negatives: each class must never map to a different exit.
Assert-True ($notFrozenRes.exitCode -ne 2 -and $notFrozenRes.exitCode -ne 5 -and $notFrozenRes.exitCode -ne 6) 'reversal-not-frozen-only-exit-3' 'INPUT_NOT_FROZEN must not share an exit with precheck/fixed-chain/unknown'
Assert-True ($unknownRes.exitCode -ne 5 -and $unknownRes.disposition -ne 'BLOCKED_BY_FAILED_CHECKS') 'reversal-unknown-not-exit-5' 'unknown exception must never map to exit 5'
Assert-True ($historyRes.disposition -ne 'BLOCKED_EXCEPTION_FAIL_CLOSED') 'reversal-history-not-exception-class' 'history violation must not map to the unknown-exception class'
Assert-True ($precheckRes.exitCode -ne 3 -and $precheckRes.exitCode -ne 4) 'reversal-precheck-not-3-or-4' 'output precheck must never map to exit 3 or 4'
Assert-True ($driftRes.exitCode -ne 5 -and $driftRes.exitCode -ne 6) 'reversal-drift-not-5-or-6' 'source pin drift must never map to exit 5 or 6'
$unrelatedFallbackRes = Get-CollectorFailureClassification -Message 'System.Exception: generic unclassified failure' -BlockedReasons @('CHECK_FAIL:unrelated-check-id')
Assert-True ($unrelatedFallbackRes.exitCode -eq 6) 'unrelated-blocked-reason-stays-exit-6' 'an unrelated CHECK_FAIL reason must not trigger the fixed-chain fallback'

# ---------------------------------------------------------------------------
# Line factories: meta/closed field shape (with a selftest-owned Constants)
# ---------------------------------------------------------------------------
Write-Output '--- meta/closed line factory shapes ---'
$constants = [ordered]@{
    schema = 'P02-NEW-TIME-X6-executor-1'
    task = 'P02-NEW-TIME-X6'
    evidenceClass = 'NEW_TIME_EVIDENCE'
    substitutionLabel = 'CANNOT_SUBSTITUTE_H1_P2_1_TIME_EVIDENCE'
    historyNote = 'test history note'
    baseCommit = 'bc502e7aae07074fff7228d585674e87d53efcfd'
    expectedBranch = 'agent/zcode/P02-NEW-TIME-X6'
    outputDir = 'G:/tmp/agent-output'
    worktree = 'G:/tmp/wt'
    tools = [ordered]@{ pwshExe = 'pwsh'; gitExe = 'git'; whoamiExe = 'whoami'; expectedPsVersion = '7.6.6'; expectedPsEdition = 'Core'; expectedLanguageMode = 'FullLanguage'; expectedPsHome = 'ph'; expectedGitVersion = 'git version 2.52.0.windows.1' }
}
$notRun = [ordered]@{ x6PostRunReview = 'NOT_RUN'; buildCargo = 'NOT_RUN'; productAc1_Ac7 = 'BLOCKED / NOT_RUN'; windowsSandbox = 'NOT_RUN (forbidden)' }
$meta = New-MetaLineObject -RunId 'selftest-run' -StartedUtc '2026-10-14T00:00:00.0000000Z' -Constants $constants `
    -Manifest $validManifest -ManifestPath 'G:/outside/freeze-selftest.json' -ManifestSha256 $goodSha `
    -NotRunTable $notRun -ForbiddenHistorySegments $frozenSegments
Assert-True ($meta.kind -ceq 'meta' -and $meta.runId -ceq 'selftest-run' -and $meta.schema -ceq 'P02-NEW-TIME-X6-executor-1') 'meta-shape-core-fields' 'meta line must carry kind/runId/schema'
Assert-True ($meta.frozenInputs.baseCommit -ceq 'bc502e7aae07074fff7228d585674e87d53efcfd' -and $meta.frozenInputs.deliveryHead -ceq $manifestHead) 'meta-shape-frozen-inputs' 'meta line must record the manifest-frozen inputs verbatim'
Assert-True ($meta.freezeManifest.path -ceq 'G:/outside/freeze-selftest.json' -and $meta.freezeManifest.sha256 -ceq $goodSha -and $meta.freezeManifest.runId -ceq 'selftest-run') 'meta-shape-freeze-manifest-triple' 'meta line must name exactly which external freeze input produced the run (path + argv-bound sha + runId)'
Assert-True ($meta.notRun.x6PostRunReview -ceq 'NOT_RUN' -and $meta.notRun.productAc1_Ac7 -like 'BLOCKED*') 'meta-shape-notrun-table' 'meta line must carry the NOT_RUN table (never PASS)'
Assert-True (@($meta.forbiddenHistorySegments).Count -eq 3) 'meta-shape-history-segments' 'meta line must carry the frozen history segments'
Assert-True ($meta.frozenTaskDeliverablePins[0].name -ceq 'collector-source' -and $meta.frozenTaskDeliverablePins[0].sha256 -ceq $collectorSelfSha) 'meta-shape-manifest-deliverable-pins' 'meta line must carry the manifest pins including the collector self-pin SHA'
$metaJson = ConvertTo-Json -InputObject $meta -Depth 96 -Compress
$reparsed = ConvertFrom-Json $metaJson
Assert-True ($reparsed.task -ceq 'P02-NEW-TIME-X6' -and $null -ne $reparsed.frozenContractPins[0].sha256) 'meta-json-roundtrip' 'meta line must survive JSON round-trip with pins intact'

$nulObsSim = New-ObservationRecord -Id 'git-status-verbatim' -Kind 'helper-process'
$nulObsSim.state = 'OK'
$nulObsSim.output = [ordered]@{ stdout = ConvertTo-RawBytesRecord -Bytes $nulBytes }
$nulObsSim.seq = 0
$checkSim = New-CheckRecord -Id 'status-root' -Category 'status' -Expected 'e' `
    -ObservedPointer '/observations/0/output/stdout/base64' -ObservedSummary 's' -Result 'PASS'
$closed = New-ClosedLineObject -RunId 'selftest-run' -Constants $constants -State 'COMPLETED' -Disposition 'COLLECTED_NEW_TIME_EVIDENCE' -ExitCode 0 `
    -NotRunTable $notRun -Observations @($nulObsSim) -Checks @($checkSim) -BlockedReasons @()
Assert-True ($closed.kind -ceq 'closed' -and $closed.state -ceq 'COMPLETED' -and $closed.exitCode -eq 0) 'closed-shape-core-fields' 'closed line must carry kind/state/exitCode'
Assert-True ($closed.counts.observations -eq 1 -and $closed.counts.checks -eq 1 -and $closed.counts.pass -eq 1 -and $closed.counts.fail -eq 0) 'closed-shape-counts' 'closed counts must match the embedded observations/checks'
$rrClosed = Resolve-JsonPointer -Graph $closed -Pointer $closed.checks[0].observedPointer
Assert-True ($rrClosed.found -and $rrClosed.value -ceq $nulRecord.base64) 'closed-line-check-pointer-resolves-to-nul-raw' 'NUL-faithful raw base64 must be reachable via the check pointer inside the closed line'
$closedBlocked = New-ClosedLineObject -RunId 'selftest-run' -Constants $constants -State 'FAILED_STOPPED' -Disposition 'BLOCKED_BY_FAILED_CHECKS' -ExitCode 5 `
    -NotRunTable $notRun -Observations @($nulObsSim) -Checks @($checkSim) -BlockedReasons @('CHECK_FAIL:status-root')
Assert-True ($closedBlocked.counts.pass -eq 1 -and @($closedBlocked.blockedReasons).Count -eq 1 -and $closedBlocked.exitCode -eq 5) 'closed-shape-blocked-variant' 'blocked closed lines must keep blockedReasons and non-zero exit'

# ---------------------------------------------------------------------------
# Git argv builders (pure; exact frozen forms)
# ---------------------------------------------------------------------------
Write-Output '--- git argv builders ---'
$prefix = New-GitPrefixArgv
Assert-True (@($prefix).Count -eq 5 -and $prefix[0] -ceq '--no-pager' -and $prefix[2] -ceq 'core.fsmonitor=false' -and $prefix[4] -ceq 'core.hooksPath=NUL') 'git-prefix-exact' 'fixed git prefix must match the frozen form'
$statusArgv = New-StatusArgv
Assert-True ((@($statusArgv) -contains '--no-optional-locks') -and (@($statusArgv) -contains 'status') -and (@($statusArgv) -contains '--porcelain=v2') -and (@($statusArgv) -contains '-z')) 'status-argv-frozen-form' 'status argv must match the frozen byte-exact form'
Assert-True (-not (@($statusArgv) -contains 'add') -and -not (@($statusArgv) -contains 'commit')) 'status-argv-readonly-verbs-only' 'status argv must contain no mutating git verb'
$ignoreArgv = New-CheckIgnoreArgv -Path 'G:/tmp/x.json'
Assert-True ((@($ignoreArgv) -contains 'check-ignore') -and (@($ignoreArgv)[-1] -ceq 'G:/tmp/x.json')) 'check-ignore-argv-shape' 'check-ignore argv must end with the target path after --'

# ---------------------------------------------------------------------------
# git-branch-matches-freeze branch comparison (AC3-BRANCH-REF-MISMATCH fix):
# symbolic-ref returns the FULL ref while the freeze manifest pins only the
# SHORT branch name; matching is the refs/heads/-prefixed compare and every
# other outcome (wrong branch, bare short name, other ref namespace, detached
# HEAD, case drift) must fail closed.
# ---------------------------------------------------------------------------
Write-Output '--- branch ref matching (git-branch-matches-freeze) ---'
Assert-True (Test-BranchRefMatchesManifest -BranchRef 'refs/heads/agent/zcode/P02-NEW-TIME-X6' -ManifestBranch 'agent/zcode/P02-NEW-TIME-X6') `
    'branch-ref-full-ref-matches-manifest-short-name' 'the runtime full refs/heads/<name> must match the manifest short branch name'
Assert-True (-not (Test-BranchRefMatchesManifest -BranchRef 'refs/heads/agent/zcode/P02-NEW-TIME-X6-AC3-BRANCH-RESOLUTION' -ManifestBranch 'agent/zcode/P02-NEW-TIME-X6')) `
    'branch-ref-wrong-branch-fails-closed' 'a different branch, even a hyphen-suffixed sibling, must fail closed'
Assert-True (-not (Test-BranchRefMatchesManifest -BranchRef 'refs/heads/main' -ManifestBranch 'agent/zcode/P02-NEW-TIME-X6')) `
    'branch-ref-unrelated-branch-fails-closed' 'an unrelated branch must fail closed'
Assert-True (-not (Test-BranchRefMatchesManifest -BranchRef 'refs/tags/agent/zcode/P02-NEW-TIME-X6' -ManifestBranch 'agent/zcode/P02-NEW-TIME-X6')) `
    'branch-ref-non-heads-namespace-fails-closed' 'a non-refs/heads/ ref namespace must fail closed'
Assert-True (-not (Test-BranchRefMatchesManifest -BranchRef 'agent/zcode/P02-NEW-TIME-X6' -ManifestBranch 'agent/zcode/P02-NEW-TIME-X6')) `
    'branch-ref-bare-short-name-not-a-runtime-ref' 'a bare short name is not a symbolic-ref output and must not be accepted'
Assert-True (-not (Test-BranchRefMatchesManifest -BranchRef '' -ManifestBranch 'agent/zcode/P02-NEW-TIME-X6')) `
    'branch-ref-empty-detached-head-fails-closed' 'detached HEAD (empty symbolic-ref stdout) must fail closed'
Assert-True (-not (Test-BranchRefMatchesManifest -BranchRef 'refs/heads/AGENT/ZCODE/P02-NEW-TIME-X6' -ManifestBranch 'agent/zcode/P02-NEW-TIME-X6')) `
    'branch-ref-compare-stays-case-sensitive' 'branch matching stays case-sensitive like the git-head pin (no case-insensitive widening)'

# ---------------------------------------------------------------------------
# git-toplevel-matches-worktree path comparison (AC3-GIT-TOPLEVEL-PATH-
# SEPARATOR fix): Git for Windows reports rev-parse --show-toplevel with
# forward slashes while the frozen manifest worktree is pinned with
# backslashes, so the SAME absolute directory in either separator style must
# match (case-insensitive on Windows), while a different volume, directory or
# leaf must fail closed. Pure string assertions only — no git child process.
# ---------------------------------------------------------------------------
Write-Output '--- git toplevel matching (git-toplevel-matches-worktree) ---'
$frozenWorktree = 'G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-X6'
Assert-True (Test-GitToplevelMatchesWorktree -Toplevel 'G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6' -Worktree $frozenWorktree) `
    'toplevel-git-slash-form-matches-frozen-backslash-form' 'the same absolute path reported by Git for Windows with forward slashes must match the backslash frozen manifest path (the fixed defect scenario)'
Assert-True (Test-GitToplevelMatchesWorktree -Toplevel 'G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6' -Worktree 'G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6') `
    'toplevel-identical-slash-forms-match' 'identical forward-slash forms on both sides must match'
Assert-True (Test-GitToplevelMatchesWorktree -Toplevel 'G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-X6' -Worktree $frozenWorktree) `
    'toplevel-identical-backslash-forms-match' 'identical backslash forms on both sides must match'
Assert-True (Test-GitToplevelMatchesWorktree -Toplevel 'g:/codex/new manga.workspace/worktrees/p02-new-time-x6' -Worktree $frozenWorktree) `
    'toplevel-case-insensitive-across-separator-styles' 'Windows path comparison stays case-insensitive across both separator styles'
Assert-True (Test-GitToplevelMatchesWorktree -Toplevel 'G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-X6\' -Worktree $frozenWorktree) `
    'toplevel-trailing-separator-tolerated-on-either-side' 'a trailing separator difference denotes the same directory and must not fail the pin'
Assert-True (-not (Test-GitToplevelMatchesWorktree -Toplevel 'H:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6' -Worktree $frozenWorktree)) `
    'toplevel-different-drive-fails-closed' 'a different drive letter must fail closed'
Assert-True (-not (Test-GitToplevelMatchesWorktree -Toplevel 'G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6' -Worktree $frozenWorktree)) `
    'toplevel-different-directory-same-leaf-fails-closed' 'a different parent directory with the same leaf name must fail closed'
Assert-True (-not (Test-GitToplevelMatchesWorktree -Toplevel 'G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-OTHER' -Worktree $frozenWorktree)) `
    'toplevel-different-leaf-fails-closed' 'a different (hyphen-suffixed sibling) leaf directory must fail closed'
Assert-True (-not (Test-GitToplevelMatchesWorktree -Toplevel 'G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6/sub/dir' -Worktree $frozenWorktree)) `
    'toplevel-subdirectory-of-worktree-fails-closed' 'a subdirectory of the worktree must fail closed (prefix containment is not equality)'
Assert-True (-not (Test-GitToplevelMatchesWorktree -Toplevel 'G:/CODEX/New Manga.workspace/worktrees' -Worktree $frozenWorktree)) `
    'toplevel-parent-directory-fails-closed' 'a parent directory of the worktree must fail closed'
Assert-True (-not (Test-GitToplevelMatchesWorktree -Toplevel '' -Worktree $frozenWorktree) -and -not (Test-GitToplevelMatchesWorktree -Toplevel 'G:/CODEX/x' -Worktree '')) `
    'toplevel-empty-input-fails-closed' 'empty toplevel stdout (failed git child) or empty manifest worktree must fail closed'

# ---------------------------------------------------------------------------
# CreateNew collision / exclusive sharing / partial preservation (temp fixtures only)
# ---------------------------------------------------------------------------
Write-Output '--- create-new collision and partial preservation (temp fixtures) ---'
$fixtureDir = Join-Path $TempRoot "$Stamp-pure-selftest"
New-Item -ItemType Directory -Force -Path $fixtureDir | Out-Null

$collisionPath = Join-Path $fixtureDir 'collision.bin'
$collisionBytes = [byte[]](1, 2, 3, 4, 5)
[IO.File]::WriteAllBytes($collisionPath, $collisionBytes)
Assert-Throws -Body { $null = Open-ExclusiveCreateNew -Path $collisionPath } `
    -Name 'createnew-conflict-throws' -Detail 'existing target must throw (no overwrite, no retry under the same RunId)'
$collisionAfter = [IO.File]::ReadAllBytes($collisionPath)
$collisionIntact = ($collisionAfter.Length -eq $collisionBytes.Length)
if ($collisionIntact) { for ($i = 0; $i -lt $collisionBytes.Length; $i++) { if ($collisionAfter[$i] -ne $collisionBytes[$i]) { $collisionIntact = $false; break } } }
Assert-True $collisionIntact 'createnew-conflict-preserves-existing-bytes' 'pre-existing content must remain byte-identical after the refused CreateNew'

$exclusivePath = Join-Path $fixtureDir 'exclusive.bin'
$exclusiveStream = Open-ExclusiveCreateNew -Path $exclusivePath
$exclusiveStream.WriteByte(0x41)
$exclusiveStream.Flush()
Assert-Throws -Body { $null = [IO.FileStream]::new($exclusivePath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::None) } `
    -Name 'fileshare-none-blocks-second-opener' -Detail 'an exclusive-open stream must block other openers'
$exclusiveStream.Dispose()
$exclusiveReadback = [IO.File]::ReadAllBytes($exclusivePath)
Assert-True ($exclusiveReadback.Length -eq 1 -and $exclusiveReadback[0] -eq 0x41) 'exclusive-write-survives-dispose' 'written byte must be durable after dispose'

$missingDirPath = Join-Path $fixtureDir ("no-such-dir-" + [Guid]::NewGuid().ToString('N') + '/x.bin')
Assert-Throws -Body { $null = Open-ExclusiveCreateNew -Path $missingDirPath } `
    -Name 'createnew-missing-parent-fails-closed' -Detail 'missing parent directory must throw; directories are never created'

# --- partial-output preservation behavioral simulation: line-by-line flush
#     keeps already-written evidence readable when a failure happens mid-run,
#     and the failed partial file is never deleted or truncated. ---
$partialPath = Join-Path $fixtureDir 'partial-run.json'
$partialStream = [IO.FileStream]::new($partialPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
$partialWriter = [IO.StreamWriter]::new($partialStream, [System.Text.UTF8Encoding]::new($false))
$partialWriter.NewLine = "`n"
try {
    $partialWriter.WriteLine((ConvertTo-Json -InputObject ([ordered]@{ kind = 'meta'; task = 'P02-NEW-TIME-X6' }) -Depth 8 -Compress))
    $partialWriter.Flush()
    $partialWriter.WriteLine((ConvertTo-Json -InputObject ([ordered]@{ kind = 'observation'; observation = [ordered]@{ id = 'first' } }) -Depth 8 -Compress))
    $partialWriter.Flush()
    # Simulate a mid-run failure AFTER two durable lines (no closed line yet).
    throw 'OUTPUT_PRECHECK_FAILED: simulated mid-run failure'
} catch {
    $midRunFailure = [string]$_.Exception.Message
    # The failure classification must still work and must NOT touch the file.
    $midClass = Get-CollectorFailureClassification -Message $midRunFailure
    Assert-True ($midClass.exitCode -eq 2) 'partial-preservation-classification-still-works' 'failure classification during a mid-run failure must still map correctly'
}
try { $partialWriter.Dispose() } catch { }
try { $partialStream.Dispose() } catch { }
$partialLines = @([IO.File]::ReadAllLines($partialPath)) | Where-Object { $_ -ne '' }
Assert-True (@($partialLines).Count -eq 2) 'partial-preservation-lines-survive' ("lines=$(@($partialLines).Count)")
$partialMeta = ConvertFrom-Json $partialLines[0]
$partialObs = ConvertFrom-Json $partialLines[1]
Assert-True ($partialMeta.kind -ceq 'meta' -and $partialObs.kind -ceq 'observation') 'partial-preservation-lines-parse' 'both durable lines must remain parseable JSON after the failure'
Assert-True ([IO.File]::Exists($partialPath)) 'partial-preservation-file-not-deleted' 'the partial output file must be preserved verbatim (no overwrite, no delete, no retry under the same RunId)'

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
$finishedUtc = [DateTime]::UtcNow.ToString('o')
$summary = [ordered]@{
    task = 'P02-NEW-TIME-X6'
    kind = 'pure-selftest-summary'
    revision = 'x6-source-delivery-r1 (rebound from reviewed baseline i2-r3 lineage; adds forbidden-write-prefix guard)'
    collectorPath = $CollectorPath
    collectorSha256 = (Get-FileHash -LiteralPath $CollectorPath -Algorithm SHA256).Hash
    selfPath = $SelfPath
    fixtureDir = $fixtureDir
    shell = $pwshExePath
    psVersion = $PSVersionTable.PSVersion.ToString()
    edition = $PSVersionTable.PSEdition
    languageMode = $ExecutionContext.SessionState.LanguageMode.ToString()
    startedUtc = $script:StartedUtc
    finishedUtc = $finishedUtc
    argv = @($PSCommandPath, $CollectorPath, $SelfPath, $TempRoot, $Stamp)
    assertsPassed = $script:AssertsPassed
    assertsFailed = $script:AssertsFailed
    assertsSkipped = @($script:Skips)
    liveQueriesExecuted = $false
    liveCollectorExecuted = $false
    gitChildExecuted = $false
    historicalInputAccessed = $false
}
Write-Output ''
Write-Output '=== SUMMARY-JSON ==='
Write-Output (ConvertTo-Json -InputObject $summary -Depth 16 -Compress)
if ($script:AssertsFailed -gt 0) { exit 1 } else { exit 0 }
