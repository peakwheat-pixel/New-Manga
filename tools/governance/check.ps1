[CmdletBinding()]
param(
    [string]$TaskPath
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Add-Error([string]$Message) { $script:errors.Add($Message) }
function Add-Warning([string]$Message) { $script:warnings.Add($Message) }

$script:evidenceExceptions = @()
$script:evidenceExceptionIndex = @{}
$script:evidenceExceptionEligibility = @{}
$script:evidenceExceptionBaseline = $null
# Frozen eligibility baseline for historical six-column inference (Codex ruling 2026-11-16)
$script:frozenEvidenceBaseline = '8db997f94683c6c959c30ba672af6df5d1bbc977'

# Historical-pin exceptions (Codex ruling Q1=B, doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-GATE-RULING-2026-11-16.md).
# A row may only be downgraded to a warning when the registry entry matches the row on EVERY
# field AND the row provably existed, unchanged, in a terminal card at the frozen baseline.
function Initialize-EvidenceExceptions([string]$RegistryPath) {
    if (-not (Test-Path -LiteralPath $RegistryPath -PathType Leaf)) { return }
    try { $doc = (Get-Content -LiteralPath $RegistryPath -Raw) | ConvertFrom-Json }
    catch { Add-Error 'EVIDENCE_EXCEPTION_REGISTRY_INVALID: 例外登记表不是合法 JSON。'; return }
    $required = @('schema_version', 'eligibility_baseline', 'entries')
    $names = @($doc.PSObject.Properties.Name)
    foreach ($k in $required) {
        if ($names -notcontains $k) { Add-Error "EVIDENCE_EXCEPTION_REGISTRY_INVALID: 缺少字段 $k"; return }
    }
    $extraTop = @($names | Where-Object { $required -notcontains $_ })
    if ($extraTop.Count -gt 0) { Add-Error "EVIDENCE_EXCEPTION_REGISTRY_INVALID: 未登记字段 $($extraTop -join ',')"; return }
    if ([string]$doc.schema_version -ne '1') { Add-Error 'EVIDENCE_EXCEPTION_REGISTRY_INVALID: schema_version 必须为 1'; return }
    $baseline = [string]$doc.eligibility_baseline
    if ($baseline -notmatch '^[0-9a-f]{40}$') {
        Add-Error "EVIDENCE_EXCEPTION_BASELINE_INVALID: 资格基线必须是完整 40 位 commit：$baseline"; return
    }
    & git -C $repoRoot cat-file -e "${baseline}^{commit}" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Add-Error "EVIDENCE_EXCEPTION_BASELINE_UNRESOLVED: 资格基线在本仓不可解析：$baseline"; return
    }
    $script:evidenceExceptionBaseline = $baseline
    $entryKeys = @('id', 'card', 'task_id', 'evidence_id', 'path', 'commit', 'sha256', 'class',
                   'error_type', 'reason', 'ruling', 'expires_when')
    $allowedTypes = @('SHA_MISMATCH', 'PATH_MISSING', 'COMMIT_PATH_MISSING', 'COMMIT_FORMAT', 'SHA_MULTI')
    $seenIds = @{}
    foreach ($e in @($doc.entries)) {
        $enames = @($e.PSObject.Properties.Name)
        $missing = @($entryKeys | Where-Object { $enames -notcontains $_ })
        $extra = @($enames | Where-Object { $entryKeys -notcontains $_ })
        if ($missing.Count -gt 0 -or $extra.Count -gt 0) {
            Add-Error "EVIDENCE_EXCEPTION_SCHEMA: 条目字段必须恰为 $($entryKeys -join ',')：$($e.id)"
            continue
        }
        if ($allowedTypes -notcontains [string]$e.error_type) {
            Add-Error "EVIDENCE_EXCEPTION_ERROR_TYPE: 不允许的登记错误类型：$($e.id)"
            continue
        }
        if (([string]$e.path) -match '[\*\?\[\]]' -or ([string]$e.evidence_id) -match '[\*\?\[\]]') {
            Add-Error "EVIDENCE_EXCEPTION_WILDCARD: 登记项不得含通配符：$($e.id)"
            continue
        }
        $shaValues = @($e.sha256 | ForEach-Object { ([string]$_).Trim().ToLowerInvariant() })
        if ($shaValues.Count -eq 0 -or $shaValues.Count -gt 8) {
            Add-Error "EVIDENCE_EXCEPTION_SHA_INVALID: 登记项的 sha256 必须是 1-8 个摘要：$($e.id)"
            continue
        }
        $shaBad = @($shaValues | Where-Object { $_ -notmatch '^[0-9a-f]{64}$' })
        if ($shaBad.Count -gt 0) {
            Add-Error "EVIDENCE_EXCEPTION_SHA_INVALID: 登记项的 sha256 必须是 64 位小写十六进制：$($e.id)"
            continue
        }
        $proseCommit = ([string]$e.error_type -eq 'COMMIT_FORMAT')
        if ($proseCommit) {
            # ruling Q1=A: the prose commit must be recorded verbatim, so any
            # non-empty text is allowed for this hook (and only this hook).
            if ([string]::IsNullOrWhiteSpace([string]$e.commit)) {
                Add-Error "EVIDENCE_EXCEPTION_COMMIT_INVALID: COMMIT_FORMAT 登记项必须逐字记录异常的 commit 原文：$($e.id)"
                continue
            }
        } elseif (([string]$e.commit) -notmatch '^([0-9a-f]{7,40}|-)$') {
            Add-Error "EVIDENCE_EXCEPTION_COMMIT_INVALID: 登记项的 commit 必须是 7-40 位十六进制或 -：$($e.id)"
            continue
        }
        if ($seenIds.ContainsKey([string]$e.id)) {
            Add-Error "EVIDENCE_EXCEPTION_DUPLICATE_ID: 登记项 id 重复：$($e.id)"; continue
        }
        $seenIds[[string]$e.id] = $true
        $commitKey = if ([string]$e.commit -eq '-') { '' } else { [string]$e.commit }
        $shaKey = (($shaValues) -join ',')
        $key = @($e.card, $e.task_id, $e.evidence_id, $e.path, $commitKey, $shaKey,
                 $e.class, $e.error_type) -join '|'
        if ($script:evidenceExceptionIndex.ContainsKey($key)) {
            Add-Error "EVIDENCE_EXCEPTION_DUPLICATE_ROW: 同一行指纹被登记两次：$($e.id)"; continue
        }
        $script:evidenceExceptionIndex[$key] = $e
        $script:evidenceExceptions += $e
    }
}

function Test-EvidenceExceptionEligibility($Entry) {
    $id = [string]$Entry.id
    if ($script:evidenceExceptionEligibility.ContainsKey($id)) {
        return [bool]$script:evidenceExceptionEligibility[$id]
    }
    $ok = $false
    $baseline = $script:evidenceExceptionBaseline
    if ($baseline) {
        & git -C $repoRoot cat-file -e "${baseline}:$($Entry.card)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $cardText = ((& git -C $repoRoot cat-file blob "${baseline}:$($Entry.card)" 2>$null) -join "`n")
            $statusLine = [regex]::Match($cardText, '(?m)^status:\s*(\S+)\s*$')
            $terminal = $statusLine.Success -and
                (@('done', 'closed_with_limitations') -contains $statusLine.Groups[1].Value.ToLowerInvariant())
            if ($terminal) {
                $escape = [regex]::Escape([string]$Entry.evidence_id)
                $rowLine = [regex]::Match($cardText, "(?m)^\|\s*$escape\s*\|.*$")
                if ($rowLine.Success) {
                    $cells = @($rowLine.Value.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim().Trim('`').Trim() })
                    $hexRe = '^[0-9a-fA-F]{7,40}$'
                    $baseCommit = ([string]$cells[3]).Trim()
                    $entryCommit = ([string]$Entry.commit).Trim()
                    # A non-hex commit is a representation of "no usable commit": `-`,
                    # empty and prose forms are all the same fact for eligibility.
                    $commitOk = ($baseCommit -eq $entryCommit) -or
                        (($baseCommit -notmatch $hexRe) -and ($entryCommit -notmatch $hexRe))
                    $shaOk = $false
                    $listed = @($Entry.sha256 | ForEach-Object { ([string]$_).Trim().ToLowerInvariant() })
                    if ($listed.Count -gt 0) {
                        $cellDigests = @([regex]::Matches([string]$cells[4], '[0-9a-fA-F]{64}') | ForEach-Object { $_.Value.ToLowerInvariant() })
                        $shaOk = (($listed -join ',') -eq ($cellDigests -join ','))
                    }
                    if ($cells.Count -ge 6 -and
                        $cells[2] -eq $Entry.path -and
                        $commitOk -and
                        $shaOk -and
                        $cells[5].ToUpperInvariant() -eq ([string]$Entry.class).ToUpperInvariant()) {
                        $ok = $true
                    }
                }
            }
        }
    }
    $script:evidenceExceptionEligibility[$id] = $ok
    return [bool]$ok
}

function Get-EvidenceException([string]$ErrorType, [string]$TaskId, [string]$EvidenceId,
                              [string]$Path, [string]$Commit, [string]$Sha, [string]$Class,
                              [string]$CommitRaw = $null, [string]$ShaRaw = $null) {
    if ($script:evidenceExceptions.Count -eq 0) { return $null }
    # Ruling condition 4: an exception lapses as soon as the card is reopened.
    $currentStatus = ''
    if ($metadata -and $metadata.ContainsKey('status')) { $currentStatus = ([string]$metadata['status']).ToLowerInvariant() }
    if (@('done', 'closed_with_limitations') -notcontains $currentStatus) {
        return $null
    }
    $cardRel = [IO.Path]::GetRelativePath($repoRoot, $TaskPath).Replace('\', '/')
    $commitKey = if ($Commit -match '^[0-9a-fA-F]{7,40}$') { $Commit } else { '' }
    # A cell may carry several digests; the registry stores them as an ordered list,
    # so the lookup key must use the same joined form.
    $shaKeyInput = $Sha
    $shaDigits = @([regex]::Matches([string]$Sha, '[0-9a-fA-F]{64}') | ForEach-Object { $_.Value.ToLowerInvariant() })
    if ($shaDigits.Count -gt 1) { $shaKeyInput = ($shaDigits -join ',') }
    $key = @($cardRel, $TaskId, $EvidenceId, $Path, $commitKey, $shaKeyInput, $Class, $ErrorType) -join '|'
    if ($ErrorType -eq 'COMMIT_FORMAT') {
        # the prose commit must be recorded verbatim (ruling Q1=A)
        $rawKey = if ($null -ne $CommitRaw) { $CommitRaw } else { $Commit }
        $found = $null
        foreach ($candidate in $script:evidenceExceptions) {
            if ($candidate.card -eq $cardRel -and $candidate.task_id -eq $TaskId -and
                $candidate.evidence_id -eq $EvidenceId -and $candidate.path -eq $Path -and
                $candidate.class.ToUpperInvariant() -eq $Class -and
                [string]$candidate.error_type -eq 'COMMIT_FORMAT' -and
                [string]$candidate.commit -eq $rawKey) { $found = $candidate; break }
        }
        if (-not $found) { return $null }
        if (-not (Test-EvidenceExceptionEligibility $found)) {
            Add-Warning "EVIDENCE_EXCEPTION_INELIGIBLE: 登记项 $($found.id) 在资格基线中不成立，仍按错误处理。"
            return $null
        }
        return $found
    }
    if ($ErrorType -eq 'SHA_MULTI') {
        $rawDigests = @([regex]::Matches([string]$ShaRaw, '[0-9a-fA-F]{64}') | ForEach-Object { $_.Value.ToLowerInvariant() })
        $joined = $rawDigests -join ','
        $found = $null
        foreach ($candidate in $script:evidenceExceptions) {
            $listed = @($candidate.sha256 | ForEach-Object { ([string]$_).Trim().ToLowerInvariant() })
            if ($candidate.card -eq $cardRel -and $candidate.task_id -eq $TaskId -and
                $candidate.evidence_id -eq $EvidenceId -and $candidate.path -eq $Path -and
                $candidate.class.ToUpperInvariant() -eq $Class -and
                [string]$candidate.error_type -eq 'SHA_MULTI' -and
                (($listed -join ',') -eq $joined)) { $found = $candidate; break }
        }
        if (-not $found) { return $null }
        if (-not (Test-EvidenceExceptionEligibility $found)) {
            Add-Warning "EVIDENCE_EXCEPTION_INELIGIBLE: 登记项 $($found.id) 在资格基线中不成立，仍按错误处理。"
            return $null
        }
        return $found
    }
    if (-not $script:evidenceExceptionIndex.ContainsKey($key)) { return $null }
    $entry = $script:evidenceExceptionIndex[$key]
    if (-not (Test-EvidenceExceptionEligibility $entry)) {
        Add-Warning "EVIDENCE_EXCEPTION_INELIGIBLE: 登记项 $($entry.id) 在资格基线中不成立（行不存在、字段已变或卡片当时非终态），仍按错误处理。"
        return $null
    }
    return $entry
}

function Resolve-LocalPath([string]$Value, [string]$BaseDirectory) {
    $path = $Value.Trim().Trim('`').Trim('<', '>')
    if ([string]::IsNullOrWhiteSpace($path)) { return $null }
    $path = [uri]::UnescapeDataString(($path -split '[?#]', 2)[0])
    if ($path -match '^(?i:https?|mailto|codex)://' -or $path.StartsWith('#')) { return $null }
    $path = $path.Replace('/', [IO.Path]::DirectorySeparatorChar)
    if (-not [IO.Path]::IsPathRooted($path)) { $path = Join-Path $BaseDirectory $path }
    return [IO.Path]::GetFullPath($path)
}

function Get-FrontMatter([string]$Text) {
    $match = [regex]::Match($Text, '(?s)^---\s*\r?\n(?<body>.*?)\r?\n---\s*(?:\r?\n|$)')
    $fields = @{}
    if (-not $match.Success) { return $fields }
    foreach ($line in ($match.Groups['body'].Value -split '\r?\n')) {
        if ($line -match '^([A-Za-z0-9_-]+):\s*(.*?)\s*$') {
            $value = $Matches[2].Trim().Trim("'").Trim('"')
            $fields[$Matches[1]] = $value
        }
    }
    return $fields
}

function Get-Section([string]$Text, [string]$Heading) {
    $pattern = '(?ms)^##\s+' + [regex]::Escape($Heading) + '\s*\r?\n(?<body>.*?)(?=^##\s+|\z)'
    $match = [regex]::Match($Text, $pattern)
    if ($match.Success) { return $match.Groups['body'].Value }
    return ''
}

function Get-TableRows([string]$Section) {
    $rows = [System.Collections.Generic.List[object]]::new()
    foreach ($line in ($Section -split '\r?\n')) {
        if ($line -notmatch '^\s*\|.*\|\s*$') { continue }
        $cells = @($line.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim().Trim('`') })
        if ($cells.Count -gt 0 -and $cells[0] -notmatch '^[-: ]+$' -and $cells[0] -notmatch '^(?i:evidence_id|resource_type)$') { $rows.Add($cells) }
    }
    return $rows
}

$script:blobFormCache = @{}
$script:baselineCardCache = @{}
$script:baselineRowCache = @{}

# Byte-level EOL forms (Codex ruling Q1=A, 2026-11-16): only CRLF<->LF is
# applied.  The derivation is refused for bytes containing NUL or a lone CR, so
# a mixed or binary payload can never match through a transformation.
function Get-ByteForms([byte[]]$Bytes) {
    if ($null -eq $Bytes) { return $null }
    foreach ($b in $Bytes) { if ($b -eq 0) { return $null } }
    $lf = [System.Collections.Generic.List[byte]]::new()
    $crlfPairs = 0
    $bareLf = 0
    for ($i = 0; $i -lt $Bytes.Length; $i++) {
        if ($Bytes[$i] -eq 13) {
            if ($i + 1 -ge $Bytes.Length -or $Bytes[$i + 1] -ne 10) { return $null }  # lone CR
            $crlfPairs++
            continue
        }
        if ($Bytes[$i] -eq 10) {
            if ($i -eq 0 -or $Bytes[$i - 1] -ne 13) { $bareLf++ }
        }
        $lf.Add($Bytes[$i])
    }
    # Ruling condition 3: a MIXED payload has no derived form at all -- only its
    # exact raw bytes may match.
    if ($crlfPairs -gt 0 -and $bareLf -gt 0) {
        $shaOnly = [System.Security.Cryptography.SHA256]::Create()
        try { return @{ Raw = [Convert]::ToHexString($shaOnly.ComputeHash($Bytes)).ToLowerInvariant() } }
        finally { $shaOnly.Dispose() }
    }
    $lfBytes = $lf.ToArray()
    $crlf = [System.Collections.Generic.List[byte]]::new()
    foreach ($b in $lfBytes) {
        if ($b -eq 10) { $crlf.Add(13) }
        $crlf.Add($b)
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return @{
            Raw = [Convert]::ToHexString($sha.ComputeHash($Bytes)).ToLowerInvariant()
            LF = [Convert]::ToHexString($sha.ComputeHash($lfBytes)).ToLowerInvariant()
            CRLF = [Convert]::ToHexString($sha.ComputeHash($crlf.ToArray())).ToLowerInvariant()
        }
    } finally { $sha.Dispose() }
}

function Get-GitBlobBytes([string]$Commit, [string]$RepoRelativePath) {
    $process = [System.Diagnostics.Process]::new()
    $memory = [System.IO.MemoryStream]::new()
    try {
        $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
        $startInfo.FileName = 'git'
        $startInfo.WorkingDirectory = $repoRoot
        $startInfo.UseShellExecute = $false
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        [void]$startInfo.ArgumentList.Add('cat-file')
        [void]$startInfo.ArgumentList.Add('blob')
        [void]$startInfo.ArgumentList.Add("${Commit}:$RepoRelativePath")
        $process.StartInfo = $startInfo
        if (-not $process.Start()) { return $null }
        $process.StandardOutput.BaseStream.CopyTo($memory)
        [void]$process.StandardError.ReadToEnd()
        $process.WaitForExit()
        if ($process.ExitCode -ne 0) { return $null }
        return $memory.ToArray()
    } catch { return $null } finally {
        $memory.Dispose()
        $process.Dispose()
    }
}

function Get-GitBlobForms([string]$Commit, [string]$RepoRelativePath) {
    $key = "${Commit}:$RepoRelativePath"
    if ($script:blobFormCache.ContainsKey($key)) { return $script:blobFormCache[$key] }
    $forms = Get-ByteForms (Get-GitBlobBytes $Commit $RepoRelativePath)
    $script:blobFormCache[$key] = $forms
    return $forms
}

function Get-WorktreeForms([string]$Path) {
    if (-not $Path -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try { return Get-ByteForms ([IO.File]::ReadAllBytes($Path)) } catch { return $null }
}

function Get-BaselineCardText([string]$CardRelative) {
    if ($script:baselineCardCache.ContainsKey($CardRelative)) {
        return $script:baselineCardCache[$CardRelative]
    }
    $text = $null
    $baseline = $script:frozenEvidenceBaseline
    if (-not $baseline) { $baseline = $script:evidenceExceptionBaseline }
    if ($baseline) {
        & git -C $repoRoot cat-file -e "${baseline}:$CardRelative" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $text = ((& git -C $repoRoot cat-file blob "${baseline}:$CardRelative" 2>$null) -join "`n")
        }
    }
    $script:baselineCardCache[$CardRelative] = $text
    return $text
}

# Six-column EOL inference is only allowed for rows that already existed, byte for
# byte, in a terminal card at the frozen baseline (ruling condition 4).
function Get-BaselineRowEligible([string]$CardRelative, [string]$EvidenceId, $Cells) {
    $key = "$CardRelative|$EvidenceId"
    if ($script:baselineRowCache.ContainsKey($key)) { return [bool]$script:baselineRowCache[$key] }
    $ok = $false
    $text = Get-BaselineCardText $CardRelative
    if ($text) {
        $status = [regex]::Match($text, '(?m)^status:\s*(\S+)\s*$')
        if ($status.Success -and (@('done', 'closed_with_limitations') -contains $status.Groups[1].Value.ToLowerInvariant())) {
            $escape = [regex]::Escape($EvidenceId)
            $rowLine = [regex]::Match($text, "(?m)^\|\s*$escape\s*\|.*$")
            if ($rowLine.Success) {
                $base = @($rowLine.Value.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim().Trim('`').Trim() })
                $now = @($Cells | ForEach-Object { ([string]$_).Trim().Trim('`').Trim() })
                $normCommit = { param($v) $x = ([string]$v).Trim(); if ($x -in @('', '-', 'null', 'none')) { '-' } else { $x } }
                $baseC = (& $normCommit $base[3]); $nowC = (& $normCommit $now[3])
                $hexRe = '^[0-9a-fA-F]{7,40}$'
                # A non-hex commit is a *representation* of "no usable commit", so the
                # baseline and the live row may write it differently (e.g. `-` vs `(见提交)`).
                $commitOk = ($baseC -eq $nowC) -or (($baseC -notmatch $hexRe) -and ($nowC -notmatch $hexRe))
                if ($base.Count -ge 6 -and $now.Count -ge 6 -and
                    $base[2] -eq $now[2] -and
                    $commitOk -and
                    $base[4].ToLowerInvariant() -eq $now[4].ToLowerInvariant() -and
                    $base[5].ToUpperInvariant() -eq $now[5].ToUpperInvariant()) {
                    $ok = $true
                }
            }
        }
    }
    $script:baselineRowCache[$key] = $ok
    return [bool]$ok
}

function Get-GitBlobSha256([string]$Commit, [string]$RepoRelativePath) {
    $process = [System.Diagnostics.Process]::new()
    $memory = [System.IO.MemoryStream]::new()
    $hashAlgorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
        $startInfo.FileName = 'git'
        $startInfo.WorkingDirectory = $repoRoot
        $startInfo.UseShellExecute = $false
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        [void]$startInfo.ArgumentList.Add('cat-file')
        [void]$startInfo.ArgumentList.Add('blob')
        [void]$startInfo.ArgumentList.Add("${Commit}:$RepoRelativePath")
        $process.StartInfo = $startInfo
        if (-not $process.Start()) { return $null }
        $process.StandardOutput.BaseStream.CopyTo($memory)
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        if ($process.ExitCode -ne 0) { return $null }
        $digest = $hashAlgorithm.ComputeHash($memory.ToArray())
        return [Convert]::ToHexString($digest).ToLowerInvariant()
    } catch {
        return $null
    } finally {
        $hashAlgorithm.Dispose()
        $memory.Dispose()
        $process.Dispose()
    }
}

function Get-RepoPathInfo([string]$Path, [string]$RepoRoot) {
    $relative = [IO.Path]::GetRelativePath($RepoRoot, $Path)
    $normalized = $relative.Replace('\', '/')
    $inside = -not [IO.Path]::IsPathRooted($relative) -and
        $normalized -ne '..' -and -not $normalized.StartsWith('../')
    return [pscustomobject]@{ Relative = $normalized; IsInside = $inside }
}

function Resolve-ManifestReference([string]$Section, [string]$RepoRoot) {
    # A Resource Manifest section may reference exactly one repository-relative JSON file.
    # Anything ambiguous or outside verification/** is refused rather than guessed at.
    $refs = [System.Collections.Generic.List[string]]::new()
    foreach ($m in [regex]::Matches($Section, '`([^`\s]+\.json)`')) { $refs.Add($m.Groups[1].Value.Trim()) }
    if ($refs.Count -eq 0) { return @{ Path = $null; Error = $null } }
    if ($refs.Count -gt 1) { return @{ Path = $null; Error = "Resource Manifest 引用了多个 JSON：$($refs -join ', ')" } }
    $ref = $refs[0]
    if ($ref -match '^(?i:[a-z]+:)' -or $ref.StartsWith('/') -or $ref.StartsWith('\')) {
        return @{ Path = $null; Error = "Resource Manifest 引用不得为绝对路径或 URL：$ref" }
    }
    if ($ref -match '[*?\[\]]') { return @{ Path = $null; Error = "Resource Manifest 引用不得含 glob：$ref" } }
    if ($ref -match '%[^%]+%' -or $ref -match '\$[A-Za-z_{(]') { return @{ Path = $null; Error = "Resource Manifest 引用不得含环境变量或宏：$ref" } }
    $full = Join-Path $RepoRoot ($ref -replace '/', [IO.Path]::DirectorySeparatorChar)
    $norm = $ref -replace '\\', '/'
    if ($norm -notmatch '^verification/') { return @{ Path = $null; Error = "Resource Manifest 引用必须位于 verification/**：$ref" } }
    if ($norm -match '\.\./') { return @{ Path = $null; Error = "Resource Manifest 引用不得越出仓库：$ref" } }
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { return @{ Path = $null; Error = "Resource Manifest 引用的文件不存在：$ref" } }
    $item = Get-Item -LiteralPath $full
    if ($item.LinkType) { return @{ Path = $null; Error = "Resource Manifest 引用不得为符号链接：$ref" } }
    return @{ Path = $full; Error = $null }
}

function Test-ExternalResourceManifest([string]$ManifestPath, [string]$TaskId, [string]$RepoRoot) {
    # Validates the referenced JSON against the fixed v1 schema, then applies the same
    # disposition rules the table path uses, plus the strict ALREADY_ABSENT semantics.
    $problems = [System.Collections.Generic.List[string]]::new()
    $notes = [System.Collections.Generic.List[string]]::new()
    try { $json = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch { return @{ Errors = @("Resource Manifest JSON 无法解析：$ManifestPath"); Resources = @() } }
    if ($json.schema_version -ne 1) { $problems.Add("Resource Manifest schema_version 必须为 1") }
    if ($json.task_id -ne $TaskId) { $problems.Add("Resource Manifest task_id '$($json.task_id)' 与 Task '$TaskId' 不一致") }
    if (-not $json.resources -or $json.resources.Count -eq 0) { $problems.Add("Resource Manifest resources 不得为空") }

    $allowed = @('DELETE_SAFE','MIGRATE','ARCHIVE','PRESERVE_REFERENCED','PRESERVE_USER_DATA','PRESERVE_UNKNOWN','NOT_APPLICABLE','ALREADY_ABSENT')
    $sameLocationSentinels = @(
        'Same ignored target/dist locations in this worktree',
        'Same source location',
        'Same shared build environment',
        'Same local cache location',
        'Same main-repository paths'
    )
    $counts = @{ deleted = 0; moved = 0; migrated = 0; archived = 0 }
    $resources = @()
    foreach ($res in $json.resources) {
        $disposition = ([string]$res.disposition).ToUpperInvariant()
        if ($disposition -notin $allowed) { $problems.Add("Resource disposition 无效：$disposition"); continue }
        if ([string]::IsNullOrWhiteSpace([string]$res.process_check)) { $problems.Add("Resource Manifest 缺少引用/进程检查结果：$($res.source_path)") }
        if ($res.deleted) { $counts.deleted++ }
        if ($res.moved) { $counts.moved++ }
        if ($res.modified -eq $null) { }

        $rawDest = if ($res.destination_path -ne $null) { [string]$res.destination_path } else { '' }
        $trimmedDest = $rawDest.Trim()
        $isSentinel = $sameLocationSentinels -contains $trimmedDest
        $isBlank = [string]::IsNullOrWhiteSpace($rawDest)
        $isDash = ($trimmedDest -eq '-')
        $isSameLocation = $isSentinel -or $isBlank -or $isDash

        if ($isSameLocation) {
            $destDesc = if ($isBlank) { '(blank)' } elseif ($isDash) { '-' } else { $rawDest }
            $resId = if (-not [string]::IsNullOrWhiteSpace([string]$res.resource_type)) {
                [string]$res.resource_type
            } elseif (-not [string]::IsNullOrWhiteSpace([string]$res.source_path)) {
                [string]$res.source_path
            } else {
                'resource'
            }
            $notes.Add("Resource '$resId' destination '$destDesc' 解释为同源，使用 source_path '$([string]$res.source_path)'")
        }

        if ($disposition -eq 'ALREADY_ABSENT') {
            if ([string]::IsNullOrWhiteSpace([string]$res.absent_evidence)) { $problems.Add("ALREADY_ABSENT 缺少 absent_evidence：$($res.source_path)") }
            $exprs = if ($isSameLocation) { @([string]$res.source_path) } else { @([string]$res.source_path, [string]$res.destination_path) }
            foreach ($expr in $exprs) {
                if ([string]::IsNullOrWhiteSpace($expr)) { continue }
                if ($expr -match '[{}*?\[\]]' -or $expr -match '%[^%]+%') { continue }
                # Resolve-LocalPath handles rooted paths; a bare Join-Path would glue an
                # absolute expression onto the repo root (G:\...\C:\Windows\...), making every
                # existing absolute target look absent and letting a fake disappearance pass.
                $cand = Resolve-LocalPath $expr $RepoRoot
                if ($cand -and (Test-Path -LiteralPath $cand)) { $problems.Add("ALREADY_ABSENT 但目标仍存在：$expr") }
            }
        } elseif ($disposition -eq 'NOT_APPLICABLE' -and ([string]$res.absent_evidence)) {
            $problems.Add("NOT_APPLICABLE 不得用于已消失资源：$($res.source_path)")
        }
        $resources += [pscustomobject]@{
            Disposition = $disposition
            Source = [string]$res.source_path
            Destination = [string]$res.destination_path
            Sha256 = [string]$res.sha256
            ManifestPath = [string]$res.manifest_path
            IsSameLocation = $isSameLocation
            IsSentinel = $isSentinel
        }
    }
    if ($json.closeout_counts) {
        foreach ($k in @('deleted','moved','migrated','archived')) {
            $declared = 0
            try { $declared = [int]$json.closeout_counts.$k } catch { $problems.Add("closeout_counts.$k 必须为整数") }
            if ($declared -lt 0) { $problems.Add("closeout_counts.$k 不得为负") }
        }
        # Declared counts are a record of closeout actions, which may cover files that are not
        # themselves listed in resources. P19-UI-FIX-1 declares moved=6 for six logs renamed
        # inside its evidence dir while all seven listed resources carry moved=false - accurate,
        # not inconsistent. Differences are surfaced as notes, never as failures.
        foreach ($k in @('deleted','moved','migrated','archived')) {
            $declared = 0
            try { $declared = [int]$json.closeout_counts.$k } catch { }
            if ($declared -ne $counts[$k]) { $notes.Add("closeout_counts.$k=$declared 与 resources 中布尔为 true 的项数 $($counts[$k]) 不同（声明口径包含未列入 resources 的处置动作）") }
        }
    } else { $problems.Add("Resource Manifest 缺少 closeout_counts") }
    return @{ Errors = $problems; Notes = $notes; Resources = $resources }
}

$staticFiles = @(
    'AGENTS.md',
    'doc/00_INDEX.md',
    'doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md',
    'doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md',
    'doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md',
    'doc/STATUS.md',
    'doc/REBASELINE_PLAN.md',
    'doc/09_COLLABORATION.md',
    'doc/WORKSPACE_GOVERNANCE.md',
    'doc/tasks/README.md',
    'doc/TASK_LEDGER.md',
    'doc/templates/TASK.md',
    'doc/templates/REVIEW.md',
    'doc/templates/HANDOFF.md'
)

foreach ($relative in $staticFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $relative) -PathType Leaf)) { Add-Error "缺少当前治理入口：$relative" }
}

$statusPath = Join-Path $repoRoot 'doc/STATUS.md'
$statusText = Get-Content -LiteralPath $statusPath -Raw
$activeMatch = [regex]::Match($statusText, '(?m)^-\s*当前 Task：.*?\((?<path>tasks/[^)]+\.md)\)')
$activeTaskPath = $null
$noCurrentTask = $false
if ($activeMatch.Success) { $activeTaskPath = [IO.Path]::GetFullPath((Join-Path (Join-Path $repoRoot 'doc') $activeMatch.Groups['path'].Value)) }
if (-not $TaskPath) {
    if (-not $activeMatch.Success) {
        foreach ($line in ($statusText -split '\r?\n')) {
            $emptyDeclaration = $line -match '^-\s*当前 Task：无[ \t]*$' -or
                $line -match '^-\s*当前 Task：无（[^）]*）[。]?[ \t]*$'
            if ($emptyDeclaration -and $line -notmatch '(?i)tasks[/\\]') { $noCurrentTask = $true; break }
        }
        if ($noCurrentTask) { Add-Warning 'STATUS 声明无当前 Task（空窗）；跳过当前 Task 检查。' }
        else { Add-Error 'STATUS 未提供可解析的当前 Task 指针。' }
    }
    else { $TaskPath = $activeTaskPath }
} elseif (-not [IO.Path]::IsPathRooted($TaskPath)) {
    $TaskPath = Join-Path $repoRoot $TaskPath
}

# r38 §5-3: the ledger must not go stale. doc/TASK_LEDGER.md is generated by
# tools/governance/task_ledger.py, so a task-status change without a rerun leaves
# a file that still claims yesterday's totals. Comparing the reported metrics
# against a fresh scan is cheap and catches exactly that.
$ledgerPath = Join-Path $repoRoot 'doc/TASK_LEDGER.md'
if (Test-Path -LiteralPath $ledgerPath -PathType Leaf) {
    $ledgerText = Get-Content -LiteralPath $ledgerPath -Raw
    $fresh = @{}
    $terminalSet = @('done', 'closed_with_limitations', 'cancelled', 'superseded', 'historical')
    $taskFiles = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'doc/tasks') -Filter '*.md' -File |
        Where-Object { $_.BaseName -ne 'README' })
    $nonTerminal = 0
    foreach ($f in $taskFiles) {
        $head = Get-Content -LiteralPath $f.FullName -TotalCount 40
        $st = $null
        foreach ($line in $head) {
            if ($line -match '^status:\s*(.+?)\s*$') { $st = $Matches[1].Trim('"', "'").ToLowerInvariant(); break }
        }
        if ($st -and $st -notin $terminalSet) { $nonTerminal++ }
    }
    $fresh['task files'] = $taskFiles.Count
    $fresh['non-terminal'] = $nonTerminal
    if ($ledgerText -match '\|\s*task files\s*\|\s*(\d+)\s*\|') {
        $declared = [int]$Matches[1]
        if ($declared -ne $fresh['task files']) {
            Add-Error "TASK_LEDGER 已过期：声明 $declared 个 Task，实际 $($fresh['task files']) 个（重跑 tools/governance/task_ledger.py --write）"
        }
    } else { Add-Error 'TASK_LEDGER 缺少 task files 指标。' }
    if ($ledgerText -match '\|\s*non-terminal\s*\|\s*(\d+)\s*\|') {
        $declared = [int]$Matches[1]
        if ($declared -ne $fresh['non-terminal']) {
            Add-Error "TASK_LEDGER 已过期：声明 $declared 个非终态 Task，实际 $($fresh['non-terminal']) 个（重跑 tools/governance/task_ledger.py --write）"
        }
    } else { Add-Error 'TASK_LEDGER 缺少 non-terminal 指标。' }
    if ($fresh['non-terminal'] -gt 0) {
        Add-Warning "存在 $($fresh['non-terminal']) 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）"
    }
}

$selectedFiles = [System.Collections.Generic.List[string]]::new()
foreach ($relative in $staticFiles) {
    $fullPath = Join-Path $repoRoot $relative
    if (Test-Path -LiteralPath $fullPath -PathType Leaf) { $selectedFiles.Add((Resolve-Path -LiteralPath $fullPath).Path) }
}
if ($TaskPath -and (Test-Path -LiteralPath $TaskPath -PathType Leaf)) {
    $TaskPath = (Resolve-Path -LiteralPath $TaskPath).Path
    if (-not $selectedFiles.Contains($TaskPath)) { $selectedFiles.Add($TaskPath) }
} elseif (-not $noCurrentTask) { Add-Error "当前 Task 文件不存在：$TaskPath" }

# Check only the declared current-document set and the selected Task; target files are existence-checked, not opened.
foreach ($file in $selectedFiles) {
    $text = Get-Content -LiteralPath $file -Raw
    foreach ($link in [regex]::Matches($text, '(?<!\!)\[[^\]]+\]\((?<target>[^)\s]+)(?:\s+[^)]*)?\)')) {
        $target = $link.Groups['target'].Value
        $resolved = Resolve-LocalPath $target (Split-Path -Parent $file)
        if ($resolved -and -not (Test-Path -LiteralPath $resolved)) { Add-Error "失效的本地引用：$([IO.Path]::GetRelativePath($repoRoot, $file)) → $target" }
    }
}

# 2026-10-31 (AD-003, rev r2 after FEA-00 Codex r1 R-03/R-04):
#   AD-002 keeps the 2026-10-26 sentinel as history; the CURRENT architecture sentinel
#   lives in AD-003. A PASS here is mechanical only and does NOT replace an architecture
#   review or an ADR adjudication.
#
# Scope of machine checking is BOUNDED ON PURPOSE. Only explicit "architecture assertion
# surfaces" are validated: the sentinel fields of AD-002/AD-003, a dedicated
# machine-checked field in doc/00_INDEX.md, and the AGENTS.md product-boundary line.
# Free prose is deliberately NOT scanned: a whole-file `-like` test can be satisfied by
# any incidental mention of the old string, and any line-wide regex sweep false-positives
# on legitimate historical notes ("...为 React + TypeScript；该表述已被取代"). Stale
# claims in prose are a REVIEW concern, not a regex concern; see
# doc/reviews/FEA-00-codex-r1.md R-04 for the accepted limitation.
$architecture = 'Windows + C#/.NET + Avalonia + Python Core + SQLite + Managed Copy'
$architectureCurrent = 'Windows + C#/.NET + Avalonia + Python Core + SQLite + ReferencedSource'

# Outside a code span, an odd run of backslashes escapes a backtick. Inside a
# code span backslashes are literal, so a matching closing run still closes it.
function Test-BacktickEscaped([string]$Text, [int]$Position) {
    $slashes = 0
    for ($j = $Position - 1; $j -ge 0 -and [int][char]$Text[$j] -eq 92; $j--) { $slashes++ }
    return ($slashes % 2) -eq 1
}

# Mask inline code with spaces so callers can inspect Markdown syntax without
# accepting examples as links. An unmatched delimiter masks the remainder.
function Hide-InlineCode([string]$Line) {
    $masked = [Text.StringBuilder]::new()
    $delimiterLength = 0
    $i = 0
    while ($i -lt $Line.Length) {
        if ([int][char]$Line[$i] -eq 96) {
            $start = $i
            while ($i -lt $Line.Length -and [int][char]$Line[$i] -eq 96) { $i++ }
            $length = $i - $start
            if ($delimiterLength -eq 0 -and (Test-BacktickEscaped $Line $start)) {
                # A backslash escapes only the first backtick in a run.
                [void]$masked.Append($Line[$start])
                $i = $start + 1
                continue
            }
            if ($delimiterLength -eq 0) { $delimiterLength = $length }
            elseif ($delimiterLength -eq $length) { $delimiterLength = 0 }
            [void]$masked.Append((' ' * $length))
        } else {
            if ($delimiterLength -eq 0) { [void]$masked.Append($Line[$i]) }
            else { [void]$masked.Append(' ') }
            $i++
        }
    }
    return $masked.ToString()
}

# Link-shaped text in HTML tag attributes and Markdown image descriptions is
# not a navigable link. Mask both contexts while preserving character offsets.
function Hide-NonLinkContexts([string]$Line) {
    $chars = (Hide-InlineCode $Line).ToCharArray()
    $inTag = $false
    $quote = 0
    $i = 0
    while ($i -lt $chars.Length) {
        $value = [int][char]$chars[$i]
        if ($inTag) {
            if ($quote -ne 0) {
                if ($value -eq $quote) { $quote = 0 }
            } elseif ($value -eq 34 -or $value -eq 39) { $quote = $value }
            elseif ($value -eq 62) { $inTag = $false }
            $chars[$i] = [char]32
            $i++
        } elseif ($value -eq 60 -and $i + 1 -lt $chars.Length -and
                  [string]$chars[$i + 1] -cmatch '[A-Za-z/!?]') {
            $inTag = $true
            $chars[$i] = [char]32
            $i++
        } elseif ($value -eq 33 -and $i + 1 -lt $chars.Length -and [int][char]$chars[$i + 1] -eq 91) {
            $depth = 0
            $chars[$i] = [char]32
            $i++
            while ($i -lt $chars.Length) {
                $value = [int][char]$chars[$i]
                if ($value -eq 91) { $depth++ }
                elseif ($value -eq 93) { $depth-- }
                $chars[$i] = [char]32
                $i++
                if ($depth -eq 0) { break }
            }
        } else { $i++ }
    }
    return -join $chars
}

# A block-level HTML construct may start after at most three spaces of
# indentation (CommonMark allows 0-3); anything else is inline content.
function Test-BlockHtmlStart([string]$Text, [int]$Position) {
    $lineStart = $Position
    while ($lineStart -gt 0 -and [int][char]$Text[$lineStart - 1] -ne 10) { $lineStart-- }
    if (($Position - $lineStart) -gt 3) { return $false }
    for ($k = $lineStart; $k -lt $Position; $k++) {
        if ([int][char]$Text[$k] -ne 32) { return $false }
    }
    return $true
}

# A paragraph whose inline-code backticks open on one line and close on a later
# line forms a CommonMark code span that spans lines. Content inside such a span
# is not a link or authority field, so mask it before looking for assertions.
# Same-line spans keep their original text (sentinel values are backtick-wrapped
# by design); only spans that actually cross a line break are masked.
function Mask-ParagraphCrossLineCode([string[]]$Lines, [hashtable]$BlockState) {
    $joined = [string]::Join("`n", $Lines)
    $chars = $joined.ToCharArray()
    $i = 0
    while ($i -lt $chars.Length) {
        # Block context is tracked on raw text only to decide where inline
        # delimiters can start; actual fence/HTML filtering happens later.
        if ($BlockState.Comment) {
            $end = $joined.IndexOf('-->', $i, [StringComparison]::Ordinal)
            if ($end -lt 0) { break }
            $BlockState.Comment = $false
            $i = $end + 3
            continue
        }
        if ($BlockState.HtmlTag) {
            $close = [regex]::Match($joined.Substring($i), '(?i)</\s*' + [regex]::Escape($BlockState.HtmlTag) + '\s*>')
            if (-not $close.Success) { break }
            $BlockState.HtmlTag = ''
            $i += $close.Index + $close.Length
            continue
        }
        if ($i -eq 0 -or [int][char]$chars[$i - 1] -eq 10) {
            $lineEnd = $joined.IndexOf("`n", $i, [StringComparison]::Ordinal)
            if ($lineEnd -lt 0) { $lineEnd = $chars.Length }
            $line = $joined.Substring($i, $lineEnd - $i)
            $fence = [regex]::Match($line, '^ {0,3}(`{3,}|~{3,})')
            if ($BlockState.InFence) {
                if ($fence.Success -and $fence.Groups[1].Value.Substring(0, 1) -ceq $BlockState.FenceChar -and
                    $fence.Groups[1].Value.Length -ge $BlockState.FenceLength -and
                    $line.Substring($fence.Length).Trim().Length -eq 0) { $BlockState.InFence = $false }
                $i = $lineEnd + 1
                continue
            }
            if ($fence.Success) {
                $BlockState.InFence = $true
                $BlockState.FenceChar = $fence.Groups[1].Value.Substring(0, 1)
                $BlockState.FenceLength = $fence.Groups[1].Value.Length
                $i = $lineEnd + 1
                continue
            }
        }
        # HTML comments suppress inline parsing wherever they start.
        if ([int][char]$chars[$i] -eq 60 -and
            $joined.Substring($i).StartsWith('<!--', [StringComparison]::Ordinal)) {
            $BlockState.Comment = $true
            $i += 4
            continue
        }
        # Block-level HTML suppresses inline parsing; an inline <pre>/<code> tag
        # does not. A type-1 <pre> may interrupt a paragraph, while a type-7
        # complete <code> tag line only starts a block at the paragraph start.
        if ([int][char]$chars[$i] -eq 60 -and (Test-BlockHtmlStart $joined $i)) {
            $blockTag = ''
            $openLength = 0
            $openPre = [regex]::Match($joined.Substring($i), '^(?i:<\s*(pre)(?=[\s>/]|$))')
            if ($openPre.Success) {
                $blockTag = 'pre'
                $openLength = $openPre.Length
            } else {
                $firstLineEnd = $joined.IndexOf("`n", [StringComparison]::Ordinal)
                if ($firstLineEnd -lt 0) { $firstLineEnd = $chars.Length }
                if ($i -lt $firstLineEnd) {
                    $openCode = [regex]::Match($joined.Substring($i), '^(?i:<\s*(code)(?:\s[^>]*)?>[ \t]*(?=\n|$))')
                    if ($openCode.Success) {
                        $blockTag = 'code'
                        $openLength = $openCode.Length
                    }
                }
            }
            if ($blockTag) {
                $BlockState.HtmlTag = $blockTag
                $i += $openLength
                continue
            }
        }
        if ([int][char]$chars[$i] -eq 96) {
            $start = $i
            while ($i -lt $chars.Length -and [int][char]$chars[$i] -eq 96) { $i++ }
            $length = $i - $start
            if (Test-BacktickEscaped $joined $start) { $i = $start + 1; continue }
            $closeEnd = -1
            $j = $i
            while ($j -lt $chars.Length) {
                if ([int][char]$chars[$j] -eq 96) {
                    $m = $j
                    while ($m -lt $chars.Length -and [int][char]$chars[$m] -eq 96) { $m++ }
                    if (($m - $j) -eq $length) { $closeEnd = $m; break }
                    $j = $m
                } else { $j++ }
            }
            if ($closeEnd -ge 0) {
                if ($joined.Substring($start, $closeEnd - $start).Contains("`n")) {
                    for ($k = $start; $k -lt $closeEnd; $k++) {
                        # Keep line breaks so the masked paragraph keeps its line structure.
                        if ([int][char]$chars[$k] -ne 10 -and [int][char]$chars[$k] -ne 13) { $chars[$k] = [char]32 }
                    }
                }
                $i = $closeEnd
            }
        } else { $i++ }
    }
    return (-join $chars) -split "`n"
}

# Only unquoted Markdown outside HTML comments, fenced code, HTML pre/code and
# multi-line inline code spans can declare an authority field. Historical prose
# remains outside this check.
function Get-AuthorityLines([string]$Relative) {
    $path = Join-Path $repoRoot $Relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-Error "缺少架构权威文档：$Relative"
        return
    }
    $text = Get-Content -LiteralPath $path -Raw

    # Find spans in raw paragraphs before removing any fence/HTML content.
    # Blank lines, ATX headings and line-start block openers end a paragraph.
    # Inline <pre>/<code> tags do not, and neither does a line-start <code>:
    # it is a type-7 HTML block, which cannot interrupt a paragraph.
    $rawLines = @($text -split '\r?\n')
    $maskedLines = [System.Collections.Generic.List[string]]::new()
    $paragraph = [System.Collections.Generic.List[string]]::new()
    $blockState = @{ Comment = $false; HtmlTag = ''; InFence = $false; FenceChar = ''; FenceLength = 0 }
    foreach ($rawLine in $rawLines) {
        $isBlockBoundary = $rawLine -match '^ {0,3}(?:#{1,6}(?:[ \t]+|$)|`{3,}|~{3,}|<!--|(?i:<\s*pre(?=[\s>/]|$)))'
        if ($rawLine.Trim().Length -eq 0 -or $isBlockBoundary) {
            if ($paragraph.Count -gt 0) {
                foreach ($maskedLine in (Mask-ParagraphCrossLineCode @($paragraph.ToArray()) $blockState)) { $maskedLines.Add($maskedLine) }
                $paragraph.Clear()
            }
            if ($rawLine.Trim().Length -gt 0) {
                foreach ($maskedLine in (Mask-ParagraphCrossLineCode @($rawLine) $blockState)) { $maskedLines.Add($maskedLine) }
            } else { $maskedLines.Add($rawLine) }
        } else { $paragraph.Add($rawLine) }
    }
    if ($paragraph.Count -gt 0) {
        foreach ($maskedLine in (Mask-ParagraphCrossLineCode @($paragraph.ToArray()) $blockState)) { $maskedLines.Add($maskedLine) }
    }
    $text = [string]::Join("`n", $maskedLines)
    $inFence = $false
    $fenceChar = ''
    $fenceLength = 0
    $htmlCodeTag = ''
    $htmlComment = $false
    $visibleLines = [System.Collections.Generic.List[string]]::new()
    foreach ($line in ($text -split '\r?\n')) {
        if (-not $htmlCodeTag -and -not $htmlComment) {
            $opening = [regex]::Match($line, '^ {0,3}(`{3,}|~{3,})')
            if ($opening.Success) {
                $marker = $opening.Groups[1].Value
                if (-not $inFence) {
                    $inFence = $true
                    $fenceChar = $marker.Substring(0, 1)
                    $fenceLength = $marker.Length
                } elseif ($marker.Substring(0, 1) -ceq $fenceChar -and $marker.Length -ge $fenceLength -and
                          $line.Substring($opening.Length).Trim().Length -eq 0) {
                    $inFence = $false
                }
                $visibleLines.Add('')
                continue
            }
            if ($inFence) { $visibleLines.Add(''); continue }
        }

        $visible = [Text.StringBuilder]::new()
        $remaining = $line
        while ($remaining.Length -gt 0) {
            if ($htmlComment) {
                $closeComment = $remaining.IndexOf('-->', [StringComparison]::Ordinal)
                if ($closeComment -lt 0) { break }
                $remaining = $remaining.Substring($closeComment + 3)
                $htmlComment = $false
            } elseif ($htmlCodeTag) {
                $close = [regex]::Match($remaining, '(?i)</\s*' + [regex]::Escape($htmlCodeTag) + '\s*>')
                if (-not $close.Success) { break }
                $remaining = $remaining.Substring($close.Index + $close.Length)
                $htmlCodeTag = ''
            } else {
                # Find HTML outside inline code, while retaining original text
                # (including backtick-wrapped sentinel values) in the output.
                $masked = Hide-InlineCode $remaining
                $open = [regex]::Match($masked, '(?i)<!--|<\s*(pre|code)(?=[\s>/]|$)')
                if (-not $open.Success) { [void]$visible.Append($remaining); break }
                [void]$visible.Append($remaining.Substring(0, $open.Index))
                if ($open.Value -ceq '<!--') { $htmlComment = $true }
                else { $htmlCodeTag = $open.Groups[1].Value }
                $remaining = $remaining.Substring($open.Index + $open.Length)
            }
        }
        $visibleLines.Add($visible.ToString())
    }

    foreach ($visibleLine in $visibleLines) {
        if ($visibleLine.Length -gt 0) { $visibleLine }
    }
}

function Assert-ArchitectureSurface {
    param([string]$Relative, [string]$Marker, [string]$ExpectedLine, [string]$Label)
    $hits = @(Get-AuthorityLines $Relative | Where-Object { $_.StartsWith($Marker, [StringComparison]::Ordinal) })
    if ($hits.Count -ne 1) { Add-Error "架构断言面必须唯一（$Label）：$Relative，实际 $($hits.Count) 行"; return }
    if ($hits[0].TrimEnd() -cne $ExpectedLine) { Add-Error "架构断言面与哨兵不一致（$Label）：$Relative" }
}

Assert-ArchitectureSurface -Relative 'doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md' `
    -Marker 'Target architecture sentinel:' -ExpectedLine ('Target architecture sentinel: `' + $architecture + '`') -Label 'AD-002 历史哨兵'
Assert-ArchitectureSurface -Relative 'doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md' `
    -Marker 'Architecture sentinel:' -ExpectedLine ('Architecture sentinel: `' + $architectureCurrent + '`') -Label 'AD-003 当前哨兵'
Assert-ArchitectureSurface -Relative 'doc/00_INDEX.md' `
    -Marker '**当前架构哨兵（机器校验字段）**：' -ExpectedLine ('**当前架构哨兵（机器校验字段）**：`' + $architectureCurrent + '`') -Label '00_INDEX 当前哨兵字段'

# Parse the actual architecture value before its explanatory parenthesis; a
# historical occurrence later on the line cannot replace that value or link.
$boundaryMarker = '当前唯一继续演进的产品架构为 '
$boundary = @(Get-AuthorityLines 'AGENTS.md' | Where-Object { $_.StartsWith($boundaryMarker, [StringComparison]::Ordinal) })
if ($boundary.Count -ne 1) { Add-Error "AGENTS.md 产品边界断言行必须唯一，实际 $($boundary.Count) 行。" }
else {
    $end = $boundary[0].IndexOf('（', $boundaryMarker.Length, [StringComparison]::Ordinal)
    $expectedBoundary = 'Windows / C# .NET + Avalonia / Python Core / SQLite / ReferencedSource'
    if ($end -lt 0 -or $boundary[0].Substring($boundaryMarker.Length, $end - $boundaryMarker.Length).Trim() -cne $expectedBoundary) {
        Add-Error 'AGENTS.md 产品边界的当前架构值不一致。'
    }
    $sentenceEnd = $boundary[0].IndexOf('。', [StringComparison]::Ordinal)
    $firstSentence = if ($sentenceEnd -ge 0) { $boundary[0].Substring(0, $sentenceEnd) } else { $boundary[0] }
    $visibleSentence = Hide-NonLinkContexts $firstSentence
    if ($visibleSentence -cnotmatch '(?<![!\\])\[AD-003[^\]]*\]\(doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE\.md\)') {
        Add-Error 'AGENTS.md 产品边界的首句缺少 AD-003 Markdown 链接。'
    }
}

# Only the unique CURRENT rows in the document map are authority pointers.
$indexLines = @(Get-AuthorityLines 'doc/00_INDEX.md')
foreach ($pointer in @(
    @{ Name = 'AD-003'; Target = 'AD-003_REFERENCED_SOURCE_ARCHITECTURE.md'; Kind = 'CURRENT / ARCHITECTURE' },
    @{ Name = 'ADJ-001'; Target = 'contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md'; Kind = 'CURRENT / CONTRACT ADJUDICATION' }
)) {
    $rowPrefix = '| [' + $pointer.Name + ']('
    $rows = @($indexLines | Where-Object { $_.StartsWith($rowPrefix, [StringComparison]::Ordinal) })
    $expectedPrefix = '| [' + $pointer.Name + '](' + $pointer.Target + ') | ' + $pointer.Kind + ' |'
    if ($rows.Count -ne 1 -or -not $rows[0].StartsWith($expectedPrefix, [StringComparison]::Ordinal)) {
        Add-Error "00_INDEX 当前权威指针缺失、不唯一或状态不匹配：$($pointer.Name)"
    }
}

foreach ($budget in @(
    @{ Path = 'doc/STATUS.md'; Bytes = 3200; Lines = 45 },
    @{ Path = 'doc/REBASELINE_PLAN.md'; Bytes = 7000; Lines = 64 }
)) {
    $file = Join-Path $repoRoot $budget.Path
    $bytes = (Get-Item -LiteralPath $file).Length
    $lineCount = (Get-Content -LiteralPath $file).Count
    if ($bytes -gt $budget.Bytes -or $lineCount -gt $budget.Lines) { Add-Error "$($budget.Path) 超过防膨胀预算：$bytes bytes / $lineCount lines" }
    elseif ($bytes -ge [math]::Floor($budget.Bytes * 0.8) -or $lineCount -ge [math]::Floor($budget.Lines * 0.8)) { Add-Warning "$($budget.Path) 已达到预算的 80%：$bytes bytes / $lineCount lines" }
}

Initialize-EvidenceExceptions (Join-Path $repoRoot 'tools/governance/evidence-pin-exceptions.json')

if ($TaskPath -and (Test-Path -LiteralPath $TaskPath -PathType Leaf)) {
    $taskText = Get-Content -LiteralPath $TaskPath -Raw
    $metadata = Get-FrontMatter $taskText
    if (-not $metadata.ContainsKey('status')) { Add-Error 'Task front matter 缺少 status。' }
    else {
        $taskStatus = $metadata['status'].ToLowerInvariant()
        $validStatuses = @('proposed', 'ready', 'in_progress', 'blocked', 'in_review', 'changes_requested', 'approved', 'done', 'closed_with_limitations', 'cancelled', 'superseded', 'historical')
        if ($taskStatus -notin $validStatuses) { Add-Error "Task status 无效：$taskStatus" }
        $isStatusActiveTask = $activeTaskPath -and [IO.Path]::GetFullPath($TaskPath) -eq $activeTaskPath
        if ($isStatusActiveTask -and $taskStatus -in @('done', 'closed_with_limitations', 'cancelled', 'superseded', 'historical')) { Add-Error "STATUS 仍指向终态 Task：$taskStatus" }
        $taskId = $metadata['id']
        if ($taskId -and [IO.Path]::GetFileNameWithoutExtension($TaskPath) -ne $taskId) { Add-Error "Task 文件名与 front matter id 不一致：$taskId" }
        $readyIds = @()
        if ($taskId) {
            $planText = Get-Content -LiteralPath (Join-Path $repoRoot 'doc/REBASELINE_PLAN.md') -Raw
            $currentDag = ($planText -split '(?m)^##\s+历史快照', 2)[0]
            $readyMatch = [regex]::Match($currentDag, '(?m)^READY 节点：\s*(?<nodes>.+)$')
            if (-not $readyMatch.Success) { Add-Error 'REBASELINE_PLAN 当前 DAG 缺少 READY 节点声明。' }
            else {
                $readyList = ($readyMatch.Groups['nodes'].Value -split '[。;；]', 2)[0].Trim()
                if ($readyList -notmatch '^(?i:无|none)[.]?$') {
                    $readyIds = @([regex]::Matches($readyList, '[A-Za-z][A-Za-z0-9._-]+') | ForEach-Object { $_.Value })
                    foreach ($readyId in $readyIds) {
                        $readyTaskPath = Join-Path (Join-Path $repoRoot 'doc/tasks') "$readyId.md"
                        if (-not (Test-Path -LiteralPath $readyTaskPath -PathType Leaf)) { Add-Error "READY DAG 节点缺少 Task 文件：$readyId"; continue }
                        $readyTask = Get-FrontMatter (Get-Content -LiteralPath $readyTaskPath -Raw)
                        if ($readyTask['status'] -ne 'ready') { Add-Error "READY DAG 只允许 status: ready；$readyId 当前为 $($readyTask['status'])" }
                    }
                }
            }
            if ($taskStatus -in @('ready', 'in_progress', 'blocked', 'in_review', 'changes_requested', 'approved') -and $currentDag -notmatch [regex]::Escape($taskId)) { Add-Error "当前 DAG 未登记非终态 Task：$taskId" }
            if ($taskStatus -eq 'ready' -and $readyIds -notcontains $taskId) { Add-Error "READY Task 未出现在 Plan 的 READY 节点：$taskId" }
        }
        if (-not $metadata.ContainsKey('governance_version')) {
            Add-Warning '当前 Task 是 lifecycle v1；保留其原状态与证据，不强制回填旧 Task。'
        } elseif ($metadata['governance_version'] -in @('2', '3')) {
            if ($taskStatus -in @('in_review', 'approved', 'done', 'closed_with_limitations')) {
                $evidenceSection = Get-Section $taskText 'Canonical Evidence'
                $evidenceRows = @(Get-TableRows $evidenceSection)
                $headerLine = @($evidenceSection -split '\r?\n' | Where-Object { $_ -match '^\s*\|.*\|\s*$' } | Select-Object -First 1)
                $headerCells = @()
                if ($headerLine.Count -gt 0) {
                    $headerCells = @($headerLine[0].Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim().Trim('`') })
                }
                $legacyEvidenceSchema = $headerCells.Count -eq 6 -and
                    $headerCells[0] -ieq 'evidence_id' -and $headerCells[1] -ieq 'AC/Gate' -and
                    $headerCells[2] -match '^path(?:$|\s|[（(])' -and $headerCells[3] -ieq 'commit' -and
                    $headerCells[4] -ieq 'sha256' -and $headerCells[5] -match '^class(?:\s|$)'
                $basisEvidenceSchema = $headerCells.Count -eq 7 -and
                    $headerCells[0] -ceq 'evidence_id' -and $headerCells[1] -ceq 'AC/Gate' -and
                    $headerCells[2] -match '^path(?:$|\s|[（(])' -and $headerCells[3] -ceq 'commit' -and
                    $headerCells[4] -ceq 'sha256' -and $headerCells[5] -match '^class(?:\s|$)' -and
                    $headerCells[6] -ceq 'sha256_basis'
                if (-not $legacyEvidenceSchema -and -not $basisEvidenceSchema) {
                    Add-Error 'EVIDENCE_BASIS_HEADER_INVALID: Canonical Evidence 必须是兼容旧六列或显式 sha256_basis 新七列。'
                    $evidenceRows = @()
                }
                if ($evidenceRows.Count -eq 0) { Add-Error '进入 REVIEW/DONE 的 lifecycle v2 Task 必须列出 canonical evidence。' }
                foreach ($row in $evidenceRows) {
                    if ($row.Count -lt 6) {
                        if ($basisEvidenceSchema) { Add-Error 'EVIDENCE_BASIS_ROW_ARITY: 新七列表的每行必须有 7 列。' }
                        else { Add-Error 'Canonical Evidence 表格需要 6 列。' }
                        continue
                    }
                    if (@($row | ForEach-Object { ([string]$_).Trim() } | Where-Object { $_ -ne '-' -and $_ -ne '' }).Count -eq 0) {
                        Add-Error "Canonical Evidence 行结构非法：整行为占位符：$($row -join ' | ')"
                        continue
                    }
                    # Legacy rows often wrap cells in backticks; strip them once so
                    # every downstream comparison (and the exception fingerprint) is
                    # against the same normalised text.
                    $path = ([string]$row[2]).Trim().Trim('`').Trim()
                    $commitRaw = ([string]$row[3]).Trim().Trim('`').Trim()
                    $shaRaw = ([string]$row[4]).Trim().Trim('`').Trim()
                    $commit = $commitRaw
                    $sha = $shaRaw.ToLowerInvariant()
                    $class = ([string]$row[5]).Trim().Trim('`').Trim().ToUpperInvariant()
                    if ($class -notin @('CANONICAL', 'SOURCE_PIN')) { Add-Error "Evidence class 无效：$class" }
                    if ($basisEvidenceSchema) {
                        if ($row.Count -ne 7) { Add-Error 'EVIDENCE_BASIS_ROW_ARITY: 新七列表的每行必须恰好有 7 列。'; continue }
                        $basis = [string]$row[6]
                        if ($basis -cnotin @('BLOB', 'WORKTREE', 'EXTERNAL_SHA256')) {
                            Add-Error "EVIDENCE_BASIS_INVALID: sha256_basis 必须严格为 BLOB、WORKTREE 或 EXTERNAL_SHA256：$path"
                            continue
                        }
                        if ($sha -notmatch '^[0-9a-f]{64}$') {
                            Add-Error "EVIDENCE_BASIS_SHA_INVALID: 新格式必须提供 64 位 SHA-256：$path"
                            continue
                        }
                        $evidencePath = Resolve-LocalPath $path $repoRoot
                        if (-not $evidencePath) { Add-Error "EVIDENCE_BASIS_PATH_INVALID: 路径不可解析：$path"; continue }
                        $pathInfo = Get-RepoPathInfo $evidencePath $repoRoot
                        switch ($basis) {
                            'BLOB' {
                                if ($commit -match '^(?i:null|pending|todo|none|-|—)$' -or $commit -notmatch '^[0-9a-fA-F]{7,40}$') {
                                    Add-Error "EVIDENCE_BASIS_BLOB_COMMIT_REQUIRED: BLOB 必须提供有效 commit：$path"
                                    continue
                                }
                                if (-not $pathInfo.IsInside) { Add-Error "EVIDENCE_BASIS_BLOB_PATH_INVALID: BLOB 路径必须位于仓库内：$path"; continue }
                                $blobSha = Get-GitBlobSha256 $commit $pathInfo.Relative
                                if (-not $blobSha) { Add-Error "EVIDENCE_BASIS_BLOB_PATH_MISSING: commit 不含可读取的路径 blob：$commit`:$($pathInfo.Relative)"; continue }
                                if ($blobSha -ne $sha) { Add-Error "EVIDENCE_BASIS_HASH_MISMATCH: Git blob SHA-256 不匹配：$path" }
                            }
                            'WORKTREE' {
                                if ($row[1] -notmatch '(?i)WORKTREE_ENV\s*=\s*\S') {
                                    Add-Error "EVIDENCE_BASIS_WORKTREE_ENV_REQUIRED: AC/Gate 必须说明可复现环境（WORKTREE_ENV=...）：$path"
                                    continue
                                }
                                if (-not $pathInfo.IsInside) { Add-Error "EVIDENCE_BASIS_WORKTREE_PATH_INVALID: WORKTREE 路径必须位于当前仓库工作树：$path"; continue }
                                if (-not (Test-Path -LiteralPath $evidencePath -PathType Leaf)) { Add-Error "EVIDENCE_BASIS_WORKTREE_PATH_UNREADABLE: 工作树文件不存在：$path"; continue }
                                try { $actualSha = (Get-FileHash -LiteralPath $evidencePath -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant() }
                                catch { Add-Error "EVIDENCE_BASIS_WORKTREE_PATH_UNREADABLE: 工作树文件不可读：$path"; continue }
                                if ($actualSha -ne $sha) { Add-Error "EVIDENCE_BASIS_HASH_MISMATCH: WORKTREE SHA-256 不匹配：$path" }
                            }
                            'EXTERNAL_SHA256' {
                                if ($pathInfo.IsInside) { Add-Error "EVIDENCE_BASIS_EXTERNAL_PATH_INVALID: EXTERNAL_SHA256 路径必须在仓库外：$path"; continue }
                                if (-not (Test-Path -LiteralPath $evidencePath -PathType Leaf)) { Add-Error "EVIDENCE_BASIS_EXTERNAL_PATH_UNREADABLE: 外部文件不存在：$path"; continue }
                                try { $actualSha = (Get-FileHash -LiteralPath $evidencePath -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant() }
                                catch { Add-Error "EVIDENCE_BASIS_EXTERNAL_PATH_UNREADABLE: 外部文件不可读：$path"; continue }
                                if ($actualSha -ne $sha) { Add-Error "EVIDENCE_BASIS_HASH_MISMATCH: EXTERNAL_SHA256 不匹配：$path" }
                            }
                        }
                        continue
                    }

                    # Legacy six-column rows (r194 semantics + the 2026-11-16 EOL ruling):
                    #   * a missing WORKTREE path is not an error by itself -- the commit
                    #     blob is tried first (ruling condition 6);
                    #   * the recorded digest must equal one EXACT byte representation:
                    #     worktree raw, blob raw, or -- for rows that already existed in a
                    #     terminal card at the frozen baseline -- the pure LF / CRLF form of
                    #     those same bytes.  Nothing else is ever normalised.
                    $evidencePath = Resolve-LocalPath $path $repoRoot
                    $worktreeExists = [bool]($evidencePath -and (Test-Path -LiteralPath $evidencePath -PathType Leaf))
                    $repoRel = $null
                    if ($evidencePath) {
                        $candidate = [IO.Path]::GetRelativePath($repoRoot, $evidencePath).Replace('\', '/')
                        if ($candidate -ne '..' -and -not $candidate.StartsWith('../')) { $repoRel = $candidate }
                    }
                    $cardRel = [IO.Path]::GetRelativePath($repoRoot, $TaskPath).Replace('\', '/')
                    if ($commit -match '^(?i:null|pending|todo|-)$') { $commit = '' }
                    if ($sha -match '^(?i:null|pending|todo|-)$') { $sha = '' }
                    if (-not $commit -and -not $sha) { Add-Error "Evidence 必须有 commit 或 SHA-256 pin：$path" }
                    $commitValid = $false
                    if ($commit) {
                        if ($commit -notmatch '^[0-9a-fA-F]{7,40}$') {
                            $ex = Get-EvidenceException 'COMMIT_FORMAT' $taskId $row[0] $path $commit $sha $class $commitRaw $shaRaw
                            if ($ex) { Add-Warning "EXEMPTED[$($ex.id)]: Evidence commit 格式无效：$path（原文 `"$commit`"）—— $($ex.reason)" }
                            else { Add-Error "Evidence commit 格式无效：$path" }
                        }
                        elseif (-not $repoRel) { Add-Error "仓外 evidence 不能用仓库 commit pin：$path" }
                        else {
                            & git -C $repoRoot cat-file -e "${commit}:$repoRel" 2>$null
                            if ($LASTEXITCODE -ne 0) {
                                $ex = Get-EvidenceException 'COMMIT_PATH_MISSING' $taskId $row[0] $path $commit $sha $class
                                if ($ex) { Add-Warning "EXEMPTED[$($ex.id)]: Evidence commit 不含所 pin 文件：$commit`:$repoRel —— $($ex.reason)" }
                                else { Add-Error "Evidence commit 不含所 pin 文件：$commit`:$repoRel" }
                            } else { $commitValid = $true }
                        }
                    }
                    if ($sha) {
                        if ($sha -notmatch '^[0-9a-f]{64}$') {
                            $ex = Get-EvidenceException 'SHA_MULTI' $taskId $row[0] $path $commit $sha $class $commitRaw $shaRaw
                            if ($ex) { Add-Warning "EXEMPTED[$($ex.id)]: Evidence SHA-256 格式无效（多摘要单元格）：$path —— $($ex.reason)" }
                            else { Add-Error "Evidence SHA-256 格式无效：$path" }
                        } else {
                            $matches = $false
                            $matchBasis = ''
                            if ($worktreeExists) {
                                $worktreeSha = (Get-FileHash -LiteralPath $evidencePath -Algorithm SHA256).Hash.ToLowerInvariant()
                                if ($worktreeSha -eq $sha) { $matches = $true; $matchBasis = 'WORKTREE' }
                            }
                            if (-not $matches -and $commitValid) {
                                $blobSha = Get-GitBlobSha256 $commit $repoRel
                                if ($blobSha -eq $sha) { $matches = $true; $matchBasis = 'BLOB' }
                            }
                            # EOL forms: only for historical rows that existed, unchanged, in a
                            # terminal card at the frozen baseline (ruling condition 4).
                            if (-not $matches -and (Get-BaselineRowEligible $cardRel $row[0] $row)) {
                                if ($worktreeExists) {
                                    $forms = Get-WorktreeForms $evidencePath
                                    if ($forms) {
                                        foreach ($form in @('LF', 'CRLF')) {
                                            if ($forms[$form] -eq $sha) { $matches = $true; $matchBasis = "WORKTREE_$form"; break }
                                        }
                                    }
                                }
                                if (-not $matches -and $commitValid) {
                                    $blobForms = Get-GitBlobForms $commit $repoRel
                                    if ($blobForms) {
                                        foreach ($form in @('LF', 'CRLF')) {
                                            if ($blobForms[$form] -eq $sha) { $matches = $true; $matchBasis = "BLOB_$form"; break }
                                        }
                                    }
                                }
                            }
                            if (-not $matches) {
                                if (-not $worktreeExists -and -not $commit) {
                                    $ex = Get-EvidenceException 'PATH_MISSING' $taskId $row[0] $path $commit $sha $class
                                    if ($ex) { Add-Warning "EXEMPTED[$($ex.id)]: Canonical evidence 路径缺失：$path —— $($ex.reason)" }
                                    else { Add-Error "Canonical evidence 路径缺失：$path" }
                                } else {
                                    $ex = Get-EvidenceException 'SHA_MISMATCH' $taskId $row[0] $path $commit $sha $class
                                    if ($ex) { Add-Warning "EXEMPTED[$($ex.id)]: Evidence SHA-256 不匹配：$path —— $($ex.reason)" }
                                    else { Add-Error "Evidence SHA-256 不匹配：$path" }
                                }
                            } elseif ($matchBasis -notin @('WORKTREE', 'BLOB')) {
                                Add-Warning "Evidence SHA-256 以行尾形态匹配（$matchBasis）：$path"
                            }
                        }
                    } elseif (-not $worktreeExists) {
                        $ex = Get-EvidenceException 'PATH_MISSING' $taskId $row[0] $path $commit $sha $class
                        if ($ex) { Add-Warning "EXEMPTED[$($ex.id)]: Canonical evidence 路径缺失：$path —— $($ex.reason)" }
                        else { Add-Error "Canonical evidence 路径缺失：$path" }
                    }
                }
                $evidenceDir = $metadata['evidence_dir']
                if ($evidenceDir -and $evidenceDir -notmatch '^(?i:null|pending|todo)$') {
                    $evidenceRoot = Resolve-LocalPath $evidenceDir $repoRoot
                    if ($evidenceRoot -and (Test-Path -LiteralPath $evidenceRoot -PathType Container)) {
                        $listed = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
                        foreach ($row in $evidenceRows) {
                            if ($row.Count -ge 3) {
                                $path = Resolve-LocalPath $row[2] $repoRoot
                                if ($path) { [void]$listed.Add($path) }
                            }
                        }
                        $extras = @(Get-ChildItem -LiteralPath $evidenceRoot -File -Recurse | Where-Object { -not $listed.Contains($_.FullName) })
                        if ($extras.Count -gt 0) {
                            $names = ($extras | Select-Object -First 8 -ExpandProperty FullName) -join ', '
                            if ($taskStatus -eq 'done') { Add-Error "DONE evidence_dir 含未登记文件：$names" }
                            else { Add-Warning "evidence_dir 含未登记过程文件（归入 workspace 或列为 SOURCE_PIN）：$names" }
                        }
                    }
                }
            }
            $integrationCommit = $metadata['integration_commit']
            $hasIntegrationCommit = $integrationCommit -and $integrationCommit -notmatch '^(?i:null|pending|todo|-)$'
            # §4.3.1（GOV-CHECKER-HISTORICAL-AC-EXEMPT-1）：存量卡清理采用行内 HTML 注释标注
            # （<!-- verified|not-applicable|blocked: … -->）。含该形式且为 gv3 终态卡时，改按 §4.3.1
            # 口径校验；不含该形式的卡一律走原 §4.3 逻辑（门禁不削弱）。
            # 作用域收窄到 `**AC` 行（独立复核 r1 的 R-01）：非 AC 的 checkbox 行不参与判定，
            # 否则「零 AC 行 + 非 AC 行带注释」可绕过「未找到任何 AC 行」，或反向误分派。
            $htmlAcStyle = ($taskText -match '(?m)^[ \t]*-[ \t]*\[[ xX]\][^\r\n]*\*\*AC[0-9A-Za-z._-]*[^\r\n]*<!--\s*(verified|not-applicable|blocked)\s*:')
            $historicalAcExempt = ($htmlAcStyle -and $metadata['governance_version'] -eq '3' -and $taskStatus -in @('done', 'closed_with_limitations'))
            $terminalStatus = $taskStatus -in @('done', 'closed_with_limitations', 'cancelled', 'superseded', 'historical')
            $closeoutRequired = $terminalStatus -or ($taskStatus -eq 'approved' -and $hasIntegrationCommit)
            if ($taskStatus -eq 'done' -and -not $hasIntegrationCommit) { Add-Error 'DONE 必须记录 integration_commit。' }
            if ($taskStatus -in @('done', 'closed_with_limitations') -and $metadata['canonical_evidence_status'] -ne 'complete') { Add-Error "$($taskStatus.ToUpperInvariant()) 必须设置 canonical_evidence_status: complete。" }
            if ($closeoutRequired) {
                if ($metadata['resource_closeout_status'] -ne 'complete') { Add-Error '终态或已集成的 approved Task 必须设置 resource_closeout_status: complete。' }
            }
            if ($closeoutRequired) {
                if (-not $historicalAcExempt -and ($taskStatus -eq 'done' -or ($taskStatus -eq 'approved' -and $hasIntegrationCommit)) -and $taskText -match '(?m)^\s*-\s*\[ \]') { Add-Error 'DONE 不能保留未完成 Acceptance Criteria；范围未完成时使用 closed_with_limitations。' }
                $manifestSection = Get-Section $taskText 'Resource Manifest'
                $resourceRows = @(Get-TableRows $manifestSection)
                $externalManifestUsed = $false
                if ($resourceRows.Count -eq 0) {
                    $ref = Resolve-ManifestReference $manifestSection $repoRoot
                    if ($ref.Error) { Add-Error $ref.Error }
                    elseif ($ref.Path) {
                        $externalManifestUsed = $true
                        $checked = Test-ExternalResourceManifest $ref.Path $taskId $repoRoot
                        foreach ($p in $checked.Errors) { Add-Error $p }
                        if ($checked.Notes) { foreach ($n in $checked.Notes) { Add-Warning "$($taskId): $n" } }
                        foreach ($r in $checked.Resources) {
                            if ($r.Disposition -in @('MIGRATE','ARCHIVE','PRESERVE_REFERENCED','PRESERVE_USER_DATA','PRESERVE_UNKNOWN')) {
                                if ($r.IsSameLocation) {
                                    $target = $r.Source
                                    if ([string]::IsNullOrWhiteSpace($target) -or $target.Trim() -eq '-') { continue }
                                    if ($target -match '[{}*?\[\]]' -or $target -match '%[^%]+%') { continue }
                                    $finalPath = try { Resolve-LocalPath $target $repoRoot } catch { $null }
                                    if ($finalPath -and (Test-Path -LiteralPath $finalPath)) { continue }
                                    if ($r.IsSentinel) {
                                        # AC1: 五个已核实 sentinel 是同源位置说明，若 source 未在本地存在（例如已清理的构建缓存），明确跳过 destination 存在性校验
                                        continue
                                    }
                                    Add-Error "Resource 最终路径未验证：$target"
                                    continue
                                }
                                if ([string]::IsNullOrWhiteSpace($r.Destination) -or $r.Destination -match '^(?i:none|n/?a|-)$') { continue }
                                if ($r.Destination -match '[{}*?\[\]]' -or $r.Destination -match '%[^%]+%') { continue }
                                $finalPath = try { Resolve-LocalPath $r.Destination $repoRoot } catch { $null }
                                if (-not $finalPath -or -not (Test-Path -LiteralPath $finalPath)) { Add-Error "Resource 最终路径未验证：$($r.Destination)" }
                            }
                        }
                    } else { Add-Error 'DONE 必须逐项填写 Resource Manifest；无资源时写 NOT_APPLICABLE。' }
                }
                $allowedDisposition = @('DELETE_SAFE', 'MIGRATE', 'ARCHIVE', 'PRESERVE_REFERENCED', 'PRESERVE_USER_DATA', 'PRESERVE_UNKNOWN', 'NOT_APPLICABLE')
                foreach ($row in $resourceRows) {
                    if ($row.Count -lt 6) { Add-Error 'Resource Manifest 表格需要 6 列。'; continue }
                    $source = $row[1]
                    $disposition = $row[2].ToUpperInvariant()
                    $destination = $row[3]
                    $integrity = $row[4]
                    $result = $row[5]
                    if ($disposition -notin $allowedDisposition) { Add-Error "Resource disposition 无效：$disposition" }
                    if ([string]::IsNullOrWhiteSpace($result) -or $result -match '^(?i:待关闭|todo|pending|tbd)$') { Add-Error 'Resource Manifest 缺少引用/进程检查结果。' }
                    if ($disposition -eq 'DELETE_SAFE') {
                        $sourcePath = Resolve-LocalPath $source $repoRoot
                        if ($sourcePath -and (Test-Path -LiteralPath $sourcePath)) { Add-Error "DELETE_SAFE 来源仍存在：$source" }
                    }
                    if ($disposition -in @('MIGRATE', 'ARCHIVE', 'PRESERVE_REFERENCED', 'PRESERVE_USER_DATA', 'PRESERVE_UNKNOWN')) {
                        $finalPath = if ($destination -and $destination -notmatch '^(?i:none|n/?a|-)$') { Resolve-LocalPath $destination $repoRoot } else { $null }
                        if (-not $finalPath -or -not (Test-Path -LiteralPath $finalPath)) { Add-Error "Resource 最终路径未验证：$destination" }
                    }
                    if ($disposition -ne 'NOT_APPLICABLE') {
                        if ([string]::IsNullOrWhiteSpace($integrity) -or $integrity -match '^(?i:待关闭|todo|pending|tbd)$') { Add-Error "Resource 缺少 SHA-256/manifest 证据：$source" }
                        elseif ($integrity -notmatch '^[0-9a-fA-F]{64}$') {
                            $manifestPath = Resolve-LocalPath $integrity $repoRoot
                            if (-not $manifestPath -or -not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { Add-Error "Resource manifest 不存在：$integrity" }
                        } elseif ($disposition -in @('PRESERVE_REFERENCED', 'PRESERVE_USER_DATA', 'PRESERVE_UNKNOWN')) {
                            $finalPath = Resolve-LocalPath $destination $repoRoot
                            if ($finalPath -and (Test-Path -LiteralPath $finalPath -PathType Leaf) -and (Get-FileHash -LiteralPath $finalPath -Algorithm SHA256).Hash -ne $integrity) { Add-Error "Resource SHA-256 不匹配：$destination" }
                        }
                    }
                }
            }
            if ($metadata['governance_version'] -eq '3' -and $taskStatus -in @('in_review', 'approved', 'done', 'closed_with_limitations') -and $historicalAcExempt) {
                # §4.3.1 口径：每个 AC 行必须有三种 HTML 注释之一；勾选与 kind 一致；原因非空；禁止裸 [x]。
                $htmlAcMatches = @([regex]::Matches($taskText, '(?m)^[ \t]*-[ \t]*\[([ xX])\][^\r\n]*\*\*AC[0-9A-Za-z._-]*[^\r\n]*\r?$'))
                $htmlAcCount = 0
                foreach ($hm in $htmlAcMatches) {
                    $hLine = $hm.Value.TrimEnd([char]13)
                    $hChecked = ($hm.Groups[1].Value -ne ' ')
                    $hLabel = if ($hLine -match '\*\*(AC[0-9A-Za-z._-]+)') { $matches[1] } else { 'AC?' }
                    $hMark = [regex]::Match($hLine, '<!--\s*(verified|not-applicable|blocked)\s*:\s*(.*?)\s*-->[ \t]*$')
                    if (-not $hMark.Success) {
                        if ($hChecked) { Add-Error "§4.3.1 裸 [x]（缺 verified/not-applicable/blocked 注释）：$($taskId) $hLabel" }
                        else { Add-Error "§4.3.1 AC 缺注释：$($taskId) $hLabel" }
                        continue
                    }
                    $hKind = $hMark.Groups[1].Value
                    $hReason = $hMark.Groups[2].Value.Trim()
                    if (-not $hReason) { Add-Error "§4.3.1 注释原因为空：$($taskId) $hLabel" }
                    if ($hKind -eq 'blocked') {
                        if ($hChecked) { Add-Error "§4.3.1 blocked 不得勾选：$($taskId) $hLabel" }
                    } elseif (-not $hChecked) {
                        Add-Error "§4.3.1 $hKind 必须勾选：$($taskId) $hLabel"
                    }
                    $htmlAcCount++
                }
                if ($htmlAcCount -eq 0) { Add-Error 'lifecycle v3 Task 进入 REVIEW/DONE 时未找到任何 AC 行。' }
            } elseif ($metadata['governance_version'] -eq '3' -and $taskStatus -in @('in_review', 'approved', 'done', 'closed_with_limitations')) {
                # §4.3 AC 状态标记门禁：每个 AC 必须有合法 <<STATUS>>，且与勾选一致。
                $acMatches = @([regex]::Matches($taskText, '(?m)^[ \t]*-[ \t]*\[([ xX])\][ \t]*\*\*AC[^\r\n]*\r?$'))
                if ($acMatches.Count -eq 0) {
                    Add-Error 'lifecycle v3 Task 进入 REVIEW/DONE 时未找到任何 AC 行。'
                }
                foreach ($am in $acMatches) {
                    # r188: the AC match may end with \r on a CRLF file (the pattern above
                    # tolerates it so AC lines are visible either way). Downstream marker matching
                    # anchors on $, so strip the \r once here instead of making every later
                    # pattern CRLF-aware.
                    $acLine = $am.Value.TrimEnd([char]13)
                    $isChecked = ($am.Groups[1].Value -ne ' ')
                    $acLabel = if ($acLine -match '\*\*(AC[0-9A-Za-z._-]+)') { $matches[1] } else { 'AC?' }
                    $mk = [regex]::Match($acLine, '<<(MET|PARTIAL|BLOCKED|NOT_APPLICABLE)(?::[ \t]*([^>]*))?>>[ \t]*$')
                    if (-not $mk.Success) {
                        Add-Error "AC 状态标记缺失或非法（需行末 <<MET>> / <<PARTIAL: 原因>> / <<BLOCKED: 原因>> / <<NOT_APPLICABLE: 原因>>）：$acLabel"
                        continue
                    }
                    $acState = $mk.Groups[1].Value
                    $acReason = $mk.Groups[2].Value.Trim()
                    $acText = ($acLine -replace '\s+', ' ')
                    if ($acText.Length -gt 220) { $acText = $acText.Substring(0, 220) + '…' }
                    switch ($acState) {
                        'MET' {
                            if (-not $isChecked) { Add-Error "AC 标记为 MET 但未勾选：$acLabel" }
                            if ($acReason) { Add-Error "AC 标记为 MET 时不得附原因（依据应进 Canonical Evidence）：$acLabel" }
                        }
                        'NOT_APPLICABLE' {
                            if (-not $isChecked) { Add-Error "AC 标记为 NOT_APPLICABLE 时必须勾选：$acLabel" }
                            if (-not $acReason) { Add-Error "AC 标记为 NOT_APPLICABLE 时必须有原因：$acLabel" }
                        }
                        default {
                            if ($taskStatus -eq 'done') { Add-Error "DONE Task 不得包含未达成状态（$acState）的 AC：$acLabel；范围未达成时请使用 closed_with_limitations。" }
                            if ($isChecked) { Add-Error "AC 标记为 $acState 时不得勾选：$acLabel" }
                            if (-not $acReason) { Add-Error "AC 标记为 $acState 时必须有原因：$acLabel" }
                        }
                    }
                }
            }
        }
    }
}

Write-Output "Governance scope: $($selectedFiles.Count) current documents; no historical directory scan."
if ($TaskPath) { Write-Output "Task: $([IO.Path]::GetRelativePath($repoRoot, $TaskPath))" }
foreach ($warning in $warnings) { Write-Output "WARN: $warning" }
foreach ($errorItem in $errors) { Write-Output "FAIL: $errorItem" }
if ($errors.Count -gt 0) { Write-Output "Governance check: FAIL ($($errors.Count) errors, $($warnings.Count) warnings)"; exit 1 }
Write-Output "Governance check: PASS ($($warnings.Count) warnings)"
