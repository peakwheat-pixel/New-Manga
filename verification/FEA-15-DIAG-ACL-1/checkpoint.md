# FEA-15-DIAG-ACL-1 Checkpoint

```text
Timestamp: 2026-11-11 02:27:27 UTC / 10:27:27 Asia/Shanghai
Agent: Codex
Task ID: FEA-15-DIAG-ACL-1
TaskStatus: closed_with_limitations (candidate closeout; final pin backfill in progress)
ExecutionState: ACTIVE
Branch: main
Worktree: G:/CODEX/New Manga
Base commit: 1e4542a047e991a5f10b0b213ca5a96eafe919a4
Reviewed head: 610839af8348f8b1f36e18a623e9fc40882051b5
Current HEAD at checkpoint: dea98ce8f93a3dfd3bdab84457a212d02804dba2
```

## Resume Reality Check

- Independent Review `/root/fea15_diag_acl_review` approved reviewed head `610839af8348f8b1f36e18a623e9fc40882051b5`, P0=0/P1=0. The final stage record keeps AC1–AC3 `PARTIAL`, AC4/AC5 `MET`.
- `STATUS.md` points to `FEA-15-PIN-EOL-GOV-1` as `proposed`, explicitly not released. The Plan READY set is empty.
- Current closeout edits are documentation/evidence only. No production code, tests, dependencies, schema or frozen contracts changed.
- Candidate gate run occurred at HEAD `dea98ce8f93a3dfd3bdab84457a212d02804dba2` with the closeout files listed below modified in the working tree. Its exact command outputs and EXIT values are in `gates-terminal.log`.
- Resume result: `RESUME_SAFE`; all unknown ACL/profile/fixture resources remain untouched.

## Completed

- Recorded diagnostic findings, cross-environment failures, v7 fixture debt, NOT_RUN items and resource dispositions.
- Added the independent Review report and fixed README mapping for output-exceeded `SandboxError`.
- Updated the external Resource Manifest to identify `C:/Python314` separately from un-inventoried user AppContainer profiles; same-location sentinel warnings are explicit and no resource was changed.
- Candidate closeout gates: default `check.ps1` PASS (3 warnings, EXIT 0); TaskPath PASS (5 warnings, EXIT 0, including two explanatory same-source manifest notes); pins 18/18 PASS (EXIT 0).

## Working Tree

- Modified: `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/TASK_LEDGER.md`, `doc/tasks/FEA-15-DIAG-ACL-1.md`, `verification/FEA-15-DIAG-ACL-1/README.md`, `verification/FEA-15-DIAG-ACL-1/checkpoint.md`, `verification/FEA-15-DIAG-ACL-1/resource-manifest.json`.
- Added: `doc/handoffs/FEA-15-DIAG-ACL-1-h1.md`, `verification/FEA-15-DIAG-ACL-1/gates-terminal.log`.
- Evidence commit and Task pin backfill are pending. These paths are within the frozen Task scope.

## Tests / Gates

- No product test suite was rerun during the diagnostic closeout. Existing Python/.NET results retain their original HEAD and EXIT values in the referenced logs.
- `gates-review.log` is historical at HEAD `80edff3fcaf36e7f429dd68500a76472d38321b6`; it is not used as current evidence.
- `gates-terminal.log` records candidate closeout verification at HEAD `dea98ce8f93a3dfd3bdab84457a212d02804dba2`, with command, time, working-tree state and EXIT values.
- Final gates must be rerun after the evidence commit, Task pin backfill and clean committed closeout.

## Blockers / Decisions / Open Questions

- The exact Host ACL rejection condition is unknown; direct `SourceSecurity.PrivateDirectory` probe remains `NOT_RUN` because the execution review reported a usage-limit failure.
- Plugin sandbox failure stage and the provenance of Python ACE/profile state remain unknown.
- The 62 fixture candidates have no proven unique owner. Preserve all in place.
- No contract or architecture change is proposed; no push.

## Next Exact Step

1. Commit terminal evidence and documentation without the Task card; compute each file SHA-256 and update its pin to the commit that contains it.
2. Regenerate `doc/TASK_LEDGER.md` with `python tools/governance/task_ledger.py --write` after Task edits.
3. Run both `check.ps1` modes and `verify_pins.ps1` after pin backfill; require PASS and record exact final HEAD/time/EXIT.
4. Confirm clean `main`, keep `FEA-15-PIN-EOL-GOV-1` proposed pending ZCode scope review; do not start it or push.
