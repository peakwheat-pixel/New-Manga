# P02PRE-R1H Round6 — stale baseline found before execution

## Recovery snapshot

- Recorded: 2026-10-12; Agent=`Codex /root`; product Task=`P02`; parent=`P02PRE-R1H`; blocked slice=`P02PRE-R1H-R6-EXEC-A4`; current Active Task=`P02PRE-R1H-R6-EXEC-A5`.
- Repository=`G:\CODEX\New Manga`; branch=`main`; HEAD=`343895fb5f0329c0c07a7104ec321b698f967607`; tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`; `git write-tree`=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`; `.git/index` SHA-256=`C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68`.
- Immediately before this checkpoint was created, controlled root status was=`1056 NUL / 71915 bytes / SHA-256 AFE530D88A30E1ED362F98BE0351DFCAC9F64F4DEA324A7CA21A83D045315359`, exit=0/stderr=0. Command used PowerShell `7.6.6`, `git -c core.fsmonitor=false --no-optional-locks status --porcelain=v2 -z --untracked-files=all --no-renames --ignore-submodules=none -- :(exclude).tmp.driveupload`; pathspec was its own argv item and excluded path was not accessed. Index hash before and after status remained `C5CA...`.
- Immediately before this checkpoint, Codex Owner worktree `C:\Users\49745\.codex\worktrees\p02pre-r1h-codex` was branch=`agent/codex/P02PRE-R1H`, HEAD=`c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`, tree=`96e7273ddd5fd27bee567bba27f19453cabe0842`; controlled full status=`0 bytes`, exit=0/stderr=0, using the same separate excluded pathspec.
- Compared with the nearest prior controlled post-integration snapshot (`1054 NUL / 71452 bytes / SHA-256 5CC08C56EF64FAAAC2F2A835DC2ED15B125E8726969EC0BD8CEE37F18E3DAD19`), pre-checkpoint status is `+2 records / +463 bytes`. The newly created Task file accounts for `+1 record / +37 bytes`; the other `+1 / +426` is `UNKNOWN / NOT_VERIFIED` because the prior snapshot did not retain a path-attributed record list. Preserve all original-author dirty/untracked content; no reset, clean, stash, broad staging, overwrite, or deletion.

## Completed evidence and decisions

- A4 Owner delivery, non-author DSH static Review, Codex adjudication, exact two-commit integration, and Codex integration verification are complete. Main integrated commit=`343895fb5f0329c0c07a7104ec321b698f967607`; integrated tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`. Review=`APPROVED_STATIC_CONTENT (0/0/0/4)` with recorded method deviation; Codex pins=`16/16 MATCH`; independent Parser errors=`0`; pure in-memory assertions=`73/73`, exit=0; integration verification=`PASS_WITH_EVIDENCE`. Evidence: `verification/P02/p02pre-r1h-attempt4-review-adjudication-20261012.md`, `verification/P02/codex-p02pre-r1h-attempt4-integration-verify-20261012.json`.
- Before any attempt4 executor invocation, Codex read its `AssertRefs`/`IndexState` binding. Frozen attempt4 expected root=`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`, index SHA=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`; live root/index are the values above. The mismatch deterministically blocks the executor before any invocation; attempt4 executor remains `NOT_RUN`, and the old slice is marked `BLOCKED`, not failed.
- The A5 repair Task is `doc/tasks/P02PRE-R1H-R6-EXEC-A5.md`. Owner=`Codex /root`; independent Reviewer=`DeepSeek Harness`; Integrator/Adjudicator=`Codex /root`. Only new attempt5 executor/protocol/Handoff may be created; attempt4 frozen source remains read-only. A5 review/adjudication and final safety pre-run must pass before any execution.
- Latest governance sources: `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/00_INDEX.md`, `doc/tasks/README.md`, parent Task `doc/tasks/P02PRE-R1H.md`, P02 Task `doc/tasks/P02.md`.

## Gate and no-run boundary

- `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; exact residual text=`technical condition unmet; user explicitly accepted residual risk`.
- Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; system AC1–AC7=`BLOCKED / NOT_RUN`. Round5 AC2 historical=`FAILED` remains separate evidence.
- No attempt4/attempt5 executor, `File.Replace`, R1H capture, OS/API/registry/ACL/profile mutation, dynamic isolation, Build/Cargo, system AC, or Windows Sandbox was run. All claims above are only observed source/ref/status or previously validated evidence; the stale baseline mismatch is not a test result.
- User canceled shutdown; do not shut down. Do not query, install, enable, or start Windows Sandbox.

## Exact next step

Complete A5's new immutable attempt5 executor/protocol/Handoff with root main/tree/index pins bound to the exact Live values above, without changing logic or path/process/write scope. Freeze exact input hashes and dispatch the non-author DeepSeek Harness Review. Codex independently re-hashes and adjudicates before running PS7 parser/selfcheck and the final pre-run checklist. Stop without invocation if any ref/index/identity/path/ACL/hash/output/child condition does not match. Do not rerun the old attempt4 executor.

## Authorization and tool/agent record

- User's continuous P02 authorization remains active for the scopes already frozen in the project; it is not test evidence or a Gate PASS. Existing owner risk waiver remains exactly as recorded; no new waiver is inferred.
- Actual agents in preceding A4 work: Antigravity Owner; DeepSeek Harness non-author Reviewer; Codex integrator/adjudicator. A5 owner is Codex and planned reviewer is DeepSeek Harness. Qoder remains exited. PowerShell runtime used here was `7.6.6`; planning preference `gpt-6.1-sol/high` cannot be claimed for this local Codex task. No user-data cleanup or machine shutdown.
