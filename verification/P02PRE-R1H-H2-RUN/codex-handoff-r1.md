# H2-RUN Codex Handoff R1

Task: P02PRE-R1H-H2-RUN  
Base commit: 343895fb5f0329c0c07a7104ec321b698f967607  
Collector source integration commit: 1924fbb4fbff6044205e4f8b52adb6aaff879e2a  
RunId: h2-20261013-de77a42fccca4193925767ba4e414970

## Delivery

The approved, pinned collector was invoked once through the frozen binary-capture launcher. It completed with launcher OS exit 0 and collector exit 0, producing COLLECTED_NEW_TIME_EVIDENCE. The raw result is 788,029 bytes, SHA-256 32cd72b710857bb0f19eb92d2c01f2ff6aa13778f10836965c8619ebbf5a2179.

## Acceptance criteria evidence

- Input Gate and live preflight: PASS, 43/43; source pins and approved R7 artifacts are in preflight-freeze-r1.md.
- Raw mapping and provenance: 78 observations, 55/55 checks PASS, and 55/55 JSON Pointers resolve. Raw output and assertion summary are pinned in runtime-verification-r1.md and runtime-verification-r1.json.
- New-time disposition: COLLECTED_NEW_TIME_EVIDENCE; historical H1 v2/P2-1 remains unchanged.
- Frozen inputs: root HEAD/main/index, integration worktree, collector/selftest hashes, and collector-recorded refs/protected-file checks match the frozen values.
- Independent result Review and Codex adjudication: pending; this handoff requests DSH review of the exact pinned result.
- Evidence integration, resource closeout, and final per-AC closure: pending.

## Commands and results

- Frozen launch-once.ps1 using PS7.6.6, ProcessStartInfo.ArgumentList, and binary stdout/stderr capture: one invocation; launcher state COMPLETED; OS exit 0.
- Runtime result parser and assertion pass: 80 NDJSON records; 78 unique observations; 55/55 checks PASS; 55/55 JSON Pointers resolved; output/log hashes agree with launcher metadata.
- Post-run root/source verification: root HEAD/main/index unchanged; approved integration worktree clean; collector/selftest SHA-256 unchanged.
- Governance check will be run after the Task and status pointers are updated.

## Not run and limits

Dynamic process closure remains REQUIRES_ACTIVE_TEST / NOT_RUN. Build/Cargo, executor, and AC1–AC7 were not run and remain outside this Task. The new collection is not a substitute for the old H1 v2 timepoint and does not by itself release X6.

## Next receiver

DeepSeek Harness: independently review the exact pinned raw result and runtime verification, read-only, and report findings by severity. Codex will pin the review inputs before/after, adjudicate, integrate accepted canonical evidence in an isolated worktree, and close the Task only after resource disposition and governance checks pass.