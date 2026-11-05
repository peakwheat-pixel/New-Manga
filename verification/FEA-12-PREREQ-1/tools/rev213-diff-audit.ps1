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
    [string]$Base = '035468a81e43e8d70fb711536824cdf613a7a0c4'
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$doc = 'doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md'
$git = { & git -C $root @args }

function Write-Section([string]$text) { Write-Output ''; Write-Output "==== $text ====" }

$headNow = (& git -C $root rev-parse HEAD).Trim()
Write-Section 'BASELINE'
Write-Output "base_commit=$Base"
Write-Output "worktree_head=$headNow"
Write-Output "audited_file=$doc"
Write-Output "worktree_file_sha256=$((Get-FileHash -LiteralPath (Join-Path $root $doc) -Algorithm SHA256).Hash.ToLowerInvariant())"
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
$touched = @(& git -C $root status --porcelain)
Write-Output 'working_tree_entries:'
$touched | ForEach-Object { Write-Output $_ }

$ownPrefixes = @(
    'doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md',
    'doc/tasks/FEA-12-PREREQ-1.md',
    'apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs',
    'apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs',
    'apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs',
    'apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/',
    'verification/FEA-12-PREREQ-1/'
)
$srcTouched = @($touched | Where-Object { $_ -match '^\s*[AMDR]{1,2}\s+src/' })
Write-Output ''
Write-Output "src_touched_count=$($srcTouched.Count)  (must be 0: this card changes no Python)"
$srcTouched | ForEach-Object { Write-Output $_ }

$pinned = @(& git -C $root diff --name-only $Base -- 'doc/plan/FEA-C*')
Write-Output ''
Write-Output "pinned_contracts_changed=$($pinned.Count)  (must be 0: 18 pins stay untouched)"
$pinned | ForEach-Object { Write-Output $_ }

Write-Section 'DOC REV / PROTOCOL CONSTANT'
Select-String -LiteralPath (Join-Path $root $doc) -Pattern '状态：文档 rev `2\.13`' |
    ForEach-Object { Write-Output "doc_status_line=$($_.Line.Trim())" }
$minorLine = (& git -C $root grep -n 'PROTOCOL_MINOR = 3' -- 'src/bootstrap/core_service.py').Trim()
Write-Output "core_protocol_minor=$minorLine  (unchanged: rev 2.13 is a doc revision only)"

Write-Section 'RESULT'
$ok = ($removed.Count -eq 2) -and ($srcTouched.Count -eq 0) -and ($pinned.Count -eq 0)
Write-Output "ADDITIVE_AUDIT=$(if ($ok) { 'PASS' } else { 'FAIL' })"
if (-not $ok) { exit 1 }
