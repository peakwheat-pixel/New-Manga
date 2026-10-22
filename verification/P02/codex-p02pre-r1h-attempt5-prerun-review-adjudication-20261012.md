# Codex Adjudication：A5 Final Pre-run Evidence Review

- Task=`P02PRE-R1H-R6-EXEC-A5`; root=`G:\CODEX\New Manga`; `main@343895fb5f0329c0c07a7104ec321b698f967607`.
- Reviewer=`DeepSeek Harness` (non-author); DSH verdict=`CHANGES_REQUESTED`, P0/P1/P2/P3=`0/2/3/4`; DSH CLI=`0.2.0-rc.2`; session=`session-4226240b-d630-44de-a1c1-dc440776c6d9`.
- DSH hashes=`NOT_VERIFIED`: two read-only PowerShell/hash attempts stopped before command execution with `SetNamedSecurityInfoW failed (Win32 5)`. Codex independently verified all 8 frozen inputs before and after Review (`8/8 bytes+SHA-256 MATCH`). DSH made one path-name-only glob call. Full report=`codex-subagent-p02pre-r1h-attempt5-prerun-review-20261012.md`; raw output/stderr/exit and prompt are adjacent.

## Adjudication

| Finding | Codex disposition | Required treatment |
|---|---|---|
| P1-1 Handoff pin has no provenance and is also a write source | ACCEPTED | A5 remains blocked. A6 must pin the actual Owner Handoff raw bytes and make it an explicit independent Review input. |
| P1-2 Task pin changed after the reviewed snapshot | ACCEPTED | The review snapshot is `11473 / 9B10217614F9F72DDF076D7B41A2654C0816F456B94A64A8B8E72E45530A6009`; current Task is `14493 / 0EF728E121A4FDDF85E4AD54C9904764DCC91A221B0513DEADB67814371EFA3A`. The earlier claim “only metadata changed” is `NOT_VERIFIED`; do not treat those snapshots as identical. A6 will use a stable, immutable review-contract input and keep mutable Task status metadata out of the frozen input set. |
| P2-1 profile/registry/ACL/system state lacked post-check | ACCEPTED | Keep post-fail-stop state `NOT_VERIFIED / UNPROVABLE`; executor not run is not a post-state query. |
| P2-2 source Parser/selfcheck and executor runtime evidence were conflated | ACCEPTED | PS7 Parser `0 errors` and 73 in-memory assertions were completed before the final pre-run; the executor's own `selfcheckEvidence/engineEvidence` remains `NOT_RUN`. A6 protocol and evidence must use those distinct phases and pin the source-check report. |
| P2-3 inherited files were not in the DSH input pins | ACCEPTED IN PART | A4 executor/protocol and root old Handoff were not in that Review's fixed inputs; this remains a Review limitation. Codex independently compared A4 and A5 executor sources: each has 639 logical lines and exactly six differing lines (1, 26, 34, 366, 367, 623). The “attempt marker/header” share line 1, so the six-line claim is accurate. This Codex comparison does not retroactively make those files DSH-reviewed. A6 must pin required inherited sources. |
| P3-1 ACL SDDL evidence omitted the compared strings | ACCEPTED | A6 must record observed and expected SDDL or classify the check `NOT_VERIFIED`. |
| P3-2 malformed helper invocation bytes were not retained | ACCEPTED | Preserve the omission; do not reconstruct. Any attempted access to `.tmp.driveupload` remains `NOT_VERIFIED`. |
| P3-3 checkpoint inclusion was not explicit | ACCEPTED | A6 manifest must set `checkpointIncludedInInputPins=true` and include the checkpoint pin. |
| P3-4 output snapshot/exit semantics and numbering were ambiguous | ACCEPTED | A6 must mark the output-absence check as a pre-write snapshot, define disposition vs process-exit fields, and call them helper invocations rather than attempts. |

## Safety decision

The DSH review explicitly confirms the A5 fail-stop is correct. Frozen executor expects Owner Handoff `3551 / 700B79F3FA01308DFFEC374A4FFB92DAC69C2FD8355DE623F6A250E9F1511658`; the actual Owner worktree file is `9505 / E13C7148B79740927692D9282C4F474FEE4AADD50BFBE256509CACA3052786B1`. Because the file is also a write source, do not call attempt5. Attempt5 remains `BLOCKED / NOT_RUN`; no retry, cleanup, or mutation of A5 artifacts.

Two additional read-only root status helpers during this adjudication (UTC 04:27:37 and 04:27:45) accidentally passed the pathspec with a leading space and exited 128 before returning status bytes. The exact excluded-subtree access scope remains `NOT_VERIFIED`. A corrected call at UTC 04:27:52 used final argv `:(exclude).tmp.driveupload`, exited 0 with status `1094 NUL / 74621 bytes / SHA-256 52E06C2DC916BBC207836EC8A89253ECFA6CB842F5626DBA384EB0F6FC21AD43`, stderr 0; `.git/index` stayed `C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68`.

Gate is unchanged: `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; system AC1–AC7=`BLOCKED / NOT_RUN`. Residual risk remains `technical condition unmet; user explicitly accepted residual risk`.

## Next slice

Start `P02PRE-R1H-R6-EXEC-A6` as a new attempt, owned by ZCode in its own worktree and independently reviewed by DeepSeek Harness. It must address all accepted findings in a fresh immutable review package. A5/A4 artifacts stay frozen. The A6 Task and contract freeze the exact scope before dispatch; no executor, File.Replace, profile/registry/ACL mutation, Build/Cargo, or system AC is allowed during A6 delivery.
