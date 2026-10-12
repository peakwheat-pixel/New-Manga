# P02PRE-R1H Round6 attempt4 pure in-memory self-check.
# Validates candidate executor AST, flat method definitions, and process selection in memory.
# Does NOT dot-source or run executor top level.
# No native method invocation, live process enumeration, registry/profile/ACL query, File.Replace, build or AC action.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:AssertionsPassed = 0

function Assert([bool]$Condition, [string]$Message) {
    if (-not $Condition) {
        throw [InvalidOperationException]::new("Assertion failed: $Message")
    }
    $script:AssertionsPassed++
}

$executorPath = [IO.Path]::Combine($PSScriptRoot, 'p02pre-r1h-round6-integrator-attempt4-20261012.ps1')
Assert (Test-Path -LiteralPath $executorPath) "Candidate executor exists at $executorPath"

# 1. Parse candidate executor AST
$tokens = $null
$parseErrors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile($executorPath, [ref]$tokens, [ref]$parseErrors)
Assert (@($parseErrors).Count -eq 0) "Candidate executor has zero parse errors (actual: $(@($parseErrors).Count))"

# 2. Extract pure helper function ASTs from candidate executor
$requiredFunctions = @('Require', 'GetToolhelpDefinitions', 'SelectProcessRecords', 'InvokeChild')
$extractedAsts = @{}
foreach ($name in $requiredFunctions) {
    $funcAst = $ast.Find({ $args[0] -is [Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -eq $name }, $true)
    Assert ($null -ne $funcAst) "Candidate executor defines function AST: $name"
    $extractedAsts[$name] = $funcAst
}

# 3. Define only the pure helper ASTs in memory (no top-level executor execution)
foreach ($name in $requiredFunctions) {
    Invoke-Expression $extractedAsts[$name].Extent.Text
}

# 4. In-memory validation of GetToolhelpDefinitions
$definitions = GetToolhelpDefinitions
Assert ($definitions -is [System.Array] -or $definitions -is [System.Collections.IList]) "GetToolhelpDefinitions returns a collection"
Assert ($definitions.Count -eq 4) "GetToolhelpDefinitions returns exactly 4 definitions"

$expectedSignatures = @(
    [pscustomobject]@{
        Name = 'CreateToolhelp32Snapshot'
        ReturnType = [IntPtr]
        ParameterCount = 2
        ParameterTypes = [Type[]]@([uint32], [uint32])
    },
    [pscustomobject]@{
        Name = 'Process32FirstW'
        ReturnType = [bool]
        ParameterCount = 2
        ParameterTypes = [Type[]]@([IntPtr], [byte[]])
    },
    [pscustomobject]@{
        Name = 'Process32NextW'
        ReturnType = [bool]
        ParameterCount = 2
        ParameterTypes = [Type[]]@([IntPtr], [byte[]])
    },
    [pscustomobject]@{
        Name = 'CloseHandle'
        ReturnType = [bool]
        ParameterCount = 1
        ParameterTypes = [Type[]]@([IntPtr])
    }
)

for ($i = 0; $i -lt 4; $i++) {
    $def = $definitions[$i]
    $exp = $expectedSignatures[$i]

    Assert ($def.PSObject.Properties['name'] -ne $null) "Definition $i has named property 'name'"
    Assert ($def.PSObject.Properties['returnType'] -ne $null) "Definition $i has named property 'returnType'"
    Assert ($def.PSObject.Properties['parameterTypes'] -ne $null) "Definition $i has named property 'parameterTypes'"

    Assert ($def.name -ceq $exp.Name) "Definition $i name is $($exp.Name)"
    Assert ($def.returnType -eq $exp.ReturnType) "Definition $i returnType is $($exp.ReturnType.FullName)"
    Assert ($def.parameterTypes.Length -eq $exp.ParameterCount) "Definition $i parameterTypes count is $($exp.ParameterCount)"
    for ($p = 0; $p -lt $exp.ParameterCount; $p++) {
        Assert ($def.parameterTypes[$p] -eq $exp.ParameterTypes[$p]) "Definition $i parameter $p type is $($exp.ParameterTypes[$p].FullName)"
    }
}

# 5. TypeBuilder validation in memory: DefineMethod accepts all 4 signatures
$assembly = [Reflection.Emit.AssemblyBuilder]::DefineDynamicAssembly(
    [Reflection.AssemblyName]::new('P02Attempt4SelfCheckToolhelp'),
    [Reflection.Emit.AssemblyBuilderAccess]::Run
)
$module = $assembly.DefineDynamicModule('ToolhelpModule')
$builder = $module.DefineType(
    'P02Attempt4SelfCheckToolhelp.Native',
    [Reflection.TypeAttributes]::Public -bor [Reflection.TypeAttributes]::Sealed -bor [Reflection.TypeAttributes]::Abstract
)

foreach ($def in $definitions) {
    $method = $builder.DefineMethod(
        $def.name,
        [Reflection.MethodAttributes]::Public -bor [Reflection.MethodAttributes]::Static -bor [Reflection.MethodAttributes]::PinvokeImpl,
        [Reflection.CallingConventions]::Standard,
        $def.returnType,
        $def.parameterTypes
    )
    Assert ($null -ne $method) "TypeBuilder.DefineMethod successfully created method $($def.name)"
    Assert ($method.Name -ceq $def.name) "Created method name matches $($def.name)"
    Assert ($method.ReturnType -eq $def.returnType) "Created method returnType matches $($def.returnType.FullName)"
}

# 6. In-memory validation of SelectProcessRecords with synthetic process records
$rootPid = 1000
$childPid = 2000
$grandchildPid = 3000
$roguePid = 4000
$exitedPid = 1500
$survivingPid = 1550

$pIdle = [ordered]@{ pid = 0; parentPid = 0; executable = 'System Idle Process' }
$pSystem = [ordered]@{ pid = 4; parentPid = 0; executable = 'System' }
$pRoot = [ordered]@{ pid = $rootPid; parentPid = 4; executable = 'pwsh.exe' }
$pChild = [ordered]@{ pid = $childPid; parentPid = $rootPid; executable = 'git.exe' }
$pGrandchild = [ordered]@{ pid = $grandchildPid; parentPid = $childPid; executable = 'cmd.exe' }
$pRogue = [ordered]@{ pid = $roguePid; parentPid = $rootPid; executable = 'unknown.exe' }
$pOther = [ordered]@{ pid = 5000; parentPid = 4; executable = 'explorer.exe' }

# Case 6.1: Prelaunch clean state with $null child sentinel
$snapPrelaunch = @($pIdle, $pSystem, $pRoot, $pOther)
$kcEmpty = [Collections.Generic.Dictionary[int,string]]::new()
$resPrelaunch = SelectProcessRecords $snapPrelaunch $rootPid $kcEmpty $null
Assert ($resPrelaunch.Count -eq 1) "Prelaunch selection contains exactly 1 process (Root)"
Assert ($resPrelaunch[0].pid -eq $rootPid) "Prelaunch selection contains Root process ($rootPid)"
Assert (@($resPrelaunch | Where-Object { $_.pid -eq 0 }).Count -eq 0) "Prelaunch selection excludes System Idle Process (PID 0)"

# Case 6.2: Rejection of PID 0 as expected child PID (collision prevention)
$pid0Rejected = $false
try {
    $null = SelectProcessRecords $snapPrelaunch $rootPid $kcEmpty 0
} catch {
    $pid0Rejected = $_.Exception.Message -match 'Expected child PID must be positive or null'
}
Assert $pid0Rejected "SelectProcessRecords rejects PID 0 as expected child PID"

# Case 6.3: Running exact known child attribution
$snapRunning = @($pIdle, $pSystem, $pRoot, $pChild, $pOther)
$kcChild = [Collections.Generic.Dictionary[int,string]]::new()
$kcChild[$childPid] = 'C:\Program Files\Git\cmd\git.exe'
$resRunning = SelectProcessRecords $snapRunning $rootPid $kcChild $childPid
Assert ($resRunning.Count -eq 2) "Running selection contains exactly 2 processes (Root and Child)"
Assert (@($resRunning | Where-Object { $_.pid -eq $rootPid }).Count -eq 1) "Running selection includes Root PID"
Assert (@($resRunning | Where-Object { $_.pid -eq $childPid }).Count -eq 1) "Running selection includes Child PID"
Assert (@($resRunning | Where-Object { $_.pid -eq 0 }).Count -eq 0) "Running selection excludes PID 0"

# Case 6.4: Unknown descendant (grandchild) fails closed
$snapGrandchild = @($pIdle, $pSystem, $pRoot, $pChild, $pGrandchild, $pOther)
$grandchildFailedClosed = $false
try {
    $null = SelectProcessRecords $snapGrandchild $rootPid $kcChild $childPid
} catch {
    $grandchildFailedClosed = $_.Exception.Message -match 'Unlisted child/descendant or ambiguous PID ownership observed'
}
Assert $grandchildFailedClosed "Unknown descendant (grandchild) fails closed"

# Case 6.5: Prelaunch unexpected child (rogue process spawned before launch) fails closed
$snapRoguePrelaunch = @($pIdle, $pSystem, $pRoot, $pRogue, $pOther)
$rogueFailedClosed = $false
try {
    $null = SelectProcessRecords $snapRoguePrelaunch $rootPid $kcEmpty $null
} catch {
    $rogueFailedClosed = $_.Exception.Message -match 'Unlisted child/descendant or ambiguous PID ownership observed'
}
Assert $rogueFailedClosed "Prelaunch unexpected child fails closed"

# Case 6.6: Child executable mismatch fails closed
$pBadChild = [ordered]@{ pid = $childPid; parentPid = $rootPid; executable = 'malicious.exe' }
$snapBadChild = @($pIdle, $pSystem, $pRoot, $pBadChild)
$badExeFailedClosed = $false
try {
    $null = SelectProcessRecords $snapBadChild $rootPid $kcChild $childPid
} catch {
    $badExeFailedClosed = $_.Exception.Message -match 'Unexpected child executable observed'
}
Assert $badExeFailedClosed "Child executable mismatch fails closed"

# Case 6.7: Seeded exited parent PID detects surviving descendant and fails closed
$kcExited = [Collections.Generic.Dictionary[int,string]]::new()
$kcExited[$exitedPid] = 'C:\Program Files\Git\cmd\git.exe'
$pSurvivingDescendant = [ordered]@{ pid = $survivingPid; parentPid = $exitedPid; executable = 'survivor.exe' }
$snapSurviving = @($pIdle, $pSystem, $pRoot, $pSurvivingDescendant)
$survivorFailedClosed = $false
try {
    $null = SelectProcessRecords $snapSurviving $rootPid $kcExited $null
} catch {
    $survivorFailedClosed = $_.Exception.Message -match 'Unlisted child/descendant or ambiguous PID ownership observed'
}
Assert $survivorFailedClosed "Surviving descendant of exited parent fails closed in prelaunch sample"

# 7. In-memory and AST validation of InvokeChild fail-closed preparation paths
$invokeChildAst = $extractedAsts['InvokeChild']
Assert ($null -ne $invokeChildAst) "Candidate executor defines InvokeChild function AST"

# 7.1 AST structure verification: entire body enclosed in try-catch-finally
$topTry = $invokeChildAst.Find({ $args[0] -is [Management.Automation.Language.TryStatementAst] }, $true)
Assert ($null -ne $topTry) "InvokeChild body is enclosed in a try statement"
Assert ($topTry.CatchClauses.Count -gt 0) "InvokeChild has at least one catch clause"
Assert ($topTry.CatchClauses[0].Extent.Text -match '\$script:ProcessClosureBlocked\s*=\s*\$true') "InvokeChild catch clause sets ProcessClosureBlocked"

# 7.2 In-memory execution verification of preparation failure paths
$script:ProcessClosureBlocked = $false
$script:Root = 'G:\CODEX\New Manga'
$script:Owner = 'C:\Users\49745\.codex\worktrees\p02pre-r1h-codex'
$script:Git = 'C:\Program Files\Git\cmd\git.exe'
$script:Pwsh = 'C:\Program Files\PowerShell\7\pwsh.exe'
$script:Evidence = [ordered]@{ processes = [Collections.Generic.List[object]]::new() }

# Test 7.2.1: Unlisted executable preparation failure sets ProcessClosureBlocked before escaping
$unlistedExeThrew = $false
try {
    $null = InvokeChild 'unlisted_binary.exe' $Root @()
} catch {
    $unlistedExeThrew = $_.Exception.Message -match 'Unlisted executable'
}
Assert $unlistedExeThrew "InvokeChild throws on unlisted executable"
Assert ($script:ProcessClosureBlocked -eq $true) "InvokeChild sets ProcessClosureBlocked on unlisted executable preparation failure"

# Test 7.2.2: Already blocked check preserves ProcessClosureBlocked
$alreadyBlockedThrew = $false
try {
    $null = InvokeChild $Git $Root @()
} catch {
    $alreadyBlockedThrew = $_.Exception.Message -match 'Process closure already blocked'
}
Assert $alreadyBlockedThrew "InvokeChild throws when process closure already blocked"
Assert ($script:ProcessClosureBlocked -eq $true) "ProcessClosureBlocked remains true"

# Test 7.2.3: Unlisted CWD preparation failure sets ProcessClosureBlocked before escaping
$script:ProcessClosureBlocked = $false
$unlistedCwdThrew = $false
try {
    $null = InvokeChild $Git 'unlisted_directory' @()
} catch {
    $unlistedCwdThrew = $_.Exception.Message -match 'Unlisted child CWD'
}
Assert $unlistedCwdThrew "InvokeChild throws on unlisted child CWD"
Assert ($script:ProcessClosureBlocked -eq $true) "InvokeChild sets ProcessClosureBlocked on unlisted CWD preparation failure"
$script:ProcessClosureBlocked = $false

# Output structured summary
$summary = [ordered]@{
    task = 'P02PRE-R1H-R6-A4'
    status = 'PASS'
    parseErrors = 0
    assertionsPassed = $script:AssertionsPassed
    definitionsCheck = 'PASS'
    typeBuilderCheck = 'PASS'
    processSelectionCheck = 'PASS'
    invokeChildFailClosedCheck = 'PASS'
    isolationConfirmed = 'In-memory AST helper validation only; no native invocation, live process enumeration, filesystem write, or persistent assembly.'
}

$summaryJson = ConvertTo-Json -InputObject $summary -Compress
Write-Output $summaryJson
exit 0
