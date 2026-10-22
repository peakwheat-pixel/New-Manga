# P02PRE-R1H-R6-EXEC-A6 Immutable Task Contract

- Task ID: `P02PRE-R1H-R6-EXEC-A6`
- Owner: Antigravity
- Non-author Reviewer: DeepSeek Harness
- Integrator/Adjudicator: Codex /root
- Base commit: `343895fb5f0329c0c07a7104ec321b698f967607`
- Branch: `agent/antigravity/P02PRE-R1H-R6-EXEC-A6`
- Worktree: `C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga`
- Owner write allowlist:
  - `verification/P02/p02pre-r1h-round6-integrator-attempt6-20261012.ps1`
  - `verification/P02/p02pre-r1h-round6-integration-protocol-attempt6-20261012.md`
  - `verification/P02/p02pre-r1h-round6-attempt6-exec-handoff-20261012.md`

## Goal

Create one new attempt6 executor, protocol, and Handoff using the smallest change that addresses every accepted A5 adjudication finding. Keep A4/A5 sources byte-identical. Do not expand inherited identity, path, ACL, API, child-process, write-closure, or Gate limits. Owner delivery is not permission to run the executor or satisfy any downstream Gate.

## Acceptance criteria

1. Create only the three allowlisted attempt6 files.
2. Make the smallest justified change from the A5 executor; use new attempt6 output names and `CreateNew`; never overwrite A5 evidence.
3. Pin the actual Owner Handoff raw bytes. Separate the immutable Review-contract snapshot from mutable Task status. Set `checkpointIncludedInInputPins=true` and include the pinned checkpoint. Ensure A4/A5 inherited sources and the root Owner Handoff can be pinned and independently reviewed.
4. Keep source Parser/in-memory evidence separate from executor runtime `selfcheckEvidence`/`engineEvidence`; runtime selfcheck remains `NOT_RUN` in this Owner task.
5. Preserve observed and expected SDDL verbatim, or mark it `NOT_VERIFIED`; do not synthesize missing malformed-helper argv/stderr/exit; preserve `.tmp.driveupload` as `NOT_VERIFIED` without accessing it.
6. Mark output absence as a pre-write snapshot. Distinguish Codex disposition from OS process exit. Use “helper invocation”. Do not claim profile/registry/ACL/system state stayed unchanged after any fail-stop if it was not observed; retain `NOT_VERIFIED` / `UNPROVABLE`.
7. Prepare the immutable exact-input package for a later independent DeepSeek Harness static Review; Codex will recompute pins and adjudicate. Unresolved P0/P1/P2 block later Parser/pre-run/execution.
8. Deliver fixed branch and HEAD, exact three-path diff, Handoff, AC outcomes, permitted Parser-only result, `git diff --check` result, and blockers.

## Owner execution boundary

- The sole permitted runtime check is a PowerShell 7.6.6 Parser-only syntax check of the new executor. Do not dot-source or invoke it.
- Do not run executor/selfcheck, `File.Replace`, capture/getter, OS/API or child-process tests, profile/registry/ACL operations, Build/Cargo, or AC1–AC7.
- Do not edit Task, Plan, STATUS, index, checkpoint, review inputs, A4/A5 files, actual Owner Handoff, user data, or any non-allowlisted path. Do not stage or commit because this Task expressly protects `.git/index`; Codex freezes the delivery HEAD and diff.
- Do not query `.tmp.driveupload`. Every `git status` command must use final independent pathspec `:(exclude).tmp.driveupload`.
- Preserve the accepted risk language exactly: `private_registry_absence=UNPROVABLE`; `Technical Gate=NOT_SATISFIED`; `Owner Risk Acceptance=APPROVED`; `Gate Disposition=WAIVED_BY_OWNER`; `Build Authorization=AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`. Do not claim a Gate or AC PASS.
