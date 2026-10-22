# P02PRE-R1H round-four Owner remediation independent static Review

你是非作者 Reviewer `/root/p02_r1h_remediation_review`。本次 Owner=`/root/p02_r1h_codex_owner`；Integrator/Adjudicator=`/root`。你未参与本轮 round-four 实现。请只读静态审查冻结 commit，不要改 candidate 或治理文件。

## Frozen inputs

- Repository=`G:\CODEX\New Manga`
- Owner worktree=`C:\Users\49745\.codex\worktrees\p02pre-r1h-codex`
- Branch=`agent/codex/P02PRE-R1H`
- Frozen Task base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`
- Round-four parent=`0ecada4182d624d4f352a253e09db3bdecbee5d1`
- Delivery HEAD=`7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`
- Tree=`c9afca4e9bfd8d1b6a6c3ad5a8a33e0e12c3d87b`
- Current Task=`doc/tasks/P02PRE-R1H.md`
- Full source/candidate input pins=`verification/P02/codex-p02pre-r1h-remediation4-review-input-pins-20261012.json`
- Root delivery-boundary verification=`verification/P02/p02pre-r1h-round4-delivery-verification-20261012.md`

Verify all pins before and after Review. If any mismatch occurs, stop substantive Review and report `INPUT_PIN_MISMATCH`; do not edit pins.

## Review scope and sole write

Review the complete frozen Task base→delivery HEAD candidate diff, exactly these three candidate paths:

1. `verification/P02/p02pre-r1h-capture.ps1`
2. `verification/P02/p02pre-r1h-selfcheck.ps1`
3. `verification/P02/p02pre-r1h-handoff-20261012.md`

The only permitted write is `verification/P02/codex-subagent-p02pre-r1h-static-review-remediation4-20261012.md`.

## Core acceptance

1. Re-adjudicate R1H-007 precisely: confirm `[ordered]` integer-key semantics in PowerShell 7.6; check `$expectedDirectTexts[[object]$index]` actually selects the integer object key overload, while `$prefix[[int]$index]` remains a positional prefix array access. Inspect the entire key allowlist (`0,1,3,4,6,9,10,11,12`) and confirm each expected text is compared with its intended statement position; no positional value/key collision or cast ambiguity remains.
2. Re-check the legal real-candidate prefix contract path and all four source-only memory mutation fixtures, including that the positive check is now reachable by static control-flow reasoning and fixtures remain unexecuted. Confirm injected source cannot be executed.
3. Re-review the full Task base→HEAD diff for regression to R1H-001..006, including R1H-005 exact pure-memory helper allowlist; R1H-006 actual `$candidateLoop.Body` 13-direct-statement prefix, nested staging branch, control-flow closure, commands/member calls/assignments and the four negatives. Do not review only the one-line diff or inherit prior approval.
4. Check Handoff accurately states files, base/head, static fixes, Owner-only `git diff --check`, and all unrun checks. Candidate scope and Build/Gate status must remain unchanged.
5. Report `VERDICT`, P0/P1/P2/P3 counts, stable finding IDs/severities, exact path/line, trigger/impact/minimal fix, R1H-001..007 and AC1–AC7 dispositions. Separate static opinion from execution evidence and `NOT_RUN`.

## Restrictions

- Static reading, complete diff and necessary read-only Git metadata only.
- Do not run PowerShell parser, selfcheck or fixtures, preflight, capture, getter/API, tests, Build/Cargo, AC1–AC7, OS dynamic, or Windows Sandbox.
- Do not modify candidate, Task, manifest, Plan/STATUS/index/checkpoint, pins, adjudication or any file other than the sole Review report above.
- Do not access `.tmp.driveupload`; if status is needed, pass `:(exclude).tmp.driveupload` as a separate Git pathspec.
- State actual files read, read-only commands/results, pins pre/post, reviewer/owner/integrator identities, limitations and review date. A static Review does not establish integration, selfcheck execution, P02PRE, Build/Gate or AC PASS.
- After writing the report, stop. `/root` alone adjudicates and releases any successor.
