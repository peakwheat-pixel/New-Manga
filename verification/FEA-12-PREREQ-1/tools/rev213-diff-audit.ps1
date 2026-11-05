#!/usr/bin/env pwsh
# FEA-12-PREREQ-1 / AC1: audit that the M2-C1 rev 2.13 change is additive.
#
# Expected shape of the diff against the card base commit:
#   * exactly ONE removed metadata line (the document status line, rev 2.12 -> 2.13), and
#   * exactly ONE removed contract row (§11 `Permanent-delete user policy`, status cell updated
#     per ADJ-2026-11-05 §D2).
# Everything else must be pure insertions. The script also proves no Python (`src/**`) or pinned
# contract (`doc/plan/FEA-C*`) byte changed by this card.

param(
    [string]$Base = '035468a81e43e8d70fb711536824cdf613a7a0c4',
    # Optional contract file to audit (R-001 discriminator: run against a copy of the old head,
    # e.g. `git show 5a7c7e028:<path>`). Default = the worktree contract.
    [string]$DocFile = '',
    # This card's committed delivery commits (scope guard audits THESE, not the shared dirty tree).
    [string[]]$DeliveryCommits = @('08b359251', '5a7c7e028')
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$doc = 'doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md'
$docPath = if ($DocFile) { (Resolve-Path $DocFile).Path } else { Join-Path $root $doc }
$git = { & git -C $root @args }

function Write-Section([string]$text) { Write-Output ''; Write-Output "==== $text ====" }

$headNow = (& git -C $root rev-parse HEAD).Trim()
Write-Section 'BASELINE'
Write-Output "base_commit=$Base"
Write-Output "worktree_head=$headNow"
Write-Output "audited_file=$doc"
Write-Output "audited_doc_source=$docPath"
Write-Output "worktree_file_sha256=$((Get-FileHash -LiteralPath (Join-Path $root $doc) -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "audited_doc_sha256=$((Get-FileHash -LiteralPath $docPath -Algorithm SHA256).Hash.ToLowerInvariant())"
Write-Output "base_blob_sha256=$((& git -C $root rev-parse "${Base}:$doc").Trim())"

Write-Section 'NUMSTAT / STAT'
& git -C $root diff --numstat $Base -- $doc
& git -C $root diff --stat $Base -- $doc

Write-Section 'REMOVED LINES (existing bytes changed by this card)'
$removed = @(& git -C $root diff -U0 $Base -- $doc |
    Where-Object { $_ -match '^-' -and $_ -notmatch '^---' })
Write-Output "removed_line_count=$($removed.Count)"
$removed | ForEach-Object { Write-Output $_ }

Write-Section 'INSERTED SECTION ANCHORS (rev 2.13 additive content)'
& git -C $root diff -U0 $Base -- $doc |
    Where-Object {
        $_ -match '^\+' -and $_ -notmatch '^\+\+\+' -and
        ($_ -match '^\+#{3,4} |^\+> \*\*rev 2\.13|^\+- `2\.13`|2\.13 additive|2\.13 REGISTERED|rev 2\.13')
    } |
    ForEach-Object { Write-Output $_ }

Write-Section 'CARD SCOPE / NO-BYTES-CHANGED GUARDS'
# The working tree may carry OTHER tasks' uncommitted writes (this card is repaired while
# FEA-11-LINEAGE-1 r3 / FEA-12-DSIM-1 are in flight). The scope guard therefore audits THIS
# CARD'S COMMITTED DELIVERY SET, not the shared working tree.
$touched = @(& git -C $root status --porcelain)
Write-Output 'working_tree_entries_informational (may include other tasks):'
$touched | ForEach-Object { Write-Output $_ }

$deliverySrc = @()
$deliveryPins = @()
foreach ($commit in $DeliveryCommits) {
    $files = @(& git -C $root show --name-only --format= $commit 2>$null | Where-Object { $_ })
    foreach ($file in $files) {
        if ($file -match '^src/') { $deliverySrc += "${commit}:$file" }
        if ($file -match '^doc/plan/FEA-C') { $deliveryPins += "${commit}:$file" }
    }
}

Write-Output ''
Write-Output "delivery_commits=$($DeliveryCommits -join ',')"
Write-Output "delivery_src_changed_count=$($deliverySrc.Count)  (must be 0: this card changes no Python)"
$deliverySrc | ForEach-Object { Write-Output $_ }

$pinned = @(& git -C $root diff --name-only $Base -- 'doc/plan/FEA-C*')
Write-Output ''
Write-Output "pinned_contracts_changed_since_base=$($pinned.Count)  (must be 0: 18 pins stay untouched)"
Write-Output "delivery_pinned_contract_count=$($deliveryPins.Count)  (must be 0)"
$pinned | ForEach-Object { Write-Output $_ }
$deliveryPins | ForEach-Object { Write-Output $_ }

Write-Section 'DOC REV / PROTOCOL CONSTANT'
Select-String -LiteralPath $docPath -Pattern '状态：文档 rev `2\.13`' |
    ForEach-Object { Write-Output "doc_status_line=$($_.Line.Trim())" }
$minorLine = (& git -C $root grep -n 'PROTOCOL_MINOR = 3' -- 'src/bootstrap/core_service.py').Trim()
Write-Output "core_protocol_minor=$minorLine  (unchanged: rev 2.13 is a doc revision only)"

Write-Section 'R-001 CONSISTENCY: §5.11.3 table superset of both ErrorView code unions + 5 rev 2.13 codes registered'
$docLines = Get-Content -LiteralPath $docPath

function Get-DocSection([string[]]$lines, [string]$startPattern, [string]$endPattern) {
    $start = -1
    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match $startPattern) {
            $start = $index
            break
        }
    }

    if ($start -lt 0) { return @() }
    for ($index = $start + 1; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match $endPattern) { return $lines[$start..($index - 1)] }
    }

    return $lines[$start..($lines.Count - 1)]
}

function Get-BacktickedCodes([string[]]$lines) {
    $codes = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($line in $lines) {
        foreach ($match in [regex]::Matches($line, '`([A-Z][A-Z0-9_]{3,})`')) {
            [void]$codes.Add($match.Groups[1].Value)
        }
    }

    return ,$codes
}

function Get-ErrorViewCodes([string[]]$lines, [string]$viewName) {
    $codes = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $inBlock = $false
    $inCode = $false
    foreach ($line in $lines) {
        if (-not $inBlock) {
            if ($line -match ('^\s*' + [regex]::Escape($viewName) + '\s*=\s*\{\s*$')) { $inBlock = $true }
            continue
        }

        if ($line -match '^\s*\}') {
            $inBlock = $false
            $inCode = $false
            continue
        }

        if ($line -match '^\s*code:') { $inCode = $true }
        if ($inCode) {
            foreach ($match in [regex]::Matches($line, '\b([A-Z][A-Z0-9_]{3,})\b')) {
                [void]$codes.Add($match.Groups[1].Value)
            }

            if ($line -match '^\s*category:') {
                $inCode = $false
                $inBlock = $false
            }
        }
    }

    return ,$codes
}

$errorSemantics = @(Get-DocSection $docLines '^#### 5\.11\.3 ' '^#### 5\.11\.4 ')
$errorViews = @(Get-DocSection $docLines '^#### 5\.11\.5 ' '^### 5\.12 ')
$trashSection = @(Get-DocSection $docLines '^### 5\.14 ' '^## 6\. ')
if ($errorSemantics.Count -eq 0 -or $errorViews.Count -eq 0 -or $trashSection.Count -eq 0) {
    Write-Output 'SECTION_PARSE=FAIL (could not locate §5.11.3 / §5.11.5 / §5.14)'
    exit 1
}

$tableCodes = Get-BacktickedCodes @($errorSemantics | Where-Object { $_ -match '^\|' })
$singleViewCodes = Get-ErrorViewCodes $errorViews 'PermanentlyDeleteBookErrorView'
$batchViewCodes = Get-ErrorViewCodes $errorViews 'PermanentlyDeleteBooksErrorView'
$trashTableCodes = Get-BacktickedCodes @($trashSection | Where-Object { $_ -match '^\|' })
$viewCodes = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($code in $singleViewCodes) { [void]$viewCodes.Add($code) }
foreach ($code in $batchViewCodes) { [void]$viewCodes.Add($code) }

$missingFromTable = @($viewCodes | Where-Object { -not $tableCodes.Contains($_) } | Sort-Object)
Write-Output "s531_table_code_count=$($tableCodes.Count)"
Write-Output "single_error_view_code_count=$($singleViewCodes.Count)"
Write-Output "batch_error_view_code_count=$($batchViewCodes.Count)"
Write-Output "missing_from_s531_table=$($missingFromTable.Count)  (must be 0: every ErrorView code must be in the §5.11.3 table)"
$missingFromTable | ForEach-Object { Write-Output "  missing=$_" }

$rev213Codes = @(
    'BOOK_DELETE_STALE_PREVIEW',
    'BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE',
    'TRASH_ENTRY_NOT_FOUND',
    'TRASH_RESTORE_CONFLICT',
    'TRASH_RESTORE_LAYER_MISMATCH'
)
$registeredCodes = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($code in $tableCodes) { [void]$registeredCodes.Add($code) }
foreach ($code in $trashTableCodes) { [void]$registeredCodes.Add($code) }
$missingNewCodes = @($rev213Codes | Where-Object { -not $registeredCodes.Contains($_) })
Write-Output "rev213_code_count=$($rev213Codes.Count)"
Write-Output "rev213_codes_missing_from_error_tables=$($missingNewCodes.Count)  (must be 0)"
$missingNewCodes | ForEach-Object { Write-Output "  missing=$_" }

Write-Section 'RESULT'
$ok = ($removed.Count -eq 2) -and
    ($deliverySrc.Count -eq 0) -and
    ($deliveryPins.Count -eq 0) -and
    ($pinned.Count -eq 0) -and
    ($missingFromTable.Count -eq 0) -and
    ($missingNewCodes.Count -eq 0)
Write-Output "removed_line_count=$($removed.Count) (expected 2: document status line + §11 policy row)"
Write-Output "ADDITIVE_AUDIT=$(if ($ok) { 'PASS' } else { 'FAIL' })"
if (-not $ok) { exit 1 }
