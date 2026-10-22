# H2-RUN Codex adjudication R1

Task: P02PRE-R1H-H2-RUN  
Base commit: 343895fb5f0329c0c07a7104ec321b698f967607  
Reviewed source head: 1924fbb4fbff6044205e4f8b52adb6aaff879e2a  
RunId: h2-20261013-de77a42fccca4193925767ba4e414970  
Raw result: 788,029 bytes; SHA-256 32cd72b710857bb0f19eb92d2c01f2ff6aa13778f10836965c8619ebbf5a2179

## Decision

Verdict: APPROVED for exact H2-RUN runtime evidence and current R2 verification report, for integration into the isolated evidence worktree.

The collector result is valid new-time evidence. This approval does not make it a new H1 PRE_RUN_PASS, does not substitute for H1 v2, close historical P2-1, satisfy X6 S0, or release X6. Those decisions belong to the downstream H1 Review/adjudication Task.

## Independent review and pin adjudication

DeepSeek Harness R1 returned BLOCKED because its review environment could not execute commands. Its static review found no P0-P2 content issues and identified P3-1: the summary field notRunCount=1 was ambiguous. This is a reviewer-capability limitation, not a collector failure. Codex completed the executable checks the reviewer could not run.

After R1, Codex verified 16/16 review inputs matched their pre-review bytes and SHA-256. The exact report and input post-pin record are preserved as dsh-result-review-r1.md and result-review-r1-post-pins.json.

DSH R2 returned APPROVED_STATIC_CONTENT for the focused correction. It confirmed P3-1 resolved: the current runtime-verification-r2.json reports notRunCheckCount=0 separately from notRunScopeItemCount=7 and enumerates the seven scope categories. DSH R2 identified P3-2, a stale R1 heading in the R2 Markdown report. Codex changed only that heading to R2 and froze the corrected report hash.

DSH R3 returned APPROVED_STATIC_CONTENT for the exact R2 heading correction, with 0 P0/P1/P2/P3 findings. It confirmed P3-2 resolved and P3-1 remained resolved.

Codex independently verified review inputs after each round: R1 16/16 unchanged, R2 8/8 unchanged, and R3 6/6 unchanged. The corresponding manifests and post-pin records are listed in the Task Canonical Evidence table. The raw collector output and all other pinned source evidence remained unchanged across the rounds; the only intended changes were the clarified R2 summary/report and its one-line R2 title correction.

## Codex runtime verification

Codex parsed all 80 NDJSON lines and verified the exact RunId, 78 unique observations, final closed record, disposition COLLECTED_NEW_TIME_EVIDENCE, and collector exit code 0. All 55 checks are PASS; 0 are FAIL, NOT_VERIFIED, or NOT_RUN. Codex traversed all 55 observedPointer JSON Pointers against the final record; 55 resolved, 0 were malformed, and 0 were unresolved.

Every observation has a unique ID, start/finish timestamps and output; all states are OK. The record has 54 in-process getter observations and 24 helper-process observations. Launcher metadata matches raw stdout/stderr/exit captures and the result bytes/hash.

After collection and in the final review state, root HEAD and refs/heads/main remain 343895fb5f0329c0c07a7104ec321b698f967607; root .git/index SHA-256 remains C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68. The approved source worktree is clean at 1924fbb4fbff6044205e4f8b52adb6aaff879e2a. Collector and selftest hashes remain their frozen values. Collector-recorded root/candidate/A6 refs, protected-file and before/after root-index checks all PASS.

Machine-readable final adjudication inputs and verification are in codex-adjudication-r1-input-verification.json, SHA-256 efaa288cbc366e8a0e9e17ef8b4590b5a2ba53887ffe31c0a63254f0925e1154.

## Acceptance criteria

| AC | Result | Evidence |
|---|---|---|
| Input Gate and live preflight | PASS | 43/43 preflight; exact source/R7 pins; single authorized collector invocation |
| Raw observation and pointer provenance | PASS | 78 observations; 55/55 checks; 55/55 pointers resolve; launcher captures match |
| New-time label and historical non-substitution | PASS | NEW_TIME_EVIDENCE and CANNOT_SUBSTITUTE_V2_TIME_EVIDENCE; H1 v2/P2-1 unchanged |
| Frozen input/source/root state | PASS | source hashes, root HEAD/main/index, integration worktree, and collector-protected checks match |
| Nonauthor Review and Codex adjudication | PASS | DSH R2 and R3 approved the corrected exact artifacts; R1 limitation supplemented by Codex; all review-round input pins verified |
| Canonical evidence integration and resource closeout | PENDING | Approved integration window remains open; resource disposition, integration commit, final Handoff and closeout checks remain |

Dynamic process closure remains REQUIRES_ACTIVE_TEST / NOT_RUN. Executor, Build/Cargo, AC1–AC7, Windows Sandbox, profile live probe, and ProcessObserver/Toolhelp remain NOT_RUN. No result here changes those statuses.