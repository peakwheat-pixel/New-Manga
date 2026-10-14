#Requires -Version 7.4
<#
.SYNOPSIS
    P02-NEW-TIME-X6 — new-time-point X6 dynamic-closure executor.
    PowerShell 7 only, no new dependencies.

.DESCRIPTION
    PROPOSAL-ONLY delivery. Live execution is NOT authorized inside the Owner
    (ZCode) environment. Per Task X6-AC4/X6-AC5 the Codex freeze inputs are
    supplied EXTERNALLY (I2 design): Codex creates a freeze manifest OUTSIDE
    the Git worktree/repository and binds its exact path and expected SHA-256
    in the invocation argv:

        pwsh -NoProfile -File verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1 `
            -RunId <RunId> `
            -FreezeManifestPath <absolute path outside the repository> `
            -FreezeManifestSha256 <64 hex of the manifest bytes>

    The manifest (schema P02-NEW-TIME-X6-freeze-manifest-1) carries the
    delivery HEAD, frozen CWD, matching RunId, branch/base, the single
    CreateNew output target, every contract and Task-deliverable pin INCLUDING
    the collector source's own full SHA-256, and the remaining previously
    frozen constants (worktree/outputDir/identity/tool paths/runtime
    expectations/mutable observation paths). The collector source therefore
    contains NO expected hash of itself and NO commit hash of the commit it
    runs under: both circular references of the former embedded-sentinel
    design are removed, and the argv-supplied expected hash is the single
    independent integrity binding (no concurrent/tampered-input ambiguity).

    Validation order (everything fail-closed BEFORE the CreateNew output or
    any child process): parameter syntax -> manifest path history isolation
    and outside-repository check -> manifest bytes vs the argv-supplied SHA ->
    strict JSON schema/shape validation -> binding validation against the
    source-side structural baselines (RunId/base/branch/worktree/outputDir/
    tools/identity) -> manifest path-manifest history isolation -> output
    target absent/unignored checks -> CWD check. Failures/partial output
    after the one-shot run starts keep the streamed-line preservation.

    Contract source: doc/tasks/P02-NEW-TIME-X6.md (frozen scope and AC).
    Purpose: execute ONLY the new-time-point X6 dynamic closure of the current
    integrated version. It does not close, rewrite, backfill or replace any
    historical H1 conclusion, P2-1 OPEN finding or the 13 historical
    missing-source records; those stay exactly as they are. A PASS here means
    only that this Task's X6 checks passed — never a post-run Review,
    Build/Cargo or product AC1-AC7 pass.

    Output: one exclusive CreateNew NDJSON stream (FileShare.None), the only new
        file G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6/run-<RunId>.json
    Line kinds: 'meta', 'observation', 'closed'. Every observation is flushed to
    the stream immediately so partial failure evidence survives verbatim and is
    never retried under the same RunId (CreateNew refuses reuse). The final
    'closed' line is a self-contained JSON object (observations + checks + raw
    pointers + disposition); every check carries
    observedPointer = '/observations/<seq>/...' (JSON Pointer, RFC 6901).

    Read-only observation classes collected at this time point (Task frozen scope):
      version (pwsh/git), identity/path/permission facts, protected-file hashes,
      Git/source pins, and static contract-file presence of this worktree.
    Unknown facts, drift, pre-existing output targets or incomplete observations
    fail closed. Mutable STATUS/Plan/checkpoint files are recorded as plain
    observations and are NEVER used as immutable hash pins (Task evidence rule).

    Safety rules implemented:
      - No overwrite/retry/delete; CreateNew only; failed partial output is preserved.
      - History isolation: every fixed input/output path is rejected (fail-closed,
        before any filesystem API) when one of its segments equals a frozen
        historical task-family name or extends that name with the documented
        hyphen delimiter; no historical input or conclusion is read, written or
        re-awarded. Additionally the single CreateNew output target may never
        fall under the root repository's historical verification/P02/
        directory (Task forbidden write scope).
      - The frozen historical executor of the pre-rebaseline round is never
        referenced, read, executed or dot-sourced.
      - No File.Replace, no dynamic process enumeration (no Toolhelp/Process32*,
        no process-listing cmdlet), no profile/registry/ACL write API, no
        registry access at all.
      - All helper argv/CWD/start-finish UTC/stdout/stderr (raw bytes + base64 +
        SHA-256 + strict-UTF-8 text when lossless)/OS exit are recorded per call.
      - In-process getters record method/input/output/exception (never summaries only).
      - Unknown exceptions fail closed; disposition and OS exit are reported
        separately; any blocking disposition exits non-zero.
      - Git children: ProcessStartInfo.ArgumentList, UseShellExecute=false, fixed
        prefix '--no-pager -c core.fsmonitor=false -c core.hooksPath=NUL';
        inherited GIT context/GIT_CONFIG* fail-stop before launch; GIT_TRACE*
        removed (names recorded, values withheld); GIT_OPTIONAL_LOCKS=0,
        GIT_TERMINAL_PROMPT=0.
      - Post-run Review, Build/Cargo, product AC1-AC7 and Windows Sandbox stay
        NOT_RUN; they are released (or not) by later Gates, never by this
        executor. This run IS the single X6 one-shot and its PASS means only X6.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$')]
    [string]$RunId,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z]:\\.+|^[A-Za-z]:/.+|^//.+')]
    [string]$FreezeManifestPath,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Fa-f0-9]{64}$')]
    [string]$FreezeManifestSha256
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ===========================================================================
# Structural baselines (fixed at Owner delivery; see Task frozen scope).
# I2: the AC3 freeze inputs (delivery HEAD, frozen CWD, matching RunId, every
# output/CreateNew target and EVERY hash pin including the collector's own
# full SHA-256) are NOT embedded here any more. They arrive exclusively via an
# external Codex-frozen freeze manifest bound in the argv
# (-FreezeManifestPath / -FreezeManifestSha256); the manifest must live
# OUTSIDE the Git worktree/repository. The constants below are non-circular
# structural baselines used to cross-validate the manifest (catching a
# manifest aimed at the wrong checkout/output root) and to drive the
# collection logic; the source contains no hash of itself and no hash of the
# commit it runs under.
# ===========================================================================
$script:Schema = 'P02-NEW-TIME-X6-executor-1'
$script:ManifestSchema = 'P02-NEW-TIME-X6-freeze-manifest-1'
$script:TaskId = 'P02-NEW-TIME-X6'
$script:OutputDir = 'G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-X6'
$script:Worktree = 'G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6'
$script:BaseCommit = 'bc502e7aae07074fff7228d585674e87d53efcfd'
$script:ExpectedBranch = 'agent/zcode/P02-NEW-TIME-X6'

$script:PwshExe = 'C:/Program Files/PowerShell/7/pwsh.exe'
$script:GitExe = 'C:/Program Files/Git/cmd/git.exe'
$script:WhoamiExe = 'C:/Windows/System32/whoami.exe'
$script:ExpectedPsVersion = '7.6.6'
$script:ExpectedPsEdition = 'Core'
$script:ExpectedLanguageMode = 'FullLanguage'
$script:ExpectedPsHome = 'C:\Program Files\PowerShell\7'
$script:ExpectedGitVersion = 'git version 2.52.0.windows.1'

# Owner-host identity baseline (cross-validated against the freeze manifest).
$script:ExpectedIdentityName = 'home-my\49745'
$script:ExpectedIdentitySid = 'S-1-5-21-2196946971-914346751-4210154634-1001'

# History isolation (Task forbidden scope): no fixed path may reference the
# historical evidence families; their inputs/conclusions stay untouched.
$script:ForbiddenHistorySegments = @(
    'P02PRE-R1H-H1',
    'P02PRE-R1H-H2',
    'P02PRE-R1H-P2-1'
)

# Task X6 forbidden write scope (defense in depth): the root repository's
# historical verification/P02/ directory is never a legal output/write root
# for this executor even if a freeze manifest were mis-aimed at it. Compared
# case-insensitively after '/'->'\' normalization, both with and without a
# trailing separator.
$script:ForbiddenWritePrefixes = @(
    'G:\CODEX\New Manga\verification\P02\'
)

$script:EvidenceClass = 'NEW_TIME_EVIDENCE'
$script:SubstitutionLabel = 'CANNOT_SUBSTITUTE_H1_P2_1_TIME_EVIDENCE'
$script:HistoryNote = ('Historical H1 conclusions, the P2-1 OPEN finding and the 13 historical ' +
                       'missing-source records remain unchanged and OPEN; this collection does not ' +
                       'close, rewrite, backfill or replace any of them, and a PASS here means only ' +
                       'that this Task''s new-time-point AC checks passed.')

$script:NotRunTable = [ordered]@{
    liveX6ThisRun = 'THIS_RUN (the single X6 one-shot; RunId never reused; Codex-owned source Review / freeze / pre-run gates are recorded via the argv-bound freeze manifest, never self-awarded by this executor)'
    frozenHistoricalExecutor = 'NOT_RUN (forbidden; the frozen historical executor of the pre-rebaseline integration round is never referenced, read, executed or dot-sourced)'
    dynamicProcessEnumeration = 'NOT_RUN (forbidden: no Toolhelp/Process32* and no process-listing cmdlet)'
    profileRegistryAclWrite = 'NOT_RUN (forbidden: no profile/registry/ACL write API; no registry access at all)'
    fileReplace = 'NOT_USED (forbidden: File.Replace never called)'
    historicalVerificationP02Write = 'FORBIDDEN / NOT_PERFORMED (output target may never fall under the root repository verification/P02/ directory)'
    postRunReview = 'NOT_RUN'
    buildCargo = 'NOT_RUN'
    productAc1_Ac7 = 'BLOCKED / NOT_RUN'
    windowsSandbox = 'NOT_RUN (forbidden)'
    historicalInputRewrite = 'FORBIDDEN / NOT_PERFORMED (history isolation enforced before any file access)'
}

# Fully-parameterized constant bundle for the pure line factories (the pure
# selftest extracts New-MetaLineObject / New-ClosedLineObject from the AST and
# runs them against its own small Constants object; no script-state access).
$script:Constants = [ordered]@{
    schema = $script:Schema
    task = $script:TaskId
    evidenceClass = $script:EvidenceClass
    substitutionLabel = $script:SubstitutionLabel
    historyNote = $script:HistoryNote
    baseCommit = $script:BaseCommit
    expectedBranch = $script:ExpectedBranch
    outputDir = $script:OutputDir
    worktree = $script:Worktree
    tools = [ordered]@{
        pwshExe = $script:PwshExe
        gitExe = $script:GitExe
        whoamiExe = $script:WhoamiExe
        expectedPsVersion = $script:ExpectedPsVersion
        expectedPsEdition = $script:ExpectedPsEdition
        expectedLanguageMode = $script:ExpectedLanguageMode
        expectedPsHome = $script:ExpectedPsHome
        expectedGitVersion = $script:ExpectedGitVersion
    }
}

# Source-side structural baselines passed INTO the pure freeze-manifest
# validators (I2): the validators stay script-state free, so the selftest can
# extract and run them against its own small ExpectedBaselines object.
$script:ExpectedBaselines = [ordered]@{
    manifestSchema = $script:ManifestSchema
    taskId = $script:TaskId
    baseCommit = $script:BaseCommit
    expectedBranch = $script:ExpectedBranch
    worktree = $script:Worktree
    outputDir = $script:OutputDir
    pwshExe = $script:PwshExe
    gitExe = $script:GitExe
    whoamiExe = $script:WhoamiExe
    psVersion = $script:ExpectedPsVersion
    psEdition = $script:ExpectedPsEdition
    languageMode = $script:ExpectedLanguageMode
    gitVersion = $script:ExpectedGitVersion
    identityName = $script:ExpectedIdentityName
    identitySid = $script:ExpectedIdentitySid
}

$script:Observations = [Collections.Generic.List[object]]::new()
$script:Checks = [Collections.Generic.List[object]]::new()
$script:BlockedReasons = [Collections.Generic.List[string]]::new()
$script:ObservationSeq = 0
$script:Writer = $null
$script:Stream = $null
$script:ExitCode = 0
$script:Disposition = 'EXECUTED_X6_DYNAMIC_CLOSURE'

# ===========================================================================
# Pure helper functions (extracted by the pure selftest via AST; no script-state
# access, no child process, no live system query).
# ===========================================================================
function Require {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function Get-Sha256HexFromBytes {
    param([byte[]]$Bytes)
    if ($null -eq $Bytes) { return $null }
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash($Bytes)
        return (([BitConverter]::ToString($hash)) -replace '-', '')
    } finally { $sha.Dispose() }
}

function ConvertTo-SafeUtf8Text {
    # Strict UTF-8 decode; returns $null when the byte stream is not valid UTF-8.
    param([byte[]]$Bytes)
    if ($null -eq $Bytes) { return $null }
    $strictUtf8 = [System.Text.UTF8Encoding]::new($false, $true)
    try { return $strictUtf8.GetString($Bytes) } catch { return $null }
}

function Split-NulRecords {
    # Split a NUL-terminated byte stream (e.g. git status -z) into records.
    # Zero-length records and trailing unterminated bytes are recorded verbatim
    # (never dropped, never synthesized); each record text is strict-UTF-8 or null.
    param([byte[]]$Bytes)
    $records = [Collections.Generic.List[object]]::new()
    if ($null -eq $Bytes) { return @() }
    $start = 0
    for ($i = 0; $i -lt $Bytes.Length; $i++) {
        if ($Bytes[$i] -eq 0) {
            $length = $i - $start
            $text = ''
            if ($length -gt 0) {
                $segment = [byte[]]::new($length)
                [Array]::Copy($Bytes, $start, $segment, 0, $length)
                $text = ConvertTo-SafeUtf8Text -Bytes $segment
            }
            $records.Add([ordered]@{ offset = $start; length = $length; text = $text; unterminated = $false })
            $start = $i + 1
        }
    }
    if ($start -lt $Bytes.Length) {
        $length = $Bytes.Length - $start
        $segment = [byte[]]::new($length)
        [Array]::Copy($Bytes, $start, $segment, 0, $length)
        $records.Add([ordered]@{ offset = $start; length = $length; text = (ConvertTo-SafeUtf8Text -Bytes $segment); unterminated = $true })
    }
    return @($records.ToArray())
}

function ConvertTo-RawBytesRecord {
    # Raw-output fidelity record: bytesCount, nulCount, sha256, ALWAYS-complete
    # base64, and lossless strict-UTF-8 text only when safe. Empty bytes are a
    # real observation (not absence); NUL-containing output keeps base64 canonical.
    param([byte[]]$Bytes)
    $bytesCount = 0
    $nulCount = 0
    if ($null -eq $Bytes) {
        return [ordered]@{
            bytesCount = $null
            nulCount = $null
            sha256 = $null
            base64 = $null
            text = $null
            textOmitted = $false
            textOmitReason = $null
        }
    }
    $bytesCount = $Bytes.Length
    foreach ($b in $Bytes) { if ($b -eq 0) { $nulCount++ } }
    $record = [ordered]@{
        bytesCount = $bytesCount
        nulCount = $nulCount
        sha256 = Get-Sha256HexFromBytes -Bytes $Bytes
        base64 = [Convert]::ToBase64String($Bytes)
        text = $null
        textOmitted = $false
        textOmitReason = $null
    }
    if ($nulCount -gt 0) {
        $record.textOmitted = $true
        $record.textOmitReason = 'output contains NUL bytes; text omitted; NUL-faithful base64 is canonical'
    } else {
        $decoded = ConvertTo-SafeUtf8Text -Bytes $Bytes
        if ($null -eq $decoded) {
            $record.textOmitted = $true
            $record.textOmitReason = 'output is not valid UTF-8; text omitted; base64 is canonical'
        } else {
            $record.text = $decoded
        }
    }
    return $record
}

function Resolve-JsonPointer {
    # RFC 6901-style resolver over ordered-hashtable/array graphs. Used by the
    # pure selftest and by parsers of the self-contained closed line; returns
    # @{ found; value } and never throws.
    param($Graph, [string]$Pointer)
    $result = [ordered]@{ found = $false; value = $null }
    if ($null -eq $Graph) { return $result }
    if ([string]::IsNullOrEmpty($Pointer)) { $result.found = $true; $result.value = $Graph; return $result }
    if (-not $Pointer.StartsWith('/')) { return $result }
    $current = $Graph
    foreach ($rawToken in ($Pointer.Substring(1) -split '/')) {
        $token = $rawToken -replace '~1', '/' -replace '~0', '~'
        if ($null -eq $current) { return $result }
        if ($current -is [System.Collections.IList]) {
            if ($token -notmatch '^(0|[1-9][0-9]*)$') { return $result }
            $index = [int]$token
            if ($index -ge $current.Count) { return $result }
            $current = $current[$index]
        } elseif ($current -is [System.Collections.IDictionary]) {
            if (-not $current.Contains($token)) { return $result }
            $current = $current[$token]
        } else {
            return $result
        }
    }
    $result.found = $true
    $result.value = $current
    return $result
}

function New-PathProbeAbsentValue {
    # COMPLETE field shape for a legal absence: every field summaries access
    # exists so StrictMode-safe readers never crash.
    param([string]$Path)
    return [ordered]@{
        path = $Path
        exists = $false
        absent = $true
        isDirectory = $false
        isFile = $false
        attributes = $null
        reparsePoint = $null
        length = $null
        linkTarget = $null
        linkTargetError = $null
        attributeError = $null
        hresult = $null
        probeOnlyNote = 'existence/metadata probe only; proves nothing beyond the recorded values'
    }
}

function New-PathProbeErrorValue {
    # COMPLETE field shape for a non-absence attribute error: access, argument,
    # path-too-long or I/O error; must NOT report legal absence or PASS.
    param([string]$Path, [System.Exception]$Exception)
    $errStr = if ($null -ne $Exception) { "$($Exception.GetType().FullName): $($Exception.Message)" } else { 'UnknownAttributeError' }
    $hresult = if ($null -ne $Exception) { '0x{0:X8}' -f $Exception.HResult } else { $null }
    return [ordered]@{
        path = $Path
        exists = $false
        absent = $false
        isDirectory = $false
        isFile = $false
        attributes = $null
        reparsePoint = $null
        length = $null
        linkTarget = $null
        linkTargetError = $null
        attributeError = $errStr
        hresult = $hresult
        probeOnlyNote = 'existence/metadata probe failed with non-absence error; not a legal absence'
    }
}

function Get-PathProbeValueFromAttributes {
    # Pure classification shared by collector and selftest. Distinguishes genuine
    # absence (FileNotFound/DirectoryNotFound) from non-absence attribute errors.
    param(
        [string]$Path,
        $Attributes,
        [System.Exception]$Exception
    )
    if ($null -ne $Exception) {
        $actualEx = if ($null -ne $Exception.InnerException) { $Exception.InnerException } else { $Exception }
        if ($actualEx -is [System.IO.FileNotFoundException] -or $actualEx -is [System.IO.DirectoryNotFoundException]) {
            return New-PathProbeAbsentValue -Path $Path
        } else {
            return New-PathProbeErrorValue -Path $Path -Exception $actualEx
        }
    }
    $isDir = (($Attributes -band [System.IO.FileAttributes]::Directory) -ne 0)
    $isReparse = (($Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)
    return [ordered]@{
        path = $Path
        exists = $true
        absent = $false
        isDirectory = $isDir
        isFile = (-not $isDir)
        attributes = $Attributes.ToString()
        reparsePoint = $isReparse
        length = $null
        linkTarget = $null
        linkTargetError = $null
        attributeError = $null
        hresult = $null
        probeOnlyNote = 'existence/metadata probe only; proves nothing beyond the recorded values'
    }
}

function Get-ProbeCheckResult {
    # Pure check-result evaluation shared by collector and selftest.
    # Maps non-absence attribute errors to NOT_VERIFIED (never PASS).
    param($ProbeValue)
    if ($null -ne $ProbeValue.attributeError) {
        return 'NOT_VERIFIED'
    }
    return 'PASS'
}

function Get-CollectorFailureClassification {
    # Pure failure classification shared by collector catch block and selftest.
    #   OUTPUT_PRECHECK_FAILED*            -> exit 2 / BLOCKED_OUTPUT_PRECHECK
    #   INPUT_NOT_FROZEN*                  -> exit 3 / BLOCKED_INPUT_NOT_FROZEN
    #   FREEZE_MANIFEST_INVALID*           -> exit 3 / BLOCKED_INPUT_NOT_FROZEN
    #   SOURCE_PIN_DRIFT*                  -> exit 4 / BLOCKED_SOURCE_PIN_DRIFT
    #   FIXED_PATH_CHAIN / HISTORY_SCOPE / CHECK_FAIL:path-chain-fixed-paths
    #                                      -> exit 5 / BLOCKED_BY_FAILED_CHECKS
    #   anything else                      -> exit 6 / BLOCKED_EXCEPTION_FAIL_CLOSED
    param(
        [string]$Message,
        [object]$BlockedReasons = $null
    )
    if ($Message -like 'OUTPUT_PRECHECK_FAILED*') {
        return [ordered]@{ exitCode = 2; disposition = 'BLOCKED_OUTPUT_PRECHECK' }
    }
    if ($Message -like 'INPUT_NOT_FROZEN*' -or $Message -like 'FREEZE_MANIFEST_INVALID*') {
        return [ordered]@{ exitCode = 3; disposition = 'BLOCKED_INPUT_NOT_FROZEN' }
    }
    if ($Message -like 'SOURCE_PIN_DRIFT*') {
        return [ordered]@{ exitCode = 4; disposition = 'BLOCKED_SOURCE_PIN_DRIFT' }
    }
    $isFixedChainFailure = ($Message -like 'FIXED_PATH_CHAIN_CHECK_FAILED*') -or
                           ($Message -like 'HISTORY_SCOPE_VIOLATION*') -or
                           ($Message -like '*Fixed path-chain validation failed*')
    if (-not $isFixedChainFailure -and $null -ne $BlockedReasons) {
        foreach ($r in $BlockedReasons) {
            if ($r -eq 'CHECK_FAIL:path-chain-fixed-paths') {
                $isFixedChainFailure = $true
                break
            }
        }
    }
    if ($isFixedChainFailure) {
        return [ordered]@{ exitCode = 5; disposition = 'BLOCKED_BY_FAILED_CHECKS' }
    }
    return [ordered]@{ exitCode = 6; disposition = 'BLOCKED_EXCEPTION_FAIL_CLOSED' }
}

function Test-PathContainsHistorySegment {
    # History isolation (pure string check; no filesystem access): true when any
    # path segment (case-insensitive; both separators accepted) either equals a
    # frozen historical task-family name exactly, or starts with that family
    # name and the NEXT character is the documented hyphen delimiter (real
    # directory names extend a family with '-SUFFIX', e.g. an H2-family
    # collector directory). A longer segment whose character after the family
    # name is NOT the delimiter (e.g. an 'X' continuation) must NOT match, and
    # arbitrary substring containment is deliberately NOT used (I1 per DSH
    # R-01 / Codex adjudication).
    param(
        [string]$Path,
        [string[]]$ForbiddenSegments
    )
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    if ($null -eq $ForbiddenSegments -or @($ForbiddenSegments).Count -eq 0) { return $false }
    $normalized = ($Path -replace '/', '\')
    $segments = $normalized -split '\\'
    foreach ($seg in $segments) {
        foreach ($forbidden in $ForbiddenSegments) {
            if ($seg -ieq $forbidden) { return $true }
            if ($seg.Length -gt $forbidden.Length -and
                $seg.StartsWith($forbidden, [StringComparison]::OrdinalIgnoreCase) -and
                $seg[$forbidden.Length] -ceq '-') { return $true }
        }
    }
    return $false
}

function Assert-TaskPathIsolation {
    # Pure-string gate: evaluate a full path manifest against the frozen
    # historical segments BEFORE any filesystem/process API. Returns a complete
    # manifest; the caller must fail closed when anyUnderHistory is true.
    param([string[]]$Paths, [string[]]$ForbiddenSegments)
    $results = [Collections.Generic.List[object]]::new()
    $hits = [Collections.Generic.List[string]]::new()
    $pathList = @($Paths)
    foreach ($p in $pathList) {
        $under = Test-PathContainsHistorySegment -Path $p -ForbiddenSegments $ForbiddenSegments
        $results.Add([ordered]@{ path = $p; underHistory = $under })
        if ($under) { $hits.Add($p) }
    }
    return [ordered]@{
        segmentCount = @($ForbiddenSegments).Count
        pathCount = $results.Count
        pathManifest = @($results.ToArray())
        underHistoryPaths = @($hits.ToArray())
        anyUnderHistory = ($hits.Count -gt 0)
    }
}

function Test-FreezeManifestBytes {
    # Pure integrity binding for the external freeze manifest: the manifest
    # bytes must hash to the argv-supplied expected SHA-256. The expected hash
    # is NEVER stored inside the collector (I2: removes the self-referential
    # hash cycle); the argv is the single independent binding.
    param([byte[]]$Bytes, [string]$ExpectedSha256)
    $actual = Get-Sha256HexFromBytes -Bytes $Bytes
    return [ordered]@{
        match = ($null -ne $actual -and $actual -ieq $ExpectedSha256)
        actualSha256 = $actual
        expectedSha256 = $ExpectedSha256
    }
}

function Get-ManifestField {
    # Pure StrictMode-safe field access over a deserialized manifest object:
    # returns @{ present; value } without ever throwing on missing fields.
    param($Object, [string]$Name)
    $result = [ordered]@{ present = $false; value = $null }
    if ($null -eq $Object) { return $result }
    $prop = $Object.PSObject.Properties[$Name]
    if ($null -ne $prop) {
        $result.present = $true
        $result.value = $prop.Value
    }
    return $result
}

function Test-PathOutsideRepository {
    # Pure string check: true when the normalized path is NOT inside (or equal
    # to) the worktree/repository. The freeze manifest must live outside the
    # repository so pinning it can never create a commit-hash cycle.
    param([string]$Path, [string]$Worktree)
    if ([string]::IsNullOrWhiteSpace($Path) -or [string]::IsNullOrWhiteSpace($Worktree)) { return $false }
    $p = ($Path -replace '/', '\').TrimEnd('\')
    $w = ($Worktree -replace '/', '\').TrimEnd('\')
    if ($p -ieq $w) { return $false }
    return (-not $p.StartsWith($w + '\', [StringComparison]::OrdinalIgnoreCase))
}

function Test-PathUnderAnyForbiddenPrefix {
    # Pure write-scope guard (Task X6 forbidden write scope): TRUE when the
    # normalized path equals a forbidden write root OR falls under it via an
    # explicit separator boundary (so the sibling Task directory
    # verification/P02-NEW-TIME-X6/ is NOT mis-flagged by the shorter
    # verification/P02/ root). No filesystem access; case-insensitive; '/' and
    # '\' equivalent; trailing separators ignored. Used as defense in depth so
    # the single CreateNew output target can never land in the root
    # repository's historical verification/P02/ directory even if a freeze
    # manifest were mis-aimed.
    param([string]$Path, [string[]]$ForbiddenPrefixes)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    $normalized = ($Path -replace '/', '\').TrimEnd('\')
    foreach ($prefix in @($ForbiddenPrefixes)) {
        if ([string]::IsNullOrWhiteSpace("$prefix")) { continue }
        $prefixNormalized = ("$prefix" -replace '/', '\').TrimEnd('\')
        if ($normalized -ieq $prefixNormalized -or $normalized.StartsWith($prefixNormalized + '\', [StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    return $false
}

function Test-FreezeManifestShape {
    # Pure structural validation of the deserialized freeze manifest (I2):
    # required fields present, correct types/formats, no sentinel residue.
    # Collects ALL problems instead of stopping at the first, so Codex sees
    # the complete freeze-input defect list in one run. No filesystem access.
    param($Manifest, [string]$RunId, [object]$ExpectedBaselines)
    $errors = [Collections.Generic.List[string]]::new()
    $manifestValues = [Collections.Generic.List[string]]::new()

    function Add-FieldError([string]$Name) { $errors.Add("missing or null field: $Name") }
    function Add-SentinelScan([string]$FieldName, $Value) {
        if ($null -ne $Value -and "$Value" -like '*REPLACE_BEFORE_LIVE*') {
            $errors.Add("unfrozen sentinel residue in field: $FieldName")
        }
    }

    $schema = Get-ManifestField -Object $Manifest -Name 'schema'
    if (-not $schema.present -or [string]::IsNullOrWhiteSpace("$($schema.value)")) { Add-FieldError 'schema' }
    elseif ($schema.value -cne $ExpectedBaselines.manifestSchema) { $errors.Add("schema mismatch: got '$($schema.value)' expected '$($ExpectedBaselines.manifestSchema)'") }
    $task = Get-ManifestField -Object $Manifest -Name 'task'
    if (-not $task.present -or [string]::IsNullOrWhiteSpace("$($task.value)")) { Add-FieldError 'task' }
    elseif ($task.value -cne $ExpectedBaselines.taskId) { $errors.Add("task mismatch: got '$($task.value)' expected '$($ExpectedBaselines.taskId)'") }
    $manifestRunId = Get-ManifestField -Object $Manifest -Name 'runId'
    if (-not $manifestRunId.present -or [string]::IsNullOrWhiteSpace("$($manifestRunId.value)")) { Add-FieldError 'runId' }
    elseif ("$($manifestRunId.value)" -cne $RunId) { $errors.Add("runId mismatch: manifest '$($manifestRunId.value)' vs parameter '$RunId'") }

    foreach ($hex40Field in @('deliveryHead', 'baseCommit')) {
        $f = Get-ManifestField -Object $Manifest -Name $hex40Field
        if (-not $f.present -or $null -eq $f.value -or "$($f.value)" -notmatch '^[A-Fa-f0-9]{40}$') {
            $errors.Add("field $hex40Field must be a 40-hex commit SHA (got '$($f.value)')")
        }
        $manifestValues.Add("$($f.value)")
        Add-SentinelScan $hex40Field $f.value
    }
    foreach ($pathField in @('cwd', 'worktree', 'outputDir')) {
        $f = Get-ManifestField -Object $Manifest -Name $pathField
        if (-not $f.present -or $null -eq $f.value -or -not [IO.Path]::IsPathRooted("$($f.value)")) {
            $errors.Add("field $pathField must be an absolute path (got '$($f.value)')")
        }
        $manifestValues.Add("$($f.value)")
        Add-SentinelScan $pathField $f.value
    }

    $branch = Get-ManifestField -Object $Manifest -Name 'branch'
    if (-not $branch.present -or [string]::IsNullOrWhiteSpace("$($branch.value)")) { Add-FieldError 'branch' }
    $manifestValues.Add("$($branch.value)")
    Add-SentinelScan 'branch' $branch.value

    $targets = Get-ManifestField -Object $Manifest -Name 'outputTargets'
    if (-not $targets.present -or $null -eq $targets.value -or @($targets.value).Count -ne 1) {
        $errors.Add("outputTargets must contain exactly one CreateNew target (got $(if ($null -eq $targets.value) { 'null' } else { @($targets.value).Count }))")
    } else {
        $t = [string]@($targets.value)[0]
        if ($t -ne "run-$RunId.json") {
            $errors.Add("outputTargets[0] must be 'run-$RunId.json' (got '$t')")
        }
        $manifestValues.Add($t)
        Add-SentinelScan 'outputTargets' $t
    }

    $identity = Get-ManifestField -Object $Manifest -Name 'identity'
    if (-not $identity.present -or $null -eq $identity.value) {
        Add-FieldError 'identity'
    } else {
        $n = Get-ManifestField -Object $identity.value -Name 'name'
        $s = Get-ManifestField -Object $identity.value -Name 'sid'
        if (-not $n.present -or [string]::IsNullOrWhiteSpace("$($n.value)")) { Add-FieldError 'identity.name' }
        if (-not $s.present -or "$($s.value)" -notmatch '^S-1-[0-9A-Fa-f-]+$') { Add-FieldError 'identity.sid (S-1-... form)' }
        $manifestValues.Add("$($n.value)")
        $manifestValues.Add("$($s.value)")
        Add-SentinelScan 'identity.name' $n.value
        Add-SentinelScan 'identity.sid' $s.value
    }

    $tools = Get-ManifestField -Object $Manifest -Name 'tools'
    if (-not $tools.present -or $null -eq $tools.value) {
        Add-FieldError 'tools'
    } else {
        foreach ($toolField in @('pwshExe', 'gitExe', 'whoamiExe')) {
            $t = Get-ManifestField -Object $tools.value -Name $toolField
            if (-not $t.present -or $null -eq $t.value -or -not [IO.Path]::IsPathRooted("$($t.value)")) {
                $errors.Add("tools.$toolField must be an absolute path (got '$($t.value)')")
            }
            $manifestValues.Add("$($t.value)")
            Add-SentinelScan "tools.$toolField" $t.value
        }
    }

    $runtime = Get-ManifestField -Object $Manifest -Name 'expectedRuntime'
    if (-not $runtime.present -or $null -eq $runtime.value) {
        Add-FieldError 'expectedRuntime'
    } else {
        foreach ($rtField in @('psVersion', 'psEdition', 'languageMode', 'gitVersion')) {
            $rt = Get-ManifestField -Object $runtime.value -Name $rtField
            if (-not $rt.present -or [string]::IsNullOrWhiteSpace("$($rt.value)")) { Add-FieldError "expectedRuntime.$rtField" }
            $manifestValues.Add("$($rt.value)")
            Add-SentinelScan "expectedRuntime.$rtField" $rt.value
        }
    }

    foreach ($pinGroup in @('contractPins', 'taskDeliverablePins')) {
        $group = Get-ManifestField -Object $Manifest -Name $pinGroup
        if (-not $group.present -or $null -eq $group.value -or @($group.value).Count -lt 1) {
            $errors.Add("$pinGroup must contain at least one pin")
            continue
        }
        $seenPaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        $index = 0
        foreach ($pin in @($group.value)) {
            $pn = Get-ManifestField -Object $pin -Name 'name'
            $pp = Get-ManifestField -Object $pin -Name 'path'
            $ps = Get-ManifestField -Object $pin -Name 'size'
            $ph = Get-ManifestField -Object $pin -Name 'sha256'
            if (-not $pn.present -or [string]::IsNullOrWhiteSpace("$($pn.value)")) { $errors.Add("$pinGroup[$index].name missing/empty") }
            if (-not $pp.present -or $null -eq $pp.value -or -not [IO.Path]::IsPathRooted("$($pp.value)")) { $errors.Add("$pinGroup[$index].path must be an absolute path (got '$($pp.value)')") }
            if (-not $ps.present -or $null -eq $ps.value -or "$($ps.value)" -notmatch '^[0-9]+$') { $errors.Add("$pinGroup[$index].size must be a non-negative integer (got '$($ps.value)')") }
            if (-not $ph.present -or $null -eq $ph.value -or "$($ph.value)" -notmatch '^[A-Fa-f0-9]{64}$') { $errors.Add("$pinGroup[$index].sha256 must be 64-hex (got '$($ph.value)')") }
            if ($pp.present -and $null -ne $pp.value -and -not $seenPaths.Add(("$($pp.value)" -replace '/', '\'))) {
                $errors.Add("$pinGroup[$index].path duplicates an earlier pin path")
            }
            $manifestValues.Add("$($pn.value)")
            $manifestValues.Add("$($pp.value)")
            $manifestValues.Add("$($ph.value)")
            Add-SentinelScan "$pinGroup[$index]" "$($pn.value) $($pp.value) $($ph.value)"
            $index++
        }
    }

    $mutable = Get-ManifestField -Object $Manifest -Name 'mutableObservationPaths'
    if (-not $mutable.present -or $null -eq $mutable.value -or @($mutable.value).Count -lt 1) {
        $errors.Add('mutableObservationPaths must contain at least one path')
    } else {
        $mIndex = 0
        foreach ($mp in @($mutable.value)) {
            if ($null -eq $mp -or -not [IO.Path]::IsPathRooted("$mp")) {
                $errors.Add("mutableObservationPaths[$mIndex] must be an absolute path (got '$mp')")
            }
            $manifestValues.Add("$mp")
            Add-SentinelScan "mutableObservationPaths[$mIndex]" "$mp"
            $mIndex++
        }
    }

    return [ordered]@{
        valid = ($errors.Count -eq 0)
        errors = @($errors.ToArray())
        scannedValueCount = $manifestValues.Count
    }
}

function Test-FreezeManifestBinding {
    # Pure binding validation (I2): cross-checks the manifest against the
    # source-side structural baselines and the invocation parameters. This
    # catches a manifest aimed at the wrong checkout/output root WITHOUT
    # embedding any commit hash or self hash in the source. No filesystem
    # access. The collector-source pin presence is enforced here so the
    # manifest can never omit the collector's own full SHA binding.
    param($Manifest, [string]$RunId, [object]$ExpectedBaselines)
    $errors = [Collections.Generic.List[string]]::new()

    $manifestRunId = (Get-ManifestField -Object $Manifest -Name 'runId').value
    if ("$manifestRunId" -cne $RunId) { $errors.Add("runId binding: manifest '$manifestRunId' != parameter '$RunId'") }

    $base = (Get-ManifestField -Object $Manifest -Name 'baseCommit').value
    if ("$base" -cne $ExpectedBaselines.baseCommit) { $errors.Add("baseCommit binding: manifest '$base' != source baseline '$($ExpectedBaselines.baseCommit)'") }

    $branch = (Get-ManifestField -Object $Manifest -Name 'branch').value
    if ("$branch" -cne $ExpectedBaselines.expectedBranch) { $errors.Add("branch binding: manifest '$branch' != source baseline '$($ExpectedBaselines.expectedBranch)'") }

    $worktree = "$((Get-ManifestField -Object $Manifest -Name 'worktree').value)"
    if ($worktree -ne '' -and ($worktree -replace '/', '\') -ine (($ExpectedBaselines.worktree -replace '/', '\'))) {
        $errors.Add("worktree binding: manifest '$worktree' != source baseline '$($ExpectedBaselines.worktree)'")
    }

    $outputDir = "$((Get-ManifestField -Object $Manifest -Name 'outputDir').value)"
    if ($outputDir -ne '' -and ($outputDir -replace '/', '\') -ine (($ExpectedBaselines.outputDir -replace '/', '\'))) {
        $errors.Add("outputDir binding: manifest '$outputDir' != source baseline '$($ExpectedBaselines.outputDir)'")
    }

    $tools = (Get-ManifestField -Object $Manifest -Name 'tools').value
    if ($null -ne $tools) {
        foreach ($pair in @(@('pwshExe', $ExpectedBaselines.pwshExe), @('gitExe', $ExpectedBaselines.gitExe), @('whoamiExe', $ExpectedBaselines.whoamiExe))) {
            $mv = "$((Get-ManifestField -Object $tools -Name $pair[0]).value)"
            if ($mv -ne '' -and $mv -ine $pair[1]) {
                $errors.Add("tools.$($pair[0]) binding: manifest '$mv' != source baseline '$($pair[1])'")
            }
        }
    }

    $identity = (Get-ManifestField -Object $Manifest -Name 'identity').value
    if ($null -ne $identity) {
        $mn = "$((Get-ManifestField -Object $identity -Name 'name').value)"
        $ms = "$((Get-ManifestField -Object $identity -Name 'sid').value)"
        if ($mn -ne '' -and $mn -ine $ExpectedBaselines.identityName) {
            $errors.Add("identity.name binding: manifest '$mn' != source baseline '$($ExpectedBaselines.identityName)'")
        }
        if ($ms -ne '' -and $ms -ine $ExpectedBaselines.identitySid) {
            $errors.Add("identity.sid binding: manifest '$ms' != source baseline '$($ExpectedBaselines.identitySid)'")
        }
    }

    $runtime = (Get-ManifestField -Object $Manifest -Name 'expectedRuntime').value
    if ($null -ne $runtime) {
        foreach ($pair in @(@('psVersion', $ExpectedBaselines.psVersion), @('psEdition', $ExpectedBaselines.psEdition),
                          @('languageMode', $ExpectedBaselines.languageMode), @('gitVersion', $ExpectedBaselines.gitVersion))) {
            $mv = "$((Get-ManifestField -Object $runtime -Name $pair[0]).value)"
            if ($mv -ne '' -and $mv -cne $pair[1]) {
                $errors.Add("expectedRuntime.$($pair[0]) binding: manifest '$mv' != source baseline '$($pair[1])'")
            }
        }
    }

    # The manifest must pin the executor source file itself by its exact path
    # (the full SHA value was already format-checked by the shape gate; this
    # binding guarantees the self-pin cannot be omitted from the freeze).
    $deliverables = (Get-ManifestField -Object $Manifest -Name 'taskDeliverablePins').value
    $executorSelfPinFound = $false
    if ($null -ne $deliverables) {
        $selfPathNormalized = (($ExpectedBaselines.worktree -replace '/', '\') + '\verification\P02-NEW-TIME-X6\executor\p02-new-time-x6.ps1')
        foreach ($pin in @($deliverables)) {
            $pp = "$((Get-ManifestField -Object $pin -Name 'path').value)"
            if (($pp -replace '/', '\') -ieq $selfPathNormalized) { $executorSelfPinFound = $true; break }
        }
    }
    if (-not $executorSelfPinFound) {
        $errors.Add("taskDeliverablePins must contain the executor source self-pin at $ExpectedBaselines.worktree/verification/P02-NEW-TIME-X6/executor/p02-new-time-x6.ps1")
    }

    return [ordered]@{
        valid = ($errors.Count -eq 0)
        errors = @($errors.ToArray())
    }
}

function New-GitPrefixArgv {
    # Fixed Git prefix for every child (no pager, no fsmonitor, no hooks).
    return [string[]]@('--no-pager', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=NUL')
}

function New-StatusArgv {
    # Exact frozen status argv for the worktree (full untracked detail, verbatim).
    return [string[]]@('--no-pager', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=NUL') +
        @('--no-optional-locks', 'status', '--porcelain=v2', '-z', '--untracked-files=all', '--no-renames')
}

function New-CheckIgnoreArgv {
    param([string]$Path)
    return [string[]]@('--no-pager', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=NUL') +
        @('check-ignore', '--no-index', '--quiet', '--', $Path)
}

function Test-BranchRefMatchesManifest {
    # git symbolic-ref --quiet HEAD returns the full ref (refs/heads/<name>);
    # the freeze manifest pins only the short branch name, so the runtime ref
    # must equal the manifest name prefixed with refs/heads/ (any other ref
    # namespace, a wrong branch or empty detached-HEAD output fails closed).
    param([string]$BranchRef, [string]$ManifestBranch)
    return ($BranchRef -ceq "refs/heads/$ManifestBranch")
}

function Test-GitToplevelMatchesWorktree {
    # Pure string check for git-toplevel-matches-worktree: Git for Windows
    # reports the rev-parse --show-toplevel path with forward slashes while
    # the frozen manifest worktree may be pinned with backslashes, so BOTH
    # sides are normalized to Windows separators (trailing separator trimmed)
    # before the case-insensitive compare. A different volume, directory or
    # leaf — and empty input on either side — fails closed.
    param([string]$Toplevel, [string]$Worktree)
    if ([string]::IsNullOrWhiteSpace($Toplevel) -or [string]::IsNullOrWhiteSpace($Worktree)) { return $false }
    $t = ($Toplevel -replace '/', '\').TrimEnd('\')
    $w = ($Worktree -replace '/', '\').TrimEnd('\')
    return ($t -ieq $w)
}

function New-ObservationRecord {
    param([string]$Id, [string]$Kind)
    if ([string]::IsNullOrWhiteSpace($Id)) { throw "OBSERVATION_CONTRACT_VIOLATION: empty Id" }
    if (@('helper-process', 'in-process-getter') -notcontains $Kind) {
        throw "OBSERVATION_CONTRACT_VIOLATION: unknown kind '$Kind' for $Id"
    }
    return [ordered]@{
        seq = -1
        id = $Id
        kind = $Kind
        startedUtc = $null
        finishedUtc = $null
        executable = $null
        argv = $null
        cwd = $null
        allowedExit = $null
        method = $null
        input = $null
        output = $null
        removedGitEnvironmentNames = $null
        exception = $null
        state = 'NOT_STARTED'
        exit = $null
    }
}

function Add-ObservationException {
    param($Observation, [string]$Stage, $ErrorRecord)
    $Observation.exception = [ordered]@{
        stage = $Stage
        type = $ErrorRecord.Exception.GetType().FullName
        message = [string]$ErrorRecord.Exception.Message
        hresult = $ErrorRecord.Exception.HResult
    }
    $Observation.state = 'ERROR'
    return $Observation
}

function New-CheckRecord {
    # Every check must reference its raw observation through a parseable JSON
    # Pointer; unparseable collection-style labels are rejected (fail-closed).
    param(
        [string]$Id,
        [string]$Category,
        [string]$Expected,
        [string]$ObservedPointer,
        [string]$ObservedSummary,
        [ValidateSet('PASS', 'FAIL', 'NOT_VERIFIED', 'NOT_RUN')]
        [string]$Result,
        [string]$Note = ''
    )
    if ([string]::IsNullOrWhiteSpace($Id)) { throw "CHECK_CONTRACT_VIOLATION: empty Id" }
    if ([string]::IsNullOrWhiteSpace($Expected)) { throw "CHECK_CONTRACT_VIOLATION: empty Expected for $Id" }
    if ([string]::IsNullOrWhiteSpace($ObservedPointer) -or -not $ObservedPointer.StartsWith('/observations/')) {
        throw "CHECK_CONTRACT_VIOLATION: check '$Id' lacks a parseable raw observation JSON Pointer"
    }
    return [ordered]@{
        id = $Id
        category = $Category
        expected = $Expected
        observedPointer = $ObservedPointer
        observedSummary = $ObservedSummary
        result = $Result
        note = $Note
    }
}

function Get-VolumeEvidence {
    # Real volume facts for a fixed path - DriveInfo readiness and actual drive
    # format - instead of inferring "same volume" from a shared drive letter.
    param([string]$Path)
    $root = [IO.Path]::GetPathRoot(($Path -replace '/', '\'))
    $drive = [IO.DriveInfo]::new($root)
    return [ordered]@{
        pathRoot = $root
        isReady = $drive.IsReady
        driveFormat = $(if ($drive.IsReady) { $drive.DriveFormat } else { $null })
        driveType = $drive.DriveType.ToString()
    }
}

function Test-PathAncestorsOrdinary {
    # Classify the LEAF itself AND every ancestor up to the drive root.
    # Lstat semantics: a dangling junction/link still reports exists=true with
    # ReparsePoint, so it can never pass an absence or ordinary check; the link
    # target is NEVER followed or read.
    param([string]$Path)
    $result = [ordered]@{
        path = $Path
        allOrdinary = $false
        leafExists = $false
        leafIsDirectory = $false
        leafIsFile = $false
        leafAttributes = $null
        leafReparsePoint = $null
        leafAttributeError = $null
        leafAbsent = $true
        leafLinkTarget = $null
        reparseComponents = [Collections.Generic.List[string]]::new()
        nonDirectoryComponents = [Collections.Generic.List[string]]::new()
        missingComponents = [Collections.Generic.List[string]]::new()
        checkedAncestors = 0
    }
    # --- leaf classification (lstat; never follows the link target) ---
    $leafAttr = $null
    $leafAttrException = $null
    try {
        $leafAttr = [IO.File]::GetAttributes($Path)
    } catch {
        $leafAttrException = $_
    }
    if ($null -ne $leafAttr) {
        $result.leafExists = $true
        $result.leafAbsent = $false
        $result.leafAttributes = $leafAttr.ToString()
        $result.leafReparsePoint = (($leafAttr -band [IO.FileAttributes]::ReparsePoint) -ne 0)
        $result.leafIsDirectory = (($leafAttr -band [IO.FileAttributes]::Directory) -ne 0)
        $result.leafIsFile = -not $result.leafIsDirectory
        if ($result.leafReparsePoint) {
            $result.reparseComponents.Add($Path)
            try {
                $fi = [IO.FileInfo]::new($Path)
                $di = [IO.DirectoryInfo]::new($Path)
                $result.leafLinkTarget = if ($null -ne $fi.LinkTarget) { $fi.LinkTarget } elseif ($null -ne $di.LinkTarget) { $di.LinkTarget } else { $null }
            } catch { }
        }
    } else {
        $actualEx = if ($null -ne $leafAttrException.Exception.InnerException) { $leafAttrException.Exception.InnerException } else { $leafAttrException.Exception }
        if ($actualEx -is [IO.FileNotFoundException] -or $actualEx -is [IO.DirectoryNotFoundException]) {
            $result.leafExists = $false
            $result.leafAbsent = $true
            $result.leafIsDirectory = $false
            $result.leafIsFile = $false
            $result.leafReparsePoint = $false
        } else {
            $result.leafExists = $false
            $result.leafAbsent = $false
            $result.leafAttributeError = "$($actualEx.GetType().FullName): $($actualEx.Message)"
        }
    }
    # --- ancestor chain ---
    $normalized = ($Path -replace '/', '\').TrimEnd('\')
    $prefix = [IO.Path]::GetPathRoot($normalized)
    $current = $normalized
    $guard = 0
    while ($guard -lt 128) {
        $guard++
        if ([string]::IsNullOrWhiteSpace($current)) { break }
        if ($current -ceq $prefix) { break }
        $parent = Split-Path -Parent $current
        if ([string]::IsNullOrWhiteSpace($parent)) { break }
        if ([IO.Directory]::Exists($parent)) {
            $di = [IO.DirectoryInfo]::new($parent)
            $result.checkedAncestors++
            if (($di.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                $result.reparseComponents.Add($parent)
            }
        } elseif ([IO.File]::Exists($parent)) {
            $result.nonDirectoryComponents.Add($parent)
        } else {
            $result.missingComponents.Add($parent)
        }
        if ($current -ceq $parent) { break }
        $current = $parent
    }
    $result.reparseComponents = @($result.reparseComponents.ToArray())
    $result.nonDirectoryComponents = @($result.nonDirectoryComponents.ToArray())
    $result.missingComponents = @($result.missingComponents.ToArray())
    $result.allOrdinary = ($result.reparseComponents.Count -eq 0 -and
                           $result.nonDirectoryComponents.Count -eq 0 -and
                           $result.missingComponents.Count -eq 0 -and
                           $result.checkedAncestors -gt 0 -and
                           $null -eq $result.leafAttributeError)
    return $result
}

function New-OutputPreflightCapture {
    # Capture the REAL pre-create conditions strictly BEFORE CreateNew so the
    # post-create observation can report them without fabrication.
    param([string]$OutputDir, [string]$OutputFile)
    $chain = Test-PathAncestorsOrdinary -Path $OutputDir
    $outputFileChain = Test-PathAncestorsOrdinary -Path $OutputFile
    $volume = Get-VolumeEvidence -Path $OutputDir
    $targetAbsent = ($outputFileChain.leafAbsent -and -not (Test-Path -LiteralPath $OutputFile))
    return [ordered]@{
        capturedBeforeCreateNew = $true
        capturedUtc = [DateTime]::UtcNow.ToString('o')
        outputDir = $OutputDir
        outputFile = $OutputFile
        chain = $chain
        chainAllOrdinary = $chain.allOrdinary
        outputFileChain = $outputFileChain
        targetAbsent = $targetAbsent
        volume = $volume
    }
}

function New-OutputPostCreateFacts {
    # Post-create facts recorded AFTER the successful CreateNew only.
    param([string]$OutputFile)
    $attr = [IO.File]::GetAttributes($OutputFile)
    return [ordered]@{
        capturedAfterCreateNew = $true
        capturedUtc = [DateTime]::UtcNow.ToString('o')
        targetExists = $true
        targetAttributes = $attr.ToString()
        exclusiveStreamOpen = $true
    }
}

function Open-ExclusiveCreateNew {
    # Single write channel: CreateNew + FileShare.None; throws on conflict (no
    # overwrite, no retry, no delete, no File.Replace). Callers must treat any
    # throw as fail-closed.
    param([string]$Path)
    return [IO.FileStream]::new($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
}

function New-MetaLineObject {
    # Pure meta-line factory shared by collector and selftest (full field shape).
    # Fully parameterized: no script-state access, so the pure selftest can
    # extract and run it from the AST with its own small Constants object and a
    # selftest-built freeze manifest. All freeze values come from the validated
    # external manifest (I2); the manifest's own path/hash triple is recorded
    # verbatim so the closed evidence names exactly which freeze input produced it.
    param(
        [string]$RunId,
        [string]$StartedUtc,
        [object]$Constants,
        [object]$Manifest,
        [string]$ManifestPath,
        [string]$ManifestSha256,
        [object]$NotRunTable,
        [string[]]$ForbiddenHistorySegments
    )
    return [ordered]@{
        kind = 'meta'
        schema = $Constants.schema
        task = $Constants.task
        runId = $RunId
        evidenceClass = $Constants.evidenceClass
        substitution = $Constants.substitutionLabel
        historyNote = $Constants.historyNote
        notRun = $NotRunTable
        freezeManifest = [ordered]@{
            schema = (Get-ManifestField -Object $Manifest -Name 'schema').value
            path = $ManifestPath
            sha256 = $ManifestSha256
            runId = (Get-ManifestField -Object $Manifest -Name 'runId').value
        }
        frozenInputs = [ordered]@{
            baseCommit = (Get-ManifestField -Object $Manifest -Name 'baseCommit').value
            expectedBranch = (Get-ManifestField -Object $Manifest -Name 'branch').value
            deliveryHead = (Get-ManifestField -Object $Manifest -Name 'deliveryHead').value
            cwd = (Get-ManifestField -Object $Manifest -Name 'cwd').value
            outputDir = (Get-ManifestField -Object $Manifest -Name 'outputDir').value
            worktree = (Get-ManifestField -Object $Manifest -Name 'worktree').value
        }
        tools = $Constants.tools
        frozenContractPins = [object[]](@((Get-ManifestField -Object $Manifest -Name 'contractPins').value) | ForEach-Object {
            [ordered]@{
                name = (Get-ManifestField -Object $_ -Name 'name').value
                path = (Get-ManifestField -Object $_ -Name 'path').value
                size = (Get-ManifestField -Object $_ -Name 'size').value
                sha256 = (Get-ManifestField -Object $_ -Name 'sha256').value
            }
        })
        mutableObservationPaths = [string[]]@((Get-ManifestField -Object $Manifest -Name 'mutableObservationPaths').value)
        mutablePinPolicy = 'recorded as plain observations only; mutable STATUS/Plan/checkpoint are NEVER immutable hash pins'
        frozenTaskDeliverablePins = [object[]](@((Get-ManifestField -Object $Manifest -Name 'taskDeliverablePins').value) | ForEach-Object {
            [ordered]@{
                name = (Get-ManifestField -Object $_ -Name 'name').value
                path = (Get-ManifestField -Object $_ -Name 'path').value
                size = (Get-ManifestField -Object $_ -Name 'size').value
                sha256 = (Get-ManifestField -Object $_ -Name 'sha256').value
            }
        })
        forbiddenHistorySegments = [string[]]$ForbiddenHistorySegments
        outputRule = 'single exclusive CreateNew NDJSON stream; line kinds meta/observation/closed; final closed line is self-contained; every check references /observations/<seq>/... JSON Pointers'
        startedUtc = $StartedUtc
    }
}

function New-ClosedLineObject {
    # Pure closed-line factory shared by collector and selftest (full field shape).
    # Fully parameterized: no script-state access.
    param(
        [string]$RunId,
        [object]$Constants,
        [string]$State,
        [string]$Disposition,
        [int]$ExitCode,
        [object]$NotRunTable,
        [object[]]$Observations,
        [object[]]$Checks,
        [string[]]$BlockedReasons
    )
    $passCount = 0; $failCount = 0; $nvCount = 0; $nrCount = 0
    foreach ($c in @($Checks)) {
        switch ($c.result) {
            'PASS' { $passCount++ }
            'FAIL' { $failCount++ }
            'NOT_VERIFIED' { $nvCount++ }
            'NOT_RUN' { $nrCount++ }
        }
    }
    return [ordered]@{
        kind = 'closed'
        schema = $Constants.schema
        task = $Constants.task
        runId = $RunId
        state = $State
        disposition = $Disposition
        blockedReasons = @($BlockedReasons)
        exitCode = $ExitCode
        evidenceClass = $Constants.evidenceClass
        substitution = $Constants.substitutionLabel
        historyNote = $Constants.historyNote
        notRun = $NotRunTable
        observations = @($Observations)
        checks = @($Checks)
        counts = [ordered]@{
            observations = @($Observations).Count
            checks = @($Checks).Count
            pass = $passCount; fail = $failCount; notVerified = $nvCount; notRunChecks = $nrCount
        }
        finishedUtc = [DateTime]::UtcNow.ToString('o')
    }
}

# ===========================================================================
# Streaming framework (writes each line immediately; partial evidence survives).
# ===========================================================================
function Write-StreamLine {
    param([string]$Json)
    Require ($null -ne $script:Writer) 'STREAM_CLOSED: writer is not available'
    $script:Writer.WriteLine($Json)
    $script:Writer.Flush()
}

function Save-Observation {
    param([object]$Observation)
    $Observation.seq = $script:ObservationSeq
    $script:ObservationSeq++
    $script:Observations.Add($Observation)
    Write-StreamLine -Json (ConvertTo-Json -InputObject ([ordered]@{ kind = 'observation'; observation = $Observation }) -Depth 96 -Compress)
    return "/observations/$($Observation.seq)"
}

function Add-Check {
    param(
        [string]$Id, [string]$Category, [string]$Expected, [string]$ObservedPointer,
        [string]$ObservedSummary, [string]$Result, [string]$Note = ''
    )
    $record = New-CheckRecord -Id $Id -Category $Category -Expected $Expected `
        -ObservedPointer $ObservedPointer -ObservedSummary $ObservedSummary -Result $Result -Note $Note
    # A check pointer must resolve to an EXISTING observation right now; dangling
    # pointers fail closed instead of being accepted by prefix alone.
    $graph = [ordered]@{ observations = $script:Observations }
    $resolved = Resolve-JsonPointer -Graph $graph -Pointer $record.observedPointer
    Require $resolved.found "DANGLING_POINTER: check '$Id' pointer '$($record.observedPointer)' does not resolve to an existing observation"
    $script:Checks.Add($record)
    if ($Result -eq 'FAIL') { $script:BlockedReasons.Add("CHECK_FAIL:$Id") }
    return $record
}

function Write-ClosedLine {
    param([string]$State, [string]$Disposition, [int]$ExitCode)
    $closed = New-ClosedLineObject -RunId $RunId -Constants $script:Constants -State $State -Disposition $Disposition -ExitCode $ExitCode `
        -NotRunTable $script:NotRunTable -Observations @($script:Observations.ToArray()) `
        -Checks @($script:Checks.ToArray()) -BlockedReasons @($script:BlockedReasons.ToArray())
    Write-StreamLine -Json (ConvertTo-Json -InputObject $closed -Depth 96 -Compress)
}

# ===========================================================================
# Observation drivers.
# ===========================================================================
function Invoke-InProcessGetter {
    param([string]$Id, [string]$Method, [object]$GetterInput, [scriptblock]$Body)
    $obs = New-ObservationRecord -Id $Id -Kind 'in-process-getter'
    $obs.method = $Method
    $obs.input = $GetterInput
    $obs.startedUtc = [DateTime]::UtcNow.ToString('o')
    try {
        $value = & $Body $GetterInput
        $obs.output = [ordered]@{ value = $value }
        $obs.state = 'OK'
    } catch {
        $obs.output = [ordered]@{ value = $null }
        $null = Add-ObservationException -Observation $obs -Stage 'getter' -ErrorRecord $_
    }
    $obs.finishedUtc = [DateTime]::UtcNow.ToString('o')
    $pointer = Save-Observation -Observation $obs
    Require ($obs.state -eq 'OK') "GETTER_ERROR_FAIL_CLOSED: $Id (see observation seq $($obs.seq))"
    return @{ observation = $obs; pointer = $pointer }
}

function Invoke-HelperProcess {
    param(
        [string]$Id,
        [string]$Executable,
        [string]$Cwd,
        [string[]]$Argv,
        [int[]]$AllowedExit = @(0),
        [scriptblock]$PostProcess = $null
    )
    $obs = New-ObservationRecord -Id $Id -Kind 'helper-process'
    $obs.executable = $Executable
    $obs.cwd = $Cwd
    $obs.argv = [string[]]$Argv
    $obs.allowedExit = [int[]]$AllowedExit
    $obs.startedUtc = [DateTime]::UtcNow.ToString('o')
    $process = $null
    $stdoutMs = [IO.MemoryStream]::new()
    $stderrMs = [IO.MemoryStream]::new()
    $outCopy = $null
    $errCopy = $null
    try {
        Require ([IO.File]::Exists($Executable)) "HELPER_START_FAILED: executable not found: $Executable"
        Require ([IO.Directory]::Exists($Cwd)) "HELPER_START_FAILED: cwd not found: $Cwd"
        $psi = [Diagnostics.ProcessStartInfo]::new()
        $psi.FileName = $Executable
        $psi.WorkingDirectory = $Cwd
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        foreach ($argument in $Argv) { $null = $psi.ArgumentList.Add($argument) }
        $contextNames = @('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR',
                          'GIT_PREFIX', 'GIT_CEILING_DIRECTORIES', 'GIT_EXTERNAL_DIFF')
        $removedNames = [Collections.Generic.List[string]]::new()
        $contextInherited = [Collections.Generic.List[string]]::new()
        foreach ($key in @($psi.Environment.Keys)) {
            if ($contextNames -contains $key -or $key -like 'GIT_CONFIG*') {
                $contextInherited.Add($key)
            } elseif ($key -like 'GIT_TRACE*') {
                $removedNames.Add($key)
                $null = $psi.Environment.Remove($key)
            }
        }
        $obs.removedGitEnvironmentNames = @($removedNames.ToArray())
        Require ($contextInherited.Count -eq 0) ("INHERITED_GIT_CONTEXT_OVERRIDE: child not launched; names recorded: " +
            "$($contextInherited -join ',') (values withheld)")
        $psi.Environment['GIT_OPTIONAL_LOCKS'] = '0'
        $psi.Environment['GIT_TERMINAL_PROMPT'] = '0'
        $process = [Diagnostics.Process]::new()
        $process.StartInfo = $psi
        $null = $process.Start()
        $outCopy = $process.StandardOutput.BaseStream.CopyToAsync($stdoutMs)
        $errCopy = $process.StandardError.BaseStream.CopyToAsync($stderrMs)
        $process.WaitForExit()
        $outCopy.Wait()
        $errCopy.Wait()
        $obs.exit = $process.ExitCode
        # Unified helper observation envelope (AC3-WHOAMI-HELPER-OUTPUT-SHAPE):
        # output.value.{stdout,stderr} matches Invoke-InProcessGetter's
        # output.value shape read by every consumer and /output/value/... pointer.
        $obs.output = [ordered]@{
            value = [ordered]@{
                stdout = ConvertTo-RawBytesRecord -Bytes ($stdoutMs.ToArray())
                stderr = ConvertTo-RawBytesRecord -Bytes ($stderrMs.ToArray())
            }
        }
        if ($AllowedExit -contains $process.ExitCode) { $obs.state = 'OK' } else { $obs.state = 'UNEXPECTED_EXIT' }
        if ($null -ne $PostProcess) {
            # A PostProcess exception never clobbers the captured OS exit.
            try {
                & $PostProcess $obs $stdoutMs $stderrMs
            } catch {
                $obs.postProcessException = [ordered]@{
                    stage = 'postProcess'
                    type = $_.Exception.GetType().FullName
                    message = [string]$_.Exception.Message
                    hresult = $_.Exception.HResult
                }
                $obs.state = 'POST_PROCESS_ERROR'
            }
        }
    } catch {
        if ($null -eq $obs.output) {
            # Same output.value.{stdout,stderr} envelope as the success path;
            # the exception path must never emit a second producer shape.
            $obs.output = [ordered]@{
                value = [ordered]@{
                    stdout = ConvertTo-RawBytesRecord -Bytes ($stdoutMs.ToArray())
                    stderr = ConvertTo-RawBytesRecord -Bytes ($stderrMs.ToArray())
                }
            }
        }
        # An exception path must not erase an exit the process already returned;
        # exit stays $null only when the process never got that far.
        $null = Add-ObservationException -Observation $obs -Stage 'invoke' -ErrorRecord $_
    } finally {
        if ($null -ne $process) { try { $process.Dispose() } catch { } }
        try { $stdoutMs.Dispose() } catch { }
        try { $stderrMs.Dispose() } catch { }
    }
    $obs.finishedUtc = [DateTime]::UtcNow.ToString('o')
    $pointer = Save-Observation -Observation $obs
    Require ($obs.state -eq 'OK') "HELPER_ERROR_FAIL_CLOSED: $Id state=$($obs.state) (see observation seq $($obs.seq))"
    return @{ observation = $obs; pointer = $pointer }
}

function Invoke-GitHelper {
    param([string]$Id, [string]$Cwd, [string[]]$GitArgv, [int[]]$AllowedExit = @(0), [scriptblock]$PostProcess = $null)
    $argv = @(New-GitPrefixArgv) + @($GitArgv)
    return Invoke-HelperProcess -Id $Id -Executable $script:GitExe -Cwd $Cwd -Argv $argv -AllowedExit $AllowedExit -PostProcess $PostProcess
}

function Get-FilePinObservation {
    param([string]$Id, [string]$Path)
    return Invoke-InProcessGetter -Id $Id `
        -Method 'IO.File.ReadAllBytes + SHA256 (read-only file pin)' `
        -GetterInput ([ordered]@{ path = $Path }) `
        -Body {
            param($src)
            $bytes = [IO.File]::ReadAllBytes($src.path)
            [ordered]@{
                exists = $true
                bytesCount = $bytes.Length
                sha256 = Get-Sha256HexFromBytes -Bytes $bytes
                readUtc = [DateTime]::UtcNow.ToString('o')
            }
        }
}

function Get-PathProbeObservation {
    param([string]$Id, [string]$Path)
    return Invoke-InProcessGetter -Id $Id `
        -Method 'IO.File.GetAttributes / FileSystemInfo (lstat existence probe; never follows link target)' `
        -GetterInput ([ordered]@{ path = $Path }) `
        -Body {
            param($src)
            $attr = $null
            $attrEx = $null
            try {
                $attr = [IO.File]::GetAttributes($src.path)
            } catch {
                $attrEx = $_.Exception
            }
            $value = Get-PathProbeValueFromAttributes -Path $src.path -Attributes $attr -Exception $attrEx
            if ($value.exists) {
                if ($value.reparsePoint) {
                    # Never read target metadata for a reparse leaf; following a
                    # file link loses link metadata for dangling links.
                    try {
                        if ($value.isDirectory) {
                            $di = [IO.DirectoryInfo]::new($src.path)
                            $value.linkTarget = $di.LinkTarget
                        } else {
                            $fi = [IO.FileInfo]::new($src.path)
                            $value.linkTarget = $fi.LinkTarget
                        }
                    } catch {
                        $value.linkTargetError = "$($_.Exception.GetType().FullName): $($_.Exception.Message)"
                    }
                } else {
                    if (-not $value.isDirectory) {
                        try {
                            $fi = [IO.FileInfo]::new($src.path)
                            $value.length = $fi.Length
                        } catch { }
                    }
                }
            }
            return $value
        }
}

# ===========================================================================
# Main sequence.
# ===========================================================================
try {
    # ---- 1) freeze gate (I2): parameter syntax + safe path/history boundaries
    #         BEFORE opening the manifest; manifest bytes vs the argv-supplied
    #         expected SHA; strict schema/shape/binding validation. ALL of it
    #         fails closed BEFORE any CreateNew output or child process. ----
    Require (-not [string]::IsNullOrWhiteSpace($FreezeManifestPath)) 'FREEZE_MANIFEST_INVALID: FreezeManifestPath is empty'
    Require (-not [regex]::IsMatch($FreezeManifestPath, '[\x00-\x1F]')) 'FREEZE_MANIFEST_INVALID: FreezeManifestPath contains control characters'
    Require (-not (Test-PathContainsHistorySegment -Path $FreezeManifestPath -ForbiddenSegments $script:ForbiddenHistorySegments)) "HISTORY_SCOPE_VIOLATION: freeze manifest path references a historical evidence family: $FreezeManifestPath"
    Require (Test-PathOutsideRepository -Path $FreezeManifestPath -Worktree $script:Worktree) "FREEZE_MANIFEST_INVALID: freeze manifest must live outside the Git worktree/repository: $FreezeManifestPath"
    Require ([IO.File]::Exists($FreezeManifestPath)) "FREEZE_MANIFEST_INVALID: freeze manifest not found: $FreezeManifestPath"

    # ---- manifest bytes vs the independently argv-supplied expected SHA ----
    $manifestBytes = [IO.File]::ReadAllBytes($FreezeManifestPath)
    $manifestIntegrity = Test-FreezeManifestBytes -Bytes $manifestBytes -ExpectedSha256 $FreezeManifestSha256
    Require $manifestIntegrity.match ("FREEZE_MANIFEST_INVALID: manifest bytes do not match the argv-supplied expected SHA-256 (tampered or stale freeze input): expected=$($manifestIntegrity.expectedSha256) actual=$($manifestIntegrity.actualSha256)")

    # ---- strict validation of the manifest (pure seams; never throws on fields) ----
    $manifestText = ConvertTo-SafeUtf8Text -Bytes $manifestBytes
    Require ($null -ne $manifestText) 'FREEZE_MANIFEST_INVALID: manifest is not valid UTF-8'
    $manifest = $null
    try { $manifest = ConvertFrom-Json -InputObject $manifestText } catch {
        Require $false ("FREEZE_MANIFEST_INVALID: manifest is not valid JSON: " + [string]$_.Exception.Message)
    }
    $shapeResult = Test-FreezeManifestShape -Manifest $manifest -RunId $RunId -ExpectedBaselines $script:ExpectedBaselines
    Require $shapeResult.valid ("FREEZE_MANIFEST_INVALID: manifest shape validation failed: " + ($shapeResult.errors -join '; '))
    $bindingResult = Test-FreezeManifestBinding -Manifest $manifest -RunId $RunId -ExpectedBaselines $script:ExpectedBaselines
    Require $bindingResult.valid ("FREEZE_MANIFEST_INVALID: manifest binding validation failed: " + ($bindingResult.errors -join '; '))

    # ---- resolve manifest values (everything validated above) ----
    $manifestDeliveryHead = (Get-ManifestField -Object $manifest -Name 'deliveryHead').value
    $manifestWorktree = (Get-ManifestField -Object $manifest -Name 'worktree').value
    $manifestOutputDir = (Get-ManifestField -Object $manifest -Name 'outputDir').value
    $manifestCwd = (Get-ManifestField -Object $manifest -Name 'cwd').value
    $manifestBaseCommit = (Get-ManifestField -Object $manifest -Name 'baseCommit').value
    $manifestBranch = (Get-ManifestField -Object $manifest -Name 'branch').value
    $manifestIdentity = (Get-ManifestField -Object $manifest -Name 'identity').value
    $manifestRuntime = (Get-ManifestField -Object $manifest -Name 'expectedRuntime').value
    $manifestContractPins = @((Get-ManifestField -Object $manifest -Name 'contractPins').value)
    $manifestDeliverablePins = @((Get-ManifestField -Object $manifest -Name 'taskDeliverablePins').value)
    $manifestMutablePaths = @((Get-ManifestField -Object $manifest -Name 'mutableObservationPaths').value)
    $manifestOutputTarget = [string]@((Get-ManifestField -Object $manifest -Name 'outputTargets').value)[0]
    $outputFile = Join-Path $manifestOutputDir $manifestOutputTarget

    # ---- 2) fail-closed history isolation over the COMPLETE freeze path set
    #         (manifest itself, output target, worktree, cwd, every pin and
    #         mutable path) BEFORE any further filesystem/process API ----
    $prePaths = @($FreezeManifestPath, $outputFile, $manifestWorktree, $manifestCwd) +
                @($manifestContractPins | ForEach-Object { (Get-ManifestField -Object $_ -Name 'path').value }) +
                @($manifestDeliverablePins | ForEach-Object { (Get-ManifestField -Object $_ -Name 'path').value }) +
                @($manifestMutablePaths)
    $preIsolation = Assert-TaskPathIsolation -Paths $prePaths -ForbiddenSegments $script:ForbiddenHistorySegments
    Require (-not $preIsolation.anyUnderHistory) ('HISTORY_SCOPE_VIOLATION: a freeze-manifest path references a historical evidence family; refusing to continue: ' +
        "$($preIsolation.underHistoryPaths -join ';')")

    # ---- 2b) Task X6 forbidden write scope (defense in depth): the single
    #          output target may never fall under the root repository's
    #          historical verification/P02/ directory, regardless of what the
    #          freeze manifest says. Fail-closed BEFORE CreateNew. ----
    Require (-not (Test-PathUnderAnyForbiddenPrefix -Path $outputFile -ForbiddenPrefixes $script:ForbiddenWritePrefixes)) "HISTORY_SCOPE_VIOLATION: X6 output target falls under the forbidden historical write root (verification/P02/): $outputFile"

    # ---- 3) output-exists / CWD / preflight checks (still BEFORE CreateNew) ----
    Require (-not [IO.File]::Exists($outputFile)) "OUTPUT_PRECHECK_FAILED: target already exists (CreateNew contract, no overwrite, no retry under the same RunId): $outputFile"
    Require ([IO.Directory]::GetCurrentDirectory() -ieq ($manifestCwd -replace '/', '\')) "FREEZE_MANIFEST_INVALID: collector CWD does not match the frozen manifest CWD: manifest=$manifestCwd actual=$([IO.Directory]::GetCurrentDirectory())"
    # Real pre-create capture (kept verbatim, never re-derived post-create).
    $script:OutputPreflight = New-OutputPreflightCapture -OutputDir $manifestOutputDir -OutputFile $outputFile
    Require ([IO.Directory]::Exists($manifestOutputDir)) "OUTPUT_PRECHECK_FAILED: output directory does not exist: $($manifestOutputDir)"
    Require $script:OutputPreflight.chainAllOrdinary ("OUTPUT_PRECHECK_FAILED: output directory chain not fully ordinary: " +
        "reparse=$($script:OutputPreflight.chain.reparseComponents -join ';') nonDir=$($script:OutputPreflight.chain.nonDirectoryComponents -join ';') missing=$($script:OutputPreflight.chain.missingComponents -join ';') leafAttributeError=$($script:OutputPreflight.chain.leafAttributeError)")
    Require ($script:OutputPreflight.volume.isReady -and $script:OutputPreflight.volume.driveFormat -ceq 'NTFS') ("OUTPUT_PRECHECK_FAILED: output volume not ready NTFS: root=$($script:OutputPreflight.volume.pathRoot) ready=$($script:OutputPreflight.volume.isReady) format=$($script:OutputPreflight.volume.driveFormat)")
    Require ($script:OutputPreflight.chain.leafExists -and -not $script:OutputPreflight.chain.leafReparsePoint) "OUTPUT_PRECHECK_FAILED: output directory leaf missing or is a reparse point"

    $script:Stream = Open-ExclusiveCreateNew -Path $outputFile
    # Post-create facts recorded AFTER the successful CreateNew only.
    $script:OutputPostCreate = New-OutputPostCreateFacts -OutputFile $outputFile
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    $script:Writer = [IO.StreamWriter]::new($script:Stream, $utf8NoBom)
    $script:Writer.NewLine = "`n"

    $startedUtc = [DateTime]::UtcNow.ToString('o')
    $metaLine = New-MetaLineObject -RunId $RunId -StartedUtc $startedUtc -Constants $script:Constants `
        -Manifest $manifest -ManifestPath $FreezeManifestPath -ManifestSha256 $FreezeManifestSha256 `
        -NotRunTable $script:NotRunTable `
        -ForbiddenHistorySegments $script:ForbiddenHistorySegments
    Write-StreamLine -Json (ConvertTo-Json -InputObject $metaLine -Depth 96 -Compress)

    # ---- 4) history isolation re-recorded as an observation (the SAME pure
    #         check already fail-closed the run pre-create; this keeps the
    #         full {path, underHistory} manifest inside the evidence stream) ----
    $expIdentityName = (Get-ManifestField -Object $manifestIdentity -Name 'name').value
    $expIdentitySid = (Get-ManifestField -Object $manifestIdentity -Name 'sid').value
    $expPsVersion = (Get-ManifestField -Object $manifestRuntime -Name 'psVersion').value
    $expPsEdition = (Get-ManifestField -Object $manifestRuntime -Name 'psEdition').value
    $expLanguageMode = (Get-ManifestField -Object $manifestRuntime -Name 'languageMode').value
    $expGitVersion = (Get-ManifestField -Object $manifestRuntime -Name 'gitVersion').value
    $fixedPaths = $prePaths + @($script:PwshExe, $script:GitExe, $script:WhoamiExe, (Join-Path $PSHOME 'pwsh.exe'))
    $isolation = Invoke-InProcessGetter -Id 'history-isolation-fixed-paths' `
        -Method 'Test-PathContainsHistorySegment over every fixed path (pure string-segment check; full {path, underHistory} manifest in input and output; no filesystem access)' `
        -GetterInput ([ordered]@{ forbiddenSegments = [string[]]$script:ForbiddenHistorySegments; paths = [string[]]$fixedPaths }) `
        -Body {
            param($src)
            Assert-TaskPathIsolation -Paths $src.paths -ForbiddenSegments $src.forbiddenSegments
        }
    Require (-not $isolation.observation.output.value.anyUnderHistory) ('HISTORY_SCOPE_VIOLATION: a fixed path references a historical evidence family; refusing to continue: ' +
        "$($isolation.observation.output.value.underHistoryPaths -join ';')")
    Add-Check -Id 'history-isolation-fixed-paths' -Category 'history-isolation' `
        -Expected "no fixed path (output/worktree/tools/pins/mutable/cwd) contains a frozen historical task-family segment ($($script:ForbiddenHistorySegments -join ', ')); historical inputs/conclusions are never accessed" `
        -ObservedPointer "$($isolation.pointer)/output/value" `
        -ObservedSummary "pathCount=$($isolation.observation.output.value.pathCount) anyUnderHistory=$($isolation.observation.output.value.anyUnderHistory)" `
        -Result 'PASS' `
        -Note 'full {path, underHistory} manifest retained in this observation''s input and output; string-segment check only'

    # ---- 4) output path chain/volume evidence (pre-create + post-create verbatim) ----
    $outputSafety = Invoke-InProcessGetter -Id 'output-path-chain-volume' `
        -Method 'New-OutputPreflightCapture BEFORE CreateNew + New-OutputPostCreateFacts AFTER CreateNew (real ordering; pre-create values never re-derived post-create)' `
        -GetterInput ([ordered]@{ outputDir = $manifestOutputDir; outputFile = $outputFile }) `
        -Body {
            param($src)
            [ordered]@{
                preCreate = $script:OutputPreflight
                postCreate = $script:OutputPostCreate
            }
        }
    $outputSafetyOk = ($script:OutputPreflight.targetAbsent -and
                       $script:OutputPreflight.chainAllOrdinary -and
                       $script:OutputPreflight.volume.isReady -and
                       $script:OutputPreflight.volume.driveFormat -ceq 'NTFS' -and
                       $script:OutputPostCreate.targetExists -and
                       $script:OutputPostCreate.exclusiveStreamOpen -and
                       $script:OutputPostCreate.capturedAfterCreateNew)
    Add-Check -Id 'output-path-chain-volume' -Category 'pre-write' `
        -Expected 'PRE-CREATE (captured before CreateNew): target absent, output chain fully ordinary, volume ready NTFS; POST-CREATE: target exists via the open exclusive stream; CreateNew refuses reuse of the same RunId' `
        -ObservedPointer "$($outputSafety.pointer)/output/value" `
        -ObservedSummary "preCreate.targetAbsent=$($script:OutputPreflight.targetAbsent) preCreate.chainAllOrdinary=$($script:OutputPreflight.chainAllOrdinary) preCreate.volumeReady=$($script:OutputPreflight.volume.isReady)/$($script:OutputPreflight.volume.driveFormat) postCreate.targetExists=$($script:OutputPostCreate.targetExists) postCreate.streamOpen=$($script:OutputPostCreate.exclusiveStreamOpen)" `
        -Result $(if ($outputSafetyOk) { 'PASS' } else { 'FAIL' }) `
        -Note 'preflight Required the same conditions before the stream opened; both captures are serialized verbatim in this observation'

    # ---- 5) host PowerShell runtime facts (version/edition/language mode; in-process) ----
    $psRuntime = Invoke-InProcessGetter -Id 'host-pwsh-runtime' `
        -Method 'PSVersionTable + SessionState.LanguageMode + PSHOME (in-process; read-only)' `
        -GetterInput ([ordered]@{ expectedPsVersion = $expPsVersion; expectedPsEdition = $expPsEdition; expectedLanguageMode = $expLanguageMode }) `
        -Body {
            param($src)
            [ordered]@{
                psVersion = $PSVersionTable.PSVersion.ToString()
                psEdition = $PSVersionTable.PSEdition
                languageMode = $ExecutionContext.SessionState.LanguageMode.ToString()
                psHome = $PSHOME
                os = $PSVersionTable.OS
                platform = $PSVersionTable.Platform
            }
        }
    $pv = $psRuntime.observation.output.value
    $psOk = ($pv.psVersion -ceq $expPsVersion -and
             $pv.psEdition -ceq $expPsEdition -and
             $pv.languageMode -ceq $expLanguageMode)
    Add-Check -Id 'host-pwsh-runtime-matches-freeze' -Category 'version' `
        -Expected "pwsh $expPsVersion / $expPsEdition / $expLanguageMode (frozen via the external freeze manifest)" `
        -ObservedPointer "$($psRuntime.pointer)/output/value" `
        -ObservedSummary "version=$($pv.psVersion) edition=$($pv.psEdition) languageMode=$($pv.languageMode) psHome=$($pv.psHome)" `
        -Result $(if ($psOk) { 'PASS' } else { 'FAIL' }) `
        -Note 'host facts recorded verbatim; any drift fails closed'

    # ---- 6) identity (whoami child + WindowsIdentity SID; read-only) ----
    $whoami = Invoke-HelperProcess -Id 'identity-whoami' `
        -Executable $script:WhoamiExe -Cwd $manifestWorktree -Argv @() -AllowedExit @(0)
    $whoamiText = $whoami.observation.output.value.stdout.text
    $identity = Invoke-InProcessGetter -Id 'identity-sid' `
        -Method 'Security.Principal.WindowsIdentity.GetCurrent() (in-process; read-only SID/name facts)' `
        -GetterInput ([ordered]@{ expectedSid = $expIdentitySid }) `
        -Body {
            param($src)
            $wid = [Security.Principal.WindowsIdentity]::GetCurrent()
            [ordered]@{
                sid = $wid.User.Value
                name = $wid.Name
                isSystem = $wid.IsSystem
                authenticationType = $wid.AuthenticationType
            }
        }
    $sidOk = ($identity.observation.output.value.sid -ieq $expIdentitySid)
    $nameOk = ($null -ne $whoamiText -and $whoamiText.Trim() -ieq $expIdentityName)
    Add-Check -Id 'identity-matches-freeze' -Category 'identity' `
        -Expected "whoami output '$expIdentityName' (case-insensitive) and SID $expIdentitySid (frozen via the external freeze manifest)" `
        -ObservedPointer "$($identity.pointer)/output/value" `
        -ObservedSummary "whoamiRaw='$whoamiText' sid=$($identity.observation.output.value.sid) nameOk=$nameOk sidOk=$sidOk" `
        -Result $(if ($nameOk -and $sidOk) { 'PASS' } else { 'FAIL' }) `
        -Note 'whoami raw stdout retained byte-faithfully in its own observation'

    # ---- 7) Git/source pins (compare against the external freeze manifest, never force) ----
    $revHead = Invoke-GitHelper -Id 'git-rev-parse-head' -Cwd $manifestWorktree -GitArgv @('rev-parse', 'HEAD')
    $headSha = $revHead.observation.output.value.stdout.text.Trim()
    $headOk = ($headSha -ceq $manifestDeliveryHead)
    Add-Check -Id 'git-head-matches-freeze' -Category 'git-pin' `
        -Expected "worktree HEAD == frozen delivery commit $manifestDeliveryHead (from the external freeze manifest)" `
        -ObservedPointer "$($revHead.pointer)/output/value/stdout" `
        -ObservedSummary "head=$headSha expected=$manifestDeliveryHead match=$headOk" `
        -Result $(if ($headOk) { 'PASS' } else { 'FAIL' }) `
        -Note 'raw rev-parse stdout retained; drift fails closed'

    $revTree = Invoke-GitHelper -Id 'git-rev-parse-tree' -Cwd $manifestWorktree -GitArgv @('rev-parse', 'HEAD^{tree}')
    $revBranch = Invoke-GitHelper -Id 'git-symbolic-ref' -Cwd $manifestWorktree -GitArgv @('symbolic-ref', '--quiet', 'HEAD')
    $branchRef = $revBranch.observation.output.value.stdout.text.Trim()
    $branchOk = Test-BranchRefMatchesManifest -BranchRef $branchRef -ManifestBranch $manifestBranch
    Add-Check -Id 'git-branch-matches-freeze' -Category 'git-pin' `
        -Expected "symbolic-ref HEAD == refs/heads/$manifestBranch" `
        -ObservedPointer "$($revBranch.pointer)/output/value/stdout" `
        -ObservedSummary "branch=$branchRef expected=refs/heads/$manifestBranch match=$branchOk" `
        -Result $(if ($branchOk) { 'PASS' } else { 'FAIL' }) `
        -Note 'raw symbolic-ref stdout retained'

    $revToplevel = Invoke-GitHelper -Id 'git-toplevel' -Cwd $manifestWorktree -GitArgv @('rev-parse', '--show-toplevel')
    $toplevel = $revToplevel.observation.output.value.stdout.text.Trim()
    $toplevelOk = Test-GitToplevelMatchesWorktree -Toplevel $toplevel -Worktree $manifestWorktree
    Add-Check -Id 'git-toplevel-matches-worktree' -Category 'git-pin' `
        -Expected "git toplevel == frozen worktree path $manifestWorktree" `
        -ObservedPointer "$($revToplevel.pointer)/output/value/stdout" `
        -ObservedSummary "toplevel=$toplevel expected=$manifestWorktree match=$toplevelOk" `
        -Result $(if ($toplevelOk) { 'PASS' } else { 'FAIL' }) `
        -Note 'the collector must never operate on a different checkout'

    $revCommonDir = Invoke-GitHelper -Id 'git-common-dir' -Cwd $manifestWorktree -GitArgv @('rev-parse', '--git-common-dir')
    $commonDirRaw = $revCommonDir.observation.output.value.stdout.text.Trim()
    $gitVersion = Invoke-GitHelper -Id 'git-version' -Cwd $manifestWorktree -GitArgv @('--version')
    $gitVersionText = $gitVersion.observation.output.value.stdout.text.Trim()
    $gitVersionOk = ($gitVersionText -ceq $expGitVersion)
    Add-Check -Id 'git-version-matches-freeze' -Category 'version' `
        -Expected "git version output == '$expGitVersion'" `
        -ObservedPointer "$($gitVersion.pointer)/output/value/stdout" `
        -ObservedSummary "version='$gitVersionText' match=$gitVersionOk" `
        -Result $(if ($gitVersionOk) { 'PASS' } else { 'FAIL' }) `
        -Note 'raw git --version stdout retained'

    $mergeBase = Invoke-GitHelper -Id 'git-merge-base-ancestor' -Cwd $manifestWorktree `
        -GitArgv @('merge-base', '--is-ancestor', $manifestBaseCommit, 'HEAD') -AllowedExit @(0, 1)
    $ancestorOk = ($mergeBase.observation.exit -eq 0)
    Add-Check -Id 'git-base-commit-is-ancestor' -Category 'git-pin' `
        -Expected "base commit $manifestBaseCommit is an ancestor of delivery HEAD (dispatched baseline lineage)" `
        -ObservedPointer "$($mergeBase.pointer)/exit" `
        -ObservedSummary "mergeBaseExit=$($mergeBase.observation.exit) isAncestor=$ancestorOk" `
        -Result $(if ($ancestorOk) { 'PASS' } else { 'FAIL' }) `
        -Note 'exit 0 = ancestor; exit 1 (allowed for capture) fails the check and blocks the run'

    # ---- 8) worktree status verbatim (recorded; never judged clean/dirty) ----
    $status = Invoke-GitHelper -Id 'git-status-verbatim' -Cwd $manifestWorktree -GitArgv (New-StatusArgv)
    $statusRecordCount = 0
    if ($status.observation.output.value.stdout.bytesCount -gt 0) {
        $statusRecords = Split-NulRecords -Bytes ([Convert]::FromBase64String($status.observation.output.value.stdout.base64))
        $statusRecordCount = @($statusRecords).Count
    }
    $statusSummary = Invoke-InProcessGetter -Id 'git-status-summary' `
        -Method 'Split-NulRecords over the captured status bytes (pure; records retained verbatim)' `
        -GetterInput ([ordered]@{ recordCount = $statusRecordCount }) `
        -Body {
            param($src)
            [ordered]@{
                recordCount = $src.recordCount
                interpretationPolicy = 'verbatim capture only; clean/dirty state is never judged by this collector'
            }
        }
    Add-Check -Id 'git-status-captured' -Category 'git-pin' `
        -Expected 'status --porcelain=v2 -z captured byte-faithfully (exit 0); content recorded verbatim, never judged' `
        -ObservedPointer "$($statusSummary.pointer)/output/value" `
        -ObservedSummary "exit=$($status.observation.exit) bytes=$($status.observation.output.value.stdout.bytesCount) records=$statusRecordCount" `
        -Result 'PASS' `
        -Note 'full raw stdout (base64+sha256) lives in the git-status-verbatim observation'

    # ---- 9) output target ignore state (recorded; target is outside the repo) ----
    $ignoreRecord = Invoke-InProcessGetter -Id 'output-target-ignore-state' `
        -Method 'pure path-prefix classification (no write; git check-ignore applies to repository paths only)' `
        -GetterInput ([ordered]@{ outputFile = $outputFile; worktree = $manifestWorktree }) `
        -Body {
            param($src)
            $out = ($src.outputFile -replace '/', '\')
            $wt = ($src.worktree -replace '/', '\') + '\'
            $inside = $out.StartsWith($wt)
            return [ordered]@{
                insideRepository = $inside
                gitIgnoreApplicable = $inside
                note = 'the frozen output target lives under the workspace agent-output root outside any repository; git ignore semantics do not apply there'
            }
        }
    Add-Check -Id 'output-target-unignored-or-outside-repo' -Category 'pre-write' `
        -Expected 'output target either git-unignored (repository path) or outside any repository (agent-output root); combined with pre-create targetAbsent this keeps CreateNew collision-free' `
        -ObservedPointer "$($ignoreRecord.pointer)/output/value" `
        -ObservedSummary "insideRepository=$($ignoreRecord.observation.output.value.insideRepository) targetAbsent=$($script:OutputPreflight.targetAbsent)" `
        -Result $(if ($script:OutputPreflight.targetAbsent) { 'PASS' } else { 'FAIL' }) `
        -Note 'AC3 requires targets frozen and absent/unignored before live; the collector re-verifies absence itself'

    # ---- 10) CWD freeze check ----
    $cwdRecord = Invoke-InProcessGetter -Id 'collector-cwd' `
        -Method 'GetCurrentDirectory (in-process; read-only)' `
        -GetterInput ([ordered]@{ frozenCwd = $manifestCwd }) `
        -Body {
            param($src)
            [ordered]@{
                cwd = [IO.Directory]::GetCurrentDirectory()
                frozenCwd = $src.frozenCwd
            }
        }
    $cwdOk = ($cwdRecord.observation.output.value.cwd -ieq ($manifestCwd -replace '/', '\'))
    Add-Check -Id 'collector-cwd-matches-freeze' -Category 'freeze' `
        -Expected "collector CWD == frozen CWD $($manifestCwd) (from the external freeze manifest)" `
        -ObservedPointer "$($cwdRecord.pointer)/output/value" `
        -ObservedSummary "cwd=$($cwdRecord.observation.output.value.cwd) match=$cwdOk" `
        -Result $(if ($cwdOk) { 'PASS' } else { 'FAIL' }) `
        -Note 'AC3 requires CWD frozen before live; every helper child uses its own explicit fixed WorkingDirectory'

    # ---- 11) contract pins BEFORE (immutable; drift fails closed) ----
    $contractBefore = @{}
    foreach ($pin in $manifestContractPins) {
        $obs = Get-FilePinObservation -Id "contract-pin-before-$($pin.name)" -Path $pin.path
        $contractBefore[$pin.name] = $obs
        $ok = ($obs.observation.output.value.bytesCount -eq $pin.size) -and ($obs.observation.output.value.sha256 -ceq $pin.sha256)
        Add-Check -Id "contract-pin-before-$($pin.name)" -Category 'frozen-pin' `
            -Expected "$($pin.size) / $($pin.sha256)" `
            -ObservedPointer "$($obs.pointer)/output/value" `
            -ObservedSummary "$($obs.observation.output.value.bytesCount) / $($obs.observation.output.value.sha256)" `
            -Result $(if ($ok) { 'PASS' } else { 'FAIL' }) `
            -Note 'immutable contract pin; drift means a frozen shared input changed and blocks admission'
    }

    # ---- 12) mutable planning/status surfaces (observations ONLY, never pins) ----
    foreach ($mp in $manifestMutablePaths) {
        $leaf = Split-Path -Leaf $mp
        $obs = Get-FilePinObservation -Id "mutable-observation-$leaf" -Path $mp
        Add-Check -Id "mutable-observation-recorded-$leaf" -Category 'mutable-observation' `
            -Expected 'current hash/size recorded as a plain observation; mutable STATUS/Plan/checkpoint are NEVER immutable hash pins and are never judged PASS/FAIL here' `
            -ObservedPointer "$($obs.pointer)/output/value" `
            -ObservedSummary "$($obs.observation.output.value.bytesCount) / $($obs.observation.output.value.sha256)" `
            -Result 'PASS' `
            -Note 'Task evidence rule: mutable planning surfaces are recorded, not pinned'
    }

    # ---- 13) Task deliverable pins BEFORE (frozen by Codex before live) ----
    $deliverableBefore = @{}
    foreach ($pin in $manifestDeliverablePins) {
        $obs = Get-FilePinObservation -Id "deliverable-pin-before-$($pin.name)" -Path $pin.path
        $deliverableBefore[$pin.name] = $obs
        $ok = ($obs.observation.output.value.bytesCount -eq $pin.size) -and ($obs.observation.output.value.sha256 -ceq $pin.sha256)
        Add-Check -Id "deliverable-pin-before-$($pin.name)" -Category 'frozen-pin' `
            -Expected "$($pin.size) / $($pin.sha256)" `
            -ObservedPointer "$($obs.pointer)/output/value" `
            -ObservedSummary "$($obs.observation.output.value.bytesCount) / $($obs.observation.output.value.sha256)" `
            -Result $(if ($ok) { 'PASS' } else { 'FAIL' }) `
            -Note 'Task-deliverable source pin; drift means the reviewed source changed and blocks admission'
    }

    # ---- 14) git index hash BEFORE (index must not be disturbed) ----
    $commonDirNormalized = ($commonDirRaw -replace '/', '\')
    if (-not [IO.Path]::IsPathRooted($commonDirNormalized)) {
        $commonDirNormalized = Join-Path ($manifestWorktree -replace '/', '\') $commonDirNormalized
    }
    $rootIndexPath = Join-Path $commonDirNormalized 'index'
    $rootIndexBefore = Invoke-InProcessGetter -Id 'git-index-hash-before' `
        -Method 'IO.File.ReadAllBytes(worktree .git index) + SHA256 (read-only)' `
        -GetterInput ([ordered]@{ path = $rootIndexPath }) `
        -Body {
            param($src)
            $bytes = [IO.File]::ReadAllBytes($src.path)
            [ordered]@{ bytesCount = $bytes.Length; sha256 = Get-Sha256HexFromBytes -Bytes $bytes }
        }

    # ---- 15) static contract files of the worktree (existence probe only) ----
    foreach ($mp in $manifestMutablePaths) {
        $leaf = Split-Path -Leaf $mp
        $obs = Get-PathProbeObservation -Id "static-contract-probe-$leaf" -Path $mp
        $check = Get-ProbeCheckResult -ProbeValue $obs.observation.output.value
        Add-Check -Id "static-contract-probe-$leaf" -Category 'static-contract' `
            -Expected 'path exists as an ordinary file (probe only; never judged beyond the recorded values)' `
            -ObservedPointer "$($obs.pointer)/output/value" `
            -ObservedSummary "exists=$($obs.observation.output.value.exists) absent=$($obs.observation.output.value.absent) attributeError=$($obs.observation.output.value.attributeError)" `
            -Result $check `
            -Note 'existence/metadata probe of a mutable planning surface; NOT a hash pin'
    }

    # ---- 16) contract pins AFTER (unchanged until close) ----
    foreach ($pin in $manifestContractPins) {
        $obsAfter = Get-FilePinObservation -Id "contract-pin-after-$($pin.name)" -Path $pin.path
        $b = $contractBefore[$pin.name].observation.output.value
        $a = $obsAfter.observation.output.value
        $ok = ($a.bytesCount -eq $b.bytesCount) -and ($a.sha256 -ceq $b.sha256)
        Add-Check -Id "contract-pin-after-$($pin.name)" -Category 'frozen-pin' `
            -Expected "unchanged until close: $($pin.size) / $($pin.sha256)" `
            -ObservedPointer "$($obsAfter.pointer)/output/value" `
            -ObservedSummary "before=$($b.sha256) after=$($a.sha256)" `
            -Result $(if ($ok) { 'PASS' } else { 'FAIL' }) `
            -Note 'before/after recheck; drift means the collection itself disturbed a frozen input'
    }

    # ---- 17) Task deliverable pins AFTER ----
    foreach ($pin in $manifestDeliverablePins) {
        $obsAfter = Get-FilePinObservation -Id "deliverable-pin-after-$($pin.name)" -Path $pin.path
        $b = $deliverableBefore[$pin.name].observation.output.value
        $a = $obsAfter.observation.output.value
        $ok = ($a.bytesCount -eq $b.bytesCount) -and ($a.sha256 -ceq $b.sha256)
        Add-Check -Id "deliverable-pin-after-$($pin.name)" -Category 'frozen-pin' `
            -Expected "unchanged until close: $($pin.size) / $($pin.sha256)" `
            -ObservedPointer "$($obsAfter.pointer)/output/value" `
            -ObservedSummary "before=$($b.sha256) after=$($a.sha256)" `
            -Result $(if ($ok) { 'PASS' } else { 'FAIL' }) `
            -Note 'before/after recheck; drift means the collection itself disturbed a frozen input'
    }

    # ---- 18) git index hash AFTER (final recheck before close) ----
    $rootIndexAfter = Invoke-InProcessGetter -Id 'git-index-hash-after' `
        -Method 'IO.File.ReadAllBytes(worktree .git/index) + SHA256 (final read-only recheck after ALL helper children and source-file reads; last observation before close)' `
        -GetterInput ([ordered]@{ path = $rootIndexPath }) `
        -Body {
            param($src)
            $bytes = [IO.File]::ReadAllBytes($src.path)
            [ordered]@{ bytesCount = $bytes.Length; sha256 = Get-Sha256HexFromBytes -Bytes $bytes }
        }
    $indexUnchanged = ($rootIndexAfter.observation.output.value.sha256 -ceq $rootIndexBefore.observation.output.value.sha256) -and
                      ($rootIndexAfter.observation.output.value.bytesCount -eq $rootIndexBefore.observation.output.value.bytesCount)
    Add-Check -Id 'git-index-after-unchanged' -Category 'index' `
        -Expected 'worktree .git/index identical before/after the whole collection; the AFTER sample is the last observation before the closed line' `
        -ObservedPointer "$($rootIndexAfter.pointer)/output/value" `
        -ObservedSummary "before=$($rootIndexBefore.observation.output.value.sha256) after=$($rootIndexAfter.observation.output.value.sha256) unchanged=$indexUnchanged" `
        -Result $(if ($indexUnchanged) { 'PASS' } else { 'FAIL' }) `
        -Note 'closed JSON carries index before/after comparison; Git HEAD/ref/index must stay untouched by this collector'

    # ---- close ----
    if ($script:BlockedReasons.Count -gt 0) {
        $script:ExitCode = 5
        $script:Disposition = 'BLOCKED_BY_FAILED_CHECKS'
        Write-ClosedLine -State 'FAILED_STOPPED' -Disposition $script:Disposition -ExitCode $script:ExitCode
    } else {
        Write-ClosedLine -State 'COMPLETED' -Disposition $script:Disposition -ExitCode 0
    }
} catch {
    $message = [string]$_.Exception.Message
    $classification = Get-CollectorFailureClassification -Message $message -BlockedReasons $script:BlockedReasons
    $script:ExitCode = $classification.exitCode
    $script:Disposition = $classification.disposition
    $script:BlockedReasons.Add("EXCEPTION: $($_.Exception.GetType().FullName): $message")
    if ($null -ne $script:Writer) {
        try { Write-ClosedLine -State 'FAILED_STOPPED' -Disposition $script:Disposition -ExitCode $script:ExitCode } catch { }
    } else {
        [Console]::Error.WriteLine("disposition=$($script:Disposition) exit=$($script:ExitCode) reason=$message")
    }
} finally {
    if ($null -ne $script:Writer) { try { $script:Writer.Dispose() } catch { } }
    elseif ($null -ne $script:Stream) { try { $script:Stream.Dispose() } catch { } }
}

exit $script:ExitCode
