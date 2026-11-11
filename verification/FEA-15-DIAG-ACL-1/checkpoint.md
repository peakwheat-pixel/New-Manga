# FEA-15-DIAG-ACL-1 Checkpoint

```text
Timestamp: 2026-11-11 00:36:13 UTC / 08:36:13 Asia/Shanghai
Agent: Codex
Task ID: FEA-15-DIAG-ACL-1
TaskStatus: in_progress
ExecutionState: ACTIVE
Branch: main
Worktree: G:/CODEX/New Manga
Base commit: 1e4542a047e991a5f10b0b213ca5a96eafe919a4
Task claim commit: 5ed87d05d95e6b861c297c3063905b60e5fe7b7c
Current HEAD at checkpoint: 5ed87d05d95e6b861c297c3063905b60e5fe7b7c
```

## Resume Reality Check

- Task card and `STATUS.md` both name `FEA-15-DIAG-ACL-1` as `in_progress`.
- `REBASELINE_PLAN.md` marks this task `in_progress`; the serial follow-up `FEA-15-PIN-EOL-GOV-1` remains `proposed`; READY nodes are none.
- Claim commit `5ed87d05d95e6b861c297c3063905b60e5fe7b7c` descends from task base `1e4542a047e991a5f10b0b213ca5a96eafe919a4`.
- At resume, the only untracked path was `verification/FEA-15-DIAG-ACL-1/`; no pre-existing user changes were overwritten.
- Result: `RESUME_SAFE` for this Task's allowed read-only evidence and documentation work.

## Completed

- Read the active Task, STATUS, DAG, prior acceptance report and relevant source/tests.
- Cross-checked plugin sandbox/export hook, Host ACL, Python ACL/profile and v7 failure evidence.
- Added a diagnostic matrix, resource manifest and initial checkpoint. No production/test/contract bytes changed.
- Recorded NTFS persistent ACL capability for C:/G:, a PowerShell ACL-equivalent success on a new Task-owned directory, and a read-only workspace observation.
- Explicitly marked the direct `SourceSecurity.PrivateDirectory` probe `NOT_RUN`; its automatic approval review did not execute it.

## Working Tree

- `verification/FEA-15-DIAG-ACL-1/`: untracked Task evidence containing the three probe logs plus `README.md`, `resource-manifest.json`, `checkpoint.md`, and `workspace-observation.log`.
- No staged files; no committed diagnostic report yet.

## Tests / Gates

- No test suite was re-run in this diagnostic step; existing measured runs remain linked from `README.md` and retain their original HEADs and EXIT codes.
- `check.ps1` default and `-TaskPath`, `verify_pins.ps1`, evidence hashes, canonical pin and commit pin: pending final closeout.
- Independent ZCode Review and final adjudication: pending.

## Blockers / Decisions / Open Questions

- Exact Host ACL failure condition is unproven. A direct reflection call was not executed because the automatic approval review could not run the command after a usage-limit failure.
- Plugin failure stage and origin of observed system Python ACE/profile state are unproven; do not rerun ACL/profile-mutating tests without a fresh isolated plan and before-state snapshot.
- The 62 fixture candidates are not attributed to a unique owner; keep them all in place.
- No contractual or architecture change is proposed.

## Next Exact Step

1. Finish `workspace-observation.log` and verify all diagnostic paths and hashes.
2. Update Task AC states and resource manifest references; create reviewer appointment for ZCode.
3. Run both `check.ps1` modes and `verify_pins.ps1`; record command, time, HEAD and EXIT.
4. Commit evidence and Task metadata in the project's required sequence, then dispatch the independent ZCode Review and request its adjudication.
5. Follow ZCode's decision. Any missing exact Host probe remains `NOT_RUN` unless approval review becomes available; do not modify/clean system ACLs, profiles or fixtures.
