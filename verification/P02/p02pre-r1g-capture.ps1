$ErrorActionPreference = 'Stop'

$Repo = 'G:\CODEX\New Manga'
$Scratch = 'G:\CODEX\P02-scratch-build-source'
$EvidencePath = 'G:\CODEX\New Manga\verification\P02\p02pre-r1g-evidence-20261011.json'
$GitExe = 'C:\Program Files\Git\mingw64\bin\git.exe'
$WhoAmIExe = 'C:\Windows\System32\whoami.exe'
$ExpectedUser = 'HOME-MY\49745'
$ExpectedSid = 'S-1-5-21-2196946971-914346751-4210154634-1001'
$RepoHead = 'cddff58469b56e181019a8ddfeade80684bc7eb9'
$RepoTree = 'c25d051a4b9a0bd9773b50170e100f575ea19f2b'
$ScratchHead = '7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a'
$ScratchTree = 'ce8056b8ef4d2ebd11bb4754b206adf921a39e41'

if (Test-Path -LiteralPath $EvidencePath) { throw "Evidence target already exists; no capture performed: $EvidencePath" }

$T0 = [DateTime]::UtcNow.ToString('o')
$T0Tick = [Diagnostics.Stopwatch]::GetTimestamp()
$Result = [ordered]@{
    task = 'P02PRE-R1G'
    manifest = 'verification/P02/p02pre-r1g-manifest-20261011.md'
    t0Utc = $T0
    t0StopwatchTicks = $T0Tick
    command = 'pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File verification/P02/p02pre-r1g-capture.ps1'
    cwd = (Get-Location).Path
    phases = [ordered]@{
        identity = 'NOT_REACHED'
        mainRepository = 'NOT_REACHED'
        scratchRepository = 'NOT_REACHED'
        environment = 'NOT_REACHED'
        paths = 'NOT_REACHED'
        wer = 'NOT_REACHED'
        protectedHashes = 'NOT_REACHED'
        aclStability = 'NOT_REACHED'
    }
    stopCategory = $null
    stopDetail = $null
    stopReason = $null
    process = [ordered]@{}
    identity = [ordered]@{}
    repository = [ordered]@{}
    environment = [ordered]@{}
    paths = [ordered]@{}
    wer = [ordered]@{}
    protectedHashes = [ordered]@{}
    classifications = [ordered]@{
        hostIdentity = 'NOT_REACHED'
        private_registry_absence = 'UNPROVABLE'
        profile_api_path_and_store = 'REQUIRES_ACTIVE_TEST'
        lpac_write_and_child_closure = 'REQUIRES_ACTIVE_TEST'
        product_build_and_ac1_ac7 = 'NOT_RUN'
        process_and_path_access_closure = 'UNPROVABLE_NOT_MONITORED_IN_R1G'
        tempCache = 'NOT_REACHED'
        werEffectivePolicy = 'NOT_REACHED'
        repositoryProtectedInventory = 'NOT_REACHED'
    }
    errors = [System.Collections.Generic.List[string]]::new()
}

function Invoke-CapturedProcess([string]$FileName, [string[]]$ArgumentList) {
    $info = New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName = $FileName
    $info.WorkingDirectory = (Get-Location).Path
    foreach ($arg in $ArgumentList) {
        $info.ArgumentList.Add($arg)
    }
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $info
    if (-not $process.Start()) { throw "Process start returned false: $FileName $($ArgumentList -join ' ')" }
    $stdoutBuffer = New-Object System.IO.MemoryStream
    $stderrBuffer = New-Object System.IO.MemoryStream
    $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
    $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderrBuffer)
    $null = $process.WaitForExit()
    $null = $stdoutTask.GetAwaiter().GetResult()
    $null = $stderrTask.GetAwaiter().GetResult()
    $stdoutBytes = $stdoutBuffer.ToArray()
    $stderrBytes = $stderrBuffer.ToArray()
    $encoding = if ($FileName -eq $GitExe) { [Text.UTF8Encoding]::new($false, $false) } else { [Console]::OutputEncoding }
    $captured = [pscustomobject][ordered]@{
        executable = $FileName
        argumentList = @($ArgumentList)
        workingDirectory = (Get-Location).Path
        exitCode = $process.ExitCode
        stdout = $encoding.GetString($stdoutBytes)
        stdoutTextEncoding = $encoding.WebName
        stdoutTextCodePage = $encoding.CodePage
        textDecodeNote = if ($FileName -eq $GitExe) { 'UTF-8 replacement decode for display only; raw bytes are authoritative.' } else { 'Console.OutputEncoding snapshot for display only; raw bytes are authoritative.' }
        stdoutBase64 = [Convert]::ToBase64String($stdoutBytes)
        stdoutSha256 = Get-ByteHash $stdoutBytes
        stderr = $encoding.GetString($stderrBytes)
        stderrBase64 = [Convert]::ToBase64String($stderrBytes)
        stderrSha256 = Get-ByteHash $stderrBytes
        processId = $process.Id
    }
    $null = $stdoutBuffer.Dispose()
    $null = $stderrBuffer.Dispose()
    $null = $process.Dispose()
    return $captured
}

function Invoke-Git([string]$Root, [string[]]$Arguments) {
    $prefix = @(
        '--no-optional-locks',
        '-c', 'core.quotepath=false',
        '-c', 'core.fsmonitor=false',
        '-c', 'core.untrackedCache=false',
        '-C', $Root
    )
    $fullArgs = @($prefix + $Arguments)
    return Invoke-CapturedProcess $GitExe $fullArgs
}

function Get-ByteHash([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($sha.ComputeHash($Bytes)).Replace('-', '') }
    finally { $sha.Dispose() }
}

function Assert-SingleCommandRecord([object]$Record, [string]$Name) {
    if ($null -eq $Record -or $Record -isnot [System.Management.Automation.PSCustomObject] -or $null -eq $Record.PSObject.Properties['exitCode']) {
        throw "Command record must be one named object, not an array or placeholder: $Name"
    }
}

function Test-UnreadUserDataStagingPath([string]$RelativePath) {
    return ($RelativePath.Equals('.tmp.driveupload', [StringComparison]::OrdinalIgnoreCase) -or $RelativePath.StartsWith('.tmp.driveupload/', [StringComparison]::OrdinalIgnoreCase) -or $RelativePath.StartsWith('.tmp.driveupload\', [StringComparison]::OrdinalIgnoreCase))
}

function Test-SafeRepositoryRelativePath([string]$RelativePath) {
    if ([string]::IsNullOrEmpty($RelativePath) -or $RelativePath.StartsWith('/') -or $RelativePath.StartsWith('\')) { return $false }
    foreach ($part in $RelativePath.Replace('\', '/').Split('/')) {
        if ([string]::IsNullOrEmpty($part) -or $part -in @('.', '..') -or $part.Contains(':') -or $part.EndsWith('.') -or $part.EndsWith(' ') -or $part -match '~[0-9]') { return $false }
    }
    return $true
}

function Get-LinkTypeEvidence([object]$Item) {
    $property = $Item.PSObject.Properties['LinkType']
    if ($null -eq $property -or [string]::IsNullOrEmpty([string]$property.Value)) { return 'NOT_AVAILABLE_ON_ENGINE' }
    return [string]$property.Value
}

function Test-ExpectedDetachedBranchResult([object]$CommandRecord) {
    return ($CommandRecord.exitCode -eq 128 -and $CommandRecord.stdoutBase64 -eq '' -and $CommandRecord.stderrBase64 -ceq 'ZmF0YWw6IHJlZiBIRUFEIGlzIG5vdCBhIHN5bWJvbGljIHJlZgo=')
}

function Get-InventoryAction([object]$GitMode, [bool]$IsReparsePoint, [bool]$IsLeaf, [bool]$IsContainer) {
    if ($IsLeaf -and $GitMode -eq '120000' -and $IsReparsePoint) { return 'SKIP_TRACKED_SYMLINK' }
    if ($IsReparsePoint -or ($IsLeaf -and ($GitMode -eq '120000' -or $IsContainer))) { return 'STOP' }
    if ($IsLeaf -and $null -ne $GitMode -and $GitMode -notin @('100644', '100755')) { return 'STOP' }
    return 'HASH_REGULAR_FILE'
}

function Assert-InventoryPolicySelfCheck {
    if ((Get-InventoryAction '120000' $true $true $true) -ne 'SKIP_TRACKED_SYMLINK') { throw 'Inventory policy self-check failed: tracked leaf symlink must be metadata-only.' }
    if ((Get-InventoryAction '120000' $false $false $true) -ne 'HASH_REGULAR_FILE') { throw 'Inventory policy self-check failed: a parent directory must be traversable for a tracked symlink candidate.' }
    if ((Get-InventoryAction '100644' $false $false $true) -ne 'HASH_REGULAR_FILE') { throw 'Inventory policy self-check failed: ordinary parent directories must be traversable.' }
    if ((Get-InventoryAction '100644' $false $true $true) -ne 'STOP') { throw 'Inventory policy self-check failed: a directory leaf must stop.' }
    if ((Get-InventoryAction '100644' $true $true $false) -ne 'STOP') { throw 'Inventory policy self-check failed: non-symlink reparse leaf must stop.' }
    if ((Get-InventoryAction $null $true $true $false) -ne 'STOP') { throw 'Inventory policy self-check failed: untracked reparse leaf must stop.' }
    if ((Get-InventoryAction $null $false $true $false) -ne 'HASH_REGULAR_FILE') { throw 'Inventory policy self-check failed: untracked regular file must hash.' }
    if ((Get-InventoryAction '120000' $false $true $false) -ne 'STOP') { throw 'Inventory policy self-check failed: mode/reparse mismatch must stop.' }
    if ((Get-InventoryAction '160000' $false $true $false) -ne 'STOP') { throw 'Inventory policy self-check failed: submodule mode must stop.' }
    if ((Get-InventoryAction '100644' $false $true $false) -ne 'HASH_REGULAR_FILE') { throw 'Inventory policy self-check failed: regular file must hash.' }
    if (-not (Test-SafeRepositoryRelativePath '.tmp.driveupload/item')) { throw 'Inventory policy self-check failed: canonical staging path must be accepted.' }
    foreach ($unsafePath in @('.tmp.driveupload./x', '.tmp.driveupload /x', './.tmp.driveupload/x', '.tmp.driveupload/x:stream', '../.tmp.driveupload/x', '/.tmp.driveupload/x', '.tmp.driveupload//x')) {
        if (Test-SafeRepositoryRelativePath $unsafePath) { throw "Inventory policy self-check failed: unsafe repository path must stop: $unsafePath" }
    }
    if (Test-SafeRepositoryRelativePath 'TMPDRI~1/183728') { throw 'Inventory policy self-check failed: a DOS 8.3 alias path must stop before filesystem access.' }
    if ((Get-LinkTypeEvidence ([pscustomobject]@{ LinkType = 'SymbolicLink' })) -ne 'SymbolicLink') { throw 'Inventory policy self-check failed: available LinkType metadata must be preserved.' }
    if ((Get-LinkTypeEvidence ([pscustomobject]@{})) -ne 'NOT_AVAILABLE_ON_ENGINE') { throw 'Inventory policy self-check failed: missing LinkType metadata must be explicit.' }
    if ((Get-LinkTypeEvidence ([pscustomobject]@{ LinkType = '' })) -ne 'NOT_AVAILABLE_ON_ENGINE') { throw 'Inventory policy self-check failed: empty LinkType metadata must be explicit.' }
    if (-not (Test-UnreadUserDataStagingPath '.tmp.driveupload/183728')) { throw 'Inventory policy self-check failed: upload-staging content must be excluded before filesystem access.' }
    if (-not (Test-UnreadUserDataStagingPath '.TMP.DRIVEUPLOAD/nested/item')) { throw 'Inventory policy self-check failed: staging path classification must match Windows case-insensitively.' }
    if (Test-UnreadUserDataStagingPath 'verification/P02/evidence.json') { throw 'Inventory policy self-check failed: ordinary project evidence must remain in inventory.' }
    $detachedSample = [pscustomobject]@{ exitCode = 128; stdoutBase64 = ''; stderrBase64 = 'ZmF0YWw6IHJlZiBIRUFEIGlzIG5vdCBhIHN5bWJvbGljIHJlZgo=' }
    if (-not (Test-ExpectedDetachedBranchResult $detachedSample)) { throw 'Inventory policy self-check failed: exact detached symbolic-ref result must be accepted.' }
    $unexpectedDetachedSample = [pscustomobject]@{ exitCode = 128; stdoutBase64 = ''; stderrBase64 = 'ZmF0YWw6IHJlZiBIRUFEIGVycm9yCg==' }
    if (Test-ExpectedDetachedBranchResult $unexpectedDetachedSample) { throw 'Inventory policy self-check failed: unexpected symbolic-ref errors must stop.' }
}

function Assert-CommandSerializationSelfCheck {
    $sample = [pscustomobject]@{ name = 'shape-check'; exitCode = 0 }
    $json = ConvertTo-Json -InputObject ([pscustomobject]@{ command = $sample }) -Compress -Depth 4
    $parsed = ConvertFrom-Json $json
    if ($parsed.command -is [array] -or $parsed.command.name -ne 'shape-check' -or $parsed.command.exitCode -ne 0) { throw 'Command serialization self-check failed: one command must serialize as one named object.' }
}

function Get-GitNulPaths([byte[]]$Bytes) {
    if ($Bytes.Length -eq 0) { return [pscustomobject]@{ paths = [string[]]@(); nulTerminatorCount = 0; emptySplitArtifactCount = 0 } }
    $decoded = [Text.UTF8Encoding]::new($false, $true).GetString($Bytes)
    $segments = $decoded.Split([char]0)
    $emptyCount = @($segments | Where-Object { $_.Length -eq 0 }).Count
    $nulCount = 0
    foreach ($byte in $Bytes) { if ($byte -eq 0) { $nulCount++ } }
    $paths = @($segments | Where-Object { $_.Length -gt 0 })
    if ($emptyCount -ne 1 -or $segments[-1].Length -ne 0 -or $nulCount -ne $paths.Count) {
        throw "Malformed Git -z path list: candidates=$($paths.Count); NUL=$nulCount; emptySplitSegments=$emptyCount"
    }
    return [pscustomobject]@{ paths = [string[]]$paths; nulTerminatorCount = $nulCount; emptySplitArtifactCount = $emptyCount }
}

function Get-GitIndexModes([byte[]]$Bytes) {
    $modes = [System.Collections.Generic.Dictionary[string,string]]::new([StringComparer]::OrdinalIgnoreCase)
    if ($Bytes.Length -eq 0) { return [pscustomobject]@{ modes = $modes; entryCount = 0; nulTerminatorCount = 0 } }
    $decoded = [Text.UTF8Encoding]::new($false, $true).GetString($Bytes)
    $segments = $decoded.Split([char]0)
    $nulCount = 0
    foreach ($byte in $Bytes) { if ($byte -eq 0) { $nulCount++ } }
    $emptyCount = @($segments | Where-Object { $_.Length -eq 0 }).Count
    if ($emptyCount -ne 1 -or $segments[-1].Length -ne 0 -or $nulCount -ne ($segments.Count - 1)) { throw 'Malformed Git index --stage -z output.' }
    foreach ($segment in $segments) {
        if ($segment.Length -eq 0) { continue }
        $tab = $segment.IndexOf([char]9)
        if ($tab -lt 0) { throw 'Git index --stage entry has no path delimiter.' }
        $metadata = $segment.Substring(0, $tab).Split(' ')
        $path = $segment.Substring($tab + 1)
        if ($metadata.Count -ne 3 -or $metadata[0] -notmatch '^(100644|100755|120000|160000)$' -or $metadata[1] -notmatch '^[0-9a-f]{40,64}$' -or $metadata[2] -notmatch '^[0-3]$' -or [string]::IsNullOrEmpty($path)) { throw 'Git index --stage entry is malformed.' }
        if ($modes.ContainsKey($path)) { throw "Duplicate staged path is unsupported: $path" }
        $modes.Add($path, $metadata[0])
    }
    return [pscustomobject]@{ modes = $modes; entryCount = $modes.Count; nulTerminatorCount = $nulCount }
}

function Assert-InventoryParserSelfCheck {
    $pathBytes = [Text.UTF8Encoding]::new($false).GetBytes("alpha`0beta`0")
    $parsedPaths = Get-GitNulPaths $pathBytes
    if ($parsedPaths.paths.Count -ne 2 -or $parsedPaths.nulTerminatorCount -ne 2 -or $parsedPaths.emptySplitArtifactCount -ne 1) { throw 'Git path parser self-check failed: terminal NUL artifact was counted as a candidate.' }
    $modeText = '120000 ' + ('a' * 40) + " 0`tsymbolic-link`0"
    $parsedModes = Get-GitIndexModes ([Text.UTF8Encoding]::new($false).GetBytes($modeText))
    if ($parsedModes.entryCount -ne 1 -or $parsedModes.nulTerminatorCount -ne 1 -or $parsedModes.modes['symbolic-link'] -ne '120000') { throw 'Git index mode parser self-check failed.' }
    $caseCollisionRejected = $false
    try { $null = Get-GitIndexModes ([Text.UTF8Encoding]::new($false).GetBytes(('100644 ' + ('a' * 40) + " 0`ta`0" + '100644 ' + ('b' * 40) + " 0`tA`0"))) }
    catch { $caseCollisionRejected = $true }
    if (-not $caseCollisionRejected) { throw 'Git index mode parser self-check failed: case-only path collisions must be rejected on Windows.' }
    $invalidUtf8 = [byte[]](255, 0)
    $pathUtf8Rejected = $false
    try { $null = Get-GitNulPaths $invalidUtf8 } catch { $pathUtf8Rejected = $true }
    if (-not $pathUtf8Rejected) { throw 'Git path parser self-check failed: invalid UTF-8 must be rejected.' }
    $indexUtf8Rejected = $false
    try { $null = Get-GitIndexModes $invalidUtf8 } catch { $indexUtf8Rejected = $true }
    if (-not $indexUtf8Rejected) { throw 'Git index mode parser self-check failed: invalid UTF-8 must be rejected.' }
}

function Get-PathChain([string]$Path) {
    $components = [System.Collections.Generic.List[object]]::new()
    $full = [IO.Path]::GetFullPath($Path)
    $root = [IO.Path]::GetPathRoot($full)
    $current = $root
    try { $rootItem = Get-Item -LiteralPath $root -Force -ErrorAction Stop }
    catch { return [ordered]@{ state = 'QUERY_ERROR'; queriedPath = $root; errorType = $_.Exception.GetType().FullName; error = $_.Exception.Message; components = $components } }
    $rootComponent = [ordered]@{ path = $root; fullName = $rootItem.FullName; attributes = [string]$rootItem.Attributes; reparsePoint = [bool]($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) }
    $components.Add($rootComponent)
    if ($rootComponent.reparsePoint) { return [ordered]@{ state = 'REPARSE_POINT'; queriedPath = $root; components = $components } }
    foreach ($part in ($full.Substring($root.Length) -split '[\\/]')) {
        if ([string]::IsNullOrEmpty($part)) { continue }
        $current = Join-Path $current $part
        try { $item = Get-Item -LiteralPath $current -Force -ErrorAction Stop }
        catch {
            if ($_.Exception -is [Management.Automation.ItemNotFoundException] -or $_.FullyQualifiedErrorId -match 'PathNotFound|FileNotFound|ObjectNotFound') {
                return [ordered]@{ state = 'ABSENT'; queriedPath = $current; components = $components }
            }
            return [ordered]@{ state = 'QUERY_ERROR'; queriedPath = $current; errorType = $_.Exception.GetType().FullName; error = $_.Exception.Message; components = $components }
        }
        $component = [ordered]@{ path = $current; fullName = $item.FullName; attributes = [string]$item.Attributes; reparsePoint = [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint) }
        $components.Add($component)
        if ($component.reparsePoint) { return [ordered]@{ state = 'REPARSE_POINT'; queriedPath = $current; components = $components } }
    }
    return [ordered]@{ state = 'PRESENT'; queriedPath = $full; components = $components }
}

function Get-FileRecord([string]$Path) {
    $chain = Get-PathChain $Path
    if ($chain.state -ne 'PRESENT') { return [ordered]@{ path = $Path; state = $chain.state; pathChain = $chain.components; error = $chain.error } }
    try { $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop }
    catch { return [ordered]@{ path = $Path; state = 'QUERY_ERROR'; errorType = $_.Exception.GetType().FullName; error = $_.Exception.Message; pathChain = $chain.components } }
    if ($item.PSIsContainer) { return [ordered]@{ path = $Path; state = 'NOT_FILE'; attributes = [string]$item.Attributes } }
    try { $hash = Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop }
    catch { return [ordered]@{ path = $Path; state = 'QUERY_ERROR'; errorType = $_.Exception.GetType().FullName; error = $_.Exception.Message; pathChain = $chain.components } }
    return [ordered]@{
        path = $Path
        state = 'PRESENT'
        pathChain = $chain.components
        length = $item.Length
        lastWriteTimeUtc = $item.LastWriteTimeUtc.ToString('o')
        attributes = [string]$item.Attributes
        sha256 = $hash.Hash
    }
}

function Get-ExactDirectoryRecord([string]$Path, [bool]$CountChildren) {
    $chain = Get-PathChain $Path
    if ($chain.state -ne 'PRESENT') { return [ordered]@{ path = $Path; state = $chain.state; pathChain = $chain.components; error = $chain.error } }
    try { $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop }
    catch { return [ordered]@{ path = $Path; state = 'QUERY_ERROR'; pathChain = $chain.components; errorOperation = 'Get-Item'; errorType = $_.Exception.GetType().FullName; error = $_.Exception.Message } }
    if (-not $item.PSIsContainer) { return [ordered]@{ path = $Path; state = 'NOT_DIRECTORY'; pathChain = $chain.components; attributes = [string]$item.Attributes } }
    $record = [ordered]@{
        path = $Path
        state = 'PRESENT'
        pathChain = $chain.components
        fullName = $item.FullName
        attributes = [string]$item.Attributes
        creationTimeUtc = $item.CreationTimeUtc.ToString('o')
        lastWriteTimeUtc = $item.LastWriteTimeUtc.ToString('o')
        reparsePoint = $false
    }
    if ($CountChildren) {
        try { $record.directEntryCount = (Get-ChildItem -LiteralPath $Path -Force -ErrorAction Stop | Measure-Object).Count }
        catch { $record.state = 'QUERY_ERROR'; $record.errorOperation = 'Get-ChildItem'; $record.errorType = $_.Exception.GetType().FullName; $record.error = $_.Exception.Message; return $record }
    }
    try { $acl = Get-Acl -LiteralPath $Path -ErrorAction Stop }
    catch { $record.state = 'ACL_QUERY_ERROR'; $record.errorOperation = 'Get-Acl'; $record.errorType = $_.Exception.GetType().FullName; $record.error = $_.Exception.Message; return $record }
    $owner = if ($null -ne $acl) { [string]$acl.Owner } else { '' }
    $sddl = if ($null -ne $acl) { [string]$acl.Sddl } else { '' }
    $record.owner = $owner
    $record.securityDescriptorSddl = $sddl
    if ([string]::IsNullOrWhiteSpace($owner) -or [string]::IsNullOrWhiteSpace($sddl)) { $record.state = 'ACL_UNVERIFIABLE' }
    return $record
}

function Set-RepositoryStop([System.Collections.IDictionary]$Record, [string]$State, [string]$Operation, [string]$Message, [object]$BlockingPath = $null) {
    $Record.state = $State
    $Record.errorOperation = $Operation
    $Record.error = $Message
    if ($null -ne $BlockingPath) { $Record.firstBlockingPath = $BlockingPath }
    $Record.omittedCount = if ($Record.candidateCountKnown) { [Math]::Max(0, $Record.candidateCount - $Record.processedCount) } else { $null }
}

function Get-RepositoryRecord([string]$Name, [string]$Root, [string]$ExpectedHead, [string]$ExpectedTree, [string]$ExpectedBranch, [string]$ExpectedCommonDir) {
    $record = [ordered]@{ name = $Name; root = $Root; commands = [ordered]@{}; fileInventory = [System.Collections.Generic.List[object]]::new(); linkInventory = [System.Collections.Generic.List[object]]::new(); candidateCount = 0; candidateCountKnown = $false; processedCount = 0; regularFileHashCount = 0; skippedSymlinkCount = 0; unreadUserDataCount = 0; firstUnreadUserDataPath = $null; omittedCount = $null; firstBlockingPath = $null; errorOperation = $null; error = $null; gitMetadata = [System.Collections.Generic.List[object]]::new(); state = 'STARTED' }
    $record.rootPathChain = Get-PathChain $Root
    $record.gitDirPathChain = Get-PathChain (Join-Path $Root '.git')
    if ($record.rootPathChain.state -ne 'PRESENT' -or $record.gitDirPathChain.state -ne 'PRESENT') {
        $blockingPath = if ($record.rootPathChain.state -ne 'PRESENT') { $Root } else { Join-Path $Root '.git' }
        Set-RepositoryStop $record 'REPOSITORY_PATH_CHAIN_INVALID' 'Get-PathChain' "root=$($record.rootPathChain.state); gitDir=$($record.gitDirPathChain.state)" $blockingPath
        return $record
    }
    try {
        $rootItem = Get-Item -LiteralPath $Root -Force -ErrorAction Stop
        $gitDirItem = Get-Item -LiteralPath (Join-Path $Root '.git') -Force -ErrorAction Stop
    }
    catch {
        Set-RepositoryStop $record 'REPOSITORY_ROOT_OR_GITDIR_QUERY_FAILED' 'Get-Item' ($_.Exception.GetType().FullName + ': ' + $_.Exception.Message) $Root
        return $record
    }
    if (-not $rootItem.PSIsContainer -or ($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -or -not $gitDirItem.PSIsContainer -or ($gitDirItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        $blockingPath = if (-not $rootItem.PSIsContainer -or ($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) { $Root } else { Join-Path $Root '.git' }
        Set-RepositoryStop $record 'REPOSITORY_ROOT_OR_GITDIR_INVALID' 'Get-Item validation' 'Repository root and .git must be ordinary directories without ReparsePoint.' $blockingPath
        return $record
    }
    $record.gitMetadataBefore = Get-FileRecord (Join-Path $Root '.git\index')
    if ($record.gitMetadataBefore.state -ne 'PRESENT') { Set-RepositoryStop $record 'GIT_INDEX_PREHASH_INVALID' 'Get-FileRecord(.git/index)' ([string]$record.gitMetadataBefore.error) (Join-Path $Root '.git\index'); return $record }
    $record.commands.revParse = Invoke-Git $Root @('rev-parse', '--show-toplevel', '--git-common-dir', 'HEAD', 'HEAD^{tree}')
    Assert-SingleCommandRecord $record.commands.revParse 'git rev-parse'
    $record.commands.branch = Invoke-Git $Root @('symbolic-ref', '--short', 'HEAD')
    Assert-SingleCommandRecord $record.commands.branch 'git symbolic-ref'
    $detachedBranchResponse = ($ExpectedBranch -eq 'DETACHED' -and (Test-ExpectedDetachedBranchResult $record.commands.branch))
    $branchQueryFailed = ($record.commands.branch.exitCode -ne 0 -and -not $detachedBranchResponse)
    if ($record.commands.revParse.exitCode -ne 0 -or $branchQueryFailed) {
        Set-RepositoryStop $record 'GIT_BASELINE_QUERY_FAILED' 'git rev-parse/symbolic-ref' "rev-parse=$($record.commands.revParse.exitCode); symbolic-ref=$($record.commands.branch.exitCode)"
        return $record
    }
    $refs = ([string]$record.commands.revParse.stdout).Trim() -split '\r?\n'
    $record.gitTopLevel = if ($refs.Count -ge 1) { [IO.Path]::GetFullPath($refs[0]) } else { $null }
    $record.gitCommonDir = if ($refs.Count -ge 2) { [IO.Path]::GetFullPath($(if ([IO.Path]::IsPathRooted($refs[1])) { $refs[1] } else { Join-Path $Root $refs[1] })) } else { $null }
    $record.head = if ($refs.Count -ge 3) { $refs[2] } else { $null }
    $record.tree = if ($refs.Count -ge 4) { $refs[3] } else { $null }
    $record.branch = if ($record.commands.branch.exitCode -eq 0) { ([string]$record.commands.branch.stdout).Trim() } elseif ($detachedBranchResponse) { 'DETACHED' } else { 'QUERY_ERROR' }
    $record.targetMatches = ($record.gitTopLevel -and $record.gitCommonDir -and $record.gitTopLevel.TrimEnd('\') -eq [IO.Path]::GetFullPath($Root).TrimEnd('\') -and $record.gitCommonDir.TrimEnd('\') -eq [IO.Path]::GetFullPath($ExpectedCommonDir).TrimEnd('\') -and $record.head -eq $ExpectedHead -and $record.tree -eq $ExpectedTree -and $record.branch -eq $ExpectedBranch)
    if (-not $record.targetMatches) { Set-RepositoryStop $record 'REPOSITORY_TARGET_MISMATCH' 'Git baseline comparison' "actual=$($record.gitTopLevel)|$($record.gitCommonDir)|$($record.head)|$($record.tree)|$($record.branch); expected=$([IO.Path]::GetFullPath($Root))|$([IO.Path]::GetFullPath($ExpectedCommonDir))|$ExpectedHead|$ExpectedTree|$ExpectedBranch" $Root; return $record }
    $record.commands.status = Invoke-Git $Root @('status', '--porcelain=v1', '-z', '--untracked-files=all', '--no-renames', '--ignore-submodules=none', '--', '.', ':(exclude).tmp.driveupload')
    Assert-SingleCommandRecord $record.commands.status 'git status'
    $statusBytes = [Convert]::FromBase64String($record.commands.status.stdoutBase64)
    $nulSegments = 0
    foreach ($byte in $statusBytes) { if ($byte -eq 0) { $nulSegments++ } }
    $record.status = [ordered]@{
        exitCode = $record.commands.status.exitCode
        stderr = $record.commands.status.stderr
        rawByteCount = $statusBytes.Length
        nulSegmentCountApprox = $nulSegments
        countDefinition = 'NUL terminator count; --no-renames means one terminator per porcelain record for this capture.'
        sha256 = Get-ByteHash $statusBytes
        base64 = [Convert]::ToBase64String($statusBytes)
    }
    $record.commands.files = Invoke-Git $Root @('ls-files', '--cached', '--others', '--exclude-standard', '-z')
    Assert-SingleCommandRecord $record.commands.files 'git ls-files inventory'
    $record.commands.indexStages = Invoke-Git $Root @('ls-files', '--stage', '-z')
    Assert-SingleCommandRecord $record.commands.indexStages 'git ls-files --stage'
    if ($record.commands.files.exitCode -ne 0 -or $record.commands.status.exitCode -ne 0 -or $record.commands.indexStages.exitCode -ne 0) {
        $failedCommands = [System.Collections.Generic.List[string]]::new()
        foreach ($commandName in @('status', 'files', 'indexStages')) { if ($record.commands[$commandName].exitCode -ne 0) { $failedCommands.Add($commandName + '=' + $record.commands[$commandName].exitCode) } }
        Set-RepositoryStop $record 'GIT_STATUS_OR_INVENTORY_FAILED' 'git status/ls-files' ($failedCommands -join '; ')
        return $record
    }
    $fileBytes = [Convert]::FromBase64String($record.commands.files.stdoutBase64)
    try { $parsedPaths = Get-GitNulPaths $fileBytes }
    catch { Set-RepositoryStop $record 'GIT_FILE_INVENTORY_PARSE_FAILED' 'git ls-files inventory strict UTF-8/NUL parse' ($_.Exception.GetType().FullName + ': ' + $_.Exception.Message); return $record }
    $record.paths = $parsedPaths.paths
    $record.inventoryNulTerminatorCount = $parsedPaths.nulTerminatorCount
    $record.emptySplitArtifactCount = $parsedPaths.emptySplitArtifactCount
    $record.candidateCount = $record.paths.Count
    $record.candidateCountKnown = $true
    $record.omittedCount = $record.candidateCount
    $stageBytes = [Convert]::FromBase64String($record.commands.indexStages.stdoutBase64)
    try { $parsedModes = Get-GitIndexModes $stageBytes }
    catch { Set-RepositoryStop $record 'GIT_INDEX_STAGE_PARSE_FAILED' 'git ls-files --stage strict UTF-8/NUL parse' ($_.Exception.GetType().FullName + ': ' + $_.Exception.Message); return $record }
    $record.indexStageEntryCount = $parsedModes.entryCount
    $record.indexStageNulTerminatorCount = $parsedModes.nulTerminatorCount
    $indexModes = $parsedModes.modes
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
    $currentRelativePath = $null
    $currentOperation = 'Path validation'
    try {
        foreach ($relative in $record.paths) {
            $currentRelativePath = $relative
            $currentOperation = 'Path normalization'
            if (-not (Test-SafeRepositoryRelativePath $relative)) { throw "Unsafe Git-relative path form: $relative" }
            $normalizedRelative = $relative.Replace('\', '/')
            $full = [IO.Path]::GetFullPath((Join-Path $Root ($normalizedRelative.Replace('/', '\'))))
            if (-not $full.StartsWith($rootFull, [StringComparison]::OrdinalIgnoreCase)) { throw "Git path escaped repository: $relative" }
            $canonicalRelative = $full.Substring($rootFull.Length).Replace('\', '/')
            if (-not (Test-SafeRepositoryRelativePath $canonicalRelative) -or -not $canonicalRelative.Equals($normalizedRelative, [StringComparison]::OrdinalIgnoreCase)) { throw "Git path did not normalize to one safe repository-relative path: $relative" }
            if (Test-UnreadUserDataStagingPath $canonicalRelative) {
                $record.unreadUserDataCount++
                if ($null -eq $record.firstUnreadUserDataPath) { $record.firstUnreadUserDataPath = $relative }
                $record.processedCount++
                continue
            }
            $cursor = $Root
            $item = $null
            $parts = $relative -split '[\\/]'
            $linkSkipped = $false
            for ($partIndex = 0; $partIndex -lt $parts.Count; $partIndex++) {
                $part = $parts[$partIndex]
                $cursor = Join-Path $cursor $part
                $currentOperation = 'Get-Item path component'
                $item = Get-Item -LiteralPath $cursor -Force -ErrorAction Stop
                $isLeaf = ($partIndex -eq ($parts.Count - 1))
                $reparse = [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
                $gitMode = if ($indexModes.ContainsKey($relative)) { $indexModes[$relative] } else { $null }
                $action = Get-InventoryAction $gitMode $reparse $isLeaf ([bool]$item.PSIsContainer)
                if ($action -eq 'SKIP_TRACKED_SYMLINK') {
                    $record.linkInventory.Add([ordered]@{ path = $relative; mode = $gitMode; state = 'SKIPPED_SYMLINK_NOT_FOLLOWED'; attributes = [string]$item.Attributes; linkType = (Get-LinkTypeEvidence $item); targetRead = 'NOT_ATTEMPTED'; targetHash = 'NOT_CAPTURED' })
                    $record.skippedSymlinkCount++
                    $record.processedCount++
                    $linkSkipped = $true
                    # A skipped symlink must not receive any further path, target, hash, or ACL query.
                    break
                }
                if ($action -eq 'STOP') { throw "Unsupported reparse or non-regular object in protected inventory: $relative; mode=$gitMode; leaf=$isLeaf; attributes=$($item.Attributes)" }
                if (-not $isLeaf -and -not $item.PSIsContainer) { throw "Non-directory parent in protected inventory: $relative" }
            }
            if ($linkSkipped) { continue }
            $currentOperation = 'Get-FileHash'
            $hash = Get-FileHash -LiteralPath $full -Algorithm SHA256 -ErrorAction Stop
            $record.fileInventory.Add([ordered]@{ path = $relative; length = $item.Length; lastWriteTimeUtc = $item.LastWriteTimeUtc.ToString('o'); sha256 = $hash.Hash })
            $record.regularFileHashCount++
            $record.processedCount++
        }
    }
    catch { Set-RepositoryStop $record 'PROTECTED_HASH_FAILED' $currentOperation ($_.Exception.GetType().FullName + ': ' + $_.Exception.Message) $currentRelativePath; return $record }
    $record.omittedCount = [Math]::Max(0, $record.candidateCount - $record.processedCount)
    if ($record.processedCount -ne $record.candidateCount -or $record.omittedCount -ne 0) { Set-RepositoryStop $record 'PROTECTED_INVENTORY_INCOMPLETE' 'Inventory count validation' "candidate=$($record.candidateCount); processed=$($record.processedCount); omitted=$($record.omittedCount)"; return $record }
    foreach ($name in @('.git\HEAD', '.git\index', '.git\config')) { $record.gitMetadata.Add((Get-FileRecord (Join-Path $Root $name))) }
    $record.gitMetadataAfter = Get-FileRecord (Join-Path $Root '.git\index')
    $record.gitMetadataStates = @($record.gitMetadata | ForEach-Object { $_.state })
    $record.gitMetadataComplete = (@($record.gitMetadataStates | Where-Object { $_ -ne 'PRESENT' }).Count -eq 0 -and $record.gitMetadataBefore.state -eq 'PRESENT' -and $record.gitMetadataAfter.state -eq 'PRESENT')
    $record.indexStable = ($record.gitMetadataBefore.sha256 -eq $record.gitMetadataAfter.sha256)
    if (-not $record.gitMetadataComplete) {
        $invalidMetadata = @($record.gitMetadata | Where-Object { $_.state -ne 'PRESENT' } | Select-Object -First 1)
        $blockingPath = if ($invalidMetadata.Count -gt 0) { $invalidMetadata[0].path } else { Join-Path $Root '.git\index' }
        Set-RepositoryStop $record 'GIT_METADATA_INVALID' 'Git metadata post-inventory query' ($record.gitMetadataStates -join ',') $blockingPath
        return $record
    }
    $record.state = if ($record.targetMatches -and $record.indexStable) { 'CAPTURED' } else { 'TARGET_OR_INDEX_MISMATCH' }
    if ($record.state -ne 'CAPTURED') { Set-RepositoryStop $record 'TARGET_OR_INDEX_MISMATCH' 'Git index stability check' "targetMatches=$($record.targetMatches); indexStable=$($record.indexStable)" (Join-Path $Root '.git\index') }
    return $record
}

function Get-WerRecord {
    $result = [System.Collections.Generic.List[object]]::new()
    $subPath = 'SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps'
    $values = @('DumpFolder', 'DumpCount', 'DumpType', 'CustomDumpFlags')
    foreach ($hive in @([Microsoft.Win32.RegistryHive]::LocalMachine, [Microsoft.Win32.RegistryHive]::CurrentUser)) {
        foreach ($view in @([Microsoft.Win32.RegistryView]::Registry32, [Microsoft.Win32.RegistryView]::Registry64)) {
            $base = $null
            $key = $null
            try {
                $base = [Microsoft.Win32.RegistryKey]::OpenBaseKey($hive, $view)
                $key = $base.OpenSubKey($subPath, $false)
                $item = [ordered]@{
                    hive = $hive.ToString()
                    hiveNumeric = [int64]$hive
                    view = $view.ToString()
                    viewNumeric = [int]$view
                    path = $subPath
                    state = if ($null -eq $key) { 'ABSENT' } else { 'PRESENT' }
                    lastWriteMetadata = 'NOT_AVAILABLE_BY_GETTER'
                    values = [ordered]@{}
                }
                if ($null -ne $key) {
                    foreach ($valueName in $values) {
                        try { $item.values[$valueName] = [ordered]@{ kind = [string]$key.GetValueKind($valueName); value = $key.GetValue($valueName, $null, [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames) } }
                        catch [System.IO.IOException] { $item.values[$valueName] = [ordered]@{ state = 'ABSENT' } }
                    }
                }
                $result.Add($item)
            }
            catch { $result.Add([ordered]@{ hive = $hive.ToString(); hiveNumeric = [int64]$hive; view = $view.ToString(); viewNumeric = [int]$view; path = $subPath; state = 'QUERY_ERROR'; errorType = $_.Exception.GetType().FullName; error = $_.Exception.Message }) }
            finally { if ($null -ne $key) { $key.Dispose() }; if ($null -ne $base) { $base.Dispose() } }
        }
    }
    return ,$result
}

function Get-PartialRepository([object]$Record, [int]$MaxFileRecords) {
    if ($null -eq $Record -or $Record -isnot [System.Collections.IDictionary] -or -not $Record.Contains('fileInventory')) { return [ordered]@{ state = 'NOT_CAPTURED' } }
    $files = @($Record.fileInventory | Select-Object -First $MaxFileRecords)
    $links = @($Record.linkInventory | Select-Object -First $MaxFileRecords)
    $commandSummaries = [ordered]@{}
    foreach ($commandName in $Record.commands.Keys) {
        $command = $Record.commands[$commandName]
        $commandSummaries[$commandName] = [ordered]@{ executable = $command.executable; argumentList = @($command.argumentList); workingDirectory = $command.workingDirectory; exitCode = $command.exitCode; processId = $command.processId; stdoutTextEncoding = $command.stdoutTextEncoding; stdoutTextCodePage = $command.stdoutTextCodePage; textDecodeNote = $command.textDecodeNote; stdoutSha256 = $command.stdoutSha256; stdoutBase64Length = ([string]$command.stdoutBase64).Length; stderrSha256 = $command.stderrSha256; stderrBase64Length = ([string]$command.stderrBase64).Length }
    }
    $partialStatus = $null
    if ($null -ne $Record.status) {
        $partialStatus = [ordered]@{
            exitCode = $Record.status.exitCode
            rawByteCount = $Record.status.rawByteCount
            nulSegmentCountApprox = $Record.status.nulSegmentCountApprox
            countDefinition = $Record.status.countDefinition
            sha256 = $Record.status.sha256
            base64Included = $false
            omissionReason = 'Status raw bytes remain SHA-256-bound but were omitted from bounded partial JSON.'
        }
    }
    return [ordered]@{
        name = $Record.name
        root = $Record.root
        state = $Record.state
        commandSummaries = $commandSummaries
        gitTopLevel = $Record.gitTopLevel
        gitCommonDir = $Record.gitCommonDir
        head = $Record.head
        tree = $Record.tree
        branch = $Record.branch
        targetMatches = $Record.targetMatches
        candidateCountKnown = $Record.candidateCountKnown
        status = $partialStatus
        gitMetadataBefore = $Record.gitMetadataBefore
        gitMetadata = $Record.gitMetadata
        gitMetadataAfter = $Record.gitMetadataAfter
        indexStable = $Record.indexStable
        candidateCount = $Record.candidateCount
        processedCount = $Record.processedCount
        regularFileHashCount = $Record.regularFileHashCount
        skippedSymlinkCount = $Record.skippedSymlinkCount
        unreadUserDataCount = $Record.unreadUserDataCount
        firstUnreadUserDataPath = $Record.firstUnreadUserDataPath
        omittedCount = $Record.omittedCount
        firstBlockingPath = $Record.firstBlockingPath
        errorOperation = $Record.errorOperation
        emptySplitArtifactCount = $Record.emptySplitArtifactCount
        inventoryNulTerminatorCount = $Record.inventoryNulTerminatorCount
        indexStageEntryCount = $Record.indexStageEntryCount
        indexStageNulTerminatorCount = $Record.indexStageNulTerminatorCount
        fileInventoryRecordCount = @($Record.fileInventory).Count
        fileInventoryIncludedCount = $files.Count
        fileInventoryOmittedCount = [Math]::Max(0, @($Record.fileInventory).Count - $files.Count)
        fileInventory = $files
        linkInventoryIncludedCount = $links.Count
        linkInventoryOmittedCount = [Math]::Max(0, @($Record.linkInventory).Count - $links.Count)
        linkInventory = $links
        error = $Record.error
    }
}

function Get-BoundedPhaseMap([object]$Phases) {
    $keys = @('identity','mainRepository','scratchRepository','environment','paths','wer','protectedHashes','aclStability')
    $map = [ordered]@{}
    foreach ($key in $keys) {
        $val = if ($null -ne $Phases -and ($Phases -is [System.Collections.IDictionary]) -and $Phases.Contains($key)) { [string]$Phases[$key] } else { 'NOT_REACHED' }
        $map[$key] = $val
    }
    return $map
}

function New-PartialEvidence([string]$Reason, [object]$OriginalStopReason, [object]$OriginalStopCategory = $null, [object]$OriginalStopDetail = $null) {
    return [ordered]@{
        task = $Result.task
        manifest = $Result.manifest
        t0Utc = $Result.t0Utc
        t0StopwatchTicks = $Result.t0StopwatchTicks
        captureStatus = 'PARTIAL_EVIDENCE'
        partialReason = $Reason
        originalStopReason = $OriginalStopReason
        originalStopCategory = $OriginalStopCategory
        originalStopDetail = $OriginalStopDetail
        phases = Get-BoundedPhaseMap $Result.phases
        stopCategory = $Result.stopCategory
        stopDetail = $Result.stopDetail
        process = $Result.process
        identity = $Result.identity
        repository = [ordered]@{
            main = Get-PartialRepository $Result.repository.main 1000
            scratch = Get-PartialRepository $Result.repository.scratch 1000
        }
        environment = $Result.environment
        homeEnvironmentCheck = $Result.homeEnvironmentCheck
        paths = $Result.paths
        wer = $Result.wer
        protectedHashes = $Result.protectedHashes
        aclStability = $Result.aclStability
        classifications = $Result.classifications
        summary = $Result.summary
        errors = $Result.errors
        stopReason = $Result.stopReason
        omittedFullInventory = $true
    }
}

try {
    $null = Assert-InventoryPolicySelfCheck
    Assert-CommandSerializationSelfCheck
    Assert-InventoryParserSelfCheck
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    $currentProcess = [Diagnostics.Process]::GetCurrentProcess()

    $languageMode = $ExecutionContext.SessionState.LanguageMode.ToString()
    $getFileHashCmd = Get-Command -Name 'Get-FileHash' -ErrorAction SilentlyContinue
    $getAclCmd = Get-Command -Name 'Get-Acl' -ErrorAction SilentlyContinue

    $Result.process = [ordered]@{
        id = $PID
        startTimeUtc = $currentProcess.StartTime.ToUniversalTime().ToString('o')
        executablePath = $currentProcess.MainModule.FileName
        powerShellVersion = $PSVersionTable.PSVersion.ToString()
        psEdition = $PSVersionTable.PSEdition
        psHome = $PSHOME
        languageMode = $languageMode
        hostName = $Host.Name
        expectedExecutablePath = 'C:\Program Files\PowerShell\7\pwsh.exe'
        expectedPowerShellVersion = '7.6.6'
        expectedPSEdition = 'Core'
        expectedLanguageMode = 'FullLanguage'
        executablePathMatchesExpected = ($currentProcess.MainModule.FileName.Equals('C:\Program Files\PowerShell\7\pwsh.exe', [StringComparison]::OrdinalIgnoreCase))
        versionMatchesExpected = ($PSVersionTable.PSVersion.ToString() -eq '7.6.6')
        editionMatchesExpected = ($PSVersionTable.PSEdition -eq 'Core')
        languageModeMatchesExpected = ($languageMode -eq 'FullLanguage')
        getFileHashAvailable = ($null -ne $getFileHashCmd)
        getFileHashSource = if ($null -ne $getFileHashCmd) { $getFileHashCmd.Source } else { $null }
        getFileHashVersion = if ($null -ne $getFileHashCmd) { [string]$getFileHashCmd.Version } else { $null }
        getAclAvailable = ($null -ne $getAclCmd)
        getAclSource = if ($null -ne $getAclCmd) { $getAclCmd.Source } else { $null }
        getAclVersion = if ($null -ne $getAclCmd) { [string]$getAclCmd.Version } else { $null }
    }

    if (-not $Result.process.executablePathMatchesExpected -or -not $Result.process.versionMatchesExpected -or -not $Result.process.editionMatchesExpected -or -not $Result.process.languageModeMatchesExpected -or -not $Result.process.getFileHashAvailable -or -not $Result.process.getAclAvailable) {
        $Result.stopCategory = 'RUNTIME_PREREQUISITE'
        $Result.stopReason = 'RUNTIME_PREREQUISITE_FAILED'
        $Result.stopDetail = "executable=$($Result.process.executablePath); version=$($Result.process.powerShellVersion); edition=$($Result.process.psEdition); languageMode=$languageMode; getFileHash=$($Result.process.getFileHashAvailable); getAcl=$($Result.process.getAclAvailable)"
    }

    if (-not $Result.stopReason) {
        $Result.phases.identity = 'IN_PROGRESS'
        $whoamiRecord = Invoke-CapturedProcess $WhoAmIExe @('/all')
        Assert-SingleCommandRecord $whoamiRecord 'whoami /all'
        $Result.identity = [ordered]@{
            name = $identity.Name
            sid = $identity.User.Value
            authenticationType = $identity.AuthenticationType
            impersonationLevel = [string]$identity.ImpersonationLevel
            isSystem = $identity.IsSystem
            isAdministrator = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
            whoami = $whoamiRecord
        }
        $identity.Dispose()
        if ($Result.identity.whoami.exitCode -ne 0) {
            $Result.phases.identity = 'FAILED'
            $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
            $Result.stopReason = 'WHOAMI_QUERY_FAILED'
            $Result.stopDetail = "whoami exitCode=$($Result.identity.whoami.exitCode); stderr=$($Result.identity.whoami.stderr)"
            $Result.classifications.hostIdentity = 'FAILED'
        }
        elseif ($Result.identity.name -ne $ExpectedUser -or $Result.identity.sid -ne $ExpectedSid) {
            $Result.phases.identity = 'FAILED'
            $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
            $Result.stopReason = 'IDENTITY_MISMATCH'
            $Result.stopDetail = "actual=$($Result.identity.name)|$($Result.identity.sid); expected=$ExpectedUser|$ExpectedSid"
            $Result.classifications.hostIdentity = 'FAILED'
        }
        else {
            $Result.phases.identity = 'COMPLETED'
            $Result.classifications.hostIdentity = 'PASS_WITH_EVIDENCE'
        }
    }

    if (-not $Result.stopReason) {
        $Result.phases.mainRepository = 'IN_PROGRESS'
        $repoRecord = Get-RepositoryRecord 'main' $Repo $RepoHead $RepoTree 'main' 'G:\CODEX\New Manga\.git'
        $Result.repository.main = $repoRecord
        if ($repoRecord.state -ne 'CAPTURED') {
            $Result.phases.mainRepository = 'FAILED'
            $Result.classifications.repositoryProtectedInventory = 'FAILED'
            if ($repoRecord.state -eq 'GIT_INDEX_PREHASH_INVALID') {
                $Result.stopCategory = 'REPOSITORY_PREHASH'
                $Result.stopReason = 'MAIN_REPOSITORY_INDEX_PREHASH_FAILED'
            } else {
                $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
                $Result.stopReason = 'MAIN_REPOSITORY_BASELINE_OR_HASH_FAILED'
            }
            $Result.stopDetail = "state=$($repoRecord.state); op=$($repoRecord.errorOperation); err=$($repoRecord.error); path=$($repoRecord.firstBlockingPath)"
        }
        else {
            $Result.phases.mainRepository = 'COMPLETED'
        }
    }

    if (-not $Result.stopReason) {
        $Result.phases.scratchRepository = 'IN_PROGRESS'
        $scratchRecord = Get-RepositoryRecord 'scratch' $Scratch $ScratchHead $ScratchTree 'DETACHED' 'G:\CODEX\P02-scratch-build-source\.git'
        $Result.repository.scratch = $scratchRecord
        if ($scratchRecord.state -ne 'CAPTURED') {
            $Result.phases.scratchRepository = 'FAILED'
            $Result.classifications.repositoryProtectedInventory = 'FAILED'
            if ($scratchRecord.state -eq 'GIT_INDEX_PREHASH_INVALID') {
                $Result.stopCategory = 'REPOSITORY_PREHASH'
                $Result.stopReason = 'SCRATCH_REPOSITORY_INDEX_PREHASH_FAILED'
            } else {
                $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
                $Result.stopReason = 'SCRATCH_BASELINE_OR_HASH_FAILED'
            }
            $Result.stopDetail = "state=$($scratchRecord.state); op=$($scratchRecord.errorOperation); err=$($scratchRecord.error); path=$($scratchRecord.firstBlockingPath)"
        }
        else {
            $Result.phases.scratchRepository = 'COMPLETED'
        }
    }

    if (-not $Result.stopReason) {
        $Result.phases.environment = 'IN_PROGRESS'
        $envNames = 'LOCALAPPDATA,TEMP,TMP,APPDATA,USERPROFILE,HOME,HOMEDRIVE,HOMEPATH,PYTHONPYCACHEPREFIX,PYTHONDONTWRITEBYTECODE,PYTHONUSERBASE,PYTHONNOUSERSITE,TRITON_CACHE_DIR,PYINSTALLER_CONFIG_DIR,TORCH_HOME,TORCHINDUCTOR_CACHE_DIR,TORCH_EXTENSIONS_DIR,XDG_CACHE_HOME,XDG_DATA_HOME,HF_HOME,HF_HUB_CACHE,HF_ASSETS_CACHE,HF_XET_CACHE,HF_TOKEN_PATH,HF_HUB_DISABLE_IMPLICIT_TOKEN,TRANSFORMERS_CACHE,PIP_CACHE_DIR,UV_CACHE_DIR,CARGO_HOME,CARGO_TARGET_DIR,NPM_CONFIG_CACHE,NPM_CONFIG_USERCONFIG,GIT_CONFIG_GLOBAL,GIT_CONFIG_NOSYSTEM,GIT_TERMINAL_PROMPT'.Split(',')
        foreach ($name in $envNames) { $Result.environment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
        $homeDrive = $Result.environment.HOMEDRIVE
        $homePath = $Result.environment.HOMEPATH
        $userProfile = $Result.environment.USERPROFILE
        if ($homeDrive -and $homePath -and $userProfile) {
            $combinedHome = [IO.Path]::GetFullPath($homeDrive + $homePath).TrimEnd('\')
            $normalizedUserProfile = [IO.Path]::GetFullPath($userProfile).TrimEnd('\')
            $Result.homeEnvironmentCheck = [ordered]@{
                combinedHostHome = $combinedHome
                normalizedHostUserProfile = $normalizedUserProfile
                matchesHostUserProfile = ($combinedHome -eq $normalizedUserProfile)
                futureLpacHome = (Join-Path $Scratch 'tmp\home')
                futureLpacMappingState = 'NOT_APPLIED_IN_R1G; verify exact new environment in P02PRE-R2'
            }
        }
        else { $Result.homeEnvironmentCheck = [ordered]@{ state = 'UNPROVABLE'; missingVariable = 'HOMEDRIVE/HOMEPATH/USERPROFILE'; futureLpacMappingState = 'NOT_APPLIED_IN_R1G' } }
        $homeState = if ($Result.homeEnvironmentCheck.matchesHostUserProfile -eq $true) { 'PASS_WITH_EVIDENCE' } elseif ($Result.homeEnvironmentCheck.matchesHostUserProfile -eq $false) { 'FAILED' } else { 'UNPROVABLE' }
        $Result.classifications.hostHomeConsistency = $homeState
        if ($homeState -eq 'FAILED') {
            $Result.phases.environment = 'FAILED'
            $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
            $Result.stopReason = 'HOME_ENVIRONMENT_MISMATCH'
            $Result.stopDetail = "combinedHome=$combinedHome; normalizedUserProfile=$normalizedUserProfile"
        }
        else {
            $Result.phases.environment = 'COMPLETED'
        }
    }

    if (-not $Result.stopReason) {
        $Result.phases.paths = 'IN_PROGRESS'
        $inputRoots = @(
            'C:\Users\49745\AppData\Local\Programs\Python\Python312',
            'G:\CODEX\New Manga.task-envs\m2ac5-build',
            'G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\ogkalu-comic-text-and-bubble-detector',
            'G:\CODEX\New Manga.task-envs\M2-SFX-DETECT\weights-v2b',
            'E:\Program Files\nodejs',
            'C:\Users\49745\.rustup\toolchains\stable-x86_64-pc-windows-msvc',
            'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools',
            'C:\Program Files (x86)\Microsoft Visual Studio\Installer',
            'C:\Program Files (x86)\Windows Kits\10',
            'C:\Program Files\Git\cmd',
            'C:\Program Files\Git\mingw64',
            $Scratch
        )
        foreach ($path in $inputRoots) { $Result.paths[$path] = Get-ExactDirectoryRecord $path $false }
        $outputLeaves = @('apps/desktop/frontend/node_modules','apps/desktop/frontend/dist','apps/desktop/src-tauri/target/core-sidecar','apps/desktop/src-tauri/target/pyinstaller-work','apps/desktop/src-tauri/gen/schemas','apps/desktop/src-tauri/permissions/autogenerated','verification/P02/cargo-target','npm-cache','cargo-home','tmp/appdata','tmp/home','python-cache','pyinstaller-config')
        foreach ($leaf in $outputLeaves) { $path = Join-Path $Scratch $leaf; $Result.paths[$path] = Get-ExactDirectoryRecord $path $true }
        $canaryLeaves = @('verification/P02/tmp/smoke-readonly-probe','verification/P02/tmp/lpac-write-control','verification/P02/tmp/lpac-write-deny-control')
        foreach ($leaf in $canaryLeaves) { $path = Join-Path $Scratch $leaf; $Result.paths[$path] = Get-ExactDirectoryRecord $path $true }

        $pathRecords = @($Result.paths.Values)
        $pathQueryErrorCount = @($pathRecords | Where-Object { $_.state -in @('QUERY_ERROR','ACL_QUERY_ERROR') }).Count
        $pathAclUnverifiableCount = @($pathRecords | Where-Object { $_.state -eq 'ACL_UNVERIFIABLE' }).Count
        $invalidPathCount = @($pathRecords | Where-Object { $_.state -in @('REPARSE_POINT','NOT_DIRECTORY') }).Count
        $missingInputRootCount = @($inputRoots | Where-Object { $Result.paths[$_].state -eq 'ABSENT' }).Count

        $Result.classifications.hostPathSnapshots = if ($pathQueryErrorCount -gt 0 -or $invalidPathCount -gt 0 -or $missingInputRootCount -gt 0) { 'FAILED' } elseif ($pathAclUnverifiableCount -gt 0) { 'UNPROVABLE' } else { 'PASS_WITH_EVIDENCE' }
        $Result.classifications.tempCache = 'UNPROVABLE'

        if ($pathQueryErrorCount -gt 0 -or $invalidPathCount -gt 0 -or $missingInputRootCount -gt 0) {
            $Result.phases.paths = 'FAILED'
            $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
            $Result.stopReason = 'PATH_SNAPSHOTS_FAILED'
            $Result.stopDetail = "queryErrors=$pathQueryErrorCount; invalidPaths=$invalidPathCount; missingRoots=$missingInputRootCount"
        }
        else {
            $Result.phases.paths = 'COMPLETED'
        }
    }

    if (-not $Result.stopReason) {
        $Result.phases.wer = 'IN_PROGRESS'
        $werDirs = @('C:\Users\49745\AppData\Local\CrashDumps','C:\ProgramData\Microsoft\Windows\WER\ReportQueue','C:\ProgramData\Microsoft\Windows\WER\ReportArchive')
        foreach ($path in $werDirs) { $Result.wer[$path] = Get-ExactDirectoryRecord $path $false }
        $Result.wer.registry = Get-WerRecord
        $Result.wer.unqueriedPolicyScope = [ordered]@{ perImageSubkeys = 'NOT_ENUMERATED / UNPROVABLE'; otherValues = 'NOT_ENUMERATED / UNPROVABLE'; hkcuInterpretation = 'Historical observation candidate only; not treated as effective LocalDumps policy.' }

        $werDirectoryRecords = @($werDirs | ForEach-Object { $Result.wer[$_] })
        $werDirectoryQueryErrorCount = @($werDirectoryRecords | Where-Object { $_.state -in @('QUERY_ERROR','ACL_QUERY_ERROR') }).Count
        $werInvalidDirectoryRecords = @($werDirectoryRecords | Where-Object { $_.state -in @('REPARSE_POINT','NOT_DIRECTORY') })
        $werInvalidDirectoryCount = $werInvalidDirectoryRecords.Count
        $registryRecords = @($Result.wer.registry)
        $werRegistryQueryErrorCount = @($registryRecords | Where-Object { $_.state -eq 'QUERY_ERROR' }).Count
        $werQueryErrorCount = $werDirectoryQueryErrorCount + $werRegistryQueryErrorCount

        $Result.classifications.werQueriedFields = if ($werQueryErrorCount -eq 0 -and $werInvalidDirectoryCount -eq 0) { 'PASS_WITH_EVIDENCE' } else { 'FAILED' }
        $Result.classifications.werEffectivePolicy = 'UNPROVABLE'

        if ($werInvalidDirectoryCount -gt 0 -or $werQueryErrorCount -gt 0) {
            $Result.phases.wer = 'FAILED'
            $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
            $Result.stopReason = if ($werInvalidDirectoryCount -gt 0) { 'WER_INVALID_DIRECTORY_FAILED' } else { 'WER_QUERY_FAILED' }
            $invalidDetails = if ($werInvalidDirectoryCount -gt 0) { " ($(@($werInvalidDirectoryRecords | ForEach-Object { "$($_.path)=$($_.state)" }) -join '; '))" } else { '' }
            $Result.stopDetail = "directoryQueryErrors=$werDirectoryQueryErrorCount; invalidDirectories=$werInvalidDirectoryCount$invalidDetails; registryQueryErrors=$werRegistryQueryErrorCount"
        }
        else {
            $Result.phases.wer = 'COMPLETED'
        }
    }

    if (-not $Result.stopReason) {
        $Result.phases.protectedHashes = 'IN_PROGRESS'
        foreach ($key in @(
            'AGENTS.md',
            'doc/REBASELINE_PLAN.md',
            'doc/00_INDEX.md',
            'doc/STATUS.md',
            'doc/09_COLLABORATION.md',
            'doc/tasks/P02.md',
            'doc/tasks/P02PRE-R0S6.md',
            'doc/tasks/P02PRE-R1.md',
            'doc/tasks/P02PRE-R1F.md',
            'verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md',
            'verification/P02/p02pre-r1-manifest-20261011.md',
            'verification/P02/p02pre-r1-capture.ps1',
            'verification/P02/p02pre-r1-evidence-20261011.json',
            'verification/P02/p02pre-r1f-manifest-20261011.md',
            'verification/P02/p02pre-r1f-capture.ps1',
            'verification/P02/p02pre-r1f-r2-selfcheck-20261011.json',
            'verification/P02/p02pre-r1f-r5-selfcheck-20261011.json',
            'verification/P02/p02pre-r1f-r5-selfcheck-retry-20261011.json',
            'verification/P02/p02pre-r1f-parser-20261011.json',
            'verification/P02/p02pre-r1f-parser-windows-powershell-5.1-20261011.json',
            'verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r2-20261011.json',
            'verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r3-20261011.json',
            'verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r4-20261011.json',
            'verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r6-20261011.json',
            'verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r7-20261011.json',
            'verification/P02/dsh-p02pre-r1f-review-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-20261011.stdout.jsonl',
            'verification/P02/dsh-p02pre-r1f-review-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-20261011.exit',
            'verification/P02/dsh-p02pre-r1f-review-20261011.md',
            'verification/P02/dsh-p02pre-r1f-review-r2-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r2-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r2-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r2-20261011.exit',
            'verification/P02/dsh-p02pre-r1f-review-r3-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r3-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r3-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r3-20261011.exit',
            'verification/P02/dsh-p02pre-r1f-review-r5-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r5-20261011.exit',
            'verification/P02/p02pre-r1f-adjudication-20261011.md',
            'verification/P02/codex-checkpoint-p02pre-r1f-20261011.md',
            'verification/P02/p02pre-r0s6-checkpoint-20261011.md',
            'verification/P02/p02pre-r1f-r5-reviewfix-selfcheck-20261011.json',
            'verification/P02/p02pre-r1f-followupfix-selfcheck-wrapper-attempt1-20261011.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.exit',
            'verification/P02/p02pre-r1f-r5-adjudication-20261011.md',
            'verification/P02/p02pre-r1f-r5-followupfix-selfcheck-20261011.json',
            'verification/P02/p02pre-r1f-r5-followupfix2-selfcheck-20261011.json',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup2-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup2-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup2-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup2-20261011.exit',
            'verification/P02/p02pre-r1f-r5-followup2-adjudication-20261011.md',
            'verification/P02/p02pre-r1f-r5-followup2-review-adjudication-20261011.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup3-20261011.exit',
            'verification/P02/p02pre-r1f-r5-followup3-review-adjudication-20261011.md',
            'verification/P02/p02pre-r1f-r5-followupfix3-selfcheck-20261011.json',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup4-20261011.exit',
            'verification/P02/p02pre-r1f-r5-followup4-review-adjudication-20261011.md',
            'verification/P02/p02pre-r1f-r5-followupfix4-selfcheck-20261011.json',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup5-20261011.exit',
            'verification/P02/p02pre-r1f-r5-followup5-review-adjudication-20261011.md',
            'verification/P02/p02pre-r1f-r5-followupfix5-selfcheck-20261011.json',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup6-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup6-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup6-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r5-followup6-20261011.exit',
            'verification/P02/p02pre-r1f-r5-followup6-review-adjudication-20261011.md'
        )) {
            $Result.protectedHashes[$key] = Get-FileRecord (Join-Path $Repo $key)
        }
        foreach ($key in @(
            'verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json',
            'verification/P02/dsh-p02pre-r1f-review-r4-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r4-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r4-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r4-20261011.exit',
            'verification/P02/dsh-p02pre-r1f-review-r4-retry-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r4-retry-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r4-retry-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r4-retry-20261011.exit',
            'verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.prompt.md',
            'verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.stdout.md',
            'verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.stderr.log',
            'verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.exit'
        )) {
            $Result.protectedHashes[$key] = Get-FileRecord (Join-Path $Repo $key)
        }
        $hashRecords = @($Result.protectedHashes.Values)
        $invalidHashCount = @($hashRecords | Where-Object { $_.state -ne 'PRESENT' }).Count
        if ($invalidHashCount -gt 0) {
            $Result.phases.protectedHashes = 'FAILED'
            $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
            $Result.stopReason = 'PROTECTED_HASH_FAILED'
            $Result.stopDetail = "invalidHashCount=$invalidHashCount"
        }
        else {
            $Result.phases.protectedHashes = 'COMPLETED'
        }

        if (-not $Result.stopReason) {
            $Result.phases.aclStability = 'IN_PROGRESS'
            $aclTargets = [System.Collections.Generic.List[object]]::new()
            foreach ($path in $Result.paths.Keys) { $aclTargets.Add([ordered]@{ path = $path; before = $Result.paths[$path] }) }
            foreach ($path in $werDirs) { $aclTargets.Add([ordered]@{ path = $path; before = $Result.wer[$path] }) }
            $aclComparisons = [System.Collections.Generic.List[object]]::new()
            foreach ($target in $aclTargets) {
                $before = $target.before
                if ($before.state -ne 'PRESENT') {
                    $beforeCompareState = if ($before.state -eq 'ACL_UNVERIFIABLE') { 'UNVERIFIABLE' } elseif ($before.state -eq 'ACL_QUERY_ERROR') { 'QUERY_ERROR' } else { 'NOT_COMPARABLE' }
                    $aclComparisons.Add([ordered]@{ path = $target.path; state = $beforeCompareState; beforeState = $before.state })
                    continue
                }
                try {
                    $afterChain = Get-PathChain $target.path
                    if ($afterChain.state -ne 'PRESENT') { $aclComparisons.Add([ordered]@{ path = $target.path; state = 'PATH_QUERY_ERROR'; afterPathState = $afterChain.state }); continue }
                    $afterAcl = Get-Acl -LiteralPath $target.path -ErrorAction Stop
                    if ($null -eq $afterAcl -or [string]::IsNullOrWhiteSpace([string]$afterAcl.Owner) -or [string]::IsNullOrWhiteSpace([string]$afterAcl.Sddl)) { $aclComparisons.Add([ordered]@{ path = $target.path; state = 'UNVERIFIABLE'; reason = 'Owner or SDDL was empty/unavailable at endpoint recheck.'; afterOwner = $afterAcl.Owner; afterSddl = $afterAcl.Sddl }); continue }
                    $beforeChainJson = ConvertTo-Json -InputObject $before.pathChain -Compress -Depth 4
                    $afterChainJson = ConvertTo-Json -InputObject $afterChain.components -Compress -Depth 4
                    $changed = ($before.owner -ne $afterAcl.Owner -or $before.securityDescriptorSddl -ne $afterAcl.Sddl -or $beforeChainJson -ne $afterChainJson)
                    $aclComparisons.Add([ordered]@{ path = $target.path; state = if ($changed) { 'CHANGED' } else { 'SAME_AT_ENDPOINTS' }; beforeOwner = $before.owner; afterOwner = $afterAcl.Owner; beforeSddl = $before.securityDescriptorSddl; afterSddl = $afterAcl.Sddl; ancestorChainSame = ($beforeChainJson -eq $afterChainJson) })
                }
                catch { $aclComparisons.Add([ordered]@{ path = $target.path; state = 'QUERY_ERROR'; errorType = $_.Exception.GetType().FullName; error = $_.Exception.Message }) }
            }
            $aclChangedCount = @($aclComparisons | Where-Object { $_.state -eq 'CHANGED' }).Count
            $aclQueryErrorCount = @($aclComparisons | Where-Object { $_.state -match 'QUERY_ERROR|PATH_QUERY_ERROR' }).Count
            $aclNotComparableCount = @($aclComparisons | Where-Object { $_.state -eq 'NOT_COMPARABLE' }).Count
            $aclUnverifiableCount = @($aclComparisons | Where-Object { $_.state -eq 'UNVERIFIABLE' }).Count
            $Result.aclStability = [ordered]@{
                comparisons = $aclComparisons
                changedCount = $aclChangedCount
                queryErrorCount = $aclQueryErrorCount
                notComparableCount = $aclNotComparableCount
                unverifiableCount = $aclUnverifiableCount
                scope = 'Before/after endpoint owner, SDDL and component attributes only; not proof against transient changes or file-ID/hardlink/ADS changes.'
            }
            $Result.classifications.hostAclSnapshots = if ($aclChangedCount -gt 0 -or $aclQueryErrorCount -gt 0) { 'FAILED' } elseif ($aclNotComparableCount -gt 0 -or $aclUnverifiableCount -gt 0) { 'UNPROVABLE' } else { 'PASS_WITH_EVIDENCE' }

            if ($aclChangedCount -gt 0 -or $aclQueryErrorCount -gt 0 -or $aclUnverifiableCount -gt 0) {
                $Result.phases.aclStability = 'FAILED'
                $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
                $Result.stopReason = 'ACL_STABILITY_OR_QUERY_FAILED'
                $Result.stopDetail = "aclChangedCount=$aclChangedCount; aclQueryErrorCount=$aclQueryErrorCount; aclUnverifiableCount=$aclUnverifiableCount"
            }
            else {
                $Result.phases.aclStability = 'COMPLETED'
            }
        }

        $pathRecords = @($Result.paths.Values)
        $werDirectoryRecords = @($werDirs | ForEach-Object { $Result.wer[$_] })
        $registryRecords = @($Result.wer.registry)
        $hashRecords = @($Result.protectedHashes.Values)
        $repoRecords = @($Result.repository.main, $Result.repository.scratch)
        $nonemptyOutputCount = 0
        foreach ($leaf in $outputLeaves) { $leafRecord = $Result.paths[(Join-Path $Scratch $leaf)]; if ($null -ne $leafRecord.directEntryCount -and $leafRecord.directEntryCount -gt 0) { $nonemptyOutputCount++ } }
        $pathQueryErrorCount = @($pathRecords | Where-Object { $_.state -in @('QUERY_ERROR','ACL_QUERY_ERROR') }).Count
        $werDirectoryQueryErrorCount = @($werDirectoryRecords | Where-Object { $_.state -in @('QUERY_ERROR','ACL_QUERY_ERROR') }).Count
        $pathAclUnverifiableCount = @($pathRecords | Where-Object { $_.state -eq 'ACL_UNVERIFIABLE' }).Count
        $werRegistryQueryErrorCount = @($registryRecords | Where-Object { $_.state -eq 'QUERY_ERROR' }).Count
        $werQueryErrorCount = $werDirectoryQueryErrorCount + $werRegistryQueryErrorCount
        $queryErrorCount = $pathQueryErrorCount + $werQueryErrorCount
        $invalidPathCount = @($pathRecords + $werDirectoryRecords | Where-Object { $_.state -in @('REPARSE_POINT','NOT_DIRECTORY') }).Count
        $missingInputRootCount = @($inputRoots | Where-Object { $Result.paths[$_].state -eq 'ABSENT' }).Count
        $repoFailureCount = @($repoRecords | Where-Object { $_.state -ne 'CAPTURED' }).Count
        $repoCandidateCount = (@($repoRecords | ForEach-Object { $_.candidateCount } | Measure-Object -Sum).Sum)
        $repoProcessedCount = (@($repoRecords | ForEach-Object { $_.processedCount } | Measure-Object -Sum).Sum)
        $repoSymlinkSkipCount = (@($repoRecords | ForEach-Object { $_.skippedSymlinkCount } | Measure-Object -Sum).Sum)
        $repoUnreadUserDataCount = (@($repoRecords | ForEach-Object { $_.unreadUserDataCount } | Measure-Object -Sum).Sum)
        $repoOmittedCountKnown = @($repoRecords | Where-Object { $_.candidateCountKnown -ne $true }).Count -eq 0
        $repoOmittedCount = if ($repoOmittedCountKnown) { (@($repoRecords | ForEach-Object { $_.omittedCount } | Measure-Object -Sum).Sum) } else { $null }
        $aclChangedCount = if ($null -ne $Result.aclStability) { $Result.aclStability.changedCount } else { 0 }
        $aclQueryErrorCount = if ($null -ne $Result.aclStability) { $Result.aclStability.queryErrorCount } else { 0 }
        $aclNotComparableCount = if ($null -ne $Result.aclStability) { $Result.aclStability.notComparableCount } else { 0 }
        $aclUnverifiableCount = if ($null -ne $Result.aclStability) { $Result.aclStability.unverifiableCount } else { 0 }
        $aclEndpointCount = if ($null -ne $Result.aclStability -and $null -ne $Result.aclStability.comparisons) { @($Result.aclStability.comparisons).Count } else { 0 }
        $homeState = if ($Result.homeEnvironmentCheck.matchesHostUserProfile -eq $true) { 'PASS_WITH_EVIDENCE' } elseif ($Result.homeEnvironmentCheck.matchesHostUserProfile -eq $false) { 'FAILED' } else { 'UNPROVABLE' }
        $Result.summary = [ordered]@{
            exactPathObjects = $pathRecords.Count + $werDirectoryRecords.Count
            pathQueryErrors = $pathQueryErrorCount
            werDirectoryQueryErrors = $werDirectoryQueryErrorCount
            werRegistryQueryErrors = $werRegistryQueryErrorCount
            werQueryErrors = $werQueryErrorCount
            reparseOrNotDirectory = $invalidPathCount
            missingInputRoots = $missingInputRootCount
            registryRecords = $registryRecords.Count
            invalidProtectedHashRecords = $invalidHashCount
            repositoryCaptureFailures = $repoFailureCount
            repositoryFileInventoryRecords = (@($repoRecords | ForEach-Object { @($_.fileInventory).Count } | Measure-Object -Sum).Sum)
            repositoryCandidatePaths = $repoCandidateCount
            repositoryProcessedPaths = $repoProcessedCount
            repositorySkippedSymlinks = $repoSymlinkSkipCount
            repositoryUnreadUserDataPaths = $repoUnreadUserDataCount
            repositoryOmittedCountKnown = $repoOmittedCountKnown
            repositoryOmittedPaths = $repoOmittedCount
            repositoryStatusRawBytes = (@($repoRecords | ForEach-Object { $_.status.rawByteCount } | Measure-Object -Sum).Sum)
            aclEndpointComparisons = $aclEndpointCount
            aclChangesObserved = $aclChangedCount
            aclRecheckErrors = $aclQueryErrorCount
            aclNotComparable = $aclNotComparableCount
            aclUnverifiable = $aclUnverifiableCount
            pathAclUnverifiable = $pathAclUnverifiableCount
            nonemptyScratchOutputLeaves = $nonemptyOutputCount
            environmentVariables = $envNames.Count
            queryErrorCount = ($queryErrorCount + $repoFailureCount + $aclQueryErrorCount + $invalidHashCount + [int]($Result.identity.whoami.exitCode -ne 0))
            outputLeafState = if ($nonemptyOutputCount -gt 0) { 'FAILED_FOR_REUSE; no leaf changed' } else { 'EMPTY_OR_ABSENT_AT_CAPTURE' }
            accessClosure = 'UNPROVABLE_NOT_MONITORED_IN_R1G'
        }
        $Result.classifications.repositoryProtectedInventory = if ($repoFailureCount -gt 0) { 'FAILED' } elseif ($repoSymlinkSkipCount -gt 0 -or $repoUnreadUserDataCount -gt 0) { 'UNPROVABLE' } else { 'PASS_WITH_EVIDENCE' }
        $Result.classifications.repositoryProtectedInventoryNote = if ($repoUnreadUserDataCount -gt 0 -and $repoSymlinkSkipCount -gt 0) { "Root .tmp.driveupload paths were not opened or hashed (excluded=$repoUnreadUserDataCount); tracked symlink targets were not read or hashed (skipped=$repoSymlinkSkipCount)." } elseif ($repoUnreadUserDataCount -gt 0) { "Root .tmp.driveupload staging paths were not opened or hashed; excluded paths=$repoUnreadUserDataCount; first path=$(@($repoRecords | Where-Object { $_.firstUnreadUserDataPath } | Select-Object -First 1 -ExpandProperty firstUnreadUserDataPath))" } elseif ($repoSymlinkSkipCount -gt 0) { 'Tracked mode=120000 symlink leaves were recorded as metadata-only; target content was not read or hashed.' } else { 'All enumerated regular-file candidates were hashed.' }
        $Result.classifications.hostPathSnapshots = if ($pathQueryErrorCount -gt 0 -or @($pathRecords | Where-Object { $_.state -in @('REPARSE_POINT','NOT_DIRECTORY') }).Count -gt 0 -or $missingInputRootCount -gt 0) { 'FAILED' } elseif ($pathAclUnverifiableCount -gt 0) { 'UNPROVABLE' } else { 'PASS_WITH_EVIDENCE' }
        if (-not $Result.classifications.Contains('hostAclSnapshots')) {
            $Result.classifications.hostAclSnapshots = if ($aclChangedCount -gt 0 -or $aclQueryErrorCount -gt 0) { 'FAILED' } elseif ($aclNotComparableCount -gt 0 -or $aclUnverifiableCount -gt 0) { 'UNPROVABLE' } elseif ($Result.phases.aclStability -eq 'COMPLETED') { 'PASS_WITH_EVIDENCE' } else { 'NOT_REACHED' }
        }
        $Result.classifications.effectiveAccessAndWriteClosure = 'REQUIRES_ACTIVE_TEST'
        $Result.classifications.hostHomeConsistency = $homeState
        $Result.classifications.tempCache = 'UNPROVABLE'
        $Result.classifications.werQueriedFields = if ($werQueryErrorCount -eq 0 -and $werInvalidDirectoryCount -eq 0) { 'PASS_WITH_EVIDENCE' } else { 'FAILED' }
        $Result.classifications.fullProtectedInvariantsAndDynamicWriteClosure = 'REQUIRES_ACTIVE_TEST'

        if (-not $Result.stopReason) {
            if ($queryErrorCount -gt 0 -or $invalidPathCount -gt 0 -or $missingInputRootCount -gt 0 -or $repoFailureCount -gt 0 -or $homeState -eq 'FAILED') {
                $Result.stopCategory = 'INVENTORY_OR_QUERY_STOP'
                $Result.stopReason = 'QUERY_ERROR_OR_PATH_DRIFT_INCOMPLETE'
                $Result.stopDetail = "queryErrorCount=$queryErrorCount; invalidPathCount=$invalidPathCount; missingInputRootCount=$missingInputRootCount; repoFailureCount=$repoFailureCount"
            }
        }
    }
}
catch {
    $Result.errors.Add(($_.Exception.GetType().FullName + ': ' + $_.Exception.Message))
    if ([string]::IsNullOrEmpty($Result.stopCategory)) { $Result.stopCategory = 'UNEXPECTED_EXCEPTION' }
    if ([string]::IsNullOrEmpty($Result.stopReason)) { $Result.stopReason = 'CAPTURE_EXCEPTION' }
    if ([string]::IsNullOrEmpty($Result.stopDetail)) { $Result.stopDetail = ($_.Exception.GetType().FullName + ': ' + $_.Exception.Message) }
    foreach ($phaseName in @('identity','mainRepository','scratchRepository','environment','paths','wer','protectedHashes','aclStability')) {
        if ($Result.phases[$phaseName] -eq 'IN_PROGRESS') {
            $Result.phases[$phaseName] = 'FAILED'
        }
    }
}

$json = $null
try { $json = ConvertTo-Json -InputObject $Result -Depth 16 }
catch {
    $underlyingStopCategory = $Result.stopCategory
    $underlyingStopReason = $Result.stopReason
    $underlyingStopDetail = $Result.stopDetail
    $serializationException = ($_.Exception.GetType().FullName + ': ' + $_.Exception.Message)
    $serializationError = 'JSON serialization: ' + $serializationException
    $Result.errors.Add($serializationError)
    $Result.stopCategory = 'EVIDENCE_SERIALIZATION_FAILED'
    $Result.stopReason = 'EVIDENCE_SERIALIZATION_FAILED'
    $Result.stopDetail = $serializationError
    $json = ConvertTo-Json -InputObject ([ordered]@{
        task = $Result.task
        manifest = $Result.manifest
        t0Utc = $Result.t0Utc
        captureStatus = 'PARTIAL_EVIDENCE'
        underlyingStopCategory = $underlyingStopCategory
        underlyingStopReason = $underlyingStopReason
        underlyingStopDetail = $underlyingStopDetail
        phases = Get-BoundedPhaseMap $Result.phases
        stopCategory = $Result.stopCategory
        stopReason = $Result.stopReason
        stopDetail = $Result.stopDetail
        serializationException = $serializationException
        errors = $Result.errors
    }) -Depth 4
}
$maxEvidenceBytes = 67108864
if ([Text.Encoding]::UTF8.GetByteCount($json) -gt $maxEvidenceBytes) {
    $originalStopCategory = $Result.stopCategory
    $originalStopReason = $Result.stopReason
    $originalStopDetail = $Result.stopDetail
    $Result.stopCategory = 'EVIDENCE_SIZE_LIMIT_PARTIAL'
    $Result.stopReason = 'EVIDENCE_SIZE_LIMIT_PARTIAL'
    $Result.stopDetail = 'Full JSON exceeded 64 MiB; bounded partial records retained.'
    $partial = New-PartialEvidence 'Full JSON exceeded 64 MiB; bounded partial records retained, full per-file inventory omitted.' $originalStopReason $originalStopCategory $originalStopDetail
    $json = ConvertTo-Json -InputObject $partial -Depth 16
    if ([Text.Encoding]::UTF8.GetByteCount($json) -gt $maxEvidenceBytes) {
        $json = ConvertTo-Json -InputObject ([ordered]@{
            task = $Result.task
            manifest = $Result.manifest
            t0Utc = $Result.t0Utc
            captureStatus = 'PARTIAL_EVIDENCE'
            partialReason = 'Bounded partial JSON also exceeded 64 MiB.'
            originalStopCategory = $originalStopCategory
            originalStopReason = $originalStopReason
            originalStopDetail = $originalStopDetail
            phases = Get-BoundedPhaseMap $Result.phases
            stopCategory = $Result.stopCategory
            stopDetail = $Result.stopDetail
            stopReason = $Result.stopReason
            fullEvidenceBytesExceeded = $maxEvidenceBytes
            omittedFullInventory = $true
            repositoryStates = [ordered]@{ main = $Result.repository.main.state; scratch = $Result.repository.scratch.state }
            classifications = $Result.classifications
            summary = $Result.summary
            errors = $Result.errors
        }) -Depth 6
    }
}
try {
    $stream = [IO.File]::Open($EvidencePath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json)
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    }
    finally { $stream.Dispose() }
}
catch {
    $writeError = "EVIDENCE_WRITE_FAILED; stopCategory=EVIDENCE_WRITE_FAILED; stopReason=$($Result.stopReason); no retry or cleanup; target may contain partial bytes: $($_.Exception.GetType().FullName): $($_.Exception.Message)"
    $Result.errors.Add($writeError)
    throw $writeError
}

if ($Result.stopReason) { throw "P02PRE-R1G stopped: $($Result.stopReason); evidence=$EvidencePath" }
Write-Output "P02PRE-R1G capture complete; evidence=$EvidencePath"
