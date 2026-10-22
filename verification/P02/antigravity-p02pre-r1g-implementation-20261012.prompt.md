# Antigravity Implementation Dispatch — P02PRE-R1G

## Assignment and frozen inputs

- Task=`P02PRE-R1G — PowerShell 7 只读取证恢复`.
- Owner/author=`Antigravity`; independent Reviewer=`DeepSeek Harness`; Integrator/adjudicator=`Codex`.
- Main repo=`G:\CODEX\New Manga`; base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`; tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2f`.
- Your task worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`; required branch=`agent/antigravity/P02PRE-R1G`; common-dir=`G:/CODEX/New Manga/.git`.
- Frozen read-only inputs at dispatch:

| Input | bytes | SHA-256 |
|---|---:|---|
| `doc/tasks/P02PRE-R1G.md` | 7246 | `7A1E711E8A1B1E85C91D6948BF8EEF6A797E80DCBAB5ED04EEEF41843F51C4BC` |
| `verification/P02/p02pre-r1g-manifest-20261011.md` | 10599 | `BC103E0B7032561DF20AA2D0F91D226ED690915F476054F25D805C0455693D3E` |
| `verification/P02/p02pre-r1f-capture.ps1` | 67582 | `5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316` |
| `doc/tasks/P02PRE-R1F.md` | 38572 | `F99D4B207FD3D7DEFE3C75171C7DBEF0519BEEB853958C13ACF229C72D97CC80` |
| `verification/P02/p02pre-r1f-manifest-20261011.md` | 49783 | `F91AF7B1785B77A57CEEAFE0FFD879345CF361FD85A5E147CD970CF5EF43717B` |
| `verification/P02/p02pre-r1f-postrun-review-followup4-docs-adjudication-20261012.md` | 5544 | `2CCB2A6D6DEBEFE8C4610264F7B4F2199EB2BB18C98224F43EEDCC02ABCC3EB9` |

The closed R1F attempt actually stopped on `Get-FileHash` command resolution under its frozen PowerShell 5.1 child; that does not prove PS 7 incompatible or compatible. R1G selects PowerShell 7.6.6 and mandates a separate exact no-profile command/module preflight by Codex after your delivery and independent Review.

## Implementation scope

First verify the required worktree/branch/base/common-dir and clean status. Read the frozen Task and manifest from the main repo as read-only inputs. The main checkout has unrelated pre-existing changes; do not edit or copy them.

Write ownership is limited to exactly these three paths in the R1G worktree:

1. `verification/P02/p02pre-r1g-capture.ps1`
2. `verification/P02/p02pre-r1g-author-selfcheck-20261011.json`
3. `verification/P02/p02pre-r1g-antigravity-handoff-20261011.md`

Implement the smallest safe successor candidate preserving the R1F manifest's exact identity/path scope, `.tmp.driveupload` path-only exclusion, symlink no-follow behavior, no-read boundary, allowlisted Git/`whoami.exe` children, fail-stop semantics and unique `CreateNew` outputs. Add explicit reached/not-reached phase reporting and truthful engine attestation for the fixed PowerShell 7.6.6 executable. Do not broaden paths, APIs, children, registry/ACL/profile access, or behavior. Use the exact source pin above; do not edit R1F files.

The author self-check JSON must be truthful and pin the exact candidate bytes. Do not claim a parse/assertion PASS unless you actually ran it and the manifest permits that stage. Per the frozen release order, do not run parser/self-check, host preflight, getters, capture, Build/Cargo or AC; Codex runs the independent checks after Reviewer approval. Mark checks you did not run as `NOT_RUN`.

## Delivery and acceptance

- Commit only the three assigned files on `agent/antigravity/P02PRE-R1G`; no merge or main-branch edits.
- Provide a Handoff at the assigned path with fixed commit, changed paths and hashes, design notes, acceptance-criteria mapping, commands actually run and results, checks not run, risks and the exact next receiver (`Codex` for integration/review dispatch).
- Do not review your own work. Do not alter R1F evidence, Plan/STATUS/shared contracts, Task/manifest, or any other path.
- Stop on wrong branch/base/common-dir, dirty worktree before your edits, source-pin mismatch, unexpected files or inability to keep the write set exact. Report the concrete blocker without broadening scope.

This is implementation delivery only; it is not an approval to run R1G capture or release any P02 Gate. `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; exact residual-risk text=`technical condition unmet; user explicitly accepted residual risk`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`.
