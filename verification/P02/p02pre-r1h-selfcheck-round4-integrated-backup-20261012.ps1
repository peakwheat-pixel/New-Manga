$ErrorActionPreference = 'Stop'

# P02PRE-R1H Self-Check: AST Parser, Pure Function Assertions, and Static Control Flow Guarantees
# Strict Isolation: Does NOT invoke capture script, Git, host getters, registry/ACL/profile APIs, Build/Cargo or AC.

$TargetCaptureScript = Join-Path $PSScriptRoot 'p02pre-r1h-capture.ps1'
if (-not (Test-Path -LiteralPath $TargetCaptureScript)) {
    throw "Target capture script does not exist: $TargetCaptureScript"
}

# 1. PowerShell AST Parser Check
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($TargetCaptureScript, [ref]$tokens, [ref]$parseErrors)

if ($null -ne $parseErrors -and $parseErrors.Count -gt 0) {
    $errMessages = @($parseErrors | ForEach-Object { "$($_.Extent.StartLineNumber):$($_.Extent.StartColumnNumber) $($_.Message)" }) -join '; '
    throw "PowerShell AST Parse Failed on $TargetCaptureScript ($($parseErrors.Count) errors): $errMessages"
}

# 2. Pure Functions Definition for Assertion Testing
function Get-InventoryAction([object]$GitMode, [bool]$IsReparsePoint, [bool]$IsLeaf, [bool]$IsContainer, [bool]$IsOrdinaryFile) {
    if ($IsLeaf -and $GitMode -eq '120000' -and $IsReparsePoint) { return 'SKIP_TRACKED_SYMLINK' }
    if ($IsLeaf -and $GitMode -eq '120000' -and -not $IsReparsePoint -and -not $IsContainer -and $IsOrdinaryFile) { return 'SKIP_GIT_SYMLINK_NONREPARSE' }
    if ($IsReparsePoint -or ($IsLeaf -and ($GitMode -eq '120000' -or $IsContainer))) { return 'STOP' }
    if ($IsLeaf -and $null -ne $GitMode -and $GitMode -notin @('100644', '100755')) { return 'STOP' }
    if ($IsLeaf -and -not $IsContainer -and -not $IsOrdinaryFile) { return 'STOP' }
    return 'HASH_REGULAR_FILE'
}

function Test-OrdinaryFileMetadata([type]$ItemType, [IO.FileAttributes]$Attributes) {
    if ($ItemType -ne [IO.FileInfo]) { return $false }
    if ($Attributes -eq [IO.FileAttributes]::Normal) { return $true }
    $allowed = [IO.FileAttributes]::ReadOnly -bor [IO.FileAttributes]::Hidden -bor [IO.FileAttributes]::System -bor [IO.FileAttributes]::Archive -bor [IO.FileAttributes]::Temporary -bor [IO.FileAttributes]::Offline -bor [IO.FileAttributes]::NotContentIndexed -bor [IO.FileAttributes]::Encrypted
    $actualBits = [int]$Attributes
    return ($actualBits -ne 0 -and ($actualBits -band (-bnot [int]$allowed)) -eq 0)
}

function Test-FrozenGitBaselineMatch([object]$Expected, [object]$Actual) {
    if ($null -eq $Expected -or $null -eq $Actual) { return $false }
    foreach ($name in @('statusSha256', 'indexSha256')) {
        if ($Expected[$name] -notmatch '^[0-9a-fA-F]{64}$' -or $Actual[$name] -notmatch '^[0-9a-fA-F]{64}$' -or $Expected[$name] -ine $Actual[$name]) { return $false }
    }
    return $true
}

function Test-SafeRepositoryRelativePath([string]$RelativePath) {
    if ([string]::IsNullOrEmpty($RelativePath) -or $RelativePath.StartsWith('/') -or $RelativePath.StartsWith('\')) { return $false }
    foreach ($part in $RelativePath.Replace('\', '/').Split('/')) {
        if ([string]::IsNullOrEmpty($part) -or $part -in @('.', '..') -or $part.Contains(':') -or $part.EndsWith('.') -or $part.EndsWith(' ') -or $part -match '~[0-9]') { return $false }
    }
    return $true
}

function Test-UnreadUserDataStagingPath([string]$RelativePath) {
    return ($RelativePath.Equals('.tmp.driveupload', [StringComparison]::OrdinalIgnoreCase) -or $RelativePath.StartsWith('.tmp.driveupload/', [StringComparison]::OrdinalIgnoreCase) -or $RelativePath.StartsWith('.tmp.driveupload\', [StringComparison]::OrdinalIgnoreCase))
}

function Get-LinkTypeEvidence([object]$Item) {
    $property = $Item.PSObject.Properties['LinkType']
    if ($null -eq $property -or [string]::IsNullOrEmpty([string]$property.Value)) { return 'NOT_AVAILABLE_ON_ENGINE' }
    return [string]$property.Value
}

function Test-ExpectedDetachedBranchResult([object]$CommandRecord) {
    return ($CommandRecord.exitCode -eq 128 -and $CommandRecord.stdoutBase64 -eq '' -and $CommandRecord.stderrBase64 -ceq 'ZmF0YWw6IHJlZiBIRUFEIGlzIG5vdCBhIHN5bWJvbGljIHJlZgo=')
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
    $modes = [System.Collections.Generic.Dictionary[string,object]]::new([StringComparer]::OrdinalIgnoreCase)
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
        if ($metadata.Count -ne 3 -or $metadata[0] -notmatch '^(100644|100755|120000|160000)$' -or $metadata[1] -notmatch '^[0-9a-f]{40,64}$' -or $metadata[2] -notmatch '^[0-3]$' -or [string]::IsNullOrEmpty($path)) { throw 'Git index --stage entry is malformed or uses an unknown mode.' }
        $stage = [int]$metadata[2]
        if ($stage -ne 0) { throw "Unmerged Git index stage is unsupported: stage=$stage" }
        if ($modes.ContainsKey($path)) { throw "Duplicate staged path is unsupported: $path" }
        $modes.Add($path, [pscustomobject]@{ mode = $metadata[0]; stage = $stage })
    }
    return [pscustomobject]@{ modes = $modes; entryCount = $modes.Count; nulTerminatorCount = $nulCount }
}

function Get-ParsedFunctionAst([string]$SourceText, [string]$FunctionName) {
    $mutationTokens = $null
    $mutationErrors = $null
    $parsed = [System.Management.Automation.Language.Parser]::ParseInput($SourceText, [ref]$mutationTokens, [ref]$mutationErrors)
    if ($null -eq $parsed -or ($null -ne $mutationErrors -and $mutationErrors.Count -gt 0)) { return $null }
    $matches = @($parsed.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $args[0].Name -ceq $FunctionName }, $true))
    if ($matches.Count -ne 1) { return $null }
    return $matches[0]
}

function Test-SkipHelperAstContract([System.Management.Automation.Language.FunctionDefinitionAst]$HelperAst) {
    if ($null -eq $HelperAst) { return $false }
    $expectedReceiver = $null
    $expectedMethod = $null
    $expectedArguments = @()
    switch ($HelperAst.Name) {
        'Get-LinkTypeEvidence' {
            $expectedReceiver = '[string]'
            $expectedMethod = 'IsNullOrEmpty'
            $expectedArguments = @('[string]$property.Value')
        }
        'Set-RepositoryStop' {
            $expectedReceiver = '[Math]'
            $expectedMethod = 'Max'
            $expectedArguments = @('0', '$Record.candidateCount - $Record.processedCount')
        }
        default { return $false }
    }
    $commands = @($HelperAst.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true))
    $invocations = @($HelperAst.FindAll({ $args[0] -is [System.Management.Automation.Language.InvokeMemberExpressionAst] }, $true))
    $redirections = @($HelperAst.FindAll({ $args[0] -is [System.Management.Automation.Language.FileRedirectionAst] }, $true))
    if ($commands.Count -ne 0 -or $invocations.Count -ne 1 -or $redirections.Count -ne 0) { return $false }
    $invocation = $invocations[0]
    if (-not $invocation.Static -or $invocation.Expression.Extent.Text.Trim() -cne $expectedReceiver -or $invocation.Member.Extent.Text.Trim() -cne $expectedMethod -or $invocation.Arguments.Count -ne $expectedArguments.Count) { return $false }
    for ($argumentIndex = 0; $argumentIndex -lt $expectedArguments.Count; $argumentIndex++) {
        if ($invocation.Arguments[$argumentIndex].Extent.Text.Trim() -cne $expectedArguments[$argumentIndex]) { return $false }
    }
    return $true
}

function Get-DirectStatementIndex([System.Management.Automation.Language.StatementBlockAst]$Block, [System.Management.Automation.Language.Ast]$Target) {
    if ($null -eq $Block -or $null -eq $Target) { return -1 }
    for ($statementIndex = 0; $statementIndex -lt $Block.Statements.Count; $statementIndex++) {
        if ([object]::ReferenceEquals($Block.Statements[$statementIndex], $Target)) { return $statementIndex }
    }
    return -1
}

function Test-SkipBranchAstContract([System.Management.Automation.Language.IfStatementAst]$Branch, [string]$ExpectedCondition, [string]$ExpectedState) {
    if ($null -eq $Branch -or $Branch.Clauses.Count -ne 1 -or $null -ne $Branch.ElseClause -or $Branch.Clauses[0].Item1.Extent.Text.Trim() -cne $ExpectedCondition) { return $false }
    $block = $Branch.Clauses[0].Item2
    $commands = @($block.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true))
    $invocations = @($block.FindAll({ $args[0] -is [System.Management.Automation.Language.InvokeMemberExpressionAst] }, $true))
    $assignments = @($block.FindAll({ $args[0] -is [System.Management.Automation.Language.AssignmentStatementAst] }, $true))
    $breaks = @($block.FindAll({ $args[0] -is [System.Management.Automation.Language.BreakStatementAst] }, $true))
    $continues = @($block.FindAll({ $args[0] -is [System.Management.Automation.Language.ContinueStatementAst] }, $true))
    $redirections = @($block.FindAll({ $args[0] -is [System.Management.Automation.Language.FileRedirectionAst] }, $true))
    if ($commands.Count -ne 1 -or $commands[0].Extent.Text.Trim() -cne 'Get-LinkTypeEvidence $item' -or $invocations.Count -ne 1 -or $assignments.Count -lt 1 -or $assignments.Count -gt 3 -or $breaks.Count -ne 1 -or $continues.Count -ne 0 -or $redirections.Count -ne 0) { return $false }
    if (@($assignments | Where-Object { $_.Left.Extent.Text.Trim() -notin @('$linkSkipped', '$record.skippedSymlinkCount', '$record.processedCount') }).Count -ne 0) { return $false }
    $add = $invocations[0]
    if ($add.Static -or $add.Expression.Extent.Text.Trim() -cne '$record.linkInventory' -or $add.Member.Extent.Text.Trim() -cne 'Add' -or $add.Arguments.Count -ne 1) { return $false }
    if ($add.Extent.Text -notmatch ("state\s*=\s*'" + [regex]::Escape($ExpectedState) + "'") -or $add.Extent.Text -notmatch "targetRead\s*=\s*'NOT_ATTEMPTED'" -or $add.Extent.Text -notmatch "targetHash\s*=\s*'NOT_CAPTURED'") { return $false }
    $isTrackedBranch = ($ExpectedState -ceq 'SKIPPED_SYMLINK_NOT_FOLLOWED')
    $expectedStatementCount = if ($isTrackedBranch) { 5 } else { 6 }
    $addStatementIndex = if ($isTrackedBranch) { 0 } else { 1 }
    if ($block.Statements.Count -ne $expectedStatementCount -or $block.Statements[$addStatementIndex].Extent.StartOffset -gt $add.Extent.StartOffset -or $block.Statements[$addStatementIndex].Extent.EndOffset -lt $add.Extent.EndOffset) { return $false }
    if (-not $isTrackedBranch) {
        $baselineGuard = $block.Statements[0]
        if ($baselineGuard -isnot [System.Management.Automation.Language.IfStatementAst] -or $baselineGuard.Clauses.Count -ne 1 -or $null -ne $baselineGuard.ElseClause) { return $false }
        if ($baselineGuard.Clauses[0].Item1.Extent.Text -notmatch '\$record\.targetMatches' -or $baselineGuard.Clauses[0].Item1.Extent.Text -notmatch '\$record\.commands\.status\.exitCode' -or $baselineGuard.Clauses[0].Item1.Extent.Text -notmatch '-not' -or $baselineGuard.Clauses[0].Item1.Extent.Text -notmatch '-ne\s+0') { return $false }
        if (@($baselineGuard.FindAll({ $args[0] -is [System.Management.Automation.Language.ThrowStatementAst] }, $true)).Count -ne 1 -or @($baselineGuard.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] -or $args[0] -is [System.Management.Automation.Language.InvokeMemberExpressionAst] -or $args[0] -is [System.Management.Automation.Language.FileRedirectionAst] }, $true)).Count -ne 0) { return $false }
    }
    $assignmentOffset = if ($isTrackedBranch) { 1 } else { 2 }
    if ($block.Statements[$assignmentOffset].Extent.Text.Trim() -cne '$record.skippedSymlinkCount++' -or $block.Statements[$assignmentOffset + 1].Extent.Text.Trim() -cne '$record.processedCount++' -or $block.Statements[$assignmentOffset + 2].Extent.Text.Trim() -cne '$linkSkipped = $true') { return $false }
    if (@($assignments | Where-Object { $_.Left.Extent.Text.Trim() -ceq '$linkSkipped' -and $_.Right.Extent.Text.Trim() -ceq '$true' }).Count -ne 1) { return $false }
    if ($block.Statements.Count -eq 0 -or $block.Statements[-1] -isnot [System.Management.Automation.Language.BreakStatementAst]) { return $false }
    return $true
}

function Test-CandidatePrefixThrowGuard([System.Management.Automation.Language.IfStatementAst]$Guard, [string]$ExpectedCondition, [string]$ExpectedMessage) {
    if ($null -eq $Guard -or $Guard.Clauses.Count -ne 1 -or $null -ne $Guard.ElseClause -or $Guard.Clauses[0].Item1.Extent.Text.Trim() -cne $ExpectedCondition) { return $false }
    $statements = $Guard.Clauses[0].Item2.Statements
    if ($statements.Count -ne 1 -or $statements[0] -isnot [System.Management.Automation.Language.ThrowStatementAst]) { return $false }
    return ($statements[0].Extent.Text.Trim() -ceq ('throw "' + $ExpectedMessage + '"'))
}

function Test-CandidateStagingBranchAst([System.Management.Automation.Language.IfStatementAst]$Branch) {
    if ($null -eq $Branch -or $Branch.Clauses.Count -ne 1 -or $null -ne $Branch.ElseClause -or $Branch.Clauses[0].Item1.Extent.Text.Trim() -cne 'Test-UnreadUserDataStagingPath $canonicalRelative') { return $false }
    $statements = $Branch.Clauses[0].Item2.Statements
    if ($statements.Count -ne 4 -or $statements[0].Extent.Text.Trim() -cne '$record.unreadUserDataCount++' -or $statements[2].Extent.Text.Trim() -cne '$record.processedCount++' -or $statements[3] -isnot [System.Management.Automation.Language.ContinueStatementAst]) { return $false }
    $firstPathGuard = $statements[1]
    if ($firstPathGuard -isnot [System.Management.Automation.Language.IfStatementAst] -or $firstPathGuard.Clauses.Count -ne 1 -or $null -ne $firstPathGuard.ElseClause -or $firstPathGuard.Clauses[0].Item1.Extent.Text.Trim() -cne '$null -eq $record.firstUnreadUserDataPath') { return $false }
    $firstPathStatements = $firstPathGuard.Clauses[0].Item2.Statements
    if ($firstPathStatements.Count -ne 1 -or $firstPathStatements[0].Extent.Text.Trim() -cne '$record.firstUnreadUserDataPath = $relative') { return $false }
    if (@($Branch.FindAll({ $args[0] -is [System.Management.Automation.Language.ThrowStatementAst] -or $args[0] -is [System.Management.Automation.Language.BreakStatementAst] -or $args[0] -is [System.Management.Automation.Language.ReturnStatementAst] }, $true)).Count -ne 0) { return $false }
    return $true
}

function Test-CandidateLoopPrefixAstContract([System.Management.Automation.Language.ForEachStatementAst]$CandidateLoop, [int]$PathLoopIndex) {
    if ($null -eq $CandidateLoop -or $CandidateLoop.Variable.Extent.Text.Trim() -cne '$relative' -or $CandidateLoop.Expression.Extent.Text.Trim() -cne '$record.paths' -or $PathLoopIndex -ne 13) { return $false }
    $statements = $CandidateLoop.Body.Statements
    if ($statements.Count -le $PathLoopIndex) { return $false }
    $prefix = @($statements[0..($PathLoopIndex - 1)])
    if ($prefix.Count -ne 13) { return $false }
    $expectedDirectTexts = [ordered]@{
        0 = '$currentRelativePath = $relative'
        1 = '$currentOperation = ''Path normalization'''
        3 = '$normalizedRelative = $relative.Replace(''\'', ''/'')'
        4 = '$full = [IO.Path]::GetFullPath((Join-Path $Root ($normalizedRelative.Replace(''/'', ''\''))))'
        6 = '$canonicalRelative = $full.Substring($rootFull.Length).Replace(''\'', ''/'')'
        9 = '$cursor = $Root'
        10 = '$item = $null'
        11 = '$parts = $relative -split ''[\\/]'''
        12 = '$linkSkipped = $false'
    }
    foreach ($index in $expectedDirectTexts.Keys) {
        if ($prefix[[int]$index].Extent.Text.Trim() -cne $expectedDirectTexts[[object]$index]) { return $false }
    }
    if (-not (Test-CandidatePrefixThrowGuard $prefix[2] '-not (Test-SafeRepositoryRelativePath $relative)' 'Unsafe Git-relative path form: $relative')) { return $false }
    if (-not (Test-CandidatePrefixThrowGuard $prefix[5] '-not $full.StartsWith($rootFull, [StringComparison]::OrdinalIgnoreCase)' 'Git path escaped repository: $relative')) { return $false }
    if (-not (Test-CandidatePrefixThrowGuard $prefix[7] '-not (Test-SafeRepositoryRelativePath $canonicalRelative) -or -not $canonicalRelative.Equals($normalizedRelative, [StringComparison]::OrdinalIgnoreCase)' 'Git path did not normalize to one safe repository-relative path: $relative')) { return $false }
    if ($prefix[8] -isnot [System.Management.Automation.Language.IfStatementAst] -or -not (Test-CandidateStagingBranchAst $prefix[8])) { return $false }

    $prefixStartOffset = $prefix[0].Extent.StartOffset
    $prefixEndOffset = $prefix[-1].Extent.EndOffset
    $prefixNodes = @($CandidateLoop.Body.FindAll({
        $node = $args[0]
        $node.Extent.StartOffset -ge $prefixStartOffset -and $node.Extent.EndOffset -le $prefixEndOffset
    }, $true))
    $commands = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.CommandAst] })
    $invocations = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.InvokeMemberExpressionAst] })
    $memberExpressions = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.MemberExpressionAst] -and $_ -isnot [System.Management.Automation.Language.InvokeMemberExpressionAst] })
    $indexExpressions = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.IndexExpressionAst] })
    $redirections = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.FileRedirectionAst] })
    $assignments = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.AssignmentStatementAst] })
    $ifStatements = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.IfStatementAst] })
    $throws = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.ThrowStatementAst] })
    $continues = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.ContinueStatementAst] })
    $breaks = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.BreakStatementAst] })
    $returns = @($prefixNodes | Where-Object { $_ -is [System.Management.Automation.Language.ReturnStatementAst] })
    $expectedCommands = [ordered]@{ 'Test-SafeRepositoryRelativePath' = 2; 'Join-Path' = 1; 'Test-UnreadUserDataStagingPath' = 1 }
    $commandCounts = @{}
    foreach ($command in $commands) {
        $name = $command.GetCommandName()
        if ([string]::IsNullOrEmpty($name) -or -not $expectedCommands.Contains($name)) { return $false }
        if (-not $commandCounts.ContainsKey($name)) { $commandCounts[$name] = 0 }
        $commandCounts[$name]++
    }
    if ($commands.Count -ne 4) { return $false }
    foreach ($name in $expectedCommands.Keys) {
        if (-not $commandCounts.ContainsKey($name) -or $commandCounts[$name] -ne $expectedCommands[$name]) { return $false }
    }

    $expectedInvocationShapes = @(
        [pscustomobject]@{ static = $false; expression = '$relative'; member = 'Replace'; count = 2 },
        [pscustomobject]@{ static = $true; expression = '[IO.Path]'; member = 'GetFullPath'; count = 1 },
        [pscustomobject]@{ static = $false; expression = '$normalizedRelative'; member = 'Replace'; count = 2 },
        [pscustomobject]@{ static = $false; expression = '$full'; member = 'StartsWith'; count = 2 },
        [pscustomobject]@{ static = $false; expression = '$full'; member = 'Substring'; count = 1 },
        [pscustomobject]@{ static = $false; expression = '$full.Substring($rootFull.Length)'; member = 'Replace'; count = 2 },
        [pscustomobject]@{ static = $false; expression = '$canonicalRelative'; member = 'Equals'; count = 2 }
    )
    if ($invocations.Count -ne $expectedInvocationShapes.Count) { return $false }
    foreach ($shape in $expectedInvocationShapes) {
        if (@($invocations | Where-Object { $_.Static -eq $shape.static -and $_.Expression.Extent.Text.Trim() -ceq $shape.expression -and $_.Member.Extent.Text.Trim() -ceq $shape.member -and $_.Arguments.Count -eq $shape.count }).Count -ne 1) { return $false }
    }

    $expectedMemberExpressions = [ordered]@{
        '[StringComparison]::OrdinalIgnoreCase' = 2
        '$rootFull.Length' = 1
        '$record.unreadUserDataCount' = 1
        '$record.firstUnreadUserDataPath' = 2
        '$record.processedCount' = 1
    }
    $memberCounts = @{}
    foreach ($memberExpression in $memberExpressions) {
        $name = $memberExpression.Extent.Text.Trim()
        if (-not $expectedMemberExpressions.Contains($name)) { return $false }
        if (-not $memberCounts.ContainsKey($name)) { $memberCounts[$name] = 0 }
        $memberCounts[$name]++
    }
    foreach ($name in $expectedMemberExpressions.Keys) {
        if (-not $memberCounts.ContainsKey($name) -or $memberCounts[$name] -ne $expectedMemberExpressions[$name]) { return $false }
    }
    if ($indexExpressions.Count -ne 0 -or $redirections.Count -ne 0 -or $ifStatements.Count -ne 5 -or $throws.Count -ne 3 -or $continues.Count -ne 1 -or $breaks.Count -ne 0 -or $returns.Count -ne 0) { return $false }

    $expectedAssignments = [ordered]@{
        '$currentRelativePath' = 1; '$currentOperation' = 1; '$normalizedRelative' = 1; '$full' = 1; '$canonicalRelative' = 1
        '$cursor' = 1; '$item' = 1; '$parts' = 1; '$linkSkipped' = 1; '$record.firstUnreadUserDataPath' = 1
        '$record.unreadUserDataCount' = 1; '$record.processedCount' = 1
    }
    $assignmentCounts = @{}
    foreach ($assignment in $assignments) {
        $left = $assignment.Left.Extent.Text.Trim()
        if (-not $expectedAssignments.Contains($left)) { return $false }
        if (-not $assignmentCounts.ContainsKey($left)) { $assignmentCounts[$left] = 0 }
        $assignmentCounts[$left]++
    }
    if ($assignments.Count -notin @(10, 12)) { return $false }
    foreach ($left in $expectedAssignments.Keys) {
        $stagingCounter = $left -in @('$record.unreadUserDataCount', '$record.processedCount')
        if ($stagingCounter) {
            if (($assignmentCounts.ContainsKey($left) -and $assignmentCounts[$left] -notin @(0, 1)) -or (-not $assignmentCounts.ContainsKey($left) -and $assignments.Count -eq 12)) { return $false }
        }
        elseif (-not $assignmentCounts.ContainsKey($left) -or $assignmentCounts[$left] -ne $expectedAssignments[$left]) { return $false }
    }
    return $true
}

function Test-RepositorySkipAstContract([System.Management.Automation.Language.FunctionDefinitionAst]$RepositoryFunctionAst) {
    if ($null -eq $RepositoryFunctionAst -or $RepositoryFunctionAst.Name -cne 'Get-RepositoryRecord') { return $false }
    $trackedBranches = @($RepositoryFunctionAst.FindAll({ $args[0] -is [System.Management.Automation.Language.IfStatementAst] -and $args[0].Clauses[0].Item1.Extent.Text.Trim() -ceq '$action -eq ''SKIP_TRACKED_SYMLINK''' }, $true))
    $nonReparseBranches = @($RepositoryFunctionAst.FindAll({ $args[0] -is [System.Management.Automation.Language.IfStatementAst] -and $args[0].Clauses[0].Item1.Extent.Text.Trim() -ceq '$action -eq ''SKIP_GIT_SYMLINK_NONREPARSE''' }, $true))
    if ($trackedBranches.Count -ne 1 -or $nonReparseBranches.Count -ne 1) { return $false }
    $trackedBranch = $trackedBranches[0]
    $nonReparseBranch = $nonReparseBranches[0]
    $pathLoops = @($RepositoryFunctionAst.FindAll({
        $node = $args[0]
        $node -is [System.Management.Automation.Language.ForStatementAst] -and
            $node.Condition.Extent.Text -match '^\$partIndex\s*-lt\s*\$parts\.Count$' -and
            $node.Extent.StartOffset -lt $trackedBranch.Extent.StartOffset -and $node.Extent.EndOffset -gt $nonReparseBranch.Extent.EndOffset
    }, $true))
    if ($pathLoops.Count -ne 1) { return $false }
    $pathLoop = $pathLoops[0]
    $trackedIndex = Get-DirectStatementIndex $pathLoop.Body $trackedBranch
    $nonReparseIndex = Get-DirectStatementIndex $pathLoop.Body $nonReparseBranch
    if ($trackedIndex -lt 0 -or $nonReparseIndex -ne ($trackedIndex + 1)) { return $false }
    if (-not (Test-SkipBranchAstContract $trackedBranch '$action -eq ''SKIP_TRACKED_SYMLINK''' 'SKIPPED_SYMLINK_NOT_FOLLOWED')) { return $false }
    if (-not (Test-SkipBranchAstContract $nonReparseBranch '$action -eq ''SKIP_GIT_SYMLINK_NONREPARSE''' 'SKIPPED_GIT_SYMLINK_NONREPARSE')) { return $false }

    $expectedCommandTexts = [ordered]@{
        'Join-Path' = 'Join-Path $cursor $part'
        'Get-Item' = 'Get-Item -LiteralPath $cursor -Force -ErrorAction Stop'
        'Test-OrdinaryFileMetadata' = 'Test-OrdinaryFileMetadata $itemType ([IO.FileAttributes]$item.Attributes)'
        'Get-InventoryAction' = 'Get-InventoryAction $gitMode $reparse $isLeaf ([bool]$item.PSIsContainer) $ordinaryFile'
        'Get-LinkTypeEvidence' = 'Get-LinkTypeEvidence $item'
    }
    $expectedCommandCounts = [ordered]@{ 'Join-Path' = 1; 'Get-Item' = 1; 'Test-OrdinaryFileMetadata' = 1; 'Get-InventoryAction' = 1; 'Get-LinkTypeEvidence' = 2 }
    $commandCounts = @{}
    $commands = @($pathLoop.Body.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] }, $true))
    foreach ($command in $commands) {
        $name = $command.GetCommandName()
        if ([string]::IsNullOrEmpty($name) -or -not $expectedCommandTexts.Contains($name) -or $command.Extent.Text.Trim() -cne $expectedCommandTexts[$name]) { return $false }
        if (-not $commandCounts.ContainsKey($name)) { $commandCounts[$name] = 0 }
        $commandCounts[$name]++
    }
    if ($commands.Count -ne 6) { return $false }
    foreach ($name in $expectedCommandCounts.Keys) {
        if (-not $commandCounts.ContainsKey($name) -or $commandCounts[$name] -ne $expectedCommandCounts[$name]) { return $false }
    }
    foreach ($command in @($commands | Where-Object { $_.GetCommandName() -ne 'Get-LinkTypeEvidence' })) {
        if ($command.Extent.StartOffset -ge $trackedBranch.Extent.StartOffset) { return $false }
    }
    foreach ($branch in @($trackedBranch, $nonReparseBranch)) {
        if (@($branch.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] -and $args[0].GetCommandName() -eq 'Get-LinkTypeEvidence' }, $true)).Count -ne 1) { return $false }
    }

    $invocations = @($pathLoop.Body.FindAll({ $args[0] -is [System.Management.Automation.Language.InvokeMemberExpressionAst] }, $true))
    if ($invocations.Count -ne 4) { return $false }
    $getTypeCalls = @($invocations | Where-Object { $_.Expression.Extent.Text.Trim() -ceq '$item' -and $_.Member.Extent.Text.Trim() -ceq 'GetType' -and $_.Arguments.Count -eq 0 -and $_.Extent.Text.Trim() -ceq '$item.GetType()' })
    $containsKeyCalls = @($invocations | Where-Object { $_.Expression.Extent.Text.Trim() -ceq '$indexModes' -and $_.Member.Extent.Text.Trim() -ceq 'ContainsKey' -and $_.Arguments.Count -eq 1 -and $_.Arguments[0].Extent.Text.Trim() -ceq '$relative' -and $_.Extent.Text.Trim() -ceq '$indexModes.ContainsKey($relative)' })
    $addCalls = @($invocations | Where-Object { $_.Expression.Extent.Text.Trim() -ceq '$record.linkInventory' -and $_.Member.Extent.Text.Trim() -ceq 'Add' -and $_.Arguments.Count -eq 1 })
    if ($getTypeCalls.Count -ne 1 -or $containsKeyCalls.Count -ne 1 -or $addCalls.Count -ne 2) { return $false }
    foreach ($addCall in $addCalls) {
        if ($addCall.Extent.StartOffset -lt $trackedBranch.Extent.StartOffset -or $addCall.Extent.EndOffset -gt $nonReparseBranch.Extent.EndOffset) { return $false }
    }
    $allowedMemberExpressions = @(
        '$item.Attributes', '$item.PSIsContainer', '$itemType.FullName', '[IO.FileAttributes]::ReparsePoint',
        '$record.linkInventory', '$record.skippedSymlinkCount', '$record.processedCount', '$record.targetMatches',
        '$record.commands', '$record.commands.status', '$record.commands.status.exitCode', '$indexEntry.mode', '$indexEntry.stage'
    )
    $memberExpressions = @($pathLoop.Body.FindAll({ $args[0] -is [System.Management.Automation.Language.MemberExpressionAst] -and $args[0] -isnot [System.Management.Automation.Language.InvokeMemberExpressionAst] }, $true))
    foreach ($memberExpression in $memberExpressions) {
        if ($memberExpression.Extent.Text.Trim() -notin $allowedMemberExpressions) { return $false }
    }
    $indexExpressions = @($pathLoop.Body.FindAll({ $args[0] -is [System.Management.Automation.Language.IndexExpressionAst] }, $true))
    if ($indexExpressions.Count -ne 1 -or $indexExpressions[0].Extent.Text.Trim() -cne '$indexModes[$relative]') { return $false }
    $redirections = @($pathLoop.Body.FindAll({ $args[0] -is [System.Management.Automation.Language.FileRedirectionAst] }, $true))
    if ($redirections.Count -ne 0) { return $false }

    $expectedAssignments = [ordered]@{
        '$part' = 1; '$cursor' = 1; '$currentOperation' = 1; '$item' = 1; '$isLeaf' = 1; '$reparse' = 1
        '$itemType' = 1; '$ordinaryFile' = 1; '$indexEntry' = 1; '$gitMode' = 1; '$indexStage' = 1; '$action' = 1
        '$record.skippedSymlinkCount' = 2; '$record.processedCount' = 2; '$linkSkipped' = 2
    }
    $assignmentCounts = @{}
    $assignments = @($pathLoop.Body.FindAll({ $args[0] -is [System.Management.Automation.Language.AssignmentStatementAst] }, $true))
    foreach ($assignment in $assignments) {
        $left = $assignment.Left.Extent.Text.Trim()
        if (-not $expectedAssignments.Contains($left)) { return $false }
        if (-not $assignmentCounts.ContainsKey($left)) { $assignmentCounts[$left] = 0 }
        $assignmentCounts[$left]++
    }
    if ($assignments.Count -notin @(14, 18)) { return $false }
    foreach ($left in $expectedAssignments.Keys) {
        $isCounterIncrement = $left -in @('$record.skippedSymlinkCount', '$record.processedCount')
        if ($isCounterIncrement) {
            if (($assignmentCounts.ContainsKey($left) -and $assignmentCounts[$left] -notin @(0, $expectedAssignments[$left])) -or (-not $assignmentCounts.ContainsKey($left) -and $assignments.Count -eq 18)) { return $false }
        }
        elseif (-not $assignmentCounts.ContainsKey($left) -or $assignmentCounts[$left] -ne $expectedAssignments[$left]) { return $false }
    }
    $breaks = @($pathLoop.Body.FindAll({ $args[0] -is [System.Management.Automation.Language.BreakStatementAst] }, $true))
    $continues = @($pathLoop.Body.FindAll({ $args[0] -is [System.Management.Automation.Language.ContinueStatementAst] }, $true))
    $returns = @($pathLoop.Body.FindAll({ $args[0] -is [System.Management.Automation.Language.ReturnStatementAst] }, $true))
    if ($breaks.Count -ne 2 -or $continues.Count -ne 0 -or $returns.Count -ne 0) { return $false }

    $continueBranches = @($RepositoryFunctionAst.FindAll({
        $node = $args[0]
        $node -is [System.Management.Automation.Language.IfStatementAst] -and $node.Clauses.Count -eq 1 -and $node.Clauses[0].Item1.Extent.Text.Trim() -ceq '$linkSkipped'
    }, $true))
    if ($continueBranches.Count -ne 1) { return $false }
    $continueBranch = $continueBranches[0]
    $continueBlock = $continueBranch.Clauses[0].Item2
    if ($null -ne $continueBranch.ElseClause -or $continueBlock.Statements.Count -ne 1 -or $continueBlock.Statements[0] -isnot [System.Management.Automation.Language.ContinueStatementAst]) { return $false }
    if (@($continueBlock.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] -or $args[0] -is [System.Management.Automation.Language.InvokeMemberExpressionAst] -or $args[0] -is [System.Management.Automation.Language.FileRedirectionAst] }, $true)).Count -ne 0) { return $false }
    $candidateLoops = @($RepositoryFunctionAst.FindAll({
        $node = $args[0]
        $node -is [System.Management.Automation.Language.ForEachStatementAst] -and
            $node.Extent.StartOffset -lt $pathLoop.Extent.StartOffset -and $node.Extent.EndOffset -gt $continueBranch.Extent.EndOffset
    }, $true))
    if ($candidateLoops.Count -ne 1) { return $false }
    $candidateLoop = $candidateLoops[0]
    $pathLoopIndex = Get-DirectStatementIndex $candidateLoop.Body $pathLoop
    $continueIndex = Get-DirectStatementIndex $candidateLoop.Body $continueBranch
    if ($pathLoopIndex -lt 0 -or -not (Test-CandidateLoopPrefixAstContract $candidateLoop $pathLoopIndex) -or $continueIndex -ne ($pathLoopIndex + 1) -or ($continueIndex + 2) -ge $candidateLoop.Body.Statements.Count) { return $false }
    if ($candidateLoop.Body.Statements[$continueIndex + 1].Extent.Text.Trim() -cne '$currentOperation = ''Get-FileHash''') { return $false }
    if ($candidateLoop.Body.Statements[$continueIndex + 2].Extent.Text -notmatch '^\$hash\s*=\s*Get-FileHash\s+-LiteralPath\s+\$full\b') { return $false }
    if (@($RepositoryFunctionAst.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] -and $args[0].GetCommandName() -eq 'Get-FileHash' }, $true)).Count -ne 1) { return $false }
    return $true
}

function New-SourceInsertion([string]$Source, [string]$Anchor, [string]$InsertedText, [switch]$After, [int]$StartIndex = 0) {
    if ($null -eq $Source -or $null -eq $Anchor) { return $null }
    $index = $Source.IndexOf($Anchor, $StartIndex, [StringComparison]::Ordinal)
    if ($index -lt 0) { return $null }
    if ($After) { $index += $Anchor.Length }
    return $Source.Insert($index, $InsertedText)
}

function New-SourceReplacement([string]$Source, [string]$Anchor, [string]$Replacement, [int]$StartIndex = 0) {
    if ($null -eq $Source -or $null -eq $Anchor) { return $null }
    $index = $Source.IndexOf($Anchor, $StartIndex, [StringComparison]::Ordinal)
    if ($index -lt 0) { return $null }
    return $Source.Remove($index, $Anchor.Length).Insert($index, $Replacement)
}

# 3. Pure Function Assertions
$assertionsPassed = 0

# 3.1 Real reparse symlink
if ((Get-InventoryAction '120000' $true $true $true $false) -ne 'SKIP_TRACKED_SYMLINK') { throw 'Assertion failed: real reparse leaf symlink (container) must return SKIP_TRACKED_SYMLINK' }
$assertionsPassed++
if ((Get-InventoryAction '120000' $true $true $false $false) -ne 'SKIP_TRACKED_SYMLINK') { throw 'Assertion failed: real reparse leaf symlink (non-container) must return SKIP_TRACKED_SYMLINK' }
$assertionsPassed++

# 3.2 Non-reparse tracked symlink leaf
if ((Get-InventoryAction '120000' $false $true $false $true) -ne 'SKIP_GIT_SYMLINK_NONREPARSE') { throw 'Assertion failed: mode 120000 ordinary non-reparse leaf must return SKIP_GIT_SYMLINK_NONREPARSE' }
$assertionsPassed++
if ((Get-InventoryAction '120000' $false $true $false $false) -ne 'STOP') { throw 'Assertion failed: unknown non-reparse object must STOP instead of skip' }
$assertionsPassed++

# 3.3 Non-reparse tracked symlink directory leaf (container) must STOP
if ((Get-InventoryAction '120000' $false $true $true $false) -ne 'STOP') { throw 'Assertion failed: mode 120000 directory container leaf must STOP' }
$assertionsPassed++

# 3.4 Traversable parents
if ((Get-InventoryAction '120000' $false $false $true $false) -ne 'HASH_REGULAR_FILE') { throw 'Assertion failed: parent directory for tracked symlink candidate must be traversable' }
$assertionsPassed++
if ((Get-InventoryAction '100644' $false $false $true $false) -ne 'HASH_REGULAR_FILE') { throw 'Assertion failed: ordinary parent directory must be traversable' }
$assertionsPassed++

# 3.5 Regular files
if ((Get-InventoryAction '100644' $false $true $false $true) -ne 'HASH_REGULAR_FILE') { throw 'Assertion failed: ordinary regular file must return HASH_REGULAR_FILE' }
$assertionsPassed++
if ((Get-InventoryAction '100755' $false $true $false $true) -ne 'HASH_REGULAR_FILE') { throw 'Assertion failed: executable regular file must return HASH_REGULAR_FILE' }
$assertionsPassed++

# 3.6 Untracked files
if ((Get-InventoryAction $null $false $true $false $true) -ne 'HASH_REGULAR_FILE') { throw 'Assertion failed: untracked regular file must hash' }
$assertionsPassed++
if ((Get-InventoryAction $null $true $true $false $false) -ne 'STOP') { throw 'Assertion failed: untracked reparse leaf must STOP' }
$assertionsPassed++

# 3.7 Error combinations and mismatched types
if ((Get-InventoryAction '100644' $false $true $true $false) -ne 'STOP') { throw 'Assertion failed: regular directory leaf must STOP' }
$assertionsPassed++
if ((Get-InventoryAction '100644' $true $true $false $true) -ne 'STOP') { throw 'Assertion failed: regular file with reparse point must STOP' }
$assertionsPassed++
if ((Get-InventoryAction '160000' $false $true $false $false) -ne 'STOP') { throw 'Assertion failed: submodule mode must STOP' }
$assertionsPassed++
if ((Get-InventoryAction '100666' $false $true $false $true) -ne 'STOP') { throw 'Assertion failed: invalid git mode must STOP' }
$assertionsPassed++
if ((Get-InventoryAction '100644' $true $false $true $false) -ne 'STOP') { throw 'Assertion failed: reparse parent directory must STOP' }
$assertionsPassed++
if (-not (Test-OrdinaryFileMetadata ([IO.FileInfo]) ([IO.FileAttributes]::Archive))) { throw 'Assertion failed: ordinary FileInfo metadata must be accepted' }
$assertionsPassed++
if (Test-OrdinaryFileMetadata ([string]) ([IO.FileAttributes]::Archive)) { throw 'Assertion failed: unknown provider object type must STOP' }
$assertionsPassed++
if (Test-OrdinaryFileMetadata ([IO.FileInfo]) ([IO.FileAttributes]::Device)) { throw 'Assertion failed: Device attributes must STOP' }
$assertionsPassed++
if (Test-OrdinaryFileMetadata ([IO.FileInfo]) ([IO.FileAttributes]::Archive -bor [IO.FileAttributes]::Compressed)) { throw 'Assertion failed: unknown attributes must STOP' }
$assertionsPassed++

# 3.8 Path sanitization
if (-not (Test-SafeRepositoryRelativePath '.tmp.driveupload/item')) { throw 'Assertion failed: canonical staging path must be accepted' }
$assertionsPassed++
foreach ($unsafe in @('.tmp.driveupload./x', '.tmp.driveupload /x', './.tmp.driveupload/x', '.tmp.driveupload/x:stream', '../.tmp.driveupload/x', '/.tmp.driveupload/x', '.tmp.driveupload//x', 'TMPDRI~1/183728')) {
    if (Test-SafeRepositoryRelativePath $unsafe) { throw "Assertion failed: unsafe repository path must be rejected: $unsafe" }
    $assertionsPassed++
}

# 3.9 User data staging path detection
if (-not (Test-UnreadUserDataStagingPath '.tmp.driveupload/183728')) { throw 'Assertion failed: staging path must be detected' }
$assertionsPassed++
if (-not (Test-UnreadUserDataStagingPath '.TMP.DRIVEUPLOAD/nested/item')) { throw 'Assertion failed: case-insensitive staging path must be detected' }
$assertionsPassed++
if (Test-UnreadUserDataStagingPath 'verification/P02/evidence.json') { throw 'Assertion failed: regular evidence path must not be treated as staging path' }
$assertionsPassed++

# 3.10 Link type evidence
if ((Get-LinkTypeEvidence ([pscustomobject]@{ LinkType = 'SymbolicLink' })) -ne 'SymbolicLink') { throw 'Assertion failed: LinkType metadata must be preserved' }
$assertionsPassed++
if ((Get-LinkTypeEvidence ([pscustomobject]@{})) -ne 'NOT_AVAILABLE_ON_ENGINE') { throw 'Assertion failed: missing LinkType must return NOT_AVAILABLE_ON_ENGINE' }
$assertionsPassed++
if ((Get-LinkTypeEvidence ([pscustomobject]@{ LinkType = '' })) -ne 'NOT_AVAILABLE_ON_ENGINE') { throw 'Assertion failed: empty LinkType must return NOT_AVAILABLE_ON_ENGINE' }
$assertionsPassed++

# 3.11 Detached symbolic-ref helper
$detachedSample = [pscustomobject]@{ exitCode = 128; stdoutBase64 = ''; stderrBase64 = 'ZmF0YWw6IHJlZiBIRUFEIGlzIG5vdCBhIHN5bWJvbGljIHJlZgo=' }
if (-not (Test-ExpectedDetachedBranchResult $detachedSample)) { throw 'Assertion failed: exact detached branch result must be accepted' }
$assertionsPassed++
$unexpectedDetached = [pscustomobject]@{ exitCode = 128; stdoutBase64 = ''; stderrBase64 = 'ZmF0YWw6IHJlZiBIRUFEIGVycm9yCg==' }
if (Test-ExpectedDetachedBranchResult $unexpectedDetached) { throw 'Assertion failed: unexpected symbolic-ref error must be rejected' }
$assertionsPassed++

# 3.12 Git NUL parser and index mode parser
$pathBytes = [Text.UTF8Encoding]::new($false).GetBytes("alpha`0beta`0")
$parsedPaths = Get-GitNulPaths $pathBytes
if ($parsedPaths.paths.Count -ne 2 -or $parsedPaths.nulTerminatorCount -ne 2) { throw 'Assertion failed: Get-GitNulPaths count mismatch' }
$assertionsPassed++
$modeText = '120000 ' + ('a' * 40) + " 0`tsymbolic-link`0"
$parsedModes = Get-GitIndexModes ([Text.UTF8Encoding]::new($false).GetBytes($modeText))
if ($parsedModes.entryCount -ne 1 -or $parsedModes.modes['symbolic-link'].mode -ne '120000' -or $parsedModes.modes['symbolic-link'].stage -ne 0) { throw 'Assertion failed: Get-GitIndexModes must preserve mode and stage 0' }
$assertionsPassed++
foreach ($stage in 1..3) {
    $stageRejected = $false
    try { $null = Get-GitIndexModes ([Text.UTF8Encoding]::new($false).GetBytes(('120000 ' + ('a' * 40) + " $stage`tsymbolic-link`0"))) }
    catch { $stageRejected = $true }
    if (-not $stageRejected) { throw "Assertion failed: Git index stage $stage must be rejected" }
    $assertionsPassed++
}
$duplicateStagePathRejected = $false
try { $null = Get-GitIndexModes ([Text.UTF8Encoding]::new($false).GetBytes(('100644 ' + ('a' * 40) + " 0`tduplicate`0" + '100755 ' + ('b' * 40) + " 0`tduplicate`0"))) }
catch { $duplicateStagePathRejected = $true }
if (-not $duplicateStagePathRejected) { throw 'Assertion failed: duplicate Git index paths must be rejected' }
$assertionsPassed++
$unknownModeRejected = $false
try { $null = Get-GitIndexModes ([Text.UTF8Encoding]::new($false).GetBytes(('100666 ' + ('a' * 40) + " 0`tunknown-mode`0"))) }
catch { $unknownModeRejected = $true }
if (-not $unknownModeRejected) { throw 'Assertion failed: unknown Git index modes must be rejected' }
$assertionsPassed++
$baselineHashA = 'a' * 64
$baselineHashB = 'b' * 64
$syntheticExpectedBaseline = [ordered]@{ statusSha256 = $baselineHashA; indexSha256 = $baselineHashA }
if (-not (Test-FrozenGitBaselineMatch $syntheticExpectedBaseline ([ordered]@{ statusSha256 = $baselineHashA; indexSha256 = $baselineHashA }))) { throw 'Assertion failed: exact synthetic frozen status/index hashes must match' }
$assertionsPassed++
if (Test-FrozenGitBaselineMatch $syntheticExpectedBaseline ([ordered]@{ statusSha256 = $baselineHashB; indexSha256 = $baselineHashA })) { throw 'Assertion failed: frozen status mismatch must stop' }
$assertionsPassed++
if (Test-FrozenGitBaselineMatch $syntheticExpectedBaseline ([ordered]@{ statusSha256 = $baselineHashA; indexSha256 = $baselineHashB })) { throw 'Assertion failed: frozen index mismatch must stop' }
$assertionsPassed++
if (Test-FrozenGitBaselineMatch ([ordered]@{ statusSha256 = $null; indexSha256 = $null }) ([ordered]@{ statusSha256 = $baselineHashA; indexSha256 = $baselineHashA })) { throw 'Assertion failed: missing frozen status/index values must be unprovable' }
$assertionsPassed++

# 4. AST Static Control Flow and Structure Guarantees on Target Script
# 4.1 Verify function definitions present in AST
$funcAsts = $ast.FindAll({ $args[0] -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true)
$funcNames = @($funcAsts | ForEach-Object { $_.Name })
foreach ($reqFunc in @('Get-InventoryAction', 'Test-OrdinaryFileMetadata', 'Test-FrozenGitBaselineMatch', 'Assert-InventoryPolicySelfCheck', 'Get-RepositoryRecord', 'Test-SafeRepositoryRelativePath', 'Test-UnreadUserDataStagingPath', 'Get-BoundedPhaseMap')) {
    if ($reqFunc -notin $funcNames) { throw "AST check failed: missing required function $reqFunc" }
    $assertionsPassed++
}

# 4.2 Verify the no-baseline guard and actual skip helper/control-flow contracts
$repoFuncAst = @($funcAsts | Where-Object { $_.Name -eq 'Get-RepositoryRecord' })[0]
$baselineAssignments = @($ast.FindAll({ $args[0] -is [System.Management.Automation.Language.AssignmentStatementAst] -and $args[0].Left.Extent.Text.Trim() -ceq '$FrozenGitBaselines' }, $true))
if ($baselineAssignments.Count -ne 1 -or $baselineAssignments[0].Extent.Text -notmatch 'main\s*=\s*\[ordered\]@\{\s*statusSha256\s*=\s*\$null;\s*indexSha256\s*=\s*\$null\s*\}' -or $baselineAssignments[0].Extent.Text -notmatch 'scratch\s*=\s*\[ordered\]@\{\s*statusSha256\s*=\s*\$null;\s*indexSha256\s*=\s*\$null\s*\}') {
    throw 'AST check failed: both frozen repository status/index hashes must remain explicitly unavailable.'
}
$assertionsPassed++

$baselineGuards = @($repoFuncAst.FindAll({ $args[0] -is [System.Management.Automation.Language.IfStatementAst] -and $args[0].Extent.Text -match '\$FrozenGitBaselines\[\$Name\]' -and $args[0].Extent.Text -match 'FROZEN_GIT_STATUS_INDEX_BASELINE_UNPROVABLE' }, $true))
if ($baselineGuards.Count -ne 1) { throw 'AST check failed: Get-RepositoryRecord must have one explicit unavailable-baseline fail-stop.' }
$baselineGuard = $baselineGuards[0]
$guardBlock = $baselineGuard.Clauses[0].Item2
if (@($guardBlock.FindAll({ $args[0] -is [System.Management.Automation.Language.ReturnStatementAst] }, $true)).Count -ne 1 -or @($guardBlock.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] -and $args[0].GetCommandName() -eq 'Set-RepositoryStop' }, $true)).Count -ne 1) {
    throw 'AST check failed: unavailable-baseline branch must record UNPROVABLE and return before queries.'
}
$repoIoNames = @('Get-PathChain', 'Get-Item', 'Get-FileRecord', 'Invoke-Git', 'Get-GitNulPaths', 'Get-GitIndexModes', 'Get-FileHash')
$earlyRepoIo = @($repoFuncAst.FindAll({ $args[0] -is [System.Management.Automation.Language.CommandAst] -and $args[0].GetCommandName() -in $repoIoNames -and $args[0].Extent.StartOffset -lt $baselineGuard.Extent.EndOffset }, $true))
if ($earlyRepoIo.Count -ne 0) { throw 'AST check failed: repository queries or inventory must follow the unavailable-baseline return.' }
$assertionsPassed++

$helperAsts = @{}
foreach ($helperName in @('Get-LinkTypeEvidence', 'Set-RepositoryStop')) {
    $helperAst = @($funcAsts | Where-Object { $_.Name -ceq $helperName })[0]
    if (-not (Test-SkipHelperAstContract $helperAst)) { throw "AST check failed: helper $helperName must match its exact in-memory receiver/method/argument allowlist." }
    $helperAsts[$helperName] = $helperAst
    $assertionsPassed++
}
$legalHelperPositiveSource = @'
function Get-LinkTypeEvidence {
    [string]::IsNullOrEmpty([string]$property.Value)
}
'@
$legalHelperPositiveAst = Get-ParsedFunctionAst $legalHelperPositiveSource 'Get-LinkTypeEvidence'
if (-not (Test-SkipHelperAstContract $legalHelperPositiveAst)) { throw 'AST mutation self-check failed: legal exact helper invocation must be accepted.' }
$assertionsPassed++
$helperExternalFileRead = @'
function Get-LinkTypeEvidence {
    [string]::IsNullOrEmpty([string]$property.Value)
    [System.IO.File]::ReadAllText('C:\protected')
}
'@
$helperExternalItemQuery = @'
function Set-RepositoryStop {
    [Math]::Max(0, $Record.candidateCount - $Record.processedCount)
    Get-Item -LiteralPath 'C:\protected'
}
'@
$helperMutationCases = @(
    [pscustomobject]@{ name = 'external static file read'; functionName = 'Get-LinkTypeEvidence'; source = $helperExternalFileRead },
    [pscustomobject]@{ name = 'external item query'; functionName = 'Set-RepositoryStop'; source = $helperExternalItemQuery }
)
foreach ($mutation in $helperMutationCases) {
    $mutatedHelperAst = Get-ParsedFunctionAst $mutation.source $mutation.functionName
    if ($null -eq $mutatedHelperAst) { throw "AST mutation fixture failed to parse: $($mutation.name)" }
    if (Test-SkipHelperAstContract $mutatedHelperAst) { throw "AST mutation self-check failed: unsafe helper was accepted: $($mutation.name)" }
    $assertionsPassed++
}

if (-not (Test-RepositorySkipAstContract $repoFuncAst)) { throw 'AST check failed: the real component loop, complete skip branches, and direct outer continue do not satisfy the allowlisted control-flow contract.' }
$assertionsPassed++
$repositoryFunctionSource = $repoFuncAst.Extent.Text
$trackedBranchAnchor = 'if ($action -eq ''SKIP_TRACKED_SYMLINK'') {'
$continueBranchAnchor = 'if ($linkSkipped) { continue }'
$sourceLineBreak = [Environment]::NewLine
$trackedBranchStart = $repositoryFunctionSource.IndexOf($trackedBranchAnchor, [StringComparison]::Ordinal)
if ($trackedBranchStart -lt 0) { throw 'AST mutation self-check fixture failed: tracked branch anchor is missing.' }
$prefixAnchor = '$linkSkipped = $false'
$prefixAnchorStart = $repositoryFunctionSource.IndexOf($prefixAnchor, [StringComparison]::Ordinal)
$componentLoopAnchor = 'for ($partIndex = 0; $partIndex -lt $parts.Count; $partIndex++) {'
$componentLoopStart = $repositoryFunctionSource.IndexOf($componentLoopAnchor, [StringComparison]::Ordinal)
if ($prefixAnchorStart -lt 0 -or $componentLoopStart -le ($prefixAnchorStart + $prefixAnchor.Length)) { throw 'AST mutation self-check fixture failed: candidate prefix boundary is missing or reversed.' }
$breakStart = $repositoryFunctionSource.IndexOf('break', ($trackedBranchStart + $trackedBranchAnchor.Length), [StringComparison]::Ordinal)
$flagStart = $repositoryFunctionSource.IndexOf('$linkSkipped = $true', ($trackedBranchStart + $trackedBranchAnchor.Length), [StringComparison]::Ordinal)
$mutations = @(
    [pscustomobject]@{ name = 'hash before skip decision'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $trackedBranchAnchor -InsertedText ('Get-FileHash -LiteralPath $full -Algorithm SHA256' + $sourceLineBreak + '                ') },
    [pscustomobject]@{ name = 'ACL query inside skip branch'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $trackedBranchAnchor -InsertedText ($sourceLineBreak + '                    Get-Acl -LiteralPath $full' + $sourceLineBreak + '                    ') -After },
    [pscustomobject]@{ name = 'directory enumeration inside skip branch'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $trackedBranchAnchor -InsertedText ($sourceLineBreak + '                    Get-ChildItem -LiteralPath $full' + $sourceLineBreak + '                    ') -After },
    [pscustomobject]@{ name = 'target content read inside skip branch'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $trackedBranchAnchor -InsertedText ($sourceLineBreak + '                    [IO.File]::ReadAllText($full)' + $sourceLineBreak + '                    ') -After },
    [pscustomobject]@{ name = 'ACL query after component break'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor 'break' -InsertedText ($sourceLineBreak + '                    Get-Acl -LiteralPath $full' + $sourceLineBreak + '                    ') -After -StartIndex $breakStart },
    [pscustomobject]@{ name = 'protected state write inside skip branch'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $trackedBranchAnchor -InsertedText ($sourceLineBreak + '                    $record.state = ''CAPTURED''' + $sourceLineBreak + '                    ') -After },
    [pscustomobject]@{ name = 'skip evidence state changed'; source = New-SourceReplacement -Source $repositoryFunctionSource -Anchor "state = 'SKIPPED_SYMLINK_NOT_FOLLOWED'" -Replacement "state = 'TARGET_READ'" },
    [pscustomobject]@{ name = 'component break removed'; source = New-SourceReplacement -Source $repositoryFunctionSource -Anchor 'break' -Replacement '' -StartIndex $breakStart },
    [pscustomobject]@{ name = 'skip flag bypasses outer continue'; source = New-SourceReplacement -Source $repositoryFunctionSource -Anchor '$linkSkipped = $true' -Replacement '$linkSkipped = $false' -StartIndex $flagStart },
    [pscustomobject]@{ name = 'outer continue removed'; source = New-SourceReplacement -Source $repositoryFunctionSource -Anchor $continueBranchAnchor -Replacement '' },
    [pscustomobject]@{ name = 'ACL query in component-loop to continue gap'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $continueBranchAnchor -InsertedText ('Get-Acl -LiteralPath $full' + $sourceLineBreak + '            ') }
)
$mutations += @(
    [pscustomobject]@{ name = 'candidate prefix ACL query'; expectedSnippet = 'Get-Acl -LiteralPath $full'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $prefixAnchor -InsertedText ($sourceLineBreak + '            Get-Acl -LiteralPath $full' + $sourceLineBreak + '            ') -After -StartIndex $prefixAnchorStart },
    [pscustomobject]@{ name = 'candidate prefix target content read'; expectedSnippet = '[IO.File]::ReadAllText($full)'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $prefixAnchor -InsertedText ($sourceLineBreak + '            [IO.File]::ReadAllText($full)' + $sourceLineBreak + '            ') -After -StartIndex $prefixAnchorStart },
    [pscustomobject]@{ name = 'candidate prefix content hash'; expectedSnippet = 'Get-FileHash -LiteralPath $full -Algorithm SHA256'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $prefixAnchor -InsertedText ($sourceLineBreak + '            Get-FileHash -LiteralPath $full -Algorithm SHA256' + $sourceLineBreak + '            ') -After -StartIndex $prefixAnchorStart },
    [pscustomobject]@{ name = 'candidate prefix directory enumeration'; expectedSnippet = 'Get-ChildItem -LiteralPath $full'; source = New-SourceInsertion -Source $repositoryFunctionSource -Anchor $prefixAnchor -InsertedText ($sourceLineBreak + '            Get-ChildItem -LiteralPath $full' + $sourceLineBreak + '            ') -After -StartIndex $prefixAnchorStart }
)
foreach ($mutation in $mutations) {
    if ([string]::IsNullOrEmpty($mutation.source)) { throw "AST mutation fixture failed to apply: $($mutation.name)" }
    if (-not [string]::IsNullOrEmpty($mutation.expectedSnippet)) {
        $mutationStart = $mutation.source.IndexOf($mutation.expectedSnippet, ($prefixAnchorStart + $prefixAnchor.Length), [StringComparison]::Ordinal)
        $mutatedComponentLoopStart = $mutation.source.IndexOf($componentLoopAnchor, ($prefixAnchorStart + $prefixAnchor.Length), [StringComparison]::Ordinal)
        if ($mutationStart -lt ($prefixAnchorStart + $prefixAnchor.Length) -or $mutatedComponentLoopStart -le $mutationStart) { throw "AST mutation fixture missed the candidate prefix boundary: $($mutation.name)" }
    }
    $mutatedRepositoryAst = Get-ParsedFunctionAst $mutation.source 'Get-RepositoryRecord'
    if ($null -eq $mutatedRepositoryAst) { throw "AST mutation fixture failed to parse: $($mutation.name)" }
    if (Test-RepositorySkipAstContract $mutatedRepositoryAst) { throw "AST mutation self-check failed: unsafe real control flow was accepted: $($mutation.name)" }
    $assertionsPassed++
}

# 4.3 Verify task and evidence targets in AST
if ($ast.Extent.Text -notmatch 'task\s*=\s*''P02PRE-R1H''') {
    throw 'AST check failed: task metadata must be P02PRE-R1H'
}
$assertionsPassed++
if ($ast.Extent.Text -notmatch 'p02pre-r1h-manifest-20261012\.md') {
    throw 'AST check failed: manifest metadata must be p02pre-r1h-manifest-20261012.md'
}
$assertionsPassed++
if ($ast.Extent.Text -notmatch 'p02pre-r1h-evidence-20261012\.json') {
    throw 'AST check failed: evidence path must target p02pre-r1h-evidence-20261012.json'
}
$assertionsPassed++

# 5. Output Summary
$summary = [ordered]@{
    task = 'P02PRE-R1H'
    targetScript = $TargetCaptureScript
    parseErrors = 0
    assertionsPassed = $assertionsPassed
    status = 'PASS'
    astControlFlowChecked = $true
    skipBranchNoExternalCalls = $true
    frozenStatusIndexBaseline = 'UNPROVABLE; capture stops before repository queries or inventory'
    isolationConfirmed = 'No capture, git, host getter, registry, ACL, build, cargo or AC invoked.'
}

$summaryJson = ConvertTo-Json -InputObject $summary -Depth 4
Write-Output $summaryJson
