# Antigravity Dispatch：P02PRE-R1H-R6-EXEC-A6

## Assignment

Task: `P02PRE-R1H-R6-EXEC-A6`
Owner: Antigravity
Reviewer: DeepSeek Harness (independent non-author static Review)
Integrator/Adjudicator: Codex /root
Repository root: `G:\CODEX\New Manga`
Base HEAD: `343895fb5f0329c0c07a7104ec321b698f967607`
Working tree: `C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-exec-a6-antigravity\New Manga`
Branch: `agent/antigravity/P02PRE-R1H-R6-EXEC-A6`

## Read-only inputs

The task worktree is a clean checkout at the frozen base; it intentionally does not contain the root worktree’s uncommitted task/control evidence. Read the current project context and task contract from the absolute repository-root paths below. Read the technical evidence listed in `G:\CODEX\New Manga\verification\P02\agy-p02pre-r1h-r6-exec-a6-input-manifest-20261012.json` and verify each pinned SHA-256 before relying on it. If an input is missing or has a different hash, stop and report the exact path and mismatch; do not repair or copy it.

- `G:\CODEX\New Manga\AGENTS.md`
- `G:\CODEX\New Manga\doc\REBASELINE_PLAN.md` (unique DAG)
- `G:\CODEX\New Manga\doc\00_INDEX.md`
- `G:\CODEX\New Manga\doc\STATUS.md`
- `G:\CODEX\New Manga\doc\09_COLLABORATION.md`
- `G:\CODEX\New Manga\doc\tasks\P02.md`
- `G:\CODEX\New Manga\doc\tasks\P02PRE-R1H-R6-EXEC-A6.md`
- `G:\CODEX\New Manga\verification\P02\agy-p02pre-r1h-r6-exec-a6-task-contract-20261012.md` (immutable A6 scope/AC contract)
- `G:\CODEX\New Manga\verification\P02\agy-p02pre-r1h-r6-exec-a6-input-manifest-20261012.json`
- Actual Owner Handoff: `C:\Users\49745\.codex\worktrees\p02pre-r1h-codex\verification\P02\p02pre-r1h-handoff-20261012.md`

Treat every A4/A5 source, manifest, Review/adjudication, checkpoint, actual Owner Handoff, and Task contract as immutable read-only input. The root worktree contains original-author dirty/untracked data: never copy it into this worktree, overwrite it, or clean/stash/reset it. The previous ZCode prompt and failure report are historical routing evidence only; do not follow their Owner/path instructions.

## Work

Implement the immutable A6 Task contract with the smallest change that fully addresses each accepted A5 adjudication finding. Write only these three files in the Antigravity worktree:

- `verification/P02/p02pre-r1h-round6-integrator-attempt6-20261012.ps1`
- `verification/P02/p02pre-r1h-round6-integration-protocol-attempt6-20261012.md`
- `verification/P02/p02pre-r1h-round6-attempt6-exec-handoff-20261012.md`

Use the user’s existing P02 authorization only within this Task’s stated Owner boundary. It does not waive any unresolved condition, does not permit a Gate PASS claim, and does not authorize runtime execution from the A6 Owner worktree.

## Strict execution and write boundary

- The only permitted runtime check is PowerShell 7.6.6 Parser-only syntax parsing of the new executor. Do not dot-source or invoke the executor.
- Do not run selfcheck, capture/getter, `File.Replace`, OS/API, child-process, AppContainer/profile/registry/ACL operation, Build/Cargo, or AC1–AC7.
- Do not modify Task, Plan, STATUS, `.git/index`, checkpoint, Review inputs, A4/A5 files, actual Owner Handoff, user files, or any non-allowlisted path. Do not stage or commit; Codex will freeze the current delivery HEAD and exact diff.
- Never access `.tmp.driveupload`. Every `git status` must include final independent pathspec `:(exclude).tmp.driveupload`.
- Keep the known residual exactly honest: `private_registry_absence=UNPROVABLE`; `Technical Gate=NOT_SATISFIED`; `Owner Risk Acceptance=APPROVED`; `Gate Disposition=WAIVED_BY_OWNER`; `Build Authorization=AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`. Build Gate remains `BLOCKED`; Hard Build Barrier remains `EFFECTIVE`; Build/Cargo and system AC1–AC7 remain `NOT_RUN` unless a later Codex gate adjudication authorizes a real change.
- If the worktree/base/input pins drift or a required input is unavailable, stop before writing and report the evidence. Do not broaden scope or permissions.

## Delivery response

Return the fixed branch and HEAD, exact changed-path list and diff summary, Handoff path, every AC as `PASS_WITH_EVIDENCE`, `FAILED`, `BLOCKED`, or `NOT_RUN` with evidence, the exact PS7.6.6 Parser command/environment/result, `git diff --check` result, and blockers. State explicitly that no executor, OS/API mutation, Build/Cargo, or AC1–AC7 ran. Do not claim to have committed changes.
