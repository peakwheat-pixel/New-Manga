# Root-owned Round6 executor (attempt 4). Requires independent attempt4 review and adjudication before invocation.
# No cleanup, retry, rollback, build, capture or system AC is authorized by this file.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'G:\CODEX\New Manga'
$Owner = 'C:\Users\49745\.codex\worktrees\p02pre-r1h-codex'
$Pwsh = 'C:\Program Files\PowerShell\7\pwsh.exe'
$Git = 'C:\Program Files\Git\cmd\git.exe'
$Prefix = 'verification/P02/'
$Paths = [ordered]@{
    destination = $Prefix + 'p02pre-r1h-selfcheck.ps1'
    stage = $Prefix + 'p02pre-r1h-selfcheck-round6-stage-20261012.ps1'
    recovery = $Prefix + 'p02pre-r1h-selfcheck-round5-recovery-20261012.ps1'
    apiBackup = $Prefix + 'p02pre-r1h-selfcheck-round5-integrated-backup-20261012.ps1'
    handoff = $Prefix + 'p02pre-r1h-round6-handoff-20261012.md'
    execution = $Prefix + 'p02pre-r1h-integration-round6-execution-20261012.json'
    selfcheckEvidence = $Prefix + 'p02pre-r1h-selfcheck-round6-20261012.json'
    engineEvidence = $Prefix + 'p02pre-r1h-engine-preflight-round6-20261012.json'
}
$NewKeys = @('stage','recovery','apiBackup','handoff','execution','selfcheckEvidence','engineEvidence')
$OldHash = '977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA'
$NewHash = '6BD9160854275DA94C61B8FC48B180CD16368AF56C2AF7D63D616490A1AB85A9'
$CaptureHash = '0BD41442800BA2336B277C3F8C16C41D4DDF983B2B5D5967378A9EF564078DA3'
$HandoffHash = '700B79F3FA01308DFFEC374A4FFB92DAC69C2FD8355DE623F6A250E9F1511658'
$IndexHash = '214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C'
$ExpectedSddl = 'O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;0x1301bf;;;S-1-5-21-2196946971-914346751-4210154634-1003)(A;ID;0x1301bf;;;S-1-5-21-884840046-396652784-710274065-85489587)(A;ID;FA;;;BA)(A;ID;FA;;;SY)(A;ID;0x1301bf;;;AU)(A;ID;0x1200a9;;;BU)'
$Utf8 = [Text.UTF8Encoding]::new($false, $true)
$EvidenceStream = $null
$ReplaceCalls = 0
$ProcessClosureBlocked = $false
$Phase = 'PRE_WRITE'
$Evidence = [ordered]@{
    schema = 'P02PRE-R1H-round6-attempt4'; state = 'NOT_RUN'; phase = $Phase
    startedUtc = [DateTime]::UtcNow.ToString('o'); finishedUtc = $null
    historicalDeviations = @(
        'Prior helper used reserved $args and launched Git without argv: historical deviation, not PASS.'
        'Prior status before execution evidence CreateNew: out-of-protocol diagnostic, not S0/S1/S2/S3 and not PASS.'
    )
    gates = [ordered]@{
        private_registry_absence = 'UNPROVABLE'; TechnicalGate = 'NOT_SATISFIED'
        OwnerRiskAcceptance = 'APPROVED'; GateDisposition = 'WAIVED_BY_OWNER'
        BuildAuthorization = 'AUTHORIZED_WITH_EXCEPTION'
        residual = 'technical condition unmet; user explicitly accepted residual risk'
        BuildGate = 'BLOCKED'; HardBuildBarrier = 'EFFECTIVE'; BuildCargo = 'NOT_RUN'
        systemAC1_AC7 = 'BLOCKED / NOT_RUN'
    }
    integration = 'NOT_RUN'; parser = 'NOT_RUN'; selfcheck = 'NOT_RUN'; capability = 'NOT_RUN'
    processObservationLimit = 'Toolhelp32 snapshots cannot exclude transient processes shorter than the sampling interval.'
    observationRaceLimit = 'Narrow non-atomic observation window between S2 status and subsequent destination/recovery/backup hash/ACL/stream assertions is an evidence limitation; atomic snapshot is not claimed.'
    childTimeoutLimit = 'No total child timeout: executor waits indefinitely on a hung child process; live children are not killed and no automatic retry is attempted.'
    nativeInteropLimit = 'P/Invoke signatures, PROCESSENTRY32W offsets, BOOL marshalling and SetLastError metadata were reviewed as text only. Reflection.Emit invocation and Marshal.GetLastPInvokeError behavior are dynamically NOT_VERIFIED; any failed or ambiguous observation blocks execution.'
    metadataLimits = 'Attributes, timestamps and file identity preservation are NOT_VERIFIED.'
    processes = [Collections.Generic.List[object]]::new()
    checks = [Collections.Generic.List[object]]::new()
    snapshots = [ordered]@{}; statusDeltas = [Collections.Generic.List[object]]::new()
    failure = $null; failureActualState = [Collections.Generic.List[object]]::new()
}

function Require([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw [InvalidOperationException]::new($Message) }
}
function FullPath([string]$Relative) {
    Require ($Paths.Values -ccontains $Relative -or $Relative -ceq ($Prefix + 'p02pre-r1h-capture.ps1') -or $Relative -ceq ($Prefix + 'p02pre-r1h-handoff-20261012.md')) 'Unlisted project path.'
    return [IO.Path]::GetFullPath([IO.Path]::Combine($Root, $Relative))
}
function HashBytes([byte[]]$Bytes) { return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)) }
function ByteEvidence([byte[]]$Bytes) {
    return [ordered]@{ bytes = $Bytes.Length; sha256 = HashBytes $Bytes; rawBase64 = [Convert]::ToBase64String($Bytes) }
}
function ExceptionEvidence($Failure) {
    return [ordered]@{ type = $Failure.Exception.GetType().FullName; message = $Failure.Exception.Message; hresult = $Failure.Exception.HResult; detail = $Failure.ToString() }
}
function SaveExecution {
    Require ($null -ne $EvidenceStream) 'Execution evidence has not been created.'
    $Evidence.phase = $Phase
    $Evidence.replaceCalls = $ReplaceCalls
    $json = ConvertTo-Json -InputObject $Evidence -Depth 64 -Compress
    $bytes = $Utf8.GetBytes($json)
    $EvidenceStream.Position = 0
    $EvidenceStream.SetLength(0)
    $EvidenceStream.Write($bytes, 0, $bytes.Length)
    $EvidenceStream.Flush($true)
}
function AssertChain([string]$Path, [bool]$LeafMayBeAbsent = $false) {
    $full = [IO.Path]::GetFullPath($Path)
    Require ($full -notmatch '(?i)(^|[\\/])\.tmp\.driveupload([\\/]|$)') 'Excluded path is unavailable.'
    $cursor = $full
    $isLeaf = $true
    while ($cursor) {
        try {
            $attributes = [IO.File]::GetAttributes($cursor)
            Require (($attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) "Reparse component: $cursor"
            if (-not $isLeaf) { Require (($attributes -band [IO.FileAttributes]::Directory) -ne 0) "Non-directory ancestor: $cursor" }
        } catch [IO.FileNotFoundException] {
            Require ($isLeaf -and $LeafMayBeAbsent) "Missing required path: $cursor"
        } catch [IO.DirectoryNotFoundException] {
            throw
        }
        $parent = [IO.Path]::GetDirectoryName($cursor)
        if (-not $parent -or $parent -ceq $cursor) { break }
        $cursor = $parent
        $isLeaf = $false
    }
    return $full
}
function AssertAbsent([string]$Path) {
    $null = AssertChain $Path $true
    try { $null = [IO.File]::GetAttributes($Path) } catch [IO.FileNotFoundException] { return }
    throw "Output collision: $Path"
}
function FileState([string]$Path, [bool]$AllowUnknownStreams = $false) {
    $null = AssertChain $Path
    $item = Get-Item -LiteralPath $Path -Force
    Require ($item -is [IO.FileInfo] -and -not $item.PSIsContainer) "Not an ordinary file: $Path"
    $bytes = [IO.File]::ReadAllBytes($Path)
    $acl = (Get-Acl -LiteralPath $Path).Sddl
    $streams = @(Get-Item -LiteralPath $Path -Stream * -ErrorAction Stop)
    if (-not $AllowUnknownStreams) {
        Require ($streams.Count -eq 1 -and $streams[0].Stream -ceq ':$DATA') "Unknown stream: $Path"
        Require ($streams[0].Length -eq $bytes.Length) "Stream length mismatch: $Path"
    }
    return [ordered]@{
        path = $Path; exists = $true; type = $item.GetType().FullName
        attributes = $item.Attributes.ToString(); bytes = $bytes.Length; sha256 = HashBytes $bytes
        aclSddl = $acl; streams = @($streams | ForEach-Object { [ordered]@{ name=$_.Stream; bytes=$_.Length; sha256=if ($_.Stream -ceq ':$DATA') { HashBytes $bytes } else { 'NOT_READ_UNKNOWN_STREAM' } } })
    }
}
function AssertPin([string]$Path, [long]$Length, [string]$Hash) {
    $state = FileState $Path
    Require ($state.bytes -eq $Length -and $state.sha256 -ceq $Hash) "Pin mismatch: $Path"
    return $state
}
function ParentState([string]$Path) {
    $parent = [IO.Path]::GetDirectoryName($Path)
    $null = AssertChain $parent
    $item = Get-Item -LiteralPath $parent -Force
    Require ($item -is [IO.DirectoryInfo]) "Not an ordinary parent directory: $parent"
    $streams = @(Get-Item -LiteralPath $parent -Stream * -ErrorAction Stop)
    Require (@($streams | Where-Object { $_.Stream -cne ':$DATA' -or $_.Length -ne 0 }).Count -eq 0) "Unknown directory stream: $parent"
    return [ordered]@{ path = $parent; type = $item.GetType().FullName; aclSddl = (Get-Acl -LiteralPath $parent).Sddl; streams = @($streams | ForEach-Object { [ordered]@{ name=$_.Stream; bytes=$_.Length } }) }
}
function AssertHost {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    try {
        $principal = [Security.Principal.WindowsPrincipal]::new($identity)
        $state = [ordered]@{
            pid = $PID; executable = [Environment]::ProcessPath
            argv = @([Environment]::GetCommandLineArgs())
            cwd = [Environment]::CurrentDirectory; psLocation = (Get-Location).Path
            version = $PSVersionTable.PSVersion.ToString(); edition = $PSVersionTable.PSEdition
            languageMode = $ExecutionContext.SessionState.LanguageMode.ToString()
            user = $identity.Name; sid = $identity.User.Value
            administrator = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        }
        Require ($state.executable -ceq $Pwsh -and $state.version -ceq '7.6.6' -and $state.edition -ceq 'Core' -and $state.languageMode -ceq 'FullLanguage') 'Host executable/version/edition/language mismatch.'
        Require ($state.user -ceq 'HOME-MY\49745' -and $state.sid -ceq 'S-1-5-21-2196946971-914346751-4210154634-1001' -and -not $state.administrator) 'Host identity mismatch.'
        Require ($state.psLocation -ceq $Root -and $state.cwd -ceq $Root) 'Root host CWD mismatch.'
        return $state
    } finally { $identity.Dispose() }
}

# Pure helper returning flat Toolhelp method definitions with named fields.
function GetToolhelpDefinitions {
    return @(
        [pscustomobject]@{
            name = 'CreateToolhelp32Snapshot'
            returnType = [IntPtr]
            parameterTypes = [Type[]]@([uint32], [uint32])
        },
        [pscustomobject]@{
            name = 'Process32FirstW'
            returnType = [bool]
            parameterTypes = [Type[]]@([IntPtr], [byte[]])
        },
        [pscustomobject]@{
            name = 'Process32NextW'
            returnType = [bool]
            parameterTypes = [Type[]]@([IntPtr], [byte[]])
        },
        [pscustomobject]@{
            name = 'CloseHandle'
            returnType = [bool]
            parameterTypes = [Type[]]@([IntPtr])
        }
    )
}

# Reflection.Emit creates in-memory declarations; their runtime ABI/error propagation remains NOT_VERIFIED.
function InitializeProcessObserver {
    $assembly = [Reflection.Emit.AssemblyBuilder]::DefineDynamicAssembly([Reflection.AssemblyName]::new('P02Round6Toolhelp'), [Reflection.Emit.AssemblyBuilderAccess]::Run)
    $module = $assembly.DefineDynamicModule('Toolhelp')
    $builder = $module.DefineType('P02Round6Toolhelp.Native', [Reflection.TypeAttributes]::Public -bor [Reflection.TypeAttributes]::Sealed -bor [Reflection.TypeAttributes]::Abstract)
    $definitions = GetToolhelpDefinitions
    foreach ($def in $definitions) {
        $method = $builder.DefineMethod($def.name, [Reflection.MethodAttributes]::Public -bor [Reflection.MethodAttributes]::Static -bor [Reflection.MethodAttributes]::PinvokeImpl, [Reflection.CallingConventions]::Standard, $def.returnType, $def.parameterTypes)
        $method.SetImplementationFlags($method.GetMethodImplementationFlags() -bor [Reflection.MethodImplAttributes]::PreserveSig)
        $attributeType = [Runtime.InteropServices.DllImportAttribute]
        $fields = [Reflection.FieldInfo[]]@($attributeType.GetField('SetLastError'),$attributeType.GetField('ExactSpelling'),$attributeType.GetField('CharSet'),$attributeType.GetField('CallingConvention'))
        $attribute = [Reflection.Emit.CustomAttributeBuilder]::new($attributeType.GetConstructor([Type[]]@([string])),[object[]]@('kernel32.dll'),$fields,[object[]]@($true,$true,[Runtime.InteropServices.CharSet]::Unicode,[Runtime.InteropServices.CallingConvention]::Winapi))
        $method.SetCustomAttribute($attribute)
        if ($def.name -like 'Process32*') { $null = $method.DefineParameter(2, [Reflection.ParameterAttributes]::In -bor [Reflection.ParameterAttributes]::Out, 'entry') }
    }
    $script:Native = $builder.CreateType()
    $script:KnownChildren = [Collections.Generic.Dictionary[int,string]]::new()
    try { $null = ProcessSnapshot } catch { $script:ProcessClosureBlocked=$true; throw }
}
function ProcessSnapshot {
    $snapshot = $Native.GetMethod('CreateToolhelp32Snapshot').Invoke($null, @([uint32]2, [uint32]0))
    if ($snapshot -eq [IntPtr]::new(-1) -or $snapshot -eq [IntPtr]::Zero) { throw [ComponentModel.Win32Exception]::new([Runtime.InteropServices.Marshal]::GetLastPInvokeError(),'Toolhelp32 snapshot failed.') }
    try {
        $size = if ([IntPtr]::Size -eq 8) { 568 } else { 556 }
        $parentOffset = if ([IntPtr]::Size -eq 8) { 32 } else { 24 }
        $nameOffset = if ([IntPtr]::Size -eq 8) { 44 } else { 36 }
        $entry = [byte[]]::new($size)
        [BitConverter]::GetBytes([uint32]$size).CopyTo($entry,0)
        $result = [Collections.Generic.List[object]]::new()
        $ok = $Native.GetMethod('Process32FirstW').Invoke($null, @($snapshot, $entry))
        if (-not $ok) { throw [ComponentModel.Win32Exception]::new([Runtime.InteropServices.Marshal]::GetLastPInvokeError(),'Toolhelp32 first process query failed.') }
        while ($ok) {
            $result.Add([ordered]@{ pid = [BitConverter]::ToInt32($entry,8); parentPid = [BitConverter]::ToInt32($entry,$parentOffset); executable = [Text.Encoding]::Unicode.GetString($entry,$nameOffset,520).Split([char]0)[0] })
            $ok = $Native.GetMethod('Process32NextW').Invoke($null, @($snapshot, $entry))
            if (-not $ok) {
                $nativeError=[Runtime.InteropServices.Marshal]::GetLastPInvokeError()
                if ($nativeError -ne 18) { throw [ComponentModel.Win32Exception]::new($nativeError,'Toolhelp32 enumeration failed before end of snapshot.') }
            }
        }
        # A second snapshot must still contain this root; empty/unknown attribution is never accepted.
        Require (@($result | Where-Object { $_.pid -eq $PID }).Count -eq 1) 'Root PID missing or ambiguous in process snapshot.'
        return ,$result.ToArray()
    } finally {
        Require ([bool]$Native.GetMethod('CloseHandle').Invoke($null,@($snapshot))) 'Toolhelp32 handle close failed.'
    }
}

# Pure helper for process-record selection and attribution validation.
# Prelaunch sentinel is represented by $null or positive child PID; PID 0 cannot be used as child sentinel.
function SelectProcessRecords($Snapshot, [int]$RootPid, $KnownChildren, [Nullable[int]]$ExpectedChildPid = $null) {
    Require ($RootPid -gt 0) 'Root PID must be positive.'
    Require ($null -eq $ExpectedChildPid -or $ExpectedChildPid -gt 0) 'Expected child PID must be positive or null.'
    $related = [Collections.Generic.HashSet[int]]::new()
    $null = $related.Add($RootPid)
    if ($null -ne $KnownChildren) {
        foreach ($knownPid in $KnownChildren.Keys) { $null = $related.Add([int]$knownPid) }
    }
    $changed = $true
    while ($changed) {
        $changed = $false
        foreach ($entry in $Snapshot) {
            if ($related.Contains($entry.parentPid) -and $related.Add($entry.pid)) { $changed = $true }
        }
    }
    $observed = @($Snapshot | Where-Object { $related.Contains($_.pid) -or ($null -ne $ExpectedChildPid -and $_.pid -eq $ExpectedChildPid) })
    foreach ($entry in $observed) {
        if ($entry.pid -eq $RootPid) { continue }
        Require ($null -ne $ExpectedChildPid -and $entry.pid -eq $ExpectedChildPid -and $entry.parentPid -eq $RootPid -and $null -ne $KnownChildren -and $KnownChildren.ContainsKey($entry.pid)) 'Unlisted child/descendant or ambiguous PID ownership observed.'
        Require ($entry.executable -ieq [IO.Path]::GetFileName($KnownChildren[$entry.pid])) 'Unexpected child executable observed.'
    }
    return ,$observed
}

function ObserveProcesses($Record, [Nullable[int]]$ChildPid = $null) {
    try {
        $all = ProcessSnapshot
        $observed = SelectProcessRecords $all $PID $KnownChildren $ChildPid
        $Record.observations.Add([ordered]@{ timeUtc = [DateTime]::UtcNow.ToString('o'); entries = $observed })
    } catch { $script:ProcessClosureBlocked=$true; throw }
}
function InvokeChild([string]$Executable, [string]$Cwd, [string[]]$Argv, [int[]]$AllowedExit = @(0)) {
    $record = $null
    $process = $null
    $stdout = $null
    $stderr = $null
    $succeeded = $false
    try {
        Require (-not $ProcessClosureBlocked) 'Process closure already blocked; no child may start.'
        Require ($Executable -ceq $Git -or $Executable -ceq $Pwsh) 'Unlisted executable.'
        Require ($Cwd -ceq $Root -or ($Executable -ceq $Git -and $Cwd -ceq $Owner)) 'Unlisted child CWD.'
        $record = [ordered]@{ executable = $Executable; cwd = $Cwd; argv = @($Argv); pid = $null; startedUtc = [DateTime]::UtcNow.ToString('o'); finishedUtc = $null; stdout = $null; stderr = $null; exit = $null; error = $null; lifecycle='NOT_STARTED'; outputCaptureState='NOT_STARTED'; observations = [Collections.Generic.List[object]]::new(); removedGitEnvironment = @() }
        $Evidence.processes.Add($record)
        $start = [Diagnostics.ProcessStartInfo]::new()
        $start.FileName = $Executable; $start.WorkingDirectory = $Cwd
        $start.UseShellExecute = $false; $start.CreateNoWindow = $true
        $start.RedirectStandardOutput = $true; $start.RedirectStandardError = $true
        foreach ($argument in $Argv) { $start.ArgumentList.Add($argument) }
        $contextNames = @('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_PREFIX','GIT_CEILING_DIRECTORIES','GIT_EXTERNAL_DIFF')
        $removed = [Collections.Generic.List[string]]::new()
        $contextInherited = $false
        foreach ($key in @($start.Environment.Keys)) {
            if ($contextNames -contains $key -or $key -like 'GIT_CONFIG*' -or $key -like 'GIT_TRACE*') {
                if ($contextNames -contains $key -or $key -like 'GIT_CONFIG*') { $contextInherited = $true }
                $removed.Add($key); $null = $start.Environment.Remove($key)
            }
        }
        $record.removedGitEnvironment = $removed.ToArray()
        Require (-not $contextInherited) 'Inherited Git context/config override: child not launched; names recorded, values withheld.'
        $start.Environment['GIT_OPTIONAL_LOCKS'] = '0'; $start.Environment['GIT_TERMINAL_PROMPT'] = '0'
        $process = [Diagnostics.Process]::new(); $process.StartInfo = $start
        $stdout = [IO.MemoryStream]::new(); $stderr = [IO.MemoryStream]::new()
        ObserveProcesses $record $null
        Require ($process.Start()) 'Child failed to start.'
        $record.pid = $process.Id; $KnownChildren[$process.Id]=$Executable
        $record.lifecycle='RUNNING'; $record.outputCaptureState='PARTIAL_UNCLOSED'
        $outTask = $process.StandardOutput.BaseStream.CopyToAsync($stdout)
        $errTask = $process.StandardError.BaseStream.CopyToAsync($stderr)
        do { ObserveProcesses $record $process.Id } while (-not $process.WaitForExit(10))
        ObserveProcesses $record $process.Id
        $record.lifecycle='EXITED'; $record.exit=$process.ExitCode
        if (-not [Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($outTask,$errTask),5000)) {
            $script:ProcessClosureBlocked=$true
            throw 'Unclosed stdout/stderr pipe or unexpected surviving descendant.'
        }
        $record.exit = $process.ExitCode
        $outBytes = $stdout.ToArray(); $errBytes = $stderr.ToArray()
        $record.stdout = ByteEvidence $outBytes; $record.stderr = ByteEvidence $errBytes
        $record.outputCaptureState='COMPLETE'
        Require ($AllowedExit -contains $record.exit) "Child exit $($record.exit): $Executable"
        if ($Executable -ceq $Git) { Require ($errBytes.Length -eq 0) 'Unexpected Git stderr.' }
        $succeeded = $true
        return [ordered]@{ record = $record; bytes = $outBytes; text = $Utf8.GetString($outBytes) }
    } catch {
        $script:ProcessClosureBlocked = $true
        if ($null -ne $record) {
            $record.error = ExceptionEvidence $_
            if ($null -ne $stdout) { try { $record.stdout = ByteEvidence ($stdout.ToArray()) } catch { } }
            if ($null -ne $stderr) { try { $record.stderr = ByteEvidence ($stderr.ToArray()) } catch { } }
            if ($record.pid -and $null -ne $process) {
                try { if ($process.HasExited) { $record.exit = $process.ExitCode } } catch { }
            }
        }
        throw
    } finally {
        if (-not $succeeded) {
            $script:ProcessClosureBlocked = $true
        }
        if ($null -ne $record) {
            try { $record.finishedUtc = [DateTime]::UtcNow.ToString('o') } catch { }
        }
        # Live children are not killed or retried; their unknown state blocks all subsequent writes.
        if ($null -ne $process) { try { $process.Dispose() } catch { } }
        if ($null -ne $stdout) { try { $stdout.Dispose() } catch { } }
        if ($null -ne $stderr) { try { $stderr.Dispose() } catch { } }
    }
}
function InvokeGit([string]$Cwd, [string[]]$GitArgv, [int[]]$AllowedExit = @(0)) {
    $argv = [string[]]@('--no-pager','-c','core.fsmonitor=false','-c','core.hooksPath=NUL') + $GitArgv
    return InvokeChild $Git $Cwd $argv $AllowedExit
}
function GitValue([string]$Cwd, [string[]]$GitArgv) {
    $result = InvokeGit $Cwd $GitArgv
    Require ($result.bytes.Length -gt 0 -and $result.text -notmatch '\x00') 'Invalid Git identity output.'
    return $result.text.TrimEnd([char[]]@([char]13,[char]10))
}
function NormalPath([string]$Path, [string]$Cwd) {
    return [IO.Path]::GetFullPath([IO.Path]::Combine($Cwd,$Path)).TrimEnd([char]'\').Replace('/','\')
}
function AssertRefs {
    foreach ($cwd in @($Root,$Owner)) {
        $isOwner = $cwd -ceq $Owner
        $branch = GitValue $cwd @('symbolic-ref','--short','HEAD')
        $top = GitValue $cwd @('rev-parse','--show-toplevel')
        $common = GitValue $cwd @('rev-parse','--git-common-dir')
        $head = GitValue $cwd @('rev-parse','HEAD')
        $tree = GitValue $cwd @('rev-parse','HEAD^{tree}')
        $expectedBranch = if ($isOwner) { 'agent/codex/P02PRE-R1H' } else { 'main' }
        $expectedHead = if ($isOwner) { 'c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d' } else { 'cddff58469b56e181019a8ddfeade80684bc7eb9' }
        $expectedTree = if ($isOwner) { '96e7273ddd5fd27bee567bba27f19453cabe0842' } else { 'c25d051a4b9a0bd9773b50170e100f575ea19f2b' }
        Require ($branch -ceq $expectedBranch -and $head -ceq $expectedHead -and $tree -ceq $expectedTree) 'Frozen refs mismatch.'
        Require ((NormalPath $top $cwd) -ceq $cwd -and (NormalPath $common $cwd) -ceq ($Root + '\.git')) 'Git repository identity mismatch.'
        $parent = $null
        if ($isOwner) {
            $parent = GitValue $cwd @('rev-parse','HEAD^')
            Require ($parent -ceq 'dd5d2e3bc8e0702da9d059131f6364a997897661') 'Owner parent mismatch.'
        }
        $Evidence.checks.Add([ordered]@{ phase = $Phase; refs = [ordered]@{ cwd = $cwd; branch = $branch; top = $top; common = $common; head = $head; tree = $tree; parent = $parent } })
    }
}
function IndexState([bool]$EnforceFrozen = $true) {
    $path = $Root + '\.git\index'
    $null = AssertChain $path
    $bytes = [IO.File]::ReadAllBytes($path)
    $hash = HashBytes $bytes
    $state = ByteEvidence $bytes
    $state.matchesFrozen = $hash -ceq $IndexHash
    if ($EnforceFrozen) { Require $state.matchesFrozen 'Root index changed.' }
    return $state
}
function ReadStatus([string]$Name, [string]$Cwd, [bool]$EnforceIndex = $true) {
    Require ($null -ne $EvidenceStream) 'Status forbidden before execution evidence CreateNew.'
    $result = InvokeGit $Cwd @('--no-optional-locks','status','--porcelain=v2','-z','--untracked-files=all','--no-renames','--ignore-submodules=none','--','.',':(exclude).tmp.driveupload')
    $records = [Collections.Generic.List[string]]::new()
    $offset = 0
    for ($i=0; $i -lt $result.bytes.Length; $i++) {
        if ($result.bytes[$i] -eq 0) {
            Require ($i -gt $offset) 'Empty status record.'
            $recordBytes = [byte[]]::new($i-$offset)
            [Array]::Copy($result.bytes,$offset,$recordBytes,0,$recordBytes.Length)
            $decoded = $Utf8.GetString($recordBytes)
            Require ($decoded -match '^(1 |2 |u |\? |! )' -and $decoded -notmatch '(?i)\.tmp\.driveupload') 'Unknown/excluded status record.'
            Require (-not $decoded.StartsWith('2 ') -and -not $decoded.StartsWith('! ')) 'Unexpected rename/ignored status record.'
            $records.Add([Convert]::ToBase64String($recordBytes)); $offset=$i+1
        }
    }
    Require ($offset -eq $result.bytes.Length) 'Status lacks final NUL.'
    $multiset = [Collections.Generic.Dictionary[string,int]]::new([StringComparer]::Ordinal)
    foreach ($record in $records) { if ($multiset.ContainsKey($record)) { $multiset[$record]++ } else { $multiset.Add($record,1) } }
    $state = [ordered]@{ cwd = $Cwd; raw = ByteEvidence $result.bytes; recordCount = $records.Count; recordsBase64 = $records.ToArray(); nulRecordMultiset = $multiset; index = IndexState $EnforceIndex }
    $Evidence.snapshots[$Name] = $state
    return $state
}
function AssertDelta([string]$Before, [string]$After, [string[]]$AddPaths, [bool]$Enforce = $true) {
    $prior = $Evidence.snapshots[$Before].nulRecordMultiset
    $actual = $Evidence.snapshots[$After].nulRecordMultiset
    $expected = [Collections.Generic.Dictionary[string,int]]::new([StringComparer]::Ordinal)
    foreach ($key in $prior.Keys) { $expected.Add($key,$prior[$key]) }
    foreach ($path in $AddPaths) {
        $key = [Convert]::ToBase64String($Utf8.GetBytes('? ' + $path))
        Require (-not $expected.ContainsKey($key)) 'Expected new output already had a baseline status record.'
        $expected.Add($key,1)
    }
    $changes = [Collections.Generic.List[object]]::new()
    $keys = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($key in $prior.Keys) { $null=$keys.Add($key) }; foreach ($key in $actual.Keys) { $null=$keys.Add($key) }
    foreach ($key in $keys) {
        $beforeCount = if ($prior.ContainsKey($key)) { $prior[$key] } else { 0 }
        $afterCount = if ($actual.ContainsKey($key)) { $actual[$key] } else { 0 }
        if ($beforeCount -ne $afterCount) { $changes.Add([ordered]@{ recordBase64=$key; before=$beforeCount; after=$afterCount }) }
    }
    $Evidence.statusDeltas.Add([ordered]@{ before=$Before; after=$After; changes=$changes.ToArray(); allowedAdditions=@($AddPaths); enforced=$Enforce; classification=if ($Enforce) { 'FIXED_EXPECTATION' } else { 'ACTUAL_UNADJUDICATED' } })
    if (-not $Enforce) { return }
    Require ($expected.Count -eq $actual.Count) 'Unexpected status multiset size.'
    foreach ($key in $expected.Keys) { Require ($actual.ContainsKey($key) -and $actual[$key] -eq $expected[$key]) 'Unexpected status multiset delta.' }
}
function PrecheckFiles([bool]$ExecutionExists) {
    $result = [ordered]@{}
    $result.destination = AssertPin (FullPath $Paths.destination) 57648 $OldHash
    Require ($result.destination.attributes -ceq 'Archive' -and $result.destination.aclSddl -ceq $ExpectedSddl) 'Destination attributes/ACL mismatch.'
    $result.source = AssertPin ($Owner + '\verification\P02\p02pre-r1h-selfcheck.ps1') 57812 $NewHash
    $result.ownerCapture = AssertPin ($Owner + '\verification\P02\p02pre-r1h-capture.ps1') 93124 $CaptureHash
    $result.ownerHandoff = AssertPin ($Owner + '\verification\P02\p02pre-r1h-handoff-20261012.md') 3551 $HandoffHash
    $result.rootCapture = AssertPin (FullPath ($Prefix+'p02pre-r1h-capture.ps1')) 93124 $CaptureHash
    $result.rootOldHandoff = AssertPin (FullPath ($Prefix+'p02pre-r1h-handoff-20261012.md')) 8651 '394CCF80E58017798CA2994C0505F2F5B5BB571143D21C655CEFC77B6173520F'
    $result.ownerParent = ParentState ($Owner + '\verification\P02\p02pre-r1h-selfcheck.ps1')
    $result.rootParent = ParentState (FullPath $Paths.destination)
    $result.index = IndexState
    foreach ($key in $NewKeys) {
        if ($key -ceq 'execution' -and $ExecutionExists) { continue }
        AssertAbsent (FullPath $Paths[$key])
    }
    $directory = [IO.Path]::GetDirectoryName((FullPath $Paths.destination))
    foreach ($key in @('stage','recovery','apiBackup')) { Require ([IO.Path]::GetDirectoryName((FullPath $Paths[$key])) -ceq $directory) 'Replacement paths not in same directory.' }
    $volume = [IO.DriveInfo]::new('G:\')
    Require ($volume.IsReady -and $volume.DriveFormat -ceq 'NTFS') 'Replacement volume is not ready NTFS.'
    $result.volume = [ordered]@{ name=$volume.Name; format=$volume.DriveFormat; ready=$volume.IsReady }
    return $result
}
function AssertStable($Before, $After) {
    Require ((ConvertTo-Json -InputObject $Before -Depth 20 -Compress) -ceq (ConvertTo-Json -InputObject $After -Depth 20 -Compress)) 'Frozen file/ACL/stream/parent/index state changed.'
}
function CreateBytes([string]$Path, [byte[]]$Bytes) {
    AssertAbsent $Path
    AssertWriteSafe $Path
    $stream = [IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $stream.Write($Bytes,0,$Bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
    $Evidence.checks.Add([ordered]@{ phase=$Phase; createdFile=AssertPin $Path $Bytes.Length (HashBytes $Bytes) })
}
function AssertWriteSafe([string]$Path) {
    Require (-not $ProcessClosureBlocked) 'Process observation blocked; protected write forbidden.'
    $record=[ordered]@{ path=$Path; phase=$Phase; observations=[Collections.Generic.List[object]]::new() }
    $Evidence.checks.Add($record)
    ObserveProcesses $record $null
}
function ParsePinned([string]$Path, [long]$Length, [string]$Hash) {
    $null = AssertPin $Path $Length $Hash
    $tokens=$null; $errors=$null
    $null = [Management.Automation.Language.Parser]::ParseFile($Path,[ref]$tokens,[ref]$errors)
    return [ordered]@{ path=$Path; errors=@($errors | ForEach-Object { [ordered]@{ id=$_.ErrorId; message=$_.Message; line=$_.Extent.StartLineNumber; column=$_.Extent.StartColumnNumber } }); errorCount=@($errors).Count }
}

try {
    $Evidence.host = AssertHost
    InitializeProcessObserver
    AssertRefs
    $initial = PrecheckFiles $false
    $Evidence.preWrite = $initial
    foreach ($key in $NewKeys) {
        $check = InvokeGit $Root @('check-ignore','--no-index','--quiet','--',$Paths[$key]) @(1)
        Require ($check.bytes.Length -eq 0) 'Unexpected check-ignore stdout.'
    }
    # Recheck all absent outputs immediately before the first CreateNew; no status has run.
    foreach ($key in $NewKeys) { AssertAbsent (FullPath $Paths[$key]) }
    AssertWriteSafe (FullPath $Paths.execution)
    $EvidenceStream = [IO.FileStream]::new((FullPath $Paths.execution),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    $Evidence.state = 'ACTIVE'; SaveExecution
    $Phase='S0'
    $null = ReadStatus 'S0-root' $Root
    $ownerS0 = ReadStatus 'S0-owner' $Owner
    Require ($ownerS0.raw.bytes -eq 0) 'Owner S0 status is not clean.'
    SaveExecution
    $Phase='PRE_STAGE_RECHECK'
    $Evidence.hostRecheck = AssertHost
    AssertRefs
    $preStageOwner = ReadStatus 'pre-stage-owner' $Owner
    Require ($preStageOwner.raw.bytes -eq 0) 'Owner pre-stage status is not clean.'
    $second = PrecheckFiles $true
    AssertStable $initial $second
    $Evidence.preStage=$second; SaveExecution
    # Read only pinned working-tree default bytes, never substitute Git blobs.
    $newBytes=[IO.File]::ReadAllBytes($Owner+'\verification\P02\p02pre-r1h-selfcheck.ps1')
    $oldBytes=[IO.File]::ReadAllBytes((FullPath $Paths.destination))
    $handoffBytes=[IO.File]::ReadAllBytes($Owner+'\verification\P02\p02pre-r1h-handoff-20261012.md')
    Require ($newBytes.Length -eq 57812 -and (HashBytes $newBytes) -ceq $NewHash -and $oldBytes.Length -eq 57648 -and (HashBytes $oldBytes) -ceq $OldHash -and $handoffBytes.Length -eq 3551 -and (HashBytes $handoffBytes) -ceq $HandoffHash) 'Copy source changed.'
    $Phase='CREATE_STAGE_RECOVERY_HANDOFF'
    CreateBytes (FullPath $Paths.stage) $newBytes
    CreateBytes (FullPath $Paths.recovery) $oldBytes
    CreateBytes (FullPath $Paths.handoff) $handoffBytes
    $Phase='S1'
    $null = ReadStatus 'S1-root' $Root
    AssertDelta 'S0-root' 'S1-root' @($Paths.stage,$Paths.recovery,$Paths.handoff)
    $Evidence.S1Files=[ordered]@{
        destination=AssertPin (FullPath $Paths.destination) 57648 $OldHash
        stage=AssertPin (FullPath $Paths.stage) 57812 $NewHash
        recovery=AssertPin (FullPath $Paths.recovery) 57648 $OldHash
        handoff=AssertPin (FullPath $Paths.handoff) 3551 $HandoffHash
    }
    AssertStable $initial.destination $Evidence.S1Files.destination
    AssertStable $initial.rootParent (ParentState (FullPath $Paths.destination))
    AssertStable $initial.rootCapture (AssertPin (FullPath ($Prefix+'p02pre-r1h-capture.ps1')) 93124 $CaptureHash)
    AssertStable $initial.rootOldHandoff (AssertPin (FullPath ($Prefix+'p02pre-r1h-handoff-20261012.md')) 8651 '394CCF80E58017798CA2994C0505F2F5B5BB571143D21C655CEFC77B6173520F')
    AssertStable $initial.source (AssertPin ($Owner+'\verification\P02\p02pre-r1h-selfcheck.ps1') 57812 $NewHash)
    AssertStable $initial.ownerCapture (AssertPin ($Owner+'\verification\P02\p02pre-r1h-capture.ps1') 93124 $CaptureHash)
    AssertStable $initial.ownerHandoff (AssertPin ($Owner+'\verification\P02\p02pre-r1h-handoff-20261012.md') 3551 $HandoffHash)
    AssertStable $initial.ownerParent (ParentState ($Owner+'\verification\P02\p02pre-r1h-selfcheck.ps1'))
    AssertAbsent (FullPath $Paths.apiBackup)
    SaveExecution
    $Phase='REPLACE'
    AssertWriteSafe (FullPath $Paths.destination)
    $destinationPreReplace = AssertPin (FullPath $Paths.destination) 57648 $OldHash
    Require ($destinationPreReplace.attributes -ceq 'Archive' -and $destinationPreReplace.aclSddl -ceq $ExpectedSddl) 'Destination attributes/ACL mismatch immediately before Replace.'
    AssertStable $initial.destination $destinationPreReplace
    $Evidence.checks.Add([ordered]@{ phase=$Phase; preReplaceDestination=$destinationPreReplace })
    $ReplaceCalls++
    [IO.File]::Replace((FullPath $Paths.stage),(FullPath $Paths.destination),(FullPath $Paths.apiBackup))
    $Phase='S2'
    # The S2 status is the first child after Replace; file checks immediately follow.
    $null = ReadStatus 'S2-root' $Root
    $Evidence.S2Files=[ordered]@{
        destination=AssertPin (FullPath $Paths.destination) 57812 $NewHash
        recovery=AssertPin (FullPath $Paths.recovery) 57648 $OldHash
        apiBackup=AssertPin (FullPath $Paths.apiBackup) 57648 $OldHash
        handoff=AssertPin (FullPath $Paths.handoff) 3551 $HandoffHash
        stage='ABSENT'
    }
    AssertAbsent (FullPath $Paths.stage)
    AssertStable $Evidence.S1Files.recovery $Evidence.S2Files.recovery
    AssertStable $Evidence.S1Files.handoff $Evidence.S2Files.handoff
    Require ($Evidence.S2Files.destination.aclSddl -ceq $initial.destination.aclSddl -and $Evidence.S2Files.apiBackup.aclSddl -ceq $initial.destination.aclSddl) 'Replace destination/backup ACL mismatch.'
    AssertStable $initial.destination.streams $Evidence.S2Files.apiBackup.streams
    Require ($Evidence.S2Files.destination.streams.Count -eq 1 -and $Evidence.S2Files.destination.streams[0].name -ceq $initial.destination.streams[0].name) 'Destination stream layout changed.'
    AssertDelta 'S0-root' 'S2-root' @($Paths.recovery,$Paths.apiBackup,$Paths.handoff)
    $Evidence.integration='PASS_WITH_EVIDENCE'; SaveExecution
    $Phase='VALIDATION'
    $parserResults=@(
        (ParsePinned (FullPath ($Prefix+'p02pre-r1h-capture.ps1')) 93124 $CaptureHash)
        (ParsePinned (FullPath $Paths.destination) 57812 $NewHash)
    )
    $Evidence.parserResults=$parserResults
    if (@($parserResults | Where-Object { $_.errorCount -ne 0 }).Count -ne 0) {
        $Evidence.parser='FAILED'
        CreateBytes (FullPath $Paths.selfcheckEvidence) ($Utf8.GetBytes((ConvertTo-Json -InputObject ([ordered]@{ state='FAILED'; parser=$parserResults; selfcheck='NOT_RUN' }) -Depth 32 -Compress)))
        throw 'Parser errors: selfcheck and capability children not launched.'
    }
    $Evidence.parser='PASS_WITH_EVIDENCE'
    $self=InvokeChild $Pwsh $Root @('-NoLogo','-NoProfile','-NonInteractive','-File','verification/P02/p02pre-r1h-selfcheck.ps1') @(0,1)
    $summary=$null; $summaryError=$null; $summaryValid=$false
    try {
        $summary=ConvertFrom-Json -InputObject $self.text -AsHashtable -ErrorAction Stop
        $summaryValid=$summary.Count -eq 9 -and $summary.task -ceq 'P02PRE-R1H' -and $summary.status -ceq 'PASS' -and $summary.parseErrors -eq 0 -and $summary.assertionsPassed -gt 0 -and $summary.astControlFlowChecked -eq $true -and $summary.skipBranchNoExternalCalls -eq $true -and $summary.targetScript -ceq (FullPath ($Prefix+'p02pre-r1h-capture.ps1')) -and $summary.isolationConfirmed -ceq 'No capture, git, host getter, registry, ACL, build, cargo or AC invoked.'
    } catch { $summaryError=ExceptionEvidence $_ }
    $Evidence.selfcheck=if ($self.record.exit -eq 0 -and $self.record.stderr.bytes -eq 0 -and $summaryValid) { 'PASS_WITH_EVIDENCE' } else { 'FAILED' }
    CreateBytes (FullPath $Paths.selfcheckEvidence) ($Utf8.GetBytes((ConvertTo-Json -InputObject ([ordered]@{ state=$Evidence.selfcheck; parser=$parserResults; child=$self.record; output=$self.text; summary=$summary; summaryError=$summaryError; historicalRound5='FAILED (preserved)' }) -Depth 64 -Compress)))
    Require ($Evidence.selfcheck -ceq 'PASS_WITH_EVIDENCE') 'Selfcheck failed or positive/negative assertion completion was not reported.'
    $query = '$ErrorActionPreference=''Stop''; $mods=@(Get-Module -ListAvailable Microsoft.PowerShell.Utility,Microsoft.PowerShell.Security | ForEach-Object {[ordered]@{name=$_.Name;version=$_.Version.ToString();path=$_.Path}}); $cmds=[ordered]@{}; foreach($n in @(''Get-FileHash'',''Get-Acl'')){$c=Get-Command -Name $n -ErrorAction Stop; $cmds[$n]=[ordered]@{commandType=$c.CommandType.ToString();source=$c.Source;version=[string]$c.Version}}; $o=[ordered]@{version=$PSVersionTable.PSVersion.ToString();edition=$PSVersionTable.PSEdition;psHome=$PSHOME;modulePath=$env:PSModulePath;languageMode=$ExecutionContext.SessionState.LanguageMode.ToString();modules=$mods;commands=$cmds}; ConvertTo-Json -InputObject $o -Depth 8 -Compress'
    $engine=InvokeChild $Pwsh $Root @('-NoLogo','-NoProfile','-NonInteractive','-Command',$query)
    $capability=$null; $capabilityError=$null; $valid=$false
    try {
        $capability=ConvertFrom-Json -InputObject $engine.text -AsHashtable -ErrorAction Stop
        $valid=$engine.record.stderr.bytes -eq 0 -and $capability.Count -eq 7 -and $capability.version -ceq '7.6.6' -and $capability.edition -ceq 'Core' -and $capability.languageMode -ceq 'FullLanguage' -and $capability.psHome -ceq 'C:\Program Files\PowerShell\7' -and $capability.commands.Count -eq 2 -and $capability.commands.ContainsKey('Get-FileHash') -and $capability.commands.ContainsKey('Get-Acl')
        if ($valid) {
            $valid=$capability.commands['Get-FileHash'].commandType -ceq 'Cmdlet' -and $capability.commands['Get-FileHash'].source -ceq 'Microsoft.PowerShell.Utility' -and $capability.commands['Get-Acl'].commandType -ceq 'Cmdlet' -and $capability.commands['Get-Acl'].source -ceq 'Microsoft.PowerShell.Security'
        }
    } catch { $capabilityError=ExceptionEvidence $_ }
    $Evidence.capability=if ($valid) { 'PASS_WITH_EVIDENCE' } else { 'FAILED' }
    CreateBytes (FullPath $Paths.engineEvidence) ($Utf8.GetBytes((ConvertTo-Json -InputObject ([ordered]@{ state=$Evidence.capability; child=$engine.record; result=$capability; resultError=$capabilityError; output=$engine.text }) -Depth 64 -Compress)))
    Require $valid 'Capability output does not meet frozen contract.'
    $Phase='S3'
    $null = ReadStatus 'S3-root' $Root
    AssertDelta 'S2-root' 'S3-root' @($Paths.selfcheckEvidence,$Paths.engineEvidence)
    $null=AssertPin (FullPath $Paths.destination) 57812 $NewHash
    AssertStable $initial.rootCapture (AssertPin (FullPath ($Prefix+'p02pre-r1h-capture.ps1')) 93124 $CaptureHash)
    AssertStable $initial.rootOldHandoff (AssertPin (FullPath ($Prefix+'p02pre-r1h-handoff-20261012.md')) 8651 '394CCF80E58017798CA2994C0505F2F5B5BB571143D21C655CEFC77B6173520F')
    AssertStable $Evidence.S2Files.destination (AssertPin (FullPath $Paths.destination) 57812 $NewHash)
    AssertStable $Evidence.S2Files.recovery (AssertPin (FullPath $Paths.recovery) 57648 $OldHash)
    AssertStable $Evidence.S2Files.apiBackup (AssertPin (FullPath $Paths.apiBackup) 57648 $OldHash)
    AssertStable $Evidence.S2Files.handoff (AssertPin (FullPath $Paths.handoff) 3551 $HandoffHash)
    AssertAbsent (FullPath $Paths.stage)
    $Evidence.state='PASS_WITH_EVIDENCE'; $Phase='COMPLETE'
    $Evidence.finishedUtc=[DateTime]::UtcNow.ToString('o'); SaveExecution
} catch {
    $Evidence.state='BLOCKED'; $Evidence.failure=ExceptionEvidence $_
    if ($Evidence.integration -cne 'PASS_WITH_EVIDENCE') { $Evidence.integration='BLOCKED' }
    $Evidence.finishedUtc=[DateTime]::UtcNow.ToString('o')
    if ($null -ne $EvidenceStream) {
        foreach ($key in $Paths.Keys) {
            if ($key -ceq 'execution') { continue }
            try {
                $path=FullPath $Paths[$key]
                try { AssertAbsent $path; $actual=[ordered]@{ path=$path; exists=$false } }
                catch { $actual=FileState $path $true }
                $Evidence.failureActualState.Add($actual)
            } catch { $Evidence.failureActualState.Add([ordered]@{ path=$Paths[$key]; state='UNQUERYABLE'; error=ExceptionEvidence $_ }) }
        }
        # The attempt4 FAILURE phase is a single diagnostic, never a replacement for S0/S1/S2/S3.
        if (-not $ProcessClosureBlocked) {
            $Phase='FAILURE'
            try {
                $null=ReadStatus 'FAILURE-root' $Root $false
                if ($Evidence.snapshots.Contains('S0-root')) { AssertDelta 'S0-root' 'FAILURE-root' @() $false }
            } catch { $Evidence.failureStatusError=ExceptionEvidence $_ }
        } else { $Evidence.failureStatus='NOT_RUN: process observation or closure blocked' }
        try { $Evidence.failureIndex=IndexState $false } catch { $Evidence.failureIndex=[ordered]@{ state='UNQUERYABLE'; error=ExceptionEvidence $_ } }
        try { SaveExecution } catch { [Console]::Error.WriteLine('BLOCKED: execution evidence update failed; partial file retained. ' + $_.Exception.Message) }
    }
    [Console]::Error.WriteLine('BLOCKED: ' + $Evidence.failure.message)
    throw
} finally {
    if ($null -ne $EvidenceStream) { $EvidenceStream.Dispose() }
}
