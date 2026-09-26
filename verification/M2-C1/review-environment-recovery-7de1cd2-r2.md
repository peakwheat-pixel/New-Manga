# M2-C1 Reviewer Environment Recovery — r2 Outcome

Date: 2026-09-26 (Asia/Shanghai)
Owner Delivery: 7de1cd27e22037d4b76b235c9f11399b0cea9463
Fixed reviewed head: b2377288680569dbee4e2299df7dfae4de067c54
Task state: blocked
Integration Gate: not opened

## Current fixed state

ZCode remains the Owner. Delivery, Handoff, Contract blob (4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3) and reviewed head were not modified. Qoder's independent Review is formally committed and APPROVED at 0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5. DSH r2 is not a formal Review artifact because its report/evidence could not be committed.

## Root causes

### DeepSeek Harness

The original G: Review worktree remains preserved. DSH startup failed before Git verification with:

SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\M2-C1-dsh-review-7de1cd2)

Host-side ordinary file-write probes on the worktree and its .git/worktrees metadata succeeded; the failure was DSH's default workspace-write sandbox ACL initialization for the G: location. A new linked worktree was created under the user-owned C: workspace:

- branch: review/deepseek/M2-C1-zcode-7de1cd2-r2
- worktree: C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r2
- HEAD: b2377288680569dbee4e2299df7dfae4de067c54
- git-common-dir: G:/CODEX/New Manga/.git

DSH could execute Git reads and write authorized report/evidence files under C:. However, the linked-worktree index is stored under G:/CODEX/New Manga/.git/worktrees/M2-C1-dsh-review-7de1cd2-r2/. Staging failed three times with:

fatal: Unable to create 'G:/CODEX/New Manga/.git/worktrees/M2-C1-dsh-review-7de1cd2-r2/index.lock': Permission denied

No elevation was requested or used. This is a DSH sandbox/write-boundary issue, not a Contract finding or Owner defect. Host PowerShell can read the fixed object and the mandatory ancestry/blob/whitespace commands pass, but those host checks do not substitute for DSH's formal submission.

### Qoder

Qoder's earlier Git write blocker was caused by CLI command-prefix allowlist syntax that did not match the requested commands, not by NTFS, worktree or index ACL. Using supported Bash(<command-prefix>:*) patterns allowed Qoder to stage only its authorized report/evidence and create formal commit 0d73983.... .qoder-credits/ remains untracked and excluded.

## DSH r2 output and correction

DSH completed its technical analysis against the fixed Owner head and generated these files in its C: linked worktree, but they remain untracked/uncommitted and have no Gate effect:

- doc/reviews/M2-C1-zcode-7de1cd2-dsh-r2.md
- verification/M2-C1/review-dsh-zcode-7de1cd2-r2/**

The report records Decision = BLOCKED because the required Reviewer commit is impossible in the current sandbox. Its substantive analysis reports no blocking Contract finding and an approval-eligible content assessment. It judges the known Contract section 1 source-trace.md link as a documented, non-blocking observation, not a reason to return the Owner Delivery.

During its first environment probe DSH transposed two hexadecimal characters in a manually entered SHA and observed misleading bad object errors. It corrected this by deriving the SHA from git rev-parse HEAD; the fixed head then matched the Task/Handoff and DSH's mandatory checks passed. No repository object corruption finding is supported by the corrected checks. Product pytest, GUI, QML, IPC runtime and large-media capacity checks remain NOT_RUN.

## Current disposition and minimum recovery option

Task remains blocked. Qoder has one formal approval; DSH has no committed Review report/evidence. Integration Gate is not ready. Owner worktree, both original Reviewer worktrees, the C: DSH r2 worktree, its uncommitted files, and Qoder .qoder-credits/ are preserved.

The minimum candidate environment is a standalone clone under C:/Users/49745/.codex/worktrees/** with the clone's .git directory, index, objects and refs all inside the DSH workspace-write area. A linked worktree whose common Git directory remains on G: does not solve the write boundary. If DSH commits in that standalone clone, any transfer into the shared repository must preserve the exact Reviewer-created commit (for example, an explicit bundle/fetch of that commit); Codex must not edit or re-commit the Reviewer report. This option was not created or dispatched in this recovery turn.

No Integration Gate, integration, M2-S1, or implementation work was started.
