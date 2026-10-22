$ErrorActionPreference = 'Stop'

$Repo = 'G:\CODEX\New Manga'
$Scratch = 'G:\CODEX\P02-scratch-build-source'
$EvidencePath = 'G:\CODEX\New Manga\verification\P02\p02pre-r1-evidence-20261011.json'
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
    task = 'P02PRE-R1'
    manifest = 'verification/P02/p02pre-r1-manifest-20261011.md'
    t0Utc = $T0
    t0StopwatchTicks = $T0Tick
    command = 'Windows PowerShell -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File verification/P02/p02pre-r1-capture.ps1'
    cwd = (Get-Location).Path
    process = [ordered]@{}
    identity = [ordered]@{}
    repository = [ordered]@{}
    environment = [ordered]@{}
    paths = [ordered]@{}
    wer = [ordered]@{}
    protectedHashes = [ordered]@{}
    classifications = [ordered]@{
        hostIdentity = 'UNPROVABLE'
        private_registry_absence = 'UNPROVABLE'
        profile_api_path_and_store = 'REQUIRES_ACTIVE_TEST'
        lpac_write_and_child_closure = 'REQUIRES_ACTIVE_TEST'
        product_build_and_ac1_ac7 = 'NOT_RUN'
        process_and_path_access_closure = 'UNPROVABLE_NOT_MONITORED_IN_R1'
        tempCache = 'UNPROVABLE'
        werEffectivePolicy = 'UNPROVABLE'
    }
    errors = [System.Collections.Generic.List[string]]::new()
    stopReason = $null
}

function Invoke-CapturedProcess([string]$FileName, [string]$Arguments) {
    $info = New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName = $FileName
    $info.Arguments = $Arguments
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $info
    if (-not $process.Start()) { throw "Process start returned false: $FileName $Arguments" }
    $stdoutBuffer = New-Object System.IO.MemoryStream
    $stderrBuffer = New-Object System.IO.MemoryStream
    $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($stdoutBuffer)
    $stderrTask = $process.StandardError.BaseStream.CopyToAsync($stderrBuffer)
    $process.WaitForExit()
    $stdoutTask.GetAwaiter().GetResult()
    $stderrTask.GetAwaiter().GetResult()
    $stdoutBytes = $stdoutBuffer.ToArray()
    $stderrBytes = $stderrBuffer.ToArray()
    $encoding = if ($FileName -eq $GitExe) { [Text.UTF8Encoding]::new($false, $false) } else { [Console]::OutputEncoding }
    $captured = [ordered]@{
        executable = $FileName
        arguments = $Arguments
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
    $stdoutBuffer.Dispose()
    $stderrBuffer.Dispose()
    $process.Dispose()
    return $captured
}

function Invoke-Git([string]$Root, [string]$Arguments) {
    $prefix = '--no-optional-locks -c core.quotepath=false -c core.fsmonitor=false -c core.untrackedCache=false -C "' + $Root + '" '
    return Invoke-CapturedProcess $GitExe ($prefix + $Arguments)
}

function Get-ByteHash([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($sha.ComputeHash($Bytes)).Replace('-', '') }
    finally { $sha.Dispose() }
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

function Get-RepositoryRecord([string]$Name, [string]$Root, [string]$ExpectedHead, [string]$ExpectedTree, [string]$ExpectedBranch, [string]$ExpectedCommonDir) {
    $record = [ordered]@{ name = $Name; root = $Root; commands = [ordered]@{}; fileInventory = [System.Collections.Generic.List[object]]::new(); gitMetadata = [System.Collections.Generic.List[object]]::new(); state = 'STARTED' }
    $record.rootPathChain = Get-PathChain $Root
    $record.gitDirPathChain = Get-PathChain (Join-Path $Root '.git')
    if ($record.rootPathChain.state -ne 'PRESENT' -or $record.gitDirPathChain.state -ne 'PRESENT') { $record.state = 'REPOSITORY_PATH_CHAIN_INVALID'; return $record }
    $rootItem = Get-Item -LiteralPath $Root -Force -ErrorAction Stop
    $gitDirItem = Get-Item -LiteralPath (Join-Path $Root '.git') -Force -ErrorAction Stop
    if (-not $rootItem.PSIsContainer -or ($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -or -not $gitDirItem.PSIsContainer -or ($gitDirItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        $record.state = 'REPOSITORY_ROOT_OR_GITDIR_INVALID'
        return $record
    }
    $record.gitMetadataBefore = Get-FileRecord (Join-Path $Root '.git\index')
    if ($record.gitMetadataBefore.state -ne 'PRESENT') { $record.state = 'GIT_INDEX_PREHASH_INVALID'; return $record }
    $record.commands.revParse = Invoke-Git $Root 'rev-parse --show-toplevel --git-common-dir HEAD "HEAD^{tree}"'
    $record.commands.branch = Invoke-Git $Root 'symbolic-ref --short HEAD'
    if ($record.commands.revParse.exitCode -ne 0 -or $record.commands.branch.exitCode -gt 1) {
        $record.state = 'GIT_BASELINE_QUERY_FAILED'
        return $record
    }
    $refs = ([string]$record.commands.revParse.stdout).Trim() -split '\r?\n'
    $record.gitTopLevel = if ($refs.Count -ge 1) { [IO.Path]::GetFullPath($refs[0]) } else { $null }
    $record.gitCommonDir = if ($refs.Count -ge 2) { [IO.Path]::GetFullPath($(if ([IO.Path]::IsPathRooted($refs[1])) { $refs[1] } else { Join-Path $Root $refs[1] })) } else { $null }
    $record.head = if ($refs.Count -ge 3) { $refs[2] } else { $null }
    $record.tree = if ($refs.Count -ge 4) { $refs[3] } else { $null }
    $record.branch = if ($record.commands.branch.exitCode -eq 0) { ([string]$record.commands.branch.stdout).Trim() } elseif ($record.commands.branch.exitCode -eq 1) { 'DETACHED' } else { 'QUERY_ERROR' }
    $record.targetMatches = ($record.gitTopLevel -and $record.gitCommonDir -and $record.gitTopLevel.TrimEnd('\') -eq [IO.Path]::GetFullPath($Root).TrimEnd('\') -and $record.gitCommonDir.TrimEnd('\') -eq [IO.Path]::GetFullPath($ExpectedCommonDir).TrimEnd('\') -and $record.head -eq $ExpectedHead -and $record.tree -eq $ExpectedTree -and $record.branch -eq $ExpectedBranch)
    if (-not $record.targetMatches) { $record.state = 'REPOSITORY_TARGET_MISMATCH'; return $record }
    $record.commands.status = Invoke-Git $Root 'status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none'
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
    $record.commands.files = Invoke-Git $Root 'ls-files --cached --others --exclude-standard -z'
    if ($record.commands.files.exitCode -ne 0 -or $record.commands.status.exitCode -ne 0) { $record.state = 'GIT_STATUS_OR_INVENTORY_FAILED'; return $record }
    $fileBytes = [Convert]::FromBase64String($record.commands.files.stdoutBase64)
    $record.paths = ([Text.UTF8Encoding]::new($false, $true).GetString($fileBytes)).Split([char]0, [StringSplitOptions]::RemoveEmptyEntries)
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
    try {
        foreach ($relative in $record.paths) {
            $full = [IO.Path]::GetFullPath((Join-Path $Root $relative))
            if (-not $full.StartsWith($rootFull, [StringComparison]::OrdinalIgnoreCase)) { throw "Git path escaped repository: $relative" }
            $cursor = $Root
            $item = $null
            foreach ($part in ($relative -split '[\\/]')) {
                $cursor = Join-Path $cursor $part
                $item = Get-Item -LiteralPath $cursor -Force -ErrorAction Stop
                if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Reparse path in protected inventory: $relative" }
            }
            if ($item.PSIsContainer) { throw "Non-regular object in protected inventory: $relative" }
            $hash = Get-FileHash -LiteralPath $full -Algorithm SHA256 -ErrorAction Stop
            $record.fileInventory.Add([ordered]@{ path = $relative; length = $item.Length; lastWriteTimeUtc = $item.LastWriteTimeUtc.ToString('o'); sha256 = $hash.Hash })
        }
    }
    catch { $record.state = 'PROTECTED_HASH_FAILED'; $record.error = $_.Exception.GetType().FullName + ': ' + $_.Exception.Message; return $record }
    foreach ($name in @('.git\HEAD', '.git\index', '.git\config')) { $record.gitMetadata.Add((Get-FileRecord (Join-Path $Root $name))) }
    $record.gitMetadataAfter = Get-FileRecord (Join-Path $Root '.git\index')
    $record.gitMetadataStates = @($record.gitMetadata | ForEach-Object { $_.state })
    $record.gitMetadataComplete = (@($record.gitMetadataStates | Where-Object { $_ -ne 'PRESENT' }).Count -eq 0 -and $record.gitMetadataBefore.state -eq 'PRESENT' -and $record.gitMetadataAfter.state -eq 'PRESENT')
    $record.indexStable = ($record.gitMetadataBefore.sha256 -eq $record.gitMetadataAfter.sha256)
    if (-not $record.gitMetadataComplete) { $record.state = 'GIT_METADATA_INVALID'; return $record }
    $record.state = if ($record.targetMatches -and $record.indexStable) { 'CAPTURED' } else { 'TARGET_OR_INDEX_MISMATCH' }
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
    $commandSummaries = [ordered]@{}
    foreach ($commandName in $Record.commands.Keys) {
        $command = $Record.commands[$commandName]
        $commandSummaries[$commandName] = [ordered]@{ executable = $command.executable; arguments = $command.arguments; exitCode = $command.exitCode; processId = $command.processId; stdoutTextEncoding = $command.stdoutTextEncoding; stdoutTextCodePage = $command.stdoutTextCodePage; textDecodeNote = $command.textDecodeNote; stdoutSha256 = $command.stdoutSha256; stdoutBase64Length = ([string]$command.stdoutBase64).Length; stderrSha256 = $command.stderrSha256; stderrBase64Length = ([string]$command.stderrBase64).Length }
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
        status = $partialStatus
        gitMetadataBefore = $Record.gitMetadataBefore
        gitMetadata = $Record.gitMetadata
        gitMetadataAfter = $Record.gitMetadataAfter
        indexStable = $Record.indexStable
        fileInventoryRecordCount = @($Record.fileInventory).Count
        fileInventoryIncludedCount = $files.Count
        fileInventoryOmittedCount = [Math]::Max(0, @($Record.fileInventory).Count - $files.Count)
        fileInventory = $files
        error = $Record.error
    }
}

function New-PartialEvidence([string]$Reason, [object]$OriginalStopReason) {
    return [ordered]@{
        task = $Result.task
        manifest = $Result.manifest
        t0Utc = $Result.t0Utc
        t0StopwatchTicks = $Result.t0StopwatchTicks
        captureStatus = 'PARTIAL_EVIDENCE'
        partialReason = $Reason
        originalStopReason = $OriginalStopReason
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
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    $currentProcess = [Diagnostics.Process]::GetCurrentProcess()
    $Result.process = [ordered]@{
        id = $PID
        startTimeUtc = $currentProcess.StartTime.ToUniversalTime().ToString('o')
        executablePath = $currentProcess.MainModule.FileName
        powerShellVersion = $PSVersionTable.PSVersion.ToString()
        hostName = $Host.Name
    }
    $Result.identity = [ordered]@{
        name = $identity.Name
        sid = $identity.User.Value
        authenticationType = $identity.AuthenticationType
        impersonationLevel = [string]$identity.ImpersonationLevel
        isSystem = $identity.IsSystem
        isAdministrator = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        whoami = (Invoke-CapturedProcess $WhoAmIExe '/all')
    }
    $identity.Dispose()
    if ($Result.identity.whoami.exitCode -ne 0) { $Result.stopReason = 'WHOAMI_QUERY_FAILED' }
    elseif ($Result.identity.name -ne $ExpectedUser -or $Result.identity.sid -ne $ExpectedSid) { $Result.stopReason = 'IDENTITY_MISMATCH' }
    else {
        $Result.classifications.hostIdentity = 'PASS_WITH_EVIDENCE'
        $repoRecord = Get-RepositoryRecord 'main' $Repo $RepoHead $RepoTree 'main' 'G:\CODEX\New Manga\.git'
        $Result.repository.main = $repoRecord
        if ($repoRecord.state -ne 'CAPTURED') { $Result.stopReason = 'MAIN_REPOSITORY_BASELINE_OR_HASH_FAILED' }
    }
    if (-not $Result.stopReason) {
        $scratchRecord = Get-RepositoryRecord 'scratch' $Scratch $ScratchHead $ScratchTree 'DETACHED' 'G:\CODEX\P02-scratch-build-source\.git'
        $Result.repository.scratch = $scratchRecord
        if ($scratchRecord.state -ne 'CAPTURED') { $Result.stopReason = 'SCRATCH_BASELINE_OR_HASH_FAILED' }
    }
    if (-not $Result.stopReason) {
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
                futureLpacMappingState = 'NOT_APPLIED_IN_R1; verify exact new environment in P02PRE-R2'
            }
        }
        else { $Result.homeEnvironmentCheck = [ordered]@{ state = 'UNPROVABLE'; missingVariable = 'HOMEDRIVE/HOMEPATH/USERPROFILE'; futureLpacMappingState = 'NOT_APPLIED_IN_R1' } }
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
        $werDirs = @('C:\Users\49745\AppData\Local\CrashDumps','C:\ProgramData\Microsoft\Windows\WER\ReportQueue','C:\ProgramData\Microsoft\Windows\WER\ReportArchive')
        foreach ($path in $werDirs) { $Result.wer[$path] = Get-ExactDirectoryRecord $path $false }
        $Result.wer.registry = Get-WerRecord
        $Result.wer.unqueriedPolicyScope = [ordered]@{ perImageSubkeys = 'NOT_ENUMERATED / UNPROVABLE'; otherValues = 'NOT_ENUMERATED / UNPROVABLE'; hkcuInterpretation = 'Historical observation candidate only; not treated as effective LocalDumps policy.' }
        foreach ($key in @('AGENTS.md','doc/REBASELINE_PLAN.md','doc/00_INDEX.md','doc/STATUS.md','doc/09_COLLABORATION.md','doc/tasks/P02.md','doc/tasks/P02PRE-R0S6.md','doc/tasks/P02PRE-R1.md','verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md','verification/P02/p02pre-r1-manifest-20261011.md','verification/P02/p02pre-r1-capture.ps1','verification/P02/p02pre-r0s6-checkpoint-20261011.md')) {
            $Result.protectedHashes[$key] = Get-FileRecord (Join-Path $Repo $key)
        }
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
        $Result.aclStability = [ordered]@{
            comparisons = $aclComparisons
            changedCount = @($aclComparisons | Where-Object { $_.state -eq 'CHANGED' }).Count
            queryErrorCount = @($aclComparisons | Where-Object { $_.state -match 'QUERY_ERROR|PATH_QUERY_ERROR' }).Count
            notComparableCount = @($aclComparisons | Where-Object { $_.state -eq 'NOT_COMPARABLE' }).Count
            unverifiableCount = @($aclComparisons | Where-Object { $_.state -eq 'UNVERIFIABLE' }).Count
            scope = 'Before/after endpoint owner, SDDL and component attributes only; not proof against transient changes or file-ID/hardlink/ADS changes.'
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
        $invalidHashCount = @($hashRecords | Where-Object { $_.state -ne 'PRESENT' }).Count
        $repoFailureCount = @($repoRecords | Where-Object { $_.state -ne 'CAPTURED' }).Count
        $aclChangedCount = $Result.aclStability.changedCount
        $aclQueryErrorCount = $Result.aclStability.queryErrorCount
        $aclNotComparableCount = $Result.aclStability.notComparableCount
        $aclUnverifiableCount = $Result.aclStability.unverifiableCount
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
            repositoryStatusRawBytes = (@($repoRecords | ForEach-Object { $_.status.rawByteCount } | Measure-Object -Sum).Sum)
            aclEndpointComparisons = $aclComparisons.Count
            aclChangesObserved = $aclChangedCount
            aclRecheckErrors = $aclQueryErrorCount
            aclNotComparable = $aclNotComparableCount
            aclUnverifiable = $aclUnverifiableCount
            pathAclUnverifiable = $pathAclUnverifiableCount
            nonemptyScratchOutputLeaves = $nonemptyOutputCount
            environmentVariables = $envNames.Count
            queryErrorCount = ($queryErrorCount + $repoFailureCount + $aclQueryErrorCount + $invalidHashCount + [int]($Result.identity.whoami.exitCode -ne 0))
            outputLeafState = if ($nonemptyOutputCount -gt 0) { 'FAILED_FOR_REUSE; no leaf changed' } else { 'EMPTY_OR_ABSENT_AT_CAPTURE' }
            accessClosure = 'UNPROVABLE_NOT_MONITORED_IN_R1'
        }
        $Result.classifications.hostPathSnapshots = if ($pathQueryErrorCount -gt 0 -or @($pathRecords | Where-Object { $_.state -in @('REPARSE_POINT','NOT_DIRECTORY') }).Count -gt 0 -or $missingInputRootCount -gt 0) { 'FAILED' } elseif ($pathAclUnverifiableCount -gt 0) { 'UNPROVABLE' } else { 'PASS_WITH_EVIDENCE' }
        $Result.classifications.hostAclSnapshots = if ($aclChangedCount -gt 0 -or $aclQueryErrorCount -gt 0) { 'FAILED' } elseif ($aclNotComparableCount -gt 0 -or $aclUnverifiableCount -gt 0) { 'UNPROVABLE' } else { 'PASS_WITH_EVIDENCE' }
        $Result.classifications.effectiveAccessAndWriteClosure = 'REQUIRES_ACTIVE_TEST'
        $Result.classifications.hostHomeConsistency = $homeState
        $Result.classifications.tempCache = 'UNPROVABLE'
        $Result.classifications.werQueriedFields = if ($werQueryErrorCount -eq 0) { 'PASS_WITH_EVIDENCE' } else { 'FAILED' }
        $Result.classifications.fullProtectedInvariantsAndDynamicWriteClosure = 'REQUIRES_ACTIVE_TEST'
        if ($queryErrorCount -gt 0 -or $invalidPathCount -gt 0 -or $missingInputRootCount -gt 0 -or $invalidHashCount -gt 0 -or $repoFailureCount -gt 0 -or $aclChangedCount -gt 0 -or $aclQueryErrorCount -gt 0 -or $aclUnverifiableCount -gt 0 -or $homeState -eq 'FAILED') { $Result.stopReason = 'QUERY_ERROR_OR_ACL_PATH_DRIFT_OR_HASH_INCOMPLETE' }
    }
}
catch {
    $Result.errors.Add(($_.Exception.GetType().FullName + ': ' + $_.Exception.Message))
    if ([string]::IsNullOrEmpty($Result.stopReason)) { $Result.stopReason = 'CAPTURE_EXCEPTION' }
}

$json = $null
try { $json = ConvertTo-Json -InputObject $Result -Depth 16 }
catch {
    $Result.errors.Add(('JSON serialization: ' + $_.Exception.GetType().FullName + ': ' + $_.Exception.Message))
    if ([string]::IsNullOrEmpty($Result.stopReason)) { $Result.stopReason = 'EVIDENCE_SERIALIZATION_FAILED' }
    $json = ConvertTo-Json -InputObject ([ordered]@{ task = $Result.task; t0Utc = $Result.t0Utc; captureStatus = 'PARTIAL_EVIDENCE'; stopReason = $Result.stopReason; errors = $Result.errors }) -Depth 4
}
$maxEvidenceBytes = 67108864
if ([Text.Encoding]::UTF8.GetByteCount($json) -gt $maxEvidenceBytes) {
    $originalStopReason = $Result.stopReason
    if ([string]::IsNullOrEmpty($Result.stopReason)) { $Result.stopReason = 'EVIDENCE_SIZE_LIMIT_PARTIAL' }
    $partial = New-PartialEvidence 'Full JSON exceeded 64 MiB; bounded partial records retained, full per-file inventory omitted.' $originalStopReason
    $json = ConvertTo-Json -InputObject $partial -Depth 16
    if ([Text.Encoding]::UTF8.GetByteCount($json) -gt $maxEvidenceBytes) {
        $json = ConvertTo-Json -InputObject ([ordered]@{ task = $Result.task; manifest = $Result.manifest; t0Utc = $Result.t0Utc; captureStatus = 'PARTIAL_EVIDENCE'; partialReason = 'Bounded partial JSON also exceeded 64 MiB.'; originalStopReason = $originalStopReason; stopReason = $Result.stopReason; fullEvidenceBytesExceeded = $maxEvidenceBytes; omittedFullInventory = $true; repositoryStates = [ordered]@{ main = $Result.repository.main.state; scratch = $Result.repository.scratch.state }; classifications = $Result.classifications; summary = $Result.summary; errors = $Result.errors }) -Depth 6
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
    $writeError = "EVIDENCE_WRITE_FAILED; stopReason=$($Result.stopReason); no retry or cleanup; target may contain partial bytes: $($_.Exception.GetType().FullName): $($_.Exception.Message)"
    $Result.errors.Add($writeError)
    throw $writeError
}

if ($Result.stopReason) { throw "P02PRE-R1 stopped: $($Result.stopReason); evidence=$EvidencePath" }
Write-Output "P02PRE-R1 capture complete; evidence=$EvidencePath"
