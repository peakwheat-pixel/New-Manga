# Antigravity Owner Dispatch — P02PRE-R1H Round6 attempt4

You are the Antigravity Owner for Task `P02PRE-R1H-R6-A4`.

## Fixed workspace and task

- Repository: `G:\CODEX\New Manga`
- Work only in the already-created linked worktree: `C:\Users\49745\.codex\worktrees\p02pre-r1h-r6-attempt4-antigravity`
- Branch: `agent/antigravity/P02PRE-R1H-R6-A4`
- Base/current starting HEAD: `cddff58469b56e181019a8ddfeade80684bc7eb9` (tree `c25d051a4b9a0bd9773b50170e100f575ea19f2b`)
- Task spec (read-only copy in main checkout): `G:\CODEX\New Manga\doc\tasks\P02PRE-R1H-R6-A4.md`
- Parent Task/manifest are read-only in main checkout: `G:\CODEX\New Manga\doc\tasks\P02PRE-R1H.md` and `G:\CODEX\New Manga\verification\P02\p02pre-r1h-manifest-20261012.md`.
- Frozen attempt3 inputs are read-only: executor `G:\CODEX\New Manga\verification\P02\p02pre-r1h-round6-integrator-20261012.ps1` SHA-256 `DACDD544784A035E980F74250207D8EB561E13D0C5A06AA9F810DA9A1B29F222`; protocol `G:\CODEX\New Manga\verification\P02\p02pre-r1h-round6-integration-protocol-attempt3-20261012.md` SHA-256 `CAA5984BDAC01DE4A81E10154A9677D04F9A48DB40CB96804B6ECF8DA7F35313`; Codex in-memory definitions evidence `G:\CODEX\New Manga\verification\P02\p02pre-r1h-round6-attempt3-definitions-check-20261012.json` SHA-256 `0787E5C18E2CE1D6D8B319DF74928649A09F590F0B9EB92A26F323C6E9E38740`; adjudication `G:\CODEX\New Manga\verification\P02\p02pre-r1h-integration-protocol-review-adjudication-round6-attempt3-20261012.md` SHA-256 `8EADB35CE481D34D88191272360FD89F09312E7FC2AD867AA5A0EDFDB25A6FC4`.

## Owner write allowlist — exact new paths only

1. `verification/P02/p02pre-r1h-round6-integrator-attempt4-20261012.ps1`
2. `verification/P02/p02pre-r1h-round6-integration-protocol-attempt4-20261012.md`
3. `verification/P02/p02pre-r1h-round6-attempt4-selfcheck-20261012.ps1`
4. `verification/P02/p02pre-r1h-round6-attempt4-handoff-20261012.md`

All four targets must be absent before creation. Preserve attempt3 and all existing files. Do not edit Task/governance files in main, or any path outside this allowlist in the linked worktree. Do not reset/clean/stash/delete or modify any pre-existing file. If a target is present or the exact branch/base differs, stop before writing and report the collision.

## Required fixes

1. Replace the nested `$definitions` array with an explicit flat structure and named fields, then use those named fields when calling `DefineMethod`. Add a pure helper that returns the definitions. Prove in a PS 7.6.6 in-memory check that four definitions have the expected names, return types and parameter types, and that `TypeBuilder.DefineMethod` accepts every signature. Do not invoke any generated native method or create a persisted assembly.
2. Refactor process-record selection into a pure helper used by `ObserveProcesses`. Represent “no child has launched yet” as an explicit null/known-state or other sentinel that cannot collide with PID 0. A prelaunch sample must not classify System Idle PID 0 as the child. Unknown descendants and ambiguous attribution still fail closed. Add in-memory cases using synthetic records for root, PID 0, exact child, and unknown descendant; do not enumerate live processes.
3. Every `InvokeChild` start/observe/capture exception path must set `$script:ProcessClosureBlocked=$true` before propagating, and callers must stop before later protected reads/writes. Preserve current no-kill/no-retry behavior.
4. Immediately before the single reviewed three-argument `File.Replace`, re-pin destination bytes, ACL and streams (and any other exact destination invariants already required); stop on drift. Keep all paths and writes unchanged.
5. Open the execution evidence stream with `FileShare.None` so no reader can observe intermediate bytes.
6. In protocol attempt4, make reviewer report transport unambiguous: DSH returns Markdown via stdout; the Codex wrapper captures stdout/stderr/exit and separately CreateNew-writes the report body into the designated report path. Do not ask DSH to write repository files when its shell cannot initialize. Make checkpoint pin metadata agree with whether the checkpoint is in the input list.
7. Keep the external S2-to-hash observation race as an explicit narrow non-atomic evidence limitation. Keep the no-total-child-timeout/hung-child limitation; do not add killing or automatic retry.

## Required self-check and verification

The self-check must parse the candidate executor, extract only the pure helper function ASTs, and invoke those helpers in memory; it must not dot-source or run the executor’s top level. It may construct an in-memory `TypeBuilder` solely to validate method signatures. No native method invocation, Toolhelp/process enumeration, registry/profile/ACL/path/environment/WER query, file creation, File.Replace, build/Cargo, AC, or Sandbox action.

Using exactly `C:\Program Files\PowerShell\7\pwsh.exe` (PowerShell 7.6.6), run:

- `Parser::ParseFile` on the attempt4 executor and self-check, requiring zero parse errors.
- The attempt4 self-check, requiring all assertions pass and exit 0.
- `git diff --check`.
- Controlled status only with argv `git status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none -- . :(exclude).tmp.driveupload` (the final pathspec must be a separate argument; do not access the excluded path).

Commit only the four allowlisted files on the assigned branch using the configured Git identity. Return fixed commit/hash/tree, each file’s bytes and SHA-256, exact commands/exits, self-check counts, controlled status, and a concise Handoff. Do not claim any OS/runtime isolation, capture, Gate, Build, or AC PASS.

## Strict prohibited actions

Never run the attempt4 executor or any executor from prior rounds; never call File.Replace; never invoke native APIs or OS getters; never touch registry/profile/ACL/security settings; never run dynamic isolation, Build/Cargo, product/system AC1–AC7, or Windows Sandbox; never access `.tmp.driveupload`; never kill processes, retry, clean, restore, or delete. Preserve the parent Gate exactly: `private_registry_absence=UNPROVABLE`, Owner Risk Acceptance=`APPROVED`, disposition=`WAIVED_BY_OWNER`, Build Gate=`BLOCKED`, Hard Build Barrier=`EFFECTIVE`.

The attempt3 independent Review verdict remains `CHANGES_REQUESTED`; implement only these repairs and hand off for a new independent Review. You are the Owner and must not review your own changes. Codex `/root` owns integration and adjudication. DeepSeek Harness is the designated non-author Reviewer.